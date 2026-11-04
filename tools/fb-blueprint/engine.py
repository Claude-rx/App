"""Decision engine for the Facebook Ads Blueprint SOP.

Pure functions: plain dicts in, plain dicts out, no network. The skills
(.claude/skills/fb-*) pull numbers from Meta through the Meta Ads MCP, pass them
here, and act on the returned decision only after a human approves it.

Every result carries `rule` (the SOP section) and `why` (plain-language reasons
with the numbers), so a media buyer can check each call against SOP.md.
"""

from __future__ import annotations

import math

from rules import load_rules

R = load_rules()


def _r(section: str) -> dict:
    return R[section]


# ======================================================================
# LAUNCH
# ======================================================================

def ads_per_week(monthly_spend: float) -> dict:
    """SOP 6.1: how many new ads to launch per week, and the new/proven split."""
    L = _r("launch")
    count = max(L["ads_per_week_floor"], math.ceil(monthly_spend / L["ads_per_week_per_monthly_spend"]))
    proven = _interp(monthly_spend, L["proven_share_anchors"], L["proven_share_cap"])
    proven_n = round(count * proven)
    return {
        "rule": "SOP 6.1",
        "ads_per_week": count,
        "proven_share": round(proven, 2),
        "new_concepts": count - proven_n,
        "proven_iterations": proven_n,
        "packs_suggested": max(1, math.ceil(count / L["ads_per_pack_sweet_high"])),
        "why": [
            f"1 new ad per week per ${L['ads_per_week_per_monthly_spend']:,} monthly spend, floor {L['ads_per_week_floor']}",
            f"proven-concept share at ${monthly_spend:,.0f}/mo = {proven:.0%} (calculator anchors, capped at {L['proven_share_cap']:.0%})",
            "Quality beats volume: launch only ads you would be proud of, even if fewer than this number.",
        ],
    }


def _interp(x: float, anchors: list, cap: float) -> float:
    if x <= anchors[0][0]:
        return anchors[0][1]
    for (x0, y0), (x1, y1) in zip(anchors, anchors[1:]):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return cap


def pack_minimum(target_cpa: float, campaign_daily_budget: float, pack_number: int,
                 other_active_minimums: float = 0.0, interest_pack: bool = False,
                 one_pack_per_week: bool = False) -> dict:
    """SOP 5.4: ad set daily minimum for a new prospecting pack.

    min = 1x target CPA, but all live minimums together <= 20% of the campaign
    budget; pack 1 never gets one; below the spend-limit threshold none at all.
    """
    L = _r("launch")
    why = []
    threshold = L["min_spend_limits_from_daily_budget"]
    if pack_number <= 1:
        return {"rule": "SOP 5.4", "status": "none", "daily_minimum": 0,
                "why": ["Pack 1 never gets an ad set minimum."]}
    if interest_pack:
        return {"rule": "SOP 5.4", "status": "none", "daily_minimum": 0,
                "why": ["Interest packs hold already-proven winners: no minimum (Product First call). "
                        "Minimums are only for newly launched broad packs."]}
    if campaign_daily_budget < threshold:
        return {"rule": "SOP 5.4", "status": "none", "daily_minimum": 0,
                "why": [f"Prospecting budget ${campaign_daily_budget:,.0f}/day is below ${threshold:,}/day: "
                        "no ad set spending limits yet (First $100 Setup / live calls). Let CBO distribute."]}
    pool = L["pack_min_budget_cap_pct"] * campaign_daily_budget - other_active_minimums
    standard = campaign_daily_budget >= L["min_spend_limits_standard_from_daily_budget"]
    mult = L["pack_min_boost_cpa_multiple"] if (one_pack_per_week and standard) else L["pack_min_cpa_multiple"]
    wanted = mult * target_cpa
    amount = max(0.0, min(wanted, pool))
    why.append(f"wanted {mult:g}x target CPA = ${wanted:,.2f}"
               + (" (only ~1 pack a week at a standard budget, so a firmer minimum is allowed)" if mult > 1 else ""))
    why.append(f"20% cap = ${L['pack_min_budget_cap_pct'] * campaign_daily_budget:,.2f}, "
               f"already used by other live minimums ${other_active_minimums:,.2f} -> room ${max(pool, 0):,.2f}")
    status = "set" if amount >= wanted else ("reduced" if amount > 0 else "none")
    if status == "none":
        why.append("No room under the 20% cap: launch without a minimum, or wait for an older pack's 7 days to end.")
    optional = campaign_daily_budget < L["min_spend_limits_standard_from_daily_budget"]
    if optional and amount > 0:
        why.append(f"Budget under ${L['min_spend_limits_standard_from_daily_budget']:,}/day: the minimum is OPTIONAL "
                   "(buyer's call). Skip it if CBO is already giving new packs spend.")
    why.append("Remove after 7 days no matter what, unless it is crushing above target while still only "
               "spending at the minimum.")
    return {"rule": "SOP 5.4", "status": status, "optional": optional and amount > 0,
            "daily_minimum": round(amount, 2), "remove_after_days": L["pack_min_days"], "why": why}


def minimum_signal(avg_daily_spend: float, daily_minimum: float, days_live: int,
                   above_target: bool | None = None) -> dict:
    """SOP 5.4 / 7.2: read a pack's minimum-spend behaviour before the minimum comes off.

    Spending clearly ABOVE the minimum = CBO wants it on its own (winner signal).
    Sitting AT the minimum = it will fall away once the minimum is removed.
    """
    T, L = _r("test"), _r("launch")
    band = T["minimum_stuck_band"]
    ratio = avg_daily_spend / daily_minimum if daily_minimum else 0
    stuck = ratio <= 1 + band
    remove = days_live >= L["pack_min_days"]
    if stuck and remove and above_target:
        action, why = "KEEP_MINIMUM", ("Still only spending at the minimum but above target: the one case where the "
                                       "minimum can stay a little longer.")
    elif remove:
        action, why = "REMOVE_MINIMUM", f"{days_live} days live: remove the minimum (7 days max)."
    else:
        action, why = "WAIT", f"Day {days_live} of {L['pack_min_days']}: leave the minimum on."
    signal = "AT_MINIMUM (expect it to fade once removed)" if stuck else "ABOVE_MINIMUM (carrying itself: positive signal)"
    return {"rule": "SOP 5.4", "action": action, "signal": signal, "spend_vs_minimum": round(ratio, 2),
            "why": [f"Average ${avg_daily_spend:,.2f}/day vs minimum ${daily_minimum:,.2f}/day ({ratio:.2f}x).", why]}


