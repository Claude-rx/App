// Render Mediclab label artwork for Supliful private-label products.
//   node tools/supliful/cli.mjs labels [--only SKU,SKU] [--out dir]
// Per SKU: <sku>-print.pdf (trim + bleed, no guides; upload to Supliful's label editor) and
// <sku>-proof.jpg (guides: bleed, trim, safe area, the Supplement Facts zone Supliful prints).
// Plus index.html (contact sheet) and report.json (what needs a person before printing).
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";
import { directions, warnings } from "./extract.mjs";

const HERE = dirname(fileURLToPath(import.meta.url));
const PX = 96; // CSS px per inch
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);

export function loadInputs(dir = HERE) {
  const brand = JSON.parse(readFileSync(join(dir, "brand.json"), "utf8"));
  const specs = JSON.parse(readFileSync(join(dir, "specs.json"), "utf8"));
  const catalog = JSON.parse(readFileSync(join(dir, "catalog.json"), "utf8"));
  return { brand, specs, catalog };
}

/** Everything one label needs, with the issues a person must resolve before printing. */
export function buildLabel(spec, { brand, specs, catalog }) {
  const container = specs.containers[spec.container];
  if (!container) throw new Error(`${spec.sku}: unknown container ${spec.container}`);
  const product = catalog.products.find((p) => p.sku === spec.sku);
  if (!product) throw new Error(`${spec.sku}: not in catalog.json`);
  const small = container.heightIn < 2;
  const dir = directions(product.text);
  const warn = warnings(product.text, { maxChars: small ? 420 : 900 });
  const issues = [];
  if (!spec.netVerified) issues.push(`net quantity "${spec.net}" is inferred - confirm on the Supliful product`);
  if (!container.verified) issues.push(`${spec.container} size ${container.widthIn}x${container.heightIn} in is provisional - set it from Supliful's label editor`);
  if (!dir) issues.push("no directions found in the product copy");
  if (warn.dropped.length) issues.push(`${warn.dropped.length} low-priority caution(s) left off for space`);
  if (!brand.distributorAddress) issues.push("brand.json distributorAddress is empty (name and place of business)");
  return { spec, container, brand, accent: brand.accents[spec.accent] || brand.colors.ink, directions: dir, warnings: warn.text, dropped: warn.dropped, issues };
}

const wordmark = (brand, color) => `
  <div class="wordmark" style="color:${color}">
    <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="9" y="2" width="6" height="20" rx="1.2" fill="currentColor"/><rect x="2" y="9" width="20" height="6" rx="1.2" fill="currentColor"/></svg>
    <span>${esc(brand.name)}</span>
  </div>`;

const identity = (L) => `
    <div class="identity">
      <span>${esc(L.brand.statementOfIdentity)}${L.spec.flavor ? ` · ${esc(L.spec.flavor)}` : ""}</span>
      <strong>${esc(L.spec.net)}</strong>
    </div>`;

function frontPanel(L, { withIdentity = false } = {}) {
  const { spec, brand, accent } = L;
  return `
  <section class="front">
    ${wordmark(brand, brand.colors.ink)}
    <div class="rule" style="background:${accent}"></div>
    <h1 class="name fit-line">${esc(spec.name)}</h1>
    <p class="claim">${esc(spec.claim)}</p>
    <p class="key" style="background:${accent}">${esc(spec.key)}</p>
    ${withIdentity ? identity(L) : ""}
  </section>`;
}

function infoPanel(L) {
  const { brand, spec } = L;
  const addr = brand.distributorAddress ? `, ${esc(brand.distributorAddress)}` : "";
  return `
  <section class="info fit-box">
    <h2>Directions</h2>
    <p>${esc(L.directions)}</p>
    <h2>Warnings</h2>
    <p>${esc(L.warnings)}</p>
    <p class="disclaimer">${esc(brand.disclaimer)}</p>
    <p class="dist">${esc(brand.distributor)}${addr} · ${esc(brand.site)} · ${esc(spec.sku)}</p>
  </section>`;
}

