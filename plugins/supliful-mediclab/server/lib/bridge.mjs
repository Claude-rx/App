// The order bridge: paid Shopify orders -> Supliful, Supliful shipments -> Shopify fulfillments.
// Every handler is idempotent: Supliful dedupes orders on externalOrderId, and shipments already
// turned into fulfillments are remembered in the state store.
import {
  externalIdFor,
  shopifyIdFromExternal,
  toSuplifulAddress,
  toSuplifulLines,
  shipmentQuantities,
  fulfillmentLines,
  carrierFromUrl,
  localStatus,
} from "./mapping.mjs";
import { gid } from "./shopify.mjs";
import { syncProducts, hideLinked } from "./sync.mjs";

export const TAG_SENT = "supliful-sent";
export const TAG_TEST = "supliful-test";
export const TAG_HOLD = "supliful-on-hold";
export const TAG_CANCELED = "supliful-canceled";
const FORWARDABLE = new Set(["PAID", "PARTIALLY_REFUNDED"]);

/**
 * Forward one Shopify order's Supliful lines to Supliful.
 * Real (charged) orders only when liveOrders is true; otherwise testMode sandbox orders.
 * @returns {{status: string, ...}} status: sent | replayed | skipped | dry-run
 */
export async function forwardShopifyOrder({ orderId, shopify, supliful, store, liveOrders = false, dryRun = false, force = false, log = () => {} }) {
  const order = await shopify.getOrder(orderId);
  if (!order) return { status: "skipped", reason: "order not found" };
  if (order.cancelledAt) return { status: "skipped", reason: "order is cancelled", order: order.name };
  if (!force && !FORWARDABLE.has(order.displayFinancialStatus)) return { status: "skipped", reason: `financial status ${order.displayFinancialStatus}`, order: order.name };

  const variantMap = new Map(order.lineItems.filter((li) => li.suplifulProductId).map((li) => [String(li.variantId).split("/").pop(), li.suplifulProductId]));
  const { lines, unmapped } = toSuplifulLines(order.lineItems, variantMap);
  if (!lines.length) return { status: "skipped", reason: "no Supliful products on this order", order: order.name, unmapped: unmapped.length };

  const shippingAddress = toSuplifulAddress(order.shippingAddress);
  const externalOrderId = externalIdFor(order.id);
  const testMode = !liveOrders;
  const request = { externalOrderId, shippingAddress, lines, testMode };
  if (dryRun) return { status: "dry-run", order: order.name, request: { ...request, shippingAddress: redactAddress(shippingAddress) }, unmapped };

  const res = await supliful.createOrder(request);
  const record = { shopifyOrderId: order.id, shopifyName: order.name, suplifulOrderId: res.order.id, testMode, lines, sentAt: new Date().toISOString() };
  store?.set("orders", externalOrderId, record);
  store?.append("events", { kind: "order.forwarded", externalOrderId, suplifulOrderId: res.order.id, replay: res.replay, adopted: res.adopted ?? false, testMode });
  try {
    await shopify.addTags(order.id, testMode ? [TAG_SENT, TAG_TEST] : [TAG_SENT]);
  } catch (err) {
    log(`tag failed on ${order.name}: ${err.message}`);
  }
  log(`${res.replay ? "replayed" : "sent"} ${order.name} -> Supliful ${res.order.id}${testMode ? " (testMode)" : ""}`);
  return { status: res.replay ? "replayed" : "sent", order: order.name, suplifulOrderId: res.order.id, testMode, lines, unmapped };
}

const redactAddress = (a) => ({ ...a, firstName: "[redacted]", lastName: "[redacted]", name: "[redacted]", phone: a.phone ? "[redacted]" : undefined, address1: "[redacted]", address2: a.address2 ? "[redacted]" : undefined });

/**
 * Turn every shipped Supliful parcel into a Shopify fulfillment with tracking (once each).
 * Parcels with no tracking number or URL yet are left for the next event or reconcile pass.
 */
