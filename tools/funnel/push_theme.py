"""Push the store theme's changed files, and only those, to the store (theme 34 on skinofab.29next.store).

usage: NEXT_API_TOKEN=... python3 -I tools/funnel/push_theme.py [--dry-run] [--init]

The store gives every uploaded asset a new stored copy and drops the old one, even when the file did not change. A page
the store has cached (up to 30 minutes) still points at the old copy, which then answers 403: on 29 Oct 2026 a second
push re-sent the sales hero's mobile picture unchanged, and for 16 minutes every public visitor saw a broken hero
(live review 10). So this pushes a file only when its bytes differ from what was last pushed, by the record in
tools/funnel/theme-push-manifest.json (path -> sha256, committed; not in the theme folder, which a build regenerates). The funnels' assets carry their
content hash in their names, so a changed picture is a new name and the old one stays for the cached pages.

--init records the theme as it is in git HEAD as pushed (run once, right after a push whose files are committed).
The Admin token comes from $NEXT_API_TOKEN and is never printed.
"""
import hashlib, json, os, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
THEME = ROOT / 'skinofab-theme'
MANIFEST = ROOT / 'tools' / 'funnel' / 'theme-push-manifest.json'   # outside the theme: build_theme.py regenerates the theme folder
SKIP = {'.push-manifest.json'}
THEME_DIRS = ('assets/', 'configs/', 'layouts/', 'locales/', 'partials/', 'templates/')   # what the store takes; not DESIGN.md, scripts/…


def sha(data):
    return hashlib.sha256(data).hexdigest()


def files():
    """The theme's files on disk that git sees (committed, or new and not ignored: never config.yml or local files),
    by theme-relative path (what ntk pushes)."""
    names = subprocess.run(['git', 'ls-files', '--cached', '--others', '--exclude-standard', 'skinofab-theme'], cwd=ROOT,
                           capture_output=True, text=True, check=True).stdout.split('\n')
    out = {}
    for n in filter(None, names):
        rel = n[len('skinofab-theme/'):]
        p = THEME / rel
        if p.is_file() and rel.startswith(THEME_DIRS) and not any(part.startswith('.') for part in rel.split('/')):
            out[rel] = p
    return out


def head_files():
    """The theme's files as committed in HEAD: path -> sha256."""
    names = subprocess.run(['git', 'ls-tree', '-r', '--name-only', 'HEAD', 'skinofab-theme'], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
    rec = {}
    for n in names:
        rel = n[len('skinofab-theme/'):]
        if not rel.startswith(THEME_DIRS) or any(part.startswith('.') for part in rel.split('/')): continue
        blob = subprocess.run(['git', 'show', f'HEAD:{n}'], cwd=ROOT, capture_output=True, check=True).stdout
        rec[rel] = sha(blob)
    return rec


IGNORED_REF = __import__('re').compile(r"sf/(?:img|media|fonts)/[\w.@%-]+")   # the store's generated binaries: git-ignored


def new_refs(todo):
    """The git-ignored theme binaries (assets/sf/img, media, fonts: generated, so not in git and not in files()) that a
    changed file now references and its HEAD version did not: a rebuilt picture gets a new hashed name, and without its
    file the page would point at nothing (the serum's two regenerated gallery images, live review 14, F9). Only new
    names: re-sending one the store already has would drop its stored copy under the cached pages."""
    out = set()
    for rel in todo:
        if not rel.endswith(('.html', '.json', '.css', '.js')): continue
        now = set(IGNORED_REF.findall((THEME / rel).read_text(encoding='utf-8', errors='ignore')))
        head = subprocess.run(['git', 'show', f'HEAD:skinofab-theme/{rel}'], cwd=ROOT, capture_output=True, text=True, errors='ignore')
        was = set(IGNORED_REF.findall(head.stdout)) if head.returncode == 0 else set()
        out |= {f'assets/{n}' for n in now - was if (THEME / 'assets' / n).is_file()}
    return sorted(out)


def main():
    if '--init' in sys.argv:
        rec = head_files()
        MANIFEST.write_text(json.dumps(rec, indent=0, sort_keys=True) + '\n')
        print(f'push_theme: recorded {len(rec)} files as pushed (git HEAD)')
        return
    if not MANIFEST.exists():
        sys.exit('push_theme: no .push-manifest.json: run with --init right after a committed push first')
    rec = json.loads(MANIFEST.read_text())
    todo = sorted(rel for rel, p in files().items() if rec.get(rel) != sha(p.read_bytes()))
    todo = [r for r in new_refs(todo) if rec.get(r) != sha((THEME / r).read_bytes())] + todo   # the pictures before the pages
    print(f'push_theme: {len(todo)} changed files')
    for rel in todo: print('  ' + rel)
    if not todo or '--dry-run' in sys.argv: return
    token = os.environ.get('NEXT_API_TOKEN', '')
    if not token: sys.exit('push_theme: NEXT_API_TOKEN is not set')
    for i in range(0, len(todo), 40):                       # in batches, so one long argument list never fails
        batch = todo[i:i + 40]
        r = subprocess.run(['ntk', 'push', '-a', token, *batch], cwd=THEME, capture_output=True, text=True)
        log = (r.stdout + r.stderr).replace(token, '***')
        if r.returncode != 0 or 'ERROR' in log:
            print(log[-2000:]); sys.exit(f'push_theme: the push failed at file {i + 1}; nothing after it was recorded')
        for rel in batch: rec[rel] = sha((THEME / rel).read_bytes())
        MANIFEST.write_text(json.dumps(rec, indent=0, sort_keys=True) + '\n')
    print(f'push_theme: pushed {len(todo)} files')


if __name__ == '__main__':
    main()
