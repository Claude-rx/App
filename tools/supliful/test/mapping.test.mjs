import { test } from "node:test";
import assert from "node:assert/strict";
import {
  toProductSetInput,
  planProduct,
  indexShopify,
  toSuplifulAddress,
  toSuplifulLines,
  localStatus,
  shipmentQuantities,
  fulfillmentLines,
  externalIdFor,
  shopifyIdFromExternal,
  carrierFromUrl,
  descriptionToHtml,
  slugify,
  isSellable,
  productImages,
} from "../lib/mapping.mjs";
import { product } from "./fakes.mjs";

test("toProductSetInput builds a DRAFT single-variant product linked to Supliful", () => {
  const p = product({ id: "p1" });
  const input = toProductSetInput(p);
  assert.equal(input.status, "DRAFT");
  assert.equal(input.handle, "magnesium-glycinate");
  assert.equal(input.vendor, "Mediclab");
  assert.equal(input.variants.length, 1);
  assert.equal(input.variants[0].price, "45.00");
  assert.equal(input.variants[0].sku, "MLX-MAG-GLY");
  assert.equal(input.variants[0].inventoryPolicy, "CONTINUE");
  assert.deepEqual(input.variants[0].inventoryItem.measurement, { weight: { value: 6, unit: "OUNCES" } });
  assert.equal(input.files.length, 2, "imageUrl and mockups de-duplicated");
  assert.deepEqual(input.metafields.map((m) => `${m.namespace}.${m.key}=${m.value}`), ["supliful.product_id=p1", "supliful.updated_at=2026-11-01T00:00:00.000Z"]);
  assert.ok(input.tags.includes("supliful"));
});

test("toProductSetInput: ACTIVE only when publishing a sellable product; price override wins", () => {
  assert.equal(toProductSetInput(product(), { publish: true }).status, "ACTIVE");
  assert.equal(toProductSetInput(product({ available: false }), { publish: true }).status, "DRAFT");
  assert.equal(toProductSetInput(product({ status: "discontinued" }), { publish: true }).status, "DRAFT");
  assert.equal(toProductSetInput(product(), { price: 39 }).variants[0].price, "39.00");
  assert.throws(() => toProductSetInput(product({ retailPrice: null })), /No price/);
});

test("planProduct covers create, link, update, hide, ok, conflict, skip", () => {
  const p = product({ id: "s1" });
  const empty = indexShopify([]);
  assert.equal(planProduct(p, empty).action, "create");
  assert.equal(planProduct(product({ available: false }), empty).action, "skip");

  const bySku = indexShopify([{ id: "A", status: "ACTIVE", skus: ["MLX-MAG-GLY"] }]);
  assert.equal(planProduct(p, bySku).action, "link");

  const dup = indexShopify([{ id: "A", skus: ["MLX-MAG-GLY"] }, { id: "B", skus: ["MLX-MAG-GLY"] }]);
  assert.equal(planProduct(p, dup).action, "conflict");

  const linked = (over) => indexShopify([{ id: "A", status: "ACTIVE", skus: ["X"], suplifulId: "s1", suplifulUpdatedAt: p.updatedAt, ...over }]);
  assert.equal(planProduct(p, linked()).action, "ok");
  assert.equal(planProduct(p, linked({ suplifulUpdatedAt: "old" })).action, "update");
  assert.equal(planProduct(product({ id: "s1", status: "discontinued" }), linked()).action, "hide");
  assert.equal(planProduct(product({ id: "s1", available: false }), linked({ status: "DRAFT" })).action, "ok", "already hidden");
});

test("a SKU already linked to another Supliful product is not re-linked", () => {
  const idx = indexShopify([{ id: "A", skus: ["MLX-MAG-GLY"], suplifulId: "other" }]);
  assert.equal(planProduct(product({ id: "new" }), idx).action, "create");
});

test("toSuplifulAddress maps REST and GraphQL shapes and refuses incomplete ones", () => {
  const rest = toSuplifulAddress({ first_name: "Ada", last_name: "Lovelace", address1: "1 Main", city: "Denver", province_code: "CO", zip: "80202", country_code: "US", phone: "+1" });
  assert.deepEqual(rest, { firstName: "Ada", lastName: "Lovelace", name: "Ada Lovelace", phone: "+1", address1: "1 Main", city: "Denver", stateCode: "CO", zip: "80202", countryCode: "US" });
  const gql = toSuplifulAddress({ firstName: "", lastName: "", name: "Grace Brewster Hopper", address1: "2 Elm", city: "NYC", provinceCode: "NY", zip: "10001", countryCodeV2: "US" });
  assert.equal(gql.firstName, "Grace");
  assert.equal(gql.lastName, "Brewster Hopper");
  assert.throws(() => toSuplifulAddress({ firstName: "A", lastName: "B", city: "X", zip: "1", countryCode: "US" }), /address1/);
  assert.throws(() => toSuplifulAddress(null), /no shipping address/);
});

