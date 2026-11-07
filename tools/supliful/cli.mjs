#!/usr/bin/env node
// Supliful <-> Shopify command line. `node tools/supliful/cli.mjs help` lists the commands.
import { writeFileSync, readFileSync, mkdirSync } from "node:fs";
import { join, dirname } from "node:path";
import { pathToFileURL } from "node:url";
import { loadDotEnv, getConfig, ConfigError } from "./lib/config.mjs";
import { SuplifulClient, SuplifulError } from "./lib/supliful.mjs";
import { ShopifyClient } from "./lib/shopify.mjs";
import { JsonStore } from "./lib/store.mjs";
import { syncProducts, formatReport } from "./lib/sync.mjs";
import { forwardShopifyOrder, syncShipments } from "./lib/bridge.mjs";
import { localStatus, isSellable } from "./lib/mapping.mjs";

const HELP = `Supliful <-> Shopify (Mediclab)

  doctor                         check config, the Supliful key (GET /v1/me) and the Shopify token
  ping                           Supliful liveness, no key needed
  me                             the API connection the key acts as
  products [--json]              products published to the connection
  product <uuid>                 one product
  sync [--apply] [--publish] [--update-content] [--prices f.json] [--out report.md]
                                 Supliful products -> Shopify. Dry run unless --apply.
                                 --publish: new products go ACTIVE (default DRAFT for review)
  push-order <shopifyOrderId> [--dry-run] [--force]
                                 send a paid Shopify order's Supliful lines to Supliful
                                 (testMode unless SUPLIFUL_LIVE_ORDERS=1)
  order <id>                     Supliful order by its id or our externalOrderId (shopify-<id>)
  cancel <id>                    cancel while NEW (first ~2 hours); refunds the merchant
  shipments <suplifulOrderId>    turn shipped parcels into Shopify fulfillments with tracking
  reconcile                      re-check every open forwarded order (after a webhook outage)
  test-webhook <event> [--order id]   ask Supliful to send a signed test delivery
  rehearse                       walk a sandbox testMode order NEW -> ACCEPTED -> shipped -> COMPLETED
  labels [--only SKU,SKU] [--proof] render Mediclab label artwork (see tools/supliful/labels)

Environment: tools/supliful/.env.example. Secrets come from the environment or a gitignored .env.`;

function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith("--")) {
      const [k, v] = a.slice(2).split("=", 2);
      if (v !== undefined) args[k] = v;
      else if (argv[i + 1] && !argv[i + 1].startsWith("--")) args[k] = argv[++i];
      else args[k] = true;
    } else args._.push(a);
  }
  return args;
}

const out = (x) => console.log(typeof x === "string" ? x : JSON.stringify(x, null, 2));

function clients(cfg, { needShopify = false } = {}) {
  const store = new JsonStore(cfg.stateDir);
  const supliful = new SuplifulClient({ baseUrl: cfg.supliful.baseUrl, apiKey: cfg.supliful.apiKey, logFile: cfg.supliful.logFile || join(cfg.stateDir, "supliful-requests.jsonl") });
  const shopify = needShopify ? new ShopifyClient(cfg.shopify) : null;
  return { store, supliful, shopify };
}

const SAMPLE_ADDRESS = {
  firstName: "Sandbox",
  lastName: "Rehearsal",
  address1: "2525 Arapahoe Ave",
  address2: "Ste E4",
  city: "Boulder",
  stateCode: "CO",
  zip: "80302",
  countryCode: "US",
};