def retention_budget(prospecting_daily: float, retention_daily: float) -> dict:
    """SOP 5.6: retention <= 10% of prospecting."""
    cap = _r("launch")["retention_budget_max_pct_of_prospecting"] * prospecting_daily
    ok = retention_daily <= cap
    return {"rule": "SOP 5.6", "ok": ok, "max_retention_daily": round(cap, 2),
            "why": [f"Retention ${retention_daily:,.2f} vs cap ${cap:,.2f} (10% of prospecting, 'not law'). "
                    "Manage retention by frequency, not ROAS."]}


def preflight(account: dict) -> dict:
    """SOP 4: launch preflight. Missing keys count as 'unknown' and block launch."""
    checks = [
        ("king_goal_set", "One King Goal (ROAS or CPA) is written down (SOP 3.3)."),
        ("pixel_gut_check_passed", "Pixel gut check passed this month (SOP 4.2)."),
        ("audience_segments_set", "Audience segments set: engaged = ATC 90d + visitors 30d; existing = purchasers 180d + CRM list (SOP 4.3)."),
        ("advantage_creative_test_off", "Advertiser settings: Advantage+ creative 'test new enhancements' unchecked (SOP 4.3)."),
        ("no_account_controls", "No account-level audience/placement controls unless legally required (SOP 4.3)."),
        ("purchaser_audiences_exist", "Purchasers 180d (pixel) and all-time (CRM) audiences exist for exclusions (SOP 4.3)."),
        ("hero_product_chosen", "Hero product/collection/offer chosen (80-90% of spend) (SOP 3.4)."),
        ("special_ad_category_checked", "Special ad category declared if it applies (SOP 4.3)."),
    ]
    results, blockers = [], []
    for key, text in checks:
        val = account.get(key)
        state = "pass" if val is True else ("fail" if val is False else "unknown")
        results.append({"check": key, "state": state, "requirement": text})
        if state != "pass":
            blockers.append(key)
    return {"rule": "SOP 4", "ready": not blockers, "blockers": blockers, "checks": results}


# ======================================================================
# TEST
# ======================================================================

def judgment_window(avg_daily_spend: float) -> dict:
    """SOP 7.1: minimum days before judging creative."""
    T = _r("test")
    days = (T["judgment_window_high_spend_days"] if avg_daily_spend >= T["judgment_window_spend_threshold_daily"]
            else T["judgment_window_low_spend_days"])
    return {"rule": "SOP 7.1", "days": days,
            "why": [f"${avg_daily_spend:,.0f}/day -> judge creative on {days}-day windows "
                    f"(14 days under ${T['judgment_window_spend_threshold_daily']:,}/day, 7 days at or above)."]}


def _within_kpi(kpi_type: str, target: float, actual: float, tol: float) -> bool:
    if kpi_type == "roas":
        return actual >= (1 - tol) * target
    return actual <= (1 + tol) * target  # cpa: interpretation flagged in SOP 7.3


def _hits_kpi(kpi_type: str, target: float, actual: float) -> bool:
    return actual >= target if kpi_type == "roas" else actual <= target


def pause_decision(ad: dict, ctx: dict) -> dict:
    """SOP 7.3: the 13-question pausing tree, in order.

    ad:  spend, purchases, atc, ic, cost_per_ic, kpi_actual (on the judging
         attribution), days_live, plus optional flags viral, wrong_demographic.
    ctx: kpi_type ('roas'|'cpa'), kpi_target, target_cpa, avg_cost_per_ic,
         post_event (bool), pixel_ok (bool), window_days,
         account_at_goal (bool, optional: the campaign/account is hitting the King Goal).
    ad may also carry adset_spend_share (share of campaign spend its ad set takes).
    Returns action KEEP | WAIT | PAUSE | CAP_ADSET | FIX_TRACKING.
    """
    T = _r("test")
    kt, target, cpa = ctx["kpi_type"], ctx["kpi_target"], ctx["target_cpa"]
    spend, purchases = ad.get("spend", 0.0), ad.get("purchases", 0)
    actual = ad.get("kpi_actual")
    window = ctx.get("window_days", ad.get("days_live", 0))

    def out(action, q, why):
        return {"rule": "SOP 7.3", "action": action, "question": q, "why": why}

    if actual is not None and purchases > 0 and _hits_kpi(kt, target, actual):
        return out("KEEP", 1, [f"Hitting KPI ({kt} {actual} vs target {target}). Never pause an ad that hits KPI, however old."])
    if window < T["pause_window_min_days"]:
        return out("WAIT", 2, [f"Only {window} days of data; judge on 7-14 day windows, never one bad day or a slow morning."])
    if ctx.get("post_event"):
        return out("WAIT", 4, ["Post-sale / post-holiday period: give grace, do not pause on the dip."])
    if ctx.get("pixel_ok") is False:
        return out("FIX_TRACKING", 5, ["Tracking not confirmed: run the pixel gut check before any pause."])
    if ad.get("viral") or ad.get("wrong_demographic"):
        return out("CAP_ADSET", 8 if ad.get("viral") else 9,
                   ["Viral or off-demographic spend: put a MAX % spending limit on this pack instead of pausing "
                    "(e.g. 90% of spend that deserves ~20% -> max 20%)."])
    gate = T["pause_spend_gate_cpa_multiple"] * cpa
    if spend < gate:
        return out("WAIT", 10, [f"Spent ${spend:,.2f} < 2x target CPA (${gate:,.2f}). Not enough spend to judge."])
    if purchases == 0:
        cpic, avg = ad.get("cost_per_ic"), ctx.get("avg_cost_per_ic")
        if ad.get("ic", 0) > 0 and cpic is not None and avg and cpic <= avg:
            return out("KEEP", 7, [f"0 purchases but cost per IC ${cpic:,.2f} <= average ${avg:,.2f}: leading indicator, the ad 'has legs'."])
        return out("PAUSE", 11, [f"Spent ${spend:,.2f} (>= 2x target CPA) with 0 purchases and no healthy mid-funnel signal."])
    if actual is not None and _within_kpi(kt, target, actual, T["pause_kpi_tolerance"]):
        why12 = [f"Within 50% of KPI ({kt} {actual} vs {target}): generally not worth pausing yet; re-check next cycle."]
        if window >= 2 * T["pause_window_min_days"]:
            why12.append("It has sat at this level for a while: pausing can be considered (Pausing Ads, Q12).")
        return out("KEEP", 12, why12)
    under = T["pause_underperformer_cpa_multiple"] * cpa
    if spend >= under:
        if ctx.get("account_at_goal"):
            share = ad.get("adset_spend_share", 0) or 0
            if share >= T["hog_cap_pct"]:
                return out("CAP_ADSET", 13, [
                    f"Off KPI, but the campaign is at goal and this ad set takes {share:.0%} of spend. Do NOT pause "
                    f"(pausing a top spender spikes results for 3-7 days, then drains the funnel below target). "
                    f"Set a MAX of {T['hog_cap_pct']:.0%} on the ad set and judge over {T['hog_judge_days']} days."])
            return out("KEEP", 13, [
                f"Off KPI ({kt} {actual} vs {target}) after ${spend:,.2f}, but the account is at goal: likely an "
                "assisting ad. Keep it; pause only if the account itself falls below goal (check its cost per ATC/IC first)."])
        return out("PAUSE", 13, [f"Spent ${spend:,.2f} >= 3x target CPA (${under:,.2f}) and still 50%+ off KPI ({kt} {actual} vs {target})."])
    return out("WAIT", 13, [f"50%+ off KPI but only ${spend:,.2f} spent (< 3x target CPA ${under:,.2f}). Let it reach the gate."])


