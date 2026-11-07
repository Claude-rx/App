// In-memory fakes of the Supliful public API and the Shopify Admin GraphQL API, served through
// an injected `fetch`, so the real clients are exercised end to end without the network.

const json = (status, body, headers = {}) =>
  new Response(body === undefined ? "" : JSON.stringify(body), { status, headers: { "content-type": status >= 400 ? "application/problem+json" : "application/json", ...headers } });

const problem = (status, code, detail, extra = {}) => json(status, { type: `https://developers.supliful.com/errors/${code}`, title: code, status, detail, ...extra });

export function product(over = {}) {
  return {
    id: over.id ?? crypto.randomUUID(),
    name: "Magnesium Glycinate",
    shortDescription: "Calm",
    description: "Para one.\n\nPara two.",
    sku: "MLX-MAG-GLY",
    retailPrice: 45,
    imageUrl: "https://cdn.example/mag.png",
    mockupUrls: ["https://cdn.example/mag.png", "https://cdn.example/mag-2.png"],
    dimensions: null,
    weight: { value: 6, unit: "OUNCE" },
    available: true,
    status: "active",
    updatedAt: "2026-11-01T00:00:00.000Z",
    ...over,
  };
}

export class FakeSupliful {
  constructor({ key = "test-key", products = [] } = {}) {
    this.key = key;
    this.products = products;
    this.orders = new Map(); // id -> order detail
    this.byExternal = new Map();
    this.byIdem = new Map();
    this.calls = [];
    this.failures = []; // queue of {path, status, code, headers}
    this.pageSize = 2;
  }
  fetch = async (url, init = {}) => {
    const u = new URL(url);
    const method = init.method || "GET";
    const headers = Object.fromEntries(Object.entries(init.headers || {}).map(([k, v]) => [k.toLowerCase(), v]));
    this.calls.push({ method, path: u.pathname, headers, body: init.body ? JSON.parse(init.body) : undefined });
    const f = this.failures.findIndex((x) => u.pathname.startsWith(x.path));
    if (f >= 0) {
      const x = this.failures.splice(f, 1)[0];
      if (x.raw) return new Response(x.raw, { status: x.status, headers: { "content-type": "text/html", ...(x.headers || {}) } });
      return problem(x.status, x.code, x.detail || x.code, x.extra);
    }
    if (u.pathname === "/v1/ping") return json(200, { status: "ok", servedAt: new Date().toISOString() });
    if (headers.authorization !== `Bearer ${this.key}`) return problem(401, "invalid-api-key", "The API key is missing, invalid or revoked.", { instance: u.pathname });
    if (u.pathname === "/v1/me") return json(200, { connection: { id: "11111111-1111-4111-8111-111111111111", name: "Mediclab Shopify bridge" } });
    if (u.pathname === "/v1/products" && method === "GET") {
      const start = Number(u.searchParams.get("cursor") || 0);
      const limit = Math.min(Number(u.searchParams.get("limit") || 50), this.pageSize);
      const sku = u.searchParams.get("sku");
      const list = sku ? this.products.filter((p) => p.sku === sku) : this.products;
      const data = list.slice(start, start + limit);
      return json(200, { data, nextCursor: start + limit < list.length ? String(start + limit) : null });
    }
    let m;
    if ((m = /^\/v1\/products\/([^/]+)$/.exec(u.pathname))) {
      const p = this.products.find((x) => x.id === m[1]);
      return p ? json(200, p) : problem(404, "not-found", "No such product");
    }
    if (u.pathname === "/v1/orders" && method === "POST") {
      const body = JSON.parse(init.body);
      const key = headers["idempotency-key"] || body.externalOrderId;
      if (!key) return problem(400, "validation-failed", "Send an Idempotency-Key or externalOrderId", { errors: [{ path: "externalOrderId", message: "required" }] });
      const fingerprint = JSON.stringify(body);
      if (this.byIdem.has(key)) {
        const prev = this.byIdem.get(key);
        if (prev.fingerprint !== fingerprint) return problem(422, "idempotency-key-reused", "Key used for another request", { orderId: prev.id });
        return json(200, summary(this.orders.get(prev.id)));
      }
      if (body.externalOrderId && this.byExternal.has(body.externalOrderId)) return problem(409, "order-already-exists", "exists", { orderId: this.byExternal.get(body.externalOrderId) });
      for (const l of body.lines) if (!this.products.some((p) => p.id === l.productId && p.status !== "discontinued")) return problem(422, "validation-failed", "refused", { errors: [{ path: "lines.productId", message: `${l.productId} is not available to this connection` }] });
      const id = (body.testMode ? "test_" : "") + crypto.randomUUID();
      const order = {
        id,
        testMode: Boolean(body.testMode),
        externalOrderId: body.externalOrderId ?? null,
        status: "NEW",
        onHold: false,
        onHoldReasons: [],
        createdAt: new Date().toISOString(),
        shippingAddress: body.shippingAddress,
        lines: body.lines.map((l, i) => ({ id: `${id}-l${i}`, productId: l.productId, quantity: l.quantity, shipmentId: null })),
        shipments: [],
      };
      this.orders.set(id, order);
      this.byIdem.set(key, { id, fingerprint });
      if (body.externalOrderId) this.byExternal.set(body.externalOrderId, id);
      return json(201, summary(order));
    }
    if ((m = /^\/v1\/orders\/([^/]+)$/.exec(u.pathname))) {
      const o = this.find(decodeURIComponent(m[1]));
      return o ? json(200, o) : problem(404, "not-found", "No such order");
    }
    if ((m = /^\/v1\/orders\/([^/]+)\/cancel$/.exec(u.pathname))) {
      const o = this.find(decodeURIComponent(m[1]));
      if (!o) return problem(404, "not-found", "No such order");
      if (o.status === "CANCELED") return json(200, o);
      if (o.status !== "NEW") return problem(409, "order-not-cancelable", "Past its window", { orderStatus: o.status });
      o.status = "CANCELED";
      return json(200, o);
    }
    if (u.pathname === "/v1/test/webhooks") return json(202, { deliveries: 1 });
    if ((m = /^\/v1\/test\/orders\/([^/]+)\/transitions$/.exec(u.pathname))) {
      const o = this.find(decodeURIComponent(m[1]));
      const { transition } = JSON.parse(init.body);
      if (transition === "accept") o.status = "ACCEPTED";
      if (transition === "ship") this.ship(o.id);
      if (transition === "complete") o.status = "COMPLETED";
      return json(200, { order: o, event: transition === "ship" ? "order.shipmentCreated" : transition === "complete" ? "order.completed" : null, deliveries: 1 });
    }
    return problem(404, "not-found", `No route ${method} ${u.pathname}`);
  };
  find(id) {
    return this.orders.get(id) || this.orders.get(this.byExternal.get(id));
  }
  /** Ship some (or all unshipped) lines of an order with tracking. */
  ship(orderId, lineIds, { tracking = true } = {}) {
    const o = this.find(orderId);
    const ids = lineIds || o.lines.filter((l) => !l.shipmentId).map((l) => l.id);
    const sid = `shp_${o.shipments.length + 1}`;
    o.shipments.push({ id: sid, status: "shipped", trackingNumber: tracking ? `9400${o.shipments.length}111` : null, trackingUrl: tracking ? `https://tools.usps.com/go/TrackConfirmAction?tLabels=9400${o.shipments.length}111` : null, createdAt: new Date().toISOString(), lineIds: ids });
    for (const l of o.lines) if (ids.includes(l.id)) l.shipmentId = sid;
    o.status = "IN_PROGRESS";
    return sid;
  }
}

