#!/usr/bin/env node
// Webhook bridge between Shopify and Supliful.
//   POST /webhooks/shopify/orders-paid  Shopify "orders/paid"      -> place the Supliful order
//   POST /webhooks/supliful             every Supliful event        -> fulfil / tag / sync products
//   GET  /health                        liveness, plus which connection the key acts as
// Rules from the Supliful skill: verify signatures over raw bytes, dedupe on the delivery key,
// answer 2xx fast and process afterwards, log every delivery so it can be replayed.
import { createServer as createHttpServer } from "node:http";
import { pathToFileURL } from "node:url";
import { verifySupliful, verifyShopify } from "./lib/webhooks.mjs";
import { forwardShopifyOrder, handleSuplifulEvent } from "./lib/bridge.mjs";

const MAX_BODY = 1024 * 1024;

function readRaw(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    let size = 0;
    req.on("data", (c) => {
      size += c.length;
      if (size > MAX_BODY) {
        reject(Object.assign(new Error("body too large"), { status: 413 }));
        req.destroy();
      } else chunks.push(c);
    });
    req.on("end", () => resolve(Buffer.concat(chunks)));
    req.on("error", reject);
  });
}

const send = (res, status, body) => {
  res.writeHead(status, { "content-type": "application/json" });
  res.end(JSON.stringify(body));
};

/**
 * @param {object} deps { cfg, supliful, shopify, store, log, schedule }
 * `schedule` runs work after the response (default setImmediate); tests pass a collector.
 */
export function createBridgeServer({ cfg, supliful, shopify, store, log = console.log, schedule = (fn) => setImmediate(fn) }) {
  const processTestEvents = /^(1|true)$/i.test(process.env.SUPLIFUL_PROCESS_TEST_EVENTS || "");

  return createHttpServer(async (req, res) => {
    const url = new URL(req.url, "http://local");
    try {
      if (req.method === "GET" && url.pathname === "/health") {
        let connection = null;
        try {
          connection = (await supliful.me()).connection;
        } catch (err) {
          connection = { error: err.code || err.message };
        }
        return send(res, 200, { ok: true, liveOrders: cfg.supliful.liveOrders, connection });
      }

      if (req.method === "POST" && url.pathname === "/webhooks/supliful") {
        const raw = await readRaw(req);
        const key = req.headers["x-supliful-idempotency-key"] || "";
        const valid = verifySupliful(raw.toString("utf8"), req.headers["x-supliful-signature"], cfg.supliful.webhookSecrets);
        if (!valid) {
          store.append("supliful-rejected", { key, signature: Boolean(req.headers["x-supliful-signature"]), bytes: raw.length });
          return send(res, 401, { error: "invalid signature" });
        }
        if (key && store.get("supliful-deliveries", key)) return send(res, 200, { duplicate: true });
        let event;
        try {
          event = JSON.parse(raw.toString("utf8"));
        } catch {
          return send(res, 400, { error: "invalid JSON" });
        }
        store.set("supliful-deliveries", key || `nokey-${Date.now()}`, { type: event.type, occurredAt: event.occurredAt, receivedAt: new Date().toISOString(), outcome: "received" });
        store.append("supliful-events", { key, event });
        send(res, 200, { received: true });
        schedule(async () => {
          try {
            const outcome = await handleSuplifulEvent(event, { shopify, supliful, store, processTestEvents, notifyCustomer: cfg.shopify.notifyCustomer, log });
            store.set("supliful-deliveries", key, { type: event.type, occurredAt: event.occurredAt, outcome: outcome?.status ?? "ok", processedAt: new Date().toISOString() });
            log(`supliful ${event.type}: ${outcome?.status ?? "ok"}`);
          } catch (err) {
            store.set("supliful-deliveries", key, { type: event.type, occurredAt: event.occurredAt, outcome: "error", error: err.message, processedAt: new Date().toISOString() });
            log(`supliful ${event.type} failed: ${err.message}`);
          }
        });
        return;
      }

      if (req.method === "POST" && url.pathname === "/webhooks/shopify/orders-paid") {
        const raw = await readRaw(req);
        if (!verifyShopify(raw, req.headers["x-shopify-hmac-sha256"], cfg.shopify.webhookSecret)) return send(res, 401, { error: "invalid signature" });
        const webhookId = req.headers["x-shopify-webhook-id"] || "";
        if (webhookId && store.get("shopify-deliveries", webhookId)) return send(res, 200, { duplicate: true });
        let payload;
        try {
          payload = JSON.parse(raw.toString("utf8"));
        } catch {
          return send(res, 400, { error: "invalid JSON" });
        }
        const orderId = payload.admin_graphql_api_id || payload.id;
        store.set("shopify-deliveries", webhookId || `nokey-${Date.now()}`, { orderId, receivedAt: new Date().toISOString(), outcome: "received" });
        send(res, 200, { received: true });
        schedule(async () => {
          try {
            const r = await forwardShopifyOrder({ orderId, shopify, supliful, store, liveOrders: cfg.supliful.liveOrders, log });
            store.set("shopify-deliveries", webhookId, { orderId, outcome: r.status, reason: r.reason, suplifulOrderId: r.suplifulOrderId, processedAt: new Date().toISOString() });
          } catch (err) {
            store.set("shopify-deliveries", webhookId, { orderId, outcome: "error", error: err.message, code: err.code, processedAt: new Date().toISOString() });
            log(`forward ${orderId} failed: ${err.message}`);
          }
        });
        return;
      }

      send(res, 404, { error: "not found" });
    } catch (err) {
      send(res, err.status || 500, { error: err.status ? err.message : "internal error" });
    }
  });
}

// ---- run directly --------------------------------------------------------------------------
if (import.meta.url === pathToFileURL(process.argv[1] || "").href) {
  const { loadDotEnv, getConfig } = await import("./lib/config.mjs");
  const { SuplifulClient } = await import("./lib/supliful.mjs");
  const { ShopifyClient } = await import("./lib/shopify.mjs");
  const { JsonStore } = await import("./lib/store.mjs");
  const { join } = await import("node:path");
  loadDotEnv();
  const cfg = getConfig(["supliful", "shopify", "webhooks"]);
  const store = new JsonStore(cfg.stateDir);
  const supliful = new SuplifulClient({ baseUrl: cfg.supliful.baseUrl, apiKey: cfg.supliful.apiKey, logFile: cfg.supliful.logFile || join(cfg.stateDir, "supliful-requests.jsonl") });
  const shopify = new ShopifyClient(cfg.shopify);
  const me = await supliful.me();
  createBridgeServer({ cfg, supliful, shopify, store }).listen(cfg.port, () => {
    console.log(`Supliful bridge on :${cfg.port} - connection ${me.connection.name ?? me.connection.id} - ${cfg.supliful.liveOrders ? "LIVE orders" : "testMode orders"}`);
  });
}
