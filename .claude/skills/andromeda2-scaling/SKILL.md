---
name: andromeda2-scaling
description: Scaling Meta (Facebook/Instagram) ad budgets profitably in the Andromeda 2 era with the Twin Engine method — vertical budget raises on the prospecting CBO when the King goal is beaten (move size by how far above target, 48-72 h cadence, doubling and delta-math rules) plus always-on creative expansion on winning angles and avatars so ROAS stays flat as spend climbs. Includes the pre-move checks (new-customer share, incremental ROAS, 14/7/3-day trend), what to expect after a raise and when to hold or cut, and day-of-week, value-rule, geo and frequency levers. Use this whenever the user asks how to scale Facebook ads, increase budget or spend more, grow from $X to $Y a day, why ROAS dropped after a budget increase, whether to duplicate a winning campaign or open a scale campaign, or how to get more volume without losing efficiency. Prefer this over generic scaling or campaign skills for Meta. For cost caps, bid caps and ROAS goals at $50k+/day use andromeda2-hard-scaling.
---

# Scaling under Andromeda 2 — the Twin Engine

Scaling is two engines running at once. **Vertical** = spend more on the vehicle that already works (the prospecting CBO)
whenever you are above the King goal. **Internal horizontal** = keep feeding that vehicle new executions of what works, so
efficiency stays flat against "the gravitational pull of more spend". "Vertical raises the ceiling. Horizontal stops the
floor from falling out." (Blueprint)

Why Andromeda 2 makes this the method: retrieval routes each ad to the sides of people it matches. More budget on the same
few ads pushes them into colder, less matched sides (rising frequency, CPM, CPA); new executions on the winning angles and
avatars give the system fresh, specific candidates for those new sides.

## Before you start

1. Read `references/andromeda2-doctrine.md`, `references/metrics-and-diagnosis.md` §3, §6-8, and `references/scaling-playbook.md`.
2. Gather: King goal (target CPA/ROAS — compute with `scripts/a2.py economics` if missing), current daily budget per campaign,
   ROAS/CPA for the last 14, 7 and 3 days and yesterday/today, conversions per day, date of the last budget change,
   Breakdown → Audience segments (new/engaged/existing spend and ROAS), the Incremental attribution column, blended MER from
   the store, frequency by segment, creative pipeline (new ads per week). An ad-level export lets you run `a2.py analyze`.
3. If the account is below target, the job is not scaling: "make money first" — route to `andromeda2-creative-iteration`
   (and `andromeda2-launch-testing` if the structure is wrong).

## Workflow

### 1. The five checks before any vertical move (Blueprint)
1. **King goal known** — one efficiency number from the profit model (blended). Everything else (CPM, CPC, ATC) is diagnosis.
2. **Above target?** If yes, the default is to spend more: "The goal is not to go above target. The goal is to extract every
   dollar of profit and build an army of customers." 4x on a 2.5x target is money left on the table.
3. **New customers carry it?** Breakdown → Audience segments. Extra spend returns roughly what the *new* segment returns, not
   the blended number. Engaged + existing must not be carrying the account.
4. **Incremental holds?** Compare → Incremental attribution. "The incremental new ROAS is what your next dollar will
   realistically return" (example blended 2.6 → incremental 1.73).
5. **Stable over time?** Look 14 days → 7 → last 3 → yesterday/today. Never scale (or cut) on yesterday alone.