const summary = (o) => ({ id: o.id, testMode: o.testMode, status: o.status, createdAt: o.createdAt, externalOrderId: o.externalOrderId, lines: o.lines.map(({ productId, quantity }) => ({ productId, quantity })) });

let seq = 1000;
const nextId = (type) => `gid://shopify/${type}/${++seq}`;

export class FakeShopify {
  constructor() {
    this.products = []; // {id,title,handle,status,metafields:{key:value},variants:[{id,sku}]}
    this.orders = new Map();
    this.mutations = [];
    this.throttleNext = 0;
  }
  addProduct({ title, sku, status = "ACTIVE", link, updatedAt }) {
    const p = { id: nextId("Product"), title, handle: title.toLowerCase().replace(/\W+/g, "-"), status, metafields: {}, variants: [{ id: nextId("ProductVariant"), sku }] };
    if (link) p.metafields["supliful.product_id"] = link;
    if (updatedAt) p.metafields["supliful.updated_at"] = updatedAt;
    this.products.push(p);
    return p;
  }
  /** A paid order; lines: [{product (fake product), quantity}] */
  addOrder({ lines, financial = "PAID", cancelledAt = null, address }) {
    const id = nextId("Order");
    const lineItems = lines.map((l) => ({ id: nextId("LineItem"), name: l.product.title, sku: l.product.variants[0].sku, currentQuantity: l.quantity, variant: { id: l.product.variants[0].id, product: { metafield: l.product.metafields["supliful.product_id"] ? { value: l.product.metafields["supliful.product_id"] } : null } } }));
    const fo = { id: nextId("FulfillmentOrder"), status: "OPEN", lineItems: { nodes: lineItems.map((li) => ({ id: nextId("FulfillmentOrderLineItem"), remainingQuantity: li.currentQuantity, variant: li.variant })) } };
    const order = {
      id,
      name: `#${1000 + this.orders.size + 1}`,
      displayFinancialStatus: financial,
      displayFulfillmentStatus: "UNFULFILLED",
      cancelledAt,
      tags: [],
      shippingAddress: address ?? { firstName: "Ada", lastName: "Lovelace", name: "Ada Lovelace", company: null, phone: "+1 555 0100", address1: "1 Main St", address2: null, city: "Denver", provinceCode: "CO", zip: "80202", countryCodeV2: "US" },
      lineItems: { nodes: lineItems },
      fulfillmentOrders: { nodes: [fo] },
      fulfillments: [],
    };
    this.orders.set(id, order);
    return order;
  }
  fetch = async (_url, init) => {
    const { query, variables } = JSON.parse(init.body);
    if (this.throttleNext > 0) {
      this.throttleNext--;
      return new Response(JSON.stringify({ errors: [{ message: "Throttled", extensions: { code: "THROTTLED" } }] }), { status: 200 });
    }
    const op = /(?:query|mutation)\s+(\w+)/.exec(query)?.[1] || "anonymous";
    const data = this.handle(op, variables || {}, query);
    return new Response(JSON.stringify({ data }), { status: 200, headers: { "content-type": "application/json" } });
  };
  handle(op, v, query) {
    const mf = (p, key) => (p.metafields[`supliful.${key}`] ? { value: p.metafields[`supliful.${key}`] } : null);
    switch (op) {
      case "anonymous":
        if (query.includes("shop")) return { shop: { name: "Mediclab", myshopifyDomain: "mediclab-2.myshopify.com" } };
        throw new Error("unknown anonymous query");
      case "Catalog": {
        const start = Number(v.after || 0);
        const page = this.products.slice(start, start + 100);
        return { products: { pageInfo: { hasNextPage: start + 100 < this.products.length, endCursor: String(start + 100) }, nodes: page.map((p) => ({ id: p.id, title: p.title, handle: p.handle, status: p.status, linkId: mf(p, "product_id"), linkUpdatedAt: mf(p, "updated_at"), variants: { nodes: p.variants } })) } };
      }
      case "VariantLinks":
        return { nodes: v.ids.map((id) => { const p = this.products.find((x) => x.variants.some((vv) => vv.id === id)); return p ? { id, sku: p.variants[0].sku, product: { id: p.id, metafield: mf(p, "product_id") } } : null; }) };
      case "OrderForSupliful":
        return { order: this.orders.get(v.id) ?? null };
      case "SuplifulProductSet": {
        this.mutations.push({ op, v });
        let p = v.identifier?.id ? this.products.find((x) => x.id === v.identifier.id) : null;
        if (!p) {
          p = { id: nextId("Product"), title: v.input.title, handle: v.input.handle, status: v.input.status, metafields: {}, variants: (v.input.variants || []).map((vv) => ({ id: nextId("ProductVariant"), sku: vv.sku })) };
          this.products.push(p);
        } else if (v.input.title) p.title = v.input.title;
        for (const m of v.input.metafields || []) p.metafields[`${m.namespace}.${m.key}`] = m.value;
        return { productSet: { product: { id: p.id, handle: p.handle, status: p.status }, userErrors: [] } };
      }
      case "SuplifulLink": {
        this.mutations.push({ op, v });
        for (const m of v.metafields) {
          const p = this.products.find((x) => x.id === m.ownerId);
          p.metafields[`${m.namespace}.${m.key}`] = m.value;
        }
        return { metafieldsSet: { metafields: v.metafields.map((m) => ({ id: nextId("Metafield"), key: m.key })), userErrors: [] } };
      }
      case "SuplifulStatus": {
        this.mutations.push({ op, v });
        const p = this.products.find((x) => x.id === v.product.id);
        p.status = v.product.status;
        return { productUpdate: { product: { id: p.id, status: p.status }, userErrors: [] } };
      }
      case "SuplifulFulfil": {
        this.mutations.push({ op, v });
        for (const g of v.fulfillment.lineItemsByFulfillmentOrder) {
          for (const o of this.orders.values()) {
            const fo = o.fulfillmentOrders.nodes.find((x) => x.id === g.fulfillmentOrderId);
            if (!fo) continue;
            for (const it of g.fulfillmentOrderLineItems) {
              const li = fo.lineItems.nodes.find((x) => x.id === it.id);
              if (it.quantity > li.remainingQuantity) return { fulfillmentCreate: { fulfillment: null, userErrors: [{ field: ["quantity"], message: "too many" }] } };
              li.remainingQuantity -= it.quantity;
            }
            if (fo.lineItems.nodes.every((x) => x.remainingQuantity === 0)) fo.status = "CLOSED";
            o.fulfillments.push(v.fulfillment);
          }
        }
        return { fulfillmentCreate: { fulfillment: { id: nextId("Fulfillment"), status: "SUCCESS", trackingInfo: [v.fulfillment.trackingInfo] }, userErrors: [] } };
      }
      case "SuplifulTagsAdd":
      case "SuplifulTagsRemove": {
        this.mutations.push({ op, v });
        const o = this.orders.get(v.id);
        if (o) o.tags = op === "SuplifulTagsAdd" ? [...new Set([...o.tags, ...v.tags])] : o.tags.filter((t) => !v.tags.includes(t));
        return { [op === "SuplifulTagsAdd" ? "tagsAdd" : "tagsRemove"]: { node: { id: v.id }, userErrors: [] } };
      }
      default:
        throw new Error(`FakeShopify: unhandled operation ${op}`);
    }
  }
}
