import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import fs from 'fs'; import path from 'path'; import crypto from 'crypto';
const OUT = process.argv[2];
fs.mkdirSync(OUT + '/raw', { recursive: true });
const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36' });
const page = await ctx.newPage();
const manifest = [];
page.on('response', async r => {
  try {
    const url = r.url(); const ct = r.headers()['content-type'] || '';
    if (r.status() >= 300 || url.startsWith('data:')) return;
    const type = r.request().resourceType();
    if (!['image','stylesheet','font','script','media','document'].includes(type) && !/svg|image|font|css/.test(ct)) return;
    const body = await r.body();
    const h = crypto.createHash('md5').update(url).digest('hex').slice(0,12);
    fs.writeFileSync(`${OUT}/raw/${h}`, body);
    manifest.push({ url, type, ct, file: h, size: body.length });
  } catch {}
});
await page.goto('https://smooche.com/', { waitUntil: 'networkidle', timeout: 90000 }).catch(e=>console.log('goto', e.message));
for (let y = 0; y < 30; y++) { await page.mouse.wheel(0, 700); await page.waitForTimeout(400); }
await page.evaluate(() => window.scrollTo(0, 0));
await page.waitForTimeout(3000);
fs.writeFileSync(OUT + '/rendered.html', await page.content());
await page.screenshot({ path: OUT + '/original.png', fullPage: true });
fs.writeFileSync(OUT + '/manifest.json', JSON.stringify(manifest, null, 1));
console.log('responses', manifest.length);
await browser.close();