### 2. Size and time the move
Run `python3 scripts/a2.py scale --budget <now> --kpi-3d <x> --kpi-7d <y> --kpi-14d <z> --target <King goal> [--metric cpa] --hours-since-change <h>`.
Rules it encodes:
- Default 10-30% every 48-72 h on the prospecting CBO; 10-15% on big, tight campaigns (multi-thousand $/day).
- Small budgets need bigger steps: $100 → $150 → $225 → $300 (10% does nothing).
- ~40%+ above target and stable → +50% is fine; the dip that follows is conversion lag on new impressions ("the learning phase
  is fake" — re-entering learning after a big jump is not the problem people think).
- "Smashing" (≥ 2x target) → double, bounded by delta math: even if the new dollars returned nothing, blended KPI stays ≥ target.
  Don't jump 5x ($100 → $500).
- At or just below target → hold the budget and push creative; 10-25% below for a week → trim 20%; worse → cut 30% and fix.
- Sale periods: bigger, faster moves (see the playbook); retargeting/retention are never scaled this way (frequency-managed).

### 3. Expect the after-effects (don't panic-cut)
After a raise: reach grows slower than impressions → frequency ↑, CPM ↑, CPC ↑, ROAS dips for a few days, because the extra
spend reaches people earlier in their journey who take longer to buy. Watch cost per ATC and cost per IC: **if cost per ATC is
flat while purchases lag, hold the line.** On a doubling, cost/ATC +3-15% and cost/IC +10-15% is normal; cost/ATC doubling is a
real problem. Cutting spend after 2 days and seeing ROAS "recover" is just harvesting the pipeline you already paid for.

### 4. Run internal horizontal every week (the second engine)
Never gated by performance — "the pipeline never stops."
- **Winning angles → more executions**: same angle, different executions (Gruns "better poops" → "poop more", "normal poops",
  "poop like you mean it"). Not headline swaps — distinct ads.
- **Winning avatars → their other problems**: GLP-1 users → hair loss, metabolism, digestion. One winning avatar opens several angles.
- **Interest suggestions**: a winners-only pack with one adjacent interest suggestion to push the pixel into a neighbouring pocket.
- Volume: `python3 scripts/a2.py testing-plan …` (1 new ad/week per $10k monthly spend; more iterations as spend grows; at
  $2-3M/month that is ~100-150 creatives a week, mostly iterations). Hand-off: `andromeda2-creative-iteration`.
- Healthy shape: 5-10 creatives taking 60-70% of spend is expected; iterate on them first.

### 5. Monitor the two numbers that tell you if scaling is real
1. **Incremental ROAS by audience segment, period over period.** Flat while spend rises → keep going. Falling → you are
   outrunning the creative: slow vertical until horizontal catches up.
2. **Blended business ROI (MER)** from the store. "Meta can look good while your blended picture deteriorates."
Also: new-audience frequency (≈ 6 on new customers = cannot scale there → new concepts/interest packs), engaged share
(20-25% healthy; mid-40s% investigate), placements (top six should carry spend; a gap = missing format).

### 6. External horizontal — only for real reasons
A new campaign beside the core only for: (a) sales/drops (lifetime-budget campaign for the window); (b) truly different
price points or businesses — first try a **max-value** CBO beside the max-conversions core; (c) an optional winners campaign of
1-5 home-run ads ("fuel on the fire, not the fire itself"). Not at $100/day; careful at $1,000/day. "Campaign number one
should look nothing like campaign number two" — duplicating the same winners into another campaign is just sloppy vertical
scaling. One ad account; no "fresh" duplicate campaigns as a reset.

### 7. Other levers (details in the playbook)
Day-of-week budget shaping on the prospecting CBO (correct maths: +50% and −50% don't cancel); value rules (≤ 25% first,
for big gaps by age, country, placement); max value vs max conversions for mixed AOV; geo expansion via winners-only country
packs; AOV levers (bundles, BOGO, free-shipping threshold near AOV) that raise the CPA you can afford and win more auctions.

## Output format

Save to `ads/<brand-slug>/scaling-plan-<YYYY-MM-DD>.md` and summarise in chat.

```markdown
# Scaling plan — <brand> — <date>
## Verdict      (one line: SCALE / HOLD / FIX FIRST, and why)
## The five checks   (table: check · value · pass/fail)
## Budget moves      (table: campaign · now · next · % · when · a2 rationale · delta-math ceiling)
## What to expect next 3-7 days   (metrics that will move and the hold-the-line thresholds in $)
## Creative engine   (this week: # iterations on which winners, # new concepts on which avatars, interest packs; owner; launch day)
## Monitoring        (incremental by segment, MER, frequency, engaged share — values now and alert levels)
## Other levers      (only those that apply: DOW, value rules, max value, geo, offer/AOV)
## Next review date
```

## Quality bar

- Every budget number comes from `a2.py scale` (or is explicitly justified as an override).
- The five checks are answered with numbers; incremental and new-segment figures are used, not only blended Meta ROAS.
- A creative plan accompanies every budget increase.
- No recommendation relies on one day; no new campaign without one of the three reasons.
- Retargeting/retention handled by frequency, not by budget scaling.

## References

- `references/scaling-playbook.md` — vertical procedure details, doubling/rebuild mode, sale scaling, day-of-week maths,
  value rules, max value migration, geo, inventory limits, efficiency ceilings, troubleshooting table, dated tactics to avoid.
- `references/metrics-and-diagnosis.md` — windows, frequency caps, attribution, funnel-drop procedure.
- `references/andromeda2-doctrine.md` — why concepts open pockets and iterations deepen them.
- `scripts/a2.py` — `scale`, `testing-plan`, `analyze`, `economics`.
- Siblings: `andromeda2-hard-scaling` (cost caps / bid caps / ROAS goals, $50k+/day), `andromeda2-creative-iteration`,
  `andromeda2-zombie-campaigns`.
