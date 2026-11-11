// The MedicLab funnel for a static host (Netlify, Vercel, Cloudflare Pages): `npm run build:static`.
// Builds with Campaign Page Kit into _site/ (/berberine-glp1/<page>/), then writes the host's redirects and headers.
// The funnel's domain must be on the campaign's Allowed Domains in the Campaigns App (the SDK refuses any other).
import { writeFileSync } from 'node:fs';
import { execSync } from 'node:child_process';

const ENTRY = '/berberine-glp1/glp1-support/';
const ALIASES = { '/': ENTRY, '/berberine': ENTRY, '/glp1': ENTRY };

execSync('npx --no-install campaign-build', { stdio: 'inherit', env: { ...process.env, CPK_ENV: process.env.CPK_ENV || 'production' } });
writeFileSync('_site/_redirects', Object.entries(ALIASES).map(([from, to]) => `${from} ${to} 302`).join('\n') + '\n');
writeFileSync('_site/_headers', ['/*', '  X-Content-Type-Options: nosniff', '  Referrer-Policy: strict-origin-when-cross-origin',
  '  X-Frame-Options: SAMEORIGIN', ''].join('\n'));
console.log(`build-static: _site built; redirects ${Object.keys(ALIASES).join(', ')} -> ${ENTRY}`);
