---
name: andromeda2-hard-scaling
description: Hard scaling Meta (Facebook/Instagram) ads at $50k+/day ($1.5M+/month) in the Andromeda 2 era with cost caps, bid caps, ROAS goals and value rules — caps set at the true target CPA with budgets sized for ~80% spend-through, the 4-scenario cost-cap diagnosis (raise budget, change the cap, or ship creative), multi-campaign architecture for big accounts, incremental-attribution optimisation, placement and day-of-week shaping, 100+ new ads a week and risk controls. Use this whenever the user mentions cost caps, cost per result goal, bid caps, ROAS goal or minimum ROAS, value rules, a capped campaign that won't spend or misses its cap, spending $50k, $100k or $1M+ a day or month, or how the biggest brands structure accounts at that spend. Prefer this over generic bidding or scaling skills for Meta. Below ~$50k/month use andromeda2-scaling; for reviving dead ads in a bid cap use andromeda2-zombie-campaigns.
---

# Hard scaling — $50k+/day with cost controls

At this spend the job changes: you are no longer finding whether the account works, you are buying the maximum number of
customers at a controlled price every day, across many campaigns, with creative volume measured in hundreds per week.
Cost controls become the steering wheel. "Most gigantic accounts — $2 million budgets plus — basically all of them are
managed in cost caps." (Blueprint)

Why it fits Andromeda 2: at this volume the ranking/retrieval stack has abundant conversion signal, so an average-cost target
(cost cap) or a per-auction ceiling (bid cap) can be honoured; the system "spends more when CPAs are being hit, less when not".
Below that signal level caps give "two variable elements — nothing is forecastable" and often bottom-feed existing customers.

## Before you start

1. Read `references/andromeda2-doctrine.md`, `references/metrics-and-diagnosis.md` and `references/high-spend-architecture.md`.
2. Confirm fit — all should be true, otherwise use `andromeda2-scaling`:
   - The account already spends ≥ ~$50-100k/month **at target** with conversions every day (cost caps evaluate on a ~7-day
     lookback and need "a massive amount of data flowing in to support that cap").
   - There is a profit model: true target CPA (first purchase or underwritten LTV), break-even CPA, target ROAS, MER goal.
   - Tracking is clean (server purchases ≈ store orders, EMQ ≥ 8.4) and audience segments are set up.
3. Gather: campaign list with bid strategy, daily budget, 7-day average spend and 7-day CPA/ROAS per campaign; account MER;
   new/engaged/existing split; incremental vs standard; creative output per week; margin tiers; markets.

## Workflow

### 1. Choose the operating mode
- **Mode A — hybrid (entering $50k/day):** highest-volume prospecting CBO(s) remain the engine and creative proving ground;
  proven winners also run in cost-capped CBO(s) at the true target CPA (and a ROAS-goal CBO if AOV varies); a bid-cap zombie
  layer; retention and catalog retargeting by frequency.
- **Mode B — cost-cap-led (mature, ~$1.5-2M+/month, daily conversions in the hundreds):** most spend sits in cost-capped CBOs
  at the true target CPA with inflated budgets, managed by spend-through; a smaller highest-volume CBO keeps discovering new
  concepts; same zombie and retention layers.
Explain the choice from the data (conversion volume per day, stability of CPA, creative output).

### 2. Set every cost control from the profit model, not by feel
Run `python3 scripts/a2.py cost-controls --expected-spend <$/day for that campaign> --target-cpa <true target> [--target-roas <true target>] --monthly-spend <account>`.
- **Cost cap / cost per result goal = the true target CPA.** "Don't try to game the system and squeeze a couple dollars out."
  Budget = expected spend ÷ 0.8 so the cap — not the budget — limits delivery; healthy = ~80% average spend-through (good days
  ≥ 100%, bad days ≤ 50%).
- **ROAS goal (maximize value)** = the true target ROAS on the attribution you judge on; same budget rule. "Quite successful
  in recent months."
- **Bid cap** (per-auction ceiling) = advanced operators only. Two uses: (1) Pellegrini's controlled-scaling campaign for the
  very best winners — normal bid at target, inflated budget (2-5x expected spend), one ad set per bid rung; (2) the zombie
  campaign at break-even CPA (`andromeda2-zombie-campaigns`). Bid caps force Standard attribution.
- Margin tiers / countries with different economics → separate ad sets or campaigns, each with its own cap.
- Keep caps away from retargeting and retention audiences (exclude them 100%), and never "test" caps against highest volume —
  caps always win on efficiency and lose on volume, and look even better by bottom-feeding impressions highest volume created.

### 3. Run the 4-scenario diagnosis every 2-3 days per capped campaign
`python3 scripts/a2.py cap-diagnose --cap <cap> --actual <7d CPA> --budget <budget> --avg-spend <7d avg spend> [--true-target <T>]`

