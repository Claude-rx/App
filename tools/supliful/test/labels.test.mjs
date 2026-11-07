import { test } from "node:test";
import assert from "node:assert/strict";
import { mkdtempSync, existsSync, readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { directions, warnings, sentences } from "../labels/extract.mjs";
import { loadInputs, buildLabel, labelHtml, renderLabels } from "../labels/render.mjs";

const inputs = loadInputs();
const text = (sku) => inputs.catalog.products.find((p) => p.sku === sku).text;

test("every spec has a catalog product, a known container and accent", () => {
  for (const s of inputs.specs.products) {
    assert.ok(inputs.catalog.products.some((p) => p.sku === s.sku), `${s.sku} in catalog`);
    assert.ok(inputs.specs.containers[s.container], `${s.sku} container`);
    assert.ok(inputs.brand.accents[s.accent], `${s.sku} accent`);
    assert.ok(s.claim && s.key && s.net && s.name, `${s.sku} front-panel facts`);
  }
});

test("directions come from the product's own copy, for every product", () => {
  assert.match(directions(text("MLX-BEET")), /^Adults take two \(2\) capsules once a day/);
  assert.match(directions(text("MLX-METB")), /^Adults: shake well\. Take 1 mL \(20 drops\)/);
  assert.match(directions(text("MLX-MAG-GLY")), /Take three capsules once a day/);
  for (const p of inputs.catalog.products) assert.ok(directions(p.text).length > 15, `${p.sku} has directions`);
});

test("warnings keep every serious caution and always end with the child-safety line", () => {
  const w = warnings(text("MLX-METB"), { maxChars: 200 });
  assert.match(w.text, /SSRIs/);
  assert.match(w.text, /G6PD/);
  assert.match(w.text, /Keep out of reach of children\.$/);
  assert.doesNotMatch(w.text, /Food and Drug Administration/);
  for (const p of inputs.catalog.products) assert.match(warnings(p.text).text, /Keep out of reach of children\.$/, p.sku);
  assert.ok(sentences("A b.* C d. E").length === 3);
});

test("buildLabel flags what a person must confirm before printing", () => {
  const L = buildLabel(inputs.specs.products.find((s) => s.sku === "MLX-MAG-GLY"), inputs);
  assert.ok(L.issues.some((i) => /inferred/.test(i)));
  assert.ok(L.issues.some((i) => /provisional/.test(i)));
  const html = labelHtml(L, { proof: true });
  assert.match(html, /Magnesium Glycinate/);
  assert.match(html, /90 Capsules/);
  assert.match(html, /Dietary Supplement/);
  assert.doesNotMatch(labelHtml(L, { proof: false }), /class="facts show"/, "print file has no guides");
});

let playwright = true;
try {
  await import("node:module").then((m) => m.createRequire(import.meta.url)("playwright"));
} catch {
  playwright = !!process.env.NODE_PATH;
}

test("renders print PDFs and proofs (needs Playwright + Chromium)", { skip: !playwright && "playwright not installed" }, async () => {
  const out = mkdtempSync(join(tmpdir(), "labels-"));
  const res = await renderLabels({ only: ["MLX-BEET", "MLX-CREA", "MLX-METB"], outDir: out });
  assert.equal(res.errors, 0);
  for (const sku of ["MLX-BEET", "MLX-CREA", "MLX-METB"]) {
    const pdf = readFileSync(join(out, `${sku}-print.pdf`));
    assert.equal(pdf.subarray(0, 5).toString(), "%PDF-");
    assert.ok(existsSync(join(out, `${sku}-proof.jpg`)));
  }
  const pages = (readFileSync(join(out, "MLX-CREA-print.pdf"), "latin1").match(/\/Type\s*\/Page[^s]/g) || []).length;
  assert.equal(pages, 2, "pouch = front + back");
  const report = JSON.parse(readFileSync(join(out, "report.json"), "utf8")).labels;
  assert.ok(report.every((r) => !r.issues.some((i) => /overflows/.test(i))), "no text overflow");
  assert.ok(report.find((r) => r.sku === "MLX-BEET").infoTextPt >= 6);
});
