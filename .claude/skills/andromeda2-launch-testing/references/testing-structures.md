# Testing structures — full build steps

Sources: *The Facebook Ads Blueprint* 2026 (M4 structure, First $100, Shotgun + Sniper, geo, placements, sales), its 2026
live calls, Spencer Pawliw's Evolve (3:2:2), Matteo Pellegrini 2026 (volume test). Numbers are practitioner heuristics.

Contents
1. M0 — the first $100/day
2. M4 core — prospecting CBO with packs
3. Retention campaign
4. Optional retargeting split
5. Catalog retargeting
6. Interest-winners ad sets (expanding broad)
7. Geo test packs
8. Landing-page / advertorial / listicle packs
9. Short sales and drops
10. Shotgun + Sniper (high creative volume)
11. Evolve 3:2:2 (DCT)
12. Pellegrini's high-volume ABO test
13. Moving an existing account into M4
14. Lead-gen adaptations

---

## 1. M0 — the first $100/day

- Expect the "early tax": you may lose 10-20% on ads at first; you are paying to learn creative, offer, price and CVR. Don't
  judge after two days; review weekly.
- Campaign `Prospecting_CBO`: Sales · Auction · CBO ~$100/day · highest volume · Advantage+ catalog off.
- Ad set `Broad_Pack_1`: Website · Maximize number of conversions · Purchase · Standard attribution, every window on
  (7-day click + 1-day engaged-view + 1-day view) · all conversions · no spending limits (not before ~$1k/day) · exclude
  Purchasers 180d + customer list · your languages · all placements.
- One interest suggestion **only** if lifetime spend < ~$1k or broad has been stuck at $100/day with no success: Suggest an
  audience → detailed targeting → ONE adjacent interest; rename the ad set (e.g. `Skincare_Suggestion_Pack_1`). It is only a
  starting point; delivery expands from it. Remove when data allows. Never stack interests or test interests with different
  creatives at the same time.
- New creative = duplicate the ad set (same settings) → new pack. 5-6 ads targeting different things can share one pack at
  this budget. Choose your core avatar; three avatars at $150/day "is just not the move yet".
- Goal: $250-500/day as fast as profitability allows (up to 5x more pixel signal), then move to M4.

## 2. M4 core — prospecting CBO with packs

Campaign `Prospecting_CBO`: Sales · Auction · CBO daily (no lifetime unless you need ad scheduling) · **highest volume**
("we're not cost capping it anytime soon") · no campaign spending limit · catalog off · A/B off · declare special ad
categories if they apply.

Packs (ad sets):
- Name `broad_<avatar>_<concept>_pack<N>`; pack numbers run across the campaign.
- Settings identical across packs; the only difference is the spending limit when used.
- 4-8 ads per pack (2 OK when small; up to 12 if all are strong). On ~$150-200/day, stay at 4-5: "you can't force budget
  against eight or ten different creatives in an ad set."
- Group by avatar first, then concept: "If they're really, really different, separate them… if not, group them."
- Packs are containers: campaigns with 100 ad sets are normal.
- New round of creative → new pack. Never inject into a live pack ("let's not mess up the thing that's actively working").
  Iterations of a winner → their own new pack.
- Fair-shot minimum (from pack 2 on, only if new packs are starved): ad set spending limit → daily minimum = 1x target CPA;
  total of all live minimums ≤ 20% of the campaign budget (e.g. $1,000/day → ≤ $200; a $100/day CBO → ~$20); removed after
  7 days no matter what (exception: still at the minimum with ROAS far above target → keep it a little longer). Winner signal:
  the pack spends **above** its floor; losers sit at the floor and decline when it is removed — "you want it to die."
- Maximums: a % daily maximum (not $) on a pack that hogs spend below target (80% → 60%; viral/wrong-demographic 90% → 20%).
  Never leave limits on forever. Percentages survive budget changes.
- Products: hero product/collection takes 80-90% of spend; test other products as a pack in the same CBO (~10-20%).
  Mixed price points (e.g. $20-40 products with a $120 bundle) → a value-optimised CBO beside it (see the scaling skill).
- ABO legacy campaigns still at target: leave them running ("different rocket ships"); launch new rounds in the CBO.
- When migrating ABO → CBO: make the top 5-10 winners "pack 1" of the new CBO as a baseline — a new pack only gets spend if it
  can beat them.

