---
name: fb-test
description: Judge Meta ad tests exactly per the media-buying SOP (The Facebook Ads Blueprint). Applies the judgment window (7 vs 14 days), the 13-question pausing tree (2x / 3x target CPA gates, within-50%-of-KPI, mid-funnel leading indicators, cap-instead-of-pause), graduation (top 10% spend AND incremental ROAS over baseline), daily breakout winners (launched ≤30d, ≥10% of spend, ROAS above account average), Shotgun & Sniper kill switches and the zombie campaign, then proposes pauses, caps and graduations for approval. Use when: "which ads should I pause", "judge this week's pack", "find winners", "graduate winners", "kill losers", "breakout winners report", "creative test results", "should I turn this ad off".
---

# fb-test: judge tests per the SOP

Rulebook: **`docs/media-buying/SOP.md` §7** (plus §6.3 and §6.7). Every decision comes from the engine:

```bash
echo '<json>' | python3 tools/fb-blueprint/blueprint.py <command>
```

## Safety contract

- Read freely. **Pausing, capping, duplicating and moving ads are proposals** until the user says yes; then apply them with `ads_update_entity` / `ads_create_ad`.
- **Never pause an ad that hits KPI. Never pause on a window shorter than 7 days. Never pause a high spender while the account is at target.** Instead, cap its pack with a max %. (SOP §7.3)
- Turn off **ads, not packs.** Kill a whole pack only if it goes 0-for-5 or it's a sale pack.
- Never move ads between live ad sets (it resets learning). The only exception is moving them into the zombie campaign.
- Same `client_conversation_id` on every Meta call.

## Step 0: Inputs

King Goal (type and target), target CPA, and average daily spend of the prospecting CBO. If unknown, ask, or read the account brief that `fb-launch` wrote.

## Step 1: Window

`judgment_window {avg_daily_spend}` → 7 or 14 days. Only judge ads with at least that much data. Always pull **14d, 7d, 3d and yesterday** and read them in that order.

## Step 2: Pull the data (Meta Ads MCP)

`ads_get_ad_entities`, level `ad`, prospecting campaign, `date_preset` matching the window. Verify the field names first with `ads_get_field_context`. Fields:
- spend, purchases, cost per purchase, purchase ROAS, ATC, cost per ATC, initiate checkout, cost per IC, CTR, CPC, CPM, frequency, created time
- `action_attribution_windows: ["default","7d_click","incrementality"]`

Also pull the campaign-level averages: cost per IC, CPC, CTR, CPM. Read every `next_actions` the tool returns.

## Step 3: Pausing tree, per ad (SOP §7.3)

For each ad with enough data, run:

```json
pause_decision {"ad": {"spend":..,"purchases":..,"atc":..,"ic":..,"cost_per_ic":..,"kpi_actual":..,
                        "viral": <CPM/CTR wildly off the account average>, "wrong_demographic": <from breakdown>},
                "ctx": {"kpi_type":"roas|cpa","kpi_target":..,"target_cpa":..,"avg_cost_per_ic":..,
                        "post_event": <post-sale/holiday?>, "pixel_ok": <last gut check>, "window_days":..}}
```

- `viral`: CPM, CTR or CPC wildly different from the account (course example: account 1.3% CTR / $5.81 CPM; ad ~5% CTR / ~$1 CPM).
- `wrong_demographic`: run `ads_get_ad_entities` with breakdowns `age`, `gender`, `publisher_platform`/`platform_position`, `country` on the ad. Flag it when spend sits in an unexpected cohort.
- `kpi_actual`: read on the account's standard attribution. Also report 7-day-click and incremental values (question 6).

Map the results:
- `PAUSE` → propose pausing the **ad**.
- `CAP_ADSET` → propose a max spend % on its pack (`ads_update_entity` with the ad set's daily max spend; e.g. 90% → about 20%).
- `KEEP` / `WAIT` → no action; say when to re-check.
- `FIX_TRACKING` → stop and hand off to the `fb-launch` pixel check.

**Overrides from the course, applied after the tree:**
- An ad that takes a large share of spend while the account hits target → **don't pause** even if the tree says PAUSE. Check its cost per ATC/IC and incremental ROAS. If it truly lags, cap the pack at about 50% and evaluate over 2 weeks.
- Ads spending under ~$50/month are funnel support. Don't kill them for noisy ROAS.
- Packs whose minimum just ended: spending **above** the minimum = winner. Stuck **at** the minimum = it will die. Propose dud ads stuck at $2–3/day for the zombie campaign if one exists (SOP §7.7).

## Step 4: Graduation (weekly, SOP §7.4)

`graduation {"ads": [{"name","spend","incremental_roas"}...], "incremental_roas_baseline": <business baseline>}`

If the baseline is unknown, ask. The course example is 1.2, and it is business-specific. For each winner, propose:
1. Duplicate it into the interest packs (`interest_[x]_winners`; create one via `fb-launch` if none exist). If an interest pack is on fire, duplicate the pack instead of adding ads.
2. Duplicate it into Retention (and Retargeting if it exists).
3. Scale only for 1–3 home runs (hand off to `fb-scale`).

The originals always keep running.

## Step 5: Breakout winners (daily, SOP §7.5)

Pull 7, 14 and 30-day windows: account spend + account ROAS, and per-ad spend, ROAS and created time. Then run:

```json
breakout_winners {"windows": {"7": {"account_spend":..,"account_roas":..,"ads":[{"id","name","spend","roas"}]}, "14": {...}, "30": {...}},
                  "today_age_days": {"<ad_id>": <days since created>}}
```

Output one short message: the date, then per winner: name, top spend share, ROAS, and an Ads Manager link. If there are none, say "No new breakout winners today." Then draft an **iteration brief** for each winner (SOP §6.7):
- same concept and hook, plus new hooks, voiceovers, statics, landing pages, splices
- 1–6 iterations, changing one layer at a time

## Step 6: Shotgun & Sniper (only if the account runs it, SOP §7.6)

1. `shotgun_targets {cost_per_atc, cost_per_ic, cost_per_purchase, aov}` from account averages, on the attribution you judge on.
2. Daily: `shotgun_kill {adset, targets, days_live}` per ad set.
3. Never automate the kill switches with Meta rules.
4. Survivors after 7 days: propose ABO→CBO, or +25%/day while the targets hold.

Before anything else, check the precondition: dozens of new creatives or products every week. If it isn't met, recommend the core CBO packs instead.

## Output: test report

```
TEST REPORT: <account> · window 14d (spend $640/day) · King Goal ROAS 2.2
PAUSE (2): ad "X" Q13: spent $162 ≥ 3×CPA $150, ROAS 0.6 vs 2.2 · ad "Y" Q11: $104, 0 purchases, no IC
CAP (1):   pack "momUGC_pack5" Q8 viral: CTR 5.1% vs 1.3% → max 20%
KEEP (14) / WAIT (6): next read <date>
GRADUATE (1): "Z" top-10% spend, iROAS 1.6 ≥ 1.2 → interest_yoga_winners + retention
BREAKOUT: "Z" 14% spend, ROAS 3.1 vs 2.4 → iteration brief attached
Proposed changes need approval: reply "apply" or edit the list.
```
