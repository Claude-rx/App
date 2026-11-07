// Configuration, read once from the environment (and an optional gitignored .env file).
// Secrets are never logged, never defaulted, never written anywhere by this module.
import { readFileSync, existsSync } from "node:fs";
import { resolve } from "node:path";

/** Load KEY=VALUE lines from a .env file into process.env without overwriting set vars. */
export function loadDotEnv(file = resolve(process.cwd(), ".env")) {
  if (!existsSync(file)) return false;
  for (const raw of readFileSync(file, "utf8").split(/\r?\n/)) {
    const line = raw.trim();
    if (!line || line.startsWith("#")) continue;
    const eq = line.indexOf("=");
    if (eq < 1) continue;
    const key = line.slice(0, eq).trim();
    let val = line.slice(eq + 1).trim();
    if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) val = val.slice(1, -1);
    if (process.env[key] === undefined) process.env[key] = val;
  }
  return true;
}

export class ConfigError extends Error {
  constructor(message) {
    super(message);
    this.name = "ConfigError";
  }
}

const truthy = (v) => /^(1|true|yes|on)$/i.test(String(v ?? "").trim());

/**
 * Build the config object. `need` lists the groups the caller requires: "supliful", "shopify",
 * "webhooks". A missing required value throws ConfigError naming the variable (never its value).
 */
export function getConfig(need = [], env = process.env) {
  const cfg = {
    supliful: {
      baseUrl: (env.SUPLIFUL_BASE_URL || "https://public-api.supliful.com").replace(/\/+$/, ""),
      apiKey: env.SUPLIFUL_API_KEY?.trim() || "",
      webhookSecrets: (env.SUPLIFUL_WEBHOOK_SECRETS || "").split(",").map((s) => s.trim()).filter(Boolean),
      // Orders are sandbox (testMode) unless this is explicitly switched on. A real order is charged.
      liveOrders: truthy(env.SUPLIFUL_LIVE_ORDERS),
      logFile: env.SUPLIFUL_LOG_FILE || "",
    },
    shopify: {
      storeDomain: (env.SHOPIFY_STORE_DOMAIN || "").replace(/^https?:\/\//, "").replace(/\/+$/, ""),
      adminToken: env.SHOPIFY_ADMIN_TOKEN?.trim() || "",
      apiVersion: env.SHOPIFY_API_VERSION || "2026-10",
      webhookSecret: env.SHOPIFY_WEBHOOK_SECRET?.trim() || "",
      vendor: env.SHOPIFY_VENDOR || "Mediclab",
      productType: env.SHOPIFY_PRODUCT_TYPE || "Specialty Supplements",
      notifyCustomer: env.SHOPIFY_NOTIFY_CUSTOMER === undefined ? true : truthy(env.SHOPIFY_NOTIFY_CUSTOMER),
    },
    stateDir: env.SUPLIFUL_STATE_DIR || resolve(process.cwd(), ".supliful-state"),
    port: Number(env.PORT || 8787),
  };

  const missing = [];
  if (need.includes("supliful") && !cfg.supliful.apiKey) missing.push("SUPLIFUL_API_KEY");
  if (need.includes("shopify")) {
    if (!cfg.shopify.storeDomain) missing.push("SHOPIFY_STORE_DOMAIN");
    if (!cfg.shopify.adminToken) missing.push("SHOPIFY_ADMIN_TOKEN");
  }
  if (need.includes("webhooks")) {
    if (!cfg.supliful.webhookSecrets.length) missing.push("SUPLIFUL_WEBHOOK_SECRETS");
    if (!cfg.shopify.webhookSecret) missing.push("SHOPIFY_WEBHOOK_SECRET");
  }
  if (missing.length) {
    throw new ConfigError(
      `Missing ${missing.join(", ")}. Set ${missing.length > 1 ? "them" : "it"} in the environment or a gitignored .env ` +
        `(see tools/supliful/.env.example).`,
    );
  }
  return cfg;
}
