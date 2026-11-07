#!/usr/bin/env node
// Supliful <-> Shopify MCP server (stdio, JSON-RPC 2.0, zero dependencies) for Claude Cowork and
// Claude Code. Wraps the same library the CLI uses, so behaviour and tests are shared.
//
// Secrets never pass through the chat: they are read from the environment or from a private
// settings file (default ~/.supliful-mediclab/.env) that `supliful_setup` creates for the user.
// stdout carries protocol messages only; every log line goes to stderr.
import { createInterface } from "node:readline";
import { existsSync, mkdirSync, copyFileSync, writeFileSync, readFileSync, chmodSync } from "node:fs";
import { join, dirname, resolve, isAbsolute } from "node:path";
import { homedir } from "node:os";
import { fileURLToPath, pathToFileURL } from "node:url";
import { getConfig, ConfigError } from "./lib/config.mjs";
import { SuplifulClient, SuplifulError } from "./lib/supliful.mjs";
import { ShopifyClient } from "./lib/shopify.mjs";
import { JsonStore } from "./lib/store.mjs";
import { syncProducts, formatReport } from "./lib/sync.mjs";
import { forwardShopifyOrder, syncShipments } from "./lib/bridge.mjs";
import { localStatus, isSellable } from "./lib/mapping.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
export const SERVER_INFO = { name: "supliful-mediclab", version: "0.2.0" };
const PROTOCOL_VERSIONS = ["2025-06-18", "2025-03-26", "2024-11-05"];

export const HOME_DIR = () => process.env.SUPLIFUL_HOME || join(homedir(), ".supliful-mediclab");
const LABEL_FILES = ["brand.json", "specs.json", "catalog.json"];

const ENV_TEMPLATE = readTemplate();
function readTemplate() {
  for (const p of [join(HERE, ".env.example"), join(HERE, "env.example")]) if (existsSync(p)) return readFileSync(p, "utf8");
  return "SUPLIFUL_API_KEY=\nSHOPIFY_STORE_DOMAIN=\nSHOPIFY_ADMIN_TOKEN=\nSUPLIFUL_LIVE_ORDERS=0\n";
}

/** The label workspace: editable copies of brand/specs/catalog, seeded from the bundled defaults. */
export function labelsDir() {
  const dir = join(HOME_DIR(), "labels");
  mkdirSync(dir, { recursive: true });
  const src = existsSync(join(HERE, "labels", "defaults")) ? join(HERE, "labels", "defaults") : join(HERE, "labels");
  for (const f of LABEL_FILES) if (!existsSync(join(dir, f))) copyFileSync(join(src, f), join(dir, f));
  return dir;
}

function settingsFile() {
  return process.env.SUPLIFUL_ENV_FILE || join(HOME_DIR(), ".env");
}

