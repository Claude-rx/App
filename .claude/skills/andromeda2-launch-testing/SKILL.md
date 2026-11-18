---
name: andromeda2-launch-testing
description: Plans and builds Meta ad launches and creative tests the way Andromeda 2 rewards them — one highest-volume prospecting CBO where every new round of creative goes in as a new pack (ad set) grouped by avatar then concept, a retention lane, short fair-shot minimums, exact Ads Manager settings, a weekly creative quota sized to spend, and kill/keep/winner rules computed from the brand's unit economics. Use this whenever the user wants to launch ads, test creatives, structure a new ad account or campaign, set up testing campaigns, decide CBO vs ABO, figure out budgets for testing, how many ads to launch, when to turn ads off, how to read a test, or restructure a messy account — even if they never say "Andromeda" or "testing". Covers first $100/day setups through $1k+/day accounts, plus the Shotgun + Sniper (high-volume ABO) and 3:2:2 alternatives. For raising budgets on a working account use andromeda2-scaling; for $50k+/day cost caps use andromeda2-hard-scaling.
---

# Launch & test under Andromeda 2

Produces a launch plan the user can build in Ads Manager today: unit economics → structure → packs → exact settings →
creative calendar → decision rules. The design principle: give the algorithm a hyper-competitive pool of genuinely different
concepts and let it allocate spend; force as little as possible; judge on windows long enough to be true.

## Before you start

1. Read `references/andromeda2-doctrine.md` (R1-R8) and `references/metrics-and-diagnosis.md` §3 and §6.
2. Gather (infer what you can; ask only for what blocks the plan; otherwise state assumptions):
   - Daily/monthly budget, market(s), products (hero product?), AOV, COGS %, shipping, fees, LTV if known.
   - Target CPA/ROAS if they have one — else compute it: `python3 scripts/a2.py economics --aov … --cogs-pct … --shipping … --fees-pct …`
   - Current account state: new pixel or history? existing campaigns that work (never break a working campaign)?
   - Creative inventory: how many ready ads, which avatars and concepts, formats (video/static, 9:16 + 1:1?).
   - Tracking: pixel + Conversions API live? purchase counts match Shopify? audience segments defined?
3. If there is no creative or no avatar work yet, route first: `andromeda2-core` (sides/avatars), then the creative skills.

## Workflow

### 1. Pre-flight (do not skip — a test on broken tracking is a waste)
- Purchase event firing from pixel + CAPI; Events Manager purchases ≈ Shopify orders (±10%); EMQ ≥ 8.4.
- Advertiser settings → **Audience segments**: engaged (ATC 90d + visitors 30d) and existing customers (purchasers 180d + CRM
  list). Not retroactive — set it up now.
- Advertiser settings: no account-level age/placement restrictions; "test new creative enhancements" unticked.
- Custom audiences ready: Purchasers 180d (pixel), all-time customer list (Klaviyo/CRM), ATC/IC 90d, visitors 30d.
- King goal set: one number (target CPA or ROAS, blended) the whole account runs on.

### 2. Choose the structure by stage
Pick one and explain why in one line. Details and settings for every option: `references/testing-structures.md`.

| Stage | Structure |
|---|---|
| New / < ~$150/day ("M0") | `Prospecting_CBO` (highest volume) · one pack per round · no minimums · one interest *suggestion* only if the pixel has < ~$1k lifetime spend or broad is stuck · retention only if needed, tiny. Goal: reach $250-500/day fast for signal. |
| ~$150-1,000/day (core M4) | Prospecting CBO (default) + Retention CBO (≤ 10% of prospecting). Packs by avatar → concept, 4-8 ads. 7-day 1x-CPA floor only for packs that are being starved. |
| $1,000+/day | M4 + interest-winners ad sets (adjacent single interests, winners only) + optional retargeting split (only if engaged > ~20-25% of prospecting spend or frequency is high) + catalog retargeting ($5-10/day) + geo packs. |
| Dozens of new creatives per week, quick-purchase product | Shotgun + Sniper: each round = new ABO campaign, one ad per ad set, budget 1x CPA (or cost/IC or cost/ATC target), manual kill switches on cost per ATC → IC → purchase. High effort; only for that profile. |
| Brand prefers fixed test cells | Evolve 3:2:2: one CBO "Acquisition" campaign, a Champions ad set of winning post IDs + one DCT ad set per concept with 3 visuals × 2 primary texts × 2 headlines; ≤ 5 live ad sets at a few hundred $/day; no min/max. |

Default under Andromeda 2 is the CBO pack system: it lets retrieval compare every ad in one competitive pool, and zero spend is
a trustworthy verdict now that the system scores every ad (Pawliw). Never test in ABO and "graduate" to a scale campaign — it
builds a permanent cost centre of unproven ads.

### 3. Size the creative pipeline
Run `python3 scripts/a2.py testing-plan --campaign-budget <daily> --target-cpa <CPA> --new-packs <n>`. Rules it applies:
one new ad per week per $10k monthly spend (floor 2/week, round up); proven-vs-new mix by spend tier (mostly new concepts
when small; ~50/50 near $100k/month; 80% iterations at $200k+/month); quality overrides the number — launch only ads you would
bet on. At $100/day, "four to six ads every other week" beats two a week.

### 4. Design each pack
- One pack = one avatar (side) + one concept, 4-8 ads (2 minimum at small budgets, 12 maximum). Iterations of a winner and
  new formats get their own new pack. Very different concepts → separate packs; close variations can share.
