// Replica product page: one stylesheet holding only the rules the page can use.
//
//   node tools/funnel/getridof/replica/purge_css.mjs        (run by build_replica.py, last)
//
// The source page ships a whole storefront theme (16 stylesheets, ~620 KB) plus ~200 <style> blocks. This opens the
// built page in a browser (network off, files served from the funnel folder), walks every stylesheet in document
// order and keeps a rule when one of its selectors matches an element, or could match after an interaction:
//   - state pseudo-classes and pseudo-elements are ignored for the test (:hover, :checked, ::before, ...)
//   - a class or attribute that scripts toggle (DYNAMIC below) is taken out of the selector before the test, so
//     ".drawer.is-open .item" is kept only if ".drawer .item" exists; anything named gro- (this page's own) is kept
//   - a selector the browser cannot test is kept
// @font-face, @keyframes and other at-rules are kept as they are; @media / @supports / @layer blocks are walked.
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

const file = path.join(CAMP, 'index.html');
const src = fs.readFileSync(file, 'utf8');
const a = src.indexOf('{% raw %}'), b = src.lastIndexOf('{% endraw %}');
if (a < 0 || b < 0) throw new Error('index.html: raw block not found');
const front = src.slice(0, a + 9), html = src.slice(a + 9, b), back = src.slice(b);
if (html.includes('pdp/replica.css')) throw new Error('index.html is already purged: run build_replica.py, which rebuilds it first');

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
await page.route('**/*', route => {
  const u = new URL(route.request().url());
  if (u.origin !== ORIGIN) return route.abort();
  if (u.pathname === `/${SLUG}/`) return route.fulfill({ contentType: 'text/html; charset=utf-8', body: html });
  const rel = u.pathname.startsWith(`/${SLUG}/`) ? u.pathname.slice(SLUG.length + 2) : null;
  const f = rel && path.join(CAMP, 'assets', decodeURIComponent(rel));
  if (!f || !f.startsWith(path.join(CAMP, 'assets')) || !fs.existsSync(f)) return route.fulfill({ status: 404, body: '' });
  return route.fulfill({ contentType: TYPES[path.extname(f).toLowerCase()] || 'application/octet-stream', body: fs.readFileSync(f) });
});
await page.goto(`${ORIGIN}/${SLUG}/`, { waitUntil: 'load' });
await page.waitForTimeout(800);   // pdp.js has built its own elements (refill terms, carousels)

