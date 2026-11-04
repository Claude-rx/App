---
name: fb-scale
description: Scale Meta ad accounts exactly per the media-buying SOP (The Facebook Ads Blueprint). Vertical scaling of the prospecting CBO with the 5 checks (King Goal, above target on 14/7/3-day windows, New audience segment, incremental attribution, stability) and the move sizes (10-30% every 48-72h, 10-15% at large spend, bigger near $100/day, double when smashing ≥2x with the delta check); twin engine (creative always on); horizontal scaling only for sales, margin tiers or a 1-3 ad scale campaign; cost controls only at $50k+/month; sale-period scaling. Proposes budget moves for approval. Use when: "scale", "increase budget", "can I spend more", "we're above target", "double the budget", "should I make a scale campaign", "horizontal scaling", "cost cap", "scale for Black Friday".
---

# fb-scale: scale per the SOP

Rulebook: **`docs/media-buying/SOP.md` §9** (plus §5.9 and §6.1). Engine:

```bash
echo '<json>' | python3 tools/fb-blueprint/blueprint.py <command>
```

## Safety contract

- **Budget changes are proposals.** Show the old and new budget, the step %, and the engine's `why`. Apply with `ads_update_entity` (`daily_budget` in **cents**) only after an explicit yes, then read it back.
- Scale the **prospecting CBO**. Retargeting and retention are managed by frequency (`fb-optimize`), not by these steps.
- Never duplicate the CBO with the same ads "for more spend". Never build a new campaign that competes with the main one.
- Same `client_conversation_id` on every Meta call.

## Step 1: Inputs

- King Goal (type and target). Without it, stop (SOP §3.3).
- The prospecting CBO's current daily budget, and the time of the last budget change. Read it with `ads_account_get_activity_logs`, filtering budget changes, and compute `hours_since_last_change`.
- King Goal metric for **14d, 7d, 3d and yesterday** (`ads_get_ad_entities` level campaign, one call per `date_preset`: last_14d, last_7d, last_3d, yesterday).
- **New**-segment incremental ROAS or CPA, last 7d: breakdown by audience segment plus `action_attribution_windows ["incrementality"]`.
- Average daily revenue over the last 7d (for the smashing delta check).
- Blended business view: store revenue ÷ total ad spend (MER) if the Shopify MCP is connected. Report it next to the platform numbers.

## Step 2: Vertical decision (SOP §9.1)

```json
vertical_scale {"ctx": {"kpi_type":"roas|cpa","kpi_target":..,"daily_budget":..,"hours_since_last_change":..,
                        "kpi_by_window":{"14":..,"7":..,"3":..,"1":..},
                        "new_incremental_kpi":..,"revenue_7d_daily_avg":..}}
```

- `INCREASE`: propose `new_daily_budget`. Remind the buyer what to expect: frequency, CPM and CPC up, ROAS down short-term. Hold if cost per ATC stays flat.
- `DOUBLE`: smashing, and the delta check passed. Propose doubling. Never jump like $100 → $500.
- `WAIT`: inside 48–72 h. State the next check time.
- `HOLD`: below target or unstable. Do not raise. Hand creative work to `fb-test` (iterations of winners); twin engine.

If ROAS has slid during steady weekly increases, propose pausing the increases and letting it settle. If the account is recovering a previous spend level, doubling steps (500 → 1,000 → 2,000 → 3,000) are allowed, judged on incremental (SOP §9.1).

## Step 3: Twin engine check (SOP §9.3)

Always pair the budget decision with the creative plan: `ads_per_week {monthly_spend}` at the **new** spend level. Report whether the creative pipeline keeps up. Creative output never pauses, whether above or below goal.

## Step 4: Horizontal (only on request or a trigger, SOP §9.2)

`horizontal_readiness {daily_spend, reason}`, where reason is `sale`, `margin_tier` or `scale_campaign`.
- **Internal horizontal is always allowed:** iterate winning angles, expand winning avatars, add interest packs (hand off to `fb-launch`).
- **Scale campaign:** only for 1–3 home runs that are top-10% spenders and above target on incremental (`graduation` in `fb-test`). Duplicates only; the originals stay. CBO, no ad set limits, exclude everything targeted elsewhere.
- **Dominant ad below KPI:** propose a max % on its pack (e.g. 80% → 60%), not a scale campaign.

## Step 5: Cost controls (SOP §9.4)

Only when monthly spend is at least ~$50k. Use cost cap = **real** target CPA, with the budget sized so spend averages about 80% of it. Then decide with `cost_cap_action`. Bid caps are for very advanced operators only.

## Step 6: Sale scaling (SOP §9.5)

Judge against the **sale** KPI. Big upward jumps are allowed, intraday +10–20% and several raises a day. Avoid repeated cuts. After the sale, don't pause evergreen ads on the post-sale dip.

## Output: scale log

```
SCALE: <account> · prospecting CBO · King Goal ROAS 2.5
Windows: 14d 2.9 · 7d 3.1 · 3d 3.0 · yday 2.6 · New iROAS 2.4 · MER 3.4
Last move 70h ago · budget $1,200/day
Decision: INCREASE +22% → $1,464/day (band 10–30%, scaled by distance above goal)
Expect: CPM/CPC/frequency up, ROAS dip; hold if cost/ATC flat
Creative: at $44k/mo → 5 new ads/week (calculator) · pipeline: 6 ready ✓
Apply? (yes / edit)
```