def graduation(ads: list, incremental_roas_baseline: float) -> dict:
    """SOP 7.4: winners = top 10% of spenders AND incremental ROAS >= baseline."""
    T = _r("test")
    ranked = sorted(ads, key=lambda a: a.get("spend", 0), reverse=True)
    top_n = max(1, math.ceil(len(ranked) * T["graduation_top_spend_pct"]))
    top = ranked[:top_n]
    winners = [a for a in top if a.get("incremental_roas", 0) >= incremental_roas_baseline]
    return {
        "rule": "SOP 7.4",
        "top_spenders_considered": [a.get("name") for a in top],
        "winners": [a.get("name") for a in winners],
        "why": [f"Top {T['graduation_top_spend_pct']:.0%} by spend = {top_n} of {len(ranked)} ads; "
                f"winners also need incremental ROAS >= {incremental_roas_baseline}. "
                "High ROAS on low spend is noise and never graduates."],
        "next": "Duplicate winners into interest_[name]_winners packs and Retention; originals keep running. "
                "Scale campaign only for 1-3 home runs.",
    }


def breakout_winners(windows: dict, today_age_days: dict) -> dict:
    """SOP 7.5 (Claude Unlimited Ads Workflow): launched <=30d, >=10% of spend,
    ROAS > account average in at least one 7/14/30-day window.

    windows: {"7": {"account_spend": x, "account_roas": y, "ads": [{"id","name","spend","roas"}]}, ...}
    today_age_days: {ad_id: days since created}
    """
    T = _r("test")
    found: dict = {}
    for win, data in windows.items():
        acct_spend, acct_roas = data["account_spend"], data["account_roas"]
        for ad in data["ads"]:
            age = today_age_days.get(ad["id"], 10**6)
            share = ad["spend"] / acct_spend if acct_spend else 0
            if age <= T["breakout_max_age_days"] and share >= T["breakout_min_spend_share"] and ad["roas"] >= acct_roas:
                rec = found.setdefault(ad["id"], {"id": ad["id"], "name": ad.get("name"), "windows": [],
                                                  "top_spend_share": 0.0, "roas": ad["roas"], "borderline": False})
                rec["windows"].append(int(win))
                if share > rec["top_spend_share"]:
                    rec["top_spend_share"], rec["roas"] = round(share, 4), ad["roas"]
                if ad["roas"] == acct_roas:
                    rec["borderline"] = True
    return {"rule": "SOP 7.5", "winners": list(found.values()),
            "message_if_none": "No new breakout winners today."}


def shotgun_targets(cost_per_atc: float, cost_per_ic: float, cost_per_purchase: float, aov: float) -> dict:
    """SOP 7.6 (Shotgun & Sniper, high creative-volume brands only)."""
    return {
        "rule": "SOP 7.6",
        "roas": round(aov / cost_per_purchase, 2),
        "atc_to_ic_rate": round(cost_per_atc / cost_per_ic, 3),
        "ic_to_purchase_rate": round(cost_per_ic / cost_per_purchase, 3),
        "kill_switches": {"cost_per_atc": cost_per_atc, "cost_per_ic": cost_per_ic, "cost_per_purchase": cost_per_purchase},
        "why": ["Targets must come from your own account averages on the SAME attribution you judge on."],
    }


def shotgun_kill(adset: dict, targets: dict, days_live: int) -> dict:
    """Kill switch check for one Shotgun ad set (one creative)."""
    k = targets["kill_switches"]
    spend = adset["spend"]
    if spend >= k["cost_per_atc"] and adset.get("atc", 0) == 0:
        return {"action": "KILL", "why": [f"Spent ${spend:.2f} >= target cost/ATC with 0 ATC."]}
    if spend >= k["cost_per_ic"] and adset.get("ic", 0) == 0:
        return {"action": "KILL", "why": [f"Spent ${spend:.2f} >= target cost/IC with 0 IC."]}
    early = days_live < _r("test")["shotgun_gauntlet_days"]
    if not early and spend >= k["cost_per_purchase"] and adset.get("purchases", 0) == 0:
        return {"action": "KILL", "why": [f"Spent ${spend:.2f} >= target CPA with 0 purchases (CPA switch only after the early days)."]}
    if days_live >= _r("test")["shotgun_gauntlet_days"]:
        return {"action": "SCALE", "why": ["Survived the 7-day gauntlet: switch campaign ABO->CBO, or +25%/day while targets hold."]}
    return {"action": "KEEP", "why": ["Inside kill switches; keep checking daily."]}


