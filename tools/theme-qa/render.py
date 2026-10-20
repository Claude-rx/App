"""Render the SKINOFAB theme locally with Django 4.2 and mock NEXT platform tags, for offline browser QA.

usage: python3 render.py <theme_dir> <export_dir> <out_dir>

Every theme file goes through the template engine the way the platform serves it: page templates with a mock
storefront context (catalog built from the design's product data, prices in USD), and .js/.css/.json assets with
an empty context (this proves the DTL escaping of the design's own code). Output mirrors storefront routes:
  /                         templates/index.html
  /products/<handle>/       templates/catalogue/product.<handle>.html with that product as `product`
  /products/_default/       templates/catalogue/product.html
  /catalogue/               templates/catalogue/index.html     /catalogue/category/  category.html
  /<slug>/                  templates/pages/page.<slug>.html   /_page/  page.html
  /blog/  /blog/<slug>/     blog/index.html, blog/post.html     /search/  search.html     /cart/  cart.html
  /assets/<path>            rendered asset files (media are symlinked)
"""
import json, os, re, shutil, sys, types
from decimal import Decimal
from pathlib import Path

THEME, EXPORT, OUT = (Path(p).resolve() for p in sys.argv[1:4])

import django
from django.conf import settings as dj
from django.urls import path as upath, include

# ---------------------------------------------------------------- URLconf with the platform route names templates use
def view(*a, **k): pass
def ns(name, *patterns): return (types.SimpleNamespace(urlpatterns=list(patterns)), name)
urls_mod = types.ModuleType('sf_urls')
urls_mod.urlpatterns = [
    upath('catalogue/', include(([upath('', view, name='index'),
                                  upath('<slug:product_slug>_<int:product_pk>/reviews/', view, name='reviews-list'),
                                  upath('<slug:product_slug>_<int:product_pk>/reviews/add/', view, name='reviews-add')], 'catalogue'))),
    upath('cart/', include(([upath('add/<int:pk>/', view, name='add'), upath('vouchers/add/', view, name='vouchers-add'),
                             upath('vouchers/<int:pk>/remove/', view, name='vouchers-remove'), upath('', view, name='summary')], 'cart'))),
    upath('checkout/', include(([upath('', view, name='index')], 'checkout'))),
    upath('blog/', include(([upath('', view, name='blog-list')], 'blog'))),
    upath('search/', include(([upath('', view, name='search')], 'search'))),
    upath('api/graphql/', include(([upath('', view, name='graphql')], 'storefrontapi'))),
    upath('accounts/', include(([upath('', view, name='summary'), upath('login/', view, name='login'), upath('logout/', view, name='logout'),
                                 upath('support/new/', view, name='support-ticket-create')], 'customer'))),
    upath('support/', include(([upath('', view, name='category-list')], 'support'))),
    upath('currency/', include(([upath('', view, name='set-currency')], 'core'))),
    upath('i18n/setlang/', view, name='set_language'),
]
sys.modules['sf_urls'] = urls_mod

# ---------------------------------------------------------------- platform tag/filter stand-ins
lib_mod = types.ModuleType('sf_platform')
from django import template
register = template.Library()
lib_mod.register = register
sys.modules['sf_platform'] = lib_mod

LOCALE = json.loads((THEME / 'locales' / 'en.default.json').read_text())
def lookup(key):
    node = LOCALE
    for part in key.split('.'):
        if not isinstance(node, dict) or part not in node: return key.split('.')[-1].replace('_', ' ').capitalize()
        node = node[part]
    return node if isinstance(node, str) else key

@register.simple_tag(takes_context=True)
def t(context, key, *args, **kwargs):
    s = lookup(key)
    for k, v in kwargs.items(): s = s.replace('{{ %s }}' % k, str(v)).replace('{{%s}}' % k, str(v))
    return s

@register.filter
def asset_url(path): return '/assets/' + str(path)

@register.filter
def currency(value, code=None):
    try: return '$%.2f' % Decimal(str(value))
    except Exception: return value

@register.simple_tag
def currency_symbol(code=None): return '$'

class Money:
    def __init__(self, price, retail, cur='USD'):
        self.price, self.price_retail, self.currency, self.exists = Decimal(price), Decimal(retail), cur, True
class Session:
    def __init__(self, p):
        self.price = Money(p.price, p.retail)
        self.availability = types.SimpleNamespace(is_available_to_buy=True)

@register.simple_tag
def purchase_info_for_product(request, product): return Session(product)
@register.simple_tag
def purchase_info_for_product_by_currency(request, product, currency): return Session(product)
@register.simple_tag
def purchase_info_for_line(request, line): return Session(line.product)

class Thumb:
    def __init__(self, url): self.url = url
@register.tag
def image_thumbnail(parser, token):
    bits = token.split_contents()
    src = parser.compile_filter(bits[1])
    asvar = bits[-1] if 'as' in bits else None
    class N(template.Node):
        def render(self, ctx):
            img = src.resolve(ctx)
            url = getattr(img, 'url', None) or getattr(getattr(img, 'original', None), 'url', None) or str(img or '')
            if asvar: ctx[asvar] = Thumb(url); return ''
            return url
    return N()

