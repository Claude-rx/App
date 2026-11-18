# Metrics, benchmarks and diagnosis

Shared by every `andromeda2-*` skill. The numbers here are reference points from the source courses; **the account's own
30-day baseline is the benchmark that counts.** `scripts/a2.py analyze` computes everything below from an Ads Manager CSV.
Master copy in `tools/andromeda2/shared/`.

Contents
1. Definitions
2. Reference ranges
3. Reading windows
4. The diagnosis ladder (which stage to fix)
5. Funnel-drop procedure
6. Kill / keep / cap / winner rules
7. Attribution
8. Frequency caps
9. Account-health checks

---

## 1. Definitions

| Metric | Formula | Note |
|---|---|---|
| CPM | spend ÷ impressions × 1,000 | Price of attention; driven by competition, engagement and audience breadth |
| CTR (link) | link clicks ÷ impressions | Use link CTR, not "CTR (all)" |
| CPC (link) | spend ÷ link clicks | = CPM ÷ (1,000 × CTR) |
| Hook rate (thumb-stop) | 3-second video plays ÷ impressions | Some practitioners now treat ~1 s as the real hook window |
| Hold rate (A) | ThruPlays ÷ 3-second plays | Share of hooked viewers who stay (Pellegrini). **Default in these skills.** |
| Hold rate (B) | ThruPlays ÷ impressions | Dara Denney's definition; numbers are ~3-6x lower than (A). Say which one you use |
| Cost per ATC / IC | spend ÷ adds to cart / checkouts initiated | Leading indicators; stabler than CTR/CPM |
| CPP / CPA | spend ÷ purchases | "Cost per purchase" |
| ROAS | purchase value ÷ spend | Meta-reported; compare with incremental |
| MER | total store revenue ÷ total ad spend | The blended truth; King goal usually lives here |
| Frequency | impressions ÷ reach | By window (7/14/30 days) |
| RPV | revenue ÷ sessions | $2 CPC and $4 RPV = 2.0 ROAS |

## 2. Reference ranges (use only until you have your own baseline)

| Metric | Weak | Typical | Strong | Source notes |
|---|---|---|---|---|
| Hook rate | < 20% | 25-35% | 40%+ | Denney examples 20-44%; winning test 44% |
| Hold rate (A) ThruPlay/3s | < 10% | 12-20% | 25%+ | derived: winner 7% ÷ 44% ≈ 16%; 16% hold(B) on a 42% hook ≈ 38% |
| Hold rate (B) ThruPlay/impr | < 4% | 4-7% | 10%+ | Denney examples 4-16% |
| CTR (link) | < 0.6% | 0.8-1.3% | 1.5%+ | Varos median 0.59% (2023 DTC); Blueprint account norm 1.3%; CRO soft KPI > 1% |
| CPM (US DTC) | — | $10-30 | — | Varos median $28.55 (2023); one Blueprint account $5.81 — too market-dependent for absolutes |
| Click → ATC | < 5% | 8-15% | 15%+ | Moonlighters portfolio ATC rate 14.8% |
| ATC → IC | < 40% | 50-60% | 60%+ | example account 59%; "~50% drop per stage" |
| IC → purchase | < 30% | 35-50% | 50%+ | example 36%; stable within a couple of points |
| Engaged share of prospecting spend | — | 10-25% | — | > 20-25% = consider splitting retargeting |
| Learning-phase share of spend | — | ~10-15% | — | 85-90% for weeks = over-editing |
| Event Match Quality | < 7 | 8.4+ | 8.8+ | server purchases within ~10% of Shopify orders |

