"""Tests for the Blueprint decision engine.

Each case reproduces a worked example from the course (cited) so a change to a
threshold that breaks the SOP shows up here.

    python3 -m unittest discover -s tools/fb-blueprint -v
"""

import json
import os
import subprocess
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import engine as E  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


class Launch(unittest.TestCase):
    def test_ads_per_week_course_examples(self):
        # "# Of Ads To Launch": $100k -> 10/week, $200k -> 20/week, low spend floor 2.
        self.assertEqual(E.ads_per_week(100_000)["ads_per_week"], 10)
        self.assertEqual(E.ads_per_week(200_000)["ads_per_week"], 20)
        self.assertEqual(E.ads_per_week(3_000)["ads_per_week"], 2)
        self.assertEqual(E.ads_per_week(90_000)["ads_per_week"], 9)

    def test_proven_share_anchors(self):
        self.assertAlmostEqual(E.ads_per_week(10_000)["proven_share"], 0.13)
        self.assertAlmostEqual(E.ads_per_week(100_000)["proven_share"], 0.53)
        self.assertAlmostEqual(E.ads_per_week(500_000)["proven_share"], 0.80)

    def test_pack_one_never_gets_minimum(self):
        self.assertEqual(E.pack_minimum(50, 5000, 1)["daily_minimum"], 0)

    def test_pack_minimum_is_one_cpa(self):
        r = E.pack_minimum(50, 2000, 2)
        self.assertEqual(r["daily_minimum"], 50)
        self.assertEqual(r["remove_after_days"], 7)

    def test_pack_minimum_capped_at_20pct_total(self):
        # M4 Prospecting / Retargeting Q&A: at $1,000/day all minimums total <= $200.
        r = E.pack_minimum(100, 1000, 4, other_active_minimums=150)
        self.assertEqual(r["daily_minimum"], 50)
        self.assertEqual(r["status"], "reduced")
        r = E.pack_minimum(100, 1000, 5, other_active_minimums=200)
        self.assertEqual(r["daily_minimum"], 0)

    def test_no_minimums_on_small_budgets(self):
        # First $100 Setup / Zombie Q&A ($150/day: "don't set minimums yet").
        self.assertEqual(E.pack_minimum(30, 150, 3)["status"], "none")
        mid = E.pack_minimum(50, 500, 2)  # $250-1,000: optional, capped at 20% = $100
        self.assertEqual((mid["daily_minimum"], mid["optional"]), (50, True))
        self.assertFalse(E.pack_minimum(50, 2000, 2)["optional"])

    def test_retention_cap(self):
        self.assertTrue(E.retention_budget(1000, 100)["ok"])
        self.assertFalse(E.retention_budget(1000, 150)["ok"])

    def test_preflight_blocks_on_unknown(self):
        r = E.preflight({"king_goal_set": True})
        self.assertFalse(r["ready"])
        self.assertIn("pixel_gut_check_passed", r["blockers"])
        all_ok = {c["check"]: True for c in r["checks"]}
        self.assertTrue(E.preflight(all_ok)["ready"])