const factsZone = (proof) => `<section class="facts${proof ? " show" : ""}"><span>Supplement Facts panel<br>and barcode: printed by Supliful</span></section>`;

export function labelHtml(L, { proof = false } = {}) {
  const { container, brand, accent } = L;
  const W = container.widthIn, H = container.heightIn, B = container.bleedIn, S = container.safeIn;
  const pouch = container.layout === "pouch";
  const unit = ((pouch ? W : H) * PX) / 100;
  const BAND = Math.max(0.16 * H, 0.26); // inches of coloured band above the bottom bleed // 1u = 1% of the panel's short side
  const pageW = (W + 2 * B) * PX, pageH = (H + 2 * B) * PX;
  const guides = proof
    ? `<div class="guide trim"></div><div class="guide safe"></div>${container.verified ? "" : `<div class="stamp">PROVISIONAL SIZE</div>`}`
    : "";
  const page = (inner, cls, band = "") => `<div class="page ${cls}"><div class="bleed" style="--accent:${accent}">${band}<div class="safe-area">${inner}</div></div>${guides}</div>`;
  const pages = pouch
    ? page(frontPanel(L, { withIdentity: true }), "pouch-front") + page(`<div class="back">${infoPanel(L)}${factsZone(proof)}</div>`, "pouch-back")
    : page(`<div class="wrap">${infoPanel(L)}${frontPanel(L)}${factsZone(proof)}</div>`, "wrap-page", `<div class="band"></div><div class="band-grid">${identity(L)}</div>`);

  return `<!doctype html><html><head><meta charset="utf-8"><title>${esc(L.spec.sku)}</title><style>
  @page { size: ${pageW}px ${pageH}px; margin: 0 }
  * { box-sizing: border-box; margin: 0; padding: 0 }
  html, body { background: ${proof ? "#e9edf1" : "#fff"} }
  body { font-family: ${brand.fonts.text}; color: ${brand.colors.ink}; -webkit-print-color-adjust: exact; print-color-adjust: exact }
  .page { position: relative; width: ${pageW}px; height: ${pageH}px; overflow: hidden; page-break-after: always; break-after: page; ${proof ? "margin: 0 0 24px 0;" : ""} }
  .bleed { position: absolute; inset: 0; background: ${brand.colors.paper} }
  .safe-area { position: absolute; inset: ${(B + S) * PX}px }
  .band { position: absolute; left: 0; right: 0; bottom: 0; height: ${(B + BAND) * PX}px; background: var(--accent) }
  .band-grid { position: absolute; left: ${(B + S) * PX}px; right: ${(B + S) * PX}px; bottom: ${B * PX}px; height: ${BAND * PX}px; display: grid; grid-template-columns: ${container.columns || "31% 1fr 27%"}; gap: ${2.2 * unit}px; align-items: center }
  .wrap { display: grid; grid-template-columns: ${container.columns || "31% 1fr 27%"}; gap: ${2.2 * unit}px; position: absolute; left: 0; right: 0; top: 0; bottom: ${(BAND - S + 0.04 * H) * PX}px }
  .front { display: flex; flex-direction: column; min-width: 0; position: relative }
  .wordmark { display: flex; align-items: center; gap: ${1.6 * unit}px; font-family: ${brand.fonts.display}; font-weight: 800; letter-spacing: .28em; font-size: ${5.6 * unit}px }
  .wordmark svg { width: ${5.6 * unit}px; height: ${5.6 * unit}px; color: var(--accent) }
  .rule { height: ${0.9 * unit}px; width: ${16 * unit}px; margin: ${3 * unit}px 0 ${3.2 * unit}px }
  .name { font-family: ${brand.fonts.display}; font-weight: 800; line-height: .98; letter-spacing: -.02em; font-size: ${15 * unit}px }
  .claim { margin-top: ${2.6 * unit}px; font-size: ${5.4 * unit}px; line-height: 1.25; color: ${brand.colors.muted}; font-weight: 500 }
  .key { align-self: flex-start; max-width: 100%; margin-top: ${3 * unit}px; color: #fff; font-weight: 700; font-size: ${4.4 * unit}px; padding: ${1.3 * unit}px ${2.6 * unit}px; border-radius: ${10 * unit}px; line-height: 1.2 }
  .identity { grid-column: 2; display: flex; justify-content: space-between; align-items: baseline; gap: ${2 * unit}px; color: #fff; font-size: ${4.3 * unit}px; text-transform: uppercase; letter-spacing: .08em }
  .identity strong { font-size: ${5.2 * unit}px; font-weight: 800; text-transform: none; letter-spacing: .02em }
  .info { min-width: 0; overflow: hidden; font-size: ${3.6 * unit}px; line-height: 1.3; color: ${brand.colors.ink}; border-right: ${0.25 * unit}px solid ${brand.colors.rule}; padding-right: ${2 * unit}px }
  .info h2 { font-size: 1em; text-transform: uppercase; letter-spacing: .12em; font-weight: 800; color: var(--accent); margin: .55em 0 .2em }
  .info h2:first-child { margin-top: 0 }
  .info .disclaimer { margin-top: .6em; font-size: .9em; color: ${brand.colors.muted} }
  .info .dist { margin-top: .5em; font-size: .9em; font-weight: 600 }
  .facts { border-radius: ${1.2 * unit}px; display: flex; align-items: center; justify-content: center; text-align: center; }
  .facts span { visibility: hidden; font-size: ${3.4 * unit}px; color: #7a8794; font-weight: 600; line-height: 1.3 }
  .facts.show { border: ${0.35 * unit}px dashed #9aa7b3; background: repeating-linear-gradient(45deg,#f6f8fa,#f6f8fa ${2 * unit}px,#eef2f5 ${2 * unit}px,#eef2f5 ${4 * unit}px) }
  .facts.show span { visibility: visible }
  /* pouch */
  .pouch-front .bleed { background: linear-gradient(180deg, ${brand.colors.paper} 0 64%, var(--accent) 64% 100%) }
  .pouch-front .front { height: 100%; padding: ${4 * unit}px ${2 * unit}px }
  .pouch-front .wordmark { font-size: ${6.4 * unit}px } .pouch-front .wordmark svg { width: ${6.4 * unit}px; height: ${6.4 * unit}px }
  .pouch-front .name { font-size: ${15 * unit}px; margin-top: ${2 * unit}px }
  .pouch-front .claim { font-size: ${5.6 * unit}px }
  .pouch-front .key { font-size: ${4.6 * unit}px; background: ${brand.colors.ink} !important; margin-top: ${5 * unit}px }
  .pouch-front .identity { position: absolute; bottom: ${4 * unit}px; left: ${2 * unit}px; right: ${2 * unit}px; flex-direction: column; align-items: flex-start; font-size: ${4.6 * unit}px }
  .pouch-front .identity strong { font-size: ${7 * unit}px }
  .pouch-front .front { padding-bottom: ${46 * unit}px }
  .back { display: grid; grid-template-rows: auto 1fr; gap: ${3 * unit}px; height: 100% }
  .back .info { border-right: 0; padding: 0; font-size: ${3.5 * unit}px }
  .back .facts { margin: 0; min-height: ${50 * unit}px }
  /* guides */
  .guide { position: absolute; pointer-events: none }
  .guide.trim { inset: ${B * PX}px; outline: 1px solid #e0007a }
  .guide.safe { inset: ${(B + S) * PX}px; outline: 1px dashed #00a3e0 }
  .stamp { position: absolute; right: ${B * PX + 4}px; top: ${B * PX + 3}px; font: 700 9px/1 Arial, sans-serif; color: #e0007a; letter-spacing: .08em; background: rgba(255,255,255,.85); padding: 2px 4px }
  </style></head><body>${pages}
  <script>
  // Fit: shrink the info text until it fits its box; shrink a long product name to its column.
  window.__runFit = () => {
  window.__fit = { overflow: [] };
  const MIN_PX = 6; // 4.5 pt, the smallest legible label type
  for (const box of document.querySelectorAll('.fit-box')) {
    let size = parseFloat(getComputedStyle(box).fontSize);
    while (box.scrollHeight > box.clientHeight + 0.5 && size > MIN_PX) { size -= 0.25; box.style.fontSize = size + 'px'; }
    if (box.scrollHeight > box.clientHeight + 0.5) window.__fit.overflow.push('info panel');
    window.__fit.infoPx = size;
  }
  for (const el of document.querySelectorAll('.fit-line')) {
    let size = parseFloat(getComputedStyle(el).fontSize);
    const maxH = size * 0.98 * 2 + 1;
    while ((el.scrollWidth > el.clientWidth + 0.5 || el.offsetHeight > maxH) && size > 8) { size -= 0.5; el.style.fontSize = size + 'px'; }
  }
  // One-line elements: shrink to fit (floor 60%), then allow wrapping as a last resort.
  for (const el of document.querySelectorAll('.identity, .key')) {
    el.style.whiteSpace = 'nowrap';
    const parts = [el, ...el.children];
    const base = parts.map(p => parseFloat(getComputedStyle(p).fontSize));
    const over = () => el.scrollWidth > (el.classList.contains('key') ? el.parentElement.clientWidth : el.clientWidth) + 0.5;
    let k = 1;
    while (over() && k > 0.6) { k -= 0.02; parts.forEach((p, i) => p.style.fontSize = (base[i] * k) + 'px'); }
    if (over()) el.style.whiteSpace = 'normal';
  }
  for (const f of document.querySelectorAll('.front')) {
    const kids = [...f.children].filter(c => !c.classList.contains('identity'));
    if (!kids.length) continue;
    const bottom = Math.max(...kids.map(c => c.offsetTop + c.offsetHeight));
    const id = f.querySelector('.identity');
    if (bottom > f.clientHeight - parseFloat(getComputedStyle(f).paddingBottom) + 1 || (id && bottom > id.offsetTop + 1)) window.__fit.overflow.push('front panel');
  }
  return window.__fit;
  };
  </script></body></html>`;
}