Anomaly signals (relative to the account's own norm, not absolutes): CPM < 40% of norm or CTR > 2.5× norm on a spend hog =
viral or wrong-pocket reach (e.g. norm 1.3% CTR / $5.81 CPM, red flag ~5% CTR / ~$1 CPM).

## 3. Reading windows

- **Creative verdicts:** wait 14 days if the account spends < $1k/day, 7 days at $1k+/day before calling a test.
- **Ad-level kill rules:** 7-14 day windows; never part-day data; never the day after a sale/holiday.
- **Scaling decisions:** check 14 → 7 → 3 days → yesterday/today, every time.
- **Day-over-day** only once the account does 10+ conversions a day.
- **Cost caps / ROAS goals:** judge on a ~7-day lookback (the cap's own window).
- Early-window ROAS understates final ROAS by an account-specific multiplier (1-day click vs 7-day click). Compute it once
  and judge early reads against the adjusted target rather than killing on day-1 numbers.

## 4. The diagnosis ladder — fix the first weak stage only

| Stage | Weak signal | Usual cause | Fix |
|---|---|---|---|
| 1. Hook | hook rate < 80% of account median | first 1-3 s: no pattern break, talking head before action, generic line, wrong side called out | new visual hook + first line; keep the body (hand demo, texture close-up, emotional element, recognisable moment, "hard-to-argue" demo, silent 0-2 s then reveal) |
| 2. Hold | hold rate < 80% of median with a fine hook | slow lead, shots longer than 3 s, no open loop, footage doesn't match the words | new lead (agitate, myth-bust, story from the climax), cuts every 1-3 s, movement in every shot, one shot per line, open a loop and pay it late |
| 3. Click | CTR < 80% of median with fine watch metrics | desire/feature confusion, no mechanism, weak proof, no offer/risk reversal, vague CTA | sell the moment regained, name the mechanism, anchor proof, show the offer and guarantee, direct CTA |
| 4. Purchase | click→purchase CVR < 60% of account, cost/ATC high | ad↔page mismatch (angle, avatar, offer not carried through), price shock, slow/broken page, in-app browser bugs | same headline/angle/offer on the landing page, pre-qualify in the ad, reveal price where intent is built, pre-applied discount links |
| 5. Value | CPA fine, ROAS low | AOV low | bundles ("people have two knees"), BOGO, free-shipping threshold near AOV, order bumps, max value / ROAS goal at scale |

Additional rules:
- Low ROAS but cost per ATC/IC at or better than account → supporting/assisting ad: keep it.
- High CTR with weak conversion → clickbait or wrong side; tighten the call-out.
- Engagement-bait CPM drop with no purchases → it found cheap, wrong reach; cap it, don't scale it.

## 5. Funnel-drop procedure (when results fall 20-30% beyond normal)

1. Lay out the funnel: impressions → clicks → landing views → view content → ATC → IC → purchase.
2. Columns: CPM, CPC, cost per ATC, cost per IC, cost per purchase (+ Shopify for the same period).
3. Compare the periods and find the **earliest** stage that moved. CPM/CPC/cost-per-ATC flat but cost per IC jumped
   ($25 → $40) = not the ads; look between cart and checkout (new upsell, button, shipping, discount).
4. Then check where spend moved: by ad, age, gender, placement, location, audience segment.
5. Typical causes: a spend shift between ads (ROAS 4 → 1.2 overnight at $100/day), a site change (removed collection:
   46 ATC → 8 IC), a free-shipping threshold set too high (80% drop at checkout), a pixel/UTM change that reset post IDs.

## 6. Kill / keep / cap / winner rules (ad level)

Default stance: **most ads stay on.** Ask in order (Blueprint pausing tree):
1. Hitting KPI? → keep (even if old or "fatigued").
2. One bad day / part day / post-sale day? → no action.
3. Tracking healthy? (Events Manager, server vs Shopify) → if not, fix tracking first.
4. Check 7-day-click and incremental columns before judging a big spender.
5. Cost per IC/ATC at or better than average? → leading indicator; keep.
6. Viral or wrong-demographic spend hog (anomaly signals, breakdowns)? → **CAP** its ad set with a max-% spend limit
   (e.g. 80% → 60%, 90% → 20%); do not pause.
7. Spent < 2× target CPA? → too early.
8. ≥ 2× CPA, zero purchases, no ATC/IC signal → **pause**.
9. Within 50% of KPI (target ROAS 2.0, actual 1.2) → keep watching on 7-14 days.
10. ≥ 3× CPA and still 50%+ off KPI → **pause**.

Never pause the top spender while the account is on target: it is usually the first-touch ad; accounts that kill it
improve for 3-7 days and then fall below target. Pausing too often is the #1 cause of volatility.

**Winner** = top ~10% of the account by spend AND at/above KPI AND incremental KPI above the account's acceptable baseline
(small drop from reported to incremental). Low-spend outliers (9 ROAS on $48) are not winners.
**Breakout winner** (for daily detection) = launched in the last 30 days, ≥ 10% of account spend in a 7/14/30-day window,
ROAS above the account average for that window.

Pack-level read (Evolve / Blueprint): judge the pack (ad set) as a whole — "does this avatar/concept work?" — even if one
ad takes 98% of its spend. Test classification: Winning ad found · Poor spend, great CPA · Poor spend, poor CPA · Great spend, poor CPA.

## 7. Attribution

- Default optimisation setting: 7-day click + 1-day engaged-view + 1-day view, Standard model — maximum signal while small.
- Always add Columns → Compare attribution settings → **7-day click** and **Incremental**. Judge scaling on incremental
  ROAS of the *new* audience segment: "what your next dollar will return" (example blended 2.6 → incremental 1.73).
- Switch the *optimisation* model to incremental only for big spenders (~$100k-300k+/month) or brands with 100-200k+
  engaged followers; never compare campaigns on different attribution settings; don't flip-flop.
- Kill thresholds must come from the same attribution model you judge on (incremental cost-pers are higher).

## 8. Frequency caps (rules of thumb, impressions ÷ reach)

| Audience | 7 days | 14 days | 30 days |
|---|---|---|---|
| Prospecting | 2-3 (3.5 fine if above target; 5 = expand with new concepts / interest suggestions) | 2-5 | 2-7 |
| Retargeting | ~5 max | 5-10 (10 max; 2 = spend more) | 15 max |
| Existing customers | 2-4 | 4-10 | 15 max |

Retargeting/retention are managed by frequency and ad-set maximums, not scaled like prospecting. Above-target retargeting
with high frequency: spend ~20% less there and move the cash to prospecting.

## 9. Account-health checks (weekly)

- Breakdown → Audience segments: new / engaged / existing share and ROAS (set segments up in Advertiser settings; not retroactive).
- Placements: the top six (FB & IG Feed, Stories, Reels) should hold most spend; a top-six placement near 1% = a creative
  gap for that format (usually vertical video).
- Learning-phase share of spend; number of resets on winning ads; anything auto-editing live ads (UTMs, integrations).
- Pixel gut check monthly: server purchases ≈ Shopify orders; EMQ ≥ 8.4; IC count never below purchases.
- Day-of-week: CVR by weekday from the longest Monday-to-Sunday range; shift CBO budget toward strong days with
  correct maths (+50% and −50% do not cancel).
- MER / blended business ROI next to Meta ROAS — Meta can look good while the business deteriorates.