def zombie_check(adsets: list) -> dict:
    """SOP 7.7: pick ad sets / ads for the zombie (bid-cap) campaign.

    adsets: [{name, avg_daily_spend_7d, minimum_active (bool), top_ad_spend_share,
              top_ad_hits_kpi (bool)}]. Moving an ad resets its learning; that reset is the point.
    """
    T = _r("test")
    duds, move_top_ad = [], []
    for a in adsets:
        if a.get("minimum_active"):
            continue
        if a.get("avg_daily_spend_7d", 0) <= T["zombie_dud_daily_spend_max"]:
            duds.append(a["name"])
        elif (a.get("top_ad_spend_share", 0) >= 0.9) and a.get("top_ad_hits_kpi") is False:
            move_top_ad.append(a["name"])
    return {"rule": "SOP 7.7", "dud_adsets": duds, "move_top_ad_from": move_top_ad,
            "why": [f"Duds = ad sets drawing <= ${T['zombie_dud_daily_spend_max']:.0f}/day after minimums end: move one ad "
                    "(via post ID) to the zombie campaign and pause the rest of the ad set.",
                    "An ad eating ~90% of its ad set while missing target: move that ad to the zombie so the other ads get a turn.",
                    "Never move ads between live ad sets otherwise: it loses learnings."]}


# ======================================================================
# OPTIMIZE
# ======================================================================

def frequency_check(audience: str, window_days: int, frequency: float, above_target: bool | None = None) -> dict:
    """SOP 8.2: frequency ceilings by audience and window."""
    O = _r("optimize")
    band = O["frequency"][audience][str(window_days)]
    lo, hi = band
    if hi is not None and frequency > hi:
        status = "over"
    elif lo is not None and frequency < lo:
        status = "under"
    else:
        status = "ok"
    why = [f"{audience} {window_days}d frequency {frequency} vs band {lo or '-'}-{hi}."]
    action = "none"
    if audience == "retargeting" and window_days == 30 and frequency > 15:
        action = f"cut budget ~{O['retargeting_over_freq_budget_cut']:.0%} even if above target; move cash to prospecting"
    elif audience == "retargeting" and status == "under":
        action = "probably spend more on retargeting"
    elif audience == "prospecting" and window_days == 7 and frequency >= O["prospecting_freq_dig_in_7d"]:
        action = "dig in even if above target: expand (new concepts, interest packs)"
    elif audience == "existing" and status == "over":
        action = "lower retention budget or add a daily max on the over-served ad set"
    elif status == "over":
        action = "reduce spend on this audience / expand reach"
    return {"rule": "SOP 8.2", "status": status, "action": action, "why": why}


def pixel_check(browser_purchases: int, server_purchases: int, store_orders: int, emq: float | None = None) -> dict:
    """SOP 4.2: monthly pixel gut check."""
    O = _r("optimize")
    issues = []
    base = max(browser_purchases, server_purchases) or 1
    gap = abs(browser_purchases - server_purchases) / base
    if gap > O["pixel_browser_server_max_gap"]:
        issues.append(f"browser vs server gap {gap:.1%} > 10%")
    vs = abs(server_purchases - store_orders) / (store_orders or 1)
    if vs > O["pixel_server_vs_orders_max_gap"]:
        over = server_purchases > store_orders
        issues.append(f"server purchases vs store orders off by {vs:.1%} ({'OVER-counting: worse' if over else 'under-counting'})")
    if emq is not None and emq < O["emq_good"]:
        issues.append(f"EMQ {emq} < {O['emq_good']} (benchmark {O['emq_benchmark']})")
    return {"rule": "SOP 4.2", "ok": not issues, "issues": issues,
            "next": "Hire a real developer (not a quick reinstall) if any issue persists."}


def learning_phase_check(share_in_learning_7d: float) -> dict:
    """SOP 8.6: % of spend in learning (account overview, last 7 days)."""
    O = _r("optimize")
    if share_in_learning_7d >= O["learning_phase_too_much"]:
        st, msg = "too_many_changes", "Constantly 85-90% in learning = you are changing too much. Stop editing; let it settle."
    elif share_in_learning_7d <= O["learning_phase_healthy_max"]:
        st, msg = "healthy", "Healthy (the course example: ~11%)."
    else:
        st, msg = "watch", "Between healthy and too-much: fine after a rebuild, otherwise slow down changes."
    return {"rule": "SOP 8.6", "status": st, "why": [msg]}


def anomalies(daily: list, metrics: list | None = None, threshold: float | None = None) -> dict:
    """SOP 8.1: anomaly detector over the six comparison windows.

    daily: list of {date, spend, revenue, purchases, clicks, impressions, reach?} oldest->newest,
    at least 31 days for the 30-day comparisons.
    """
    thr = threshold if threshold is not None else _r("optimize")["anomaly_threshold"]
    metrics = metrics or ["spend", "roas", "cpa", "cpc", "ctr", "cpm"]

    def agg(rows):
        s = sum(r.get("spend", 0) for r in rows)
        rev = sum(r.get("revenue", 0) for r in rows)
        p = sum(r.get("purchases", 0) for r in rows)
        c = sum(r.get("clicks", 0) for r in rows)
        i = sum(r.get("impressions", 0) for r in rows)
        n = len(rows) or 1
        return {"spend": s / n, "roas": rev / s if s else None, "cpa": s / p if p else None,
                "cpc": s / c if c else None, "ctr": c / i if i else None, "cpm": 1000 * s / i if i else None}

    d = daily
    comps = {}
    if len(d) >= 2:
        comps["yesterday_vs_day_before"] = (d[-1:], d[-2:-1])
    if len(d) >= 6:
        comps["last3_vs_prior3"] = (d[-3:], d[-6:-3])
    if len(d) >= 14:
        comps["last7_vs_prior7"] = (d[-7:], d[-14:-7])
    if len(d) >= 31:
        base30 = d[-31:-1]
        comps["yesterday_vs_30d_avg"] = (d[-1:], base30)
        comps["last3_vs_30d_avg"] = (d[-3:], d[-33:-3] if len(d) >= 33 else base30)
        comps["last7_vs_30d_avg"] = (d[-7:], d[-37:-7] if len(d) >= 37 else base30)
    flags = []
    for name, (cur, base) in comps.items():
        a, b = agg(cur), agg(base)
        for m in metrics:
            if a[m] is None or not b[m]:
                continue
            change = (a[m] - b[m]) / b[m]
            if abs(change) >= thr:
                flags.append({"window": name, "metric": m, "current": round(a[m], 4),
                              "baseline": round(b[m], 4), "change": round(change, 4)})
    primary = [f for f in flags if f["metric"] in ("spend", "roas", "cpa")]
    secondary = [f for f in flags if f["metric"] in ("cpc", "ctr", "cpm")]
    hint = None
    if primary and not secondary:
        hint = "Primary metrics moved while CPC/CTR/CPM are flat: look for a structural cause (sale ended, budget shift, tracking) before touching creative."
    return {"rule": "SOP 8.1", "threshold": thr, "flags": flags, "hint": hint}


