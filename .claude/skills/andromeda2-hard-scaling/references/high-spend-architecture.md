# High-spend architecture and cost-control operating manual

Sources: *The Facebook Ads Blueprint* 2026 (Cost Controls, Learning Phase, Value Rules, Max Value, Attribution, Placements,
Day of Week; the teacher managed BarkBox at $10k+/day with peaks over $100k/day) and its 2026 live calls (bid cap vs cost
cap, caps vs highest volume, value rules by country/age, $2-3M/month creative volume); Matteo Pellegrini 2026 (scaling CBO by
angle/avatar, bid-cap and cost-cap campaigns, zombie); Fernando Oliver (change-rate limit, payment processing); Telehealth
bonus (efficiency ceiling). Architecture tables are starting points to adapt, not fixed prescriptions.

Contents
1. Bid strategies in one table
2. Architecture blueprints
3. Cost-cap operating manual
4. ROAS goal operating manual
5. Bid-cap operating manual
6. Migrating from highest volume to caps
7. Value rules recipes
8. Attribution at scale
9. Operating cadence
10. Risk controls and the refund playbook
11. Troubleshooting

---

## 1. Bid strategies in one table

| Strategy | What Meta controls for | Spend behaviour | Use it for |
|---|---|---|---|
| Highest volume | Most conversions for the budget | Spends ~100% of budget; CPA floats | The creative-discovery engine; most accounts below $50k/month |
| Cost cap (cost per result goal) | **Average** CPA ≈ cap over ~7 days (some conversions above, some below) | Flat CPA, variable spend; healthy ≈ 80% of budget | Scaling proven winners at a fixed price; the default control at scale |
| ROAS goal (maximize value) | Average ROAS ≥ goal | Same as cost cap | Mixed AOV, bundles, subscriptions |
| Bid cap | **Maximum bid** per auction | Often far under budget; spends in full only when it can win profitably | Controlled scaling of the very best winners (advanced); zombie campaign at break-even |

"Caps of any sort will always win on efficiency… they will not win on volume." "Cost caps are the most effective for
e-commerce today… bid caps, you got to be an extremely advanced operator."

## 2. Architecture blueprints

### ~$50k/day (≈ $1.5M/month) — Mode A, hybrid

| Campaign | Bid | Role | Notes |
|---|---|---|---|
| Prospecting CBO — core | Highest volume | New concepts and iterations as packs; most new-customer volume | Exclude purchasers + customer list; 100+ ad sets is normal |
| Prospecting CBO — max value (if AOV varies) | Highest value | Pulls higher-AOV orders | Top ads per product |
| Scale CBO — cost cap | Cost cap = true target CPA | Proven winners (post IDs), ad sets by angle or avatar (Pellegrini) | Budget = expected ÷ 0.8 |
| Scale CBO — bid cap (optional, advanced) | Bid cap at target, inflated budget | 1-5 home-run winners, controlled scaling | One ad set per bid rung |
| Zombie CBO | Bid cap = break-even CPA | Fatigued winners, duds, hogs, organic | ~5% of spend plausible |
| Retention CBO | Highest volume | Existing customers | ≤ 10% of prospecting; frequency-managed |
| Catalog retargeting | Highest volume | Viewed/carted 14 days | $ small; frequency-managed |
| Sale campaign(s) | Highest volume or cost cap | Time-bound promos | Lifetime budget for the window |

### ~$150k/day (≈ $4.5M/month) — Mode B emerging
- Cost-capped CBOs carry the majority, split by **country cohort** (core English markets vs rest of world) and by **margin
  tier**; each with its own cap.
- A highest-volume discovery CBO (smaller share) launches the weekly creative packs; promote winners into the capped CBOs.
- Value rules by country and age; incremental attribution as the optimisation model on prospecting if social following/spend
  justify it (bid-cap campaigns stay Standard).
- Creative: ~100-150 new ads a week, mostly iterations of the top 5-10.

