// Pull label copy (directions, warnings) out of the product's own store copy, so the label and the
// product page never disagree. Pure functions; covered by tests.

const DISCLAIMER = /These statements have not been evaluated/i;

export function sentences(text) {
  return String(text ?? "")
    .replace(/\s+/g, " ")
    .split(/(?<=[.!?]\*?)\s+(?=[A-Z*(])/)
    .map((s) => s.trim())
    .filter(Boolean);
}

/** Directions: the label-style "Adults take ..." sentence when present, else the first steps of "How to use". */
export function directions(text, { max = 2 } = {}) {
  const all = sentences(String(text ?? "").replace(/\s*(Suggested use:)/gi, ". $1").replace(/\.\s*\./g, "."));
  const i0 = all.findIndex((s) => /^(Adults|Suggested use:)/i.test(s) && /take|mix|stir|shake|chew/i.test(s));
  if (i0 >= 0) {
    // "Adults: shake well." is only the start: keep going until the dose sentence is in.
    const picked = [all[i0].replace(/^Suggested use:\s*/i, "")];
    for (let i = i0 + 1; i < all.length && picked.length < 3 && !/\b(take|mix|stir|chew)\b/i.test(picked.join(" ")); i++) picked.push(all[i]);
    return picked.join(" ");
  }
  const t = String(text ?? "").replace(/\s+/g, " ");
  const i = t.search(/How to use/i);
  if (i < 0) return "";
  const after = sentences(t.slice(i + "How to use".length));
  // "How to use" steps are "Heading. Detail." pairs: keep the detail of the first step(s).
  const picked = [];
  for (const s of after) {
    if (picked.length >= max) break;
    if (s.split(" ").length <= 4) continue; // step headings like "Mix one scoop."
    if (DISCLAIMER.test(s)) break;
    picked.push(s);
  }
  return picked.join(" ");
}

const WARN_PRIORITY = [
  /^(Never|Do not use|Do not take|Not for use|Not for |Do not combine)/i,
  /(SSRI|MAOI|G6PD|pregnan|nursing|under 18|kidney|allerg|shellfish|milk|iodine|medication|prescription)/i,
  /^(Consult|Ask your|Talk to|Tell your doctor)/i,
  /^(Contains|Turns urine|Stains|May cause|.*can cause)/i,
  /^Do not exceed/i,
  /^(Store|Keep in a cool)/i,
  /^Do not use if the safety seal/i,
];

/**
 * Warnings: every cautionary sentence from the copy, most important first, ending with the
 * child-safety line. Nothing is dropped silently: `maxChars` only trims the lowest-priority
 * sentences, and `dropped` reports what was cut so the proof can flag it.
 */
export function warnings(text, { maxChars = Infinity } = {}) {
  const all = sentences(text).filter((s) => !DISCLAIMER.test(s) && !/^\*?This product is not intended/i.test(s));
  const isWarn = (s) =>
    /^(Never|Do not|Not for|Consult|Ask your|Contains|Keep out of reach|Store|Turns urine|Stains|Loose stools|Berberine can cause|Space it|Drink plenty)/i.test(s) ||
    /(can cause|risk of|allergic|pregnan|nursing)/i.test(s);
  const seen = new Set();
  const found = [];
  for (const s of all) {
    if (!isWarn(s)) continue;
    const k = s.toLowerCase();
    if (seen.has(k)) continue;
    seen.add(k);
    found.push(s);
  }
  const rank = (s) => {
    const i = WARN_PRIORITY.findIndex((rx) => rx.test(s));
    return i < 0 ? WARN_PRIORITY.length : i;
  };
  const keepOut = found.filter((s) => /^Keep out of reach/i.test(s));
  const rest = found.filter((s) => !/^Keep out of reach/i.test(s)).sort((a, b) => rank(a) - rank(b));
  const child = keepOut[0] || "Keep out of reach of children.";
  const kept = [];
  let len = child.length;
  const dropped = [];
  for (const s of rest) {
    if (len + s.length + 1 <= maxChars || rank(s) <= 1) {
      kept.push(s);
      len += s.length + 1;
    } else dropped.push(s);
  }
  return { text: [...kept, child].join(" "), dropped };
}
