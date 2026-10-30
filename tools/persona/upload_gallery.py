"""Replace a NEXT product's gallery with an ordered list of images (the first is the cart / checkout thumbnail).

usage: NEXT_API_TOKEN=... python3 -I upload_gallery.py <store_subdomain> <product_pk> <undo.json> <image> [<image> ...]
- each image is centre-cropped to a square, at most 1600 px, and uploaded as JPEG in the given order
- the replaced images' URLs, captions and order are appended to <undo.json> before they are deleted
- idempotent: when the product already has exactly these images (same captions, same order) nothing changes
"""
import base64, hashlib, io, json, os, sys, time, urllib.request, urllib.error
from pathlib import Path
from PIL import Image, ImageOps

STORE, PK, UNDO, PATHS = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4:]
API = f'https://{STORE}.29next.store/api/admin/'
HDR = {'Authorization': f"Bearer {os.environ['NEXT_API_TOKEN']}", 'X-29next-API-Version': '2024-04-01',
       'Content-Type': 'application/json', 'Accept': 'application/json'}

def call(method, path, body=None):
    for attempt in range(4):
        req = urllib.request.Request(API + path, data=json.dumps(body).encode() if body is not None else None, method=method, headers=HDR)
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                raw = r.read(); return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503, 504) and attempt < 3: time.sleep(2 ** (attempt + 1)); continue
            raise RuntimeError(f'{method} {path} -> {e.code}: {e.read()[:400].decode("utf-8", "replace")}')

def prepared(path):
    im = ImageOps.fit(Image.open(path).convert('RGB'), (min(Image.open(path).size),) * 2, Image.LANCZOS)
    im.thumbnail((1600, 1600))
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=88, optimize=True, progressive=True)
    data = buf.getvalue()
    return data, f'{Path(path).stem}-{hashlib.md5(data).hexdigest()[:6]}'   # caption carries a content hash

product = call('GET', f'products/{PK}/')
title = product['title']
uploads = [prepared(p) for p in PATHS]
current = sorted(product.get('images') or [], key=lambda i: i.get('display_order', 0))
if [i.get('caption') for i in current] == [f'{title} | {c}' for _, c in uploads]:
    print('gallery already up to date'); sys.exit()

prev = json.load(open(UNDO)) if os.path.exists(UNDO) else []
prev.append({'product': PK, 'replaced_at': time.strftime('%Y-%m-%dT%H:%M:%S'),
             'images': [{k: i.get(k) for k in ('id', 'attachment', 'caption', 'display_order')} for i in current]})
json.dump(prev, open(UNDO, 'w'), indent=1, ensure_ascii=False)
for i in current: call('DELETE', f"products/{PK}/images/{i['id']}/")
for n, (data, caption) in enumerate(uploads):
    call('POST', f'products/{PK}/images/', {'attachment': base64.b64encode(data).decode(), 'file_name': f'{caption}.jpg',
                                            'display_order': n, 'caption': f'{title} | {caption}'})
    print('uploaded', n, caption)
print(len(current), 'replaced by', len(uploads), 'images on product', PK)
