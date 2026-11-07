// Minimal Shopify Admin GraphQL client for the Supliful bridge. Every operation here was checked
// against the Admin API 2026-10 schema. Throttling (THROTTLED / 429) is retried with backoff.
import { MF_NAMESPACE, MF_PRODUCT_ID, MF_UPDATED_AT } from "./mapping.mjs";

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export class ShopifyError extends Error {
  constructor(message, details) {
    super(message);
    this.name = "ShopifyError";
    this.details = details;
  }
}

export const gid = (type, id) => (String(id).startsWith("gid://") ? String(id) : `gid://shopify/${type}/${id}`);
export const numericId = (g) => String(g ?? "").split("/").pop();

export const CATALOG_QUERY = `query Catalog($after: String) {
  products(first: 100, after: $after) {
    pageInfo { hasNextPage endCursor }
    nodes {
      id title handle status
      linkId: metafield(namespace: "${MF_NAMESPACE}", key: "${MF_PRODUCT_ID}") { value }
      linkUpdatedAt: metafield(namespace: "${MF_NAMESPACE}", key: "${MF_UPDATED_AT}") { value }
      variants(first: 100) { nodes { id sku } }
    }
  }
}`;

export const VARIANT_LINKS_QUERY = `query VariantLinks($ids: [ID!]!) {
  nodes(ids: $ids) {
    ... on ProductVariant { id sku product { id metafield(namespace: "${MF_NAMESPACE}", key: "${MF_PRODUCT_ID}") { value } } }
  }
}`;

export const ORDER_QUERY = `query OrderForSupliful($id: ID!) {
  order(id: $id) {
    id name displayFinancialStatus displayFulfillmentStatus cancelledAt
    shippingAddress { firstName lastName name company phone address1 address2 city provinceCode zip countryCodeV2 }
    lineItems(first: 100) {
      nodes { id name sku currentQuantity variant { id product { metafield(namespace: "${MF_NAMESPACE}", key: "${MF_PRODUCT_ID}") { value } } } }
    }
    fulfillmentOrders(first: 20) {
      nodes {
        id status
        lineItems(first: 100) {
          nodes { id remainingQuantity variant { id product { metafield(namespace: "${MF_NAMESPACE}", key: "${MF_PRODUCT_ID}") { value } } } }
        }
      }
    }
  }
}`;

export const PRODUCT_SET_MUTATION = `mutation SuplifulProductSet($input: ProductSetInput!, $identifier: ProductSetIdentifiers) {
  productSet(input: $input, identifier: $identifier, synchronous: true) {
    product { id handle status }
    userErrors { field message code }
  }
}`;

export const METAFIELDS_SET_MUTATION = `mutation SuplifulLink($metafields: [MetafieldsSetInput!]!) {
  metafieldsSet(metafields: $metafields) { metafields { id key } userErrors { field message code } }
}`;

export const PRODUCT_STATUS_MUTATION = `mutation SuplifulStatus($product: ProductUpdateInput!) {
  productUpdate(product: $product) { product { id status } userErrors { field message } }
}`;

export const FULFILLMENT_MUTATION = `mutation SuplifulFulfil($fulfillment: FulfillmentInput!) {
  fulfillmentCreate(fulfillment: $fulfillment) {
    fulfillment { id status trackingInfo { number url company } }
    userErrors { field message }
  }
}`;

export const TAGS_ADD_MUTATION = `mutation SuplifulTagsAdd($id: ID!, $tags: [String!]!) {
  tagsAdd(id: $id, tags: $tags) { node { id } userErrors { field message } }
}`;

export const TAGS_REMOVE_MUTATION = `mutation SuplifulTagsRemove($id: ID!, $tags: [String!]!) {
  tagsRemove(id: $id, tags: $tags) { node { id } userErrors { field message } }
}`;

export class ShopifyClient {
  constructor({ storeDomain, adminToken, apiVersion = "2026-10", fetch: f = globalThis.fetch, baseDelayMs = 1000, maxRetries = 5 } = {}) {
    if (!storeDomain || !adminToken) throw new Error("ShopifyClient needs storeDomain and adminToken");
    this.endpoint = `https://${storeDomain}/admin/api/${apiVersion}/graphql.json`;
    this.token = adminToken;
    this.fetch = f;
    this.baseDelayMs = baseDelayMs;
    this.maxRetries = maxRetries;
  }

