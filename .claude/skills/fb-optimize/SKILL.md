---
name: fb-optimize
description: Optimize live Meta ad accounts exactly per the media-buying SOP (The Facebook Ads Blueprint). Daily anomaly scan (6 comparison windows, 20% threshold), 7-day minimum removal, frequency by swim lane (prospecting/retargeting/existing), audience-segment split and retargeting/retention break-out triggers, funnel drop diagnosis (CPM→CPC→ATC→IC→CPA), placement/geo/age breakdowns and value rules, learning-phase share, day-of-week budgets, max conversions vs max value, cost-cap matrix, pixel gut check and free-shipping threshold. Proposes changes for approval. Use when: "daily check", "what changed", "ROAS dropped", "performance fell", "audit my account", "frequency too high", "should I break out retargeting", "placement breakdown", "day of week analysis", "value rules", "cost cap not spending".
---

# fb-optimize: run the account per the SOP

Rulebook: **`docs/media-buying/SOP.md` §8** (plus §4.2, §5.6–5.9, §9.4). Engine:

```bash
echo '<json>' | python3 tools/fb-blueprint/blueprint.py <command>
```

## Safety contract

- Diagnose first, read-only. **Every budget, limit, value-rule, exclusion or placement change is a proposal** that waits for an explicit yes.
- **Never edit placements, audiences or exclusions on a live, working ad set.** Test the change in ONE new ad set. (SOP §8.5, law 10)
- Don't react to changes under 20–30% (noise). After a big change, wait about a week and only add iterations.
- Same `client_conversation_id` on every Meta call.

## Mode A: Daily check (≤15 minutes; run it every morning)

