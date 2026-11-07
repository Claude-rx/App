// Pure mapping between Supliful and Shopify shapes. No I/O here, so every rule is unit-tested.

export const MF_NAMESPACE = "supliful";
export const MF_PRODUCT_ID = "product_id";
export const MF_UPDATED_AT = "updated_at";
export const SYNC_TAG = "supliful";

const escapeHtml = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

/** Plain-text Supliful description -> simple HTML paragraphs. */
export function descriptionToHtml(text) {
  const parts = String(text ?? "").split(/\n{2,}/).map((p) => p.trim()).filter(Boolean);
  return parts.map((p) => `<p>${escapeHtml(p).replace(/\n/g, "<br>")}</p>`).join("\n");
}

export function slugify(s) {
  return String(s ?? "")
    .normalize("NFKD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .replace(/&/g, " and ")
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 200);
}

/** A Supliful product is sellable only while available and active. */
export function isSellable(p) {
  return p?.available === true && p?.status !== "discontinued";
}

/** Supliful weight -> Shopify InventoryItemMeasurement weight. */
export function toShopifyWeight(w) {
  if (!w || typeof w.value !== "number") return undefined;
  const unit = { OUNCE: "OUNCES", POUND: "POUNDS", GRAM: "GRAMS", KILOGRAM: "KILOGRAMS" }[w.unit];
  return unit ? { value: w.value, unit } : undefined;
}

/** Product images, de-duplicated, imageUrl first. */
export function productImages(p) {
  const seen = new Set();
  const out = [];
  for (const u of [p?.imageUrl, ...(p?.mockupUrls || [])]) {
    if (u && !seen.has(u)) {
      seen.add(u);
      out.push(u);
    }
  }
  return out;
}

/**
 * Supliful product -> Shopify productSet input for a NEW product.
 * Price: an explicit override, else Supliful's retailPrice (the merchant's suggestion).
 * Status: ACTIVE only when `publish` is asked and the product is sellable; otherwise DRAFT.
 */
export function toProductSetInput(p, { vendor = "Mediclab", productType = "Specialty Supplements", price, publish = false, extraTags = [] } = {}) {
  if (!p?.id || !p?.name) throw new Error("Supliful product needs id and name");
  const finalPrice = price ?? p.retailPrice;
  if (finalPrice === undefined || finalPrice === null || Number.isNaN(Number(finalPrice))) throw new Error(`No price for ${p.name}`);
  const weight = toShopifyWeight(p.weight);
  const variant = {
    optionValues: [{ optionName: "Title", name: "Default Title" }],
    price: Number(finalPrice).toFixed(2),
    inventoryPolicy: "CONTINUE", // Supliful holds the stock; Shopify must not oversell-block it
    inventoryItem: { tracked: false, requiresShipping: true, ...(p.sku ? { sku: p.sku } : {}), ...(weight ? { measurement: { weight } } : {}) },
  };
  if (p.sku) variant.sku = p.sku;
  return {
    title: p.name,
    handle: slugify(p.name),
    descriptionHtml: descriptionToHtml(p.description || p.shortDescription),
    vendor,
    productType,
    status: publish && isSellable(p) ? "ACTIVE" : "DRAFT",
    tags: [...new Set([SYNC_TAG, ...extraTags])],
    productOptions: [{ name: "Title", values: [{ name: "Default Title" }] }],
    variants: [variant],
    files: productImages(p).map((url, i) => ({ originalSource: url, contentType: "IMAGE", alt: i === 0 ? p.name : `${p.name} ${i + 1}` })),
    metafields: linkMetafields(p),
  };
}

/** The metafields that tie a Shopify product to its Supliful product. */
export function linkMetafields(p) {
  return [
    { namespace: MF_NAMESPACE, key: MF_PRODUCT_ID, type: "single_line_text_field", value: p.id },
    { namespace: MF_NAMESPACE, key: MF_UPDATED_AT, type: "single_line_text_field", value: String(p.updatedAt ?? "") },
  ];
}

