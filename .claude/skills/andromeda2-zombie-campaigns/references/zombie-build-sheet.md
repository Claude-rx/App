# Zombie campaign — build sheet, buckets and edge cases

Source: *The Facebook Ads Blueprint* — "Training: Zombie Campaigns w/ Sam" (2026) plus the August–September 2026 Q&As;
variant from Matteo Pellegrini (Mastermind Dubai 2026). Practitioner tactics, "not law": the teacher calls it "an extra tool
in the toolkit… not as heavily tested" as the core structure.

Contents
1. Click-by-click build
2. The buckets
3. Budget behaviour
4. Monitoring and revival
5. Edge cases from the Q&As
6. Failure modes
7. Source conflicts

---

## 1. Click-by-click build (Ads Manager, 2026 UI)

**Campaign**
- Create → **Sales**. Buying type **Auction**.
- Name: `ZOMBIE_BIDCAP_<market>` (keep "zombie" in the name so nobody "optimises" it by accident).
- Campaign spending limit: none (unless risk policy requires one).
- **Advantage campaign budget (CBO): on.** Daily budget per section 3.
- Campaign bid strategy → *other options* → **Bid cap**. Not "highest volume + cost per result goal", not ROAS goal.
- Delivery: Standard. Budget scheduling: off. Audience segment reporting: your normal segments.

**Ad set (one per bucket)**
- Customer lifecycle prompt (new UI): "Get more conversions" (default) is fine because exclusions do the work; if the UI shows
  "Acquire new customers" with an exclusion field, use it to exclude existing customers.
- Conversion location: Website. Performance goal: **Maximize number of conversions**. Event: **Purchase**.
- **Bid cap amount: breakeven CPA** (first-purchase breakeven from the profit model). One value per ad set, so margin tiers
  get their own ad set and cap.
- Attribution: **Standard** model (incremental cannot be used with bid caps), 7-day click (+1-day view as in the account).
- Audience: Advantage+ / broad, but "exclude heavy": purchasers 180 days, all-time customer list (CRM/Klaviyo), engaged
  audiences, website visitors 30 days, add-to-cart / initiate-checkout 90 days, IG/FB engagers. "Do not target anybody that
  could be targeted in your other campaigns outside of broad prospecting."
- Placements: Advantage+ (all). At roughly $100k+/month account spend consider limiting to **Reels and Feed** so the zombie
  does not "sneak in and take credit for display, Audience Network, Messenger".
- Languages: only those your ads and site use.

**Ads**
- Use the existing post (**post ID**) so likes, comments and shares carry over. The delivery learning resets — intended.
- Evergreen creative only. Check every landing URL still works and every offer in the creative is still true.
- Naming: keep the original ad name + `_ZMB` so reporting can join old and new history.

## 2. The buckets

| Ad set | What goes in | How to recognise it |
|---|---|---|
| 1. Fatigued winners | Ads that "went pretty well and then just slowly tapered off" on spend, CPA or ROAS | Lifetime CPA ≤ breakeven on meaningful spend; paused or no longer getting spend |
| 2. Duds ("bad ads") | Ads that "never got off the ground" | < 2x breakeven CPA spent, no purchases; after a pack's 7-day minimum they drift to $2-3/day. Move **one** representative per dead concept, pause the rest |
| 3. Delivery, no efficiency ("in-between") | Ads that spent a lot in prospecting but never hit target — including the hog that takes ~90% of a pack while nothing converts | ≥ 3x breakeven CPA spent, CPA above breakeven. Moving the hog lets the other ads in that pack get spend |
| 4. Organic posts | Posts that engage but don't sell; you are "tired of overspending on organic because they have better engagement but they don't sell" | "You're killing them before they get killed." Default is still to test good organic posts in the prospecting CBO |
| 5+. Product / margin tiers | Same buckets for products with different breakeven CPAs | One ad set per tier, each with its own bid cap. Separate campaigns only for totally different categories |

"These buckets don't matter too much. If you have a lot of any sort of bucket, make another bucket." The CBO is budget-
and bid-restricted, so ad-set count is not a problem.

Start: "If you know you have like 15 really good ads in the last two years, just get those in there… then just start the
cycle."

## 3. Budget behaviour

- Highest volume spends right at budget. A bid cap "will spend in full… when it's hitting its target, but will spend most of
  its time restricted about 20% under." Spending the budget in full every day "would be weird".