function loadPlaywright() {
  const req = createRequire(import.meta.url);
  try {
    return req("playwright");
  } catch {
    for (const p of [process.env.NODE_PATH, "/opt/node-tools/node_modules", "/usr/local/lib/node_modules_global"].filter(Boolean)) {
      try {
        return req(join(p, "playwright"));
      } catch {
        /* try next */
      }
    }
    throw new Error("Playwright is required to render labels (npm i -D playwright, then npx playwright install chromium)");
  }
}

export async function renderLabels({ only, proof = true, outDir, dir = HERE, log = () => {} } = {}) {
  const inputs = loadInputs(dir);
  const out = outDir || join(dir, "out");
  mkdirSync(out, { recursive: true });
  const list = inputs.specs.products.filter((s) => !only || only.includes(s.sku));
  if (!list.length) throw new Error(`No label specs match ${only}`);
  const { chromium } = loadPlaywright();
  const browser = await chromium.launch();
  const report = [];
  let errors = 0;
  try {
    const ctx = await browser.newContext({ deviceScaleFactor: 2 });
    const page = await ctx.newPage();
    for (const spec of list) {
      try {
        const L = buildLabel(spec, inputs);
        const { widthIn: W, heightIn: H, bleedIn: B } = L.container;
        const pageW = Math.round((W + 2 * B) * PX), pageH = Math.round((H + 2 * B) * PX);
        // print file
        await page.setViewportSize({ width: pageW, height: pageH });
        await page.setContent(labelHtml(L, { proof: false }), { waitUntil: "load" });
        const fit = await page.evaluate(async () => { await document.fonts.ready; return window.__runFit(); });
        const pdf = join(out, `${spec.sku}-print.pdf`);
        await page.pdf({ path: pdf, width: `${W + 2 * B}in`, height: `${H + 2 * B}in`, printBackground: true, pageRanges: "" });
        // proof
        const pages = L.container.layout === "pouch" ? 2 : 1;
        await page.setViewportSize({ width: pageW, height: pageH * pages + 24 * pages });
        await page.setContent(labelHtml(L, { proof: true }), { waitUntil: "load" });
        await page.evaluate(async () => { await document.fonts.ready; window.__runFit(); });
        const png = join(out, `${spec.sku}-proof.jpg`);
        await page.screenshot({ path: png, fullPage: true, type: "jpeg", quality: 85 });
        if (fit.overflow.length) L.issues.push(`text overflows: ${fit.overflow.join(", ")}`);
        // FDA 21 CFR 101.105(h): type no smaller than 1/16 inch; ~6 pt is the safe floor for body copy.
        if (fit.infoPx * 0.75 < 6) L.issues.push(`info text is ${(fit.infoPx * 0.75).toFixed(1)} pt (under 6 pt): use a larger label, a fold-out label or an outer carton`);
        report.push({ sku: spec.sku, name: spec.name, container: spec.container, size: `${W} x ${H} in + ${B} in bleed`, pdf: `${spec.sku}-print.pdf`, proof: `${spec.sku}-proof.jpg`, infoTextPt: +(fit.infoPx * 0.75).toFixed(2), issues: L.issues, droppedCautions: L.dropped });
        log(`label  ${spec.sku.padEnd(12)} ${L.issues.length ? `${L.issues.length} to check` : "ready"}`);
      } catch (err) {
        errors++;
        report.push({ sku: spec.sku, error: err.message });
        log(`label  ${spec.sku} failed: ${err.message}`);
      }
    }
  } finally {
    await browser.close();
  }
  writeFileSync(join(out, "report.json"), JSON.stringify({ generatedAt: new Date().toISOString(), labels: report }, null, 1));
  writeFileSync(join(out, "index.html"), contactSheet(report, inputs.brand));
  const ready = report.filter((r) => !r.error && !r.issues.length).length;
  return { errors, outDir: out, report, summary: `${report.length} labels rendered to ${out} - ${ready} ready, ${report.length - ready - errors} need a check, ${errors} failed. See report.json / index.html.` };
}