class Test(unittest.TestCase):
    CTX = {"kpi_type": "roas", "kpi_target": 2.0, "target_cpa": 50, "avg_cost_per_ic": 10,
           "pixel_ok": True, "window_days": 14}

    def test_judgment_window(self):
        self.assertEqual(E.judgment_window(500)["days"], 14)
        self.assertEqual(E.judgment_window(1500)["days"], 7)

    def test_keep_when_hitting_kpi(self):
        r = E.pause_decision({"spend": 900, "purchases": 10, "kpi_actual": 2.4}, self.CTX)
        self.assertEqual((r["action"], r["question"]), ("KEEP", 1))

    def test_wait_on_short_window(self):
        r = E.pause_decision({"spend": 900, "purchases": 1, "kpi_actual": 0.3}, {**self.CTX, "window_days": 3})
        self.assertEqual(r["action"], "WAIT")

    def test_spend_gate(self):
        r = E.pause_decision({"spend": 80, "purchases": 0, "kpi_actual": 0}, self.CTX)
        self.assertEqual((r["action"], r["question"]), ("WAIT", 10))

    def test_zero_results_pause(self):
        r = E.pause_decision({"spend": 100, "purchases": 0, "ic": 0, "kpi_actual": 0}, self.CTX)
        self.assertEqual((r["action"], r["question"]), ("PAUSE", 11))

    def test_zero_purchases_but_healthy_ic_keeps(self):
        r = E.pause_decision({"spend": 120, "purchases": 0, "ic": 12, "cost_per_ic": 9, "kpi_actual": 0}, self.CTX)
        self.assertEqual((r["action"], r["question"]), ("KEEP", 7))

    def test_within_50pct_keeps(self):
        # Pausing Ads: tROAS 2.0, actual 1.2 -> "not generally worth a pause right away".
        r = E.pause_decision({"spend": 400, "purchases": 4, "kpi_actual": 1.2}, self.CTX)
        self.assertEqual((r["action"], r["question"]), ("KEEP", 12))

    def test_three_cpa_and_far_off_pauses(self):
        r = E.pause_decision({"spend": 160, "purchases": 1, "kpi_actual": 0.6}, self.CTX)
        self.assertEqual((r["action"], r["question"]), ("PAUSE", 13))

    def test_far_off_but_under_3x_waits(self):
        r = E.pause_decision({"spend": 120, "purchases": 1, "kpi_actual": 0.6}, self.CTX)
        self.assertEqual(r["action"], "WAIT")

    def test_viral_caps_instead_of_pausing(self):
        r = E.pause_decision({"spend": 900, "purchases": 1, "kpi_actual": 0.5, "viral": True}, self.CTX)
        self.assertEqual(r["action"], "CAP_ADSET")

    def test_cpa_kpi(self):
        ctx = {**self.CTX, "kpi_type": "cpa", "kpi_target": 50}
        self.assertEqual(E.pause_decision({"spend": 500, "purchases": 11, "kpi_actual": 45}, ctx)["action"], "KEEP")
        self.assertEqual(E.pause_decision({"spend": 500, "purchases": 2, "kpi_actual": 250}, ctx)["action"], "PAUSE")

    def test_graduation_ignores_low_spend_outliers(self):
        # Graduation System: 9 ROAS on $48 spend is a trap.
        ads = [{"name": f"a{i}", "spend": 1000 - i * 50, "incremental_roas": 1.0} for i in range(19)]
        ads[0]["incremental_roas"] = 1.4
        ads.append({"name": "trap", "spend": 48, "incremental_roas": 9.0})
        r = E.graduation(ads, 1.2)
        self.assertEqual(r["winners"], ["a0"])
        self.assertNotIn("trap", r["top_spenders_considered"])

    def test_breakout_winner(self):
        windows = {"7": {"account_spend": 10000, "account_roas": 2.0, "ads": [
            {"id": "1", "name": "new-winner", "spend": 1500, "roas": 2.5},
            {"id": "2", "name": "old-winner", "spend": 3000, "roas": 3.0},
            {"id": "3", "name": "small", "spend": 500, "roas": 4.0}]}}
        r = E.breakout_winners(windows, {"1": 10, "2": 90, "3": 5})
        self.assertEqual([w["name"] for w in r["winners"]], ["new-winner"])

    def test_shotgun_targets_match_course(self):
        # Shotgun & Sniper worked example.
        t = E.shotgun_targets(8.81, 14.88, 41.24, 79.22)
        self.assertAlmostEqual(t["roas"], 1.92, places=2)
        self.assertAlmostEqual(t["atc_to_ic_rate"], 0.592, places=3)
        self.assertAlmostEqual(t["ic_to_purchase_rate"], 0.361, places=3)
        self.assertEqual(E.shotgun_kill({"spend": 9, "atc": 0}, t, 1)["action"], "KILL")
        self.assertEqual(E.shotgun_kill({"spend": 45, "atc": 3, "ic": 2, "purchases": 0}, t, 2)["action"], "KEEP")


