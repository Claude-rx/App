import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { once } from "node:events";
import { SuplifulClient } from "../lib/supliful.mjs";
import { ShopifyClient } from "../lib/shopify.mjs";
import { JsonStore } from "../lib/store.mjs";
import { syncProducts, formatReport } from "../lib/sync.mjs";
import { forwardShopifyOrder, syncShipments, handleSuplifulEvent, TAG_HOLD } from "../lib/bridge.mjs";
import { signSupliful, signShopify } from "../lib/webhooks.mjs";
import { createBridgeServer } from "../server.mjs";
import { FakeSupliful, FakeShopify, product } from "./fakes.mjs";

function setup({ products = [] } = {}) {
  const sup = new FakeSupliful({ products });
  const shop = new FakeShopify();
  const supliful = new SuplifulClient({ baseUrl: "https://public-api.supliful.com", apiKey: sup.key, fetch: sup.fetch, baseDelayMs: 1 });
  const shopify = new ShopifyClient({ storeDomain: "mediclab-2.myshopify.com", adminToken: "shpat_test", fetch: shop.fetch, baseDelayMs: 1 });
  const store = new JsonStore(mkdtempSync(join(tmpdir(), "supl-state-")));
  return { sup, shop, supliful, shopify, store };
}

test("sync: dry run writes nothing; apply creates, links and hides as planned", async () => {
  const mag = product({ name: "Magnesium Glycinate", sku: "MLX-MAG-GLY" });
  const fresh = product({ name: "Ashwagandha", sku: "MLX-ASHW-NEW", retailPrice: 35 });
  const gone = product({ name: "Old Thing", sku: "OLD-1", status: "discontinued", available: false });
  const notYet = product({ name: "Unavailable New", sku: "NEW-2", available: false });
  const { shop, supliful, shopify } = setup({ products: [mag, fresh, gone, notYet] });
  shop.addProduct({ title: "Magnesium Glycinate", sku: "MLX-MAG-GLY" }); // existing, curated copy
  const linkedOld = shop.addProduct({ title: "Old Thing", sku: "OLD-1", link: gone.id, updatedAt: gone.updatedAt });
  shop.addProduct({ title: "Wegovy", sku: "WEGO-025" }); // not Supliful's

  const dry = await syncProducts({ supliful, shopify });
  assert.deepEqual(dry.counts, { link: 1, create: 1, hide: 1, skip: 1 });
  assert.equal(shop.mutations.length, 0, "dry run never writes");
  assert.match(formatReport(dry), /DRY RUN - 4 Supliful products/);

  const run = await syncProducts({ supliful, shopify, apply: true });
  assert.equal(run.errors, 0);
  const created = shop.products.find((p) => p.title === "Ashwagandha");
  assert.equal(created.status, "DRAFT", "new products wait for review");
  assert.equal(created.metafields["supliful.product_id"], fresh.id);
  const linked = shop.products.find((p) => p.title === "Magnesium Glycinate");
  assert.equal(linked.metafields["supliful.product_id"], mag.id);
  assert.ok(!shop.mutations.some((m) => m.op === "SuplifulProductSet" && m.v.identifier?.id === linked.id), "linking never overwrites the merchant's copy");
  assert.equal(linkedOld.status, "DRAFT", "discontinued product hidden");

  shop.mutations.length = 0;
  const again = await syncProducts({ supliful, shopify, apply: true });
  assert.deepEqual(again.counts, { ok: 3, skip: 1 });
  assert.equal(shop.mutations.length, 0, "second run is a no-op");
});

test("sync --publish activates new sellable products; --update-content rewrites linked copy", async () => {
  const p = product({ name: "Lion's Mane", sku: "MLX-LION" });
  const { shop, sup, supliful, shopify } = setup({ products: [p] });
  await syncProducts({ supliful, shopify, apply: true, publish: true });
  assert.equal(shop.products[0].status, "ACTIVE");
  sup.products[0] = { ...p, name: "Lion's Mane Mushroom", updatedAt: "2026-11-05T00:00:00.000Z" };
  const r = await syncProducts({ supliful, shopify, apply: true, updateContent: true });
  assert.equal(r.counts.update, 1);
  assert.equal(shop.products[0].title, "Lion's Mane Mushroom");
  assert.equal(shop.products[0].metafields["supliful.updated_at"], "2026-11-05T00:00:00.000Z");
});

