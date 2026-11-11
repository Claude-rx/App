"""Build the MedicLab Berberine campaign plan: run the next-campaigns-create `recommend`, then shape it into the funnel's
offer (as on mediclab.us) before `plan` prints it for approval.

usage: python3 -I tools/mediclab/campaign_plan.py [--discovery <discovery.json>] [--out <dir>]

Defaults: discovery next-campaigns-create-runs/mediclab/discovery.json, plan written next to it. Run
`next-campaigns-create.sh discover --store mediclab` first. Nothing is sent to the store: `apply` stays the
operator-approved step with the hash `plan` prints.

The offer, from the copy deck:
  plan-6   Monthly refill plan          variant 6 (JTP4BERB)      $20.97 first bottle (50% off), then $42.97 every 30 days
  hero-5   One bottle, one-time         variant 5 (JTP4BERB)      $52.97
  upsell   One more bottle, one-time    package hero-5 + voucher BERBERINE45 (45%, .97 rounding) = $29.97, post-purchase
Shipping: the store's "default" method, free, US only. A campaign takes one package per variant, which is why the
monthly plan is its own variant (tools/mediclab/import_berberine.py).
"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKILL = ROOT / '.claude' / 'skills' / 'next-campaigns-create' / 'next-campaigns-create.sh'
IDS = json.loads((ROOT / 'tools' / 'mediclab' / 'berberine-ids.json').read_text())
PRODUCT = IDS['product_id']
ONE_TIME, MONTHLY = IDS['variants']['one_time'], IDS['variants']['monthly']
NAME = 'MedicLab Berberine Funnel'
FIRST, RECURRING, EVERY_DAYS, ONE_BOTTLE, UPSELL_PCT = '20.97', '42.97', 30, '52.97', 45


def arg(name, default):
    return Path(sys.argv[sys.argv.index(name) + 1]) if name in sys.argv else default


def shape(plan):
    pk = {p['key']: p for p in plan['packages']}
    one, monthly = pk[f'hero-{ONE_TIME}'], pk[f'hero-{MONTHLY}']
    one['name'] = 'MedicLab Berberine - One Bottle'
    monthly.update(key='plan-' + str(MONTHLY), name='MedicLab Berberine - Monthly Refill Plan', price=FIRST,
                   price_recurring=RECURRING, interval='day', interval_count=EVERY_DAYS)
    rows = []
    for r in plan['landed_prices']:
        if r['kind'] == 'single':
            rows.append({**r, 'tier': 'Monthly plan, first bottle', 'package_keys': [monthly['key']],
                         'anchor': FIRST, 'unit_after': FIRST, 'order_total': FIRST})
            rows.append({**r, 'tier': 'One bottle, one-time', 'package_keys': [one['key']]})
        else:
            rows.append({**r, 'tier': 'Upsell: one more bottle'})
    plan['landed_prices'] = rows
    for o in plan['offers']:
        if o['key'].startswith('upsell-'):
            o['name'] = 'One more bottle at $29.97'
    plan['rationale'].append(
        f'Monthly plan: package {monthly["key"]} is recurring, ${FIRST} on the first order (50% off ${ONE_BOTTLE}), then '
        f'${RECURRING} every {EVERY_DAYS} days (copy deck 05). Its own variant (same SKU JTP4BERB), because a campaign takes '
        f'one package per variant and the one-time bottle is ${ONE_BOTTLE}.')
    plan['handoff'].append('The 3-month minimum on the monthly plan is a policy in the subscription terms; the platform '
                           'does not enforce it. Support enforces it on cancellation requests.')
    return plan


def main():
    disc = arg('--discovery', ROOT / 'next-campaigns-create-runs' / 'mediclab' / 'discovery.json')
    # the gateway group and its methods come from the live store (discovery), never assumed: the group must carry USD
    groups = [g for g in json.loads(disc.read_text())['gateway_groups'] if 'USD' in (g.get('currencies') or [])]
    if not groups:
        sys.exit('no gateway group carries USD: add a payment gateway in Dashboard > Settings > Payments, then discover')
    group = groups[0]
    methods = ','.join(group['payment_methods'])
    express = ','.join(group.get('express_payment_methods') or [])
    out = arg('--out', disc.parent)
    cmd = ['bash', str(SKILL), 'recommend', '--discovery', str(disc), '--hero', str(PRODUCT), '--ctc', 'high',
           '--anchor-price', ONE_BOTTLE, '--shipping', 'default:0.00', '--name', NAME, '--countries', 'US',
           '--currency', 'USD', '--language', 'en', '--gateway-group', str(group['id']), '--payment-methods', methods,
           *(['--express-methods', express] if express else []),
           '--upsell', f'{ONE_TIME}:{ONE_BOTTLE}:{UPSELL_PCT}', '--exit', '0', '--rounding', '0.97',
           '--short-name', f'{PRODUCT}:BERBERINE', '--statement-descriptor', 'MEDICLAB', '--out', str(out)]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        sys.exit(r.stdout + r.stderr)
    path = out / 'campaign-plan.json'
    path.write_text(json.dumps(shape(json.loads(path.read_text())), indent=2) + '\n')
    r = subprocess.run(['bash', str(SKILL), 'plan', '--plan', str(path)], cwd=ROOT, capture_output=True, text=True)
    print(r.stdout + r.stderr)
    sys.exit(r.returncode)


if __name__ == '__main__':
    main()