| Target hit? | Budget spent in full? | Move |
|---|---|---|
| Yes | Yes | **Raise the budget**, keep the cap, until spend-through falls back to ~80%. (Tightening the cap $1-2 is the only alternative.) |
| Yes | No (~80%) | Working as designed. Leave it; grow volume with iterations of the winners. |
| Yes | No, and cap below true target | Walk the cap up to the true target (small steps) or set it there. |
| No | Yes | Cap not honoured: question whether this campaign has the data for caps; trim budget; iterate the creative that has signal. |
| No | No | Double bad: usually switch the campaign back to highest volume; the real fix is new creative. |

A $1 move (~2%) can open or close a lot of inventory. Never edit cap and budget on the same day; one change per campaign per
48-72 h; judge on 7 days.

### 4. Scale budgets inside the caps
Capped campaigns can take large budget increases because the cap protects efficiency — raise budgets when scenario 1 appears.
Highest-volume campaigns follow `andromeda2-scaling` rules (10-15% steps on big tight campaigns; bigger only when far above target).
Watch MER and incremental ROAS by new-customer segment; Meta-reported efficiency inside caps flatters itself.

### 5. Feed the machine (creative is still the constraint)
Cost-cap scenarios 2-4 all end in "make or iterate creative". At $2-3M/month expect ~100-150 new creatives a week, mostly
iterations of the top 5-10 ads that carry 60-70% of spend, plus a steady stream of new concepts in the highest-volume engine.
Use `andromeda2-creative-iteration`; ship to the highest-volume engine first, promote proven ads (post ID) into capped campaigns.

### 6. Shape delivery with the advanced levers
- **Value rules**: big data-proven gaps only; start ≤ 25%; countries (+25% best market / minus break-even markets), weak ages
  (−30-40%), placements, seasonal dips (−20%).
- **Incremental attribution as the optimisation model** for very big spenders (~$100-300k+/month) or brands with huge
  engaged followings; the whole prospecting lane on one setting; never mixed inside a campaign.
- **Placements**: the top six (FB/IG Feed, Stories, Reels) should carry spend; at $100k+/month consider Reels + Feed only for
  capped/zombie campaigns so they don't "take credit for Audience Network, Messenger".
- **Day-of-week**: shift budget toward the strongest weekdays with correct maths (BarkBox spent 10-15x on its two best days).
- **Country cohorts**: split very large cohorts (core English markets vs rest of world) into their own campaigns.

### 7. Operate with risk controls
Daily anomaly scan (spend, CPA, ROAS, CPM, CTR; flag ≥ 20% moves; 1v1, 3v3, 7v7 and vs 30-day average), weekly MER + incremental
review, monthly pixel gut check. Keep total changes under ~20% of account spend in any 3-day window. Track payment-processor
limits and reserves. If Meta overspends or ignores caps through a glitch, file a refund claim with screenshots (playbook in
`references/high-spend-architecture.md`).

## Output format

Save to `ads/<brand-slug>/hard-scaling-plan-<YYYY-MM-DD>.md` and summarise in chat.

```markdown
# Hard-scaling plan — <brand> — <date>
## Economics       (true target CPA, break-even CPA, target ROAS, MER goal — from a2 economics)
## Mode            (A hybrid / B cost-cap-led, with the data that decides it)
## Architecture    (table: campaign · role · bid strategy & value · budget · expected spend · audience/exclusions · placements · creative source)
## Cost-control settings  (a2 cost-controls output per campaign)
## Diagnosis now   (a2 cap-diagnose per capped campaign → scenario → move)
## 14-day budget path (table: day · campaign · budget · trigger to proceed / stop)
## Creative engine (per week: iterations on which winners, new concepts, promotion rule into caps)
## Advanced levers (value rules, attribution model, placements, DOW, cohorts — only those justified by data)
## Operating cadence & risk controls (daily / every 3 days / weekly / monthly checklist, alert thresholds in $ and %)
```

## Quality bar

- Every cap equals the true target (or break-even for zombie bid caps) and every capped budget is sized for ~80% spend-through.
- No caps on retargeting/retention audiences; no caps-vs-highest-volume "tests".
- Each capped campaign has a scenario diagnosis and a specific next move; one change per campaign per 48-72 h.
- The plan names the creative volume that the budget path requires.
- MER and incremental new-segment ROAS are tracked alongside Meta-reported numbers.

## References

- `references/high-spend-architecture.md` — architecture blueprints for $50k, $150k and $500k/day, cost-cap / ROAS-goal / bid-cap
  operating manual, migration from highest volume to caps, value rules recipes, the daily/weekly cadence, risk and refund
  playbook, troubleshooting.
- `references/metrics-and-diagnosis.md`, `references/andromeda2-doctrine.md`.
- `scripts/a2.py` — `economics`, `cost-controls`, `cap-diagnose`, `scale`, `analyze`, `zombie`.
- Siblings: `andromeda2-scaling`, `andromeda2-zombie-campaigns`, `andromeda2-creative-iteration`, `andromeda2-launch-testing`.