async function linkedSetup() {
  const mag = product({ name: "Magnesium Glycinate", sku: "MLX-MAG-GLY" });
  const d3 = product({ name: "D3 + K2", sku: "MLX-D3K2" });
  const ctx = setup({ products: [mag, d3] });
  const pMag = ctx.shop.addProduct({ title: "Magnesium Glycinate", sku: "MLX-MAG-GLY", link: mag.id });
  const pD3 = ctx.shop.addProduct({ title: "D3 + K2", sku: "MLX-D3K2", link: d3.id });
  const pGlp = ctx.shop.addProduct({ title: "Wegovy", sku: "WEGO-025" });
  return { ...ctx, mag, d3, pMag, pD3, pGlp };
}

test("forwardShopifyOrder sends only Supliful lines, in testMode, once", async () => {
  const { sup, shop, supliful, shopify, store, mag, pMag, pD3, pGlp } = await linkedSetup();
  const order = shop.addOrder({ lines: [{ product: pMag, quantity: 2 }, { product: pD3, quantity: 1 }, { product: pGlp, quantity: 1 }] });
  const r = await forwardShopifyOrder({ orderId: order.id, shopify, supliful, store });
  assert.equal(r.status, "sent");
  assert.equal(r.testMode, true);
  assert.equal(r.unmapped.length, 1, "the GLP-1 line stays in Shopify");
  const body = sup.calls.find((c) => c.path === "/v1/orders").body;
  assert.equal(body.externalOrderId, `shopify-${order.id.split("/").pop()}`);
  assert.equal(body.testMode, true);
  assert.deepEqual(body.lines.find((l) => l.productId === mag.id), { productId: mag.id, quantity: 2 });
  assert.deepEqual(body.shippingAddress, { firstName: "Ada", lastName: "Lovelace", name: "Ada Lovelace", phone: "+1 555 0100", address1: "1 Main St", city: "Denver", stateCode: "CO", zip: "80202", countryCode: "US" });
  assert.ok(order.tags.includes("supliful-sent") && order.tags.includes("supliful-test"));
  const again = await forwardShopifyOrder({ orderId: order.id, shopify, supliful, store });
  assert.equal(again.status, "replayed");
  assert.equal(sup.orders.size, 1, "never a duplicate order");
  assert.equal(store.get("orders", body.externalOrderId).suplifulOrderId, r.suplifulOrderId);
});

test("forwardShopifyOrder: live mode, and the skip rules", async () => {
  const { sup, shop, supliful, shopify, store, pMag, pGlp } = await linkedSetup();
  const live = shop.addOrder({ lines: [{ product: pMag, quantity: 1 }] });
  const r = await forwardShopifyOrder({ orderId: live.id, shopify, supliful, store, liveOrders: true });
  assert.equal(r.testMode, false);
  assert.ok(!("testMode" in sup.calls.find((c) => c.path === "/v1/orders").body), "real orders omit testMode");

  assert.equal((await forwardShopifyOrder({ orderId: shop.addOrder({ lines: [{ product: pMag, quantity: 1 }], financial: "PENDING" }).id, shopify, supliful, store })).reason, "financial status PENDING");
  assert.equal((await forwardShopifyOrder({ orderId: shop.addOrder({ lines: [{ product: pMag, quantity: 1 }], cancelledAt: "2026-11-01" }).id, shopify, supliful, store })).reason, "order is cancelled");
  assert.equal((await forwardShopifyOrder({ orderId: shop.addOrder({ lines: [{ product: pGlp, quantity: 1 }] }).id, shopify, supliful, store })).reason, "no Supliful products on this order");
  const dry = await forwardShopifyOrder({ orderId: shop.addOrder({ lines: [{ product: pMag, quantity: 1 }] }).id, shopify, supliful, store, dryRun: true });
  assert.equal(dry.status, "dry-run");
  assert.equal(dry.request.shippingAddress.address1, "[redacted]", "dry runs never print the buyer's address");
});