/** Build clients from env + the private settings file. Never returns or logs a secret. */
export function readEnvFile(file) {
  const out = {};
  if (!existsSync(file)) return out;
  for (const raw of readFileSync(file, "utf8").split(/\r?\n/)) {
    const m = /^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$/.exec(raw);
    if (!m || raw.trim().startsWith("#")) continue;
    let v = m[2];
    if (/^(["']).*\1$/.test(v)) v = v.slice(1, -1);
    if (v !== "") out[m[1]] = v;
  }
  return out;
}

export function makeContext(need = []) {
  // Re-read the settings file on every call so edits take effect without restarting Cowork.
  // Non-empty process env wins; empty values never mask the file.
  const fromEnv = Object.fromEntries(Object.entries(process.env).filter(([, v]) => v !== undefined && v !== ""));
  const env = { SUPLIFUL_STATE_DIR: join(HOME_DIR(), "state"), ...readEnvFile(settingsFile()), ...fromEnv };
  // A relative state dir (as in the template) means "inside the plugin's home", never Cowork's cwd.
  if (!isAbsolute(env.SUPLIFUL_STATE_DIR)) env.SUPLIFUL_STATE_DIR = join(HOME_DIR(), env.SUPLIFUL_STATE_DIR === ".supliful-state" ? "state" : env.SUPLIFUL_STATE_DIR);
  const cfg = getConfig(need, env);
  const store = new JsonStore(cfg.stateDir);
  const supliful = new SuplifulClient({ baseUrl: cfg.supliful.baseUrl, apiKey: cfg.supliful.apiKey, logFile: join(cfg.stateDir, "supliful-requests.jsonl") });
  const shopify = cfg.shopify.storeDomain && cfg.shopify.adminToken ? new ShopifyClient(cfg.shopify) : null;
  return { cfg, store, supliful, shopify };
}

const log = (m) => process.stderr.write(`[supliful] ${m}\n`);
const str = { type: "string" };
const bool = (description) => ({ type: "boolean", description });

/** Tool catalogue. `run(args, deps)` returns text or a JSON-able value. */
export function buildTools(deps = {}) {
  const ctx = (need) => (deps.context ? deps.context(need) : makeContext(need));
  return [
    {
      name: "supliful_setup",
      description:
        "Create the private settings file where the user pastes their Supliful API key and Shopify Admin token (never in chat). Returns the file path and which values are still missing. Run this first, or whenever doctor reports a missing key.",
      inputSchema: { type: "object", properties: {} },
      annotations: { title: "Set up credentials", readOnlyHint: false, idempotentHint: true },
      run: async () => {
        const f = settingsFile();
        mkdirSync(dirname(f), { recursive: true });
        const created = !existsSync(f);
        if (created) writeFileSync(f, ENV_TEMPLATE, { mode: 0o600 });
        try {
          chmodSync(f, 0o600);
        } catch {
          /* not supported on this filesystem */
        }
        const env = {};
        for (const line of readFileSync(f, "utf8").split(/\r?\n/)) {
          const m = /^([A-Z_]+)=(.*)$/.exec(line.trim());
          if (m) env[m[1]] = m[2].trim();
        }
        const want = ["SUPLIFUL_API_KEY", "SHOPIFY_STORE_DOMAIN", "SHOPIFY_ADMIN_TOKEN", "SUPLIFUL_WEBHOOK_SECRETS", "SHOPIFY_WEBHOOK_SECRET"];
        const missing = want.filter((k) => !env[k] && !process.env[k]);
        return {
          settingsFile: f,
          created,
          missing,
          instructions:
            "Open the file in a text editor and paste each value after its '='. SUPLIFUL_API_KEY: Supliful > Stores > 'Supliful API' card > Create connection (shown once). SHOPIFY_ADMIN_TOKEN: Shopify admin > Settings > Apps > Develop apps > custom app. Webhook secrets are only needed for the always-on bridge server. Do not paste keys into the chat. Then run supliful_doctor.",
        };
      },
    },
    {
      name: "supliful_doctor",
      description: "Check the whole setup: Supliful reachable, API key valid (identifies the connection, never the key), products published to the connection, order mode (sandbox or live), Shopify token. Read-only.",
      inputSchema: { type: "object", properties: {} },
      annotations: { title: "Health check", readOnlyHint: true },
      run: async () => {
        const { cfg, supliful, shopify } = ctx([]);
        const checks = [];
        const add = (ok, name, detail) => checks.push(`${ok ? "PASS" : "FAIL"}  ${name}${detail ? ` - ${detail}` : ""}`);
        try {
          add(true, "Supliful API reachable", (await supliful.ping()).servedAt);
        } catch (e) {
          add(false, "Supliful API reachable", e.message);
        }
        if (!cfg.supliful.apiKey) add(false, "Supliful API key", `missing - run supliful_setup and fill SUPLIFUL_API_KEY in ${settingsFile()}`);
        else
          try {
            const me = await supliful.me();
            add(true, "Supliful API key", `connection "${me.connection.name ?? ""}" ${me.connection.id}`);
            const ps = await supliful.listAllProducts();
            add(ps.length > 0, "Products published to the connection", `${ps.length} (${ps.filter(isSellable).length} sellable)${ps.length ? "" : " - publish them in Supliful: My Products > Publish > Supliful API row"}`);
          } catch (e) {
            add(false, "Supliful API key", e.code || e.message);
          }
        add(true, "Order mode", cfg.supliful.liveOrders ? "LIVE - real orders are charged to the merchant" : "sandbox (testMode); set SUPLIFUL_LIVE_ORDERS=1 to go live");
        if (!shopify) add(false, "Shopify Admin token", "SHOPIFY_STORE_DOMAIN / SHOPIFY_ADMIN_TOKEN missing");
        else
          try {
            const d = await shopify.graphql("{ shop { name myshopifyDomain } }");
            add(true, "Shopify Admin token", `${d.shop.name} (${d.shop.myshopifyDomain})`);
          } catch (e) {
            add(false, "Shopify Admin token", e.message);
          }
        return checks.join("\n");
      },
    },
    {
      name: "supliful_list_products",
      description: "List the Supliful products published to the API connection (id, SKU, suggested retail price, sellable or not). Read-only.",
      inputSchema: { type: "object", properties: {} },
      annotations: { title: "List Supliful products", readOnlyHint: true },
      run: async () => {
        const { supliful } = ctx(["supliful"]);
        const ps = await supliful.listAllProducts();
        return ps.map((p) => ({ id: p.id, name: p.name, sku: p.sku, retailPrice: p.retailPrice, sellable: isSellable(p), status: p.status, updatedAt: p.updatedAt, images: (p.mockupUrls || []).length }));
      },
    },
    {
      name: "supliful_get_product",
      description: "Fetch one Supliful product by its UUID, with full description, images, weight and dimensions. Read-only.",
      inputSchema: { type: "object", properties: { id: { ...str, description: "Supliful product UUID" } }, required: ["id"] },
      annotations: { title: "Get Supliful product", readOnlyHint: true },
      run: async ({ id }) => ctx(["supliful"]).supliful.getProduct(id),
    },
    {
      name: "supliful_sync_products",
      description:
        "Sync Supliful products into the Shopify store. Without apply=true this is a DRY RUN that only returns the plan (create / link / update / hide / conflict / skip). Always run the dry run first and show the table to the user; apply only after they agree. Existing Shopify products matched by SKU are linked without changing their copy or price; new ones are created as DRAFT unless publish=true.",
      inputSchema: {
        type: "object",
        properties: {
          apply: bool("Write to Shopify. Default false (dry run)."),
          publish: bool("New sellable products go ACTIVE instead of DRAFT."),
          update_content: bool("Overwrite title, description and images of linked products that changed in Supliful."),
          prices: { type: "object", additionalProperties: { type: "number" }, description: "Retail price overrides keyed by Supliful id or SKU, e.g. {\"MLX-ASHW\": 35}" },
        },
      },
      annotations: { title: "Sync products to Shopify", readOnlyHint: false, destructiveHint: false, idempotentHint: true },
      run: async ({ apply = false, publish = false, update_content = false, prices = {} }) => {
        const { cfg, supliful, shopify } = ctx(["supliful", "shopify"]);
        const report = await syncProducts({ supliful, shopify, apply, publish, updateContent: update_content, prices, vendor: cfg.shopify.vendor, productType: cfg.shopify.productType, log });
        return formatReport(report);
      },
    },
    {
      name: "supliful_push_order",
      description:
        "Send one paid Shopify order's Supliful items to Supliful for fulfilment (other items, e.g. prescription products, stay in Shopify). Use dry_run=true first. Orders are sandbox (testMode) unless SUPLIFUL_LIVE_ORDERS=1 is set; a live order is charged to the merchant immediately. Safe to repeat: the same Shopify order never creates a second Supliful order.",
      inputSchema: {
        type: "object",
        properties: {
          shopify_order_id: { ...str, description: "Shopify order id, numeric or gid://shopify/Order/..." },
          dry_run: bool("Show the request without sending it (buyer address redacted)."),
          force: bool("Send even if the order is not marked paid."),
        },
        required: ["shopify_order_id"],
      },
      annotations: { title: "Send order to Supliful", readOnlyHint: false, destructiveHint: false, idempotentHint: true, openWorldHint: true },
      run: async ({ shopify_order_id, dry_run = false, force = false }) => {
        const { cfg, supliful, shopify, store } = ctx(["supliful", "shopify"]);
        return forwardShopifyOrder({ orderId: shopify_order_id, shopify, supliful, store, liveOrders: cfg.supliful.liveOrders, dryRun: dry_run, force, log });
      },
    },
    {
      name: "supliful_get_order",
      description: "Read a Supliful order by Supliful id or by our external id (shopify-<shopify order id>): status, hold reasons, lines, shipments with tracking. Read-only.",
      inputSchema: { type: "object", properties: { order_id: str }, required: ["order_id"] },
      annotations: { title: "Get Supliful order", readOnlyHint: true },
      run: async ({ order_id }) => {
        const o = await ctx(["supliful"]).supliful.getOrder(order_id);
        return { ...o, shippingAddress: o.shippingAddress ? { city: o.shippingAddress.city, stateCode: o.shippingAddress.stateCode, countryCode: o.shippingAddress.countryCode } : null, local: localStatus(o) };
      },
    },
    {
      name: "supliful_cancel_order",
      description: "Cancel a Supliful order. Only possible while it is NEW (about the first two hours) or its payment failed; the merchant is refunded. Confirm with the user before calling.",
      inputSchema: { type: "object", properties: { order_id: str }, required: ["order_id"] },
      annotations: { title: "Cancel Supliful order", readOnlyHint: false, destructiveHint: true, idempotentHint: true },
      run: async ({ order_id }) => {
        const o = await ctx(["supliful"]).supliful.cancelOrder(order_id);
        return { id: o.id, status: o.status };
      },
    },
    {
      name: "supliful_sync_shipments",
      description: "Turn a Supliful order's shipped parcels into Shopify fulfillments with tracking (customer notified). Each parcel is fulfilled once; parcels without tracking yet are left for later.",
      inputSchema: { type: "object", properties: { supliful_order_id: str }, required: ["supliful_order_id"] },
      annotations: { title: "Push tracking to Shopify", readOnlyHint: false, idempotentHint: true },
      run: async ({ supliful_order_id }) => {
        const { cfg, supliful, shopify, store } = ctx(["supliful", "shopify"]);
        return syncShipments({ suplifulOrderId: supliful_order_id, shopify, supliful, store, notifyCustomer: cfg.shopify.notifyCustomer, log });
      },
    },
    {
      name: "supliful_reconcile",
      description: "Re-check every open order this computer sent to Supliful and push any new tracking to Shopify. Use after downtime or when the user asks where orders stand.",
      inputSchema: { type: "object", properties: {} },
      annotations: { title: "Reconcile open orders", readOnlyHint: false, idempotentHint: true },
      run: async () => {
        const { cfg, supliful, shopify, store } = ctx(["supliful", "shopify"]);
        const results = [];
        for (const [ext, rec] of Object.entries(store.load("orders"))) {
          if (rec.closed) continue;
          try {
            const r = await syncShipments({ suplifulOrderId: rec.suplifulOrderId, shopify, supliful, store, notifyCustomer: cfg.shopify.notifyCustomer, log });
            if (["completed", "canceled", "returned"].includes(r.local)) store.set("orders", ext, { ...rec, closed: r.local });
            results.push({ order: rec.shopifyName, local: r.local, parcels: r.results });
          } catch (e) {
            results.push({ order: rec.shopifyName, error: e.code || e.message });
          }
        }
        return { checked: results.length, results };
      },
    },
    {
      name: "supliful_send_test_webhook",
      description: "Ask Supliful to send a signed test delivery (testMode) to every webhook endpoint on the connection, to prove the receiver works.",
      inputSchema: {
        type: "object",
        properties: {
          event: { type: "string", enum: ["order.created", "order.canceled", "order.onHold", "order.onHoldReleased", "order.shipmentCreated", "order.shipmentReturned", "order.completed", "product.published", "product.unpublished", "product.updated"] },
          order_id: str,
        },
        required: ["event"],
      },
      annotations: { title: "Send test webhook", readOnlyHint: false, idempotentHint: false },
      run: async ({ event, order_id }) => ctx(["supliful"]).supliful.sendTestWebhook(event, order_id),
    },
    {
      name: "supliful_rehearse",
      description: "Walk a sandbox order (never charged, never shipped) through create, idempotent replay, accept, ship and complete, to prove the integration end to end.",
      inputSchema: { type: "object", properties: {} },
      annotations: { title: "Sandbox rehearsal", readOnlyHint: false, idempotentHint: false },
      run: async () => {
        const { supliful } = ctx(["supliful"]);
        const product = (await supliful.listAllProducts()).find(isSellable);
        if (!product) throw new ConfigError("No sellable product is published to the connection yet. Publish one in Supliful first.");
        const ext = `rehearsal-${Date.now()}`;
        const req = { externalOrderId: ext, shippingAddress: { firstName: "Sandbox", lastName: "Rehearsal", address1: "2525 Arapahoe Ave", city: "Boulder", stateCode: "CO", zip: "80302", countryCode: "US" }, lines: [{ productId: product.id, quantity: 1 }], testMode: true };
        const steps = [];
        const { order } = await supliful.createOrder(req);
        steps.push({ step: "create", id: order.id, status: order.status });
        const again = await supliful.createOrder(req);
        steps.push({ step: "idempotent replay", sameOrder: again.order.id === order.id });
        for (const t of ["accept", "ship", "complete"]) {
          const r = await supliful.testTransition(order.id, t);
          steps.push({ step: t, status: r.order.status, webhook: r.event, local: localStatus(r.order) });
        }
        return { product: product.name, order: order.id, steps };
      },
    },
    {
      name: "supliful_label_specs",
      description:
        "Read or change the label front-panel facts for one SKU or the whole line (name, claim, key amount, net quantity, flavor, container, accent), the container sizes, or the brand settings. Pass only `sku` to read one; pass `sku` plus `set` to update fields; pass `container` plus `set` to update a container size; pass `brand` to update brand settings (e.g. distributorAddress). Returns the resulting spec.",
      inputSchema: {
        type: "object",
        properties: {
          sku: str,
          container: { ...str, description: "bottle, gummy-bottle, dropper or pouch" },
          set: { type: "object", description: "Fields to set, e.g. {\"net\": \"90 Capsules\", \"netVerified\": true} or {\"widthIn\": 8, \"heightIn\": 3, \"verified\": true}" },
          brand: { type: "object", description: "Brand fields to set, e.g. {\"distributorAddress\": \"...\"}" },
        },
      },
      annotations: { title: "Label specs", readOnlyHint: false, idempotentHint: true },
      run: async ({ sku, container, set, brand }) => {
        const dir = labelsDir();
        const specsPath = join(dir, "specs.json");
        const specs = JSON.parse(readFileSync(specsPath, "utf8"));
        if (brand) {
          const bp = join(dir, "brand.json");
          const b = { ...JSON.parse(readFileSync(bp, "utf8")), ...brand };
          writeFileSync(bp, JSON.stringify(b, null, 2) + "\n");
          return { brand: b };
        }
        if (container) {
          if (!specs.containers[container]) throw new ConfigError(`Unknown container ${container}`);
          if (set) Object.assign(specs.containers[container], set);
          writeFileSync(specsPath, JSON.stringify(specs, null, 2) + "\n");
          return { container, ...specs.containers[container] };
        }
        if (!sku) return { workspace: dir, containers: specs.containers, products: specs.products.map((p) => ({ sku: p.sku, name: p.name, net: p.net, netVerified: p.netVerified, container: p.container })) };
        let spec = specs.products.find((p) => p.sku === sku);
        if (!spec && set) {
          spec = { sku, netVerified: false, container: "bottle", accent: "cellular", ...set };
          specs.products.push(spec);
        } else if (!spec) throw new ConfigError(`No label spec for ${sku}`);
        else if (set) Object.assign(spec, set);
        if (set) writeFileSync(specsPath, JSON.stringify(specs, null, 2) + "\n");
        return spec;
      },
    },
    {
      name: "supliful_refresh_label_copy",
      description: "Re-import the product copy that label directions and warnings are taken from, live from the Shopify store (product type 'Specialty Supplements' by default). Run after product descriptions change.",
      inputSchema: { type: "object", properties: { product_type: str } },
      annotations: { title: "Refresh label copy from Shopify", readOnlyHint: false, idempotentHint: true },
      run: async ({ product_type }) => {
        const { cfg, shopify } = ctx(["shopify"]);
        const type = product_type || cfg.shopify.productType;
        const products = [];
        let after = null;
        do {
          const d = await shopify.graphql(
            `query LabelCopy($q: String, $after: String) { products(first: 100, query: $q, after: $after) { pageInfo { hasNextPage endCursor } nodes { id title handle status descriptionHtml variants(first: 1) { nodes { sku price } } } } }`,
            { q: `product_type:'${type.replace(/'/g, "")}'`, after },
          );
          for (const p of d.products.nodes) {
            const v = p.variants.nodes[0] || {};
            const text = p.descriptionHtml.replace(/<[^>]+>/g, " ").replace(/&amp;/g, "&").replace(/&#39;|&rsquo;/g, "'").replace(/&quot;/g, '"').replace(/&nbsp;/g, " ").replace(/\s+/g, " ").trim();
            products.push({ sku: v.sku, title: p.title, handle: p.handle, status: p.status, price: v.price, text, shopifyId: p.id });
          }
          after = d.products.pageInfo.hasNextPage ? d.products.pageInfo.endCursor : null;
        } while (after);
        const dir = labelsDir();
        writeFileSync(join(dir, "catalog.json"), JSON.stringify({ source: `Shopify Admin API, ${cfg.shopify.storeDomain}, product_type '${type}'`, exportedAt: new Date().toISOString().slice(0, 10), products }, null, 1));
        const specs = JSON.parse(readFileSync(join(dir, "specs.json"), "utf8"));
        const noSpec = products.filter((p) => p.sku && !specs.products.some((s) => s.sku === p.sku)).map((p) => `${p.sku} ${p.title}`);
        return { products: products.length, withoutLabelSpec: noSpec };
      },
    },
    {
      name: "supliful_render_labels",
      description:
        "Render label artwork: per SKU a print-ready PDF (trim + bleed, fonts embedded) for Supliful's label editor and a proof image with trim, safe-area and Supplement Facts zone guides, plus index.html (contact sheet) and report.json (what to confirm before printing). Look at the proofs and relay every issue in the report. Without Playwright installed it writes print-ready HTML instead (open, Print, Save as PDF, margins none).",
      inputSchema: {
        type: "object",
        properties: {
          skus: { type: "array", items: str, description: "Only these SKUs (default: all)" },
          out_dir: { ...str, description: "Folder to write to; use the user's working folder so they can open the files" },
        },
      },
      annotations: { title: "Render labels", readOnlyHint: false, idempotentHint: true },
      run: async ({ skus, out_dir }) => {
        const dir = labelsDir();
        const outDir = resolve(out_dir || join(HOME_DIR(), "labels-out"));
        const { renderLabels, loadInputs, buildLabel, labelHtml } = await import(pathToFileURL(join(HERE, "labels", "render.mjs")).href);
        try {
          const res = await renderLabels({ only: skus?.length ? skus : undefined, outDir, dir, log });
          return { summary: res.summary, outDir, labels: res.report.map((r) => ({ sku: r.sku, pdf: r.pdf && join(outDir, r.pdf), proof: r.proof && join(outDir, r.proof), issues: r.issues, error: r.error })) };
        } catch (e) {
          if (!/Playwright/i.test(e.message)) throw e;
          const inputs = loadInputs(dir);
          mkdirSync(outDir, { recursive: true });
          const files = [];
          for (const spec of inputs.specs.products.filter((s) => !skus?.length || skus.includes(s.sku))) {
            const L = buildLabel(spec, inputs);
            const f = join(outDir, `${spec.sku}-print.html`);
            writeFileSync(f, labelHtml(L, { proof: false }).replace("</body>", "<script>window.__runFit && window.__runFit()</script></body>"));
            files.push({ sku: spec.sku, html: f, issues: L.issues });
          }
          return { note: "Playwright is not installed, so print-ready HTML was written. Open each file in Chrome, Print, Destination 'Save as PDF', Margins 'None', Background graphics on. For PDFs directly: npm i -g playwright && npx playwright install chromium.", outDir, labels: files };
        }
      },
    },
  ];
}

// ---- JSON-RPC over stdio -------------------------------------------------------------------

const asText = (v) => (typeof v === "string" ? v : JSON.stringify(v, null, 2));

function errorText(err) {
  if (err instanceof ConfigError) return `${err.message}\nRun supliful_setup to create or locate the settings file.`;
  if (err instanceof SuplifulError) {
    const extra = err.fieldErrors.length ? `\n${JSON.stringify(err.fieldErrors, null, 2)}` : "";
    return `Supliful: ${err.message}${extra}${err.problem.instance ? `\n(instance ${err.problem.instance}; quote it with the time to help@supliful.com)` : ""}`;
  }
  return err?.message || String(err);
}

/** Pure request handler, so the protocol is testable without spawning a process. */
export function createHandler(tools = buildTools()) {
  const byName = new Map(tools.map((t) => [t.name, t]));
  return async function handle(msg) {
    const { id, method, params } = msg;
    const reply = (result) => ({ jsonrpc: "2.0", id, result });
    const fail = (code, message) => ({ jsonrpc: "2.0", id, error: { code, message } });
    if (id === undefined || id === null) return null; // notification: no response
    switch (method) {
      case "initialize": {
        const asked = params?.protocolVersion;
        return reply({
          protocolVersion: PROTOCOL_VERSIONS.includes(asked) ? asked : PROTOCOL_VERSIONS[0],
          capabilities: { tools: { listChanged: false } },
          serverInfo: SERVER_INFO,
          instructions:
            "Supliful private-label tools for the Mediclab Shopify store. Start with supliful_doctor. Run supliful_sync_products and supliful_push_order as dry runs first and get the user's go-ahead before applying. Orders stay in sandbox mode unless the user has set SUPLIFUL_LIVE_ORDERS=1. Never ask the user to paste API keys into chat; use supliful_setup.",
        });
      }
      case "ping":
        return reply({});
      case "tools/list":
        return reply({ tools: tools.map(({ name, description, inputSchema, annotations }) => ({ name, description, inputSchema, annotations })) });
      case "tools/call": {
        const tool = byName.get(params?.name);
        if (!tool) return fail(-32602, `Unknown tool ${params?.name}`);
        try {
          const out = await tool.run(params.arguments || {});
          return reply({ content: [{ type: "text", text: asText(out) }], isError: false });
        } catch (err) {
          log(`${tool.name} failed: ${err.message}`);
          return reply({ content: [{ type: "text", text: errorText(err) }], isError: true });
        }
      }
      case "resources/list":
        return reply({ resources: [] });
      case "prompts/list":
        return reply({ prompts: [] });
      default:
        return fail(-32601, `Method not found: ${method}`);
    }
  };
}

export function serveStdio(handle = createHandler(), input = process.stdin, output = process.stdout) {
  const rl = createInterface({ input, crlfDelay: Infinity });
  rl.on("line", async (line) => {
    if (!line.trim()) return;
    let msg;
    try {
      msg = JSON.parse(line);
    } catch {
      output.write(JSON.stringify({ jsonrpc: "2.0", id: null, error: { code: -32700, message: "Parse error" } }) + "\n");
      return;
    }
    const res = await handle(msg);
    if (res) output.write(JSON.stringify(res) + "\n");
  });
  return rl;
}

if (import.meta.url === pathToFileURL(process.argv[1] || "").href) {
  serveStdio();
  log(`${SERVER_INFO.name} ${SERVER_INFO.version} ready (settings: ${settingsFile()})`);
}
