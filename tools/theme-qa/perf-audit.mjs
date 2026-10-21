// Page-weight and loading audit of the live storefront (no mocks): what each route downloads, from where, and how fast.
// usage: node perf-audit.mjs <store_url> <theme_id> <out.json> [--routes /,/catalogue/x/] [--mobile|--desktop] [--throttle]
// Per route: requests and transferred bytes by type and host, the largest files, render-blocking CSS/JS, FCP, LCP
// (element + url), CLS, long-task time, DOM size, and every request that leaves the store's own hosts.
// --throttle emulates Lighthouse's mobile network (150 ms RTT, 1.6 Mbps down) and a 4x slower CPU.
import { chromium } from '/opt/node-tools/node_modules/playwright/index.mjs';
import fs from 'fs';

const [STORE, THEME, OUT] = process.argv.slice(2);
const arg = (k, d) => { const i = process.argv.indexOf(k); return i > 0 ? process.argv[i + 1] : d; };
const ROUTES = arg('--routes', '/,/catalogue/adaptive-peptide-foundation_14/,/cart/').split(',');
const MODES = process.argv.includes('--desktop') ? ['desktop'] : process.argv.includes('--mobile') ? ['mobile'] : ['mobile', 'desktop'];
const THROTTLE = process.argv.includes('--throttle');
// the store, its media CDN and the CloudFront host NEXT serves theme CSS/JS and platform scripts from
const OWN = [new URL(STORE).host, 'cdn.29next.store', 'd1lrxs4saq89c.cloudfront.net'];

const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
const report = { store: STORE, theme: THEME, at: new Date().toISOString(), throttle: THROTTLE, pages: [] };

for (const mode of MODES) {
  const ctx = await browser.newContext(mode === 'mobile'
    ? { viewport: { width: 390, height: 844 }, deviceScaleFactor: 3, isMobile: true, hasTouch: true,
        userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1' }
    : { viewport: { width: 1440, height: 900 } });
  const warm = await ctx.newPage();                                  // pin the preview theme for this context
  await warm.goto(`${STORE}/?preview_theme=${THEME}`, { waitUntil: 'domcontentloaded' }); await warm.close();
  for (const route of ROUTES) {
    const page = await ctx.newPage();
    const cdp = await ctx.newCDPSession(page);
    await cdp.send('Network.enable'); await cdp.send('Network.setCacheDisabled', { cacheDisabled: true });
    if (THROTTLE) {
      await cdp.send('Network.emulateNetworkConditions', { offline: false, latency: 150, downloadThroughput: 1.6e6 / 8, uploadThroughput: 750e3 / 8 });
      await cdp.send('Emulation.setCPUThrottlingRate', { rate: 4 });
    }
    const reqs = new Map();
    cdp.on('Network.requestWillBeSent', e => reqs.set(e.requestId, { url: e.request.url, type: e.type, bytes: 0, status: 0, start: e.timestamp }));
    cdp.on('Network.responseReceived', e => { const r = reqs.get(e.requestId); if (r) { r.status = e.response.status; r.mime = e.response.mimeType; } });
    cdp.on('Network.loadingFinished', e => { const r = reqs.get(e.requestId); if (r) { r.bytes = e.encodedDataLength; r.end = e.timestamp; } });
    cdp.on('Network.loadingFailed', e => { const r = reqs.get(e.requestId); if (r) r.failed = e.errorText; });
    await page.addInitScript(() => {
      window.__perf = { lcp: null, cls: 0, longTasks: 0 };
      new PerformanceObserver(l => { const e = l.getEntries().at(-1); window.__perf.lcp = { t: e.startTime, url: e.url || null,
        el: e.element ? (e.element.tagName + (e.element.id ? '#' + e.element.id : '') + (e.element.className && typeof e.element.className === 'string' ? '.' + e.element.className.trim().split(/\s+/).slice(0, 2).join('.') : '')) : null }; })
        .observe({ type: 'largest-contentful-paint', buffered: true });
      new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__perf.cls += e.value; }).observe({ type: 'layout-shift', buffered: true });
      new PerformanceObserver(l => { for (const e of l.getEntries()) window.__perf.longTasks += Math.max(0, e.duration - 50); }).observe({ type: 'longtask', buffered: true });
    });
    const url = `${STORE}${route}${route.includes('?') ? '&' : '?'}preview_theme=${THEME}`;
    const t0 = Date.now();
    await page.goto(url, { waitUntil: 'load', timeout: 180000 });
    const loadMs = Date.now() - t0;
    await page.waitForTimeout(THROTTLE ? 6000 : 2500);              // let lazy/idle work land
    const m = await page.evaluate(() => {
      const nav = performance.getEntriesByType('navigation')[0];
      const fcp = performance.getEntriesByName('first-contentful-paint')[0];
      const blocking = performance.getEntriesByType('resource').filter(r => r.renderBlockingStatus === 'blocking').map(r => r.name);
      return { ttfb: nav.responseStart, dcl: nav.domContentLoadedEventEnd, load: nav.loadEventEnd, fcp: fcp ? fcp.startTime : null,
        lcp: window.__perf.lcp, cls: +window.__perf.cls.toFixed(3), tbt: Math.round(window.__perf.longTasks), domNodes: document.getElementsByTagName('*').length,
        htmlBytes: document.documentElement.outerHTML.length, blocking };
    });
    const all = [...reqs.values()].filter(r => !r.url.startsWith('data:'));
    const byType = {}, byHost = {};
    for (const r of all) {
      const t = (r.type || 'Other'); byType[t] = byType[t] || { n: 0, kb: 0 }; byType[t].n++; byType[t].kb += r.bytes / 1024;
      const h = new URL(r.url).host; byHost[h] = byHost[h] || { n: 0, kb: 0 }; byHost[h].n++; byHost[h].kb += r.bytes / 1024;
    }
    for (const o of [...Object.values(byType), ...Object.values(byHost)]) o.kb = Math.round(o.kb);
    const entry = { mode, route, loadMs, requests: all.length, kb: Math.round(all.reduce((a, r) => a + r.bytes, 0) / 1024), ...m,
      byType, byHost, largest: all.sort((a, b) => b.bytes - a.bytes).slice(0, 12).map(r => [Math.round(r.bytes / 1024), r.type, r.url.split('?')[0].slice(-90)]),
      external: [...new Set(all.map(r => r.url).filter(u => !OWN.includes(new URL(u).host)))],
      errors: all.filter(r => r.failed || r.status >= 400).map(r => [r.status, r.failed || '', r.url.slice(0, 140)]) };
    report.pages.push(entry);
    console.log(`${mode.padEnd(7)} ${route.padEnd(48)} ${String(entry.requests).padStart(4)} req ${String(entry.kb).padStart(6)} KB  FCP ${Math.round(m.fcp)}  LCP ${Math.round(m.lcp?.t || 0)}  CLS ${m.cls}  TBT ${m.tbt}  blocking ${m.blocking.length}  ext ${entry.external.length}`);
    await page.close();
  }
  await ctx.close();
}
await browser.close();
fs.writeFileSync(OUT, JSON.stringify(report, null, 1));
console.log('report:', OUT);