- Starting size by risk tolerance:
  - Small account (~$400/day): 1x breakeven CPA (e.g. $50/day) — "would you freak out if you spent $100 and didn't hit
    target? If not, set it." Not 25% of the account.
  - Large account ($5-10k/day): ~$1,000/day; worst case it spends $1,000 with no purchases and the day's CPA inflates ~10%.
  - At ~$10k/day "it wouldn't surprise me if that could spend like 5% of the budget."
- Scale: "set it low, see how it works; if it gets some delivery and over a 7-day / 14-day period it's at your efficiency
  metrics, bump it up."

## 4. Monitoring and revival

- "This should not be overly monitored… let it run, let it rock." Review at day 7 and day 14.
- No spend = the creatives can't hit breakeven = the original pause was right. Do not raise the cap.
- Revival: "if… an ad is actually spending a lot now and is above [the] target threshold… restart that ad… in our prospecting
  CBO" or "just restart that ad set or ad wherever it was previously working." It can keep running in the zombie at the same
  time. Top accounts report ads coming back "with comments with post shares… the CBO just treats it differently all of a
  sudden — we've literally revived ads back from the dead."
- Big-brand reference: accounts running thousands of live ads (Athletic Greens "from 500 creatives… to 8,000 active ads")
  keep most of them in heavily restricted bid-cap campaigns; roughly "80% of the ads are in zombie, 20% of the ads are running
  most of the volume."

## 5. Edge cases from the Q&As

- **Dropshipper with many dead products at different prices:** one zombie campaign, one ad set per product/margin tier, bid
  cap per ad set. Not one campaign per product (unless categories are totally different).
- **"I bid at breakeven and it didn't spend, so I raised the bid and got sales":** don't. Raising the bid above breakeven
  turns the zombie into unprofitable spend; the cheap CPA you saw was luck on small numbers.
- **Should winners go in a separate capped ad set for efficiency?** For ~95% of brands no — caps cut volume. Exception:
  supply-capped businesses that must chase efficiency.
- **Ad hogging 90% of a pack, nothing at target:** move that one ad to zombie; let the other four run and see if they get spend.
  Don't throw the others down immediately.
- **Dud concept with five iterations:** move one, pause the rest.
- **Winner edited after a copyright takedown (lost its likes):** put the edit in its old place and in a new pack; force spend
  with a minimum only if it gets nothing after a week. (Not a zombie case.)
- **Account paused for months:** restart the original campaign trimmed to the best winners — keeps comments and signal.
  Don't launch a fresh campaign as a "reset button".
- **New brand at $150/day with no data:** no zombie, no minimums; one avatar, let Meta distribute.

## 6. Failure modes

| Mistake | Result |
|---|---|
| New campaign without a bid cap | "Does absolutely nothing" |
| Cost cap / cost-per-result goal / ROAS goal instead of bid cap | Averages in unprofitable conversions; not the zombie mechanism |
| Run as an A/B test vs highest volume | Caps always look more efficient (they bottom-feed HV impressions); wrong conclusion |
| Retargeting/retention not excluded | Looks great, steals warm conversions from relevant campaigns |
| Bid raised above breakeven | Defeats the purpose |
| Live winners moved into caps | Efficiency up, volume collapses |
| Sale/time-sensitive creative inside | Dated offers, wasted spend |
| Hundreds of micro-variations dumped in | "Mass creative won't do anything. Only quality creative actually produces any sort of result." |

## 7. Source conflicts

- **Bid cap vs cost cap.** Blueprint (Sam) is explicit: bid cap, never cost cap. Pellegrini's deck labels his version
  "ZOMBIE COST CAP · tous les marchés" for "creatives with good signals but not enough volume to scale + former winners that ran
  out of breath — they don't die, they run at a capped cost", next to separate bid-cap (controlled scaling of the best
  winners, "inflated, normal bid cap") and cost-cap (CPA stability on top performers) campaigns. Default: bid cap at
  breakeven; cost-cap variant at true target CPA only for accounts already succeeding with cost caps.
- **"Changing bid strategy never changed results"** (an unclear remark in one Q&A) sits awkwardly with the zombie premise; the
  zombie training is the detailed, deliberate source and wins.
- **Placements:** all placements by default; Reels + Feed only at very high spend.
