// Replica product page: one stylesheet holding only the rules the page can use.
//
//   node tools/funnel/getridof/replica/purge_css.mjs        (run by build_replica.py, last)
//
// The source page ships a whole storefront theme (16 stylesheets, ~620 KB) plus ~200 <style> blocks. This opens the
// built page in a browser (network off, files served from the funnel folder), reads every stylesheet's SOURCE TEXT in
// document order and keeps a rule when one of its selectors matches an element, or could match after an interaction:
//   - state pseudo-classes and pseudo-elements are ignored for the test (:hover, :checked, ::before, ...)
//   - a class or attribute that scripts toggle (DYNAMIC below) is taken out of the selector before the test, so
//     ".drawer.is-open .item" is kept only if ".drawer .item" exists; anything named gro- (this page's own) is kept
//   - a selector the browser cannot test is kept
// Declarations are copied verbatim from the source text. (An earlier version rebuilt them from the browser's parsed
// rules; that serialises a shorthand holding var() as empty longhands and silently broke the photo strip's animation.)
// @media / @supports / @layer / @container blocks are walked; @keyframes stay when a kept rule or an inline style
// names them; @font-face stays when its family is in use; other at-rules stay as they are.
// The result goes to assets/pdp/replica.css, loaded by a single <link> where the first stylesheet was; the old
// <link>s and <style> blocks are removed from index.html. The cascade order is unchanged (document order).
import { createRequire } from 'node:module';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const require = createRequire(import.meta.url);
const { chromium } = require('playwright');

const HERE = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(HERE, '../../../..');
const SLUG = 'mouse-repellent-pouches';
const CAMP = path.join(ROOT, 'campaigns/getridof/src', SLUG);
const ORIGIN = 'http://replica.local';
const TYPES = { '.css': 'text/css', '.js': 'text/javascript', '.svg': 'image/svg+xml', '.png': 'image/png', '.webp': 'image/webp', '.jpg': 'image/jpeg', '.woff2': 'font/woff2', '.gif': 'image/gif' };
const NESTED = /^@(media|supports|layer|container|document|-moz-document|scope|starting-style)\b/i;

