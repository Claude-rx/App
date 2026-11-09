const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1440, height: 900 } });
  const blocked = [], broken = [];
  await p.route('**/*', r => { const u = r.request().url(); if (u.startsWith('file:') || u.startsWith('data:')) return r.continue(); blocked.push(u); r.abort(); });
  await p.goto('file://' + process.argv[2], { waitUntil: 'load' });
  await p.evaluate(async () => { for (let y=0;y<document.body.scrollHeight;y+=500){scrollTo(0,y);await new Promise(r=>setTimeout(r,60));} scrollTo(0,0); });
  await p.waitForTimeout(1500);
  const r = await p.evaluate(() => ({ imgs: document.images.length, brokenImgs: [...document.images].filter(i => i.complete && i.naturalWidth === 0 && i.getAttribute('src')).map(i=>i.getAttribute('src')), fonts: [...document.fonts].filter(f=>f.status==='loaded').length, h: document.body.scrollHeight }));
  console.log(JSON.stringify(r, null, 1)); console.log('blocked network requests:', blocked.length, blocked.slice(0,10));
  await p.screenshot({ path: process.argv[3], fullPage: true }); await b.close();
})();
