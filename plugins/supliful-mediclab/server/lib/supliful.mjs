// Supliful public API client: bearer auth, RFC 9457 problem parsing, the documented retry policy,
// cursor pagination, idempotent order placement, and a request log with the key redacted.
// Contract: https://public-api.supliful.com/v1/openapi.json (see .claude/skills/supliful-api).
import { appendFileSync, mkdirSync } from "node:fs";
import { dirname } from "node:path";

export const DOCS_ERRORS = "https://developers.supliful.com/errors/";

/** A Supliful API failure, carrying the parsed problem document. Branch on `code`, not `status`. */
export class SuplifulError extends Error {
  constructor(problem, { method, path, attempt } = {}) {
    const code = problemCode(problem);
    super(`${method ?? ""} ${path ?? ""} -> ${problem.status} ${code}${problem.detail ? `: ${problem.detail}` : ""}`.trim());
    this.name = "SuplifulError";
    this.status = problem.status;
    this.code = code;
    this.problem = problem;
    this.attempt = attempt;
  }
  /** 422 with errors[] on lines.productId / shippingAddress, or detail only. */
  get fieldErrors() {
    return Array.isArray(this.problem.errors) ? this.problem.errors : [];
  }
  /** The existing order id on order-already-exists / idempotency-key-reused. */
  get existingOrderId() {
    return this.problem.orderId ?? null;
  }
}

export function problemCode(problem) {
  const t = problem?.type || "";
  if (t.startsWith("http")) return t.split("/").filter(Boolean).pop();
  return t || `http-${problem?.status ?? "error"}`;
}

