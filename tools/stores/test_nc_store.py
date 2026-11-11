"""Tests for nc_store.py against a local fake Admin API. Run: python3 -I -m unittest tools/stores/test_nc_store.py"""
import io
import json
import os
import sys
import tempfile
import threading
import unittest
from contextlib import redirect_stdout
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import nc_store  # noqa: E402

TOKEN = 'test-token-xyz'
EMPTY_STORE = {
    'store/': {'name': 'Mediclab', 'timezone': 'America/New_York', 'primary_domain': None,
               'contact_address': {'line1': '', 'city': '', 'country': None, 'phone_number': ''},
               'available_currencies': [{'code': 'USD'}], 'available_languages': [{'code': 'en'}],
               'payments': {'environment_key': 'SECRETENV', 'available_express_payment_methods': []}},
    'products/': [{'id': 3, 'title': 'Example Product', 'slug': 'example-product', 'images': [],
                   'variants': [{'sku': 'DEMO-SKU-123', 'prices': [{'currency': 'USD', 'price': '49.99'}]}]}],
    'gateways/': [], 'campaigns/': [], 'categories/': [], 'themes/': [], 'orders/': [], 'subscriptions/': [],
    'shipping-methods/': [{'id': 1, 'name': 'Default', 'countries': [], 'prices': [{'currency': 'USD', 'price_per_order': '0.00'}]}],
    'locations/': [{'id': 1, 'address': None}],
    'pages/': [{'id': 3, 'slug': 'contact', 'content': '<p>long</p>'}],
    'webhooks/': [{'id': 1, 'secret_key': 'WEBHOOKSECRET', 'target': 'https://x'}],
}


def ready_store():
    d = json.loads(json.dumps(EMPTY_STORE))
    d['store/']['contact_address'] = {'line1': '1 Main St', 'city': 'Austin', 'country': 'US', 'phone_number': '+1555'}
    d['store/']['primary_domain'] = 'mediclab.com'
    d['store/']['payments']['available_express_payment_methods'] = [{'code': 'apple_pay'}]
    d['products/'] = [{'id': 9, 'title': 'Serum', 'slug': 'serum', 'images': [{'src': 'x'}],
                       'variants': [{'sku': 'ML-1', 'prices': [{'currency': 'USD', 'price': '39'}]}]}]
    d['gateways/'] = [{'id': 1, 'is_active': True}]
    d['campaigns/'] = [{'id': 1, 'name': 'Mediclab Funnel'}]
    d['shipping-methods/'][0]['countries'] = ['US']
    d['locations/'] = [{'id': 1, 'address': {'line1': 'x'}}]
    d['themes/'] = [{'id': 1}]
    return d


class Fake(BaseHTTPRequestHandler):
    data = EMPTY_STORE

    def log_message(self, *a):
        pass

    def do_GET(self):
        if self.headers.get('Authorization') != 'Bearer ' + TOKEN:
            self.send_response(401); self.send_header('Content-Type', 'application/json'); self.end_headers()
            self.wfile.write(b'{"detail":"bad token"}'); return
        path = self.path.split('/api/admin/', 1)[1].split('?')[0]
        if path not in self.data:
            self.send_response(404); self.send_header('Content-Type', 'text/html'); self.end_headers()
            self.wfile.write(b'<html>Page not found</html>'); return
        body = self.data[path]
        if isinstance(body, list):
            # two pages when the list has >1 item, to exercise pagination
            if len(body) > 1 and 'offset=1' not in self.path:
                body = {'next': f'http://{self.headers["Host"]}/api/admin/{path}?limit=100&offset=1', 'results': body[:1]}
            elif len(body) > 1:
                body = {'next': None, 'results': body[1:]}
            else:
                body = {'next': None, 'results': body}
        self.send_response(200); self.send_header('Content-Type', 'application/json'); self.end_headers()
        self.wfile.write(json.dumps(body).encode())


class NcStoreTest(unittest.TestCase):
    def serve(self, data):
        handler = type('H', (Fake,), {'data': data})
        srv = HTTPServer(('127.0.0.1', 0), handler)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        self.addCleanup(srv.server_close)
        self.addCleanup(srv.shutdown)
        return f'http://127.0.0.1:{srv.server_port}'

    def run_cli(self, data, *args, token=TOKEN):
        base = self.serve(data)
        tmp = tempfile.mkdtemp()
        reg = os.path.join(tmp, 'stores.json')
        with open(reg, 'w') as f:
            json.dump({'mediclab': {'name': 'Mediclab', 'subdomain': 'mediclab', 'base_url': base, 'token_env': 'T_ENV'}}, f)
        old = nc_store.REGISTRY, os.environ.get('T_ENV'), os.environ.get('NEXT_API_TOKEN')
        nc_store.REGISTRY = reg
        nc_store.load_store.__defaults__ = (reg,)
        os.environ.pop('NEXT_API_TOKEN', None)
        if token is None:
            os.environ.pop('T_ENV', None)
        else:
            os.environ['T_ENV'] = token
        try:
            out = io.StringIO()
            with redirect_stdout(out):
                code = nc_store.main(['nc_store.py', *args])
            return code, out.getvalue(), tmp
        finally:
            nc_store.REGISTRY = old[0]
            nc_store.load_store.__defaults__ = (old[0],)
            for k, v in (('T_ENV', old[1]), ('NEXT_API_TOKEN', old[2])):
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

    def test_check_connects(self):
        code, out, _ = self.run_cli(EMPTY_STORE, 'check', 'mediclab')
        self.assertEqual(code, 0)
        self.assertIn('connected: Mediclab', out)

    def test_bad_token_exit_2(self):
        code, _, _ = self.run_cli(EMPTY_STORE, 'check', 'mediclab', token='wrong')
        self.assertEqual(code, 2)

    def test_missing_token_exit_2(self):
        code, _, _ = self.run_cli(EMPTY_STORE, 'check', 'mediclab', token=None)
        self.assertEqual(code, 2)

    def test_fresh_store_has_the_four_blockers(self):
        code, out, _ = self.run_cli(EMPTY_STORE, 'audit', 'mediclab')
        self.assertEqual(code, 1)
        for area in ('store', 'catalog', 'payments', 'campaigns'):
            self.assertRegex(out, rf'\*\*BLOCKER\*\* \| {area} \|')

    def test_ready_store_passes(self):
        code, out, _ = self.run_cli(ready_store(), 'audit', 'mediclab')
        self.assertEqual(code, 0, out)
        self.assertNotIn('BLOCKER', out)

    def test_snapshot_scrubs_secrets_and_page_bodies(self):
        path = os.path.join(tempfile.mkdtemp(), 'snap.json')
        self.run_cli(EMPTY_STORE, 'audit', 'mediclab', '--json', path)
        with open(path) as f:
            raw = f.read()
        for secret in ('WEBHOOKSECRET', 'SECRETENV', TOKEN, '<p>long</p>'):
            self.assertNotIn(secret, raw)

    def test_pagination_collects_every_page(self):
        data = ready_store()
        data['products/'] = data['products/'] * 2
        c = nc_store.Client(self.serve(data), TOKEN)
        self.assertEqual(len(c.list_all('products/')), 2)

    def test_html_404_is_an_error_not_json(self):
        c = nc_store.Client(self.serve(EMPTY_STORE), TOKEN)
        with self.assertRaises(nc_store.ApiError):
            c.get('payment-methods/')


if __name__ == '__main__':
    unittest.main()
