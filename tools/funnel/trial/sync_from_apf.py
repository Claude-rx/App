"""Keep the flash trial funnel's shared Page Kit parts identical to the APF funnel's.

usage: python3 -I tools/funnel/trial/sync_from_apf.py [--check]

The trial funnel (campaigns/skinofab/src/trial-funnel) was copied from the APF funnel on 4 Nov 2026: the same layouts,
includes, styles, scripts and pictures (the checkout's trust, the offers' hero and timer, the brush page, the receipt,
the review photos, the pack shots). This copies every file of apf-funnel/_layouts, _includes and assets/ over the trial's
on each build, so a fix or a new picture in the APF funnel reaches the trial's pages too. The trial's own files stay:
its pages (trial-*.html), assets/config.js (campaign 2251's key) and its clock (assets/js/sf-trial.js,
assets/css/sf-trial.css). assets/js/sf-checkout.js is copied, then given back the one line the trial needs (no exit
pop without its template: the trial's checkout has none). --check only reports what differs (exit 1 if anything does).
"""
import shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APF = ROOT / 'campaigns' / 'skinofab' / 'src' / 'apf-funnel'
TRIAL = ROOT / 'campaigns' / 'skinofab' / 'src' / 'trial-funnel'
OWN = {'assets/config.js', 'assets/js/sf-trial.js', 'assets/css/sf-trial.css'}
GUARD_AT = "  if (!window.next || typeof window.next.exitIntent !== 'function') return;\n"
GUARD = "  if (!document.querySelector('template[data-template=\"exit-intent\"]')) return;   // no exit pop on this page (the flash trial's checkout)\n"


def wanted(rel, data):
    if rel == 'assets/js/sf-checkout.js':
        text = data.decode('utf-8')
        if GUARD not in text:
            if GUARD_AT not in text: raise SystemExit('sync_from_apf: sf-checkout.js changed shape: put the trial guard back by hand')
            text = text.replace(GUARD_AT, GUARD_AT + GUARD, 1)
        return text.encode('utf-8')
    return data


def main(check):
    changed = []
    for src in sorted(APF.rglob('*')):
        rel = src.relative_to(APF).as_posix()
        if not src.is_file() or not rel.startswith(('_layouts/', '_includes/', 'assets/')) or rel in OWN: continue
        data = wanted(rel, src.read_bytes())
        dst = TRIAL / rel
        if dst.is_file() and dst.read_bytes() == data: continue
        changed.append(rel)
        if not check:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(data)
    print(f"sync_from_apf: {len(changed)} file(s) {'differ' if check else 'updated'}{': ' + ', '.join(changed[:8]) if changed else ''}")
    if check and changed: sys.exit(1)


if __name__ == '__main__':
    main('--check' in sys.argv)