def drop_diagnosis(prev: dict, curr: dict) -> dict:
    """SOP 8.3: find the first funnel stage where costs broke.

    prev/curr: {cpm, cpc, cost_per_atc, cost_per_ic, cpa} for equal periods.
    """
    thr = _r("optimize")["drop_definition_pct"]
    order = ["cpm", "cpc", "cost_per_atc", "cost_per_ic", "cpa"]
    where = {
        "cpm": "auction / audience: check placements, frequency, seasonality",
        "cpc": "creative: hooks and thumb-stop; new concepts",
        "cost_per_atc": "landing page / offer / price shown before the offer",
        "cost_per_ic": "cart -> checkout: button, upsell, shipping threshold, emails",
        "cpa": "checkout -> purchase: payment, shipping cost shock, trust",
    }
    changes = {}
    first = None
    for m in order:
        if prev.get(m) and curr.get(m) is not None:
            ch = (curr[m] - prev[m]) / prev[m]
            changes[m] = round(ch, 4)
            if first is None and ch >= thr:
                first = m
    return {"rule": "SOP 8.3", "first_break": first, "look_at": where.get(first),
            "changes": changes,
            "next": "Then check where spend moved: ad-level spend share period over period, and age/gender/placement/country breakdowns."}


def cost_cap_action(tcpa_hit: bool, budget_fully_spent: bool, current_cap: float, target_cpa: float,
                    monthly_spend: float, budget_utilisation: float | None = None) -> dict:
    """SOP 9.4: cost-cap decision matrix.

    budget_utilisation (optional, 0-1): share of the daily budget the capped
    campaign actually spends. ~80% is the healthy target.
    """
    O = _r("optimize")
    if monthly_spend < O["cost_cap_min_monthly_spend"]:
        return {"rule": "SOP 9.4", "action": "DONT_USE_CAPS",
                "why": [f"${monthly_spend:,.0f}/mo is below ~${O['cost_cap_min_monthly_spend']:,}/mo: cost caps are very unlikely to work. Use Highest volume."]}
    if budget_utilisation is not None and tcpa_hit:
        u = budget_utilisation
        if u >= O["cost_cap_too_loose"]:
            budget_fully_spent = True
        elif O["cost_cap_starved"] < u < O["cost_cap_too_loose"]:
            return {"rule": "SOP 9.4", "action": "WORKING", "new_cap": current_cap,
                    "why": [f"Spending {u:.0%} of budget while hitting the cap: around 80% is exactly where a cost cap should sit. "
                            "It is protecting you; do not tweak it to force spend."]}
        else:
            return {"rule": "SOP 9.4", "action": "RECHECK_INPUTS", "new_cap": current_cap,
                    "why": [f"Spending only {u:.0%} of budget day after day: check whether AOV, LTV or the real target CPA changed "
                            "before touching the cap; otherwise make creative."]}
    if tcpa_hit and budget_fully_spent:
        return {"rule": "SOP 9.4", "action": "RAISE_BUDGET", "new_cap": current_cap,
                "why": ["Cap hit and budget fully spent: raise budget (keep cap) until it no longer spends in full. Optionally lower cap $1-2, never $10."]}
    if tcpa_hit and not budget_fully_spent:
        if current_cap < target_cpa:
            return {"rule": "SOP 9.4", "action": "RAISE_CAP_1", "new_cap": min(current_cap + O["cost_cap_step"], target_cpa),
                    "why": ["Cap is below real target CPA: raise it $1 at a time, holding a few days per step."]}
        return {"rule": "SOP 9.4", "action": "MAKE_CREATIVE", "new_cap": current_cap,
                "why": ["Working as intended (restricting). Do not raise cap above target; make/iterate creative."]}
    if not tcpa_hit and budget_fully_spent:
        return {"rule": "SOP 9.4", "action": "ITERATE_CREATIVE", "new_cap": min(current_cap, target_cpa),
                "why": ["Spending in full but missing CPA: question whether caps fit; iterate existing creative (long-tail signal). Cap never above target CPA."]}
    return {"rule": "SOP 9.4", "action": "MAKE_NEW_CREATIVE_OR_STOP_CAPS", "new_cap": min(current_cap, target_cpa),
            "why": ["Missing CPA AND under-spending ('double bad'): probably stop cost caps; if kept, cap never above target CPA; make new creative."]}


