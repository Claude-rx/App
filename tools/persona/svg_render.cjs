// Render an SVG to a transparent PNG at a given width, in the browser (exact to the vector file).
// usage: node tools/persona/svg_render.cjs <in.svg> <out.png> <width>
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [, , svg, out, w] = process.argv;
  const src = fs.readFileSync(svg, 'utf8');
  const vb = (src.match(/viewBox="([^"]+)"/) || [, '0 0 500 100'])[1].split(/[\s,]+/).map(Number);
  const width = +w, height = Math.ceil(width * vb[3] / vb[2]);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width, height }, deviceScaleFactor: 1 });
  await p.setContent(`<html><body style="margin:0;background:transparent">${src.replace('<svg', `<svg style="display:block;width:${width}px;height:${height}px"`)}</body></html>`);
  await p.screenshot({ path: out, omitBackground: true, clip: { x: 0, y: 0, width, height } });
  await b.close();
})();
