"""Give the bundle products created by setup_ccf_offers.py their packshots on NEXT (replacing any existing ones).

usage: NEXT_API_TOKEN=... python3 -I upload_bundle_images.py <store_subdomain> <ccf-offers.json> <slug>=<image> [...]
"""
import base64, io, json, os, sys, urllib.request
from PIL import Image

STORE, OFFERS = sys.argv[1], json.load(open(sys.argv[2]))
API = f'https://{STORE}.29next.store/api/admin/'
HDR = {'Authorization': f"Bearer {os.environ['NEXT_API_TOKEN']}", 'X-29next-API-Version': '2024-04-01',
       'Content-Type': 'application/json', 'Accept': 'application/json'}

def call(method, path, body=None):
    req = urllib.request.Request(API + path, data=json.dumps(body).encode() if body is not None else None, method=method, headers=HDR)
    with urllib.request.urlopen(req, timeout=180) as r:
        raw = r.read(); return json.loads(raw) if raw else {}

for arg in sys.argv[3:]:
    slug, path = arg.split('=', 1)
    pk = OFFERS[slug]['pk']
    for img in call('GET', f'products/{pk}/').get('images') or []:
        call('DELETE', f"products/{pk}/images/{img['id']}/")
    im = Image.open(path).convert('RGB'); im.thumbnail((1600, 1600))
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=88, optimize=True, progressive=True)
    call('POST', f'products/{pk}/images/', {'attachment': base64.b64encode(buf.getvalue()).decode(),
                                            'file_name': f'{slug}.jpg', 'display_order': 0, 'caption': slug.replace('-', ' ').title()})
    print('uploaded', slug, pk)
