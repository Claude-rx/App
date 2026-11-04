// The funnels for a static host (Netlify, Vercel, Cloudflare Pages): `npm run build:static`.
//
// Builds every funnel with Campaign Page Kit into _site/ (/apf-funnel/<page>/, /stick-funnel/<page>/), then writes the
// host's redirects and headers into it. Node only, no packages beyond next-campaign-page-kit.
//
// FUNNEL_HOST (set it in the host's environment variables, e.g. https://go.skinofab.com): the domain the funnels are
// served from, which must be on each Campaigns App campaign's Allowed Domains (the SDK refuses calls from any other).
// Every production page sends a visitor on another host (the host's own *.netlify.app / *.vercel.app / *.pages.dev
// name) to the same page on this one. Unset, no page redirects (a preview: the pages show, the SDK stays refused until
// the preview host is allowed). The campaign data keeps try.skinofab.com, the store-hosted copy's host; only the build
// here reads the override, and the file is put back as it was.
import { readFileSync, writeFileSync } from 'node:fs';
import { execSync } from 'node:child_process';

const DATA = '_data/campaigns.json';
const ENTRY = '/apf-funnel/10-reasons-adaptive-foundation/';
const ALIASES = { '/': ENTRY, '/apf': ENTRY, '/stick': '/stick-funnel/10-reasons-foundation-stick/' };

let host = (process.env.FUNNEL_HOST || '').trim().replace(/\/+$/, '');
if (host && !/^https?:\/\//.test(host)) host = 'https://' + host;
if (host) new URL(host);                                   // a malformed value stops the build here, not in the browser

const original = readFileSync(DATA, 'utf8');
const data = JSON.parse(original);
for (const c of Object.values(data)) c.funnel_host = host;
writeFileSync(DATA, JSON.stringify(data, null, 2) + '\n');
try {
  execSync('npx --no-install campaign-build', { stdio: 'inherit', env: { ...process.env, CPK_ENV: process.env.CPK_ENV || 'production' } });
} finally {
  writeFileSync(DATA, original);
}

// Netlify and Cloudflare Pages read these two files from the publish folder; vercel.json says the same for Vercel
writeFileSync('_site/_redirects', Object.entries(ALIASES).map(([from, to]) => `${from} ${to} 302`).join('\n') + '\n');
writeFileSync('_site/_headers', [
  '/*',
  '  X-Content-Type-Options: nosniff',
  '  Referrer-Policy: strict-origin-when-cross-origin',
  '  X-Frame-Options: SAMEORIGIN',
  '',
].join('\n'));
console.log(`build-static: _site built${host ? `, every page on ${host}` : ' (no FUNNEL_HOST: no host redirect)'}; redirects ${Object.keys(ALIASES).join(', ')}`);