/**
 * Decide what to do with one Supliful product given the Shopify catalogue.
 * shopifyIndex: { byLinkId: Map<suplifulId, shopProduct>, bySku: Map<sku, shopProduct[]> }
 * Returns {action, reason, shopify?} where action is one of:
 *   create   — no Shopify product yet
 *   link     — matched by SKU, not linked yet: add metafields, leave the merchant's copy alone
 *   update   — linked, Supliful content changed (updatedAt differs)
 *   hide     — linked and Supliful says stop selling, Shopify product still ACTIVE
 *   ok       — nothing to do
 *   conflict — SKU matches several Shopify products; a person must choose
 *   skip     — unsellable and not in Shopify: don't create it
 */
export function planProduct(p, shopifyIndex) {
  const linked = shopifyIndex.byLinkId.get(p.id);
  const sellable = isSellable(p);
  if (linked) {
    if (!sellable && linked.status === "ACTIVE") return { action: "hide", reason: p.status === "discontinued" ? "discontinued" : "unavailable", shopify: linked };
    if (String(linked.suplifulUpdatedAt ?? "") !== String(p.updatedAt ?? "")) return { action: "update", reason: "supliful content changed", shopify: linked };
    return { action: "ok", reason: "in sync", shopify: linked };
  }
  const bySku = p.sku ? shopifyIndex.bySku.get(p.sku) || [] : [];
  const unlinked = bySku.filter((s) => !s.suplifulId);
  if (unlinked.length === 1) return { action: "link", reason: `SKU ${p.sku} matches`, shopify: unlinked[0] };
  if (unlinked.length > 1) return { action: "conflict", reason: `SKU ${p.sku} matches ${unlinked.length} Shopify products` };
  if (!sellable) return { action: "skip", reason: "not sellable in Supliful" };
  return { action: "create", reason: "not in Shopify" };
}

/** Build the lookup used by planProduct from Shopify products (see shopify.mjs listCatalog). */
export function indexShopify(products) {
  const byLinkId = new Map();
  const bySku = new Map();
  for (const s of products) {
    if (s.suplifulId) byLinkId.set(s.suplifulId, s);
    for (const sku of s.skus || []) {
      if (!sku) continue;
      if (!bySku.has(sku)) bySku.set(sku, []);
      bySku.get(sku).push(s);
    }
  }
  return { byLinkId, bySku };
}

// ---- orders ---------------------------------------------------------------------------------

/** The externalOrderId (and idempotency key) for a Shopify order. Stable across retries. */
export const externalIdFor = (shopifyOrderId) => `shopify-${String(shopifyOrderId).replace(/^gid:\/\/shopify\/Order\//, "")}`;

/** Shopify order id (numeric) back from an externalOrderId, or null. */
export const shopifyIdFromExternal = (ext) => {
  const m = /^shopify-(\d+)$/.exec(String(ext ?? ""));
  return m ? m[1] : null;
};

const clip = (s, n) => (s === undefined || s === null || s === "" ? undefined : String(s).slice(0, n));

/** Shopify (REST webhook or GraphQL) address -> Supliful OrderAddress. Throws when unusable. */
export function toSuplifulAddress(a) {
  if (!a) throw new Error("Order has no shipping address");
  const first = a.first_name ?? a.firstName ?? "";
  const last = a.last_name ?? a.lastName ?? "";
  const name = a.name ?? `${first} ${last}`.trim();
  const [nFirst, ...rest] = String(name).trim().split(/\s+/);
  const out = {
    firstName: clip(first || nFirst, 100),
    lastName: clip(last || rest.join(" ") || nFirst, 100),
    name: clip(name, 200),
    company: clip(a.company, 200),
    phone: clip(a.phone, 50),
    address1: clip(a.address1, 200),
    address2: clip(a.address2, 200),
    city: clip(a.city, 100),
    stateCode: clip(a.province_code ?? a.provinceCode, 10),
    zip: clip(a.zip, 20),
    countryCode: clip(a.country_code ?? a.countryCodeV2 ?? a.countryCode, 2),
  };
  const missing = ["firstName", "lastName", "address1", "city", "zip", "countryCode"].filter((k) => !out[k]);
  if (missing.length) throw new Error(`Shipping address is missing ${missing.join(", ")}`);
  for (const k of Object.keys(out)) if (out[k] === undefined) delete out[k];
  return out;
}