for name in ('seo', 'pixels', 'core_js', 'customer_event_iframes', 'customer_event_manager', 'get_back_button'):
    register.simple_tag(takes_context=True, name=name)(lambda context, *a, **k: '')
@register.simple_tag(takes_context=True)
def app_hook(context, name, *a, **k): return ''
@register.simple_tag
def cart_form(request, product, quantity_type=None): return []
@register.simple_tag
def basket_form(request, product, quantity_type=None): return []
@register.simple_tag
def category_tree(depth=None, parent=None): return []
@register.simple_tag
def add_query_param(request, key, val): return '?%s=%s' % (key, val)
@register.simple_tag(takes_context=True)
def extend_query_param(context, *a, **k): return ''
@register.simple_tag
def get_public_asset_url(file_name): return '/assets/' + file_name
@register.simple_tag
def recently_viewed_products(current_product=None): return []
for name in ('dividedby', 'times', 'plus', 'minus', 'modulo'):
    pass
@register.filter
def dividedby(v, d): return Decimal(str(v)) / Decimal(str(d))
@register.filter
def times(v, d): return Decimal(str(v)) * Decimal(str(d))
@register.filter
def plus(v, d): return Decimal(str(v)) + Decimal(str(d))
@register.filter
def minus(v, d): return Decimal(str(v)) - Decimal(str(d))
@register.filter
def is_review_permitted(product, user): return False
@register.filter
def split(v, sep=','): return str(v).split(sep)
@register.filter
def media_url(v): return str(v)

dj.configure(
    DEBUG=True, ROOT_URLCONF='sf_urls', USE_TZ=True, SECRET_KEY='qa',
    INSTALLED_APPS=['django.contrib.humanize'],
    TEMPLATES=[{'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [str(THEME)],
                'OPTIONS': {'builtins': ['sf_platform', 'django.templatetags.static', 'django.contrib.humanize.templatetags.humanize'],
                            'libraries': {n: 'sf_platform' for n in ('theme_tags', 'core_tags', 'image_tags', 'currency_filters',
                                          'purchase_info_tags', 'reviews_tags', 'app_hooks', 'seo_tags', 'cart_tags', 'math_filters_tags',
                                          'category_tags', 'history_tags', 'display_tags', 'widget_tweaks', 'pixels', 'filter_tags')},
                            'string_if_invalid': ''}}])
django.setup()
from django.template import engines
engine = engines['django']

# ---------------------------------------------------------------- mock catalog from the design's product data
SNAP = {f.stem: json.loads(f.read_text()) for f in (EXPORT / 'products').glob('*.js')}
IMAGES = sorted(p.name for p in (THEME / 'assets' / 'sf' / 'img').glob('*.jpg'))[:40]

class Img:
    def __init__(self, url): self.url = url; self.original = self
class Product:
    _pk = 1000
    def __init__(self, handle, title, price, retail, variants=None, parent=None):
        Product._pk += 1
        self.pk = self.id = Product._pk
        self.handle, self.slug, self.title = handle, handle, title
        self.price, self.retail = price, retail
        self.parent = parent
        self.children_list = [Product(handle, f'{title} - {v}', price, retail, parent=self) for v in (variants or [])]
        self.variant_names = variants or []
        self.rating, self.num_approved_reviews = 0, 0
        self.reviews = types.SimpleNamespace(approved=types.SimpleNamespace(all=[]))
    @property
    def children(self):
        lst = self.children_list
        return types.SimpleNamespace(first=lst[0] if lst else None, all=lst, count=len(lst), __iter__=lambda s: iter(lst))
    def get_title(self): return self.title
    def get_meta_title(self): return self.title
    def get_absolute_url(self): return f'/products/{self.handle}/'
    def get_description(self): return '<p>Product description from NEXT.</p>'
    def get_all_images(self): return [Img('/assets/sf/img/' + i) for i in IMAGES[:3]]
    @property
    def primary_image(self): return Img('/assets/sf/img/' + IMAGES[0])
    def get_interval(self): return None
    @property
    def data(self):
        kids = self.children_list or [self]
        return {'id': self.pk, 'title': self.title, 'children': [
            {'id': c.pk, 'title': c.title,
             'variant_attribute_values': ([{'code': 'color', 'id': i + 1}] if self.children_list else []),
             'purchase_info': {'price': {'price': str(self.price), 'format': '$%s' % self.price},
                               'price_retail': {'price': str(self.retail), 'format': '$%s' % self.retail},
                               'availability': 'instock'}} for i, c in enumerate(kids)]}

def product_for(handle):
    d = SNAP.get(handle, {})
    variants = [v.get('title') for v in d.get('variants', [])] if len(d.get('variants', [])) > 1 else []
    price = Decimal(d.get('price', 3900)) / 100
    retail = Decimal(d.get('compare_at_price') or d.get('price', 3900)) / 100
    return Product(handle, d.get('title', handle.replace('-', ' ').title()), price, retail, variants)

