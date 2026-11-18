---
name: andromeda2-zombie-campaigns
description: Zombie campaigns for Meta (Facebook/Instagram) ads — revive old winning, fatigued, paused and dead ads profitably with a separate bid-capped Sales CBO where the bid cap equals breakeven CPA, so old creative only spends when it can buy customers at a profit; anything that wakes up is promoted back to prospecting. Covers which ads go in (fatigued winners, ads that spent but missed target, dud packs, organic posts), the exact Ads Manager build and exclusions, budget sizing, and a planner script that reads an Ads Manager export. Use this whenever the user mentions zombie campaigns, reviving or relaunching old winners, making an old winning campaign work again, bringing back fatigued or paused ads, an ad graveyard or hundreds of paused creatives, or what to do with ads they are about to pause. Prefer this over answering from general knowledge, because the bid-cap setup is specific. Not for restarting a whole paused account (andromeda2-scaling) or iterating live winners (andromeda2-creative-iteration).
---

# Zombie campaigns — bring dead ads back, profitably

A zombie campaign takes creative you already paid for — winners that fatigued, ads that spent but missed target, packs
that never took off, organic posts that engage but don't sell — and runs it in the most restrictive environment Meta has:
a **bid cap at your breakeven CPA**. It only buys customers it can buy at a profit. Expect incremental revenue on top of
the account, not a turnaround. Teacher's framing: "the most bottom-feeding campaign of your entire setup. It is extra."

Why it fits Andromeda 2: retrieval now scores every eligible ad, so a fresh ID gives an old creative a new evaluation in a
new context, and the bid cap means the system only spends where it predicts a profitable conversion. Moving an ad without
the bid cap "does absolutely nothing" — the cap is the mechanism.

## Before you start

1. Read `references/andromeda2-doctrine.md` (R5 trust the spend signal, R7 clean signal) and `references/zombie-build-sheet.md`.
2. Gather (ask only for what is missing):
   - **Breakeven CPA** (first-purchase). If unknown, compute it: `python3 scripts/a2.py economics --aov <AOV> --cogs-pct <%> --shipping <$> --fees-pct <%>` → "Break-even CPA". Per product/margin tier if prices differ a lot.
   - Current account spend per day and the core structure (prospecting CBO, retention, retargeting).
   - An ad-level Ads Manager export over a long range (12-24 months; columns: ad set, ad name, delivery, spend, impressions,
     link clicks, purchases, purchase value). If they have none, work from their description of old winners.
3. Check fit. It is built for accounts with lots of creative history and real spend (examples in the training: $5-10k/day;
   "working at the top level spending accounts like $500k+ monthly"). At $100-400/day it still works but keep it tiny
   (1x CPA/day) — or skip it if the account has no proven ads yet. Supply-capped businesses are the one case where capping
   more than dead ads makes sense.

## Workflow

1. **Sort the graveyard.** Run the planner on the export:
   `python3 scripts/a2.py zombie export.csv --breakeven-cpa <BE> --account-daily-spend <spend/day>`
   It returns the buckets, the bid cap and a starting budget. Review its picks with judgement (seasonal/sale creative, broken
   links, off-brand ads, policy-risky ads must be dropped).
2. **Pick the first wave.** Start with the ~15 best fatigued winners of the last two years, not 500 ads: "You can't have 500
   really good ads in the last year." Evergreen only — no sale, holiday or time-bound creative.
3. **Build the campaign exactly as in `references/zombie-build-sheet.md`**: Sales · Auction · CBO · bid strategy **Bid cap**
   (not cost cap, not cost-per-result goal, not ROAS goal) · Maximize number of conversions · Purchase · Standard
   attribution (incremental is not available with bid caps) · broad audience with heavy exclusions (purchasers/customer
   lists, engaged, visitors, ATC/IC) · all placements (Reels + Feed only above ~$100k/month).
4. **One ad set per bucket** — fatigued winners · duds · delivery-but-no-efficiency · organic posts — and one ad set per
   product/margin tier when breakeven CPAs differ (bid cap set per ad set). Copy ads by **post ID** so comments and likes come
   along; the delivery reset is wanted ("we want the reset to occur").
5. **Set the bid cap = breakeven CPA. Nothing under, nothing over.** Never raise it to "get spend": zero spend validates that
   those ads deserved to be paused — "a feature, not a bug."
6. **Size the budget** at max(1x breakeven CPA, ~10% of account daily spend). The cap, not the budget, should limit delivery:
   expect it to float ≥ 20% under budget most days ("dangle the carrot"). On a $10k/day account ~5% of total spend is plausible.