### ~$500k/day — Mode B mature
- Several capped campaigns per cohort, each managed by spend-through; day-of-week budget shaping (BarkBox spent 10-15x on its
  best days); a dedicated team per creative stream; the zombie layer holds most of the live ad count ("80% of the ads are in
  zombie, 20% of the ads are running most of the volume" at accounts with thousands of live ads).

## 3. Cost-cap operating manual

1. Prerequisite: ~$50-100k+/month at target with daily conversions. At $300-500/day "save yourself these 15 minutes".
2. **Cap = true target CPA** (profitable on first purchase, or on the LTV you deliberately underwrite). Never a "greedy" cap
   below target; if one was set, walk it up ($45 → $46 → $47, a few days each) or set it straight to the target.
3. **Budget = expected spend ÷ 0.8.** Goal: average ~80% spend-through. "When CPAs are being hit it spends more; when CPAs
   are not being hit it spends less."
4. Evaluate on the ~7-day lookback. Daily CPA will swing; the 7-day average should sit near the cap.
5. Diagnose with the 4 scenarios every 2-3 days (`a2.py cap-diagnose`). Scenario 1 (hit + fully spent) → raise budget, keep
   cap. Scenario 4 (hit, ~80%) → healthy; feed iterations. Scenario 2 (miss + fully spent) → data/creative problem; trim budget,
   iterate. Scenario 3 (miss + under-spent) → usually abandon caps for that campaign; make new creative.
6. Lowering a cap to squeeze efficiency: only by $1-2, only deliberately. "I always want to scale brands. Think about your
   contribution margin."
7. Small brands with caps often get the worst of both: erratic CPA, erratic spend, and conversions harvested from existing
   customers. Don't.

## 4. ROAS goal operating manual

Same rules as cost caps with the target ROAS: goal = true target on the attribution you judge on; budget ÷ 0.8; 4-scenario
diagnosis with the inequality reversed (hit = ROAS ≥ goal). Pair with maximize value in accounts with varied AOV. Pass LTV as
the purchase value for subscriptions where possible.

## 5. Bid-cap operating manual (advanced)

- A bid cap limits what Meta bids per auction, not what you pay on average; you usually pay below the bid, and spend is
  governed by how many auctions you can win at that bid — so budgets are deliberately inflated (2-5x expected spend) and
  under-delivery is normal. (Mechanics described from general practice; the sources give no numeric bid-setting procedure
  beyond: zombie bid = break-even CPA; "inflated, normal bid cap" for top winners in Pellegrini's structure.)
- Start the bid at the target CPA (break-even for zombie). Test rungs (e.g. 0.85x / 1x / 1.2x of target) as separate ad sets
  on the same proven creative; keep the rung that delivers volume at target over 3-7 days.
- Standard attribution only (incremental cannot be used with bid caps).
- Exclude retargeting and retention audiences; proven creative only; never as an A/B test against highest volume.

## 6. Migrating from highest volume to caps

- Don't flip a working highest-volume campaign to a cap in place. Build the capped campaign beside it with the top ads (post
  IDs) and a modest budget; let it prove scenario 4 for 7-14 days; then grow its budget.
- Expect bleed-over: capped campaigns "get even more efficient" next to highest volume because impressions from highest volume
  trickle into their conversions. Judge the account on MER and incremental new-customer ROAS, not on which campaign looks best.
- Keep at least one highest-volume engine for creative discovery; caps don't find new pockets well.

## 7. Value rules recipes

| Situation | Rule |
|---|---|
| One market clearly more valuable (US vs others) | +25% on the best country, or minus on break-even countries |
| Seasonal regression in a market (UK in summer) | −20% for a few weeks, then revisit |
| Age group clearly unprofitable (65+) | −25% first, deeper only if certain |
| A creator/ad that fails with one age group | Own ad set (post ID) + −30-40% on that age |
| Placement proven poor | Negative value rule on that placement after a 1-week test ad set without it |
Start ≤ 25%; "an elimination game, not an increasing game"; don't bother for 5-10% differences. Value rules don't reset learning.

## 8. Attribution at scale

- Optimisation model: Standard 7-day click + 1-day view by default; Incremental for very large spenders (~$100-300k+/month) or
  brands with 100-200k+ engaged followers. One setting per lane; never mixed inside a campaign; don't flip-flop.
- Reporting: always compare 7-day click and incremental columns; incremental by audience segment is the scaling gauge.
- Third-party click-only tools (Hyros etc.) undercount view and engaged effects; don't kill high spenders on them —
  "deleting negative ads is usually a race to zero."

## 9. Operating cadence

| When | What |
|---|---|
| Daily (fixed time) | Anomaly scan: spend, CPA, ROAS, CPM, CTR vs 1d / 3d / 7d and 30-day average, flag ≥ 20% (30-40% for big swings); spend pacing per capped campaign; sale-campaign moves |
| Every 2-3 days | `cap-diagnose` per capped campaign; one move each at most |
| Weekly | New creative packs live (Monday); MER and incremental by segment; frequency by segment; value-rule review; promote winners into caps; zombie feed |
| Monthly | Pixel gut check (server ≈ store orders, EMQ); day-of-week report; geo review; payment-processor limits and reserves |

## 10. Risk controls and the refund playbook

- Change-rate limit: avoid changing more than ~20% of account spend in any 3-day window (older heuristic, still sensible at scale).
- Payment processing: know hard vs soft monthly limits and reserves before a scaling push; a hard limit can take sales to zero.
- Backup: some large brands keep a second ad account hard-capped (e.g. $1,000/day) for emergencies; don't scale through a second account.
- Overspend/glitch refunds: screenshot set budget vs actual spend, ad account ID, campaign names, transaction/payment IDs; only
  system glitches qualify. Contact the rep or support → "Claim refund for ad spend" → ad account → "Other ad issue". Opening:
  "My campaigns overspent their budgets and seemed to ignore their cost caps yesterday, causing campaigns to spend very
  inefficiently and more than expected." Attach the Meta status page; give a realistic loss estimate; persist.

## 11. Troubleshooting

| Symptom | Cause | Move |
|---|---|---|
| Capped campaign spends 20-30% of budget | Cap tight or creative weak | If cap < true target, walk it up; else feed iterations; check AOV/LTV changed |
| Capped campaign spends 100% and CPA above cap | Too little signal/creative | Trim budget, iterate; consider highest volume instead |
| Caps look amazing, MER flat | Bottom-feeding engaged/existing or bleed-over | Exclusions; judge on MER and incremental new-segment |
| Volume collapsed after moving winners into caps | Caps cut volume | Keep winners in highest volume too; caps are additive |
| CPA spike at a new spend tier | Efficiency ceiling | Hold the tier, ship creative, retry the step later |
| Spend shifted to a cheap SKU | Max conversions with mixed AOV | ROAS-goal / max-value campaign |