def engaged_share_check(new_spend: float, engaged_spend: float, existing_spend: float,
                        existing_freq_7d: float | None = None, daily_budget: float | None = None) -> dict:
    """SOP 5.7 / 8.4: should Retargeting or Retention be broken out?

    Bands (live calls): <10% starved, 10-25% healthy, 25-45% watch, 45%+ act.
    """
    O = _r("optimize")
    total = new_spend + engaged_spend + existing_spend or 1
    eng = engaged_spend / total
    recs = []
    if eng >= O["engaged_share_act"]:
        status = "ACT"
        recs.append(f"Engaged {eng:.0%} of prospecting spend (mid-40s or more): break out Retargeting and exclude those "
                    "audiences from Prospecting, or raise budget so Meta has to reach new people.")
    elif eng > O["engaged_share_normal_upper"]:
        status = "WATCH"
        recs.append(f"Engaged {eng:.0%} (>25%): watch it. Meta spends on engaged first, and the share rises when budget is cut. "
                    "Adding creative will not fix it; more spend will.")
        if daily_budget is not None and daily_budget < 500:
            recs.append(f"At ${daily_budget:,.0f}/day a breakout saves only a few dollars: usually not worth it yet.")
    elif eng < O["engaged_share_floor"]:
        status = "STARVED"
        recs.append(f"Engaged only {eng:.0%} (<10% bare minimum): check the advertiser-settings segments and exclusions; "
                    "validate with a $5/day retargeting campaign on the same lists. If truly starved, break out Retargeting.")
    else:
        status = "HEALTHY"
        recs.append(f"Engaged {eng:.0%}: within the normal 10-25% range; keep retargeting merged in Prospecting.")
    if existing_freq_7d is not None and existing_freq_7d > O["frequency"]["existing"]["7"][1]:
        recs.append(f"Existing-customer 7d frequency {existing_freq_7d} > 4: break out / tighten Retention.")
    return {"rule": "SOP 5.7", "status": status,
            "shares": {"new": round(new_spend / total, 3), "engaged": round(eng, 3),
                       "existing": round(existing_spend / total, 3)}, "recommendations": recs}


def funnel_health(atc: float, ic: float, purchases: float, sessions: float | None = None,
                  aov: float | None = None) -> dict:
    """SOP 8.3: where does the funnel leak? Expect ~50% drop per step."""
    O = _r("optimize")
    steps = {"atc_to_ic": ic / atc if atc else None, "ic_to_purchase": purchases / ic if ic else None}
    flags = [k for k, v in steps.items() if v is not None and v < O["funnel_step_flag"]]
    why = [f"ATC->IC {steps['atc_to_ic']:.0%}" if steps["atc_to_ic"] is not None else "ATC->IC n/a",
           f"IC->purchase {steps['ic_to_purchase']:.0%}" if steps["ic_to_purchase"] is not None else "IC->purchase n/a",
           "Expect roughly 50% per step (100 purchases ~ 200 IC ~ 400 ATC; use unique ATC for multi-item carts)."]
    out = {"rule": "SOP 8.3", "step_rates": {k: (round(v, 3) if v is not None else None) for k, v in steps.items()},
           "leaking_steps": flags, "why": why}
    if sessions:
        cvr = purchases / sessions
        out["site_cvr"] = round(cvr, 4)
        lo, hi = O["site_cvr_benchmark"]
        if aov is not None and aov <= 150 and cvr < lo:
            out["why"].append(f"Site CVR {cvr:.2%} is under ~{lo:.1%}-{hi:.1%} for a ~${aov:,.0f} AOV: the site/offer is part of the problem.")
    if "ic_to_purchase" in flags:
        out["why"].append("Break at purchase: remake the ad with a clearer CTA/offer and check checkout, price and shipping before judging the concept.")
    if "atc_to_ic" in flags:
        out["why"].append("Break at checkout start: check cart, shipping reveal and site changes (e.g. a removed collection).")
    return out


def scale_funnel_check(prev: dict, curr: dict) -> dict:
    """SOP 9.1: after a budget jump, are the early funnel costs holding?

    prev/curr: {cost_per_atc, cost_per_ic}. +3-15% is normal; ~doubling = stop.
    """
    O = _r("optimize")
    res, worst = {}, 0.0
    for k in ("cost_per_atc", "cost_per_ic"):
        if prev.get(k) and curr.get(k):
            ch = curr[k] / prev[k] - 1
            res[k] = round(ch, 3)
            worst = max(worst, ch)
    if worst >= O["scale_cost_rise_concern"]:
        verdict, why = "CONCERN", "Early funnel costs jumped sharply after the increase: stop raising and hold/step back."
    elif worst > O["scale_cost_rise_normal"]:
        verdict, why = "WATCH", "Costs up more than the normal 3-15%: hold the budget and give conversions time to catch up."
    else:
        verdict, why = "NORMAL", "Within the normal 3-15% wobble: conversion rate lags, keep going."
    return {"rule": "SOP 9.1", "verdict": verdict, "changes": res, "why": [why,
            "Judge scale moves on incremental attribution; new spend reaches people with a longer path to purchase."]}


def pareto_cut(revenue_by_item: dict, keep_share: float | None = None) -> dict:
    """SOP 8.5 / 3.4: keep the items (countries, products, categories) that make ~80% of revenue."""
    share = keep_share if keep_share is not None else _r("optimize")["pareto_keep_share"]
    total = sum(revenue_by_item.values()) or 1
    keep, run = [], 0.0
    for k, v in sorted(revenue_by_item.items(), key=lambda kv: kv[1], reverse=True):
        if run / total >= share:
            break
        keep.append(k)
        run += v
    cut = [k for k in revenue_by_item if k not in keep]
    return {"rule": "SOP 8.5", "keep": keep, "cut": cut, "kept_share": round(run / total, 3),
            "why": [f"{len(keep)} of {len(revenue_by_item)} items drive {run / total:.0%} of revenue: focus there, relaunch smaller, "
                    "and add the rest back once those are clear."]}


def placement_check(spend_by_placement: dict) -> dict:
    """SOP 8.5: top 6 placements by spend must be FB/IG Feed, Stories, Reels."""
    O = _r("optimize")
    total = sum(spend_by_placement.values()) or 1
    ranked = sorted(spend_by_placement.items(), key=lambda kv: kv[1], reverse=True)
    top6 = [k for k, _ in ranked[:6]]
    missing = [p for p in O["core_placements"] if p not in top6]
    low = [p for p in O["core_placements"] if spend_by_placement.get(p, 0) / total <= O["placement_red_flag_share"]]
    return {"rule": "SOP 8.5", "top6": top6, "core_missing_from_top6": missing, "core_at_or_below_1pct": low,
            "next": "Missing core placement = usually missing creative for it (vertical 9:16 for Reels/Stories). "
                    "Fix creative first; test exclusions only in ONE new ad set; never edit live ad set placements."}


