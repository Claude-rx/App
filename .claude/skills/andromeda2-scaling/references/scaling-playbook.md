# Scaling playbook — procedures, maths and troubleshooting

Sources: *The Facebook Ads Blueprint* 2026 (Vertical, Horizontal, Twin Engine, Learning Phase, Day of Week, Value Rules,
Max Conversions vs Max Value, Geo, Frequency) and its 2026 live calls; Telehealth media-buying bonus (efficiency ceiling);
Fernando Oliver (ROAS cliff, duplication — dated); Foundr 2020 (delayed attribution). Heuristics, not Meta documentation.

Contents
1. Vertical scaling — the full procedure
2. Doubling / rebuild mode
3. Sale and drop scaling
4. Why ROAS dips after a raise (and when it is real)
5. Internal horizontal — the creative engine
6. External horizontal — the three valid cases
7. Day-of-week budget shaping
8. Value rules
9. Max conversions vs max value
10. Geo expansion
11. Frequency, saturation and efficiency ceilings
12. Inventory-limited winners
13. Troubleshooting table
14. Dated tactics (and why not)

---

## 1. Vertical scaling — the full procedure

1. King goal from the profit model (one number; first-purchase or LTV-based). Example King goal 2.5x ROAS.
2. Above target → increase spend. Worked example: 10x ROAS at $100/day = $900 profit, 10 customers; 2.5x at $1,000/day =
   $1,500 profit, 25 customers (plus LTV and word of mouth). "Even if profit was identical, the 25-customer version wins."
3. Audience segments: new 2.35 vs target 2.5 → hesitate; new ≥ 2.6 → push harder.
4. Incremental: blended 2.6 → incremental 1.73; new 2.35 → 1.64 — "this is what you should expect" from the next dollar.
5. Stability: 14 → 7 → 3 days → yesterday/today, every time; 5-day windows only for big accounts you know well.
Moves: default 10-30% / 48-72 h; 10-15% for multi-thousand-$/day tight campaigns; +50% steps at ~$100/day
(100 → 150 → 225 → 300); +50% fine for an established campaign ~40% above target; double when ≥ 2x target.
Delta maths ("smashing"): at $1,000/day and 5x on a 2.5x target, revenue is $5,000 vs the $2,500 needed: $2,500 of headroom.
Doubling to $2,000/day stays at target even if every new dollar returned zero. `a2.py scale` reports this ceiling.
"Vertical scaling never ends. Above target → push spend → monitor incremental and blended → push again."

## 2. Doubling / rebuild mode

For a brand returning toward a spend level it has already sustained (e.g. previously $20k/day, restarted at $500/day; AOV $65,
CPA ~$25, ~1-day purchase cycle): $500 → $1,000 → $2,000 → $3,000, then "start stacking thousands". Judge only on incremental
and early-funnel costs: cost/ATC +3-15% and cost/IC +10-15% after a doubling are normal; cost/ATC doubling = stop.
"Respect how much you're spending compared to how much you used to be spending — play by the new spend."
Restarting a paused account: turn the original campaign back on trimmed to its best winners (keeps comments, engagement,
signal) rather than launching new campaigns.

## 3. Sale and drop scaling

Separate lifetime-budget campaign for the window. Judge on the sale KPI (margins differ). If above it: "I'm not talking 20%.
I'm talking big jumps"; intraday +10-20% steps, several upward changes a day are fine; avoid cutting mid-day ("changing it down
is really going to get confusing for the algorithm"). Faster kill switches on cost per ATC/IC; don't pause high spenders unless
they are killing you. BFCM psychology (Pellegrini): buyers want to *win* — visible, credible limits; quadruple offer (visible
strike-through price, free product/BOGO, mystery gift/voucher, free shipping) + an extra code.

## 4. Why ROAS dips after a raise (and when it is real)

