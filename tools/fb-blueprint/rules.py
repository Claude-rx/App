"""Facebook Ads Blueprint SOP: the numeric rules, in one place.

Every threshold the media-buying SOP (docs/media-buying/SOP.md) relies on lives in
RULES below, each with the course lesson it comes from. The decision functions in
engine.py read only from here, so a team override (rules.local.json) changes
behaviour everywhere at once.

Values marked "team default" are NOT stated in the course; they fill a boundary
the course leaves open (for example, what counts as "large spend") and are listed
in SOP.md section 13 so the team can confirm or change them.
"""

from __future__ import annotations

import copy
import json
import os

RULES: dict = {
    # ---------------------------------------------------------------- launch
    "launch": {
        # Pack 1 never gets a minimum; packs 2+ get min = 1x target CPA capped at
        # 20% of the campaign daily budget, for 7 days only.
        # Sources: M4 Prospecting, M4 Structure Overview, AOV live call.
        "pack_min_cpa_multiple": 1.0,
        "pack_min_budget_cap_pct": 0.20,
        "pack_min_days": 7,
        # Launching only ~1 pack a week at a standard budget: the minimum may go
        # above 1x CPA (Q&A 8/31: CPA $25 -> "$50-100, I lean to $50"), still
        # inside the 20% cap. Never put a minimum on an interest pack (Product
        # First call) or on an ad set already taking ~50% (M4 Scale).
        "pack_min_boost_cpa_multiple": 2.0,
        # Ad set minimums by prospecting daily budget (SOP 13 decision #1):
        # none below $100; optional $100-1,000 (live calls: "$20/day minimum at
        # $100/day -> yes and yes" (Q&A 8/31) but also "you don't really need
        # minimums quite yet at $100/day" (Scaling/Pixels Q&A); M4 Prospecting
        # shows the 20%-cap math at $100); standard from $1,000 (First $100 Setup).
        "min_spend_limits_from_daily_budget": 100,
        "min_spend_limits_standard_from_daily_budget": 1000,
        # Ads per pack: 4-8 sweet spot, 2 acceptable, up to 12 if all strong.
        # Sources: # Of Ads To Launch, M4 Structure Overview, Funnel Analysis call.
        "ads_per_pack_min": 2,
        "ads_per_pack_sweet_low": 4,
        "ads_per_pack_sweet_high": 8,
        "ads_per_pack_max": 12,
        # Weekly creative volume: 1 new ad / week per $10k MONTHLY spend, floor 2.
        # Source: # Of Ads To Launch (calculator); Funnel Analysis call.
        "ads_per_week_per_monthly_spend": 10000,
        "ads_per_week_floor": 2,
        # Proven-concept share by monthly spend (calculator readings).
        # Source: # Of Ads To Launch. Between anchors we interpolate linearly
        # (team default; the calculator is a slider).
        "proven_share_anchors": [[10000, 0.13], [100000, 0.53], [200000, 0.80]],
        "proven_share_cap": 0.80,
        # Retention budget <= 10% of prospecting ("not law"). Source: M4 Retention.
        "retention_budget_max_pct_of_prospecting": 0.10,
        # Catalog retargeting $5-10/day. Source: Catalog Retargeting Retention.
        "catalog_retargeting_daily": [5, 10],
        # Scale campaign holds 1-3 ads. Source: NEW Current Structure M4.
        "scale_campaign_max_ads": 3,
        # Audience windows (days). Sources: Advertiser Settings, M4 videos.
        "windows": {
            "purchasers_exclusion": 180,
            "engaged_atc": 90,
            "engaged_visitors": 30,
            "retargeting_visitors": 30,
            "retargeting_atc_ic": 90,
            "engagers": 14,
            "engagers_max": 30,
            "catalog_view_atc": 14,
            "catalog_purchase_exclusion": 14,
        },
        # Interest suggestion only while lifetime spend < $1,000 (First $100 Setup).
        "interest_suggestion_lifetime_spend_below": 1000,
        # Copy volume (Prospecting transcript: >=2 primary texts, ~2 headlines,
        # up to 5; Ads That Scale call: 5 + 5).
        "primary_texts_min": 2,
        "primary_texts_max": 5,
        "headlines_min": 2,
        "headlines_max": 5,
        "site_links_min": 4,
        "placements_default_count": 23,
    },
    # ------------------------------------------------------------------ test
    "test": {
        # Creative judgment window: 14 days when daily spend < $1,000, 7 days at
        # >= $1,000/day. Source: Foundation: The Flywheel.
        "judgment_window_low_spend_days": 14,
        "judgment_window_high_spend_days": 7,
        "judgment_window_spend_threshold_daily": 1000,
        # Pausing tree minimum window 7-14 days. Source: Pausing Ads.
        "pause_window_min_days": 7,
        # Spend gates. Source: Pausing Ads (Q10, Q11, Q13).
        "pause_spend_gate_cpa_multiple": 2.0,
        "pause_underperformer_cpa_multiple": 3.0,
        "pause_kpi_tolerance": 0.50,
        # Graduation: top 10% of spenders AND incremental ROAS >= baseline.
        # Source: Graduation System.
        "graduation_top_spend_pct": 0.10,
        # Breakout winner (Claude: Unlimited Ads Workflow doc prompt):
        # launched <= 30d, >= 10% of account spend, ROAS > account average in
        # any of the 7/14/30-day windows.
        "breakout_max_age_days": 30,
        "breakout_min_spend_share": 0.10,
        "breakout_windows": [7, 14, 30],
        # Minimum-spend signal (Q&A 8/31, Product First, Retargeting calls): a
        # pack that spends ABOVE its minimum is carrying itself; one that sits AT
        # the minimum will fall away when it is removed. "At" = within 10%
        # (team default; the course draws it as "right at the line").
        "minimum_stuck_band": 0.10,
        # Zombie duds: ad sets drawing $2-3/day after minimums end (Q&A 9/9).
        "zombie_dud_daily_spend_max": 3.0,
        # A hog ad set missing target while the campaign is at goal: cap it at
        # ~50% max, never pause it, and judge over ~2 weeks (Optimization Q&A).
        "hog_cap_pct": 0.50,
        "hog_judge_days": 14,
        # Shotgun & Sniper kill switches (high creative volume brands only).
        "shotgun_gauntlet_days": 7,
        "shotgun_scale_step_min": 0.25,
    },
    # -------------------------------------------------------------- optimize
    "optimize": {
        # Frequency ceilings [low, high] per window. Source: Frequency Management.
        "frequency": {
            "prospecting": {"7": [2, 3], "14": [2, 5], "30": [2, 7]},
            "retargeting": {"7": [None, 5], "14": [5, 10], "30": [None, 15]},
            "existing": {"7": [2, 4], "14": [4, 10], "30": [None, 15]},
        },
        # Retargeting 30d frequency > 15 -> cut ~20% even if above target.
        "retargeting_over_freq_budget_cut": 0.20,
        # Prospecting 7d frequency: 3.5 fine if above target; 5 = dig in.
        "prospecting_freq_dig_in_7d": 5.0,
        # Learning-phase spend share. Source: Dictionary (account overview).
        "learning_phase_healthy_max": 0.15,  # team default around the "11% very healthy" example
        "learning_phase_too_much": 0.85,
        # Pixel gut check. Source: Setup: Pixel Gut Check.
        "pixel_browser_server_max_gap": 0.10,
        "pixel_server_vs_orders_max_gap": 0.02,
        "emq_good": 8.4,
        "emq_benchmark": 8.8,
        # Anomaly detector default threshold 20%. Source: Claude: Anomaly Dashboard.
        "anomaly_threshold": 0.20,
        # Drop = results down 20-30% beyond normal. Source: Funnel Analysis call.
        "drop_definition_pct": 0.20,
        # Value rules: start <= 25% (Value Rules); 25-30% start, 30-50% sweet
        # spot, > 50% unstable (Funnel Analysis call). Ignore 5-10% gaps.
        "value_rule_start": 0.25,
        "value_rule_max": 0.50,
        "value_rule_min_effect": 0.10,
        # Placements: top 6 by spend must be FB/IG Feed, Stories, Reels; ~1% is a
        # red flag. Source: Placement Breakdown + Optimizations.
        "core_placements": [
            "facebook_feed", "instagram_feed", "facebook_stories",
            "instagram_stories", "facebook_reels", "instagram_reels",
        ],
        "placement_red_flag_share": 0.01,
        # Geo: ~2x average CPP = cut; ~+24% = keep (example-derived; team default
        # boundary 1.5x). Source: Country / Geographic Testing.
        "geo_cut_cpp_multiple": 1.5,
        # Cost caps only at ~$50k-100k+/month. Source: Cost Controls.
        "cost_cap_min_monthly_spend": 50000,
        "cost_cap_budget_utilisation": 0.80,
        # Spending ~80% of budget = ideal; >90-95% = cap too loose; ~30% every
        # day = re-check AOV/LTV/cap (Scaling/Pixels Q&A).
        "cost_cap_too_loose": 0.90,
        "cost_cap_starved": 0.30,
        "cost_cap_step": 1.0,
        # Engaged share of prospecting spend (live calls): 10% bare minimum,
        # 10-20% usual, 20-25% still healthy (Q&A 8/3), mid-40s+ = act
        # (Q&A 8/31: 35% of $150/day "not worth breaking out"). The share moves
        # opposite to budget changes; more spend (not more creative) lowers it.
        "engaged_share_floor": 0.10,
        "engaged_share_soft_flag": 0.20,
        "engaged_share_normal_upper": 0.25,
        "engaged_share_act": 0.45,
        # Funnel: expect ~50% drop per step (ATC -> IC -> purchase), i.e.
        # 100 purchases ~ 200 IC ~ 400 ATC (Q&A 8/24). Flag a step converting
        # under 35% (team default boundary).
        "funnel_step_expected": 0.50,
        "funnel_step_flag": 0.35,
        # On-site conversion rate ~1.2-1.5% at a ~$70 AOV (Retargeting call).
        "site_cvr_benchmark": [0.012, 0.015],
        # Scale check: after a budget jump, cost per ATC/IC up 3-15% is normal;
        # "if I double spend and my cost per ATC doubles, I'm very concerned"
        # (Q&A 8/31). Concern boundary +50% is a team default.
        "scale_cost_rise_normal": 0.15,
        "scale_cost_rise_concern": 0.50,
        # Geo/product 80/20: keep what drove 80% of revenue, cut the long tail
        # (Q&A 8/31 geo, Products lesson).
        "pareto_keep_share": 0.80,
        # Free-shipping threshold should qualify ~75% of orders. Source: AOV call.
        "free_shipping_qualify_share": 0.75,
    },
    # ----------------------------------------------------------------- scale
    "scale": {
        # Vertical: 10-30% every 48-72h; 10-15% at multi-thousand/day; bigger at
        # ~$100/day; double when "smashing" (>= 2x target). Source: Vertical Scaling.
        "step_default": [0.10, 0.30],
        "step_large_spend": [0.10, 0.15],
        "step_small_spend_max": 0.50,
        "large_spend_daily": 2000,   # team default for "multiple thousands of dollars per day"
        "small_spend_daily": 200,    # team default around the "$100/day" example
        "min_hours_between_moves": 48,
        "max_hours_between_moves": 72,
        "smashing_multiple": 2.0,
        # Stability: look 14 -> 7 -> 3 -> 1 days; never decide off yesterday.
        "stability_windows": [14, 7, 3, 1],
        # Relaunch to a previously proven spend (Q&A 8/31: $500 back to a former
        # $20k/day): doubling is fine while under the old level, judged on
        # INCREMENTAL attribution; past ~$3k/day add about $1k per move.
        "relaunch_double_until_daily": 3000,
        "relaunch_step_after_daily": 1000,
        # Horizontal: not at ~$100/day; careful at $1,000/day. Source: Horizontal Scaling.
        "horizontal_not_ready_daily": 100,
        "horizontal_careful_daily": 1000,
        # Retargeting/retention are managed by frequency, not by these steps.
    },
    # ---------------------------------------------------------------- profit
    "profit": {
        # LTV:CAC > 2.5 good, < 2 scary, > 3 very good. Source: Setup: Profit Tracking.
        "ltv_cac_good": 2.5,
        "ltv_cac_scary": 2.0,
        # Target ROAS = break-even + 10-20% take-home. Source: Ads That Scale /
        # Hotline calls (2.0 -> 2.2).
        "target_over_breakeven_default": 0.10,
    },
}


def load_rules(path: str | None = None) -> dict:
    """Return RULES, deep-merged with a team override JSON if one exists.

    The override file defaults to rules.local.json next to this module and may
    contain any subset of RULES (same nesting).
    """
    rules = copy.deepcopy(RULES)
    path = path or os.path.join(os.path.dirname(__file__), "rules.local.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            _deep_merge(rules, json.load(fh))
    return rules


def _deep_merge(base: dict, over: dict) -> None:
    for key, value in over.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
