#!/usr/bin/env python3
"""a2.py - the Andromeda 2 media-buying calculator and Ads Manager analyzer.

Deterministic maths for the andromeda2-* skills, so budgets, thresholds and verdicts are
computed the same way every time instead of being estimated in prose.

Subcommands
  economics      break-even ROAS/CPA and targets from unit economics
  testing-plan   creative volume per week, new-pack minimums, kill thresholds
  analyze        read an Ads Manager CSV export: metrics, diagnosis and a verdict per ad
  scale          next daily budget for a campaign from its recent ROAS/CPA (vertical scaling)
  cost-controls  cost cap / ROAS goal / bid cap setup values and budgets (hard scaling)
  cap-diagnose   the 4-scenario diagnosis for a capped campaign (budget, cap or creative?)
  zombie         zombie-campaign plan from a long-range ad-level CSV: buckets, bid cap, starting budget

Every rule is a practitioner heuristic from the source courses (see the skills' references),
not Meta documentation. The account's own baseline beats any generic number.

Stdlib only. Python 3.9+. Run `python3 a2.py <subcommand> -h` for the options.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import statistics
import sys
from dataclasses import dataclass, field, asdict
from typing import Iterable

# ----------------------------------------------------------------------------------------------
# Shared helpers
# ----------------------------------------------------------------------------------------------


def money(x: float | None) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "-"
    return f"${x:,.2f}"


def pct(x: float | None, digits: int = 1) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "-"
    return f"{x * 100:.{digits}f}%"


def num(x: float | None, digits: int = 2) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "-"
    return f"{x:,.{digits}f}"


def safe_div(a: float | None, b: float | None) -> float | None:
    if a is None or b is None or b == 0:
        return None
    return a / b


def die(msg: str) -> None:
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(2)


def emit(payload: dict, text: str, as_json: bool) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, default=str))
    else:
        print(text.rstrip() + "\n")


# ----------------------------------------------------------------------------------------------
# economics
# ----------------------------------------------------------------------------------------------


@dataclass
class Economics:
    aov: float
    variable_cost_per_order: float
    contribution_before_ads: float
    margin_before_ads: float
    break_even_cpa: float
    break_even_roas: float
    target_roas: float
    target_cpa: float
    notes: list[str] = field(default_factory=list)


def compute_economics(aov: float, cogs_pct: float = 0.0, cogs: float = 0.0, shipping: float = 0.0,
                      fees_pct: float = 0.0, other_per_order: float = 0.0, profit_pct: float | None = None,
                      buffer: float = 1.10, ltv_multiple: float = 1.0) -> Economics:
    """Break-even and target ROAS/CPA for a first purchase.

    contribution before ads = AOV - COGS - shipping - payment fees - other per-order costs
    break-even CPA = contribution (x ltv_multiple when you knowingly buy customers on LTV)
    break-even ROAS = AOV / break-even CPA
    target ROAS = break-even ROAS x buffer (default 1.10, the "break-even x 1.1" rule), or the ROAS that
    leaves profit_pct of revenue as profit when profit_pct is given.
    """
    if aov <= 0:
        die("--aov must be positive")
    cogs_total = cogs + aov * cogs_pct / 100.0
    fees = aov * fees_pct / 100.0
    var = cogs_total + shipping + fees + other_per_order
    contrib = aov - var
    notes: list[str] = []
    if contrib <= 0:
        die(f"variable costs ({money(var)}) eat the whole AOV ({money(aov)}): no ROAS is profitable. Fix price/AOV/COGS first.")
    be_cpa = contrib * ltv_multiple
    be_roas = aov / be_cpa
    if profit_pct is not None:
        # profit = AOV - var - CPA  >= profit_pct * AOV  ->  CPA <= contrib - profit_pct*AOV
        cpa_t = contrib * ltv_multiple - aov * profit_pct / 100.0
        if cpa_t <= 0:
            die(f"a {profit_pct}% profit target leaves no room for ad spend at this AOV/margin")
        t_cpa, t_roas = cpa_t, aov / cpa_t
        notes.append(f"targets leave {profit_pct}% of revenue as profit")
    else:
        t_roas = be_roas * buffer
        t_cpa = aov / t_roas
        notes.append(f"targets = break-even x {buffer:.2f} (safety buffer)")
    if ltv_multiple != 1.0:
        notes.append(f"break-even uses an LTV multiple of {ltv_multiple}: you are buying customers below first-order profit on purpose")
    if contrib / aov < 0.5:
        notes.append("contribution margin under 50% of AOV: scaling on Meta will be hard; raise AOV (bundles, order bumps) before pushing spend")
    return Economics(aov, var, contrib, contrib / aov, be_cpa, be_roas, t_roas, t_cpa, notes)


def cmd_economics(a: argparse.Namespace) -> None:
    e = compute_economics(a.aov, a.cogs_pct, a.cogs, a.shipping, a.fees_pct, a.other, a.profit_pct, a.buffer, a.ltv_multiple)
    text = f"""## Unit economics
| Item | Value |
|---|---|
| AOV | {money(e.aov)} |
| Variable cost per order | {money(e.variable_cost_per_order)} |
| Contribution before ads | {money(e.contribution_before_ads)} ({pct(e.margin_before_ads)} of AOV) |
| **Break-even CPA** | **{money(e.break_even_cpa)}** |
| **Break-even ROAS** | **{num(e.break_even_roas)}** |
| **Target CPA (King goal)** | **{money(e.target_cpa)}** |
| **Target ROAS (King goal)** | **{num(e.target_roas)}** |

