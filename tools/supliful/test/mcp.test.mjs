import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, readFileSync, statSync, writeFileSync, existsSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
import { createHandler, buildTools, makeContext, readEnvFile } from "../mcp.mjs";
import { SuplifulClient } from "../lib/supliful.mjs";
import { ShopifyClient } from "../lib/shopify.mjs";
import { JsonStore } from "../lib/store.mjs";
import { FakeSupliful, FakeShopify, product } from "./fakes.mjs";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..", "..", "..");

function fakeDeps() {
  const mag = product({ name: "Magnesium Glycinate", sku: "MLX-MAG-GLY" });
  const sup = new FakeSupliful({ products: [mag] });
  const shop = new FakeShopify();
  const pMag = shop.addProduct({ title: "Magnesium Glycinate", sku: "MLX-MAG-GLY" });
  const store = new JsonStore(mkdtempSync(join(tmpdir(), "mcp-state-")));
  const cfg = { supliful: { liveOrders: false, apiKey: "k", webhookSecrets: [] }, shopify: { vendor: "Mediclab", productType: "Specialty Supplements", notifyCustomer: true, storeDomain: "x", adminToken: "y" }, stateDir: store.dir };
  const context = () => ({
    cfg,
    store,
    supliful: new SuplifulClient({ baseUrl: "https://public-api.supliful.com", apiKey: "test-key", fetch: sup.fetch, baseDelayMs: 1 }),
    shopify: new ShopifyClient({ storeDomain: "mediclab-2.myshopify.com", adminToken: "t", fetch: shop.fetch, baseDelayMs: 1 }),
  });
  return { sup, shop, mag, pMag, context };
}

const call = async (handle, name, args = {}) => {
  const r = await handle({ jsonrpc: "2.0", id: 9, method: "tools/call", params: { name, arguments: args } });
  return { isError: r.result.isError, text: r.result.content[0].text };
};

test("protocol: initialize, ping, tools/list, notifications, unknown method/tool", async () => {
  const handle = createHandler();
  const init = await handle({ jsonrpc: "2.0", id: 1, method: "initialize", params: { protocolVersion: "2025-03-26" } });
  assert.equal(init.result.protocolVersion, "2025-03-26");
  assert.equal(init.result.serverInfo.name, "supliful-mediclab");
  assert.ok(init.result.capabilities.tools);
  assert.equal((await handle({ jsonrpc: "2.0", id: 2, method: "initialize", params: { protocolVersion: "1999-01-01" } })).result.protocolVersion, "2025-06-18");
  assert.equal(await handle({ jsonrpc: "2.0", method: "notifications/initialized" }), null);
  assert.deepEqual((await handle({ jsonrpc: "2.0", id: 3, method: "ping" })).result, {});
  const list = (await handle({ jsonrpc: "2.0", id: 4, method: "tools/list" })).result.tools;
  assert.equal(list.length, 15);
  for (const t of list) {
    assert.match(t.name, /^supliful_[a-z_]+$/);
    assert.equal(t.inputSchema.type, "object");
    assert.ok(t.description.length > 40, `${t.name} describes itself`);
    assert.equal(typeof t.annotations.readOnlyHint, "boolean");
    assert.ok(!("run" in t));
  }
  assert.equal(list.find((t) => t.name === "supliful_cancel_order").annotations.destructiveHint, true);
  assert.equal((await handle({ jsonrpc: "2.0", id: 5, method: "nope" })).error.code, -32601);
  assert.equal((await handle({ jsonrpc: "2.0", id: 6, method: "tools/call", params: { name: "nope" } })).error.code, -32602);
});

test("tools drive the real library: list, dry-run sync, apply, push order, status", async () => {
  const { sup, shop, mag, pMag, context } = fakeDeps();
  const handle = createHandler(buildTools({ context }));
  const products = JSON.parse((await call(handle, "supliful_list_products")).text);
  assert.equal(products[0].sku, "MLX-MAG-GLY");
  assert.equal(products[0].sellable, true);

  const dry = await call(handle, "supliful_sync_products");
  assert.match(dry.text, /DRY RUN/);
  assert.match(dry.text, /\| link \| Magnesium Glycinate/);
  assert.equal(shop.mutations.length, 0);
  assert.match((await call(handle, "supliful_sync_products", { apply: true })).text, /APPLIED/);
  assert.equal(pMag.metafields["supliful.product_id"], mag.id);

  const order = shop.addOrder({ lines: [{ product: pMag, quantity: 2 }] });
  const preview = JSON.parse((await call(handle, "supliful_push_order", { shopify_order_id: order.id, dry_run: true })).text);
  assert.equal(preview.status, "dry-run");
  assert.equal(sup.orders.size, 0);
  const sent = JSON.parse((await call(handle, "supliful_push_order", { shopify_order_id: order.id })).text);
  assert.equal(sent.status, "sent");
  assert.equal(sent.testMode, true);
  const status = JSON.parse((await call(handle, "supliful_get_order", { order_id: `shopify-${order.id.split("/").pop()}` })).text);
  assert.equal(status.local, "submitted");
  assert.deepEqual(Object.keys(status.shippingAddress), ["city", "stateCode", "countryCode"], "no street or name in tool output");
  assert.equal(JSON.parse((await call(handle, "supliful_cancel_order", { order_id: sent.suplifulOrderId })).text).status, "CANCELED");
});