## 3. Retention campaign

- "Facebook, without this setup, is going to drill your existing customers to the dirt."
- `Retention`: Sales · CBO daily ≤ ~10% of prospecting budget (not law).
- Ad set `Purchase_180d`: include Purchasers 180d (pixel) — "further limit the reach", unselect "use as a suggestion".
- Ad set `Purchase_AllTime`: include the all-time customer list, exclude Purchasers 180d. Small brands may merge both.
- A $5/day minimum or a max on one ad set is fine; million-dollar brands run $10/day retention ad sets.
- Creative: all winning ads, catalog ads, new arrivals, bestsellers, restocks, offers — keep them top of mind, don't hard-sell.
- Manage on frequency and reach, not ROAS: existing customers ≤ 2-4 per 7 days, ≤ 15 per 30 days.
- Subscriptions: never target subscribers; target churned customers.

## 4. Optional retargeting split

- Default 2026: keep retargeting inside prospecting (Meta handles new + engaged). Read Breakdown → Audience segments.
- Split it out only if engaged takes > ~20-25% of prospecting spend with high frequency or a big reported-vs-incremental gap
  (or the reverse: engaged is under-served for a high-ticket product).
- `Retargeting` CBO with budget slightly under current engaged spend. Ad sets: Visitors 30d · ATC 90d + IC 90d (non-buyers) ·
  optional IG + FB engagers 14d (max 30d, 1,000+ people, put a max on it — it hogs). Exclude all purchasers; turn expansion off.
- Then exclude every retargeting audience from every prospecting pack.
- New ads in retargeting: inject objection-handling and proven prospecting ads into the existing ad sets, or (if one old ad
  hogs) a new retargeting ad set with a max on the old one.
- Frequency ≤ ~10 per 7 days (15-20 = overspending on the cohort).

## 5. Catalog retargeting

- Duplicate retargeting; campaign level Advantage+ catalog ads on (Shopify catalog); budget $5-10/day.
- Ad set `ATC+visit_14d`: catalog audience "viewed or added to cart from product set", last 14 days; exclude Purchased 14 days
  at the ad set level. Optional second ad set up to 90 days if you lack retargeting creative.
- Multi-advertiser ads: only here (catalog retargeting), never in prospecting.

## 6. Interest-winners ad sets (expanding broad)

- Why: broad delivery only learns from "pockets" similar to past buyers and can plateau; feeding proven ads to an adjacent
  interest gives the pixel new inputs → broad widens → lower CPM/CPC.
- Build: new ad set in the prospecting CBO `interest_<name>_winners`; detailed targeting = ONE interest; everything else as broad
  packs; winners only (duplicates are fine; originals keep running).
- Interest choice: adjacent, "once removed" — not direct competitors (the pixel knows them). Nike → Range Rover, Neiman Marcus,
  not Adidas; heavy-metal tees → horror films; apparel → interior design. Keep audiences large (not 80k people).
- Keep graduating new winners in; if an interest set is crushing it, duplicate it rather than adding ads.

## 7. Geo test packs

- Start with the countries you can ship to efficiently that speak your ad language. One country first if resources are thin.
- New country: a pack in the prospecting CBO targeting only that country, winners only. Wait ≥ 7 days; if no spend, add a
  minimum = average CPA. A separate campaign for 7-14 days is the surest but riskiest test.
- Cut countries far off average CPP (~$85 vs $42), keep ±$10 noise. Weight countries with value rules instead of per-country
  campaigns. Very large cohorts (core English markets vs rest of world) may warrant separate campaigns.

## 8. Landing-page / advertorial / listicle packs

- PDP vs advertorial vs listicle vs quiz: run each as its own pack in the same CBO with the same winning creatives and let
  Meta show which it can scale. If Meta won't spend on the advertorial version, force a minimum for 7 days to prove it.
- Evolve alternative: an ABO `Page-Testing` campaign with congruent ads → new URL vs control.
- On-site split tests (Intelligems, Shoplift) are cleaner than separate pages for price/offer tests.

## 9. Short sales and drops (3-14 days)

- One new campaign outside the core ("so evergreen keeps flowing when it is switched off"), lifetime budget for the sale window.
- Ad sets by avatar (usually one), or by concept if many ads. Minimal exclusions; review audience segments; break out
  prospecting vs existing only for 15-20+ day sales.
