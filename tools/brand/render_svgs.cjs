// Renders SVG strings (and one HTML preview) to PNG with Chromium. Input: a JSON list of jobs written by
// getridof_brand_kit.py: {svg, out, w, h, transparent} or {html, out, w}.
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const jobs = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
  const b = await chromium.launch();
  const p = await b.newPage({ deviceScaleFactor: 1 });
  for (const j of jobs) {
    if (j.html) {
      await p.setViewportSize({ width: j.w, height: 800 });
      await p.goto('file://' + j.html);
      await p.screenshot({ path: j.out, fullPage: true });
      continue;
    }
    const h = j.h || j.w;
    await p.setViewportSize({ width: j.w, height: h });
    const svg = j.svg.replace(/<svg([^>]*?)\swidth="[^"]*"/, '<svg$1').replace(/<svg([^>]*?)\sheight="[^"]*"/, '<svg$1');
    await p.setContent(`<html><head><style>html,body{margin:0;background:transparent}svg{display:block;width:${j.w}px;height:${h}px}</style></head><body>${svg}</body></html>`);
    await p.screenshot({ path: j.out, omitBackground: !!j.transparent, clip: { x: 0, y: 0, width: j.w, height: h } });
  }
  await b.close();
})();
