// Read the star rating and the number of ratings of the owner's own Amazon listing, for the product page's
// "Rated on Amazon" box (tools/persona/brush_copy.py amazon_html). Only the totals are kept, never review text:
// Amazon's reviews belong to their writers and to Amazon.
//
// usage: node amazon_rating.mjs <ASIN or amazon.com/dp/... URL> <out.json> --brand "<your brand on Amazon>"
// - opens the listing in a browser (plain requests get a captcha) and reads its rating, rating count and brand
// - writes <out.json> only when the listing's brand matches --brand: another seller's listing of a similar brush
//   is a different product, and its ratings must not be shown as this brush's
// - the box says when the numbers were checked; run it again before a campaign to refresh them
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import fs from 'fs';

const [IN, OUT] = process.argv.slice(2);
const arg = k => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : null; };
const BRAND = arg('--brand');
const asin = (IN.match(/\b(B0[A-Z0-9]{8})\b/) || [])[1];
if (!asin || !OUT || !BRAND) { console.error('usage: node amazon_rating.mjs <ASIN|URL> <out.json> --brand "<brand>"'); process.exit(2); }
const url = `https://www.amazon.com/dp/${asin}`;

const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
const page = await (await browser.newContext({ locale: 'en-US', viewport: { width: 1280, height: 900 },
  userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36' })).newPage();
await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
await page.waitForTimeout(3000);
const got = await page.evaluate(() => ({
  title: document.title,
  captcha: /enter the characters|not a robot|captcha/i.test(document.body.innerText.slice(0, 3000)),
  rating: (document.querySelector('#acrPopover') || {}).title || (document.querySelector('[data-hook="rating-out-of-text"]') || {}).textContent || '',
  count: ((document.querySelector('#acrCustomerReviewText') || document.querySelector('[data-hook="total-review-count"]') || {}).textContent || '').trim(),
  brand: ((document.querySelector('#bylineInfo') || {}).textContent || '').trim(),
}));
await browser.close();

if (got.captcha) { console.error('Amazon answered with a captcha: try again in a few minutes'); process.exit(1); }
const rating = parseFloat((got.rating.match(/(\d(?:\.\d)?) out of 5/) || [])[1]);
const count = parseInt((got.count.replace(/[,.\s]/g, '').match(/\d+/) || [])[0], 10);
const brand = got.brand.replace(/^(Brand:|Visit the)\s*/i, '').replace(/\s*Store$/i, '').trim();
console.log(JSON.stringify({ asin, brand, rating, count, title: got.title.slice(0, 120) }));
if (!rating || !count) { console.error('no rating found on the listing'); process.exit(1); }
if (brand.toLowerCase() !== BRAND.toLowerCase()) {
  console.error(`the listing's brand is "${brand}", not "${BRAND}": not written (another seller's ratings are not this brush's)`);
  process.exit(1);
}
fs.writeFileSync(OUT, JSON.stringify({ asin, url, brand, rating, count, checked: new Date().toISOString().slice(0, 10) }, null, 1));
console.log('written', OUT);