export async function syncShipments({ suplifulOrderId, shopify, supliful, store, notifyCustomer = true, log = () => {} }) {
  const order = await supliful.getOrder(suplifulOrderId);
  const shopifyId = shopifyIdFromExternal(order.externalOrderId);
  if (!shopifyId) return { status: "skipped", reason: "order was not placed by this bridge", suplifulOrderId };
  const results = [];
  let shopOrder;
  for (const shipment of order.shipments || []) {
    if (shipment.status === "returned") continue;
    const doneKey = `${order.id}:${shipment.id}`;
    if (store?.get("shipments", doneKey)) {
      results.push({ shipmentId: shipment.id, status: "already-fulfilled" });
      continue;
    }
    if (!shipment.trackingNumber && !shipment.trackingUrl) {
      results.push({ shipmentId: shipment.id, status: "waiting-for-tracking" });
      continue;
    }
    shopOrder ??= await shopify.getOrder(shopifyId);
    if (!shopOrder) return { status: "skipped", reason: `Shopify order ${shopifyId} not found` };
    const items = fulfillmentLines(shopOrder.fulfillmentOrders, shipmentQuantities(order, shipment));
    if (!items.length) {
      store?.set("shipments", doneKey, { at: new Date().toISOString(), note: "nothing left to fulfil in Shopify" });
      results.push({ shipmentId: shipment.id, status: "nothing-to-fulfil" });
      continue;
    }
    const trackingInfo = { number: shipment.trackingNumber || undefined, url: shipment.trackingUrl || undefined, company: carrierFromUrl(shipment.trackingUrl) };
    const fulfillment = await shopify.createFulfillment({ lineItemsByFulfillmentOrder: items, trackingInfo, notifyCustomer });
    store?.set("shipments", doneKey, { at: new Date().toISOString(), fulfillmentId: fulfillment.id });
    store?.append("events", { kind: "shipment.fulfilled", suplifulOrderId: order.id, shipmentId: shipment.id, fulfillmentId: fulfillment.id });
    log(`fulfilled ${shopOrder.name} shipment ${shipment.id}`);
    shopOrder = undefined; // remaining quantities changed; refetch for the next parcel
    results.push({ shipmentId: shipment.id, status: "fulfilled", fulfillmentId: fulfillment.id });
  }
  return { status: "ok", suplifulOrderId: order.id, local: localStatus(order), results };
}

/**
 * Handle one verified Supliful webhook event. Test deliveries (data.testMode) are logged and
 * change nothing, unless processTestEvents is set for a rehearsal against a development store.
 */
export async function handleSuplifulEvent(event, { shopify, supliful, store, processTestEvents = false, notifyCustomer = true, log = () => {} }) {
  const { type, data = {} } = event;
  if (data.testMode && !processTestEvents) return { status: "ignored", reason: "testMode delivery" };
  switch (type) {
    case "order.shipmentCreated":
    case "order.completed":
      return syncShipments({ suplifulOrderId: data.orderId, shopify, supliful, store, notifyCustomer, log });
    case "order.onHold":
    case "order.onHoldReleased":
    case "order.canceled":
    case "order.shipmentReturned":
    case "order.created": {
      const order = await supliful.getOrder(data.orderId);
      const shopifyId = shopifyIdFromExternal(order.externalOrderId);
      if (!shopifyId) return { status: "skipped", reason: "order was not placed by this bridge" };
      const id = gid("Order", shopifyId);
      if (type === "order.onHold") await shopify.addTags(id, [TAG_HOLD, ...(data.reasons || order.onHoldReasons || []).map((r) => `supliful-hold:${r}`)]);
      if (type === "order.onHoldReleased") await shopify.removeTags(id, [TAG_HOLD, ...(order.onHoldReasons || []).map((r) => `supliful-hold:${r}`)]);
      if (type === "order.canceled") await shopify.addTags(id, [TAG_CANCELED]);
      if (type === "order.shipmentReturned") await shopify.addTags(id, ["supliful-returned"]);
      store?.append("events", { kind: type, suplifulOrderId: order.id, shopifyId, status: order.status, onHold: order.onHold });
      return { status: "ok", type, local: localStatus(order), needsPerson: type === "order.canceled" || type === "order.onHold" || type === "order.shipmentReturned" };
    }
    case "product.published":
    case "product.updated": {
      const product = await supliful.getProduct(data.productId);
      return syncProducts({ supliful, shopify, apply: true, products: [product], log });
    }
    case "product.unpublished":
      return hideLinked({ shopify, suplifulId: data.productId });
    default:
      return { status: "ignored", reason: `unhandled type ${type}` };
  }
}