/**
 * Shopify order line items -> Supliful lines. `variantMap` maps a Shopify variant id (numeric or
 * gid) to a Supliful product id; lines without a mapping are not Supliful's and are returned in
 * `unmapped`. Quantities for the same product are summed. Refunded/removed quantity is excluded.
 */
export function toSuplifulLines(lineItems, variantMap) {
  const qty = new Map();
  const unmapped = [];
  const key = (v) => String(v ?? "").replace(/^gid:\/\/shopify\/ProductVariant\//, "");
  for (const li of lineItems || []) {
    const variantId = key(li.variant_id ?? li.variantId ?? li.variant?.id);
    const productId = variantMap.get(variantId);
    const q = Number(li.current_quantity ?? li.currentQuantity ?? li.quantity ?? 0);
    if (!productId) {
      unmapped.push({ title: li.title ?? li.name, sku: li.sku, variantId });
      continue;
    }
    if (q > 0) qty.set(productId, (qty.get(productId) || 0) + q);
  }
  const lines = [...qty].map(([productId, quantity]) => ({ productId, quantity }));
  return { lines, unmapped };
}

/** Supliful OrderDetail -> one local status word (per the skill's webhook guidance). */
export function localStatus(order) {
  if (!order) return "unknown";
  if (["CANCELED", "RETURNED", "COMPLETED"].includes(order.status)) return order.status.toLowerCase();
  const shippedLineIds = new Set((order.shipments || []).filter((s) => s.status === "shipped").flatMap((s) => s.lineIds || []));
  const lines = order.lines || [];
  if (lines.length && lines.every((l) => shippedLineIds.has(l.id))) return "shipped";
  if (shippedLineIds.size) return "partially_shipped";
  if (["ACCEPTED", "IN_PROGRESS"].includes(order.status)) return "accepted";
  return order.onHold ? "on_hold" : "submitted";
}

/**
 * For one Supliful shipment, the quantity shipped per Supliful product id.
 * A product can sit on several lines, so quantities are summed by productId.
 */
export function shipmentQuantities(order, shipment) {
  const ids = new Set(shipment.lineIds || []);
  const out = new Map();
  for (const l of order.lines || []) if (ids.has(l.id)) out.set(l.productId, (out.get(l.productId) || 0) + l.quantity);
  return out;
}

/**
 * Pick Shopify fulfillment-order line items to fulfil for a shipment.
 * fulfillmentOrders: [{id, status, lineItems: [{id, remainingQuantity, suplifulProductId}]}]
 * Returns FulfillmentOrderLineItemsInput[] (empty if nothing remains).
 */
export function fulfillmentLines(fulfillmentOrders, qtyByProduct) {
  const remaining = new Map(qtyByProduct);
  const out = [];
  for (const fo of fulfillmentOrders || []) {
    if (!["OPEN", "IN_PROGRESS"].includes(fo.status)) continue;
    const items = [];
    for (const li of fo.lineItems || []) {
      const want = remaining.get(li.suplifulProductId) || 0;
      const take = Math.min(want, li.remainingQuantity || 0);
      if (take > 0) {
        items.push({ id: li.id, quantity: take });
        remaining.set(li.suplifulProductId, want - take);
      }
    }
    if (items.length) out.push({ fulfillmentOrderId: fo.id, fulfillmentOrderLineItems: items });
  }
  return out;
}

/** Best-effort carrier name from a tracking URL, for Shopify's tracking company field. */
export function carrierFromUrl(url) {
  const u = String(url ?? "").toLowerCase();
  if (u.includes("usps")) return "USPS";
  if (u.includes("ups.com")) return "UPS";
  if (u.includes("fedex")) return "FedEx";
  if (u.includes("dhl")) return "DHL Express";
  if (u.includes("canadapost")) return "Canada Post";
  if (u.includes("royalmail")) return "Royal Mail";
  return undefined;
}