// ---- a small CSS reader: top-level rules as { prelude, block } (block = text between the braces) or { at } ----
function parse(css) {
  const out = []; const n = css.length; let i = 0;
  const skipString = () => { const q = css[i]; i++; while (i < n && css[i] !== q) { if (css[i] === '\\') i++; i++; } i++; };
  const skipComment = () => { const e = css.indexOf('*/', i + 2); i = e < 0 ? n : e + 2; };
  const skipSpace = () => { for (;;) { while (i < n && /\s/.test(css[i])) i++; if (css.startsWith('/*', i)) skipComment(); else if (css.startsWith('<!--', i)) i += 4; else if (css.startsWith('-->', i)) i += 3; else break; } };
  const prelude = () => {
    const start = i; let depth = 0;
    while (i < n) {
      const ch = css[i];
      if (ch === '"' || ch === "'") { skipString(); continue; }
      if (css.startsWith('/*', i)) { skipComment(); continue; }
      if (ch === '\\') { i += 2; continue; }
      if (ch === '(' || ch === '[') depth++; else if (ch === ')' || ch === ']') depth = Math.max(0, depth - 1);
      else if (depth === 0 && (ch === '{' || ch === ';' || ch === '}')) break;
      i++;
    }
    return css.slice(start, i).trim();
  };
  const block = () => {
    const start = i + 1; let depth = 0;
    while (i < n) {
      const ch = css[i];
      if (ch === '"' || ch === "'") { skipString(); continue; }
      if (css.startsWith('/*', i)) { skipComment(); continue; }
      if (ch === '\\') { i += 2; continue; }
      if (ch === '{') depth++; else if (ch === '}') { depth--; if (depth === 0) { const body = css.slice(start, i); i++; return body; } }
      i++;
    }
    return css.slice(start);
  };
  for (;;) {
    skipSpace(); if (i >= n) break;
    const p = prelude();
    if (i >= n) break;
    if (css[i] === ';') { i++; if (p) out.push({ at: p }); continue; }
    if (css[i] === '}') { i++; continue; }
    out.push({ prelude: p, block: block() });
  }
  return out;
}
// @import of an embedded stylesheet (data: URL) becomes that stylesheet's rules, in place; any other @import is
// left out (nothing is fetched from another host)
function expand(rules) {
  const out = [];
  for (const r of rules) {
    const m = r.at && /^@import\s+(?:url\()?\s*["']?data:text\/css(;charset=[\w-]+)?(;base64)?,([^"')]+)/i.exec(r.at);
    if (m) out.push(...expand(parse(m[2] ? Buffer.from(m[3], 'base64').toString('utf8') : decodeURIComponent(m[3]))));
    else if (r.at && /^@import\b/i.test(r.at)) continue;
    else out.push(r);
  }
  return out;
}
const splitTop = sel => { const parts = []; let depth = 0, cur = ''; for (let k = 0; k < sel.length; k++) { const ch = sel[k]; if (ch === '\\') { cur += ch + (sel[k + 1] || ''); k++; continue; } if (ch === '(' || ch === '[') depth++; else if (ch === ')' || ch === ']') depth--; if (ch === ',' && depth === 0) { parts.push(cur); cur = ''; } else cur += ch; } parts.push(cur); return parts.map(x => x.trim()).filter(Boolean); };

// ---- the page ----
const file = path.join(CAMP, 'index.html');
const src = fs.readFileSync(file, 'utf8');
const a = src.indexOf('{% raw %}'), b = src.lastIndexOf('{% endraw %}');
if (a < 0 || b < 0) throw new Error('index.html: raw block not found');
const front = src.slice(0, a + 9), html = src.slice(a + 9, b), back = src.slice(b);
if (html.includes('pdp/replica.css')) throw new Error('index.html is already purged: run build_replica.py, which rebuilds it first');
const assetFile = p => { const rel = p.startsWith(`/${SLUG}/`) ? p.slice(SLUG.length + 2) : null; const f = rel && path.join(CAMP, 'assets', decodeURIComponent(rel)); return f && f.startsWith(path.join(CAMP, 'assets')) && fs.existsSync(f) ? f : null; };

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
await page.route('**/*', route => {
  const u = new URL(route.request().url());
  if (u.origin !== ORIGIN) return route.abort();
  if (u.pathname === `/${SLUG}/`) return route.fulfill({ contentType: 'text/html; charset=utf-8', body: html });
  const f = assetFile(u.pathname);
  if (!f) return route.fulfill({ status: 404, body: '' });
  return route.fulfill({ contentType: TYPES[path.extname(f).toLowerCase()] || 'application/octet-stream', body: fs.readFileSync(f) });
});
await page.goto(`${ORIGIN}/${SLUG}/`, { waitUntil: 'load' });
await page.waitForTimeout(800);   // pdp.js has done its work on the DOM (carousels, tabs)

// every applied stylesheet, in document order: its source text (inline) or its path (linked), and its media attribute
const sheets = await page.evaluate(() => [...document.querySelectorAll('link[rel~="stylesheet"], style')].filter(e => e.sheet && !e.sheet.disabled)
  .map(e => ({ href: e.tagName === 'LINK' ? new URL(e.href).pathname : null, text: e.tagName === 'LINK' ? null : e.textContent, media: e.getAttribute('media') || '' })));
const trees = sheets.map(s => {
  if (s.href) { const f = assetFile(s.href); if (!f) throw new Error('stylesheet not found: ' + s.href); return { ...s, rules: expand(parse(fs.readFileSync(f, 'utf8'))) }; }
  return { ...s, rules: expand(parse(s.text)) };
});
// every selector that appears, tested once in the page
const selectors = new Set();
const collect = rules => { for (const r of rules) { if (r.at) continue; if (r.prelude.startsWith('@')) { if (NESTED.test(r.prelude)) collect(r.children = expand(parse(r.block))); } else splitTop(r.prelude).forEach(x => selectors.add(x)); } };
trees.forEach(t => collect(t.rules));
const list = [...selectors];
const verdict = await page.evaluate(list => {
  // classes / attributes that scripts add or flip after load, on this page or in the storefront theme's components
  const DYNAMIC = /gro-|--selected|--active|is-active|is-open|is-visible|is-hidden|\bactive\b|\bopen\b|\bopened\b|\bshow\b|\bshown\b|\bvisible\b|\bhidden\b|\bloaded\b|\bloading\b|\bexpanded\b|\bcollapsed\b|\bselected\b|\bchecked\b|\bdisabled\b|aria-|\[open|data-state|animate|scrolled|sticky|swiper|slick|flickity|splide|menu-open|drawer|modal|popup|tooltip|toast/i;
  const STATE = /:(hover|focus-visible|focus-within|focus|active|visited|checked|disabled|enabled|target|link|any-link|placeholder-shown|autofill|-webkit-autofill|invalid|valid|required|optional|read-only|read-write|default|indeterminate|empty)\b/g;
  const PSEUDO_EL = /::?(before|after|placeholder|selection|marker|first-line|first-letter|backdrop|file-selector-button|-webkit-[\w-]+|-moz-[\w-]+|-ms-[\w-]+)(\([^)]*\))?/g;
  const DYN_TOKEN = /\.(?:\\.|[\w-])+|\[[^\]]*\]/g;   // one class or one attribute test
  const usable = sel => {
    if (/gro-/.test(sel)) return true;
    let t = sel.replace(PSEUDO_EL, '').replace(STATE, '');
    if (DYNAMIC.test(t)) {
      t = t.replace(/:(?:not|is|where|has)\(([^()]|\([^()]*\))*\)/g, m => DYNAMIC.test(m) ? '' : m)   // a functional pseudo that depends on state: no constraint
           .replace(DYN_TOKEN, m => DYNAMIC.test(m) ? '\u0001' : m)
           .replace(/(^|[\s>+~(,])\u0001+(?=$|[\s>+~),:])/g, '$1*').replace(/\u0001/g, '');
    }
    t = t.trim();
    if (!t) return true;
    try { return !!document.querySelector(t); } catch (e) { return true; }
  };
  const used = new Set(); for (const e of document.body.querySelectorAll('*')) for (const f of getComputedStyle(e).fontFamily.split(',')) used.add(f.replace(/["']/g, '').trim().toLowerCase());
  return { keep: list.map(usable), fonts: [...used], inline: [...document.querySelectorAll('[style]')].map(e => e.getAttribute('style')).join(' ') };
}, list);
await browser.close();
const keep = new Map(list.map((s, k) => [s, verdict.keep[k]]));
const fonts = new Set(verdict.fonts);

const stats = { kept: 0, dropped: 0, faces: 0, facesAll: 0, frames: 0, framesAll: 0 };
const frames = [];   // [name, text]: decided once the rest is known
const build = (rules, base) => {
  let css = '';
  const abs = text => base ? text.replace(/url\((['"]?)(?!data:|https?:|\/|#)([^'")]+)\1\)/g, (m, q, u) => `url(${q}${path.posix.join(path.posix.dirname(base), u)}${q})`) : text;
  for (const r of rules) {
    if (r.at) { if (/^@(charset|import)\b/i.test(r.at)) continue; css += r.at + ';\n'; continue; }
    if (r.prelude.startsWith('@')) {
      if (r.children) { const inner = build(r.children, base); if (inner) css += `${r.prelude}{\n${inner}}\n`; continue; }
      if (/^@(-webkit-)?keyframes\b/i.test(r.prelude)) { stats.framesAll++; frames.push([r.prelude.replace(/^@(-webkit-)?keyframes\s+/i, '').replace(/["']/g, '').trim(), abs(`${r.prelude}{${r.block}}`) + '\n']); continue; }
      if (/^@font-face\b/i.test(r.prelude)) {
        stats.facesAll++;
        const fam = (/font-family\s*:\s*([^;]+)/i.exec(r.block) || [])[1];
        if (!fam || fonts.has(fam.replace(/["']/g, '').trim().toLowerCase())) { css += abs(`${r.prelude}{${r.block}}`) + '\n'; stats.faces++; }
        continue;
      }
      css += abs(`${r.prelude}{${r.block}}`) + '\n'; continue;
    }
    const sel = splitTop(r.prelude).filter(x => keep.get(x));
    if (!sel.length) { stats.dropped++; continue; }
    stats.kept++;
    css += abs(`${sel.join(',')}{${r.block}}`) + '\n';
  }
  return css;
};
let all = '';
for (const t of trees) { const css = build(t.rules, t.href); if (css) all += t.media && t.media !== 'all' ? `@media ${t.media}{\n${css}}\n` : css; }
const hay = all + ' ' + verdict.inline;
let extra = '';
for (const [name, text] of frames) if (new RegExp('(^|[\\s:,])' + name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '($|[\\s;,!}])').test(hay)) { extra += text; stats.frames++; }
const out = extra + all;
if (/<\/style/i.test(out)) throw new Error('stylesheet text carries </style');

fs.writeFileSync(path.join(CAMP, 'assets/pdp/replica.css'), out);
// index.html: the one <link> goes where the first stylesheet was; every other local stylesheet and <style> block leaves
let n = 0, placed = false;
const link = `<link rel="stylesheet" href="/${SLUG}/pdp/replica.css">`;
const put = () => { n++; if (placed) return ''; placed = true; return link; };
const page2 = html.replace(/<link\b[^>]*\brel="stylesheet"[^>]*>/g, m => new RegExp(`href="/${SLUG}/[^"]+\\.css"`).test(m) ? put() : m)
                  .replace(/<style\b[^>]*>[\s\S]*?<\/style>/g, put);
if (!placed) throw new Error('no stylesheet found in index.html');
fs.writeFileSync(file, front + page2 + back);
console.log(`css: ${trees.length} stylesheets, ${stats.kept} rules kept, ${stats.dropped} dropped, ${stats.faces}/${stats.facesAll} @font-face, ${stats.frames}/${stats.framesAll} @keyframes -> pdp/replica.css ${(out.length / 1024).toFixed(0)} KB; ${n} <link>/<style> removed; index.html ${(page2.length / 1e6).toFixed(2)} MB`);
