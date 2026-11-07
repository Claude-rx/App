import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { createHmac } from "node:crypto";
import { verifySupliful, signSupliful, verifyShopify, signShopify } from "../lib/webhooks.mjs";

const body = '{"type":"order.created","occurredAt":"2026-11-07T00:00:00Z","data":{"orderId":"o1","externalOrderId":"shopify-1","testMode":false}}';
const secret = "whsec_test_secret";

test("verifySupliful accepts a valid signature and rejects tampering, staleness, wrong secret", () => {
  const now = 1_800_000_000;
  const header = signSupliful(body, secret, now);
  assert.equal(verifySupliful(body, header, [secret], { now }), true);
  assert.equal(verifySupliful(body + " ", header, [secret], { now }), false, "raw bytes matter");
  assert.equal(verifySupliful(body, header, [secret], { now: now + 301 }), false, "older than 300 s");
  assert.equal(verifySupliful(body, header, ["whsec_other"], { now }), false);
  assert.equal(verifySupliful(body, undefined, [secret], { now }), false);
  assert.equal(verifySupliful(body, "t=abc,v1=zz", [secret], { now }), false);
  assert.equal(verifySupliful(body, header, [], { now }), false);
});

test("verifySupliful matches any v1 during a secret rotation", () => {
  const now = 1_800_000_000;
  const sigNew = createHmac("sha256", "whsec_new").update(`${now}.${body}`).digest("hex");
  const sigOld = createHmac("sha256", "whsec_old").update(`${now}.${body}`).digest("hex");
  const header = `t=${now},v1=${sigNew},v1=${sigOld}`;
  assert.equal(verifySupliful(body, header, ["whsec_old"], { now }), true);
  assert.equal(verifySupliful(body, header, ["whsec_new"], { now }), true);
});

test("our verifier agrees with Supliful's reference signer (openssl, as in sign-webhook.sh)", () => {
  const t = Math.floor(Date.now() / 1000);
  let hex;
  try {
    hex = execFileSync("sh", ["-c", `printf '%s.%s' "$T" "$B" | openssl dgst -sha256 -hmac "$S" | awk '{print $NF}'`], { env: { ...process.env, T: String(t), B: body, S: secret } }).toString().trim();
  } catch {
    return; // openssl not installed: the HMAC test above still covers the algorithm
  }
  assert.equal(verifySupliful(body, `t=${t},v1=${hex}`, [secret]), true);
});

test("verifyShopify checks the base64 HMAC of the raw body", () => {
  const raw = Buffer.from('{"id":1}');
  const h = signShopify(raw, "shpss_secret");
  assert.equal(verifyShopify(raw, h, "shpss_secret"), true);
  assert.equal(verifyShopify(Buffer.from('{"id":2}'), h, "shpss_secret"), false);
  assert.equal(verifyShopify(raw, h, "wrong"), false);
  assert.equal(verifyShopify(raw, undefined, "shpss_secret"), false);
  assert.equal(verifyShopify(raw, h, ""), false);
});
