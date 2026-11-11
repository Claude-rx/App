"""Wire the MedicLab Berberine funnel to its campaign: copy the campaign's public Cart API key, package ids and
shipping method id from the next-campaigns-create run manifest into the Page Kit sources.

usage: python3 -I tools/mediclab/wire_funnel.py [<run-manifest.json>] [--check]

Default manifest: next-campaigns-create-runs/mediclab/run-manifest.json (gitignored, mode 600: it is the run's journal).
Only lines tagged "# wire:<name>" (frontmatter) or "// wire:<name>" (config.js) change, so a re-run after the campaign
changes is safe and nothing else in the pages is touched. --check exits 1 if any page is not wired to this manifest.

  wire:api_key   config.js apiKey            campaign.api_key (the public Campaign Cart key every funnel page ships)
  wire:plan      checkout bundle "plan"      package plan-<variant>  (monthly plan, $20.97 then $42.97 / 30 days)
  wire:one       checkout bundle "one", upsell package   package hero-<variant> (one bottle, $52.97; upsell + voucher)
  wire:shipping  checkout shipping_methods.free          the campaign's shipping method (store code "default", free)
Writes campaigns/mediclab/funnel-ids.json (ids only, no key) for the QA tools and the handoff.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAMP = ROOT / 'campaigns' / 'mediclab'
SRC = CAMP / 'src' / 'berberine-glp1'
FILES = [SRC / 'berberine-checkout.html', SRC / 'berberine-offer.html', SRC / 'assets' / 'config.js']
IDS = json.loads((ROOT / 'tools' / 'mediclab' / 'berberine-ids.json').read_text())


def values(manifest):
    one_key = f"hero-{IDS['variants']['JTP4BERB']}"
    plan_key = f"plan-{IDS['variants']['JTP4BERB-SUB']}"
    pk = {p['key']: p for p in manifest['packages']}
    missing = [k for k in (one_key, plan_key) if not (pk.get(k) or {}).get('id')]
    if missing:
        sys.exit(f'manifest has no created package for {missing}: finish apply first')
    ship = [s for s in manifest['shipping_methods'] if s.get('id')]
    if len(ship) != 1:
        sys.exit(f'expected exactly one created shipping method, found {len(ship)}')
    camp = manifest['campaign']
    if not camp.get('api_key') or not camp.get('id'):
        sys.exit('manifest has no created campaign')
    return {'api_key': camp['api_key'], 'plan': pk[plan_key]['id'], 'one': pk[one_key]['id'],
            'shipping': ship[0]['id'], '_campaign_id': camp['id']}


def rewrite(text, vals):
    def num(m):
        return f"{m.group(1)}{vals[m.group(3)]}{m.group(2)}# wire:{m.group(3)}"
    text = re.sub(r'^(\s*[\w-]+:\s*)\S+(\s+)# wire:(plan|one|shipping)\b', num, text, flags=re.M)
    text = re.sub(r'(apiKey:\s*)"[^"]*"(,\s*// wire:api_key)', lambda m: f'{m.group(1)}"{vals["api_key"]}"{m.group(2)}', text)
    return text


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    path = Path(args[0]) if args else ROOT / 'next-campaigns-create-runs' / 'mediclab' / 'run-manifest.json'
    vals = values(json.loads(path.read_text()))
    stale = []
    for f in FILES:
        old = f.read_text()
        new = rewrite(old, vals)
        if new != old:
            stale.append(f.relative_to(ROOT))
            if '--check' not in sys.argv:
                f.write_text(new)
    out = {'campaign_id': vals['_campaign_id'], 'packages': {'plan': vals['plan'], 'one': vals['one']},
           'shipping_method': vals['shipping'], 'upsell_voucher': 'BERBERINE45'}
    if '--check' in sys.argv:
        print('not wired:' if stale else 'wired', *stale)
        sys.exit(1 if stale else 0)
    (CAMP / 'funnel-ids.json').write_text(json.dumps(out, indent=2) + '\n')
    print('wired', *(stale or ['(already up to date)']))
    print(json.dumps(out))


if __name__ == '__main__':
    main()
