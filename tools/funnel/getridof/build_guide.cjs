// Builds the Whole-Home Placement Guide PDF, the bonus that comes with "Buy 2, Get 1 FREE".
//   node tools/funnel/getridof/build_guide.cjs
// Source: brand/getridof/guide/placement-guide.html  ->  campaigns/getridof/src/mouse-pouches/assets/guide/placement-guide.pdf
// (linked from the thank-you page; build_listicle.py copies it to the listicle funnel with everything else).
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
const ROOT = path.resolve(__dirname, '../../..');
const src = path.join(ROOT, 'brand/getridof/guide/placement-guide.html');
const outDir = path.join(ROOT, 'campaigns/getridof/src/mouse-pouches/assets/guide');
const uri = (f, type) => 'data:' + type + ';base64,' + fs.readFileSync(path.join(ROOT, f)).toString('base64');
(async () => {
  let html = fs.readFileSync(src, 'utf8');
  html = html.replace('@@LOGO@@', uri('campaigns/getridof/src/mouse-pouches/assets/pdp/gro-logo.svg', 'image/svg+xml'))
             .replace('@@HOUSE@@', uri('campaigns/getridof/src/mouse-pouches/assets/pdp/gro-house-3d-960.webp', 'image/webp'));
  if (/@@/.test(html)) throw new Error('unfilled token in the guide');
  fs.mkdirSync(outDir, { recursive: true });
  const b = await chromium.launch(); const p = await b.newPage();
  await p.setContent(html, { waitUntil: 'load' });
  await p.pdf({ path: path.join(outDir, 'placement-guide.pdf'), format: 'Letter', printBackground: true, preferCSSPageSize: true });
  await p.setViewportSize({ width: 816, height: 1056 });
  await p.screenshot({ path: path.join(ROOT, 'brand/getridof/guide/placement-guide-preview.png'), fullPage: true });
  await b.close();
  console.log('wrote', path.relative(ROOT, path.join(outDir, 'placement-guide.pdf')), Math.round(fs.statSync(path.join(outDir, 'placement-guide.pdf')).size / 1024) + ' KB');
})();