- Faster kill switches: KPI plus cost per ATC / IC. Do not pause high spenders unless they are killing you.
- Scale big when above the sale KPI: intraday +10-20%, several upward moves a day are fine; avoid cutting mid-day.
- Evergreen offers belong in the core CBO, not a sale campaign.

## 10. Shotgun + Sniper (high creative volume)

For brands shipping dozens of creatives (or products) every week, especially quick-purchase products; "not the preferred
strategy in many cases". New customers only.
1. Compute cost-pers from the account (same attribution you will judge on): e.g. CPC $0.91, cost/ATC $8.81, cost/IC $14.88,
   CPP $41.24, AOV $79.22 → ROAS 1.92 (break-even 1.9). Ratios ATC→IC 59%, IC→purchase 36% — normally stable.
2. Each round = a brand-new ABO campaign, one creative per ad set; exclude all retargeting and existing customers.
   Never add ads to an existing round.
3. Budget per ad set = 1x CPA; if unaffordable, the IC target, else the ATC target.
4. Kill switches, checked daily by hand (no automated rules — they fire too often): at cost/ATC spend, ≥ 1 ATC or die; at cost/IC
   spend, ≥ 1 IC or die; at CPP spend, ≥ 1 purchase or die. Early on only kill on ATC and IC.
5. Survivors (watched ≥ 7 days): switch the round to CBO, or raise surviving ad sets ≥ 25%/day while they meet the cost-pers.
6. On incremental attribution the cost-pers are higher (e.g. $10 / $17.71 / $50); mixing models kills everything.

## 11. Evolve 3:2:2 (DCT)

- Campaign `<BRAND>//Acquisition//<Country>`: CBO, broad, min $100/day.
- Ad set `Champions Broad`: winning ads by **post ID** (unlimited). New brand: create it empty.
- Ad sets `DCT <#> Broad`: one per concept, 3 visuals × 2 primary texts × 2 headlines; images and videos in separate ad sets.
- At a few hundred $/day keep ≤ 5 live ad sets including Champions; more at a few thousand/day. No min/max limits.
- Test ≥ 3 days; if spend ramps, 7 days. Turn off at ad-set level only: no spend in 3 days → off; little spend after 7 days with
  poor ROAS → off; took most of the spend but the campaign got worse → off after 2-3 days, then make that engaging idea more
  conversion-driven. Winner = majority of spend at KPI AND overall campaign ROAS improved.
- Raw-content campaign (unedited creator footage) and Promo campaign (Broad / Warm 60 / Hot 90) sit beside it.

## 12. Pellegrini's high-volume ABO test

For AI-scale creative volume (10x more ads) without burning budget:
1. ABO campaign per product, optimised on target ROAS or CPA, 7-day click + 1-day engaged-view; exclusions: Klaviyo buyers,
   website purchasers 180d, existing Shopify customers.
2. One ad set per creative batch, ≥ 3 creatives per angle, top-performing countries.
3. Per creative: 3 primary texts, 3 headlines, 1 description.
4. Cut losers early: daily review of cost per ATC, CTR, CPC, CPM, engagement — improving day after day? If not, cut.
Winners graduate to a CBO scaling campaign (ad sets by angle or avatar), bid-cap and cost-cap campaigns for the best; losers
with potential go to the zombie campaign. Under Andromeda 2 prefer the CBO pack system unless volume truly demands this.

## 13. Moving an existing account into M4

- "Don't touch it if it's actually working." Pick the highest-spending CBO closest to a prospecting campaign as the core
  (switch an ABO to CBO in place if possible); launch every new round there as a pack; trim only obvious duplicates and clear
  losers; merge existing-customer campaigns into Retention; decide retargeting with audience-segment breakdowns.
- Inherited "middle-funnel" campaigns (video viewers, engagers): don't rip them out at once; stop feeding them, remove ad sets
  one by one, worst first.
- Don't scrap-and-relaunch as a reset button; don't open a second ad account to scale.

## 14. Lead-gen adaptations

- Never optimise to raw Lead: optimise the deepest event with 10+ per week (qualified application → booked call → closed).
- Send only qualified leads back (CAPI, standard event — Purchase is fine); disqualify hard.
- Landing pages beat instant forms on quality; ungated VSL beats gated. Day-part with a lifetime-budget campaign if calls must
  be answered live.