class Optimize(unittest.TestCase):
    def test_frequency_bands(self):
        self.assertEqual(E.frequency_check("prospecting", 7, 2.5)["status"], "ok")
        self.assertEqual(E.frequency_check("prospecting", 7, 5)["status"], "over")
        self.assertIn("cut budget", E.frequency_check("retargeting", 30, 18)["action"])
        self.assertIn("spend more", E.frequency_check("retargeting", 14, 2)["action"])

    def test_pixel(self):
        self.assertTrue(E.pixel_check(920, 1000, 1005, 8.8)["ok"])
        r = E.pixel_check(700, 1000, 1000, 8.0)
        self.assertFalse(r["ok"])
        self.assertEqual(len(r["issues"]), 2)

    def test_learning_phase(self):
        self.assertEqual(E.learning_phase_check(0.11)["status"], "healthy")
        self.assertEqual(E.learning_phase_check(0.9)["status"], "too_many_changes")

    def test_anomalies_flag_spend_drop_with_flat_secondary(self):
        day = {"spend": 1000, "revenue": 2500, "purchases": 25, "clicks": 1000, "impressions": 100000}
        daily = [dict(day) for _ in range(30)] + [{"spend": 600, "revenue": 1500, "purchases": 15, "clicks": 600, "impressions": 60000}]
        r = E.anomalies(daily)
        metrics = {f["metric"] for f in r["flags"]}
        self.assertIn("spend", metrics)
        self.assertNotIn("cpc", metrics)
        self.assertIsNotNone(r["hint"])

    def test_drop_diagnosis_finds_checkout(self):
        # Funnel Analysis call: CPM/CPC/ATC flat, cost per IC $25 -> $40.
        r = E.drop_diagnosis({"cpm": 20, "cpc": 1, "cost_per_atc": 10, "cost_per_ic": 25, "cpa": 50},
                             {"cpm": 20.5, "cpc": 1.02, "cost_per_atc": 10.2, "cost_per_ic": 40, "cpa": 75})
        self.assertEqual(r["first_break"], "cost_per_ic")

    def test_cost_cap_matrix(self):
        self.assertEqual(E.cost_cap_action(True, True, 50, 50, 10_000)["action"], "DONT_USE_CAPS")
        self.assertEqual(E.cost_cap_action(True, True, 50, 50, 80_000)["action"], "RAISE_BUDGET")
        r = E.cost_cap_action(True, False, 45, 50, 80_000)
        self.assertEqual((r["action"], r["new_cap"]), ("RAISE_CAP_1", 46))
        self.assertEqual(E.cost_cap_action(True, False, 50, 50, 80_000)["action"], "MAKE_CREATIVE")
        self.assertEqual(E.cost_cap_action(False, False, 50, 50, 80_000)["action"], "MAKE_NEW_CREATIVE_OR_STOP_CAPS")

    def test_engaged_share(self):
        # NEW Current Structure example: $91k new, $26k engaged, $6k existing, existing freq 64.
        r = E.engaged_share_check(91_000, 26_000, 6_000, existing_freq_7d=64)
        self.assertAlmostEqual(r["shares"]["engaged"], 0.211, places=3)
        self.assertTrue(any("Retention" in x for x in r["recommendations"]))

    def test_placement_and_geo(self):
        spend = {"facebook_feed": 40, "instagram_feed": 20, "facebook_stories": 10, "instagram_stories": 10,
                 "facebook_reels": 0.5, "instagram_reels": 9, "audience_network": 10.5}
        r = E.placement_check(spend)
        self.assertIn("facebook_reels", r["core_missing_from_top6"])
        g = E.geo_check({"US": 40, "UK": 52, "ES": 50, "NZ": 85}, 42)
        self.assertEqual(g["cut"], ["NZ"])

    def test_value_rule_course_example(self):
        # Value Rules: -25%, $10k revenue on $5k spend -> perceived 1.5 vs actual 2.0.
        r = E.value_rule_effect(10_000, 5_000, -0.25)
        self.assertEqual((r["perceived_roas"], r["actual_roas"]), (1.5, 2.0))

    def test_dow_budgets_keep_week_flat(self):
        # Day of Week: $1,000 base, +50% on 3 days must not overspend the week.
        r = E.dow_budgets(1000, ["fri", "sat", "sun"], 0.5)
        self.assertAlmostEqual(r["weekly_total"], 7000)
        self.assertAlmostEqual(r["low_day_budget"], 625)