- Every ad: concept/iteration label, side, angle, awareness, 9:16 + 1:1 assets, sound-off proof, distinct intent (doctrine §5
  scorecard ≥ 15). Video and static may share a pack if they came from the same creator package.
- Copy per ad: 2 genuinely different primary texts + 2 headlines by default (long story vs short punchy; problem-solution vs
  offer-led); 5 + 5 once the account spends $1k+/day and you want Meta to mix. Descriptions optional. CTA Shop Now (Learn More
  for high ticket). Write it with `andromeda2-ad-copy`.
- Name it so reports can isolate the variables: `broad_<A0x-avatar>_<Cxx-concept>_pack<N>`, ads `P<N>-<V|S|C><n>_<hook-or-angle>`.

### 5. Build — settings that matter (full checklist: `references/settings-checklist.md`)
Campaign: Sales · Auction · CBO daily · highest volume · no spending limit · Advantage+ catalog off · A/B test off.
Ad set: Website · Maximize number of conversions (value only with lots of data and varied AOV) · Purchase · no cost goal ·
Standard attribution 7-day click + 1-day engaged-view + 1-day view · Advantage+ audience, no suggestion (or one adjacent
interest when the pixel is new) · exclude Purchasers 180d + customer list · only your languages · all placements.
Ad: manual upload · single image/video or carousel (no Flexible) · site links (4+) · promo code extension if any ·
enhancements that do not alter the media only · no translation if you sell in one language · UTMs in URL parameters.

### 6. Launch cadence
- Launch rounds on a fixed day (Monday); analyse Friday; finalise next Monday; brief winners; new ads 7-14 days later.
- **Never inject new ads into a live pack, never edit a live winning ad, never move ads between ad sets** (it resets learning;
  Meta's "combine your ad sets" recommendation has crashed accounts). New round = duplicate a pack, swap ads, new number.
- Fair-shot floor (only when packs are being starved): ad set spending limit → daily minimum = 1x target CPA, all live
  minimums ≤ 20% of the CBO budget, removed after 7 days no matter what. A pack that spends above its floor is a likely winner;
  one that sits at the floor will die when it is removed — let it.

### 7. Read the test and act
- Window: 14 days if the account spends < $1k/day, 7 days at $1k+/day. Never on part-day, post-sale or post-holiday data.
- Export ad-level data and run `python3 scripts/a2.py analyze export.csv --target-cpa <CPA>` (and/or `--target-roas`).
  It applies the pausing tree (2x CPA earliest verdict; 3x CPA and 50%+ off KPI = pause; cap hogs with a max-% limit) and names
  the weakest funnel stage per ad.
- Judge packs, not just ads: Winning ad found · Poor spend, great CPA · Poor spend, poor CPA · Great spend, poor CPA.
  A winning pack takes majority spend at KPI *and* the campaign's overall result improves.
- Winners (top ~10% by spend, at KPI, incremental holding): duplicate (post ID) into interest-winners ad sets and the
  retention campaign; brief iterations (`andromeda2-creative-iteration`). Never pause the top spender while the account is on target.
- Losers: pause, or move to the zombie campaign (`andromeda2-zombie-campaigns`) at higher spend levels.
- Write one learning per pack in the concept library (avatar, concept, result, why).

## Output format

Save to `ads/<brand-slug>/launch-plan-<YYYY-MM-DD>.md` and summarise in chat.

```markdown
# Launch & test plan — <brand> — <date>
## 1. Economics and King goal   (a2 economics table; target CPA/ROAS; assumptions)
## 2. Pre-flight checklist      (tracking, segments, audiences, settings — tick boxes)
## 3. Structure                 (table: campaign · type · budget · bid · audience/exclusions · purpose; one-line why)
## 4. Packs for round 1         (table: pack name · avatar/side · concept · ads (label, format, hook) · copy set · minimum y/n)
## 5. Settings checklist        (campaign / ad set / ad; only deviations from the default called out)
## 6. Creative calendar          (a2 testing-plan output; next 4 weeks: launch dates, # concepts vs iterations)
## 7. Decision rules             (windows, kill/keep/cap/winner thresholds in money for THIS account, graduation, zombie hand-off)
## 8. Day-7 / day-14 review template (what to export, the analyze command, the questions to answer)
```

## Quality bar

- Numbers are computed (a2), not guessed; thresholds are written in this brand's dollars.
- Exactly one place where new creative competes (the prospecting CBO), purchasers excluded, retention capped ≤ 10%.
- Forced spend (minimums, ABO budgets) ≤ 20% of budget and time-boxed.
- Every pack passes the doctrine scorecard and holds distinct-intent ads; 9:16 + 1:1 delivered.
- No action on the plan depends on a single day's data. Working legacy campaigns are left running.

## References

- `references/testing-structures.md` — every structure with full build steps: M0, M4 prospecting / retention / retargeting /
  catalog / interest-winners / geo / landing-page packs / short sales, Shotgun + Sniper, 3:2:2, Pellegrini's volume test,
  moving an existing account into M4.
- `references/settings-checklist.md` — every Ads Manager setting with the recommended value and why.
- `references/metrics-and-diagnosis.md` — windows, the pausing tree, frequency, attribution.
- `references/andromeda2-doctrine.md`, `references/psychology-toolkit.md` — creative requirements the packs must meet.
- `scripts/a2.py` — `economics`, `testing-plan`, `analyze`.
