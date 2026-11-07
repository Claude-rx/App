// Webhook signature verification for both directions of the bridge. Always over the raw bytes.
import { createHmac, timingSafeEqual } from "node:crypto";

/**
 * Supliful: `x-supliful-signature: t=<unix>,v1=<hex>[,v1=<hex>]`, HMAC-SHA256 over `${t}.${raw}`
 * keyed by the whole endpoint secret (including its `whsec_` prefix). Any live secret may match
 * (two during a rotation). Deliveries older than `toleranceSec` are rejected.
 */
export function verifySupliful(rawBody, header, secrets, { now = Date.now() / 1000, toleranceSec = 300 } = {}) {
  if (!header || !secrets?.length) return false;
  let t;
  const sigs = [];
  for (const part of String(header).split(",")) {
    const [k, v] = part.trim().split("=", 2);
    if (k === "t") t = Number(v);
    else if (k === "v1" && v) sigs.push(v.toLowerCase());
  }
  if (!t || !Number.isFinite(t) || !sigs.length) return false;
  if (Math.abs(now - t) > toleranceSec) return false;
  const payload = `${t}.${typeof rawBody === "string" ? rawBody : Buffer.from(rawBody).toString("utf8")}`;
  return secrets.some((secret) => {
    const expected = createHmac("sha256", secret).update(payload).digest("hex");
    return sigs.some((s) => /^[0-9a-f]+$/.test(s) && s.length === expected.length && timingSafeEqual(Buffer.from(s, "hex"), Buffer.from(expected, "hex")));
  });
}

/** Build a Supliful signature header (tests and local rehearsal only). */
export function signSupliful(rawBody, secret, t = Math.floor(Date.now() / 1000)) {
  return `t=${t},v1=${createHmac("sha256", secret).update(`${t}.${rawBody}`).digest("hex")}`;
}

/** Shopify: `X-Shopify-Hmac-Sha256` is base64 HMAC-SHA256 of the raw body keyed by the app secret. */
export function verifyShopify(rawBody, header, secret) {
  if (!header || !secret) return false;
  const expected = createHmac("sha256", secret).update(rawBody).digest();
  let got;
  try {
    got = Buffer.from(String(header), "base64");
  } catch {
    return false;
  }
  return got.length === expected.length && timingSafeEqual(got, expected);
}

export function signShopify(rawBody, secret) {
  return createHmac("sha256", secret).update(rawBody).digest("base64");
}