7. **Leave it alone for 7-14 days.** No daily tinkering. Then:
   - At/below breakeven with delivery → raise the budget (the cap protects you).
   - Little or no spend → normal; keep feeding new candidates.
   - An ad that now spends well at target → **revive it**: restart it where it used to win, or put it in a new pack in the
     prospecting CBO, keeping the post ID; optionally keep the zombie copy running too.
8. **Make it a cycle.** Every week, as you prune prospecting with the kill rules (`references/metrics-and-diagnosis.md` §6),
   send the pruned ads here instead of the graveyard: a pack hog that eats ~90% of an ad set without converting (move it so
   the other ads get spend), one representative of each dud concept (pause the rest), organic posts that engage but don't sell.

## Hard rules (and why)

- **Bid cap, at breakeven.** A cost cap averages — it buys some conversions above target. A bid cap is a ceiling per auction,
  "the most restrictive setting for a conversion event". That safety net is what makes re-running losers safe.
- **Never a test against highest volume.** Caps "always win on efficiency, never on volume" and look even better beside
  highest volume because they bottom-feed impressions it generated. The prospecting CBO on highest volume stays the engine.
- **100% exclude retargeting and retention audiences**, or the zombie "looks really good" by soaking up warm conversions
  that belonged to relevant campaigns.
- **Don't put live winners in caps** (unless supply-capped): you will spend "a lot less", and volume is what makes the
  business wealthy — "the trap is thinking ROAS makes you wealthy when volume makes you wealthy."
- **Don't use zombie as a reset button** for a whole account. To restart a paused account, turn the original campaign back on
  trimmed to its best winners (keeps comments and signal); don't scrap-and-relaunch.

## Output format

Save to `ads/<brand-slug>/zombie-plan-<YYYY-MM-DD>.md` (or the user's path) and summarise in chat:

```markdown
# Zombie campaign plan — <brand> — <date>
## Setup
| Setting | Value |
|---|---|
| Campaign | ZOMBIE_BIDCAP_<market> · Sales · Auction · CBO |
| Bid strategy | Bid cap = $<breakeven CPA> (per ad set if margin tiers) |
| Budget | $<x>/day (expected spend ≤ 80% of it) |
| Optimisation | Max number of conversions · Purchase · Standard 7-day click |
| Audience | Broad; excluded: <purchasers 180d, customer list, engaged, visitors 30d, ATC/IC 90d> |
| Placements | <all | Reels + Feed> |
## Ad sets and ads (wave 1)
### 1. Fatigued winners — <n> ads   (table: ad · post ID · lifetime spend · lifetime CPA · why)
### 2. Duds — <n> ads (one per dead concept)
### 3. Delivery, no efficiency — <n> ads
### 4. Organic posts — <n> posts
## Rules of engagement
- Review on day 7 and day 14; actions per outcome
- Weekly feed: <who moves pruned ads in, from where>
- Revival trigger: <ad spends ≥ $X at ≤ breakeven over 7 days → restart in <ad set>/new pack>
## Expected outcome
<honest range: often little spend; plausible ~5% of account spend at breakeven or better>
```

## Variant: Pellegrini's cost-cap zombie

Matteo Pellegrini (2026) runs a "Zombie cost cap" campaign across all markets for "losers with potential" (good signals,
not enough volume) and "winners that ran out of breath" — they "don't die: they run at a capped cost". Use it only if the
account already runs cost caps successfully and the brand cannot accept a bid cap's near-zero delivery. Set the cost cap at
the **true target CPA** and judge it with `python3 scripts/a2.py cap-diagnose`. Default remains the bid cap.

## Quality bar

- Bid strategy is Bid cap and the value equals breakeven CPA (not target, not "a bit higher to get spend").
- Exclusions cover purchasers, customer lists, engaged, visitors and ATC/IC; nothing time-sensitive inside.
- Every ad moved is accounted for in its old home (paused, or left running if it is still profitable there).
- Budget is sized so the cap limits delivery; review dates are set; the revival trigger is written down.
- The user knows the honest expectation: incremental, often small, sometimes zero.

## References

- `references/zombie-build-sheet.md` — click-by-click build, bucket definitions, Q&A edge cases (dropshipping margins,
  small budgets, organic posts, revived edits), conflicts between sources.
- `references/metrics-and-diagnosis.md` — the kill tree that decides which ads get demoted to the zombie.
- `references/andromeda2-doctrine.md` — why fresh entities, specificity and spend signals matter.
- `scripts/a2.py` — `economics` (breakeven CPA), `zombie` (planner), `cap-diagnose` (cost-cap variant).
- Sibling skills: `andromeda2-creative-iteration` (turn revived winners into new iterations), `andromeda2-launch-testing`
  (the prospecting CBO and pack rules), `andromeda2-hard-scaling` (cost caps, bid caps and ROAS goals at $50k+/day).
