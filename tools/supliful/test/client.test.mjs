import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { SuplifulClient, SuplifulError, problemCode } from "../lib/supliful.mjs";
import { FakeSupliful, product } from "./fakes.mjs";

const make = (fake, extra = {}) => new SuplifulClient({ baseUrl: "https://public-api.supliful.com", apiKey: fake.key, fetch: fake.fetch, baseDelayMs: 1, ...extra });

test("bearer auth, /v1/me, and ping without a key", async () => {
  const fake = new FakeSupliful();
  const c = make(fake);
  assert.equal((await c.me()).connection.name, "Mediclab Shopify bridge");
  assert.equal(fake.calls.at(-1).headers.authorization, "Bearer test-key");
  const anon = new SuplifulClient({ baseUrl: "https://x", fetch: fake.fetch });
  assert.equal((await anon.ping()).status, "ok");
  assert.equal(fake.calls.at(-1).headers.authorization, undefined);
  await assert.rejects(() => anon.me(), /SUPLIFUL_API_KEY is not set/);
});

test("invalid key surfaces as a typed, terminal invalid-api-key error", async () => {
  const fake = new FakeSupliful();
  const c = make(fake, { apiKey: "wrong" });
  await assert.rejects(c.me(), (e) => e instanceof SuplifulError && e.code === "invalid-api-key" && e.status === 401);
  assert.equal(fake.calls.length, 1, "401 is never retried");
});

test("cursor pagination walks every page and never sends an offset", async () => {
  const fake = new FakeSupliful({ products: [product(), product(), product(), product(), product()] });
  const all = await make(fake).listAllProducts();
  assert.equal(all.length, 5);
  assert.equal(fake.calls.length, 3);
  assert.ok(fake.calls.every((c) => !("offset" in Object.fromEntries(new URL("https://x" + c.path).searchParams))));
});

test("429 waits and retries; 500 retries then gives up; 422 is terminal", async () => {
  const fake = new FakeSupliful();
  fake.failures.push({ path: "/v1/me", status: 429, code: "rate-limit-exceeded" });
  assert.ok((await make(fake).me()).connection);
  assert.equal(fake.calls.length, 2);

  const f2 = new FakeSupliful();
  for (let i = 0; i < 4; i++) f2.failures.push({ path: "/v1/me", status: 500, code: "internal-error" });
  await assert.rejects(make(f2).me(), (e) => e.code === "internal-error");
  assert.equal(f2.calls.length, 4, "1 try + 3 retries");

  const f3 = new FakeSupliful();
  f3.failures.push({ path: "/v1/me", status: 422, code: "validation-failed" });
  await assert.rejects(make(f3).me(), (e) => e.code === "validation-failed");
  assert.equal(f3.calls.length, 1);
});

test("a non-JSON proxy error becomes a synthetic problem instead of a crash", async () => {
  const fake = new FakeSupliful();
  fake.failures.push({ path: "/v1/me", status: 403, raw: "<html>blocked</html>" });
  await assert.rejects(make(fake).me(), (e) => e instanceof SuplifulError && e.code === "http-403" && /blocked/.test(e.problem.detail));
  assert.equal(problemCode({ type: "https://developers.supliful.com/errors/order-already-exists" }), "order-already-exists");
});

test("createOrder is idempotent and adopts the existing order on conflicts", async () => {
  const p = product();
  const fake = new FakeSupliful({ products: [p] });
  const c = make(fake);
  const req = { externalOrderId: "shopify-1", shippingAddress: { firstName: "A", lastName: "B", address1: "1", city: "C", zip: "1", countryCode: "US" }, lines: [{ productId: p.id, quantity: 1 }] };
  const first = await c.createOrder(req);
  assert.equal(first.replay, false);
  assert.match(first.order.id, /^test_/, "testMode by default");
  assert.equal(fake.calls.at(-1).body.testMode, true);
  const again = await c.createOrder(req);
  assert.equal(again.replay, true);
  assert.equal(again.order.id, first.order.id);
  // same externalOrderId, different payload -> idempotency-key-reused -> adopt
  const changed = await c.createOrder({ ...req, lines: [{ productId: p.id, quantity: 2 }] });
  assert.equal(changed.adopted, true);
  assert.equal(changed.conflict, "idempotency-key-reused");
  assert.equal(changed.order.id, first.order.id);
  await assert.rejects(c.createOrder({ ...req, externalOrderId: undefined }), /needs externalOrderId/);
});

test("refused lines come back as field errors", async () => {
  const fake = new FakeSupliful({ products: [] });
  await assert.rejects(
    make(fake).createOrder({ externalOrderId: "x", shippingAddress: {}, lines: [{ productId: "nope", quantity: 1 }] }),
    (e) => e.status === 422 && e.fieldErrors[0].path === "lines.productId",
  );
});

test("cancel only while NEW; already-canceled is a 200", async () => {
  const p = product();
  const fake = new FakeSupliful({ products: [p] });
  const c = make(fake);
  const { order } = await c.createOrder({ externalOrderId: "e1", shippingAddress: {}, lines: [{ productId: p.id, quantity: 1 }] });
  assert.equal((await c.cancelOrder("e1")).status, "CANCELED", "by externalOrderId");
  assert.equal((await c.cancelOrder(order.id)).status, "CANCELED");
  const { order: o2 } = await c.createOrder({ externalOrderId: "e2", shippingAddress: {}, lines: [{ productId: p.id, quantity: 1 }] });
  fake.find(o2.id).status = "ACCEPTED";
  await assert.rejects(c.cancelOrder(o2.id), (e) => e.code === "order-not-cancelable" && e.problem.orderStatus === "ACCEPTED");
});

test("the request log never contains the API key", async () => {
  const dir = mkdtempSync(join(tmpdir(), "supl-"));
  const fake = new FakeSupliful();
  const c = make(fake, { logFile: join(dir, "log.jsonl") });
  await c.me();
  fake.failures.push({ path: "/v1/me", status: 404, code: "not-found" });
  await c.me().catch(() => {});
  const log = readFileSync(join(dir, "log.jsonl"), "utf8");
  assert.equal(log.trim().split("\n").length, 2);
  assert.ok(!log.includes(fake.key));
  assert.ok(!/authorization/i.test(log));
});