test("toSuplifulLines sums by product, skips non-Supliful and fully refunded lines", () => {
  const map = new Map([["11", "p1"], ["22", "p2"]]);
  const { lines, unmapped } = toSuplifulLines(
    [
      { variant_id: 11, quantity: 2 },
      { variantId: "gid://shopify/ProductVariant/11", currentQuantity: 1 },
      { variant_id: 22, quantity: 3, current_quantity: 0 },
      { variant_id: 99, quantity: 1, title: "Wegovy", sku: "WEGO-025" },
    ],
    map,
  );
  assert.deepEqual(lines, [{ productId: "p1", quantity: 3 }]);
  assert.deepEqual(unmapped, [{ title: "Wegovy", sku: "WEGO-025", variantId: "99" }]);
});

test("externalOrderId round-trips and is stable", () => {
  assert.equal(externalIdFor("gid://shopify/Order/123"), "shopify-123");
  assert.equal(externalIdFor(123), "shopify-123");
  assert.equal(shopifyIdFromExternal("shopify-123"), "123");
  assert.equal(shopifyIdFromExternal("rehearsal-1"), null);
});

test("localStatus derives shipped / partial / accepted / submitted / terminal", () => {
  const lines = [{ id: "a", productId: "p", quantity: 1 }, { id: "b", productId: "q", quantity: 1 }];
  assert.equal(localStatus({ status: "COMPLETED" }), "completed");
  assert.equal(localStatus({ status: "IN_PROGRESS", lines, shipments: [{ status: "shipped", lineIds: ["a"] }] }), "partially_shipped");
  assert.equal(localStatus({ status: "IN_PROGRESS", lines, shipments: [{ status: "shipped", lineIds: ["a", "b"] }] }), "shipped");
  assert.equal(localStatus({ status: "ACCEPTED", lines, shipments: [] }), "accepted");
  assert.equal(localStatus({ status: "NEW", lines, shipments: [], onHold: true }), "on_hold");
  assert.equal(localStatus({ status: "NEW", lines, shipments: [] }), "submitted");
});

test("shipmentQuantities sums a product spread over several lines", () => {
  const order = { lines: [{ id: "a", productId: "p", quantity: 1 }, { id: "b", productId: "p", quantity: 2 }, { id: "c", productId: "q", quantity: 5 }] };
  assert.deepEqual([...shipmentQuantities(order, { lineIds: ["a", "b"] })], [["p", 3]]);
});

test("fulfillmentLines takes only what remains, across fulfillment orders", () => {
  const fos = [
    { id: "FO1", status: "OPEN", lineItems: [{ id: "L1", remainingQuantity: 1, suplifulProductId: "p" }, { id: "L2", remainingQuantity: 4, suplifulProductId: null }] },
    { id: "FO2", status: "OPEN", lineItems: [{ id: "L3", remainingQuantity: 5, suplifulProductId: "p" }] },
    { id: "FO3", status: "CLOSED", lineItems: [{ id: "L4", remainingQuantity: 5, suplifulProductId: "p" }] },
  ];
  assert.deepEqual(fulfillmentLines(fos, new Map([["p", 3]])), [
    { fulfillmentOrderId: "FO1", fulfillmentOrderLineItems: [{ id: "L1", quantity: 1 }] },
    { fulfillmentOrderId: "FO2", fulfillmentOrderLineItems: [{ id: "L3", quantity: 2 }] },
  ]);
  assert.deepEqual(fulfillmentLines(fos, new Map([["zzz", 1]])), []);
});

test("small helpers", () => {
  assert.equal(carrierFromUrl("https://tools.usps.com/x"), "USPS");
  assert.equal(carrierFromUrl("https://www.ups.com/track"), "UPS");
  assert.equal(carrierFromUrl(null), undefined);
  assert.equal(descriptionToHtml("a <b>\n\nc\nd"), "<p>a &lt;b&gt;</p>\n<p>c<br>d</p>");
  assert.equal(slugify("Hair, Skin & Nails Gummies"), "hair-skin-and-nails-gummies");
  assert.equal(isSellable({ available: true, status: "active" }), true);
  assert.deepEqual(productImages({ imageUrl: null, mockupUrls: [] }), []);
});