  async graphql(query, variables = {}) {
    for (let attempt = 1; ; attempt++) {
      const res = await this.fetch(this.endpoint, {
        method: "POST",
        headers: { "content-type": "application/json", accept: "application/json", "x-shopify-access-token": this.token },
        body: JSON.stringify({ query, variables }),
      });
      const throttled = res.status === 429;
      const text = await res.text();
      let body;
      try {
        body = JSON.parse(text);
      } catch {
        if ((throttled || res.status >= 500) && attempt <= this.maxRetries) {
          await sleep(this.baseDelayMs * 2 ** (attempt - 1));
          continue;
        }
        throw new ShopifyError(`Shopify ${res.status}: non-JSON response`, text.slice(0, 300));
      }
      const isThrottled = throttled || (body.errors || []).some((e) => e?.extensions?.code === "THROTTLED");
      if ((isThrottled || res.status >= 500) && attempt <= this.maxRetries) {
        await sleep(this.baseDelayMs * 2 ** (attempt - 1));
        continue;
      }
      if (!res.ok || body.errors) throw new ShopifyError(`Shopify GraphQL error (${res.status})`, body.errors || body);
      return body.data;
    }
  }

  static assertNoUserErrors(payload, what) {
    const errs = payload?.userErrors || [];
    if (errs.length) throw new ShopifyError(`${what}: ${errs.map((e) => `${(e.field || []).join(".")} ${e.message}`.trim()).join("; ")}`, errs);
    return payload;
  }

  /** Every product with its SKUs and Supliful link, normalised for mapping.indexShopify(). */
  async listCatalog() {
    const out = [];
    let after = null;
    do {
      const data = await this.graphql(CATALOG_QUERY, { after });
      for (const p of data.products.nodes) {
        out.push({
          id: p.id,
          title: p.title,
          handle: p.handle,
          status: p.status,
          suplifulId: p.linkId?.value || null,
          suplifulUpdatedAt: p.linkUpdatedAt?.value || null,
          skus: p.variants.nodes.map((v) => v.sku).filter(Boolean),
        });
      }
      after = data.products.pageInfo.hasNextPage ? data.products.pageInfo.endCursor : null;
    } while (after);
    return out;
  }

  async productSet(input, identifier) {
    const data = await this.graphql(PRODUCT_SET_MUTATION, { input, identifier: identifier ?? null });
    return ShopifyClient.assertNoUserErrors(data.productSet, `productSet ${input.title ?? ""}`).product;
  }

  /** Attach Supliful metafields to an existing product without touching its copy or price. */
  async setMetafields(ownerId, metafields) {
    const data = await this.graphql(METAFIELDS_SET_MUTATION, { metafields: metafields.map((m) => ({ ownerId, ...m })) });
    return ShopifyClient.assertNoUserErrors(data.metafieldsSet, "metafieldsSet").metafields;
  }

  async setStatus(productId, status) {
    const data = await this.graphql(PRODUCT_STATUS_MUTATION, { product: { id: productId, status } });
    return ShopifyClient.assertNoUserErrors(data.productUpdate, "productUpdate").product;
  }

  /** Map Shopify variant ids (numeric or gid) -> Supliful product id, for linked products only. */
  async variantLinks(variantIds) {
    const map = new Map();
    const ids = [...new Set(variantIds.filter(Boolean).map((v) => gid("ProductVariant", v)))];
    for (let i = 0; i < ids.length; i += 100) {
      const data = await this.graphql(VARIANT_LINKS_QUERY, { ids: ids.slice(i, i + 100) });
      for (const n of data.nodes || []) {
        const link = n?.product?.metafield?.value;
        if (link) map.set(numericId(n.id), link);
      }
    }
    return map;
  }

  /** The order with addresses, lines and fulfillment orders, normalised. */
  async getOrder(orderId) {
    const data = await this.graphql(ORDER_QUERY, { id: gid("Order", orderId) });
    const o = data.order;
    if (!o) return null;
    return {
      ...o,
      lineItems: o.lineItems.nodes.map((li) => ({ ...li, variantId: li.variant?.id, suplifulProductId: li.variant?.product?.metafield?.value || null })),
      fulfillmentOrders: o.fulfillmentOrders.nodes.map((fo) => ({
        id: fo.id,
        status: fo.status,
        lineItems: fo.lineItems.nodes.map((li) => ({ id: li.id, remainingQuantity: li.remainingQuantity, suplifulProductId: li.variant?.product?.metafield?.value || null })),
      })),
    };
  }

  async addTags(id, tags) {
    const data = await this.graphql(TAGS_ADD_MUTATION, { id, tags });
    return ShopifyClient.assertNoUserErrors(data.tagsAdd, "tagsAdd");
  }

  async removeTags(id, tags) {
    const data = await this.graphql(TAGS_REMOVE_MUTATION, { id, tags });
    return ShopifyClient.assertNoUserErrors(data.tagsRemove, "tagsRemove");
  }

  async createFulfillment({ lineItemsByFulfillmentOrder, trackingInfo, notifyCustomer = true }) {
    const data = await this.graphql(FULFILLMENT_MUTATION, { fulfillment: { lineItemsByFulfillmentOrder, trackingInfo, notifyCustomer } });
    return ShopifyClient.assertNoUserErrors(data.fulfillmentCreate, "fulfillmentCreate").fulfillment;
  }
}