def geo_check(cpp_by_country: dict, account_cpp: float) -> dict:
    """SOP 8.5: countries far above the account CPP get removed from the ad set."""
    mult = _r("optimize")["geo_cut_cpp_multiple"]
    cut = [c for c, v in cpp_by_country.items() if v >= mult * account_cpp]
    return {"rule": "SOP 8.5", "cut": cut, "keep": [c for c in cpp_by_country if c not in cut],
            "why": [f"Cut countries at >= {mult}x the account cost per purchase (${account_cpp:,.2f}); small fluctuations stay."]}


def value_rule_effect(revenue: float, spend: float, adjustment: float) -> dict:
    """SOP 8.5: how a value rule changes what Meta 'sees'."""
    O = _r("optimize")
    perceived = revenue * (1 + adjustment)
    warn = []
    if abs(adjustment) > O["value_rule_max"]:
        warn.append("Over 50% gets out of control.")
    return {"rule": "SOP 8.5", "perceived_revenue": round(perceived, 2),
            "perceived_roas": round(perceived / spend, 3) if spend else None,
            "actual_roas": round(revenue / spend, 3) if spend else None,
            "warnings": warn,
            "why": [f"Start around {O['value_rule_start']:.0%} (30-50% sweet spot); don't act on 5-10% gaps."]}


def dow_budgets(base_daily: float, up_days: list, up_pct: float) -> dict:
    """SOP 8.7: day-of-week budget shift that keeps weekly spend flat."""
    n_up = len(up_days)
    n_down = 7 - n_up
    if n_down == 0:
        raise ValueError("at least one day must stay at or below base")
    high = base_daily * (1 + up_pct)
    low = (base_daily * 7 - high * n_up) / n_down
    return {"rule": "SOP 8.7", "high_day_budget": round(high, 2), "low_day_budget": round(low, 2),
            "down_pct": round(low / base_daily - 1, 6), "weekly_total": round(high * n_up + low * n_down, 2),
            "why": ["+X% and -X% are not symmetric: the down-step is solved so the week totals base x 7."]}


# ======================================================================
# SCALE
# ======================================================================

def vertical_scale(ctx: dict) -> dict:
    """SOP 9.1: vertical scaling decision for the prospecting CBO.

    ctx: kpi_type, kpi_target, daily_budget, hours_since_last_change,
         kpi_by_window {"14":x, "7":x, "3":x, "1":x} (King Goal metric, multi-day),
         new_incremental_kpi (optional; New-segment incremental ROAS/CPA),
         revenue_7d_daily_avg (optional; for the smashing delta check),
         prior_proven_daily (optional; a spend level this account sustained before a pause/rebuild),
         incremental_kpi_7d (optional; 7-day incremental-attribution KPI, required for the relaunch path).
    """
    S = _r("scale")
    kt, target, budget = ctx["kpi_type"], ctx["kpi_target"], ctx["daily_budget"]
    w = {str(k): v for k, v in ctx["kpi_by_window"].items()}
    why = []

    def ratio(v):  # >1 means better than target
        return v / target if kt == "roas" else target / v

    def better(v):
        return v is not None and _hits_kpi(kt, target, v)

    if not (better(w.get("14")) and better(w.get("7"))):
        return {"rule": "SOP 9.1", "action": "HOLD", "new_daily_budget": budget,
                "why": [f"14d {w.get('14')} / 7d {w.get('7')} not both at or above target {target}. "
                        "Below target: hold budget and fix creative (twin engine keeps creative on)."]}
    if not better(w.get("3")):
        return {"rule": "SOP 9.1", "action": "HOLD", "new_daily_budget": budget,
                "why": ["14d and 7d above target but last 3 days are not: wait for stability. Never decide off yesterday."]}

    prior, inc7 = ctx.get("prior_proven_daily"), ctx.get("incremental_kpi_7d")
    if prior and budget < prior:
        if inc7 is None:
            why.append("Relaunching toward a proven spend: pull incremental attribution before using the faster path.")
        elif better(inc7):
            if budget < S["relaunch_double_until_daily"]:
                new = min(2 * budget, prior)
                label = "doubling"
            else:
                new = min(budget + S["relaunch_step_after_daily"], prior)
                label = f"+${S['relaunch_step_after_daily']:,}"
            return {"rule": "SOP 9.1", "action": "DOUBLE" if label == "doubling" else "INCREASE",
                    "new_daily_budget": round(new, 2),
                    "why": [f"Relaunching toward a previously proven ${prior:,.0f}/day with incremental {inc7} at or above target: "
                            f"{label} is allowed. Judge only on incremental attribution and watch cost per ATC/IC "
                            "(+3-15% normal, doubling = stop)."]}
        else:
            why.append(f"Incremental {inc7} is below target: no fast relaunch path; normal steps only.")

    smashing = ratio(w["7"]) >= S["smashing_multiple"] and ratio(w["3"]) >= S["smashing_multiple"]
    if smashing and kt == "roas" and ctx.get("revenue_7d_daily_avg"):
        new = 2 * budget
        worst = ctx["revenue_7d_daily_avg"] / new
        if worst >= target:
            return {"rule": "SOP 9.1", "action": "DOUBLE", "new_daily_budget": round(new, 2),
                    "why": [f"Smashing: 7d/3d >= 2x target. Delta check: current revenue ${ctx['revenue_7d_daily_avg']:,.0f}/day "
                            f"/ new spend ${new:,.0f} = {worst:.2f} >= target {target} even if the new money converts nothing."]}
        why.append(f"Smashing but delta check fails ({worst:.2f} < {target}); using the normal step instead.")

    if ctx.get("hours_since_last_change", 999) < S["min_hours_between_moves"] and not smashing:
        return {"rule": "SOP 9.1", "action": "WAIT", "new_daily_budget": budget,
                "why": [f"Last move {ctx['hours_since_last_change']}h ago; moves are every 48-72h unless smashing."]}

    if budget >= S["large_spend_daily"]:
        lo, hi = S["step_large_spend"]
    elif budget <= S["small_spend_daily"]:
        lo, hi = S["step_default"][0], S["step_small_spend_max"]
    else:
        lo, hi = S["step_default"]
    excess = min(max(ratio(w["7"]) - 1, 0), 1)  # 0 at target, 1 at 2x target
    step = lo + (hi - lo) * excess
    inc = ctx.get("new_incremental_kpi")
    if inc is not None and not better(inc):
        step = lo
        why.append(f"New-segment incremental {inc} is below target: allowed, but use the smallest step and expect about that return.")
    elif inc is not None:
        why.append(f"New-segment incremental {inc} is at or above target: push with confidence.")
    new = budget * (1 + step)
    why.insert(0, f"Above target on 14/7/3-day windows (7d {w['7']} vs {target}). Step {step:.0%} "
                  f"(band {lo:.0%}-{hi:.0%} for ${budget:,.0f}/day, scaled by how far above goal).")
    why.append("Expect frequency, CPM and CPC up and ROAS down short-term; hold if cost per ATC stays flat.")
    return {"rule": "SOP 9.1", "action": "INCREASE", "step_pct": round(step, 4), "new_daily_budget": round(new, 2), "why": why}


