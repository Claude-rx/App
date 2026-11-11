"""Tests for wire_funnel.rewrite and campaign_plan.shape. Run: python3 -I tools/mediclab/test_wire_funnel.py"""
import json, os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import wire_funnel  # noqa: E402
import campaign_plan  # noqa: E402

VALS = {'api_key': 'PUBKEY123', 'plan': 41, 'one': 40, 'shipping': 7}


class Rewrite(unittest.TestCase):
    def test_frontmatter_numbers_and_key(self):
        src = ('packages:\n  main_package: 2 # wire:plan\nshipping_methods:\n  free: 1 # wire:shipping\n'
               'bundles:\n  - id: "plan"\n    package_id: 2 # wire:plan\n  - id: "one"\n    package_id: 1 # wire:one\n'
               'other: 5 # not wired\n  apiKey: "", // wire:api_key (public)\n')
        out = wire_funnel.rewrite(src, VALS)
        self.assertIn('main_package: 41 # wire:plan', out)
        self.assertIn('free: 7 # wire:shipping', out)
        self.assertIn('package_id: 41 # wire:plan', out)
        self.assertIn('package_id: 40 # wire:one', out)
        self.assertIn('other: 5 # not wired', out)
        self.assertIn('apiKey: "PUBKEY123", // wire:api_key (public)', out)

    def test_idempotent(self):
        src = '  package_id: 1 # wire:one\napiKey: "", // wire:api_key\n'
        once = wire_funnel.rewrite(src, VALS)
        self.assertEqual(once, wire_funnel.rewrite(once, VALS))

    def test_real_sources_are_all_tagged(self):
        text = ''.join(f.read_text() for f in wire_funnel.FILES)
        for tag in ('wire:plan', 'wire:one', 'wire:shipping', 'wire:api_key'):
            self.assertIn(tag, text)
        out = ''.join(wire_funnel.rewrite(f.read_text(), VALS) for f in wire_funnel.FILES)
        self.assertIn('package_id: 41 # wire:plan', out)
        self.assertIn('package_id: 40 # wire:one', out)
        self.assertNotIn('LLbBgtusfE2zopDcjnOY9NbrlN690zSjuedqQ04J', out)  # the starter's demo key is gone

    def test_values_refuses_incomplete_manifest(self):
        with self.assertRaises(SystemExit):
            wire_funnel.values({'packages': [], 'shipping_methods': [], 'campaign': {}})


class Shape(unittest.TestCase):
    def plan(self):
        one, mon = campaign_plan.ONE_TIME, campaign_plan.MONTHLY
        return {'packages': [{'key': f'hero-{one}', 'price': '52.97'}, {'key': f'hero-{mon}', 'price': '52.97'}],
                'landed_prices': [
                    {'tier': 'Buy 1', 'kind': 'single', 'qty': 1, 'package_keys': [f'hero-{one}', f'hero-{mon}'],
                     'anchor': '52.97', 'pct': 0, 'unit_after': '52.97', 'order_total': '52.97'},
                    {'tier': 'Upsell', 'kind': 'upsell', 'qty': 1, 'offer_key': 'upsell-4-45',
                     'package_keys': [f'hero-{one}'], 'anchor': '52.97', 'pct': 45, 'unit_after': '29.97',
                     'order_total': '29.97'}],
                'offers': [{'key': 'upsell-4-45', 'name': 'x'}], 'rationale': [], 'handoff': []}

    def test_monthly_package_is_recurring_at_deck_prices(self):
        p = campaign_plan.shape(self.plan())
        mon = next(x for x in p['packages'] if x['key'].startswith('plan-'))
        self.assertEqual((mon['price'], mon['price_recurring'], mon['interval'], mon['interval_count']),
                         ('20.97', '42.97', 'day', 30))
        one = next(x for x in p['packages'] if x['key'].startswith('hero-'))
        self.assertEqual(one['price'], '52.97')
        self.assertNotIn('price_recurring', one)

    def test_landed_rows_split_per_package(self):
        rows = campaign_plan.shape(self.plan())['landed_prices']
        self.assertEqual([(r['tier'], r['order_total']) for r in rows],
                         [('Monthly plan, first bottle', '20.97'), ('One bottle, one-time', '52.97'),
                          ('Upsell: one more bottle', '29.97')])
        self.assertTrue(all(len(r['package_keys']) == 1 for r in rows))


if __name__ == '__main__':
    unittest.main()