1. **Anomalies:** pull daily account metrics for the last 37 days with `ads_get_ad_entities` (level ad_account, `time_increment "1"`): spend, revenue (purchase value), purchases, clicks, impressions. Then run `anomalies {daily:[...]}`. Report the flags table and the `hint`.
2. **Minimums:** list prospecting ad sets with a `daily_min_spend_target`. For each, run `minimum_signal {avg_daily_spend, daily_minimum, days_live, above_target}`. `REMOVE_MINIMUM` → propose removing it (`ads_update_entity` with the ad set's min spend set to 0). Report the signal: **above** its minimum = winner; **at** it = it will fade. Also check that all live minimums total ≤20% of the campaign budget (SOP §5.4).
3. **Tracking sanity:** Events Manager/dataset stats show purchases flowing. If they drop to 0 → urgent, hand off to the pixel check.
4. **Scale due?** If 48–72 h have passed since the last budget move, hand off to `fb-scale`.
5. Sale running? Apply the sale rules: faster kills on cost per ATC/IC, big upward jumps, no repeated cuts (SOP §9.5).
6. **Pacing** (Mondays, or when asked): `pacing {spend_target, spend_mtd, revenue_target, revenue_mtd, days_remaining}` (SOP §3.5).

Volatility is mostly self-inflicted: pausing ads and ad sets too often. If the account swings, check the activity log (`ads_account_get_activity_logs`) for pauses and edits before blaming Meta.

## Mode B: Weekly optimization

1. **Audience segments:** prospecting with breakdown `user_segment_key` (audience segments; verify the name with `ads_get_field_context`), last 7/30d, spend and frequency per New/Engaged/Existing. Run `engaged_share_check {new_spend, engaged_spend, existing_spend, existing_freq_7d, daily_budget}`. Status `ACT` → propose a Retargeting breakout (build via `fb-launch`). `WATCH` → note that the share moves opposite to budget changes; more spend, not more creative, lowers it. `STARVED` → validate the segment lists with a $5/day retargeting test before changing anything (SOP §5.7). Retention spending on New usually means a mislabeled list (Shopify "boost" lists are lookalikes).
2. **Frequency:** for each campaign type and window (7/14/30d), run `frequency_check {audience, window_days, frequency, above_target}`. Follow its `action`. For example, retargeting above 15 over 30d → cut ~20% and move the cash to prospecting.
3. **Retention budget:** `retention_budget {prospecting_daily, retention_daily}`.
4. **Learning phase:** read the account-overview "% spend in learning (7d)" from the buyer or the UI, then run `learning_phase_check`.
5. **Catalog:** if catalog ads in prospecting spend mostly on Engaged, leave them. If they spend mostly on New or hog the CBO, propose a New-only catalog pack plus a one-ad-set retargeting catalog campaign at $5–10/day (SOP §5.8). Retention dead on a big catalog → propose rebuilding Retention as catalog ads.
6. **Retargeting** (if broken out): never add ad sets. Inject new objection ads/winners into the existing ones. Raise its budget only if well above goal and 7-day frequency isn't near 15–20.

## Mode C: "Performance dropped": diagnosis (SOP §8.3)

1. Confirm it's a real drop: results down ≥20–30% beyond normal noise, on 7d vs the prior 7d (or month vs month).
2. Pull both periods at campaign level: CPM, CPC, cost per ATC, cost per IC, CPA, AOV, CVR, on standard **and** incremental attribution. Run `drop_diagnosis {prev:{...}, curr:{...}}`. Say where the funnel first broke and what to check (`look_at`). Then run `funnel_health {atc, ic, purchases, sessions, aov}` on the current period: about 50% per step is normal, and site CVR around 1.2–1.5% at a ~$70 AOV.
   - Ask what changed on the site (collections removed, prices, checkout apps). A client-side change gets reverted and tested for 7–14 days before any budget cut.
3. **Where did spend move?** Ad-level spend share for both periods, sorted by the change. Then breakdowns one at a time: age, gender, placement (`publisher_platform`, `platform_position`), country.
4. Check the Shopify funnel for the same periods if the Shopify MCP is connected (sessions → ATC → checkout → orders). If the site funnel moved, the fix isn't in Ads Manager.
5. Fix options, in order:
   - creative or landing-page fix where the funnel broke
   - **value rule** on the segment that grabbed spend (start about −25–30%, never past 50%; check with `value_rule_effect`)
   - **max %** on the ad set that grabbed spend
   - never a rebuild

## Mode D: Monthly deep dives

- **Pixel gut check** → `pixel_check` (SOP §4.2).
- **Placements:** last 14 days, all campaigns, breakdown placement → `placement_check {spend_by_placement}`. A missing core placement → brief the missing creative (9:16 video) first, then test exclusions in ONE new ad set with a min of 1× CPA for at least 1 week.
- **Geo:** country breakdown → `geo_check {cpp_by_country, account_cpp}`. Remove outliers from that ad set's targeting. Add a new country only as a new pack of winners (≥7 days without a minimum, then 7 days with min = average CPA). Messy many-country accounts: `pareto_cut {revenue_by_item}` → keep the ~80% revenue countries, relaunch smaller. The same function works for products and categories.
- **Value rules:** for any segment (age, gender, OS, location, placement) clearly worse and spending heavily, propose a rule set (Advertiser settings → Value rules) starting at no more than −25%. Ignore gaps of 5–10%.
- **Day of week:** pull the longest Monday→Sunday range by day (spend, purchases, value), compute CPA and ROAS per weekday, and pick the strong days. Then run `dow_budgets {base_daily, up_days, up_pct}` so the week stays flat. Change budgets manually, or with automated rules (once daily, prospecting only, max cap, matching down rule).
- **Max conversions vs max value:** if one cheap SKU takes most of the spend (e.g. 87%) or AOV varies a lot, propose a parallel max-value CBO from the top ads. Compare CPA, ROAS and AOV, and never judge it on CPA alone (SOP §8.9).
- **Cost caps** (only if the account uses them): `cost_cap_action {tcpa_hit, budget_fully_spent, current_cap, target_cpa, monthly_spend, budget_utilisation}`. ~80% of budget spent = working; don't tweak it.
- **Opportunity score / Meta recommendations:** ignore them. They don't affect the auction, and "combine packs" or AI-creative suggestions break the system.
- **Overspend by Meta** (budget or cap ignored during an outage): run the refund playbook (SOP §4.4) and draft the support message for the buyer.
- **Free shipping:** last 100 orders above/below the threshold. Target ~75% qualifying (SOP §8.10).

## Output: optimization report

```
OPTIMIZE: <account> · <date> · King Goal CPA $45
ANOMALIES (20%): spend yesterday vs 30d −38% · ROAS flat · CPC/CTR/CPM flat → structural (sale ended?)
MINIMUMS: pack7 day 8 → REMOVE (spending $210 vs $45 min = winner) · pack8 day 3 keep
SEGMENTS: new 71% / engaged 22% / existing 7% · existing freq7d 9 → tighten retention
FREQUENCY: retargeting 30d 18 → cut 20% ($90→$72), move $18 to prospecting
DROP DIAGNOSIS: first break cost_per_ic +60% → check checkout changes
PROPOSED (needs approval): 1) remove pack7 min 2) retargeting $90→$72 3) prospecting +$18
```