Notes: {'; '.join(e.notes)}.
Judge the King goal on blended numbers (Shopify revenue / total ad spend = MER) and use Meta-reported ROAS as the proxy.
"""
    emit(asdict(e), text, a.json)


# ----------------------------------------------------------------------------------------------
# testing-plan
# ----------------------------------------------------------------------------------------------


def creative_volume(monthly_spend: float) -> dict:
    """1 new ad per week per $10k monthly spend, rounded up, floor 2; proven-vs-new mix by spend tier."""
    per_week = max(2, math.ceil(monthly_spend / 10_000))
    if monthly_spend < 5_000:
        proven = 0.0
    elif monthly_spend < 25_000:
        proven = 0.15
    elif monthly_spend < 75_000:
        proven = 0.35
    elif monthly_spend < 150_000:
        proven = 0.50
    elif monthly_spend < 200_000:
        proven = 0.65
    else:
        proven = 0.80
    iterations = round(per_week * proven)
    return {"new_ads_per_week": per_week, "iteration_share": proven, "iterations_per_week": iterations,
            "new_concepts_per_week": per_week - iterations}


def pack_minimum(target_cpa: float, campaign_budget: float, new_packs: int) -> dict:
    """Each new pack: 1x target CPA per day for 7 days, all live minimums together <= 20% of the campaign budget."""
    cap_total = 0.20 * campaign_budget
    per_pack = min(target_cpa, cap_total / max(new_packs, 1))
    return {"per_pack_daily_minimum": round(per_pack, 2), "packs": new_packs, "total_minimums": round(per_pack * new_packs, 2),
            "cap_20pct": round(cap_total, 2), "capped": per_pack < target_cpa, "days": 7}


def cmd_testing_plan(a: argparse.Namespace) -> None:
    monthly = a.monthly_spend if a.monthly_spend else a.campaign_budget * 30.4
    vol = creative_volume(monthly)
    mins = pack_minimum(a.target_cpa, a.campaign_budget, a.new_packs)
    use_minimums = a.campaign_budget >= 150 or a.force_minimums
    min_line = (f"{money(mins['per_pack_daily_minimum'])}/day per new pack for 7 days, then remove it"
                + (" (capped by the 20% rule)" if mins["capped"] else " (= 1x target CPA)")) if use_minimums else \
        "skip minimums at this budget: one ad set per round, let CBO pick (judge weekly)"
    text = f"""## Testing plan
Campaign budget {money(a.campaign_budget)}/day, monthly spend ~{money(monthly)}, target CPA {money(a.target_cpa)}.

| Lever | Rule | Value |
|---|---|---|
| New ads per week | 1 per $10k monthly spend, floor 2, round up | **{vol['new_ads_per_week']}** |
| Iterations of proven concepts | share by spend tier | {pct(vol['iteration_share'], 0)} -> {vol['iterations_per_week']}/week |
| New concepts | the rest | {vol['new_concepts_per_week']}/week |
| Ads per pack (ad set) | 4-8 sweet spot, 2 min, 12 max | group by avatar, then concept |
| New-pack minimum | 1x CPA/day, all minimums <= 20% of budget, 7 days only | {min_line} |
| Total live minimums | <= {money(mins['cap_20pct'])} | {money(mins['total_minimums']) if use_minimums else '-'} |
| Earliest verdict | ad has spent 2x target CPA | {money(2 * a.target_cpa)} |
| Pause, no signal | 2x CPA spent, 0 purchases, no ATC/IC signal | at {money(2 * a.target_cpa)} |
| Pause, off target | 3x CPA spent and still 50%+ off KPI | at {money(3 * a.target_cpa)} |
| Review window | 7-14 days (3-day only once 10+ conversions/day) | never on one day |