class VariantField:
    def __init__(self, p):
        self.html_name, self.label, self.id_for_label = 'attr_color', 'Color', 'id_attr_color'
        self.field = types.SimpleNamespace(choices=[(i + 1, n) for i, n in enumerate(p.variant_names)])

schema = json.loads((THEME / 'configs' / 'settings_schema.json').read_text())
SETTINGS = json.loads((THEME / 'configs' / 'settings_data.json').read_text())
for sec in schema.values():
    for grp in sec.values():
        for f in grp:
            SETTINGS.setdefault(f['name'], f.get('default'))
            if f['name'].startswith('sf_p_'):
                SETTINGS[f['name']] = product_for(next(h for h in SNAP if re.sub(r'[^a-z0-9]+', '_', h) == f['name'][5:]) if any(
                    re.sub(r'[^a-z0-9]+', '_', h) == f['name'][5:] for h in SNAP) else f['name'][5:].replace('_', '-'))
SETTINGS['sf_shipping_protection'] = Product('shipping-protection', 'Premium Shipping Protection', Decimal('2.99'), Decimal('2.99'))

request = types.SimpleNamespace(CURRENCY_CODE='USD', COOKIES={}, path='/', is_setting_preview=False,
                                get_host=lambda: 'skinofab.29next.store', GET={}, user=types.SimpleNamespace(is_authenticated=False))
store = types.SimpleNamespace(get_meta_title=lambda: 'SKINOFAB', tagline='', name='SKINOFAB', branding=types.SimpleNamespace(icon=None, primary_color=None, accent_color=None))
BASE_CTX = {'request': request, 'settings': SETTINGS, 'store': store, 'homepage_url': '/', 'LANGUAGE_CODE': 'en',
            'user': request.user, 'messages': [], 'currencies': [], 'storefront_geos': []}

def render(tpl, out_rel, **ctx):
    html = engine.get_template(tpl).render({**BASE_CTX, **ctx})
    p = OUT / out_rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(html, 'utf-8')
    return len(html)

# ---------------------------------------------------------------- assets: DTL-render content files, link media
if OUT.exists(): shutil.rmtree(OUT)
(OUT / 'assets').mkdir(parents=True)
for f in (THEME / 'assets').rglob('*'):
    if f.is_dir(): continue
    rel = f.relative_to(THEME / 'assets'); dest = OUT / 'assets' / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    if f.suffix in ('.js', '.css', '.json'):
        dest.write_text(engine.from_string(f.read_text('utf-8')).render({}), 'utf-8')
    else:
        os.symlink(f, dest)

# ---------------------------------------------------------------- routes
manifest = {}
def route(url, tpl, **ctx):
    out = (url.strip('/') + '/index.html') if url != '/' else 'index.html'
    manifest[url] = {'template': tpl, 'bytes': render(tpl, out, **ctx)}

route('/', 'templates/index.html')
all_products = [product_for(h) for h in sorted(SNAP)]
for f in sorted((THEME / 'templates' / 'catalogue').glob('product.*.html')):
    h = f.name[len('product.'):-5]
    p = product_for(h)
    route(f'/products/{h}/', f'templates/catalogue/{f.name}', product=p, variant_form=[VariantField(p)] if p.variant_names else [])
p = product_for('color-changing-foundation')
route('/products/_default/', 'templates/catalogue/product.html', product=p, variant_form=[])
route('/catalogue/', 'templates/catalogue/index.html', products=all_products[:24])
route('/catalogue/category/', 'templates/catalogue/category.html', products=all_products[:12],
      category=types.SimpleNamespace(name='Lips', description='', get_meta_title=lambda: 'Lips'))
for f in sorted((THEME / 'templates' / 'pages').glob('page.*.html')):
    slug = f.name[len('page.'):-5]
    route(f'/{slug}/', f'templates/pages/{f.name}', page=types.SimpleNamespace(title=slug.replace('-', ' ').title(), content='', slug=slug, url=f'/{slug}/'))
route('/_page/', 'templates/pages/page.html', page=types.SimpleNamespace(title='About SKINOFAB', content='<p>Page content managed in NEXT.</p>', slug='about', url='/about/'))
post = types.SimpleNamespace(title='Color Changing Foundation: Does It Actually Work?', content='<p>Post body managed in NEXT.</p>',
                             featured_image=None, created_at=__import__('datetime').datetime(2026, 10, 1), get_absolute_url=lambda: '/blog/post/',
                             get_meta_title=lambda: 'Post', author=types.SimpleNamespace(first_name='SKINOFAB', last_name='Team'),
                             categories=types.SimpleNamespace(all=[]))
route('/blog/', 'templates/blog/index.html', posts=[post, post, post])
route('/blog/post/', 'templates/blog/post.html', post=post)
route('/search/', 'templates/search.html', query='lip', page=types.SimpleNamespace(object_list=[types.SimpleNamespace(object=x) for x in all_products[:8]]))
route('/cart/', 'templates/cart.html', cart=types.SimpleNamespace(all_lines=[], is_empty=True, num_items=0))
(OUT / 'routes.json').write_text(json.dumps(manifest, indent=1))
print(f'rendered {len(manifest)} routes')
