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

    def test_minimums_by_budget_band(self):
        # Below $100/day: none. $100-1,000: optional (Q&A 8/31 "$20 minimum at $100/day: yes";
        # Zombie / Scaling-Pixels Q&As "not needed yet") -> buyer's call. $1,000+: standard.
        self.assertEqual(E.pack_minimum(20, 60, 2)["status"], "none")
        small = E.pack_minimum(20, 100, 2)
        self.assertEqual((small["daily_minimum"], small["optional"]), (20, True))
        r150 = E.pack_minimum(30, 150, 3)  # 20% of $150 = $30
        self.assertEqual((r150["daily_minimum"], r150["optional"]), (30, True))
        mid = E.pack_minimum(50, 500, 2)  # capped at 20% = $100
        self.assertEqual((mid["daily_minimum"], mid["optional"]), (50, True))
        self.assertFalse(E.pack_minimum(50, 2000, 2)["optional"])

    def test_minimum_20pct_example_170(self):
        # Optimization Q&A: $170/day with three $20 minimums = 35% -> over the 20% cap ($34 total).
        r = E.pack_minimum(20, 170, 4, other_active_minimums=40)
        self.assertEqual(r["daily_minimum"], 0)
        self.assertEqual(r["status"], "none")

    def test_minimum_interest_pack_and_boost(self):
        self.assertEqual(E.pack_minimum(25, 1000, 3, interest_pack=True)["daily_minimum"], 0)
        # Q&A 8/31: CPA $25, one pack a week -> "$50-100, lean $50".
        self.assertEqual(E.pack_minimum(25, 1000, 3, one_pack_per_week=True)["daily_minimum"], 50)
        # Boost never applies under the standard band, and never beats the 20% cap.
        self.assertEqual(E.pack_minimum(25, 500, 3, one_pack_per_week=True)["daily_minimum"], 25)
        self.assertEqual(E.pack_minimum(150, 1000, 3, one_pack_per_week=True)["daily_minimum"], 200)

    def test_minimum_signal(self):
        self.assertEqual(E.minimum_signal(120, 50, 7)["action"], "REMOVE_MINIMUM")
        self.assertIn("ABOVE", E.minimum_signal(120, 50, 7)["signal"])
        self.assertIn("AT_MINIMUM", E.minimum_signal(52, 50, 4)["signal"])
        self.assertEqual(E.minimum_signal(52, 50, 4)["action"], "WAIT")
        self.assertEqual(E.minimum_signal(50, 50, 8, above_target=True)["action"], "KEEP_MINIMUM")

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

    def test_q12_long_run_note(self):
        r = E.pause_decision({"spend": 400, "purchases": 4, "kpi_actual": 1.2}, {**self.CTX, "window_days": 21})
        self.assertEqual(r["action"], "KEEP")
        self.assertTrue(any("can be considered" in x for x in r["why"]))

    def test_account_at_goal_caps_hog_instead_of_pausing(self):
        # Optimization Q&A: ad set takes 70% of spend, misses target, campaign at goal -> max 50%, judge 2 weeks.
        ctx = {**self.CTX, "account_at_goal": True}
        r = E.pause_decision({"spend": 160, "purchases": 1, "kpi_actual": 0.6, "adset_spend_share": 0.7}, ctx)
        self.assertEqual((r["action"], r["question"]), ("CAP_ADSET", 13))
        # Scaling/Pixels Q&A: a $135-CPA ad vs $40 target -> keep while the account hits goal.
        k = E.pause_decision({"spend": 160, "purchases": 1, "kpi_actual": 0.6, "adset_spend_share": 0.1}, ctx)
        self.assertEqual(k["action"], "KEEP")

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
        self.assertEqual(r["status"], "HEALTHY")
        self.assertTrue(any("Retention" in x for x in r["recommendations"]))
        # Q&A 8/31: 35% of $150/day -> watch, a breakout is not worth it at this budget.
        w = E.engaged_share_check(97.5, 52.5, 0, daily_budget=150)
        self.assertEqual(w["status"], "WATCH")
        self.assertTrue(any("not worth" in x for x in w["recommendations"]))
        self.assertEqual(E.engaged_share_check(50, 50, 0)["status"], "ACT")
        self.assertEqual(E.engaged_share_check(95, 4, 1)["status"], "STARVED")

    def test_cost_cap_utilisation(self):
        # Scaling/Pixels Q&A: ~80% of budget spent = ideal; >90% = cap too loose; ~30% = re-check inputs.
        self.assertEqual(E.cost_cap_action(True, False, 50, 50, 60_000, budget_utilisation=0.8)["action"], "WORKING")
        self.assertEqual(E.cost_cap_action(True, False, 50, 50, 60_000, budget_utilisation=0.95)["action"], "RAISE_BUDGET")
        self.assertEqual(E.cost_cap_action(True, False, 50, 50, 60_000, budget_utilisation=0.3)["action"], "RECHECK_INPUTS")

    def test_funnel_health(self):
        ok = E.funnel_health(400, 200, 100)
        self.assertEqual(ok["leaking_steps"], [])
        # Scaling/Pixels Q&A: 46 ATC -> 8 IC -> 2 purchases after a collection was removed.
        bad = E.funnel_health(46, 8, 2, sessions=500, aov=70)
        self.assertIn("atc_to_ic", bad["leaking_steps"])
        # Retargeting call: 0.7% site CVR at $70 AOV is too low.
        self.assertTrue(any("Site CVR" in x for x in E.funnel_health(100, 50, 7, sessions=1000, aov=70)["why"]))

    def test_scale_funnel_check(self):
        self.assertEqual(E.scale_funnel_check({"cost_per_atc": 10}, {"cost_per_atc": 11})["verdict"], "NORMAL")
        self.assertEqual(E.scale_funnel_check({"cost_per_atc": 10}, {"cost_per_atc": 13})["verdict"], "WATCH")
        self.assertEqual(E.scale_funnel_check({"cost_per_atc": 10}, {"cost_per_atc": 20})["verdict"], "CONCERN")

    def test_pareto_cut(self):
        r = E.pareto_cut({"UK": 60, "IE": 15, "SE": 10, "NO": 5, "DK": 5, "FI": 5})
        self.assertEqual(r["keep"], ["UK", "IE", "SE"])
        self.assertIn("FI", r["cut"])

    def test_zombie_check(self):
        r = E.zombie_check([
            {"name": "p3", "avg_daily_spend_7d": 2.5},
            {"name": "p4", "avg_daily_spend_7d": 2.0, "minimum_active": True},
            {"name": "p5", "avg_daily_spend_7d": 80, "top_ad_spend_share": 0.9, "top_ad_hits_kpi": False},
            {"name": "p6", "avg_daily_spend_7d": 80, "top_ad_spend_share": 0.9, "top_ad_hits_kpi": True},
        ])
        self.assertEqual(r["dud_adsets"], ["p3"])
        self.assertEqual(r["move_top_ad_from"], ["p5"])

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

    def test_relaunch_doubles_on_incremental(self):
        # Q&A 8/31: relaunch at $500 after running $20k/day; double while judged on incremental.
        base = {**self.BASE, "daily_budget": 500, "kpi_by_window": {"14": 2.8, "7": 2.9, "3": 2.9, "1": 2.6},
                "prior_proven_daily": 20_000}
        r = E.vertical_scale({**base, "incremental_kpi_7d": 2.6})
        self.assertEqual((r["action"], r["new_daily_budget"]), ("DOUBLE", 1000))
        big = E.vertical_scale({**base, "daily_budget": 3000, "incremental_kpi_7d": 2.6})
        self.assertEqual((big["action"], big["new_daily_budget"]), ("INCREASE", 4000))
        slow = E.vertical_scale({**base, "incremental_kpi_7d": 2.0})
        self.assertEqual(slow["action"], "INCREASE")
        self.assertLess(slow["new_daily_budget"], 1000)

    def test_new_segment_push_note(self):
        r = E.vertical_scale({**self.BASE, "kpi_by_window": {"14": 2.8, "7": 2.9, "3": 2.9, "1": 2.4},
                              "new_incremental_kpi": 2.6})
        self.assertTrue(any("push" in x for x in r["why"]))

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

    def test_course_profit_sheet(self):
        # Setup: Profit Tracking sheet, opened first-hand: 100 orders x $75, 35% COGS, $0 fixed.
        be = E.profit_model(100, 75, 0.35, 0)
        self.assertEqual((be["breakeven_roas_blended"], be["breakeven_cpa"], be["ad_spend_pct_of_revenue"]), (1.54, 48.75, 0.65))
        tk = E.profit_model(100, 75, 0.35, 0, take_pct=0.10)
        self.assertEqual((tk["breakeven_roas_blended"], tk["breakeven_cpa"], tk["ad_spend_budget"], tk["profit"]),
                         (1.82, 41.25, 4125, 750))
        big = E.profit_model(1000, 125, 0.33, 10_000, take_pct=0.30)
        self.assertEqual((big["breakeven_roas_blended"], big["breakeven_cpa"], big["profit"]), (3.45, 36.25, 37_500))

    def test_pacing(self):
        r = E.pacing(30_000, 12_000, 90_000, 30_000, 15)
        self.assertEqual(r["daily_spend_to_hit_goal"], 1200)
        self.assertEqual(r["daily_revenue_to_hit_goal"], 4000)
        self.assertEqual(r["roas_to_hit_goal"], 3.33)

    def test_reverse_target(self):
        # Product First call: $100 job, 10% of calls close -> $10 per call.
        self.assertEqual(E.reverse_target(100, 0.10, "call")["target_cost_per_call"], 10)
        # Q&A 8/31: $100 per paid sub, 10% of trials convert -> $10 per trial.
        self.assertEqual(E.reverse_target(100, 0.10, "trial")["target_cost_per_trial"], 10)


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