def horizontal_readiness(daily_spend: float, reason: str | None) -> dict:
    """SOP 9.2: is an external (new-campaign) horizontal move allowed?"""
    S = _r("scale")
    allowed = {"sale", "margin_tier", "scale_campaign"}
    if daily_spend <= S["horizontal_not_ready_daily"]:
        return {"rule": "SOP 9.2", "allowed": False,
                "why": [f"${daily_spend:,.0f}/day: not ready for external horizontal scaling. Raise the prospecting CBO instead."]}
    if reason not in allowed:
        return {"rule": "SOP 9.2", "allowed": False,
                "why": ["Only three reasons justify a new campaign: a sale/drop, a huge margin/price tier, or a 1-3 ad scale campaign. "
                        "A copy of the CBO with the same ads is NOT horizontal scaling."]}
    note = " Be careful: protect the main CBO." if daily_spend <= S["horizontal_careful_daily"] else ""
    return {"rule": "SOP 9.2", "allowed": True, "why": [f"Reason '{reason}' is valid.{note}"]}


# ======================================================================
# PROFIT
# ======================================================================

def profit_model(orders: float, aov: float, cogs_pct: float, fixed_costs: float, take_pct: float = 0.0,
                 ltv_12m: float | None = None) -> dict:
    """SOP 3.2: break-even / take model (Setup: Profit Tracking)."""
    revenue = orders * aov
    cogs = revenue * cogs_pct
    ad_spend = revenue - cogs - fixed_costs - take_pct * revenue
    out = {
        "rule": "SOP 3.2",
        "revenue": round(revenue, 2),
        "ad_spend_budget": round(ad_spend, 2),
        "ad_spend_pct_of_revenue": round(ad_spend / revenue, 4) if revenue else None,
        "breakeven_roas_blended": round(revenue / ad_spend, 2) if ad_spend > 0 else None,
        "breakeven_cpa": round(ad_spend / orders, 2) if orders else None,
        "profit": round(take_pct * revenue, 2),
    }
    if ltv_12m:
        out["ltv_multiple"] = round(ltv_12m / aov, 2)
        out["gravy_12m_revenue"] = round(orders * (ltv_12m - aov), 2)
        out["gravy_12m_profit"] = round(orders * (ltv_12m - aov) * (1 - cogs_pct), 2)
    if ad_spend <= 0:
        out["warning"] = "Costs exceed revenue before ads: fix price/COGS/fixed costs first."
    return out


def target_roas(breakeven_roas: float, take_home: float | None = None) -> dict:
    """SOP 3.3: target = break-even + take-home margin (2.0 -> 2.2 at 10%)."""
    t = take_home if take_home is not None else _r("profit")["target_over_breakeven_default"]
    return {"rule": "SOP 3.3", "target_roas": round(breakeven_roas * (1 + t), 2),
            "why": [f"Break-even {breakeven_roas} + {t:.0%} take-home. 10-20% over break-even is a healthy spot."]}



def pacing(spend_target: float, spend_mtd: float, revenue_target: float, revenue_mtd: float,
           days_remaining: int) -> dict:
    """SOP 3.5: month pacing (Ads Tracking Template, tracker tab)."""
    d = max(days_remaining, 1)
    spend_left, rev_left = spend_target - spend_mtd, revenue_target - revenue_mtd
    roas_needed = rev_left / spend_left if spend_left > 0 else None
    return {"rule": "SOP 3.5",
            "daily_spend_to_hit_goal": round(spend_left / d, 2),
            "daily_revenue_to_hit_goal": round(rev_left / d, 2),
            "roas_to_hit_goal": round(roas_needed, 2) if roas_needed is not None else None,
            "why": [f"(${spend_target:,.0f} - ${spend_mtd:,.0f}) / {d} days = ${spend_left / d:,.2f}/day to spend.",
                    f"(${revenue_target:,.0f} - ${revenue_mtd:,.0f}) / {d} days = ${rev_left / d:,.2f}/day of revenue.",
                    "ROAS to hit goal = revenue remaining / spend remaining."
                    + (" Spend target already reached." if spend_left <= 0 else "")]}


def reverse_target(value_per_sale: float, conversion_rate: float, label: str = "lead") -> dict:
    """SOP 10 / 3.3: work a target backwards (cost per call, lead, trial).

    Target cost per <label> = value per sale x the share of <label>s that become a sale.
    Use contribution after delivery costs as value_per_sale to break even.
    """
    t = value_per_sale * conversion_rate
    return {"rule": "SOP 10", f"target_cost_per_{label}": round(t, 2),
            "why": [f"${value_per_sale:,.2f} per sale x {conversion_rate:.0%} of {label}s closing = ${t:,.2f} per {label} to break even.",
                    "Compare against cost per QUALIFIED " + label + ", never raw volume; national vs local CPL is not comparable."]}