export async function main(argv = process.argv.slice(2), env = process.env) {
  loadDotEnv();
  const args = parseArgs(argv);
  const [cmd, arg1] = args._;
  const log = (m) => console.error(m);

  switch (cmd) {
    case undefined:
    case "help":
    case "--help":
      return out(HELP);

    case "ping": {
      const cfg = getConfig([], env);
      return out(await new SuplifulClient({ baseUrl: cfg.supliful.baseUrl }).ping());
    }

    case "doctor": {
      const cfg = getConfig([], env);
      const checks = [];
      const add = (name, ok, detail) => checks.push({ ok, name, detail });
      const sup = new SuplifulClient({ baseUrl: cfg.supliful.baseUrl, apiKey: cfg.supliful.apiKey });
      try {
        const p = await sup.ping();
        add("Supliful API reachable", true, p.servedAt);
      } catch (e) {
        add("Supliful API reachable", false, e.message);
      }
      if (!cfg.supliful.apiKey) add("SUPLIFUL_API_KEY set", false, "missing - create it under Supliful > Stores > Supliful API");
      else {
        try {
          const me = await sup.me();
          add("Supliful key valid (GET /v1/me)", true, `connection ${me.connection.name ?? ""} ${me.connection.id}`);
          const products = await sup.listAllProducts();
          add("Products published to the connection", products.length > 0, `${products.length} (${products.filter(isSellable).length} sellable)`);
        } catch (e) {
          add("Supliful key valid (GET /v1/me)", false, e.code || e.message);
        }
      }
      add("Order mode", true, cfg.supliful.liveOrders ? "LIVE - real orders are charged" : "testMode sandbox (set SUPLIFUL_LIVE_ORDERS=1 to go live)");
      if (!cfg.shopify.storeDomain || !cfg.shopify.adminToken) add("Shopify Admin token", false, "SHOPIFY_STORE_DOMAIN / SHOPIFY_ADMIN_TOKEN missing");
      else {
        try {
          const shop = new ShopifyClient(cfg.shopify);
          const d = await shop.graphql("{ shop { name myshopifyDomain } }");
          add("Shopify Admin token", true, `${d.shop.name} (${d.shop.myshopifyDomain})`);
        } catch (e) {
          add("Shopify Admin token", false, e.message);
        }
      }
      add("Webhook secrets", cfg.supliful.webhookSecrets.length > 0 && !!cfg.shopify.webhookSecret, `supliful ${cfg.supliful.webhookSecrets.length} secret(s), shopify ${cfg.shopify.webhookSecret ? "set" : "missing"}`);
      for (const c of checks) out(`${c.ok ? "PASS" : "FAIL"}  ${c.name}${c.detail ? ` - ${c.detail}` : ""}`);
      return checks.every((c) => c.ok) ? 0 : 1;
    }

    case "me": {
      const { supliful } = clients(getConfig(["supliful"], env));
      return out(await supliful.me());
    }

    case "products": {
      const { supliful } = clients(getConfig(["supliful"], env));
      const products = await supliful.listAllProducts();
      if (args.json) return out(products);
      out(`${products.length} products published to this connection\n`);
      for (const p of products) out(`${isSellable(p) ? "  " : "x "}${p.id}  ${(p.sku ?? "-").padEnd(14)} $${String(p.retailPrice).padEnd(7)} ${p.name}${p.status === "discontinued" ? " [discontinued]" : ""}`);
      return 0;
    }

    case "product": {
      const { supliful } = clients(getConfig(["supliful"], env));
      return out(await supliful.getProduct(arg1));
    }

    case "sync": {
      const cfg = getConfig(["supliful", "shopify"], env);
      const { supliful, shopify } = clients(cfg, { needShopify: true });
      const prices = args.prices ? JSON.parse(readFileSync(args.prices, "utf8")) : {};
      const report = await syncProducts({ supliful, shopify, apply: Boolean(args.apply), publish: Boolean(args.publish), updateContent: Boolean(args["update-content"]), prices, vendor: cfg.shopify.vendor, productType: cfg.shopify.productType, log });
      const md = formatReport(report);
      if (args.out) {
        mkdirSync(dirname(args.out), { recursive: true });
        writeFileSync(args.out, md + "\n");
      }
      out(md);
      return report.errors ? 1 : 0;
    }

    case "push-order": {
      if (!arg1) throw new ConfigError("push-order needs a Shopify order id");
      const cfg = getConfig(["supliful", "shopify"], env);
      const { supliful, shopify, store } = clients(cfg, { needShopify: true });
      return out(await forwardShopifyOrder({ orderId: arg1, shopify, supliful, store, liveOrders: cfg.supliful.liveOrders, dryRun: Boolean(args["dry-run"]), force: Boolean(args.force), log }));
    }

    case "order": {
      const { supliful } = clients(getConfig(["supliful"], env));
      const o = await supliful.getOrder(arg1);
      return out({ ...o, local: localStatus(o) });
    }

    case "cancel": {
      const { supliful } = clients(getConfig(["supliful"], env));
      return out(await supliful.cancelOrder(arg1));
    }

    case "shipments": {
      const cfg = getConfig(["supliful", "shopify"], env);
      const { supliful, shopify, store } = clients(cfg, { needShopify: true });
      return out(await syncShipments({ suplifulOrderId: arg1, shopify, supliful, store, notifyCustomer: cfg.shopify.notifyCustomer, log }));
    }

    case "reconcile": {
      const cfg = getConfig(["supliful", "shopify"], env);
      const { supliful, shopify, store } = clients(cfg, { needShopify: true });
      const orders = store.load("orders");
      const results = [];
      for (const [ext, rec] of Object.entries(orders)) {
        if (rec.closed) continue;
        try {
          const r = await syncShipments({ suplifulOrderId: rec.suplifulOrderId, shopify, supliful, store, notifyCustomer: cfg.shopify.notifyCustomer, log });
          if (["completed", "canceled", "returned"].includes(r.local)) store.set("orders", ext, { ...rec, closed: r.local });
          results.push({ order: rec.shopifyName, ...r });
        } catch (e) {
          results.push({ order: rec.shopifyName, status: "error", error: e.code || e.message });
        }
      }
      return out({ checked: results.length, results });
    }

    case "test-webhook": {
      const { supliful } = clients(getConfig(["supliful"], env));
      return out(await supliful.sendTestWebhook(arg1 || "order.created", args.order));
    }

    case "rehearse": {
      const { supliful } = clients(getConfig(["supliful"], env));
      const product = (await supliful.listAllProducts()).find(isSellable);
      if (!product) throw new ConfigError("No sellable product is published to this connection yet. Publish one in Supliful first.");
      const ext = `rehearsal-${Date.now()}`;
      const steps = [];
      const { order } = await supliful.createOrder({ externalOrderId: ext, shippingAddress: SAMPLE_ADDRESS, lines: [{ productId: product.id, quantity: 1 }], testMode: true });
      steps.push({ step: "create", id: order.id, status: order.status });
      const again = await supliful.createOrder({ externalOrderId: ext, shippingAddress: SAMPLE_ADDRESS, lines: [{ productId: product.id, quantity: 1 }], testMode: true });
      steps.push({ step: "idempotent replay", sameOrder: again.order.id === order.id, replay: again.replay });
      for (const t of ["accept", "ship", "complete"]) {
        const r = await supliful.testTransition(order.id, t);
        steps.push({ step: t, status: r.order.status, event: r.event, deliveries: r.deliveries, local: localStatus(r.order), tracking: r.order.shipments?.[0]?.trackingUrl ?? null });
      }
      out({ product: product.name, order: order.id, steps });
      return 0;
    }

    case "labels": {
      const { renderLabels } = await import("./labels/render.mjs");
      const res = await renderLabels({ only: args.only ? String(args.only).split(",") : undefined, proof: Boolean(args.proof), outDir: args.out, log });
      out(res.summary);
      return res.errors ? 1 : 0;
    }

    default:
      throw new ConfigError(`Unknown command "${cmd}". Run: node tools/supliful/cli.mjs help`);
  }
}

if (import.meta.url === pathToFileURL(process.argv[1] || "").href) {
  main()
    .then((code) => process.exit(typeof code === "number" ? code : 0))
    .catch((err) => {
      if (err instanceof ConfigError) console.error(err.message);
      else if (err instanceof SuplifulError) {
        console.error(`Supliful: ${err.message}`);
        if (err.fieldErrors.length) console.error(JSON.stringify(err.fieldErrors, null, 2));
        if (err.problem.instance) console.error(`instance ${err.problem.instance} (quote it to help@supliful.com with the time)`);
      } else console.error(err.stack || err.message);
      process.exit(1);
    });
}