Quality overrides volume: launch only the ads you would bet on; never pad to hit the number.
"""
    emit({"volume": vol, "minimums": mins, "use_minimums": use_minimums, "verdict_spend": 2 * a.target_cpa,
          "pause_off_target_spend": 3 * a.target_cpa}, text, a.json)


# ----------------------------------------------------------------------------------------------
# CSV loading (Ads Manager exports)
# ----------------------------------------------------------------------------------------------

# Candidate header names, lowercase, currency suffix stripped. First match wins.
COLUMNS: dict[str, list[str]] = {
    "ad": ["ad name", "ad", "creative name", "name"],
    "adset": ["ad set name", "adset name", "ad set"],
    "campaign": ["campaign name", "campaign"],
    "spend": ["amount spent", "spend", "cost", "amount spent usd"],
    "impressions": ["impressions"],
    "reach": ["reach"],
    "frequency": ["frequency"],
    "link_clicks": ["link clicks", "clicks link", "outbound clicks", "unique link clicks"],
    "clicks_all": ["clicks all", "clicks"],
    "purchases": ["purchases", "website purchases", "results", "conversions"],
    "revenue": ["purchases conversion value", "website purchases conversion value", "purchase conversion value",
                "conversion value", "revenue", "purchase value"],
    "atc": ["adds to cart", "website adds to cart", "add to cart"],
    "ic": ["checkouts initiated", "website checkouts initiated", "initiate checkout"],
    "plays_3s": ["3-second video plays", "3 second video plays", "video plays 3s", "3s video plays"],
    "thruplays": ["thruplays", "thruplay"],
    "plays_100": ["video plays at 100%", "video plays 100%"],
    "days": ["days running", "days active", "age days", "days"],
    "start": ["reporting starts", "start date", "first day"],
    "end": ["reporting ends", "end date"],
    "inc_roas": ["incremental roas", "incremental purchase roas", "roas incremental"],
    "status": ["delivery", "status", "ad delivery"],
}


def _norm(h: str) -> str:
    h = h.strip().lower()
    h = re.sub(r"\((usd|eur|gbp|cad|aud|[a-z]{3})\)", "", h)
    h = re.sub(r"[\(\)\[\]:]", " ", h)
    h = re.sub(r"\s+", " ", h).strip()
    return h


def _to_float(v: str | None) -> float | None:
    """Parse numbers from US ("1,234.50") and EU ("1.234,50", "1234,5") exports, with currency/percent signs."""
    if v is None:
        return None
    s = re.sub(r"[^\d,.\-]", "", str(v).strip())
    if s in ("", "-", "--", ".", ","):
        return None
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):          # EU: dot thousands, comma decimal
            s = s.replace(".", "").replace(",", ".")
        else:                                    # US: comma thousands
            s = s.replace(",", "")
    elif "," in s:
        head, _, tail = s.rpartition(",")
        if len(tail) == 3 and s.count(",") >= 1 and all(len(g) == 3 for g in s.split(",")[1:]):
            s = s.replace(",", "")               # 1,234 / 12,345,678 -> thousands
        else:
            s = s.replace(",", ".")              # 12,5 / 1234,50 -> decimal comma
    try:
        return float(s)
    except ValueError:
        return None


@dataclass
class AdRow:
    ad: str
    adset: str = ""
    campaign: str = ""
    spend: float = 0.0
    impressions: float | None = None
    reach: float | None = None
    frequency: float | None = None
    link_clicks: float | None = None
    purchases: float = 0.0
    revenue: float | None = None
    atc: float | None = None
    ic: float | None = None
    plays_3s: float | None = None
    thruplays: float | None = None
    days: float | None = None
    inc_roas: float | None = None
    status: str = ""

    # derived
    @property
    def cpm(self): return safe_div(self.spend * 1000, self.impressions)
    @property
    def ctr(self): return safe_div(self.link_clicks, self.impressions)
    @property
    def cpc(self): return safe_div(self.spend, self.link_clicks)
    @property
    def cpa(self): return safe_div(self.spend, self.purchases) if self.purchases else None
    @property
    def roas(self): return safe_div(self.revenue, self.spend) if self.revenue is not None else None
    @property
    def hook_rate(self): return safe_div(self.plays_3s, self.impressions)
    @property
    def hold_rate(self): return safe_div(self.thruplays, self.plays_3s)
    @property
    def cost_atc(self): return safe_div(self.spend, self.atc) if self.atc else None
    @property
    def cost_ic(self): return safe_div(self.spend, self.ic) if self.ic else None
    @property
    def cvr_click(self): return safe_div(self.purchases, self.link_clicks) if self.link_clicks else None
    @property
    def is_video(self): return bool(self.plays_3s)


def load_csv(path: str) -> list[AdRow]:
    try:
        fh = open(path, newline="", encoding="utf-8-sig")
    except OSError as exc:
        die(f"cannot open {path}: {exc}")
    with fh:
        sample = fh.read(4096)
        fh.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        except csv.Error:
            dialect = csv.excel
        reader = csv.DictReader(fh, dialect=dialect)
        if not reader.fieldnames:
            die("CSV has no header row")
        normed = {_norm(h): h for h in reader.fieldnames}
        mapping: dict[str, str] = {}
        for key, cands in COLUMNS.items():
            for c in cands:
                if c in normed:
                    mapping[key] = normed[c]
                    break
            else:
                # fuzzy: header starts with candidate
                for c in cands:
                    hit = next((orig for n, orig in normed.items() if n.startswith(c)), None)
                    if hit:
                        mapping[key] = hit
                        break
        if "spend" not in mapping:
            die(f"no spend column found. Headers: {list(reader.fieldnames)}")
        rows: list[AdRow] = []
        for i, r in enumerate(reader):
            name = (r.get(mapping.get("ad", ""), "") or f"row {i + 1}").strip()
            if name.lower() in ("total", "totals", "results from"):
                continue
            f = lambda k: _to_float(r.get(mapping[k])) if k in mapping else None  # noqa: E731
            row = AdRow(
                ad=name,
                adset=(r.get(mapping.get("adset", ""), "") or "").strip(),
                campaign=(r.get(mapping.get("campaign", ""), "") or "").strip(),
                spend=f("spend") or 0.0,
                impressions=f("impressions"), reach=f("reach"), frequency=f("frequency"),
                link_clicks=f("link_clicks") if "link_clicks" in mapping else f("clicks_all"),
                purchases=f("purchases") or 0.0, revenue=f("revenue"), atc=f("atc"), ic=f("ic"),
                plays_3s=f("plays_3s"), thruplays=f("thruplays") if "thruplays" in mapping else f("plays_100"),
                days=f("days"), inc_roas=f("inc_roas"),
                status=(r.get(mapping.get("status", ""), "") or "").strip(),
            )
            if row.spend <= 0 and not row.impressions:
                continue
            rows.append(row)
    if not rows:
        die("no ad rows with spend found in the CSV")
    return rows


# ----------------------------------------------------------------------------------------------
# analyze
# ----------------------------------------------------------------------------------------------


@dataclass
class Verdict:
    ad: str
    adset: str
    spend: float
    share: float
    purchases: float
    cpa: float | None
    roas: float | None
    verdict: str
    reason: str
    creative_fix: str
    flags: list[str]


def _median(vals: Iterable[float | None]) -> float | None:
    v = [x for x in vals if x is not None]
    return statistics.median(v) if v else None


def account_baseline(rows: list[AdRow]) -> dict:
    tot = lambda attr: sum(getattr(r, attr) or 0 for r in rows)  # noqa: E731
    spend, imps, clicks = tot("spend"), tot("impressions"), tot("link_clicks")
    purch, atc, ic = tot("purchases"), tot("atc"), tot("ic")
    rev_rows = [r for r in rows if r.revenue is not None]
    rev = sum(r.revenue for r in rev_rows) if rev_rows else None
    vids = [r for r in rows if r.is_video]
    v_imps = sum(r.impressions or 0 for r in vids)
    v_3s = sum(r.plays_3s or 0 for r in vids)
    v_tp = sum(r.thruplays or 0 for r in vids)
    return {
        "spend": spend, "impressions": imps, "link_clicks": clicks, "purchases": purch, "revenue": rev,
        "cpm": safe_div(spend * 1000, imps), "ctr": safe_div(clicks, imps), "cpc": safe_div(spend, clicks),
        "cpa": safe_div(spend, purch) if purch else None, "roas": safe_div(rev, spend) if rev is not None else None,
        "cost_atc": safe_div(spend, atc) if atc else None, "cost_ic": safe_div(spend, ic) if ic else None,
        "cvr_click": safe_div(purch, clicks) if clicks else None,
        "hook_rate": safe_div(v_3s, v_imps) if v_imps else None, "hold_rate": safe_div(v_tp, v_3s) if v_3s else None,
        # medians are steadier references for per-ad flags than spend-weighted totals
        "median_ctr": _median(r.ctr for r in rows if (r.impressions or 0) >= 1000),
        "median_cpm": _median(r.cpm for r in rows if (r.impressions or 0) >= 1000),
        "median_hook": _median(r.hook_rate for r in vids if (r.impressions or 0) >= 1000),
        "median_hold": _median(r.hold_rate for r in vids if (r.plays_3s or 0) >= 300),
    }


def creative_diagnosis(r: AdRow, base: dict) -> str:
    """Which part of the ad to fix first, read top-down through the funnel (hook -> hold -> click -> page)."""
    if (r.impressions or 0) < 1000:
        return "not enough impressions to diagnose"
    mh, mo, mc = base.get("median_hook"), base.get("median_hold"), base.get("median_ctr")
    if r.is_video and mh and r.hook_rate is not None and r.hook_rate < 0.8 * mh:
        return "weak first 3 s: new visual hook + first line (keep the body)"
    if r.is_video and mo and r.hold_rate is not None and r.hold_rate < 0.8 * mo:
        return "hook stops people, body loses them: new lead/body pacing (cuts every 1-3 s, open loop, one shot per line)"
    if mc and r.ctr is not None and r.ctr < 0.8 * mc:
        return "watched but not clicked: sharper desire/dream outcome, proof, offer and CTA"
    acct_cvr = base.get("cvr_click")
    if acct_cvr and r.cvr_click is not None and (r.link_clicks or 0) >= 100 and r.cvr_click < 0.6 * acct_cvr:
        return "clicks but no buyers: ad-to-page message match, price/offer reveal, pre-qualify in the ad"
    return "no weak stage vs account medians"


def judge(r: AdRow, base: dict, t_cpa: float | None, t_roas: float | None, top_spend_cut: float, account_on_target: bool) -> Verdict:
    flags: list[str] = []
    share = safe_div(r.spend, base["spend"]) or 0.0
    cpa, roas = r.cpa, r.roas
    # KPI ratio: >= 1 means at/above target. Prefer ROAS if both targets given and revenue exists.
    if t_roas and roas is not None:
        ratio = roas / t_roas
    elif t_cpa and cpa is not None:
        ratio = t_cpa / cpa
    elif t_cpa and r.purchases == 0:
        ratio = 0.0
    else:
        ratio = None
    ref_cpa = t_cpa or (safe_div(base["revenue"], base["purchases"]) / t_roas if (t_roas and base.get("revenue") and base["purchases"]) else None)

    # anomaly flags (viral / wrong-demographic style spend hogs)
    if base.get("median_cpm") and r.cpm and (r.impressions or 0) >= 1000 and r.cpm < 0.4 * base["median_cpm"]:
        flags.append("CPM far below account norm (viral/low-quality reach?)")
    if base.get("median_ctr") and r.ctr and (r.impressions or 0) >= 1000 and r.ctr > 2.5 * base["median_ctr"]:
        flags.append("CTR far above account norm (check who it reaches)")
    if r.frequency and r.frequency > 4:
        flags.append(f"frequency {r.frequency:.1f} (prospecting): check fatigue / audience pocket")
    if r.inc_roas is not None and roas:
        drop = 1 - r.inc_roas / roas if roas else 0
        if drop > 0.45:
            flags.append(f"incremental ROAS {r.inc_roas:.2f} vs reported {roas:.2f}: steep drop, likely low incrementality")

    fix = creative_diagnosis(r, base)
    big_spender = r.spend >= top_spend_cut and r.spend > 0

    if ratio is not None and ratio >= 1:
        if big_spender and (r.inc_roas is None or (t_roas is None or r.inc_roas >= 0.6 * t_roas)):
            return Verdict(r.ad, r.adset, r.spend, share, r.purchases, cpa, roas, "WINNER",
                           "top-10% spender at/above target: iterate it, duplicate into interest-winners and retention", fix, flags)
        return Verdict(r.ad, r.adset, r.spend, share, r.purchases, cpa, roas, "KEEP", "hitting KPI: leave it alone", fix, flags)

    # Viral / wrong-pocket hogs are capped, not paused (checked before the CPA rules, as in the pausing tree)
    anomaly = any(f.startswith(("CPM far below", "CTR far above")) for f in flags)
    if anomaly and share >= 0.2 and ratio is not None and ratio < 1:
        return Verdict(r.ad, r.adset, r.spend, share, r.purchases, cpa, roas, "CAP",
                       f"hogs {pct(share, 0)} of spend below target with anomaly signs: put a max-% spend limit on its ad set, do not pause", fix, flags)

    if ref_cpa is None:
        return Verdict(r.ad, r.adset, r.spend, share, r.purchases, cpa, roas, "NO-TARGET", "give --target-cpa or --target-roas", fix, flags)

    if r.spend < 2 * ref_cpa:
        return Verdict(r.ad, r.adset, r.spend, share, r.purchases, cpa, roas, "TOO-EARLY",
                       f"spent {money(r.spend)} < 2x target CPA ({money(2 * ref_cpa)}): no verdict yet", fix, flags)

    leading = False
    if base.get("cost_ic") and r.cost_ic is not None and r.cost_ic <= base["cost_ic"]:
        leading = True
    elif base.get("cost_atc") and r.cost_atc is not None and r.cost_atc <= base["cost_atc"]:
        leading = True

    if r.purchases == 0:
        if leading:
            return Verdict(r.ad, r.adset, r.spend, share, 0, None, roas, "WATCH",
                           "no purchase yet but cost per checkout/ATC at or better than account: leading indicator, give it to 3x CPA", fix, flags)
        if share >= 0.25 and account_on_target:
            return Verdict(r.ad, r.adset, r.spend, share, 0, None, roas, "WATCH",
                           "big spender while the account is on target: may be an assisting top-of-funnel ad, check incremental first", fix, flags)
        return Verdict(r.ad, r.adset, r.spend, share, 0, None, roas, "PAUSE",
                       f"{money(r.spend)} spent (>= 2x CPA) with no purchases and no mid-funnel signal", fix, flags)

    if ratio is not None and ratio >= 0.5:
        if share >= 0.25 and account_on_target:
            return Verdict(r.ad, r.adset, r.spend, share, r.purchases, cpa, roas, "KEEP",
                           "top spender, account on target: likely first-touch ad; killing it usually crashes the account 3-7 days later", fix, flags)
        return Verdict(r.ad, r.adset, r.spend, share, r.purchases, cpa, roas, "WATCH",
                       "within 50% of KPI: keep running, re-check on the 7-14 day window", fix, flags)

    if r.spend >= 3 * ref_cpa:
        if share >= 0.25 and account_on_target:
            return Verdict(r.ad, r.adset, r.spend, share, r.purchases, cpa, roas, "CAP",
                           "far off KPI but carries the account: cap its ad set with a max-% limit (e.g. 50%) instead of pausing", fix, flags)
        return Verdict(r.ad, r.adset, r.spend, share, r.purchases, cpa, roas, "PAUSE",
                       f"spent >= 3x CPA ({money(3 * ref_cpa)}) and still 50%+ off KPI", fix, flags)
    return Verdict(r.ad, r.adset, r.spend, share, r.purchases, cpa, roas, "WATCH",
                   "50%+ off KPI: decide at 3x CPA spend", fix, flags)


def cmd_analyze(a: argparse.Namespace) -> None:
    if not a.target_cpa and not a.target_roas:
        die("give --target-cpa and/or --target-roas (run `a2.py economics` if you do not know them)")
    rows = load_csv(a.csv)
    base = account_baseline(rows)
    spends = sorted((r.spend for r in rows), reverse=True)
    k = max(1, math.ceil(len(spends) * 0.10))
    top_cut = spends[k - 1]
    if a.target_roas and base.get("roas") is not None:
        on_target = base["roas"] >= a.target_roas
    elif a.target_cpa and base.get("cpa") is not None:
        on_target = base["cpa"] <= a.target_cpa
    else:
        on_target = False
    verdicts = [judge(r, base, a.target_cpa, a.target_roas, top_cut, on_target) for r in rows]
    order = {"WINNER": 0, "KEEP": 1, "CAP": 2, "WATCH": 3, "TOO-EARLY": 4, "PAUSE": 5, "NO-TARGET": 6}
    verdicts.sort(key=lambda v: (order.get(v.verdict, 9), -v.spend))

    lines = ["## Account baseline (this export)", "| Metric | Value |", "|---|---|"]
    for label, key, fmt in [("Spend", "spend", money), ("CPM", "cpm", money), ("CTR (link)", "ctr", pct),
                            ("CPC (link)", "cpc", money), ("Hook rate (3s/impr)", "hook_rate", pct),
                            ("Hold rate (ThruPlay/3s)", "hold_rate", pct), ("Cost per ATC", "cost_atc", money),
                            ("Cost per checkout", "cost_ic", money), ("Click-to-purchase CVR", "cvr_click", pct),
                            ("CPA / CPP", "cpa", money), ("ROAS", "roas", num)]:
        lines.append(f"| {label} | {fmt(base.get(key))} |")
    tgt = []
    if a.target_cpa:
        tgt.append(f"target CPA {money(a.target_cpa)}")
    if a.target_roas:
        tgt.append(f"target ROAS {num(a.target_roas)}")
    lines.append(f"\nAccount is {'ON' if on_target else 'OFF'} target ({', '.join(tgt)}). Top-10% spend cut: {money(top_cut)}.\n")
    lines.append("## Verdict per ad")
    lines.append("| Verdict | Ad | Ad set | Spend | Share | Purch | CPA | ROAS | Why | Fix first | Flags |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    for v in verdicts:
        lines.append(f"| **{v.verdict}** | {v.ad} | {v.adset} | {money(v.spend)} | {pct(v.share, 0)} | {num(v.purchases, 0)} | "
                     f"{money(v.cpa)} | {num(v.roas)} | {v.reason} | {v.creative_fix} | {'; '.join(v.flags) or '-'} |")
    counts: dict[str, int] = {}
    for v in verdicts:
        counts[v.verdict] = counts.get(v.verdict, 0) + 1
    lines.append("\nCounts: " + ", ".join(f"{k} {n}" for k, n in sorted(counts.items(), key=lambda kv: order.get(kv[0], 9))))
    lines.append("\nRules: verdicts need 7-14 days of data; never act on part-day or post-sale data; check the pixel and the "
                 "incremental column before pausing a big spender. CAP = max-% ad set spending limit inside the CBO.")
    payload = {"baseline": base, "on_target": on_target, "top10_spend_cut": top_cut,
               "verdicts": [asdict(v) for v in verdicts], "counts": counts}
    emit(payload, "\n".join(lines), a.json)


# ----------------------------------------------------------------------------------------------
# scale (vertical budget moves)
# ----------------------------------------------------------------------------------------------


def scale_step(budget: float, kpi_3d: float, kpi_7d: float, target: float, metric: str = "roas",
               hours_since_change: float = 72, conv_per_day: float | None = None, kpi_14d: float | None = None) -> dict:
    """Next daily budget for the prospecting CBO (Blueprint "Vertical Scaling" + "Learning Phase" lessons).

    ratio > 1 means better than target. Decisions use the 7-day window, confirmed by 3-day (and 14-day if given).
    Default move 10-30% every 48-72 h; 10-15% for big, tight campaigns (>= $3k/day); bigger at ~$100-300/day;
    +50% is fine for an established campaign ~40% above target; double when 'smashing' (>= 2x target), bounded by
    delta math (even if the new dollars returned nothing, blended KPI stays at target).
    """
    def ratio(k: float) -> float:
        return (target / k) if metric == "cpa" else (k / target)
    r3, r7 = ratio(kpi_3d), ratio(kpi_7d)
    r14 = ratio(kpi_14d) if kpi_14d else None
    big = budget >= 3000
    small = budget <= 300
    delta_cap = round(budget * r7, 2)  # max budget at which, with zero return on new spend, the 7-day KPI still meets target
    res = {"ratio_3d": round(r3, 3), "ratio_7d": round(r7, 3), "ratio_14d": round(r14, 3) if r14 else None,
           "delta_max_budget": delta_cap}

    smashing = r7 >= 2.0 and r3 >= 1.6
    if hours_since_change < 48 and not smashing:
        return {**res, "action": "HOLD", "new_budget": budget, "change_pct": 0.0,
                "why": "last move < 48 h ago: wait 48-72 h between moves unless smashing (>= 2x target)"}
    if smashing:
        new = min(budget * 2, delta_cap)
        return {**res, "action": "INCREASE", "new_budget": round(new, 2), "change_pct": new / budget - 1,
                "why": "smashing (>= 2x target on 7 days): double, bounded by delta math — even if the new dollars "
                       "returned nothing the account would still sit at target"}
    if r7 >= 1.0 and r3 < 0.9:
        return {**res, "action": "HOLD", "new_budget": budget, "change_pct": 0.0,
                "why": "7-day above target but last 3 days soft: hold the line; if cost per ATC/IC is flat, buyers are just lagging"}
    if r14 is not None and r14 < 0.9 and r7 >= 1.0:
        step = 0.10
        why = "7-day above target but 14-day below: smallest step until the trend confirms"
    elif r7 >= 1.4 and r3 >= 1.2:
        step = 0.50 if (small or not big) else 0.30
        why = ("~40%+ above target and stable: +50% is fine (the ROAS dip after a big jump is conversion lag on new impressions)"
               if step == 0.5 else "well above target on a big campaign: +30% (top of the 10-30% band)")
    elif r7 >= 1.15:
        step = 0.15 if big else (0.35 if small else 0.25)
        why = "comfortably above target: " + ("10-15% on a big, tight campaign" if big else "a meaningful step (small budgets need bigger moves)")
    elif r7 >= 1.0:
        step = 0.10 if big else (0.25 if small else 0.15)
        why = "just above target: small step" + ("" if not small else " ($100 -> $110 does nothing at this size)")
    elif r7 >= 0.9:
        return {**res, "action": "HOLD", "new_budget": budget, "change_pct": 0.0,
                "why": "0-10% below target: do not raise; slow vertical until the creative pipeline (iterations of winners) catches up"}
    elif r7 >= 0.75:
        step = -0.20
        why = "10-25% below target for a week: trim 20% and ship iterations of the winners (make money first)"
    else:
        step = -0.30
        why = "25%+ below target for a week: cut 30%; fix creative/offer before spending more"
    if conv_per_day is not None and conv_per_day < 3 and step > 0:
        why += "; under 3 conversions/day the 3-day number is noise — lean on the 7/14-day windows"
    return {**res, "action": "INCREASE" if step > 0 else "DECREASE", "new_budget": round(budget * (1 + step), 2),
            "change_pct": step, "why": why}


def cmd_scale(a: argparse.Namespace) -> None:
    res = scale_step(a.budget, a.kpi_3d, a.kpi_7d, a.target, a.metric, a.hours_since_change, a.conv_per_day, a.kpi_14d)
    text = f"""## Vertical scaling step
