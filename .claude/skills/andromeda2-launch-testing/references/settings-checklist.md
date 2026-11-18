# Ads Manager settings checklist (2026 UI)

Source: *The Facebook Ads Blueprint* "Dictionary: every setting in Meta" and M4 lessons (2026). The rule of thumb behind
most choices: give the algorithm maximum signal and freedom, keep hard controls to location, minimum age, exclusions and
language, and never let Meta crop or alter your media.

## Advertiser (account) settings

| Setting | Value | Why |
|---|---|---|
| Audience segments | Engaged = ATC 90d + visitors 30d (+ Klaviyo lists); Existing = purchasers 180d + customer list | Breakdown by new/engaged/existing; not retroactive — set it on day 1 |
| Account controls (age, location, placement restrictions) | Off unless legally required (alcohol etc.) | Account-level restrictions behave like "shadow banning yourself" (higher CPMs) |
| Advantage+ creative "Test new creative enhancements" | Unticked | "We're not guinea pigs" — choose enhancements per ad |
| Value rules | Built here, applied per ad set, only for big proven gaps | See the scaling skill |
| Meta Verified | Optional; observed higher CPC/CPM and partner-access issues | Weigh benefits vs drawbacks |

## Campaign

| Setting | Value | Why |
|---|---|---|
| Objective | Sales (lead gen: Leads) | Only sales/conversions objectives optimise for buyers |
| Buying type | Auction | Reservation is for mass awareness |
| Advantage+ catalog ads | Off (on only for catalog campaigns) | On forces every ad to be a catalog ad |
| Budget | Campaign budget (CBO), daily | CBO beats ABO in almost all cases; lifetime only for ad scheduling |
| Bid strategy | Highest volume (core) | Cost controls only at high spend (hard-scaling skill); bid cap only for zombie |
| Campaign spending limit | None | Not needed with daily budgets |
| Budget scheduling | Off (or day-of-week pulses once proven) | — |
| Special ad category | Declare if applicable | Avoid rejections/suspension |
| A/B test | Off | Use Meta's A/B tool only for clean splits, 28 days, judged on cost per purchase |

## Ad set

| Setting | Value | Why |
|---|---|---|
| Conversion location | Website (single) | Multiple locations only if the business really has them |
| Performance goal | Maximize number of conversions | Value of conversions only with lots of data and varied AOV |
| Dataset / event | Correct pixel · Purchase | "You have to be one in 10,000 to not run the purchase event" |
| Cost per result goal | Blank | That field is a cost cap |
| Value rules | None (until proven) | — |
| Attribution | Standard · 7-day click + 1-day engaged-view + 1-day view | Max signal; compare incremental in columns, don't optimise on it until big |
| Conversion count | All conversions | — |
| Ad set spending limits | None on pack 1; 7-day 1x-CPA minimum on starved new packs; % maximum on hogs | Temporary tools only |
| Audience | Advantage+ audience; no suggestion (or one adjacent interest when the pixel is new) | Broad lets retrieval find the sides your creative speaks to |
| Exclusions | Purchasers 180d (pixel) + all-time customer list | Creates the prospecting swim lane; must mirror retention |
| Minimum age / location / language | Hard controls; languages = only those your ads and site use | — |
| Placements | All (23 included) | Cut only at high spend where data is clear |
| Devices, platforms, brand safety | All / default | "Do not make a non-data-driven decision" |
| Customer lifecycle prompt | "Get more conversions" (exclusions do the work) | New 2026 UI option |

## Ad

| Setting | Value | Why |
|---|---|---|
| Identity | Facebook page + Instagram + Threads | — |
| Partnership ad | On when whitelisting a creator | "Very, very effective" |
| Creative source | Create ad · manual upload (use existing post/post ID for proven ads) | Post ID keeps social proof |
| Format | Single image/video or carousel; no Flexible; collection only if proven | Flexible lets Meta crop and cut important parts |
| Multi-advertiser ads | Off (except catalog retargeting / marketplaces) | Confuses first exposure with other brands |
| Media | 1:1 + 9:16 for every ad (4:5 no longer the standard; horizontal gets ~2-5% of delivery) | Square + vertical carry ~99% of spend |
| Primary text / headline | 2 genuinely different of each (5 + 5 at scale) | Nuance variants muddy data |
| Description | Usually blank; optional bonus line | Often not shown |
| CTA | Shop Now (Learn More for high ticket) | "People that click Shop Now are committing in a micro way" |
| Site links | 4+ (best sellers, new arrivals, key collections, FAQ/VSL) | "It works. It's helpful." |
| Promotions extension | On when a code/offer exists | — |
| Enhancements | Yes: text improvements, summaries, product tags, relevant comments, CTA/overlays that don't touch media. No: visual touch-ups, animation, image expansion, flex media, translation (single-language) | "If it impacts the video or image, don't use it." |
| Music | Optional (sources disagree) | — |
| Image generation | Off | Build AI creative elsewhere |
| Optimized website destination | On, except specific-product ads in complex shops | Sources disagree; default on |
| Shop destination | Off | Send traffic to your site |
| URL | Clean landing URL; UTMs in URL parameters only | UTMs in the URL field (or tools rewriting them) can reset post IDs |
| Tracking | Website events on | — |
