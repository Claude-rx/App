# Meta Ads Media Buying SOP

**Source:** *The Facebook Ads Blueprint* course: every video transcript, summary doc, PDF and live-call recording in the shared course folder (75 core lesson files, 17 live-call transcripts, plus the linked tracker, profit and ad-builder sheets and the brief template). See [sources.md](sources.md).
**Owner:** Head of Media Buying · **Applies to:** every Meta ad account we manage · **Version:** 1.1 (2026-11-04). For v1.1 every one of those files was read first-hand, and the two videos without transcripts (Image Ads Templates, Multi Advertiser Ads) were watched frame by frame. v1.1 changes are in §13 (#19 onward).

This SOP is the operating rulebook. Each rule cites the lesson it comes from, in brackets, e.g. **[Pausing Ads]**. The numbers live in one place, [`tools/fb-blueprint/rules.py`](../../tools/fb-blueprint/rules.py), and the four Claude skills apply them: `fb-launch`, `fb-test`, `fb-optimize`, `fb-scale`. If you change a number, change it there; never in a skill.

> **How to read conflicts.** When lessons disagree, this order wins: **(1)** videos marked *NEW* in the course → **(2)** core-module transcripts → **(3)** live calls, when they say "we changed this" → **(4)** summary docs. Every conflict and every value the course leaves open is logged in **§13 Decisions log**. Read it before you argue with a number.

---

## 0. The ten laws (memorize these)

1. **One system per account.** Prospecting CBO + Retention is the core. Everything else is optional. **[NEW: Current Structure → M4] [Live Q&A 8/31]**
2. **One King Goal.** Pick ROAS *or* CPA from the profit model. If you are above it, spend more. **[Setup: Profit Tracking] [Vertical Scaling]**
3. **New creative always goes into a NEW pack (ad set).** Never add ads to an existing ad set. Never move ads between ad sets; the only exception is moving an ad into the zombie campaign. **[# Of Ads To Launch] [Ads That Scale] [Live Q&A 9/9]**
4. **Never pause anything that is hitting KPI.** Pausing follows the 13-question tree, never a feeling. **[Pausing Ads]**
5. **Judge on 7–14 day windows.** Never on yesterday, a slow morning, or a post-sale dip. **[Pausing Ads] [Flywheel]**
6. **Purchase is the conversion event.** Lead gen uses the deepest *qualified* event. **[Dictionary] [Must Watch For Lead Gen]**
7. **Don't let Meta modify your creative.** No flexible ads, no visual touch-ups, no animation, no Advantage+ creative test. **[Dictionary] [M4 Prospecting]**
8. **Scale vertically by default**, while the creative pipeline never stops (twin engine). **[Twin Engine]**
9. **Every decision is read on the right attribution.** Standard 7-day click / 1-day engaged view / 1-day view, sanity-checked with *Compare attributions → Incremental*. **[Attribution Settings] [Graduation System]**
10. **If it works, don't touch it.** **[NEW: Current Structure → M4] [Live Q&A 8/24]**

---

## 1. Roles and cadence

| When | Who | What | SOP |
|---|---|---|---|
| **Daily, 7–8 am** | Media buyer | Anomaly check (6 comparison windows, 20% threshold). Look at today, yesterday, 3d, 7d and 14d, but act only on 7–14d windows. Check minimums that are past day 7. Run the kill switches if Shotgun is used. | §8.1, §5.4, §7.6 |
| **Daily, midday** (big accounts) | Media buyer | Cost per ATC check; same-day budget nudge on prospecting | §8.7 |
| **Every 48–72 h** | Media buyer | Vertical scaling decision on the prospecting CBO | §9.1 |
| **Monday** | Buyer + creative lead | Launch this week's new packs. Finalize last week's analysis. Brief winners. | §6.3 |
| **Friday** | Buyer | First pass on the analysis of Monday's launches | §6.3 |
| **Weekly** | Buyer | Pausing tree on ads with ≥7 days of data. Graduation. Frequency by swim lane. Audience-segment split. | §7.3, §7.4, §8.2, §8.4 |
| **Monthly** | Buyer + owner | Pixel gut check. Profit model refresh. Placement, geo and day-of-week reports. Free-shipping threshold check. | §4.2, §3.2, §8.5, §8.7, §8.10 |

Tracking sheet data (Adveronix) refreshes automatically every day at 4–5 am **[Setup: Ads Tracking Template]**. The winners detector runs at 4 am and the anomaly refresh at 6 am **[Claude: Unlimited Ads Workflow] [Claude: Anomaly Dashboard]**.

---

## 2. Glossary (use these words exactly)

| Term | Meaning | Source |
|---|---|---|
| **King Goal** | The ONE efficiency target (ROAS *or* CPA) from the profit model. It outranks every other metric. | [Vertical Scaling] |
| **Avatar** | The "who", defined by identity, situation, aspiration or behavior. **Not a demographic** ("white male is not an avatar"). | [3 Ways To Sell] [Live: Retargeting Q&A] |
| **Template** | A repeatable ad format, e.g. Us vs Them, 3 Reasons Why, UGC in car. | [Andromeda] |
| **Concept** | **Avatar + Template.** Changing the template means a new concept. | [Andromeda] |
| **Iteration** | A controlled variation of a proven concept. It changes one emphasis layer (message, mechanism, avatar, education, offer, visual), never the structure. | [Concepts vs Iterations] |
| **Pack** | One prospecting ad set = one round of creative, grouped avatar first, then concept. | [M4 Structure Overview] |
| **Swim lanes** | New (prospecting) / Engaged (retargeting) / Existing (retention), read from *Breakdown → Audience segments*. | [M4 Retargeting] |
| **Graduation** | Duplicating a proven winner into an interest pack, Retention, or (rarely) Scale. The original keeps running. | [Graduation System] |
| **Zombie campaign** | A bid-capped campaign at break-even CPA that holds fatigued ads and duds. | [Live: Zombie Campaigns] |

---

## 3. Economics: set targets before spending a dollar

### 3.1 Tracking sheet [Setup: Ads Tracking Template]
1. Copy the Moonlighters tracker. Install the **Adveronix** add-on and authenticate Facebook, Google, Bing and Shopify.
2. In *Raw Data*, edit **only white cells**. Never add columns, and never touch black bars or blue text: one wrong cell breaks the tracker.
3. Create the 13 saved reports. Lookback is **2 years** for daily/monthly reports and **90 days** for campaign and product reports. Put the time dimension first. Shopify records are 1,000, or 10,000 if you have more than 1,000 products. Filter Shopify new customers to "first time". Filter Google campaigns to impressions > 0. Never change the Facebook attribution in the pull.
4. Schedule all reports **daily at 4–5 am** with error emails on.
5. The *Monthly* tab is the front page: spend, ad purchases, ad revenue, CPA and ROAS per platform, plus Shopify orders, sales, new customers, new-customer revenue, CPA, ROI and **MER**.

### 3.2 Profit model [Setup: Profit Tracking]
Inputs (purple cells only): monthly orders, AOV, COGS %, fixed costs (all of them, rounded **up**), 12-month LTV, and take % if you want profit up front.

```
Revenue            = Orders × AOV
COGS $             = Revenue × COGS %
Ad spend budget    = Revenue − COGS $ − Fixed costs − (Take % × Revenue)
Break-even ROAS    = Revenue ÷ Ad spend budget        (BLENDED, store revenue, not in-platform)
Break-even CPA     = Ad spend budget ÷ Orders
LTV multiple       = 12-month LTV ÷ AOV
12-month gravy     = Orders × (12-mo LTV − AOV); profit on it = × (1 − COGS %)
```
Check: 100 orders × $80, 40% COGS, $1,000 fixed → $3,800 ad budget → **2.11 break-even ROAS** (engine: `profit_model`).

- Use **today's real numbers**, not hoped-for ones. Never set ROAS targets from someone else's account.
- **Break-even model** is the default for growth: $0 first-order profit, with profit coming from repeat purchases. **Take model**: each % taken raises the required ROAS and cuts volume sharply, so don't get greedy.
- LTV:CAC above 2.5 is good, above 3 very good, below 2 scary. E-com net margin is realistically ≤10%, 20% if you're lucky.

### 3.3 King Goal and target [Profit Tracking] [Vertical Scaling] [Live: Ads That Scale, Hotline]
1. Pick **one** metric, ROAS *or* CPA. Write it in the account brief: "As long as we are at or above X, spend as much as possible."
2. Target = break-even + take-home margin: **break-even 2.0 with 10% take-home → target 2.2**. 10–20% over break-even is the healthy zone (engine: `target_roas`).
3. Judge the King Goal on **blended business numbers** (Shopify, MER). Meta is a proxy, and incremental attribution tracks blended results most closely. **[Live: Funnel Analysis]**
4. Ignore CPM, CPC, ATC, AOV and revenue targets when making the decision. They are diagnostics only.

### 3.4 What to advertise [What Products To Advertise]
1. Sort products by revenue and units. In ads, about **10%** of products drive the business (not 20%).
2. Name the hero: a **product** (most common), a **collection** (when a category such as jackets dominates), or an **offer** (e.g. a starter kit).
3. Put **90% of spend on the hero and 10% on tests**. Test other products as a **new pack in the prospecting CBO** and let CBO decide. If a test product beats the hero, you may have a new hero.
4. Never "advertise everything". Unproven products muddy the pixel.
5. Fix the product and offer before tuning ads, in this order: **product → offer → landing page**. **[Live: Product First]**
6. Many products at very different prices ($90 to $1,000): one prospecting campaign on **max value**, never one campaign per product. Break catalog ads out by price tier or category so each can be read on its own. **[Live: Product First]**

### 3.5 Month pacing [Setup: Ads Tracking Template (tracker tab)]
```
Daily spend to hit goal   = (Spend target − Spend month-to-date) ÷ Days remaining
Daily revenue to hit goal = (Revenue target − Revenue month-to-date) ÷ Days remaining
ROAS to hit goal          = Revenue remaining ÷ Spend remaining
```
Read it every Monday next to the King Goal. If the ROAS needed is above the King Goal, the spend target is the number that gives, never the goal. Engine: `pacing`.

---

## 4. Account foundations

### 4.1 Default settings, by level [Dictionary: Every Setting In Meta] [M4 Prospecting] [First $100 Setup]

**Campaign:** Auction · Sales objective (Leads for lead gen) · **no campaign spending limit** (except sale campaigns) · **CBO** (ABO only for multi-thousand-dollar AOV) · **daily** budget · bid strategy **Highest volume** · declare a **special ad category** whenever it applies (social issues, housing, finance), or risk rejection and suspension · Advantage+ catalog **off** for prospecting · never use the campaign-creation A/B toggle (if you must A/B test, run it 28 days and judge on cost per purchase).

**Ad set:** conversion location **Website** (single location) · performance goal **Maximize number of conversions** (value only for data-rich accounts, see §8.9) · dataset = your pixel · event **Purchase** · cost per result goal blank · value rules off at launch · attribution **Standard: 7-day click, 1-day engaged view, 1-day view** · conversion count **All conversions** · no end date · **Advantage+ audience on** · languages = only the languages of your ads · **all 23 placements** (cut only with data, never on a live ad set) · brand safety default.

**Ad:** identity = Facebook page + Instagram + Threads · single image/video or carousel · **no flexible ads, no collection ads, no multi-advertiser ads in prospecting** · partnership ad for creator or whitelisted content · media in **1:1 and 9:16** (not 4:5; horizontal is optional and shows <5% of the time) · **2–5 primary texts, all completely different** · **2–5 headlines, all completely different** (5 + 5 is the agency standard on big accounts) · descriptions blank or "+ free shipping" · CTA **Shop Now** (Learn More for high ticket) · **≥4 site links** (best sellers, new arrivals, 2 key collections, hero) · promotions on if you run a code · UTMs go in **URL parameters**, never in the destination URL.

**Enhancements rule:** if it crops, modifies or animates the image or video, **don't**. Everything else is your call. YES: product tags/show products, overlays, site links, text improvements, enhanced CTA. NO: visual touch-ups, image animation, 3D, flex media, Meta-generated images, music (agency default is off). **[Dictionary] [M4 Prospecting] [First $100 Setup]**

**Skip:** suggested ads/imports, the creative testing module, image generation, Shop destination, the Advantage+ creative "test new enhancements" opt-in.

### 4.2 Pixel gut check (monthly) [Setup: Pixel Gut Check]
1. Events Manager → pixel → **Purchase** → *View details*: browser vs server events must be **≤10% apart**.
2. Shopify → Orders report, same dates: **server** purchases ≈ orders, within a couple of %. Over-counting is worse than under-counting.
3. **EMQ ≥ 8.4** (benchmark 8.8) once you have a couple hundred purchases.
4. Repeat for ATC and Initiate Checkout against Shopify. The funnel must make sense; fewer ICs than purchases is a red flag.
5. On any failure: hire a real developer, not a Fiverr reinstall. Run the pixel and CAPI together; don't rely on third-party attribution. **[Live: Funnel Analysis]**
- Watch out: an automated UTM change (e.g. a HubSpot integration) can reset every post ID and all learning. **[Live: Funnel Analysis]**
- Ads Manager showing fewer purchases than the store is normal (not every sale comes from ads). **Events Manager** showing fewer purchases than the store is a real tracking fault: fix it first. **[Live Q&A 8/24]**
- Protect the pixel: share it with a second Business Manager and keep a second admin person on every ad account. **[Live: Scaling, Pixels, Dropship]**
- Engine: `pixel_check`.

### 4.3 Advertiser settings and audiences [Advertiser Settings]
1. **Account controls:** leave audience and placement controls blank unless the law requires them (alcohol, under-21). Using them to "steer" the algorithm flags you and raises CPMs.
2. **Advantage+ creative → "test new enhancements": uncheck.** We are not guinea pigs.
3. **Meta Verified:** caution. It has been seen to raise CPC/CPM and cause access issues.
4. **Audience segments (most important; not retroactive, so set them up on day 1):**
   - Engaged = **Add to cart 90d + Website visitors 30d**
   - Existing = **Purchasers 180d (pixel) + CRM/Klaviyo customer list**
5. Build these audiences now:
   - Purchasers 180d (Website → Purchase → 180 days)
   - All-time purchasers (CRM upload or Klaviyo sync)
   - Visitors 30d
   - ATC 90d
   - IC 90d
   - IG/FB engagers 14–30d (only if you have a following)
6. **Klaviyo pairing:** for every pixel audience, add the matching Klaviyo segment in the same ad set, with "use as suggestion" off. Expect a 5–15% match lift. **[Audience Enhancement (via Klaviyo)]**
   - Segments: *Added to Cart at least once in the last 90 days*, *Checkout Started in the last 90 days*, *Active on Site at least once in the last 90 days*, plus customers/purchasers.
   - Name each one `ads_[event] [days]`. In Meta, create the Klaviyo list first, then type a new audience name so the sync appears. **[Live: Scaling, Pixels, Dropship]**
7. Ignore the opportunity score; Meta says it doesn't affect delivery. **[Live: Scaling, Pixels, Dropship]**
- Engine: `preflight` blocks a launch until every item above is confirmed.

### 4.4 Overspend refunds [Start Here: Meta Refunds For Overspending]
Meta sometimes overspends budgets or ignores caps. Claim the money back:
1. **Evidence first:** screenshots of the set budget vs actual spend; ad account ID, campaign names, transaction/payment ID.
2. **Eligibility:** refunds or credits come only for Meta glitches, outages or verified bugs, not for our own budget mistakes.
3. Contact the rep, or support (faster on mobile). Describe the overspend and cap breach plainly, then choose *Claim refund for ad spend* → the ad account → *Other ad issue*.
4. Attach the Meta Status page and the budget-vs-spend evidence, and list every affected account ID.
5. Stay polite (the agent may not know about the outage), give a realistic loss estimate when asked, and follow up until the ticket closes. Persistence wins.

---

## 5. Account structure (M4)

### 5.1 Pick the phase
| Phase | When | Build |
|---|---|---|
| **M0: First $100/day** | New account, or prospecting under ~$250/day | One `Prospecting_CBO`, `Broad_Pack_1`. **No scale, no retargeting**, minimums optional (§5.4), and retention only at a tiny budget. ONE suggested interest only if lifetime spend is under $1,000 or broad has failed. 5–6 creatives can share one pack; never test different interests on different creatives at the same time. **Pausing in M0 is simple: once a week, on a fixed day, pause creatives with low spend AND low conversion value** (the 13-question tree is for M4). Goal: reach **$250–500/day** quickly; if you are near break-even at $30/day, go to $100/day so data arrives fast enough to decide. Expect to lose 10–20% at first; break-even is a win. Don't judge after 2 days. **[First $100 Setup] [Live: Scaling, Pixels, Dropship]** |
| **M4 core** | Above that | **Prospecting CBO + Retention.** Add Retargeting, Catalog and Scale only when a trigger below fires. **[M4 Structure Overview] [NEW: Current Structure] [Live Q&A 8/31]** |

### 5.2 Prospecting CBO: campaign and ad set [M4 Prospecting]
1. Create → **Sales** → name `prospecting CBO` → CBO daily budget → **Highest volume** (no cost cap, no bid cap) → no spending limit → special category if it applies.
2. Pack 1 ad set `avatar_concept_pack1`: all §4.1 ad set defaults.
3. **Exclude Purchasers 180d (pixel), the most important exclusion, plus all-time purchasers (CRM).** Never leave exclusions at "none".
4. Do **not** exclude engaged audiences unless Retargeting has been broken out (§5.7). Retargeting now lives inside prospecting by default. **[Live: Funnel Analysis]**
5. Broad: Advantage+ on, no audience suggestion. The audience should be in the hundreds of millions.
6. Placements: all 23.

### 5.3 Ads inside a pack [M4 Prospecting] [# Of Ads To Launch]
- **4–8 ads per pack** (2 is acceptable, up to 12 if every ad is strong; 4–6 is the live-call sweet spot).
- Group avatar first, then concept. Very different concepts go in separate packs. One creator's package counts as one concept. One product category per pack. **[Live Q&A 8/31]**
- Problem-aware and not-problem-aware ads can share a pack. **[Ads That Scale]**
- Don't make packs of 1–2 ads as a routine.

### 5.4 New packs and minimum budgets [M4 Prospecting] [M4 Overview] [Live: AOV, Optimization Q&A, 9/9]
1. Every new creative round = **duplicate the pack setup** into a new ad set with identical settings.
2. **Pack 1 never gets a minimum.**
3. Packs 2+: ad set spending limit **minimum = 1× target CPA**, for **7 days only**, then remove it no matter what. The one exception: it is crushing above target while still only spending at the minimum. The minimum doesn't depend on how many ads are in the pack. At $1,000/day+ with only ~1 new pack a week, a firmer minimum of up to **2× target CPA** is fine, still inside the 20% pool. **[Live: Optimization Q&A, Q&A 8/31, Retargeting Q&A]**
4. **All live minimums combined must stay ≤20% of the campaign budget.** Example: $1,000/day allows $200 in minimums in total. $50 CPA on a $100 budget means $20, not $50.
5. **No minimums under $100/day.** From $100 to $1,000/day they are optional and the buyer decides (a $20 minimum at $100/day is fine, but not required). From $1,000/day they are standard. **[First $100 Setup] [Live Q&A 8/31, Zombie Q&A, Scaling Q&A]** (see §13 #1).
6. Minimums go only on new **broad** packs, never on interest packs.
7. **Read the signal on day 7:** an ad spending *above* its minimum is a winner that can run alone; one stuck *at* the minimum will die when you remove it. Minimums push spend artificially, so the account can dip a little during those 7 days. That is the price of giving new creative a fair shot under Andromeda: winners reach their plateau weeks sooner. Engine: `minimum_signal`.
8. Never run an ABO "test campaign" that feeds a CBO. It becomes a permanent cost center. **[Live: Product First]**
- Engine: `pack_minimum` (pass `interest_pack` / `one_pack_per_week`).

### 5.5 Interest packs [M4 Prospecting] [Interests] [Graduation System] [Horizontal Scaling]
1. Inside the prospecting CBO, create `interest_[interest]_winners`: *Further limit the reach* → detailed targeting → **one** interest.
2. Pick an interest **once removed** from the brand: shoppers who overlap but aren't your category. For Nike that means Range Rover or Neiman Marcus, not Adidas. Never your own brand, direct competitors, or broad aspirational interests (Ferrari). Avoid tiny audiences (~80k). Keep to a few interests, spread far apart.
3. Fill it **only with duplicated winners**. The originals keep running.
4. If an interest pack is crushing it, don't add ads to it: **duplicate the pack** instead.
5. Use interest packs when broad plateaus, i.e. reach flattens while spend and impressions rise.

### 5.6 Retention (core) [M4 Retention]
1. Campaign `retention`, Sales, daily CBO **≤10% of prospecting** ("not law"). Example: $100 against $1,000.
2. Ad set `purchase_180 days`: include Purchasers 180d, all placements, Purchase event.
3. Ad set `purchase_all time`: include the CRM all-time list, exclude Purchasers 180d, and untick "use as suggestion".
4. With little data, merge the two into one all-time ad set.
5. Ads: all winners, catalog ads, new arrivals, bestsellers, restock alerts, offers, buy-again. Aim for variety, not hard selling.
6. **Manage by frequency, not ROAS** (§8.2). Small $5 minimums on small ad sets are fine.
7. Subscription businesses: never target current subscribers; target churned users instead.
- Engine: `retention_budget`.

### 5.7 Retargeting (optional, about 50% of brands) [M4 Retargeting] [NEW: Current Structure] [Live: Product First]
**Trigger:** in *Breakdown → Audience segments* on prospecting:

| Engaged share of prospecting spend | Read | Action |
|---|---|---|
| under 10% | starved | Check segments and exclusions. Validate with a $5/day retargeting campaign on the same lists. Break out only if truly starved. |
| 10–25% | healthy (20–25% still fine) | Keep retargeting merged. |
| 25–45% | watch | Meta spends on engaged people first, and the share rises whenever budget is cut. More creative won't fix it; more spend will. At small budgets a breakout saves only a few dollars. |
| 45%+ | act | Break out Retargeting and exclude it from Prospecting, or raise spend. |

High-ticket offers run higher. Also weigh frequency and the drop from reported to incremental ROAS. **[Live: Scaling Q&A, Q&A 8/3, 8/31]**

Build:
1. Campaign: Sales, CBO, with a budget starting below the current engaged spend (example: $3k/month engaged → ~$70/day).
2. Ad sets:
   - `Website Visitors 30d` (exclude all purchasers, expansion off)
   - `ATC/IC 90d` (non-purchasers)
   - optional `Engagers 14–30d` for big followings (exclude visitors, ATC and IC; cap it with a max if it hogs spend)
3. Then exclude all of these audiences from prospecting.
4. Inject new objection-handling ads and prospecting winners into the existing retargeting ad sets. Don't create new retargeting ad sets. Raise the retargeting budget only when it is well above goal and 7-day frequency is not near 15–20. **[Live: Retargeting Q&A]**
- Engine: `engaged_share_check`.

### 5.8 Catalog retargeting (add-on) [Catalog Retargeting Retention] [Live Q&A 8/3, 8/31]
1. Duplicate Retargeting → Advantage+ catalog ads → Shopify catalog → CBO **$5–10/day** ($10–20 for separate engaged and existing catalog campaigns).
2. One ad set, `ATC + visit_14 days`: a catalog audience of people who viewed or added to cart in 14 days. **Exclude purchased 14d at the ad set level.**
3. Catalog ads in prospecting tend to spend on the engaged audience. Check the breakdown: if the catalog pack already favors engaged, leave it. If it spends mostly on New or hogs the CBO, make the prospecting catalog pack New-only and run a separate one-ad-set retargeting catalog campaign, monitored closely. **[Live: Optimization Q&A, Q&A 8/31]**
4. Multi-advertiser ads are OK here (retargeting/catalog), **never** in prospecting. The toggle is at the **ad** level (Ad setup → Format, under *Show more settings*), so check every prospecting ad. **[Multi Advertiser Ads, video]**
5. Big catalog and Retention not working: relaunch Retention as catalog ads. Only the copy differs from the retargeting catalog; cross-sell there. **[Live: Retargeting Q&A]**

### 5.9 Scale campaign (highly optional) [M4 Scale] [Graduation] [Live Q&A 8/24, 8/31]
- First choice: just raise the prospecting budget (§9.1).
- Use Scale only for **1–3 home runs** (5 at most): ads already in the top 10% of spend and above target on incremental. You should be able to name every ad in it.
- One proven ad keeps losing spend to new packs that then flop: set a minimum of about 50% on the winner's ad set, or give that ad its own campaign and let new packs test beside it. Then iterate it hard. **[Live: Product First]**
- Campaign `scale`, CBO, no ad set limits, all placements. Exclude everything targeted elsewhere. **Duplicate** the winners into it; the originals stay live.
- If an ad dominates prospecting **and misses KPI**: set a **max %** on its pack (e.g. 80% → 60%, or about 50%) instead of killing it, and evaluate over 2 weeks. **[M4 Scale] [Live: Optimization Q&A]**

### 5.10 Migrating an existing account [NEW: Current Structure → M4]
1. Make the **highest-spending campaign** the prospecting CBO. Switch it from ABO to CBO if possible; otherwise pick an existing CBO.
2. From now on, launch new packs inside it. **Don't pause, regroup or consolidate** working ad sets.
3. Trim duplicates, zero-spend copies and clear losers (example: a 0.59 ROAS on $3.8k is an easy cut). Move proven creative in.
4. Decide on Retargeting from the segment breakdown, on Retention from existing-customer frequency (64 is "astronomical"), and on Scale from incremental winners only.
5. Never start from scratch. Never build a second system next to the first. Keep a working legacy ABO.

### 5.11 Naming
| Object | Name |
|---|---|
| Prospecting campaign | `prospecting CBO` (`Prospecting_CBO` in M0) |
| Broad pack | `avatar_concept_packN` (optional `broad_` prefix; avatar and concept are mandatory) |
| Interest pack | `interest_[interest]_winners` |
| Retention | `retention` → `purchase_180 days`, `purchase_all time` |
| Retargeting | `Website Visitors 30d`, `ATC/IC 90d`, `IG engagers 30 days` |
| Catalog | `ATC + visit_14 days` |
| Scale | `scale` |
| Klaviyo lists | `ads_[event] [days]` |
| UTMs | source = paid social · medium = ad set name · campaign = campaign name · content = ad name |

---

## 6. Creative system

### 6.1 Volume [# Of Ads To Launch] [Live calls]
```
New ads per week = max(2, ceil(monthly spend ÷ $10,000))
Proven-concept share: 13% at $10k/mo · 53% at $100k/mo · 80% (cap) at ≥$200k/mo
```
- **Quality beats volume.** If you can only make 3 good ads, launch 3. "Hit rate is what matters." Mass AI micro-variations do nothing. **[Live: Optimization Q&A, Zombie]**
- Batching every other week is fine (e.g. 6 ads every second Wednesday).
- Statics-only accounts lose roughly 60–70% of impressions, so get video. **[Live: 1 of 1 Content]**
- Engine: `ads_per_week`.

### 6.2 Foundations [3 Ways To Sell] [Andromeda] [Concepts vs Iterations]
- Every ad pulls one lever, **Offer, Mechanism or Education**, and the **Avatar** multiplies it. Be specific; vague claims don't get believed.
- Andromeda matches each concept to its audience. The avatar is the strongest targeting input. Format matters too, and Meta delivers to people who look like the person in the ad, so vary the people. **[Live: Hotline]**
- A new concept comes from the same avatar with a new template, or a new avatar with a proven template. Big accounts run ~10–50 concepts.
- Keep 1–2 core avatars and add more over time. **[Live Q&A 8/31]**

### 6.3 Weekly flywheel [The Flywheel]
1. **Monday:** launch the new packs.
2. Wait **7–14 days** before judging (14 under $1k/day, 7 at $1k+/day).
3. **Analyze:** the top-spending ads that hit KPI on incremental attribution are your winners.
4. **Develop:** mark them as validated concepts (green row in the ad builder).
5. **Iterate:** 1–6 iterations per brief (more only at very high spend), changing one layer at a time.
6. **In parallel, steal like an artist:** competitor concepts that repeat in the Ad Library, rebuilt with your own call-outs.
7. Friday is the first pass; the following Monday you brief winners. After a few cycles, there are new ads ready every Monday.

### 6.4 Ad builder and briefs [Ad Building] [Creative Briefing Template] [How To Create Avatars] [Avatar Ad Examples]
- **Ad builder columns** (from the course sheet): Core Concept (Template + Avatar + Outcome) · Template or Inspo · Avatar Wants/Needs (Outcomes/Purpose) · Call-outs (Mechanisms / Education / Offer) · Iterations (specific ad details) · Iteration/New · Format · Status · Drive link · Brief link. Fill order: avatar → product → core concept. Green row = validated concept.
- **Template library:** the course's static-template decks name each template with a "why it works" line, e.g. *Native Catch* (looks like an organic post), *Us vs. Them Throwdown* (instant contrast; Us = mechanism, Them = the gap) and a Reddit-thread native. Re-check the decks every few weeks; ugly-ad formats that stopped working get removed. **[Image Ads Templates, video] [Ad Building]**
- **Avatar build:** fill the brand guidelines doc in 15–20 minutes (links, key messages, starting avatar, main desire, education, mechanisms, 3 competitors, banned claims). Then run the mega prompt in Claude with deep research to get 20 problems, solution angles and 5 avatars. Treat the avatars as starting points.
- **UGC brief, two parts** (course template fields):
  - Header: priority · deadline · formats/sizes.
  - Internal: core concept · template(s) or inspo · avatar wants/needs · call-outs (features, problem → solution, offer) · iterations.
  - Share with the creator: **3 hooks** · important call-outs (must be captured) · additional shot list (images and video). One good brief yields 20–30 assets.
  - Don't over-brief. Ask for a second format and 3 hooks per package. **[Live: Hotline]**
- **Pre-ship check:** can you say who the ad is for in one sentence? Does the first line or frame signal that person?
- Creators: Meta Creator Marketplace (email AND DM), Billo, Instagram organic. When a creator works, spend heavily on them.

### 6.5 Video structure [Video Ads: Core Components] [Ads That Scale] [Live: Scaling Q&A]
**Micro-hook** (pattern break) → **Hook** (2–3 sentences max, with an avatar callout) → **Problem**, shown graphically → **Product as the easy solution** → **Proof** (data, UGC, before/after) → **CTA + offer**.
- First-touch videos: median **34 s**; build **30–60 s**, problem → solution.
- Iteration anatomy: lead-in 1–3 s, hook 3–5 s, body, CTA 3–5 s. Swapping the body or the hook makes a "different ad".
- Higher ticket gets longer ads; low ticket gets several short ones.

### 6.6 Brief for the top and bottom of the funnel only [Live: Hotline, 1 of 1 Content, 8/31]
- **Top:** big, graphic problem → product as the solution → offer and proof. These hit rarely and take the most spend.
- **Bottom:** statics answering real objections (price → "lasts 2× longer"). You can make them in a day.
- Don't brief the middle; misses land there naturally.
- About **20–30% of ads call out the offer directly**. No deadlines on evergreen offers.

### 6.7 Getting more from winners [Ads That Scale] [Horizontal Scaling]
When one ad takes the spend, iterate on it **immediately**:
- new voiceover, music, hook start, copy
- statics made from the video
- different landing pages (home / PDP / collection)
- pre-selecting the expensive variant
- splicing it with another winner
- an interest pack

Expand a winning **angle** into its iterations. Expand a winning **avatar** into its other problems.

---

## 7. Testing and judging

### 7.1 Windows [The Flywheel] [Pausing Ads] [Live: Ads That Scale, AOV]
- Creative judgment: **14 days under $1,000/day, 7 days at $1,000+/day**. Under ~$200/day use 7-day windows at minimum. Results settle at roughly **10+ conversions a day**; tighten windows only as volume grows.
- Always read in this order: **14d → 7d → 3d → yesterday + today.** Judge KPIs at the **campaign** level first.
- Engine: `judgment_window`.

### 7.2 Columns to keep saved
Spend, purchases, cost per purchase, ROAS, AOV, CTR, CPC, CPM, frequency, ATC, cost per ATC, IC, cost per IC, attribution setting, plus **Compare attributions → 7-day click and Incremental** (incremental purchases, cost per purchase, ROAS). **[Pausing Ads] [Graduation] [Attribution]**

### 7.3 Pausing: the 13-question tree [Pausing Ads]
Default = **do not pause**. Uneven spend is a feature: a few ads should take most of it. Go through the questions in order:

| # | Question | If… |
|---|---|---|
| 1 | Hitting KPI? | Yes → **KEEP**, however old it is |
| 2 | Reacting to one bad day? | Yes → wait |
| 3 | Slow morning or weird attribution? | Yes → wait |
| 4 | Post-sale, post-holiday or post-event? | Yes → wait (grace period) |
| 5 | Pixel/tracking confirmed OK? | No → fix tracking first |
| 6 | Check 7-day click vs incremental | Read both before deciding |
| 7 | Mid-funnel: cost per IC ≤ average? | Yes → **KEEP**, it "has legs" |
| 8 | Going viral (CPM/CTR wildly off the account)? | Yes → **max % on the pack**, don't pause |
| 9 | Spending on the wrong demographic? | Yes → **max % on the pack** |
| 10 | Spent ≥ **2× target CPA**? | No → wait |
| 11 | Any purchases or results at all? | No → **PAUSE** |
| 12 | Within 50% of KPI? | Yes → keep for now |
| 13 | Spent ≥ **3× target CPA** and still ≥50% off KPI? | Yes → **PAUSE** |

- Window **7–14 days** minimum. Turn off **ads, not packs**; kill a pack only if it goes 0-for-5 or it's a sale pack. **[Live Q&A 8/24]**
- Q12 nuance: an ad that has sat within 50% of KPI for a long while (2+ windows) can be considered for a pause. **[Pausing Ads]**
- Q13 with the account at goal: a pack taking ~50%+ of spend gets a **max of ~50%** and a 2-week read instead of a pause. A smaller ad far over CPA (e.g. $135 vs $40) stays on while the account hits goal; pause it if the account falls below goal. **[Live: Optimization Q&A, Scaling Q&A]**
- **Never kill a high spender while the account is at target.** Killing it gives a 3–7 day spike and then a slump; "deleting negative ads is usually a race to zero". Check its cost per ATC/IC and incremental ROAS. If it truly lags, cap its pack instead. **[Live: Optimization Q&A, 8/24, Ads That Scale]**
- Ads spending under ~$50/month are funnel support. Don't kill them for noisy ROAS. **[Ads That Scale]**
- Cost per ATC is the early proxy: benchmark it per campaign over 30+ days (example: $20 cost per ATC ≈ 2.0 ROAS; $10 per ATC ≈ $30 per purchase).
- Engine: `pause_decision` (returns KEEP / WAIT / PAUSE / CAP_ADSET / FIX_TRACKING plus the question number; pass `account_at_goal` and the ad's `adset_spend_share`).

### 7.4 Graduation [Graduation System]
1. Prospecting campaign → Compare attributions → **Incremental**.
2. Winner = **top 10% of account spend AND incremental ROAS at or above your baseline** (example baseline: 1.2). High ROAS on low spend is noise and never graduates.
3. Duplicate winners into interest packs and Retention (and Retargeting if it exists). Only 1–3 home runs go to Scale. The original always keeps running.
- Engine: `graduation`.

### 7.5 Breakout winners (daily, automatable) [Claude: Unlimited Ads Workflow]
An ad qualifies if it was **launched in the last 30 days**, has **≥10% of account spend** and **ROAS above the account average** in any 7/14/30-day window. ROAS exactly at the average counts as a borderline include. Post one Slack message per day (or "No new breakout winners today.") and brief iterations of each winner. Engine: `breakout_winners`.

### 7.6 Shotgun & Sniper: the ONLY exception to CBO packs [Shotgun & Sniper] [Live Q&A 8/24]
Use it **only** if you launch dozens of new creatives or products every week (30–50 products a day). Otherwise never: "45 videos on M4 and one on shotgun."
- A new **ABO campaign** per creative round, **one creative per ad set**, all retargeting and customers excluded.
- Ad set budget = target CPA (or target cost per IC/ATC if cash is short).
- **Kill switches, checked manually every day** (never via automated rules):
  - spend ≥ cost per ATC with 0 ATC → kill
  - spend ≥ cost per IC with 0 IC → kill
  - spend ≥ CPA with 0 purchases → kill, but only after the early days
- Survivors that pass the **7-day gauntlet**: switch the campaign ABO→CBO, or raise the budget **≥25%/day** while the targets hold.
- Compute every target on the attribution you judge on. Engine: `shotgun_targets`, `shotgun_kill`.

### 7.7 Zombie campaign (optional, high-volume accounts) [Live: Zombie Campaigns] [Live Q&A 9/9]
"Not law": an extra tool, mainly for accounts at $500k+/month.
1. Campaign: Sales, CBO, bid strategy **Bid cap = break-even CPA exactly** (not a cost cap).
2. Ad set: max conversions, Purchase.
3. **Exclude everything** the other campaigns can reach: purchasers, visitors, ATC, engaged.
4. Buckets:
   - **Fatigued** (worked, then tapered)
   - **Duds** (never spent; ads stuck at $2–3/day after their minimum)
   - in-between ads
   - organic posts that don't sell
5. Never put sale or time-sensitive ads in it.
6. Budget ≈ **1× target CPA per day**. It usually runs about 20% under budget; zero spend is a feature. **Never raise the bid above break-even.**
7. If a zombie ad spends well above target, relaunch it in prospecting.
8. Feeding it: an ad eating ~90% of its pack while missing target moves to the zombie so the other ads get a turn. A dead concept (all ads at $2–3/day after the minimum): move one ad, pause the rest. Use the post ID so comments and likes carry over. **[Live Q&A 9/9]** Engine: `zombie_check`.
9. Never "test" caps against highest volume with the same creative: caps always look more efficient and lose on volume.

---

## 8. Optimization

### 8.1 Daily anomaly check [Claude: Anomaly Dashboard]
Compare **yesterday vs the day before**, **last 3 vs prior 3**, **last 7 vs prior 7**, and **yesterday / last 3 / last 7 vs the 30-day average**. Use primary metrics (spend, ROAS, CPA) and diagnostics (CPC, CTR, CPM, frequency). Flag changes ≥ **20%** (30–40% to see only big moves). If primary metrics moved while CPC/CTR/CPM stayed flat, look for a structural cause first, such as a sale ending, a budget shift or tracking. Engine: `anomalies`.

### 8.2 Frequency [Frequency Management] [Live Q&A 8/3, 8/31]
Frequency = impressions ÷ reach.

| Audience | 7-day | 14-day | 30-day |
|---|---|---|---|
| Prospecting | 2–3 | 2–5 | 2–7 |
| Retargeting | ≤5 | 5–10 | ≤15 |
| Existing customers | 2–4 | 4–10 | ≤15 |

- Prospecting at 3.5 (7d) while above target is fine; at 5 (7d), dig in even if above target. You can't scale into a frequency of 6 on new customers.
- Retargeting above 15 over 30 days: **cut ~20%** even when ROAS is above target, and move the cash to prospecting. Retargeting at 2 over 14 days means you probably need to spend more.
- Retention/retargeting should never exceed 10 over 7 days.
- Engine: `frequency_check`.

### 8.3 Diagnosing a drop [Live: Funnel Analysis, Product First]
1. A drop = results down **20–30%** beyond normal noise. Don't react to less.
2. Compare equal periods, before vs after: **CPM → CPC → cost per ATC → cost per IC → CPA**, plus AOV, CVR and new/engaged/existing. Use custom columns, run the same funnel in Shopify, and read on incremental attribution.
3. The **first stage that broke** tells you where to look:
   - CPM → auction or audience
   - CPC → creative
   - ATC → landing page, offer or price shown
   - IC → cart/checkout changes, upsells, shipping
   - CPA → checkout, payment or trust
4. Then check **where spend moved**: ad-level spend share period over period, then the age, gender, placement and country breakdowns, one by one. Budget a 45–60 minute session.
5. Steer spend back with **value rules** (start around 25–30%, 30–50% is the sweet spot, above 50% is unstable; value rules don't reset learning), or with a **max %** on the ad set that grabbed spend.
- Benchmarks: roughly 50% drop-off at each step after ATC (100 ATC → 50 IC → 25 purchases). Site CVR is typically 1–2% (about 1.2–1.5% at a $70 AOV). Cost per ATC rising 3–15% when spend doubles is normal; doubling is a concern.
- A sudden overnight drop at ~$100/day is almost always a spend shift between ads. Compare every metric before and after. **[Live: Product First]**
- A pack with good CTR, ATC and IC but zero sales broke at purchase: remake the ad with a clearer CTA and offer (hook → offer → body) before calling the concept dead. **[Live Q&A 8/17]**
- Engines: `drop_diagnosis`, `funnel_health` (per-step rates, site CVR), `scale_funnel_check`.

### 8.4 Audience-segment split (weekly) [Advertiser Settings] [NEW: Current Structure] [Vertical Scaling]
Breakdown → Audience segments on prospecting: spend, revenue, ROAS and frequency for New / Engaged / Existing. Most spend must go to **New**. Use it for the Retargeting and Retention triggers (§5.6–5.7) and before every scale move (§9.1). Engine: `engaged_share_check`.

### 8.5 Breakdowns and value rules [Placement Breakdown] [Country / Geographic Testing] [Value Rules] [Audience Breakdowns]
- **Placements** (account level, last 14 days, sorted by spend): the top 6 must be **FB/IG Feed, Stories, Reels**. A core placement at about 1% of spend is a red flag, usually because it has no creative for it.
  - Fix in this order: (1) make the creative, e.g. 9:16 video; (2) ONE new ad set with the weak placements excluded, with a min of 1× CPA for at least 1 week if needed; (3) value rules by placement; (4) last resort, remove the placement everywhere.
  - Never edit placements on a live ad set.
- **Geo:** with one country running, add a new country as a **new pack of winners only** in the prospecting CBO. Run ≥7 days without a minimum, then 7 days with **min = average CPA**. Remove outlier countries from the ad set's targeting; the course example cut one at ~2× the account CPP. Never split a working multi-country campaign into one campaign per country; use value rules instead (+25% for a strong country). **[Live Q&A 8/24]** Rebuilding a messy multi-country account: keep the countries that drove ~80% of revenue, relaunch smaller, add the rest back later; only target languages your ads are in and places you can ship to. **[Live Q&A 8/31, Retargeting Q&A]** Engine: `pareto_cut`.
- **Value rules** (Advertiser settings → Value rules → rule set; apply in the ad set): start with **a decrease of 25% or less** on a weak segment found in breakdowns. Never act on a gap of 5–10%. Perceived ROAS = revenue × (1 + adj) ÷ spend. "An elimination game, not an increasing game." Engines: `placement_check`, `geo_check`, `value_rule_effect`.

### 8.6 Learning phase [Understanding the Learning Phase] [Dictionary] [Live Q&A 8/3, 8/17]
Ignore "learning limited" and don't spread budget evenly to clear it. A pack that is learning-limited after its minimum ends simply isn't a winner. Watch **% of spend in learning (account overview, 7d)**: ~11% is healthy; constantly at 85–90% means you are making too many changes. After a big change, wait about a week and only add iterations meanwhile. Engine: `learning_phase_check`.

### 8.7 Day of week [Day Of Week Analysis] [Live: Ads That Scale]
1. Ads Reporting → new report "DOW". Columns: spend, purchases, purchase value. Breakdown: Day. Use the **longest range possible, Monday through Sunday**.
2. Export the CSV into Sheets and add `=WEEKDAY(A2)` (1 = Sunday). Build a pivot with CPA = spend ÷ purchases and ROAS = revenue ÷ spend, and color-scale it.
3. Raise the prospecting budget on strong days and lower it on weak days. **Solve the down-step so the week still totals base × 7**, because +X% and −X% are not symmetric. Change budgets manually (or with automated rules once daily, prospecting only, with a max cap and a matching "down" rule).
4. Big accounts: check cost per ATC around midday and nudge the budget the same day.
- Engine: `dow_budgets`.

### 8.8 Attribution [Attribution Settings] [Dictionary]
- Under ~$10k/month (or a couple hundred dollars a day): **7-day click / 1-day view** (+ engaged view) everywhere.
- Incremental attribution only for very large spend ($100k–300k+) or 100–200k+ followers. If view-through is inflated, use incremental or 7-day click only.
- **One setting per account.** The only exception: all prospecting on one setting, all existing-customer campaigns on another. Pick one and stick with it; never test attribution settings side by side.
- Always read *Compare attributions → Incremental* before scaling or graduating.

### 8.9 Max conversions vs max value [Max Conversions vs Max Value] [Live Q&A 9/9]
- Default: **maximize number of conversions**, especially with few signals or steady AOV. Don't use value until you have thousands of dollars in spend.
- Switch when AOV varies a lot, or when one cheap SKU takes most of the spend (e.g. 87%). Build a new **max value** CBO from the top ads, run it **alongside** the max-conversions campaign with similar spend, and compare **CPA, ROAS and AOV**. Expect max conversions to win at first. Never judge max value on CPA alone. Under max value, products don't need to be split up.

### 8.10 Funnel and offer levers [Live: AOV and Free Shipping] [Live: Product First, Hotline]
- Set the free-shipping threshold so **~75% of orders qualify**: count your last 100 orders, adjust, and re-check weekly. Order of work: funnel analysis → free shipping → price.
- Shipping fees of $4.99 or less barely hurt CVR; above $5 they do. Use .99 pricing. Watch price breakpoints (99 → 129 usually loses).
- Prefer value-adding evergreen offers (buy 2 get 1) over discounts. Test offers in evergreen weeks, never on sale weekends. Judge offers on profit per order and RPV.
- Focus on **revenue per visitor**, compared with CPC.

---

## 9. Scaling

### 9.1 Vertical scaling: the default [Vertical Scaling] [Live: Product First, 8/31]
Run five checks before every move on the **prospecting CBO**:
1. You know the King Goal.
2. You are **above** it on **14d and 7d**, and the **last 3 days** hold.
3. **New**-segment ROAS supports it (Audience segments).
4. **Incremental** New ROAS is acceptable. Below target is allowed, but use the smallest step and expect that return.
5. Multi-day stability: read 14 → 7 → 3 → 1 days.

Move sizes:

| Situation | Step | Cadence |
|---|---|---|
| Default | **+10–30%**, scaled to how far above goal you are | every **48–72 h** |
| Multi-thousand $/day | **+10–15%** | 48–72 h |
| Around $100/day | bigger steps, up to **+50%** (100 → 150 → 225) | 48–72 h |
| Far above goal (e.g. 14d 7.5 / 7d 5.8 vs 3.5 target) | **+20–30%** on every 3-day window above target; **+30–50%** for a short spell to catch up | each 3-day window |
| **Smashing** (≥ 2× target on 7d and 3d) | **double**, if the delta check passes: current daily revenue ÷ new spend ≥ target, even if the new money converts nothing | faster |

- **Below target: hold** and fix creative; the twin engine never stops. Near target (e.g. 1.03): reach target before scaling. If ROAS slides during steady increases, stop increasing and let it settle.
- After a move, expect **frequency, CPM and CPC up and ROAS down** for a while. New money reaches colder people. If cost per ATC is flat, **hold the line**; don't panic-cut.
- Monitor the full funnel, incremental ROAS by segment period over period, and **blended MER**.
- Retargeting and retention are not scaled this way; they are managed by frequency.
- Recovering a previous spend level (e.g. back from $20k/day): doubling 500 → 1,000 → 2,000 → 3,000 is fine, then $1k steps. Judge it on incremental. With less spend than before, make fewer concepts and raise their quality until spend is back at $5–10k/day. **[Live Q&A 8/31]**
- After each move, read cost per ATC/IC: +3–15% is normal, doubling means stop (engine: `scale_funnel_check`). Top 5–10 creatives taking 60–70% of spend is expected; iterate those.
- One ad carrying the account and above target: just raise the budget. No scale campaign, no breakout. **[Live Q&A 8/31]**
- Engine: `vertical_scale` (pass `prior_proven_daily` + `incremental_kpi_7d` for the relaunch path).

### 9.2 Horizontal scaling [Horizontal Scaling]
- **Internal (always):** iterate winning angles, expand winning avatars into new problems, add interest packs. All inside the prospecting CBO.
- **External (new campaigns), only for:** (1) sales/drops/promos; (2) huge margin or price tiers that max value can't fix, not $50 vs $75; (3) a 1–3 ad scale campaign.
- Not at ~$100/day. Be careful at $1,000/day.
- **Never duplicate the CBO with the same ads "for more spend".** Rank opportunities and fill the best one first. If vehicle 2 returns less than vehicle 1, kill vehicle 2.
- Engine: `horizontal_readiness`.

### 9.3 Twin engine [Twin Engine]
Raise spend **only when above goal**, and keep creative output **always on**, at the §6.1 rate, whether you are above or below goal. The two are not coupled: don't raise budget because you launched ads, or launch ads because you raised budget. Success = spend up while ROAS stays **flat**.

### 9.4 Cost controls [Cost Controls] [Live: Scaling Q&A]
- Only at **~$50–100k+/month**. Below that, use Highest volume. Bid caps only for very advanced operators. Target ROAS is acceptable.
- Cost cap = **real target CPA** (don't game it). Size the budget so actual spend averages **~80%** of it. 80% means it is working: don't tweak it to force spend. Over 90–95% means the cap is too loose (raise budget). Around 30% every day means re-check AOV, LTV and the true target before touching the cap. **[Live: Scaling, Pixels, Dropship]**

| Cap hit? | Budget fully spent? | Action |
|---|---|---|
| Yes | Yes | **Raise budget** with the same cap. Optional: lower the cap $1–2, never $10. |
| Yes | No | Working as intended. If the cap is below the true target, raise it **$1 at a time**, holding a few days per step. Otherwise make creative. |
| No | Yes | Question whether caps fit at all. Iterate existing creative. The cap never goes above target CPA. |
| No | No | "Double bad": probably stop using caps. Make new creative. |

- Engine: `cost_cap_action` (pass `budget_utilisation`).

### 9.5 Sales and BFCM [How To Run A Sale] [Horizontal Scaling] [Live: Ads That Scale, 8/31, 9/9]
1. **Every limited-time sale (3/5/7/14-day, and Black Friday) runs in ONE separate campaign** with its own sale-period budget. Never put sale ads into the evergreen CBO.
2. Ad sets by **avatar** (or by concept if there's one avatar). Minimal exclusions, and review audience segments inside it. For sales of 15+ days, split into prospecting and existing ad groups.
3. **Kill faster than normal.** Use secondary kill switches on cost per ATC and cost per IC. Never pause the high spenders unless they are clearly losing.
4. **Scale with big jumps** against the sale KPI. Intraday +10–20% is fine, and raising the budget several times a day is OK. Avoid repeated cuts.
5. Evergreen offers (e.g. $25 off $75 welcome) go into the existing prospecting CBO, not a sale campaign.
6. Before Q4, use the next ~20 days to fix structural problems (e.g. the max-value switch).

---

## 10. Lead-gen variant [Must Watch For Lead Gen] [High Ticket] [Low Ticket] [Local Services] [Live calls]
- Objective **Leads**, one conversion location per ad set. Prospecting keeps the same CBO + pack system.
- **Never optimize for raw Lead.** Use the deepest stage that still gets **≥10 conversions a week**: qualified lead → booked call → showed → closed. At $20–30/day use "qualified form submitted"; expect ≥25% drop-off to booking.
- Score leads as qualified / not qualified from past revenue. **Send only qualified leads** to Meta, via CAPI or offline events from the CRM (Zapier/Make), into a standard event (Complete Registration or Purchase). Never pixel disqualified leads, and don't mix raw-lead and qualified packs in one CBO.
- Destination: your own landing page (default for high ticket). Instant forms are discouraged because they can't track downstream events. Call ads need instant pickup; schedule them with a lifetime-budget campaign that stops 30 minutes before phones close. Ungated VSLs beat gated ones, and live webinars beat evergreen.
- Retargeting = leads/applications not yet converted. High-ticket monthly-recurring businesses exclude all customers everywhere.
- No scale campaign at $200–300/day or less. Local: radius targeting, max conversions, location call-outs in creative, bid caps only at $30–50k+.
- KPI = **cost per qualified lead** and downstream outcomes, not CPL. Local CPLs are naturally higher than national ones; compare qualified rates, not raw CPL.
- **Work the target backwards:** target cost per call/lead/trial = value per sale × the share that closes. Example: a $100 job with 10% of calls closing = $10 per call to break even; $100 per paid subscriber with 10% of trials converting = $10 per trial. Engine: `reverse_target`.
- **Conversion locations, ranked** for high ticket: Website (applications, VSL → calendar, quizzes) → Messaging (needs instant human replies) → Call ads (highest intent, needs pickup by the 2nd ring) → Instant forms (avoid, except webinar invites). Instant forms can only optimize for the form fill itself. **[High Ticket] [Low Ticket] [Live Q&A 9/9]**
- Qualify inside the booking flow: the lead thinks they are booking, qualifying questions decide whether the calendar shows. Expect to disqualify a large share (the course examples run 90–95%), and never send DQs to Meta. Start on *qualified application*; move to *booked call* once volume allows. **[Live Q&A 9/9, 8/3]**
- Lead-gen agencies need access to the client's closed-sale data (sign an NDA if needed) and a CRM → Meta sync for closed-won. **[Live: Optimization Q&A]**

---

## 11. Claude and AI operations [Claude: Start Here] [Facebook MCP Setup] [Reporting Suite] [Anomaly Dashboard] [Unlimited Ads Workflow]
- **Connector:** Claude → Settings → Connectors → add `https://mcp.facebook.com/ads`. **Read tools "always allowed"; anything that creates or changes stays "needs approval".** On create prompts, choose *Allow once*, never *Always*.
- Building campaigns through Claude is allowed, but the course author prefers Ads Manager. Our skills therefore **stage drafts** and require explicit approval before anything goes live (see `fb-launch`).
- Reports: a Meta dashboard (goals bar, top 5 ads by spend, recently launched, weekly/monthly recap, 7-vs-7 full-funnel module); the anomaly detector (§8.1, daily at 6 am); the breakout-winner detector (§7.5, daily at 4 am, posted to Slack, handed to the creative team or SuperScale for iterations).
- AI creative: fine for iterations and objection statics. No fully synthetic AI performers in ads served to New York. "Slop" hurts trust. **[Live: AI Creative Flywheel]**

---

## 12. Checklists

**Launch checklist (every new pack)**
- [ ] Preflight passed (§4) · King Goal and target CPA written down
- [ ] New ad set duplicated from the pack template. Name `avatar_concept_packN`.
- [ ] 4–8 ads, one concept/avatar group. 1:1 + 9:16. 2–5 unique primary texts and headlines. ≥4 site links. UTMs in URL parameters.
- [ ] Enhancements: nothing that modifies the media
- [ ] Exclusions: purchasers 180d + all-time (plus retargeting audiences if Retargeting is broken out)
- [ ] Minimum: none for pack 1, interest packs, or under $100/day; optional $100–1,000; otherwise 1× CPA within the 20% pool, and the removal date (day 7) is on the calendar
- [ ] Draft reviewed and **approved by a human** before publishing

**Daily (≤15 min)**
- [ ] Anomaly check · tracking sanity (Events Manager) · remove minimums at day 7 · scale decision if 48–72 h have passed

**Weekly**
- [ ] Pausing tree (≥7-day data only) · graduation · breakout winners → briefs · frequency by swim lane · segment split · new packs launched Monday

**Monthly**
- [ ] Pixel gut check · profit model refresh · placement, geo and DOW reports · free-shipping threshold · learning-phase share

---

## 13. Decisions log: conflicts and team defaults

| # | Topic | What the sources say | SOP rule |
|---|---|---|---|
| 1 | Minimums at low budgets | M0 video: no spend limits "until ~$1,000/day". M4 video computes a $20 min on a $100 budget. Live calls disagree: "$20 minimum at $100/day: yes" (8/31), a $170/day account with minimums is fine if they total ≤20% (Optimization Q&A), but also "you don't need minimums yet at $100/day" (Scaling Q&A) and "$150/day don't set minimums yet" (Zombie Q&A). | **v1.1: none under $100/day, optional $100–1,000 (buyer's call), standard from $1,000.** v1.0 used a $250 boundary; first-hand reading of the 8/31 and Optimization calls moved it. |
| 2 | Retargeting threshold | M4 summary: 20%+ engaged is a red flag. NEW video: ~25% normal. Live calls: 10–20%, 20–25% healthy, worry at the mid-40s. | Soft flag above 25% or below 10%. Decide on frequency and incremental drop-off too. |
| 3 | Retargeting/Scale necessity | M4 videos list Retargeting as optional (~50% of brands). Live calls: "retargeting is now optional", "don't need a winners campaign as much". | Core = Prospecting + Retention. |
| 4 | Budget step size | Vertical (NEW): 10–30% / 48–72 h, 10–15% at large spend, +50% around $100/day, double when smashing. Learning Phase: 50% is OK when well above. Product First call: 20–30% (30–50%) after 3 days above, but "≤10% at $100/day". | Vertical Scaling (NEW video) wins. "Large spend" = **≥ $2,000/day** and "small" = **≤ $200/day** are team defaults. |
| 5 | Optimized website destination | Dictionary: don't use it. M4 Prospecting: select it, unless it's a complex shop targeting one product. | **Follow M4 Prospecting** (newer, dedicated build video). |
| 6 | Descriptions / copy count | Dictionary: 5 descriptions, 5 texts, 5 headlines. M4: ≥2 texts, ~2 headlines, descriptions blank. Live: 5 + 5, or 3 + 3. | 2–5 completely different texts and headlines. Descriptions blank or "+ free shipping". |
| 7 | Hero test split | Transcript: 90/10. Summary: 80–90 / 10–20. | **90/10.** |
| 8 | Creative volume | Calculator: 1 per $10k/month (floor 2). Live calls range from 2–5 a week; one big account ran "40 per $10k". | Calculator rule. Quality first. |
| 9 | Pack size | 4–8 (M4), 4–6 (live), ~15-ad iteration packs (one agency example). | 4–8, up to 12 if all strong. |
| 10 | Within-50%-of-KPI for CPA | Pausing Ads gives only a ROAS example (1.2 vs 2.0). | For CPA KPIs: within 50% = actual CPA ≤ 1.5× target. **Interpretation.** |
| 11 | Learning-phase "healthy" band | Course example: 11% is very healthy; 85–90% constantly is too much. | Healthy ≤ 15% (team default), too much ≥ 85%. |
| 12 | Geo cut line | Example: keep +$10 over a $42 average, cut $85. | Cut at ≥ 1.5× account CPP (team default between the two examples). |
| 13 | Retargeting attribution | Retargeting summary: 7DC/1DV. M4 transcripts: 7DC / 1D engaged / 1DV. | 7DC / 1D engaged / 1DV everywhere. |
| 14 | Engagers lookback | 14d (Overview) vs 30d recommended, 14d for big followings (Engagers video). | 30d by default, 14d for large followings. |
| 15 | Lead-gen volume → event mapping | Summary doc and transcript disagree. | Deepest stage with ≥10 conversions a week. |
| 16 | Advantage+ exclusions | Dictionary is unclear whether exclusions are hard under A+. | Always set them. (Meta's API treats custom-audience exclusions as hard controls.) |
| 17 | Sale timeline | No source gives pre/post-sale day counts. The BFCM calendar training was announced but isn't in the folder. | Gap. Add it when the training is recorded. |
| 18 | Learning-phase exit | Learning Phase video: "~25 purchases"; live: "50 is not real". | Don't manage to it. |
| 19 | Pausing a top spender that misses KPI | Pausing Ads Q13: ≥3× CPA and 50%+ off KPI → pause. Live calls: never pause a high spender while the account is at goal; cap its pack at ~50% and read for 2 weeks; keep a $135-CPA ad while the account hits a $40 goal. | Q13 pauses **unless the account is at goal**: then cap a ≥50% pack, keep smaller "assisting" ads. |
| 20 | Step size at ~$100/day | Vertical Scaling: up to +50%. Product First call (garbled): "at $100/day don't move more than 10%" next to "we're not trying to get from 100 to 110". | Keep the Vertical Scaling video (up to +50%). Flagged as unclear. |
| 21 | Creative volume at very high spend | Calculator: 1 ad/week per $10k/month. Live: a $2–3M/month account makes 100–150 a week (calculator says 200–300); "40 a week per $10k" at $400k/month. | Calculator stays the rule; quality first; big accounts are mostly iterations. |
| 22 | Scale campaign size | Horizontal Scaling video: 3–5 ads. NEW Structure: 1–3. | **1–3 default, 5 max.** |
| 23 | Multi-advertiser toggle level | Summary docs were unclear (ad set vs ad). | **Ad level** (seen on screen in the video). |
| 24 | Engaged-share bands | M4 summary 20% flag; NEW video ~25% normal; live calls: 10% bare minimum, 10–20% usual, 20–25% healthy, 35% at $150/day "not worth breaking out", mid-40s act. | Bands: <10 starved · 10–25 healthy · 25–45 watch · 45+ act (engine `engaged_share_check`). |
| 25 | Retention catalog vs ad mix | M4 Retention: winners + catalog + offers. Retargeting Q&A: big-catalog brands with dead Retention should rebuild it as catalog ads. | Default mix; switch to catalog when Retention stalls and the catalog is large. |

**Course refresh:** the live calls announce a re-record of the Blueprint for late September / early October 2026. When new videos land, re-run the extraction and update this log.

---

## 14. Source index
See [sources.md](sources.md) for every lesson file, its module, and which SOP sections cite it.