/** Wrap any non-problem body (proxy HTML, empty) into a synthetic problem document. */
export async function parseProblem(res, instance) {
  const text = await res.text();
  try {
    const body = JSON.parse(text);
    if (body && typeof body === "object" && (body.type || body.title)) return { status: res.status, ...body };
    return { type: `http-${res.status}`, title: res.statusText, status: res.status, detail: text.slice(0, 500), instance };
  } catch {
    return { type: `http-${res.status}`, title: res.statusText || "Non-JSON response", status: res.status, detail: text.slice(0, 500), instance };
  }
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export class SuplifulClient {
  /**
   * @param {object} o
   * @param {string} o.baseUrl
   * @param {string} [o.apiKey]   required for every call but ping()
   * @param {string} [o.logFile]  JSONL request log (Authorization never written)
   * @param {Function} [o.fetch]  injectable for tests
   * @param {number} [o.baseDelayMs] backoff base (tests shrink it)
   */
  constructor({ baseUrl, apiKey = "", logFile = "", fetch: f = globalThis.fetch, baseDelayMs = 2000, maxServerRetries = 3, maxRateRetries = 5, now = () => new Date() } = {}) {
    if (!baseUrl) throw new Error("SuplifulClient needs baseUrl");
    this.baseUrl = baseUrl.replace(/\/+$/, "");
    this.apiKey = apiKey;
    this.logFile = logFile;
    this.fetch = f;
    this.baseDelayMs = baseDelayMs;
    this.maxServerRetries = maxServerRetries;
    this.maxRateRetries = maxRateRetries;
    this.now = now;
  }

  log(entry) {
    if (!this.logFile) return;
    try {
      mkdirSync(dirname(this.logFile), { recursive: true });
      appendFileSync(this.logFile, JSON.stringify({ at: this.now().toISOString(), ...entry }) + "\n");
    } catch {
      /* logging must never break a request */
    }
  }

  /**
   * One request with the documented retry policy:
   * 429 -> wait Retry-After (or exponential backoff), 500/502/503/504 and network errors -> up to
   * maxServerRetries with backoff; every other status is terminal and thrown as SuplifulError.
   */
  async request(method, path, { query, body, headers = {}, auth = true } = {}) {
    if (auth && !this.apiKey) throw new Error("SUPLIFUL_API_KEY is not set");
    const url = new URL(this.baseUrl + path);
    for (const [k, v] of Object.entries(query || {})) if (v !== undefined && v !== null && v !== "") url.searchParams.set(k, String(v));
    const h = { accept: "application/json", ...headers };
    if (auth) h.authorization = `Bearer ${this.apiKey}`;
    if (body !== undefined) h["content-type"] = "application/json";

    let serverTries = 0;
    let rateTries = 0;
    for (let attempt = 1; ; attempt++) {
      const started = Date.now();
      let res;
      try {
        res = await this.fetch(url, { method, headers: h, body: body === undefined ? undefined : JSON.stringify(body) });
      } catch (err) {
        this.log({ method, path, attempt, error: String(err?.message || err) });
        if (++serverTries > this.maxServerRetries) throw err;
        await sleep(this.baseDelayMs * 2 ** (serverTries - 1));
        continue;
      }
      const ms = Date.now() - started;
      if (res.ok) {
        const text = await res.text();
        const data = text ? JSON.parse(text) : null;
        this.log({ method, path, attempt, status: res.status, ms, idempotencyKey: headers["Idempotency-Key"] });
        return { status: res.status, data, headers: res.headers };
      }
      const problem = await parseProblem(res, path);
      this.log({ method, path, attempt, status: res.status, ms, type: problem.type, instance: problem.instance, detail: problem.detail, errors: problem.errors });
      if (res.status === 429 && ++rateTries <= this.maxRateRetries) {
        const ra = Number(res.headers.get("retry-after"));
        await sleep(Number.isFinite(ra) && ra > 0 ? ra * 1000 : this.baseDelayMs * 2 ** (rateTries - 1));
        continue;
      }
      if ([500, 502, 503, 504].includes(res.status) && ++serverTries <= this.maxServerRetries) {
        await sleep(this.baseDelayMs * 2 ** (serverTries - 1));
        continue;
      }
      throw new SuplifulError(problem, { method, path, attempt });
    }
  }

  // ---- endpoints -------------------------------------------------------------------------

  async ping() {
    return (await this.request("GET", "/v1/ping", { auth: false })).data;
  }

  /** {connection: {id, name}} — the safe way to identify which credential is in use. */
  async me() {
    return (await this.request("GET", "/v1/me")).data;
  }

  async listProductsPage({ limit = 100, cursor, sku } = {}) {
    return (await this.request("GET", "/v1/products", { query: { limit, cursor, sku } })).data;
  }

  /** Every product exposed to the connection, following nextCursor (never offsets). */
  async *iterateProducts({ limit = 100, sku } = {}) {
    let cursor;
    do {
      const page = await this.listProductsPage({ limit, cursor, sku });
      for (const p of page.data || []) yield p;
      cursor = page.nextCursor || undefined;
    } while (cursor);
  }

  async listAllProducts(opts) {
    const out = [];
    for await (const p of this.iterateProducts(opts)) out.push(p);
    return out;
  }

  async getProduct(id) {
    return (await this.request("GET", `/v1/products/${encodeURIComponent(id)}`)).data;
  }

  /**
   * Place an order idempotently. `externalOrderId` doubles as the idempotency key, so a retry of
   * the same Shopify order can never create a second Supliful order. On order-already-exists or
   * idempotency-key-reused the existing order is adopted and returned with `adopted: true`.
   */
  async createOrder({ externalOrderId, shippingAddress, lines, testMode = true, idempotencyKey }) {
    if (!externalOrderId && !idempotencyKey) throw new Error("createOrder needs externalOrderId or idempotencyKey");
    const body = { shippingAddress, lines };
    if (externalOrderId) body.externalOrderId = externalOrderId;
    if (testMode) body.testMode = true;
    const headers = {};
    if (idempotencyKey) headers["Idempotency-Key"] = idempotencyKey;
    try {
      const res = await this.request("POST", "/v1/orders", { body, headers });
      return { order: res.data, replay: res.status === 200, adopted: false };
    } catch (err) {
      if (err instanceof SuplifulError && (err.code === "order-already-exists" || err.code === "idempotency-key-reused") && err.existingOrderId) {
        return { order: await this.getOrder(err.existingOrderId), replay: true, adopted: true, conflict: err.code };
      }
      throw err;
    }
  }

  /** Accepts Supliful's id or our externalOrderId. */
  async getOrder(orderId) {
    return (await this.request("GET", `/v1/orders/${encodeURIComponent(orderId)}`)).data;
  }

  async cancelOrder(orderId) {
    return (await this.request("POST", `/v1/orders/${encodeURIComponent(orderId)}/cancel`)).data;
  }

  async sendTestWebhook(event, orderId) {
    return (await this.request("POST", "/v1/test/webhooks", { body: orderId ? { event, orderId } : { event } })).data;
  }

  async testTransition(orderId, transition, extra = {}) {
    return (await this.request("POST", `/v1/test/orders/${encodeURIComponent(orderId)}/transitions`, { body: { transition, ...extra } })).data;
  }
}
