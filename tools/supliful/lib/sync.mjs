// Product sync: Supliful products published to the API connection -> Shopify products.
// Dry-run by default; nothing is written to Shopify unless `apply` is true.
import { indexShopify, planProduct, toProductSetInput, linkMetafields, descriptionToHtml, productImages, isSellable } from "./mapping.mjs";

/**
 * @param {object} o
 * @param {import('./supliful.mjs').SuplifulClient} o.supliful
 * @param {import('./shopify.mjs').ShopifyClient} o.shopify
 * @param {boolean} [o.apply=false]          write to Shopify
 * @param {boolean} [o.publish=false]        new products go ACTIVE (else DRAFT for review)
 * @param {boolean} [o.updateContent=false]  overwrite title/description/images of linked products
 * @param {Record<string, number>} [o.prices] price overrides by Supliful id or SKU
 * @param {object[]} [o.products]            Supliful products (default: fetch them all)
 */
export async function syncProducts({ supliful, shopify, apply = false, publish = false, updateContent = false, prices = {}, products, vendor, productType, log = () => {} }) {
  const source = products ?? (await supliful.listAllProducts());
  const catalog = await shopify.listCatalog();
  const index = indexShopify(catalog);
  const rows = [];
  for (const p of source) {
    const plan = planProduct(p, index);
    const row = { suplifulId: p.id, name: p.name, sku: p.sku ?? null, available: p.available, status: p.status, action: plan.action, reason: plan.reason, shopifyId: plan.shopify?.id ?? null, result: apply ? "pending" : "dry-run" };
    rows.push(row);
    if (!apply || plan.action === "ok" || plan.action === "skip" || plan.action === "conflict") {
      if (apply) row.result = plan.action === "conflict" ? "needs a person" : "unchanged";
      continue;
    }
    try {
      row.result = await applyPlan({ shopify, p, plan, publish, updateContent, price: prices[p.id] ?? (p.sku ? prices[p.sku] : undefined), vendor, productType });
      if (plan.action === "create") row.shopifyId = row.result.id ?? row.shopifyId;
      log(`${plan.action.padEnd(6)} ${p.name}`);
    } catch (err) {
      row.result = `error: ${err.message}`;
      log(`error  ${p.name}: ${err.message}`);
    }
  }
  const counts = rows.reduce((acc, r) => ((acc[r.action] = (acc[r.action] || 0) + 1), acc), {});
  const errors = rows.filter((r) => typeof r.result === "string" && r.result.startsWith("error")).length;
  return { applied: apply, total: rows.length, counts, errors, rows };
}

export async function applyPlan({ shopify, p, plan, publish, updateContent, price, vendor, productType }) {
  switch (plan.action) {
    case "create": {
      const product = await shopify.productSet(toProductSetInput(p, { publish, price, vendor, productType }));
      return { id: product.id, status: product.status };
    }
    case "link": {
      await shopify.setMetafields(plan.shopify.id, linkMetafields(p));
      if (!isSellable(p) && plan.shopify.status === "ACTIVE") await shopify.setStatus(plan.shopify.id, "DRAFT");
      return { id: plan.shopify.id, linked: true, hidden: !isSellable(p) && plan.shopify.status === "ACTIVE" };
    }
    case "update": {
      if (updateContent) {
        await shopify.productSet(
          {
            title: p.name,
            descriptionHtml: descriptionToHtml(p.description || p.shortDescription),
            files: productImages(p).map((url, i) => ({ originalSource: url, contentType: "IMAGE", alt: i === 0 ? p.name : `${p.name} ${i + 1}` })),
            metafields: linkMetafields(p),
          },
          { id: plan.shopify.id },
        );
      } else {
        await shopify.setMetafields(plan.shopify.id, linkMetafields(p));
      }
      return { id: plan.shopify.id, contentUpdated: updateContent };
    }
    case "hide": {
      await shopify.setStatus(plan.shopify.id, "DRAFT");
      return { id: plan.shopify.id, status: "DRAFT" };
    }
    default:
      return "unchanged";
  }
}

/** Hide (DRAFT) the Shopify product linked to a Supliful product id. Used on product.unpublished. */
export async function hideLinked({ shopify, suplifulId, apply = true }) {
  const linked = (await shopify.listCatalog()).find((s) => s.suplifulId === suplifulId);
  if (!linked) return { found: false };
  if (linked.status !== "ACTIVE") return { found: true, id: linked.id, status: linked.status, changed: false };
  if (apply) await shopify.setStatus(linked.id, "DRAFT");
  return { found: true, id: linked.id, status: "DRAFT", changed: apply };
}

/** Markdown table for a sync report. */
export function formatReport(report) {
  const lines = [
    `${report.applied ? "APPLIED" : "DRY RUN"} - ${report.total} Supliful products: ` +
      Object.entries(report.counts)
        .map(([k, v]) => `${v} ${k}`)
        .join(", ") +
      (report.errors ? `, ${report.errors} errors` : ""),
    "",
    "| Action | Product | SKU | Reason | Result |",
    "|---|---|---|---|---|",
  ];
  for (const r of report.rows) {
    const result = typeof r.result === "string" ? r.result : JSON.stringify(r.result);
    lines.push(`| ${r.action} | ${r.name} | ${r.sku ?? ""} | ${r.reason} | ${result} |`);
  }
  return lines.join("\n");
}