const out = await page.evaluate(() => {
  // classes / attributes that scripts add or flip after load, on this page or in the storefront theme's components
  const DYNAMIC = /gro-|--selected|--active|is-active|is-open|is-visible|is-hidden|\bactive\b|\bopen\b|\bopened\b|\bshow\b|\bshown\b|\bvisible\b|\bhidden\b|\bloaded\b|\bloading\b|\bexpanded\b|\bcollapsed\b|\bselected\b|\bchecked\b|\bdisabled\b|aria-|\[open|data-state|animate|scrolled|sticky|swiper|slick|flickity|splide|menu-open|drawer|modal|popup|tooltip|toast/i;
  const STATE = /:(hover|focus-visible|focus-within|focus|active|visited|checked|disabled|enabled|target|link|any-link|placeholder-shown|autofill|-webkit-autofill|invalid|valid|required|optional|read-only|read-write|default|indeterminate|empty)\b/g;
  const PSEUDO_EL = /::?(before|after|placeholder|selection|marker|first-line|first-letter|backdrop|file-selector-button|-webkit-[\w-]+|-moz-[\w-]+|-ms-[\w-]+)(\([^)]*\))?/g;
  const stats = { kept: 0, dropped: 0, sheets: 0, frames: 0, faces: 0 };
  const frames = [], faces = [];
  const splitTop = sel => { const parts = []; let depth = 0, cur = ''; for (const ch of sel) { if (ch === '(' || ch === '[') depth++; else if (ch === ')' || ch === ']') depth--; if (ch === ',' && depth === 0) { parts.push(cur); cur = ''; } else cur += ch; } parts.push(cur); return parts.map(x => x.trim()).filter(Boolean); };
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
  const abs = (text, base) => base ? text.replace(/url\((['"]?)(?!data:|https?:|\/|#)([^'")]+)\1\)/g, (m, q, u) => { try { return `url(${q}${new URL(u, base).pathname}${q})`; } catch (e) { return m; } }) : text;
  const walk = (rules, base) => {
    let css = '';
    for (const r of rules) {
      if (r instanceof CSSStyleRule) {
        const keep = splitTop(r.selectorText).filter(usable);
        if (!keep.length) { stats.dropped++; continue; }
        stats.kept++;
        const text = r.cssText;
        css += (text.startsWith(r.selectorText) ? keep.join(',') + text.slice(r.selectorText.length) : text) + '\n';
      } else if (r instanceof CSSMediaRule || r instanceof CSSSupportsRule || (window.CSSLayerBlockRule && r instanceof CSSLayerBlockRule) || (window.CSSContainerRule && r instanceof CSSContainerRule)) {
        const inner = walk(r.cssRules, base);
        if (inner) css += r.cssText.slice(0, r.cssText.indexOf('{') + 1) + '\n' + inner + '}\n';
      } else if (r instanceof CSSKeyframesRule) { frames.push([r.name, abs(r.cssText, base)]);
      } else if (r instanceof CSSFontFaceRule) { faces.push([r.style.getPropertyValue('font-family').replace(/["']/g, '').trim(), abs(r.cssText, base)]);
      } else css += r.cssText + '\n';
    }
    return abs(css, base);
  };
  let all = '';
  for (const sheet of document.styleSheets) {
    if (sheet.disabled) continue;
    let rules; try { rules = sheet.cssRules; } catch (e) { throw new Error('unreadable stylesheet: ' + sheet.href); }
    stats.sheets++;
    const css = walk(rules, sheet.href);
    const media = sheet.media && sheet.media.mediaText;
    if (css) all += media && media !== 'all' ? `@media ${media}{\n${css}}\n` : css;
  }
  // @keyframes whose name no kept rule (or inline style) mentions, and @font-face families nothing renders in, are left out
  const inline = [...document.querySelectorAll('[style]')].map(e => e.getAttribute('style')).join(' ');
  const hay = all + ' ' + inline;
  let extra = '';
  for (const [name, text] of frames) if (new RegExp('(^|[\\s:,])' + name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '($|[\\s;,!}])').test(hay)) { extra += text + '\n'; stats.frames++; }
  const used = new Set(); for (const e of document.body.querySelectorAll('*')) for (const f of getComputedStyle(e).fontFamily.split(',')) used.add(f.replace(/["']/g, '').trim().toLowerCase());
  for (const [fam, text] of faces) if (used.has(fam.toLowerCase())) { extra += text + '\n'; stats.faces++; }
  return { css: extra + all, stats, facesAll: faces.length, framesAll: frames.length };
});
await browser.close();
if (out.css.includes('</style')) throw new Error('stylesheet text carries </style');

fs.writeFileSync(path.join(CAMP, 'assets/pdp/replica.css'), out.css);
// index.html: the one <link> goes where the first stylesheet was; every other local stylesheet and <style> block leaves
let n = 0, placed = false;
const link = `<link rel="stylesheet" href="/${SLUG}/pdp/replica.css">`;
const put = () => { n++; if (placed) return ''; placed = true; return link; };
let page2 = html.replace(/<link\b[^>]*\brel="stylesheet"[^>]*>/g, m => new RegExp(`href="/${SLUG}/[^"]+\\.css"`).test(m) ? put() : m)
                .replace(/<style\b[^>]*>[\s\S]*?<\/style>/g, put);
if (!placed) throw new Error('no stylesheet found in index.html');
fs.writeFileSync(file, front + page2 + back);
console.log(`css: ${out.stats.sheets} stylesheets, ${out.stats.kept} rules kept, ${out.stats.dropped} dropped, ${out.stats.faces}/${out.facesAll} @font-face, ${out.stats.frames}/${out.framesAll} @keyframes -> pdp/replica.css ${(out.css.length / 1024).toFixed(0)} KB; ${n} <link>/<style> removed; index.html ${(page2.length / 1e6).toFixed(2)} MB`);
