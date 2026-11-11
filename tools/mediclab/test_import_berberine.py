"""Offline tests for import_berberine.py: both variants carry the exact Shopify SKU and are told apart by option.

usage: python3 -I tools/mediclab/test_import_berberine.py
"""
import importlib.util, json, sys, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('imp', HERE / 'import_berberine.py')
imp = importlib.util.module_from_spec(spec)
sys.argv = [sys.argv[0]]
spec.loader.exec_module(imp)


class ImportBerberine(unittest.TestCase):
    def test_no_invented_sku(self):
        # SKUs come from Shopify at run time, never from a hard-coded per-variant SKU
        self.assertEqual(imp.SKU, 'JTP4BERB')
        for v in imp.VARIANTS:
            self.assertNotIn('sku', v)

    def test_variants_by_option(self):
        mk = lambda vid, val: {'id': vid, 'sku': 'JTP4BERB', 'variant_attribute_values': [{'name': 'Purchase', 'value': val}]}
        got = {imp.opt(v): v['id'] for v in (mk(5, 'One-time purchase'), mk(6, 'Monthly refill plan'))}
        self.assertEqual(got, {'One-time purchase': 5, 'Monthly refill plan': 6})
        self.assertIsNone(imp.opt({'variant_attribute_values': []}))

    def test_ids_file_matches_store_contract(self):
        ids = json.loads((HERE / 'berberine-ids.json').read_text())
        self.assertEqual(ids['sku'], 'JTP4BERB')
        self.assertEqual(set(ids['variants']), {'one_time', 'monthly'})


if __name__ == '__main__':
    unittest.main()