test("shipments become Shopify fulfillments with tracking, partial parcels included, exactly once", async () => {
  const { sup, shop, supliful, shopify, store, pMag, pD3, pGlp } = await linkedSetup();
  const order = shop.addOrder({ lines: [{ product: pMag, quantity: 2 }, { product: pD3, quantity: 1 }, { product: pGlp, quantity: 1 }] });
  const { suplifulOrderId } = await forwardShopifyOrder({ orderId: order.id, shopify, supliful, store });
  const so = sup.find(suplifulOrderId);

  // nothing shipped yet
  assert.deepEqual((await syncShipments({ suplifulOrderId, shopify, supliful, store })).results, []);
  // first parcel: magnesium only, no tracking yet -> wait
  const s1 = sup.ship(suplifulOrderId, [so.lines.find((l) => l.quantity === 2).id], { tracking: false });
  assert.equal((await syncShipments({ suplifulOrderId, shopify, supliful, store })).results[0].status, "waiting-for-tracking");
  const shp = so.shipments.find((s) => s.id === s1);
  shp.trackingNumber = "9400111";
  shp.trackingUrl = "https://tools.usps.com/go/TrackConfirmAction?tLabels=9400111";
  let r = await syncShipments({ suplifulOrderId, shopify, supliful, store });
  assert.equal(r.results[0].status, "fulfilled");
  assert.equal(r.local, "partially_shipped");
  const f1 = shop.mutations.filter((m) => m.op === "SuplifulFulfil")[0].v.fulfillment;
  assert.deepEqual(f1.trackingInfo, { number: "9400111", url: "https://tools.usps.com/go/TrackConfirmAction?tLabels=9400111", company: "USPS" });
  assert.equal(f1.lineItemsByFulfillmentOrder[0].fulfillmentOrderLineItems[0].quantity, 2);
  assert.equal(f1.notifyCustomer, true);
  // second parcel
  sup.ship(suplifulOrderId);
  r = await syncShipments({ suplifulOrderId, shopify, supliful, store });
  assert.deepEqual(r.results.map((x) => x.status), ["already-fulfilled", "fulfilled"]);
  assert.equal(r.local, "shipped");
  // GLP-1 line untouched
  const glpLine = order.fulfillmentOrders.nodes[0].lineItems.nodes.find((li) => !li.variant.product.metafield);
  assert.equal(glpLine.remainingQuantity, 1);
  // replays change nothing
  const before = shop.mutations.length;
  await syncShipments({ suplifulOrderId, shopify, supliful, store });
  assert.equal(shop.mutations.length, before);
});

test("events: test deliveries are ignored, holds and cancels tag the order, products sync", async () => {
  const { sup, shop, supliful, shopify, store, pMag } = await linkedSetup();
  const order = shop.addOrder({ lines: [{ product: pMag, quantity: 1 }] });
  const { suplifulOrderId } = await forwardShopifyOrder({ orderId: order.id, shopify, supliful, store });
  const ctx = { shopify, supliful, store };

  assert.equal((await handleSuplifulEvent({ type: "order.onHold", data: { orderId: suplifulOrderId, testMode: true } }, ctx)).status, "ignored");
  // our forwarded orders are testMode in tests, so rehearse with processTestEvents
  const rctx = { ...ctx, processTestEvents: true };
  await handleSuplifulEvent({ type: "order.onHold", data: { orderId: suplifulOrderId, reasons: ["out_of_stock"], testMode: true } }, rctx);
  assert.ok(order.tags.includes(TAG_HOLD) && order.tags.includes("supliful-hold:out_of_stock"));
  sup.find(suplifulOrderId).onHoldReasons = ["out_of_stock"];
  await handleSuplifulEvent({ type: "order.onHoldReleased", data: { orderId: suplifulOrderId, testMode: true } }, rctx);
  assert.ok(!order.tags.includes(TAG_HOLD));
  const c = await handleSuplifulEvent({ type: "order.canceled", data: { orderId: suplifulOrderId, testMode: true } }, rctx);
  assert.equal(c.needsPerson, true);
  assert.ok(order.tags.includes("supliful-canceled"));

  const np = product({ name: "Moringa", sku: "MLX-MORI-2" });
  sup.products.push(np);
  const pub = await handleSuplifulEvent({ type: "product.published", data: { productId: np.id, testMode: false } }, ctx);
  assert.equal(pub.counts.create, 1);
  shop.products.find((p) => p.title === "Moringa").status = "ACTIVE";
  const un = await handleSuplifulEvent({ type: "product.unpublished", data: { productId: np.id, testMode: false } }, ctx);
  assert.equal(un.status, "DRAFT");
  assert.equal((await handleSuplifulEvent({ type: "weird.event", data: {} }, ctx)).status, "ignored");
});

