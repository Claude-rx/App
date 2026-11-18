"""Unit tests for tools/andromeda2/shared/scripts/a2.py.

Run: python3 -m unittest discover -s tools/andromeda2/tests -v
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "shared" / "scripts" / "a2.py"
FIX = HERE / "fixtures"
SPEC = importlib.util.spec_from_file_location("a2", SCRIPT)
a2 = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules["a2"] = a2
SPEC.loader.exec_module(a2)


def run_json(*argv: str) -> dict:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        a2.main([*argv, "--json"])
    return json.loads(buf.getvalue())


class Economics(unittest.TestCase):
    def test_break_even_and_buffer(self):
        e = a2.compute_economics(aov=100, cogs_pct=30, shipping=5, fees_pct=3)
        # contribution = 100 - 30 - 5 - 3 = 62 -> BE CPA 62, BE ROAS 1.6129, target = x1.1
        self.assertAlmostEqual(e.break_even_cpa, 62.0)
        self.assertAlmostEqual(e.break_even_roas, 100 / 62, places=4)
        self.assertAlmostEqual(e.target_roas, 100 / 62 * 1.10, places=4)
        self.assertAlmostEqual(e.target_cpa, 100 / e.target_roas, places=4)

    def test_profit_pct_target(self):
        e = a2.compute_economics(aov=100, cogs_pct=30, shipping=5, fees_pct=3, profit_pct=10)
        self.assertAlmostEqual(e.target_cpa, 52.0)  # 62 - 10

    def test_ltv_multiple_raises_break_even_cpa(self):
        e = a2.compute_economics(aov=100, cogs_pct=30, fees_pct=0, ltv_multiple=1.5)
        self.assertAlmostEqual(e.break_even_cpa, 105.0)

    def test_negative_contribution_exits(self):
        with self.assertRaises(SystemExit):
            a2.compute_economics(aov=20, cogs_pct=90, shipping=5)


class TestingPlan(unittest.TestCase):
    def test_volume_rule(self):
        self.assertEqual(a2.creative_volume(3_000)["new_ads_per_week"], 2)       # floor
        self.assertEqual(a2.creative_volume(90_000)["new_ads_per_week"], 9)
        self.assertEqual(a2.creative_volume(100_001)["new_ads_per_week"], 11)    # round up
        self.assertEqual(a2.creative_volume(250_000)["iteration_share"], 0.80)
        self.assertEqual(a2.creative_volume(2_000)["iteration_share"], 0.0)

    def test_pack_minimum_capped_at_20pct(self):
        m = a2.pack_minimum(target_cpa=50, campaign_budget=100, new_packs=1)
        self.assertEqual(m["per_pack_daily_minimum"], 20.0)
        self.assertTrue(m["capped"])
        m = a2.pack_minimum(target_cpa=50, campaign_budget=1000, new_packs=2)
        self.assertEqual(m["per_pack_daily_minimum"], 50.0)
        self.assertLessEqual(m["total_minimums"], 200.0)


class Analyze(unittest.TestCase):
    def setUp(self):
        self.out = run_json("analyze", str(FIX / "ads_export.csv"), "--target-roas", "2.0")
        self.by_ad = {v["ad"]: v for v in self.out["verdicts"]}

    def test_baseline_metrics(self):
        b = self.out["baseline"]
        self.assertAlmostEqual(b["spend"], 10221.65, places=2)
        self.assertGreater(b["hook_rate"], 0.3)
        self.assertFalse(self.out["on_target"])

    def test_top_spender_at_target_is_winner(self):
        self.assertEqual(self.by_ad["P7-V1 hands demo hook"]["verdict"], "WINNER")

    def test_viral_hog_is_capped_not_paused(self):
        self.assertEqual(self.by_ad["P9-V3 viral reel"]["verdict"], "CAP")

    def test_two_x_cpa_rule(self):
        self.assertEqual(self.by_ad["P8-S2 before-after static"]["verdict"], "TOO-EARLY")

    def test_leading_indicator_keeps_ad(self):
        self.assertEqual(self.by_ad["P9-V1 founder story"]["verdict"], "WATCH")

    def test_far_off_kpi_after_3x_cpa_pauses(self):
        self.assertEqual(self.by_ad["P9-V2 street interview"]["verdict"], "PAUSE")

    def test_weak_hook_diagnosis(self):
        self.assertIn("first 3 s", self.by_ad["P7-V2 talking head hook"]["creative_fix"])

    def test_requires_a_target(self):
        with self.assertRaises(SystemExit):
            a2.main(["analyze", str(FIX / "ads_export.csv")])


class Scale(unittest.TestCase):
    def test_small_budget_big_step(self):
        r = a2.scale_step(100, 3.6, 3.5, 2.5)
        self.assertEqual(r["new_budget"], 150.0)

    def test_smashing_doubles_within_delta_math(self):
        r = a2.scale_step(1000, 6.0, 5.2, 2.5)
        self.assertEqual(r["new_budget"], 2000.0)
        r = a2.scale_step(1000, 4.4, 4.2, 2.0)  # 2.1x -> delta cap 2100 > 2x
        self.assertEqual(r["new_budget"], 2000.0)

    def test_big_tight_campaign_small_step(self):
        r = a2.scale_step(8000, 2.8, 2.95, 2.5)
        self.assertAlmostEqual(r["change_pct"], 0.15)

    def test_hold_when_recent_dip(self):
        self.assertEqual(a2.scale_step(8000, 2.0, 2.6, 2.5)["action"], "HOLD")

    def test_cadence(self):
        self.assertEqual(a2.scale_step(2000, 3.0, 3.0, 2.5, hours_since_change=20)["action"], "HOLD")

    def test_cpa_metric_and_cuts(self):
        r = a2.scale_step(2000, 70, 70, 50, metric="cpa")  # 7-day 29% worse than target
        self.assertEqual(r["action"], "DECREASE")
        self.assertAlmostEqual(r["change_pct"], -0.30)


class CostControls(unittest.TestCase):
    def test_cap_equals_target_and_budget_for_80pct(self):
        p = a2.cost_control_plan(target_cpa=52, target_roas=None, expected_spend=40_000, monthly_spend=1_500_000)
        cap = p["controls"][0]
        self.assertEqual(cap["value"], 52)
        self.assertEqual(cap["budget"], 50_000)
        self.assertEqual(p["warnings"], [])

    def test_small_account_warning(self):
        p = a2.cost_control_plan(40, None, 300, monthly_spend=9_000)
        self.assertTrue(p["warnings"])

    def test_four_scenarios(self):
        self.assertEqual(a2.cap_diagnose(52, 48, 50_000, 49_800)["scenario"], 1)
        self.assertEqual(a2.cap_diagnose(52, 60, 50_000, 49_900)["scenario"], 2)
        self.assertEqual(a2.cap_diagnose(52, 60, 50_000, 20_000)["scenario"], 3)
        self.assertEqual(a2.cap_diagnose(52, 50, 50_000, 40_000)["scenario"], 4)
        self.assertIn("walk the cap up", a2.cap_diagnose(45, 44, 50_000, 22_000, true_target=52)["action"])

    def test_roas_goal_direction(self):
        self.assertTrue(a2.cap_diagnose(2.0, 2.3, 1000, 800, metric="roas")["target_hit"])
        self.assertFalse(a2.cap_diagnose(2.0, 1.7, 1000, 800, metric="roas")["target_hit"])


class Zombie(unittest.TestCase):
    def test_buckets(self):
        out = run_json("zombie", str(FIX / "ads_lifetime.csv"), "--breakeven-cpa", "55", "--account-daily-spend", "8000")
        b = out["buckets"]
        names = lambda k: {x["ad"] for x in b[k]}  # noqa: E731
        self.assertEqual(names("fatigued_winner"), {"P1-V1 3am knee", "P1-V2 grandson laces"})
        self.assertIn("P4-V1 golf weekend", names("no_efficiency"))
        self.assertTrue(any(x.get("hog") for x in b["no_efficiency"] if x["ad"] == "P4-V1 golf weekend"))
        self.assertEqual(len(b["dud"]), 1)  # one representative per dead pack
        self.assertEqual(names("keep"), {"P1-S1 joint drought static"})
        self.assertEqual(out["start_budget"], 800.0)

    def test_small_account_budget_floor(self):
        out = run_json("zombie", str(FIX / "ads_lifetime.csv"), "--breakeven-cpa", "55", "--account-daily-spend", "400")
        self.assertEqual(out["start_budget"], 55.0)


class CsvLoading(unittest.TestCase):
    def test_number_formats(self):
        f = a2._to_float
        self.assertEqual(f("$1,234.50"), 1234.5)
        self.assertEqual(f("1.234,50 €"), 1234.5)
        self.assertEqual(f("12,5"), 12.5)
        self.assertEqual(f("12,345,678"), 12345678)
        self.assertEqual(f("2.08%"), 2.08)
        self.assertIsNone(f("--"))

    def test_semicolon_and_currency_headers(self):
        p = HERE / "fixtures" / "_tmp_semicolon.csv"
        p.write_text("Ad name;Amount spent (EUR);Impressions;Link clicks;Website purchases;Website purchases conversion value\n"
                     "A;1.234,50;100000;1500;20;2600\n", encoding="utf-8")
        try:
            rows = a2.load_csv(str(p))
        finally:
            p.unlink()
        self.assertAlmostEqual(rows[0].spend, 1234.5)
        self.assertEqual(rows[0].purchases, 20)
        self.assertEqual(rows[0].impressions, 100000)


if __name__ == "__main__":
    unittest.main()
