"""Import real customer reviews of the foundation from a review-app export (Loox, Judge.me, Okendo, Yotpo, Stamped
CSV) into the product page review wall.

usage: python3 -I import_reviews.py <export.csv> <work_dir> [--product color-changing-foundation]
                                     [--exclude-text WORD ...] [--download-photos] [--out reviews]
                                     [--verified-only] [--since YYYY-MM-DD] [--note "of the same brush from our sister store"]

The reviews are the store owner's own (the same formula, sold before as the Smooche Color Changing Foundation):
- every review is kept word for word, with its own rating, date and verified flag; nothing is written or edited
- names are shown as "First L."
- a review whose text names another brand or claims sun protection is left out rather than edited (--exclude-text,
  repeatable, replaces EXCLUDE_DEFAULT: every spelling of the old brand, its support team, SPF and sunscreen)
- unpublished, hidden or rejected reviews are left out
- --verified-only keeps only reviews the app marks as verified buyers; --since keeps only reviews from that day on
  (the day the product went on sale there: anything older cannot be from a buyer of it)
- --note says where the reviews come from, under the review wall ("Includes N verified reviews <note>"); the
  default is the foundation's ("of the same formula from our earlier store")
- photos: --download-photos saves them to <work_dir>/reviews/photos/ with a numbered contact sheet
  (photos-sheet.jpg). Only photos listed in <work_dir>/reviews/photos-approved.txt (one photo id per line) are
  published, so a photo showing the old bottle or brand never reaches the page: approve the ones that show skin,
  results or the product without another brand's name, then run again.
Writes <work_dir>/<out>/reviews.json (--out, default reviews; the brush uses reviews-brush) (newest first, with count, average and the 5..1 star distribution);
apply_persona.py turns it into the review wall's data file and copies the approved photos.
"""
import csv, hashlib, io, json, os, re, sys, urllib.request
from datetime import datetime
from pathlib import Path

args = sys.argv[1:]
def opt(name, default=None, many=False):
    vals = [args[i + 1] for i, a in enumerate(args) if a == name and i + 1 < len(args)]
    return vals if many else (vals[-1] if vals else default)
SRC, WORK = Path(args[0]), Path(args[1])
PRODUCT = opt('--product', 'color-changing-foundation')
# the old brand in every spelling customers use (Smooch, Smooche, Smoochie, SMOOCH), its support team's name, and sun
# protection (the old bottle said SPF 15; this formula makes no SPF claim)
EXCLUDE_DEFAULT = ['smooch', 'genrev', 'spf', 'sunscreen', 'sun screen', 'sun protection', 'sunblock']
EXCLUDE = [w.lower() for w in (opt('--exclude-text', many=True) or EXCLUDE_DEFAULT)]
DOWNLOAD = '--download-photos' in args
OUT = WORK / opt('--out', 'reviews')
VERIFIED_ONLY = '--verified-only' in args
SINCE = opt('--since')
NOTE = opt('--note')
PHOTOS = OUT / 'photos'

# column names used by the common review apps, first match wins
COLS = {
    'rating': ['rating', 'score', 'stars', 'review_score', 'review_rating'],
    'title': ['title', 'review_title', 'subject', 'headline'],
    'body': ['body', 'review', 'content', 'text', 'review_body', 'review_content', 'comment', 'message'],
    'name': ['author', 'name', 'reviewer', 'reviewer_name', 'display_name', 'full_name', 'nickname', 'customer_name'],
    'date': ['created_at', 'date', 'review_date', 'submitted_at', 'created', 'published_at', 'date_created'],
    'photos': ['img', 'image', 'images', 'photo', 'photos', 'picture', 'pictures', 'media', 'photo_urls', 'picture_urls', 'image_urls'],
    'verified': ['verified', 'verified_purchase', 'verified_buyer', 'is_verified', 'verified_purchaser'],
    'product': ['handle', 'product_handle', 'product_url', 'product_id', 'product', 'product_title', 'productHandle'],
    'status': ['status', 'published', 'is_published', 'hidden', 'state', 'curated'],
    'id': ['id', 'review_id', 'uuid'],
}

def column(header, key):
    low = {h.strip().lower(): h for h in header}
    for c in COLS[key]:
        if c.lower() in low: return low[c.lower()]
    return None

def truthy(v):
    return str(v).strip().lower() in ('1', 'true', 'yes', 'y', 'verified', 'verified_buyer', 'buyer')

def published(row, col):
    if not col: return True
    v = str(row.get(col, '')).strip().lower()
    if col.lower() == 'hidden': return not truthy(v)
    return v in ('', '1', 'true', 'yes', 'published', 'active', 'approved', 'ok', 'visible', 'shown')

def short_name(full):
    parts = [p for p in re.split(r'\s+', (full or '').strip()) if p]
    if not parts: return 'Verified customer'
    first = parts[0][:1].upper() + parts[0][1:]
    return f'{first} {parts[-1][0].upper()}.' if len(parts) > 1 else first

