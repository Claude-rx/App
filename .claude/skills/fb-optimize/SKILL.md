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
2. **Minimums:** list prospecting ad sets with a `daily_min_spend_target`. Any minimum past **7 days** → propose removing it (`ads_update_entity` with the ad set's min spend set to 0). Report each pack's verdict: spending **above** its minimum = winner; stuck **at** it = it will die (SOP §5.4).
3. **Tracking sanity:** Events Manager/dataset stats show purchases flowing. If they drop to 0 → urgent, hand off to the pixel check.
4. **Scale due?** If 48–72 h have passed since the last budget move, hand off to `fb-scale`.
5. Sale running? Apply the sale rules: faster kills on cost per ATC/IC, big upward jumps, no repeated cuts (SOP §9.5).

## Mode B: Weekly optimization

1. **Audience segments:** prospecting with breakdown `user_segment_key` (audience segments; verify the name with `ads_get_field_context`), last 7/30d, spend and frequency per New/Engaged/Existing. Run `engaged_share_check {new_spend, engaged_spend, existing_spend, existing_freq_7d}`. If a trigger fires, propose a Retargeting or Retention breakout and hand the build to `fb-launch` (SOP §5.6–5.7).
2. **Frequency:** for each campaign type and window (7/14/30d), run `frequency_check {audience, window_days, frequency, above_target}`. Follow its `action`. For example, retargeting above 15 over 30d → cut ~20% and move the cash to prospecting.
3. **Retention budget:** `retention_budget {prospecting_daily, retention_daily}`.
4. **Learning phase:** read the account-overview "% spend in learning (7d)" from the buyer or the UI, then run `learning_phase_check`.
5. **Catalog:** if catalog ads in prospecting spend mostly on Engaged, leave them. If they hog spend, propose a $5–10/day catalog retargeting campaign (SOP §5.8).

## Mode C: "Performance dropped": diagnosis (SOP §8.3)

1. Confirm it's a real drop: results down ≥20–30% beyond normal noise, on 7d vs the prior 7d (or month vs month).
2. Pull both periods at campaign level: CPM, CPC, cost per ATC, cost per IC, CPA, AOV, CVR, on standard **and** incremental attribution. Run `drop_diagnosis {prev:{...}, curr:{...}}`. Say where the funnel first broke and what to check (`look_at`).
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
- **Geo:** country breakdown → `geo_check {cpp_by_country, account_cpp}`. Remove outliers from that ad set's targeting. Add a new country only as a new pack of winners (≥7 days without a minimum, then 7 days with min = average CPA).
- **Value rules:** for any segment (age, gender, OS, location, placement) clearly worse and spending heavily, propose a rule set (Advertiser settings → Value rules) starting at no more than −25%. Ignore gaps of 5–10%.
- **Day of week:** pull the longest Monday→Sunday range by day (spend, purchases, value), compute CPA and ROAS per weekday, and pick the strong days. Then run `dow_budgets {base_daily, up_days, up_pct}` so the week stays flat. Change budgets manually, or with automated rules (once daily, prospecting only, max cap, matching down rule).
- **Max conversions vs max value:** if one cheap SKU takes most of the spend (e.g. 87%) or AOV varies a lot, propose a parallel max-value CBO from the top ads. Compare CPA, ROAS and AOV, and never judge it on CPA alone (SOP §8.9).
- **Cost caps** (only if the account uses them): `cost_cap_action {tcpa_hit, budget_fully_spent, current_cap, target_cpa, monthly_spend}`.
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