Every impression has a time-to-convert. At steady spend, conversions from impressions served 1-15 days ago arrive steadily.
A raise adds a disproportionate number of top-of-funnel people who take longer; you judge total ROAS on the whole budget,
so it dips — "an unfair way to judge". Novices cut, wait five days, things "improve", and the roller-coaster repeats.
It is real when: incremental new-segment ROAS keeps falling period over period; cost per ATC rises in step with spend; CPC
doubles while CVR falls; new-audience frequency climbs toward ~6; engaged share balloons. Then stop the increases, let it
settle, and diagnose (incremental, CPC, cost/ATC, cost/IC, CPA, AOV, CVR, audience segments, breakdowns).

## 5. Internal horizontal — the creative engine

- Same angle, different executions (statics and videos that all carry one winning angle in fresh ways).
- Same avatar, new problems (the avatar's adjacent pains and desires).
- Interest-suggestion packs with winners only (adjacent interest "once removed").
- New-concept budget at scale is cheap insurance: at $10k/day, $10k over 10 days on a new concept is 10% of spend; if it runs
  50% worse that's −5% efficiency, but one winner can turn it into +25%.
- Creative volume grows with spend; iterations dominate at scale; quality over micro-variations ("mass creative won't do
  anything").

## 6. External horizontal — the three valid cases

1. **Sales, drops, promos** — new CBO with lifetime budget for the window; adding a sale into the core starves the working ad
   sets and forces a disruptive redistribution when it ends.
2. **Margin tiers / different businesses** — max conversions treats a $1 and a $100 purchase alike, so budget drifts to cheap
   SKUs. First fix: a max-value CBO beside the core. Separate campaigns only for truly different offers ($1,000+/month
   service vs $197/month membership), not $50 vs $75 products.
3. **Winners campaign (optional)** — 1-5 home-run ads already taking a huge share of spend above target, for a few weeks or a
   season. "Think of it as fuel on the fire, not the fire itself." No ad set limits; exclude everything targeted elsewhere.
Vehicles model: if vehicle 1 does 2.0 incremental and vehicle 2 does 1.8, kill vehicle 2 and spend on vehicle 1
("reverse Dave Ramsey": max out the 10x opportunities first, then go down).

## 7. Day-of-week budget shaping

Report: Ads Reporting → spend, purchases, purchase value by day over the longest Monday-to-Sunday range → sheet →
`=WEEKDAY()` → pivot by weekday → CPA and ROAS per day. Typical: weekends stronger.
Shift: e.g. flat $5,000/day, CVR Mon 2.4 / Tue 2.5 / Wed 2.6 / Thu 2.4 / Fri 3.0 / Sat 3.0 / Sun 1.4 → move $2,500 from Sunday
to Friday/Saturday → +8 purchases/week on the same $35k. Implement on the prospecting CBO budget (manually or with an
automated rule once daily, max budget set, and a second rule to bring it down). Maths: +50% on 3 days and −50% on 4 days of a
$1,000 base = $7,500/week, not $7,000 — compute the down-step so the weekly total matches.

## 8. Value rules

Advertiser settings → Value rules → rule set (age, gender, OS, location, placement) → apply in the ad set. Use only for big,
data-proven gaps; "an elimination game, not an increasing game". Start ≤ 25% (Meta suggests 50%+; above ~50% things get out of
hand). Example: −25% on 65+ makes that segment count $7,500 of $10,000 revenue (ROAS 2.0 → 1.5), so it must be 25% better to win
spend. Uses seen in 2026: weight countries (+25% for the best market, minus for break-even ones); seasonal dips (UK summer
−20%); a creator who fails with one age group (−30-40% on that age). Value rules don't reset learning.

## 9. Max conversions vs max value

Max conversions when AOV is steady or signal is thin; max value when AOV varies a lot and there is plenty of signal (bundles,
$10-$100+ ranges, subscriptions vs one-time). You usually can't switch in place: build a max-value prospecting CBO with the top
ads of each product and run it beside the max-conversions core (move up to ~half the budget). Expect max conversions to lead
first, then max value to pull ahead. Example test (incremental attribution, $28k each, ~25 days): max conversions $36 CPP /
0.8 ROAS vs max value ~$56 CPP / 1.2 ROAS. Pass estimated LTV as the value of subscribe-and-save purchases so Meta doesn't treat a
$40 subscription as worse than a $54 one-off.

## 10. Geo expansion

Winners-only country packs inside the prospecting CBO; ≥ 7 days before adding a minimum = average CPA; cut countries far off
average CPP; weight with value rules. Expand country by country — "hard to be good at baseball and basketball at the same time."

## 11. Frequency, saturation and efficiency ceilings

- Prospecting frequency: 7d 2-3 (3.5 fine above target; 5 → widen with new concepts/interest packs); 14d 2-5; 30d 2-7.
  New-customer frequency ~6 = you cannot scale into it.
- Fatigue is rarely the true ceiling: accounts spend hundreds of thousands a day unfatigued with enough concepts.
- Efficiency ceiling (Telehealth example): at $5k+/day cost per application jumped; the operator held at $5k rather than push
  to $6-7k — "respect the efficiency curve, don't chase volume." Reconcile with "volume makes you wealthy": hold when
  incremental new-segment results fall below the King goal; push while they hold. Taking profit = raise the target slightly
  (1.2 → 1.3) and keep the delta; 10-20% above break-even is a healthy operating point.
- ROAS cliff (Oliver): pushing one CBO forever walks toward the point where Meta can't find your buyer at your price; the Twin
  Engine's creative flow and new concepts are what move the cliff.

## 12. Inventory-limited winners

A 10x ROAS winner that will sell out in 16 days: spend it ("10 ROAS for 16 days then half beats cutting 35% now"); at very
high spend cool it slightly to stretch. Also: speed up production, default the swatch to the in-stock variant, recreate the
winners in the other variant, honest pre-orders with ship dates, back-in-stock lists, price tests across breakpoints
($99 is a wall; $99 → $129 usually loses, $99 → $199 can win).

## 13. Troubleshooting table

| Symptom | Likely cause | Action |
|---|---|---|
| ROAS fell 2-4 days after a raise, cost/ATC flat | Conversion lag | Hold; re-check day 5-7 |
| ROAS falling week over week with each raise | Creative pipeline behind spend | Pause increases; ship iterations of the top 5-10 ads; new concepts on winning avatars |
| New spend all went to engaged/existing | Prospecting not truly prospecting | Exclusions; retention split; check audience segments |
| Blended MER down while Meta ROAS fine | Attribution inflation, cannibalised organic/email | Judge on incremental + MER; slow down |
| One ad takes 90% and is below target | Viral/wrong pocket or fatigued hog | Cap its pack (% max) or move it to zombie; don't pause the top spender if the account is on target |
| Cheap SKUs absorb the budget | Max conversions with mixed AOV | Max-value CBO beside the core |
| Spend capped at frequency 6 on new | Saturated pocket | New concepts/avatars, interest-suggestion packs, new countries |
| A country/age segment drags | Real performance gap | Value rule −20-25% (or exclude a clear loser country) |
| Scaling stalls on a hero product sell-out | Inventory | Section 12 |

## 14. Dated tactics (and why not)

- Duplicating a winning CBO at 2-3x budget (Oliver, ~2024): duplicates split the same audience and reset learning; today
  this is "sloppy vertical scaling" — raise the existing budget instead.
- ABO testing + graduation to a scale campaign: permanent cost centre of unproven ads.
- The 10-20%-per-day rule as law: a control mechanism for nervous operators; use the move sizes above.
- 28-day click attribution, stacked interest lists, lookalike ladders (2020): replaced by broad + creative-led delivery.
- Delayed-attribution multiplier (Foundr): still useful — compute how much 1-day results understate 7-day results for your
  account (1-day click vs 7-day click) and judge early reads against the adjusted target.