def when(v):
    v = (v or '').strip()
    for fmt in ('%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%dT%H:%M:%S.%f%z', '%Y-%m-%d %H:%M:%S %Z', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d',
                '%m/%d/%Y', '%d/%m/%Y', '%m/%d/%Y %H:%M', '%Y-%m-%dT%H:%M:%SZ'):
        try: return datetime.strptime(v.replace('Z', '+0000') if fmt.endswith('%z') else v, fmt).date().isoformat()
        except ValueError: pass
    m = re.match(r'(\d{4}-\d{2}-\d{2})', v)
    return m.group(1) if m else ''

def photo_urls(v):
    return [u for u in re.split(r'[\s,;|]+', v or '') if re.match(r'https?://', u)]

def main():
    raw = SRC.read_bytes().decode('utf-8-sig', errors='replace')
    rows = list(csv.DictReader(io.StringIO(raw)))
    if not rows: sys.exit('no rows in ' + str(SRC))
    header = list(rows[0].keys())
    col = {k: column(header, k) for k in COLS}
    if not col['rating'] or not col['body']: sys.exit(f'rating/body columns not found in {header}')
    approved = set()
    if (OUT / 'photos-approved.txt').exists():
        approved = {l.strip() for l in (OUT / 'photos-approved.txt').read_text().splitlines() if l.strip() and not l.startswith('#')}
    PHOTOS.mkdir(parents=True, exist_ok=True)
    kept, skipped = [], {'other product': 0, 'unpublished': 0, 'names another brand': 0, 'no rating or text': 0,
                         'not a verified buyer': 0, 'before --since': 0}
    for n, r in enumerate(rows):
        if col['product'] and PRODUCT not in str(r.get(col['product'], '')).lower():
            skipped['other product'] += 1; continue
        if not published(r, col['status']):
            skipped['unpublished'] += 1; continue
        body = (r.get(col['body']) or '').strip()
        title = (r.get(col['title']) or '').strip() if col['title'] else ''
        try: rating = int(round(float(r.get(col['rating']) or 0)))
        except ValueError: rating = 0
        if not (1 <= rating <= 5) or not (body or title):
            skipped['no rating or text'] += 1; continue
        if any(w in (body + ' ' + title).lower() for w in EXCLUDE):
            skipped['names another brand'] += 1; continue
        if VERIFIED_ONLY and not (col['verified'] and truthy(r.get(col['verified']))):
            skipped['not a verified buyer'] += 1; continue
        if SINCE and when(r.get(col['date']) if col['date'] else '') < SINCE:
            skipped['before --since'] += 1; continue
        rid = str(r.get(col['id']) or '').strip() if col['id'] else ''
        rid = rid or hashlib.md5((body + str(n)).encode()).hexdigest()[:10]
        photos = []
        for k, url in enumerate(photo_urls(r.get(col['photos'], '')) if col['photos'] else []):
            pid = f'{re.sub(r"[^A-Za-z0-9]", "", rid)[:16]}-{k}'
            local = PHOTOS / f'{pid}.jpg'
            if DOWNLOAD and not local.exists():
                try:
                    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30) as resp:
                        local.write_bytes(resp.read())
                except Exception as e:
                    print('photo failed', pid, e, file=sys.stderr)
            if pid in approved and local.exists(): photos.append(local.name)
        kept.append({'id': rid, 'name': short_name(r.get(col['name']) if col['name'] else ''), 'rating': rating, 'title': title,
                     'body': body, 'date': when(r.get(col['date']) if col['date'] else ''),
                     'verified': truthy(r.get(col['verified'])) if col['verified'] else False, 'photos': photos})
    kept.sort(key=lambda x: x['date'], reverse=True)
    dist = {s: sum(1 for x in kept if x['rating'] == s) for s in (5, 4, 3, 2, 1)}
    avg = round(sum(x['rating'] for x in kept) / len(kept), 2) if kept else 0
    data = {'product': PRODUCT, 'count': len(kept), 'average': avg, 'distribution': dist, 'reviews': kept}
    if NOTE: data['note'] = NOTE
    (OUT / 'reviews.json').write_text(json.dumps(data, ensure_ascii=False, indent=1))
    if DOWNLOAD: contact_sheet()
    print(json.dumps({'kept': len(kept), 'average': avg, 'distribution': dist, 'skipped': skipped,
                      'with approved photos': sum(1 for x in kept if x['photos']), 'columns': col}, indent=1))

def contact_sheet():
    """Numbered thumbnails of every downloaded photo, to choose the ones to approve."""
    from PIL import Image, ImageDraw
    files = sorted(PHOTOS.glob('*.jpg'))
    if not files: return
    cols, cell = 8, 200
    sheet = Image.new('RGB', (cols * cell, ((len(files) + cols - 1) // cols) * (cell + 18)), 'white')
    d = ImageDraw.Draw(sheet)
    for i, f in enumerate(files):
        try:
            im = Image.open(f).convert('RGB'); im.thumbnail((cell - 8, cell - 8))
        except Exception: continue
        x, y = (i % cols) * cell, (i // cols) * (cell + 18)
        sheet.paste(im, (x + 4, y + 4)); d.text((x + 4, y + cell), f.stem, fill='black')
    sheet.save(OUT / 'photos-sheet.jpg', quality=80)

main()