class Scale(unittest.TestCase):
    BASE = {"kpi_type": "roas", "kpi_target": 2.5, "daily_budget": 1000, "hours_since_last_change": 72}

    def test_hold_below_target(self):
        r = E.vertical_scale({**self.BASE, "kpi_by_window": {"14": 2.3, "7": 2.6, "3": 2.7, "1": 3}})
        self.assertEqual(r["action"], "HOLD")

    def test_hold_when_last3_unstable(self):
        r = E.vertical_scale({**self.BASE, "kpi_by_window": {"14": 2.8, "7": 2.7, "3": 2.2, "1": 2}})
        self.assertEqual(r["action"], "HOLD")

    def test_increase_in_band(self):
        r = E.vertical_scale({**self.BASE, "kpi_by_window": {"14": 2.8, "7": 2.9, "3": 2.9, "1": 2.4}})
        self.assertEqual(r["action"], "INCREASE")
        self.assertTrue(0.10 <= r["step_pct"] <= 0.30)

    def test_wait_inside_48h(self):
        r = E.vertical_scale({**self.BASE, "hours_since_last_change": 24,
                              "kpi_by_window": {"14": 2.8, "7": 2.9, "3": 2.9, "1": 2.4}})
        self.assertEqual(r["action"], "WAIT")

    def test_large_spend_band(self):
        r = E.vertical_scale({**self.BASE, "daily_budget": 5000,
                              "kpi_by_window": {"14": 4, "7": 4.5, "3": 4.4, "1": 4}})
        self.assertLessEqual(r["step_pct"], 0.15)

    def test_smashing_doubles_with_delta_check(self):
        # Vertical Scaling: $1,000 at 5x vs 2.5 target -> $5,000 revenue; double to $2,000 -> 2.5 worst case.
        r = E.vertical_scale({**self.BASE, "kpi_by_window": {"14": 4.8, "7": 5, "3": 5.2, "1": 5},
                              "revenue_7d_daily_avg": 5000})
        self.assertEqual((r["action"], r["new_daily_budget"]), ("DOUBLE", 2000))

    def test_incremental_caution_uses_smallest_step(self):
        r = E.vertical_scale({**self.BASE, "kpi_by_window": {"14": 3, "7": 3.4, "3": 3.3, "1": 3},
                              "new_incremental_kpi": 1.64})
        self.assertAlmostEqual(r["step_pct"], 0.10)

    def test_horizontal(self):
        self.assertFalse(E.horizontal_readiness(100, "sale")["allowed"])
        self.assertFalse(E.horizontal_readiness(3000, "more spend")["allowed"])
        self.assertTrue(E.horizontal_readiness(3000, "sale")["allowed"])


class Profit(unittest.TestCase):
    def test_small_breakeven_example(self):
        # Profit Tracking: 100 orders, $80 AOV, 40% COGS, $1,000 fixed -> $3,800 spend, 2.11 BE ROAS.
        r = E.profit_model(100, 80, 0.40, 1000, ltv_12m=140)
        self.assertEqual(r["ad_spend_budget"], 3800)
        self.assertEqual(r["breakeven_roas_blended"], 2.11)
        self.assertEqual(r["ltv_multiple"], 1.75)
        self.assertEqual(r["gravy_12m_revenue"], 6000)
        self.assertEqual(r["gravy_12m_profit"], 3600)

    def test_large_and_take_examples(self):
        r = E.profit_model(2000, 125, 0.33, 10_000)
        self.assertEqual(r["breakeven_roas_blended"], 1.59)
        self.assertEqual(round(r["breakeven_cpa"]), 79)  # course says "$78"
        t = E.profit_model(2000, 125, 0.33, 10_000, take_pct=0.10)
        self.assertEqual(t["breakeven_roas_blended"], 1.89)
        self.assertEqual(round(t["breakeven_cpa"]), 66)
        self.assertEqual(t["profit"], 25_000)

    def test_target_roas(self):
        self.assertEqual(E.target_roas(2.0)["target_roas"], 2.2)


class Cli(unittest.TestCase):
    def run_cli(self, cmd, payload):
        out = subprocess.run([sys.executable, os.path.join(HERE, "blueprint.py"), cmd],
                             input=json.dumps(payload), capture_output=True, text=True, check=True)
        return json.loads(out.stdout)

    def test_cli_round_trip(self):
        self.assertEqual(self.run_cli("ads_per_week", {"monthly_spend": 45000})["ads_per_week"], 5)

    def test_cli_list(self):
        out = subprocess.run([sys.executable, os.path.join(HERE, "blueprint.py"), "list"],
                             capture_output=True, text=True, check=True)
        self.assertIn("pause_decision", out.stdout)


if __name__ == "__main__":
    unittest.main()