test("webhook server: signatures, dedupe, fast 200, async processing", async () => {
  const { shop, supliful, shopify, store, pMag } = await linkedSetup();
  const cfg = { supliful: { webhookSecrets: ["whsec_a"], liveOrders: false }, shopify: { webhookSecret: "shpss_b", notifyCustomer: true } };
  const jobs = [];
  const server = createBridgeServer({ cfg, supliful, shopify, store, log: () => {}, schedule: (fn) => jobs.push(fn) });
  server.listen(0);
  await once(server, "listening");
  const base = `http://127.0.0.1:${server.address().port}`;
  try {
    const order = shop.addOrder({ lines: [{ product: pMag, quantity: 1 }] });
    const raw = JSON.stringify({ id: Number(order.id.split("/").pop()), admin_graphql_api_id: order.id });
    const post = (path, body, headers) => fetch(base + path, { method: "POST", body, headers: { "content-type": "application/json", ...headers } });

    assert.equal((await post("/webhooks/shopify/orders-paid", raw, { "x-shopify-hmac-sha256": "bad" })).status, 401);
    const ok = await post("/webhooks/shopify/orders-paid", raw, { "x-shopify-hmac-sha256": signShopify(Buffer.from(raw), "shpss_b"), "x-shopify-webhook-id": "w1" });
    assert.equal(ok.status, 200);
    assert.equal(jobs.length, 1, "work is deferred until after the response");
    await jobs.shift()();
    assert.equal(store.get("shopify-deliveries", "w1").outcome, "sent");
    const dup = await post("/webhooks/shopify/orders-paid", raw, { "x-shopify-hmac-sha256": signShopify(Buffer.from(raw), "shpss_b"), "x-shopify-webhook-id": "w1" });
    assert.deepEqual(await dup.json(), { duplicate: true });

    const ev = JSON.stringify({ type: "order.created", occurredAt: new Date().toISOString(), data: { orderId: "test_x", externalOrderId: null, testMode: true } });
    assert.equal((await post("/webhooks/supliful", ev, { "x-supliful-signature": signSupliful(ev, "whsec_wrong"), "x-supliful-idempotency-key": "k1" })).status, 401);
    assert.equal(store.get("supliful-deliveries", "k1"), undefined, "a rejected delivery never blocks a valid retry");
    const good = await post("/webhooks/supliful", ev, { "x-supliful-signature": signSupliful(ev, "whsec_a"), "x-supliful-idempotency-key": "k1" });
    assert.equal(good.status, 200);
    await jobs.shift()();
    assert.equal(store.get("supliful-deliveries", "k1").outcome, "ignored", "testMode deliveries change nothing");
    const dup2 = await post("/webhooks/supliful", ev, { "x-supliful-signature": signSupliful(ev, "whsec_a"), "x-supliful-idempotency-key": "k1" });
    assert.deepEqual(await dup2.json(), { duplicate: true });

    const health = await (await fetch(base + "/health")).json();
    assert.equal(health.connection.name, "Mediclab Shopify bridge");
    assert.equal((await fetch(base + "/nope")).status, 404);
  } finally {
    server.close();
  }
});

test("Shopify throttling is retried", async () => {
  const { shop, shopify } = setup();
  shop.throttleNext = 2;
  shop.addProduct({ title: "X", sku: "X" });
  assert.equal((await shopify.listCatalog()).length, 1);
});