Budget {money(a.budget)}/day | {a.metric.upper()} 3-day {a.kpi_3d} | 7-day {a.kpi_7d} | 14-day {a.kpi_14d or '-'} | target {a.target}

**{res['action']} -> {money(res['new_budget'])}/day ({res['change_pct'] * 100:+.0f}%)**
Why: {res['why']}.
Delta-math ceiling: {money(res['delta_max_budget'])}/day. Check before moving: King goal, new-customer share (audience segments),
incremental ROAS of the new segment, and the 14 -> 7 -> 3 -> 1 day trend. Twin engine: keep iterations of winners shipping every week.
"""
    emit(res, text, a.json)


# ----------------------------------------------------------------------------------------------
# cost-controls (hard scaling)
# ----------------------------------------------------------------------------------------------


def cost_control_plan(target_cpa: float | None, target_roas: float | None, expected_spend: float,
                      monthly_spend: float | None = None) -> dict:
    """Cost-control setup (Blueprint "Cost Controls" lesson + Pellegrini's bid-cap scaling campaign).

    Cost cap / cost per result goal = the TRUE target CPA (never a "greedy" lower number).
    Budget = expected daily spend / 0.8, so the cap (not the budget) limits delivery and average spend-through is ~80%.
    ROAS goal: same rules with the true target ROAS. Bid caps: advanced operators only, budget inflated.
    """
    plan: dict = {"expected_spend": expected_spend, "controls": [], "warnings": []}
    if monthly_spend is not None and monthly_spend < 50_000:
        plan["warnings"].append(f"monthly spend {money(monthly_spend)} < $50k: cost controls rarely work sustainably here; "
                                "stay on highest volume and fix creative/offer first")
    budget = round(expected_spend / 0.8, 2)
    if target_cpa:
        plan["controls"].append({
            "type": "cost cap (cost per result goal) — default for high-spend e-commerce",
            "value": round(target_cpa, 2),
            "budget": budget,
            "why": "cap = true target CPA (profitable on first purchase or on the LTV you underwrite); budget = expected spend / 0.8",
        })
        plan["controls"].append({
            "type": "bid cap — advanced only (Pellegrini: 'inflated, normal bid cap' scaling campaign for top winners)",
            "value": round(target_cpa, 2),
            "test_rungs": sorted({round(target_cpa * m, 2) for m in (0.85, 1.0, 1.2)}),
            "budget": round(expected_spend * 3, 2),
            "why": "a bid cap limits each auction bid, so spend is governed by the bid: inflate the budget (2-5x expected spend) and let "
                   "under-delivery be normal; one ad set per rung, proven winners only, judge each rung on 3-7 days",
        })
    if target_roas:
        plan["controls"].append({
            "type": "ROAS goal (min ROAS, maximize value) — same rules as cost caps",
            "value": round(target_roas, 2),
            "budget": budget,
            "why": "goal = true target ROAS on the same attribution you judge on; budget = expected spend / 0.8",
        })
    plan["rules"] = [
        "Cost controls only when the account already spends ~$50k-100k+/month at target with daily conversion volume.",
        "The cap evaluates on a ~7-day lookback: judge it on 7 days, never on one day.",
        "Healthy = target hit and ~80% of budget spent on average (good days spend 100%+, bad days 50% or less).",
        "Never 'game' the cap below target; a $1-2 (~2%) move can open or close a lot of inventory.",
        "The prospecting CBO on highest volume stays the core; capped campaigns hold proven ads only.",
        "Run `a2.py cap-diagnose` every few days to pick the move (budget, cap, or creative).",
    ]
    return plan


def cap_diagnose(cap: float, actual: float, budget: float, avg_spend: float, true_target: float | None = None,
                 metric: str = "cpa") -> dict:
    """The 4-scenario matrix: target hit? x budget spent in full? (7-day averages)."""
    true_target = true_target or cap
    hit = actual <= cap if metric == "cpa" else actual >= cap
    util = avg_spend / budget if budget else 0.0
    full = util >= 0.95
    healthy_util = 0.7 <= util < 0.95
    below_target_cap = (cap < true_target) if metric == "cpa" else (cap > true_target)
    if hit and full:
        scen, action = 1, ("Target hit AND budget spent in full: RAISE THE BUDGET (keep the cap) until spend-through falls back to ~80%. "
                           "Only alternative: tighten the cap by $1-2 if you deliberately want more margin.")
    elif hit and not full:
        if healthy_util:
            scen, action = 4, "Working as designed (~80% spend-through at target). Leave it; feed iterations of the winners to grow volume."
        elif below_target_cap:
            scen, action = 4, ("Target hit but under-spending and the cap is below your true target: walk the cap up toward the true "
                               "target in small steps (+2-3%, a few days each) or set it straight to the true target.")
        else:
            scen, action = 4, ("Target hit but under-spending with the cap already at the true target: the cap is restricting correctly. "
                               "Grow volume with creative — iterate the winners hardest; you are close.")
    elif not hit and full:
        scen, action = 2, ("Target NOT hit while the budget is fully spent: the cap is not being honoured (too little data/creative). "
                           "Ask whether you should run caps at all at this spend; reduce the budget, and iterate the creative that has signal.")
    else:
        scen, action = 3, ("Target NOT hit AND budget not spent: double bad. Usually stop using caps for this campaign and go back to "
                           "highest volume; the real fix is new creative. If you persist, raise the cap only up to the true target.")
    return {"scenario": scen, "target_hit": hit, "spend_through": round(util, 3), "action": action}


def cmd_cost_controls(a: argparse.Namespace) -> None:
    if not a.target_cpa and not a.target_roas:
        die("give --target-cpa and/or --target-roas")
    p = cost_control_plan(a.target_cpa, a.target_roas, a.expected_spend, a.monthly_spend)
    lines = [f"## Cost-control setup (expected spend {money(a.expected_spend)}/day)"]
    for w in p["warnings"]:
        lines.append(f"\n> WARNING: {w}")
    for c in p["controls"]:
        is_roas = c["type"].startswith("ROAS")
        fmt = num if is_roas else money
        rung = f"\n- Test rungs: {', '.join(fmt(x) for x in c['test_rungs'])}" if "test_rungs" in c else ""
        lines.append(f"\n### {c['type']}\n- Set to: **{fmt(c['value'])}**\n- Daily budget: **{money(c['budget'])}**{rung}\n- Why: {c['why']}")
    lines.append("\n### Rules\n" + "\n".join(f"- {r}" for r in p["rules"]))
    emit(p, "\n".join(lines), a.json)


def cmd_cap_diagnose(a: argparse.Namespace) -> None:
    r = cap_diagnose(a.cap, a.actual, a.budget, a.avg_spend, a.true_target, a.metric)
    text = f"""## Cost-control diagnosis (7-day averages)
Cap {a.cap} | actual {a.metric.upper()} {a.actual} | budget {money(a.budget)} | avg spend {money(a.avg_spend)} ({pct(r['spend_through'], 0)} spend-through)

**Scenario {r['scenario']}** — target {'hit' if r['target_hit'] else 'NOT hit'}.
{r['action']}
"""
    emit(r, text, a.json)


# ----------------------------------------------------------------------------------------------
# zombie (candidate finder)
# ----------------------------------------------------------------------------------------------


def zombie_buckets(rows: list[AdRow], be_cpa: float, proven_spend: float) -> dict:
    """Sort ads into the zombie training's buckets (Blueprint 'Zombie Campaigns' 2026).

    fatigued_winner   proven at/below breakeven CPA on real spend, now paused/inactive (or no longer delivering)
    no_efficiency     got delivery (>= 3x breakeven CPA spent) but CPA above breakeven; includes 'hogs' (>= 60% of
                      their ad set's spend while unprofitable) — move these out so the rest of the pack can breathe
    dud               never got off the ground (< 2x breakeven CPA spent, no purchases); move ONE per ad set, pause the rest
    keep              active and profitable: leave it where it is (never move a live winner into caps)
    """
    by_set: dict[str, float] = {}
    for r in rows:
        by_set[r.adset] = by_set.get(r.adset, 0.0) + r.spend
    out: dict[str, list] = {"fatigued_winner": [], "no_efficiency": [], "dud": [], "keep": []}
    duds_by_set: dict[str, list[AdRow]] = {}
    for r in rows:
        st = r.status.lower()
        inactive = any(k in st for k in ("inactive", "paused", "off", "not delivering", "completed", "archived"))
        cpa = r.cpa
        set_share = safe_div(r.spend, by_set.get(r.adset)) or 0.0
        item = {"ad": r.ad, "adset": r.adset, "spend": round(r.spend, 2), "purchases": r.purchases,
                "cpa": round(cpa, 2) if cpa else None, "status": r.status or "-", "set_share": round(set_share, 3)}
        profitable = cpa is not None and cpa <= be_cpa
        if profitable and r.spend >= proven_spend:
            if inactive:
                out["fatigued_winner"].append({**item, "why": f"proven: CPA {money(cpa)} <= breakeven on {money(r.spend)}; now inactive"})
            else:
                out["keep"].append({**item, "why": "active and at/below breakeven: leave it in prospecting"})
        elif r.spend >= 3 * be_cpa and not profitable:
            hog = set_share >= 0.6 and not inactive
            why = (f"hogs {pct(set_share, 0)} of its ad set while unprofitable: move it so the other ads get spend" if hog
                   else f"had delivery ({money(r.spend)}) but CPA {money(cpa) if cpa else 'n/a'} > breakeven")
            out["no_efficiency"].append({**item, "why": why, "hog": hog})
        elif r.spend < 2 * be_cpa and r.purchases == 0:
            duds_by_set.setdefault(r.adset, []).append(r)
        elif profitable and not inactive:
            out["keep"].append({**item, "why": "profitable, still building spend: leave it"})
    for adset, ads in duds_by_set.items():
        ads.sort(key=lambda x: ((x.ctr or 0), x.spend), reverse=True)
        rep = ads[0]
        out["dud"].append({"ad": rep.ad, "adset": adset, "spend": round(rep.spend, 2), "purchases": 0, "cpa": None,
                           "status": rep.status or "-", "set_share": None,
                           "why": f"dud pack: move this one (best CTR of {len(ads)}), pause the other {len(ads) - 1}" if len(ads) > 1
                           else "never got off the ground"})
    return out


def cmd_zombie(a: argparse.Namespace) -> None:
    rows = load_csv(a.csv)
    be = a.breakeven_cpa
    proven = a.min_spend if a.min_spend is not None else 10 * be
    b = zombie_buckets(rows, be, proven)
    daily = a.account_daily_spend
    if daily:
        budget = max(be, 0.10 * daily)
        budget_note = (f"start ~{money(budget)}/day (between 1x breakeven CPA and ~10% of the account's {money(daily)}/day); "
                       "expect it to float >= 20% under budget, often far less")
    else:
        budget = be
        budget_note = f"start at 1x breakeven CPA = {money(be)}/day ('sneak a purchase in per day')"
    labels = {"fatigued_winner": "Ad set 1 — Fatigued winners", "no_efficiency": "Ad set 3 — Delivery but no efficiency",
              "dud": "Ad set 2 — Duds (one per dead pack)", "keep": "Leave in prospecting (do NOT move)"}
    lines = [f"## Zombie campaign plan",
             f"- Campaign: Sales, CBO, **bid strategy = Bid cap**, highest-volume campaigns untouched",
             f"- **Bid cap = breakeven CPA {money(be)}** — nothing under, nothing over; never raise it to force spend",
             f"- Budget: {budget_note}",
             f"- Audience: broad, exclude purchasers/customer lists, engaged, visitors, ATC/IC; Standard attribution (incremental not allowed with bid cap)",
             f"- Proven = lifetime spend >= {money(proven)} at CPA <= breakeven", ""]
    for key in ("fatigued_winner", "no_efficiency", "dud", "keep"):
        items = sorted(b[key], key=lambda x: -x["spend"])
        lines.append(f"### {labels[key]} ({len(items)})")
        if not items:
            lines.append("- none\n")
            continue
        lines.append("| Ad | Ad set | Spend | Purch | CPA | Status | Why |\n|---|---|---|---|---|---|---|")
        for o in items[: a.limit]:
            lines.append(f"| {o['ad']} | {o['adset']} | {money(o['spend'])} | {num(o['purchases'], 0)} | {money(o['cpa'])} | {o['status']} | {o['why']} |")
        lines.append("")
    lines.append("Start small: the ~15 best fatigued winners first, evergreen creative only (no sale ads). Copy by post ID to keep "
                 "comments/likes. Revive: if a zombie ad spends well at/below breakeven for 7-14 days, restart it where it used to win "
                 "(or a new pack in the prospecting CBO) and optionally leave it running in zombie too.")
    emit({"breakeven_cpa": be, "start_budget": round(budget, 2), "proven_spend": proven, "buckets": b}, "\n".join(lines), a.json)


# ----------------------------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="a2.py", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("economics", help="break-even and target ROAS/CPA")
    e.add_argument("--aov", type=float, required=True)
    e.add_argument("--cogs-pct", type=float, default=0.0, help="COGS as %% of AOV")
    e.add_argument("--cogs", type=float, default=0.0, help="COGS per order in money (added to --cogs-pct)")
    e.add_argument("--shipping", type=float, default=0.0, help="shipping/fulfilment cost per order")
    e.add_argument("--fees-pct", type=float, default=3.0, help="payment fees %% of AOV (default 3)")
    e.add_argument("--other", type=float, default=0.0, help="other variable cost per order")
    e.add_argument("--profit-pct", type=float, default=None, help="target profit %% of revenue (overrides --buffer)")
    e.add_argument("--buffer", type=float, default=1.10, help="target ROAS = break-even x buffer (default 1.10)")
    e.add_argument("--ltv-multiple", type=float, default=1.0, help="allow CPA above first-order profit (e.g. 1.5)")
    e.add_argument("--json", action="store_true")
    e.set_defaults(func=cmd_economics)

    t = sub.add_parser("testing-plan", help="creative volume, new-pack minimums, kill thresholds")
    t.add_argument("--campaign-budget", type=float, required=True, help="prospecting CBO daily budget")
    t.add_argument("--target-cpa", type=float, required=True)
    t.add_argument("--monthly-spend", type=float, default=None, help="defaults to budget x 30.4")
    t.add_argument("--new-packs", type=int, default=1, help="new packs (ad sets) launching this week")
    t.add_argument("--force-minimums", action="store_true", help="use minimums even under $150/day")
    t.add_argument("--json", action="store_true")
    t.set_defaults(func=cmd_testing_plan)

    an = sub.add_parser("analyze", help="metrics, diagnosis and verdicts from an Ads Manager CSV (ad level)")
    an.add_argument("csv")
    an.add_argument("--target-cpa", type=float, default=None)
    an.add_argument("--target-roas", type=float, default=None)
    an.add_argument("--json", action="store_true")
    an.set_defaults(func=cmd_analyze)

    s = sub.add_parser("scale", help="next daily budget (vertical scaling)")
    s.add_argument("--budget", type=float, required=True)
    s.add_argument("--kpi-3d", type=float, required=True, help="ROAS (or CPA) over the last 3 days")
    s.add_argument("--kpi-7d", type=float, required=True, help="ROAS (or CPA) over the last 7 days")
    s.add_argument("--target", type=float, required=True)
    s.add_argument("--metric", choices=["roas", "cpa"], default="roas")
    s.add_argument("--kpi-14d", type=float, default=None, help="ROAS (or CPA) over the last 14 days")
    s.add_argument("--hours-since-change", type=float, default=72)
    s.add_argument("--conv-per-day", type=float, default=None)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_scale)

    c = sub.add_parser("cost-controls", help="cost cap / ROAS goal / bid cap setup")
    c.add_argument("--expected-spend", type=float, required=True, help="daily spend you expect this capped campaign to take")
    c.add_argument("--target-cpa", type=float, default=None, help="TRUE target CPA (profitable on first purchase or LTV)")
    c.add_argument("--target-roas", type=float, default=None)
    c.add_argument("--monthly-spend", type=float, default=None, help="account monthly spend (warns under $50k)")
    c.add_argument("--json", action="store_true")
    c.set_defaults(func=cmd_cost_controls)

    d = sub.add_parser("cap-diagnose", help="4-scenario diagnosis of a cost-capped / ROAS-goal campaign")
    d.add_argument("--cap", type=float, required=True, help="current cap (CPA) or ROAS goal")
    d.add_argument("--actual", type=float, required=True, help="7-day actual CPA (or ROAS with --metric roas)")
    d.add_argument("--budget", type=float, required=True, help="daily budget")
    d.add_argument("--avg-spend", type=float, required=True, help="7-day average daily spend")
    d.add_argument("--true-target", type=float, default=None, help="true target if the cap was set off-target")
    d.add_argument("--metric", choices=["cpa", "roas"], default="cpa")
    d.add_argument("--json", action="store_true")
    d.set_defaults(func=cmd_cap_diagnose)

    z = sub.add_parser("zombie", help="zombie campaign plan: buckets, bid cap, budget (from a long-range ad-level CSV)")
    z.add_argument("csv", help="ad-level export over a long range (e.g. last 12-24 months) with a Delivery/status column")
    z.add_argument("--breakeven-cpa", type=float, required=True, help="first-purchase breakeven CPA (= the bid cap)")
    z.add_argument("--min-spend", type=float, default=None, help="lifetime spend that counts as proven (default 10x breakeven CPA)")
    z.add_argument("--account-daily-spend", type=float, default=None, help="current account spend/day, sizes the starting budget")
    z.add_argument("--limit", type=int, default=25, help="rows per bucket in the table")
    z.add_argument("--json", action="store_true")
    z.set_defaults(func=cmd_zombie)
    return p


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