function contactSheet(report, brand) {
  const cards = report
    .map((r) =>
      r.error
        ? `<article><h2>${esc(r.sku)}</h2><p class="err">${esc(r.error)}</p></article>`
        : `<article><img src="${esc(r.proof)}" alt="${esc(r.name)} label proof" loading="lazy"><h2>${esc(r.name)} <small>${esc(r.sku)}</small></h2><p>${esc(r.size)} · <a href="${esc(r.pdf)}">print PDF</a></p>${r.issues.length ? `<ul>${r.issues.map((i) => `<li>${esc(i)}</li>`).join("")}</ul>` : `<p class="ok">Ready</p>`}</article>`,
    )
    .join("\n");
  return `<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>${esc(brand.name)} labels</title><style>
  body{font-family:Inter,Arial,sans-serif;margin:0;padding:24px;background:#f3f5f7;color:#0e2235}
  h1{margin:0 0 4px} .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(420px,1fr));gap:20px;margin-top:20px}
  article{background:#fff;border-radius:10px;padding:14px;box-shadow:0 1px 3px rgba(0,0,0,.08)} img{width:100%;height:auto;display:block}
  h2{font-size:16px;margin:10px 0 2px} small{color:#5b6b7b;font-weight:500} ul{margin:6px 0 0;padding-left:18px;font-size:13px;color:#a3263a} .ok{color:#1f8a70;font-weight:600} .err{color:#a3263a}
  </style></head><body><h1>${esc(brand.name)} label artwork</h1><p>Print PDFs include bleed and no guides. Proofs show <span style="color:#e0007a">trim</span>, <span style="color:#00a3e0">safe area</span> and the zone Supliful prints the Supplement Facts in.</p><div class="grid">${cards}</div></body></html>`;
}