test("errors come back as tool errors with guidance, never as protocol crashes", async () => {
  const { sup, context } = fakeDeps();
  sup.key = "rotated";
  const handle = createHandler(buildTools({ context }));
  const r = await call(handle, "supliful_list_products");
  assert.equal(r.isError, true);
  assert.match(r.text, /invalid-api-key/);
});

test("setup creates a private settings file and the server picks up edits without a restart", async () => {
  const home = mkdtempSync(join(tmpdir(), "supl-home-"));
  const saved = { ...process.env };
  try {
    process.env.SUPLIFUL_HOME = home;
    delete process.env.SUPLIFUL_API_KEY;
    delete process.env.SUPLIFUL_ENV_FILE;
    const handle = createHandler();
    const out = JSON.parse((await call(handle, "supliful_setup")).text);
    assert.equal(out.settingsFile, join(home, ".env"));
    assert.equal(out.created, true);
    assert.ok(out.missing.includes("SUPLIFUL_API_KEY"));
    if (process.platform !== "win32") assert.equal(statSync(out.settingsFile).mode & 0o777, 0o600);
    assert.throws(() => makeContext(["supliful"]), /SUPLIFUL_API_KEY/);
    writeFileSync(out.settingsFile, readFileSync(out.settingsFile, "utf8").replace(/^SUPLIFUL_API_KEY=.*$/m, "SUPLIFUL_API_KEY=abc123"));
    assert.equal(makeContext(["supliful"]).cfg.supliful.apiKey, "abc123", "edit picked up live");
    assert.equal(makeContext([]).cfg.stateDir, join(home, "state"));
    assert.equal(JSON.parse((await call(handle, "supliful_setup")).text).created, false, "idempotent");
    assert.deepEqual(readEnvFile(join(home, "missing.env")), {});
  } finally {
    process.env = saved;
  }
});

test("label specs are edited in a private workspace seeded from the defaults", async () => {
  const home = mkdtempSync(join(tmpdir(), "supl-home-"));
  const saved = { ...process.env };
  try {
    process.env.SUPLIFUL_HOME = home;
    const handle = createHandler();
    const all = JSON.parse((await call(handle, "supliful_label_specs")).text);
    assert.equal(all.products.length, 28);
    assert.ok(existsSync(join(home, "labels", "catalog.json")));
    const upd = JSON.parse((await call(handle, "supliful_label_specs", { sku: "MLX-MAG-GLY", set: { net: "120 Capsules", netVerified: true } })).text);
    assert.equal(upd.net, "120 Capsules");
    const c = JSON.parse((await call(handle, "supliful_label_specs", { container: "bottle", set: { widthIn: 8, verified: true } })).text);
    assert.equal(c.widthIn, 8);
    const b = JSON.parse((await call(handle, "supliful_label_specs", { brand: { distributorAddress: "1 Test St" } })).text);
    assert.equal(b.brand.distributorAddress, "1 Test St");
    assert.equal((await call(handle, "supliful_label_specs", { sku: "NOPE" })).isError, true);
    assert.equal((await call(handle, "supliful_label_specs", { container: "crate" })).isError, true);
    const specs = JSON.parse(readFileSync(join(home, "labels", "specs.json"), "utf8"));
    assert.equal(specs.products.find((p) => p.sku === "MLX-MAG-GLY").netVerified, true);
    assert.equal(specs.containers.bottle.verified, true);
  } finally {
    process.env = saved;
  }
});

test("the packaged plugin server starts on its own and speaks MCP over stdio", { skip: !existsSync(join(ROOT, "plugins/supliful-mediclab/server/mcp.mjs")) && "plugin not built" }, async () => {
  const home = mkdtempSync(join(tmpdir(), "supl-home-"));
  const child = spawn(process.execPath, [join(ROOT, "plugins/supliful-mediclab/server/mcp.mjs")], { env: { PATH: process.env.PATH, SUPLIFUL_HOME: home }, stdio: ["pipe", "pipe", "pipe"] });
  const lines = [];
  child.stdout.on("data", (d) => lines.push(...d.toString().split("\n").filter(Boolean)));
  const send = (m) => child.stdin.write(JSON.stringify(m) + "\n");
  send({ jsonrpc: "2.0", id: 1, method: "initialize", params: { protocolVersion: "2025-06-18", capabilities: {}, clientInfo: { name: "test", version: "1" } } });
  send({ jsonrpc: "2.0", method: "notifications/initialized" });
  send({ jsonrpc: "2.0", id: 2, method: "tools/list" });
  send({ jsonrpc: "2.0", id: 3, method: "tools/call", params: { name: "supliful_label_specs", arguments: { sku: "MLX-BEET" } } });
  for (let i = 0; i < 100 && lines.length < 3; i++) await new Promise((r) => setTimeout(r, 50));
  child.kill();
  const msgs = lines.map((l) => JSON.parse(l));
  assert.equal(msgs.length, 3, "only protocol messages on stdout");
  assert.equal(msgs[0].result.serverInfo.name, "supliful-mediclab");
  assert.equal(msgs[1].result.tools.length, 15);
  assert.equal(JSON.parse(msgs[2].result.content[0].text).name, "Organic Beetroot");
});
