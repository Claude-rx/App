---
name: fb-launch
description: Launch Meta (Facebook/Instagram) ads exactly per the media-buying SOP (The Facebook Ads Blueprint M4 system). Runs the preflight (King Goal, pixel gut check, advertiser settings, audiences), builds the Prospecting CBO + Retention core or adds a new creative pack (avatar_concept_packN) with the right minimum budget, exclusions, attribution and ad-level settings, staged as drafts and published only after explicit approval. Use when: "launch ads", "new pack", "launch this week's creatives", "set up the ad account", "build the prospecting campaign", "first $100/day setup", "set up retention", "launch a sale campaign", "migrate this account to M4".
---

# fb-launch: launch per the SOP

**The rulebook is `docs/media-buying/SOP.md`.** This skill runs SOP §3–§6 and §9.5. Every number comes from `tools/fb-blueprint/rules.py`, through the engine:

```bash
echo '<json kwargs>' | python3 tools/fb-blueprint/blueprint.py <command>
```

Never hard-code a threshold in your reasoning. Run the command and quote its `why`.

## Safety contract (non-negotiable)

1. **Read before write.** Use Meta Ads MCP read tools (`ads_get_ad_accounts`, `ads_get_ad_entities`, `ads_get_ad_account_custom_audiences`, `ads_get_datasets`, `ads_get_dataset_quality`, `ads_get_ad_account_pages`) freely.
2. **Every create or update is a proposal first.** Show a launch plan table (object, name, every setting, budget in dollars, exclusions, minimum and its removal date), then wait for an explicit "yes, launch". A request to "launch ads" is permission to *prepare*, not to *publish*.
3. The Meta MCP stages creates as **drafts** (`status=DRAFT`). Check `active_errors` after each create. Call `ads_activate_entity` **only** after the user approves the finished draft.
4. Budgets go to the API in **cents**. Read them back with `ads_get_ad_entities` after every write and report the returned values.
5. Never change a live, working ad set (SOP law 10). New creative always means a **new** ad set. Never move ads between ad sets.
6. Never invent interest IDs, audience IDs or pixel IDs. Look them up or ask.
7. Send the same `client_conversation_id` on every Meta call (generate one 20-character id on the first call).

## Step 0: Intake (ask only for what you can't read)

- Ad account id. Pixel/dataset id (read with `ads_get_datasets`). Page and IG ids.
- **King Goal**: ROAS or CPA, and its value. Without it, stop and run the profit model:
  `profit_model {orders, aov, cogs_pct, fixed_costs, take_pct, ltv_12m}` → `target_roas {breakeven_roas}` (SOP §3.2–3.3).
- Target CPA (needed for minimums) and monthly spend.
- Hero product/collection/offer (SOP §3.4). Business type: e-com or lead gen (lead gen → follow SOP §10 deltas).

## Step 1: Preflight (SOP §4). It blocks the launch.

Collect evidence for each item, then run `preflight {account:{...}}`:
- `king_goal_set`
- `pixel_gut_check_passed`: run `pixel_check {browser_purchases, server_purchases, store_orders, emq}`. Get browser vs server from `ads_get_dataset_stats` / Events Manager, orders from Shopify (Shopify MCP `run-analytics-query` if connected), EMQ from `ads_get_dataset_quality`.
- `audience_segments_set`, `advantage_creative_test_off`, `no_account_controls`: these are UI-only settings. Ask the buyer to confirm, and link SOP §4.3.
- `purchaser_audiences_exist`: check `ads_get_ad_account_custom_audiences` for Purchasers 180d and the all-time CRM list. If missing, propose `ads_create_custom_audience` (approval required).
- `hero_product_chosen`, `special_ad_category_checked`.

If `ready=false`, report the blockers and stop. Offer to fix the ones you can.

## Step 2: Decide what to build

Read the existing campaigns (`ads_get_ad_entities level=campaign`, last 30d, spend, ROAS/CPA, budget, bid strategy).

| Situation | Build | SOP |
|---|---|---|
| No account history, or prospecting under ~$250/day | **M0:** `Prospecting_CBO` + `Broad_Pack_1`; minimums optional from $100/day, no scale, no retargeting | §5.1 |
| History, no M4 | **Migrate:** the highest-spending campaign becomes the prospecting CBO. Don't pause working ad sets. | §5.10 |
| M4 exists, new creative is ready | **New pack** inside the prospecting CBO (Step 4) | §5.4 |
| No retention campaign | Retention, ≤10% of prospecting (`retention_budget`) | §5.6 |
| Limited-time sale or BFCM | **One separate sale campaign** with its own sale-period budget | §9.5 |
| New evergreen offer (e.g. $25 off $75, on the homepage) | A **new pack in the prospecting CBO**, not a sale campaign | §9.5 |
| Physical store, wholesale/B2B buyer, or a must-sell product line | A **separate campaign** (own budget; local radius + its own dataset for a store) | §5.1 |
| Restarting after a long pause | Reuse the old campaign, trimmed to its best ads (keeps comments and signal); never start from scratch | §5.10 |
| Retargeting / catalog / scale | Only when `fb-optimize` or `fb-scale` shows the trigger | §5.7–5.9 |

## Step 3: Build the core (only when it's missing)

**Prospecting CBO.** `ads_create_campaign`:
- name `prospecting CBO` (M0: `Prospecting_CBO`)
- objective `OUTCOME_SALES` (lead gen: `OUTCOME_LEADS`), buying_type `AUCTION`
- `campaign_daily_budget` (cents)
- `campaign_bid_strategy` `LOWEST_COST_WITHOUT_CAP` (= Highest volume)
- `special_ad_categories` if they apply
- no spend cap

**Pack 1.** `ads_create_ad_set`:
- `ad_set_name` `avatar_concept_pack1`
- `optimization_goal` `OFFSITE_CONVERSIONS` (max number of conversions)
- `billing_event` `IMPRESSIONS`, `destination_type` `WEBSITE`
- `promoted_object` `{"pixel_id": "<id>", "custom_event_type": "PURCHASE"}`
- `attribution_spec` `[{"event_type":"CLICK_THROUGH","window_days":7},{"event_type":"ENGAGED_VIDEO_VIEW","window_days":1},{"event_type":"VIEW_THROUGH","window_days":1}]`
- `targeting`: geo countries + `locales` for the ad language only + `excluded_custom_audiences` [Purchasers 180d, all-time purchasers]
- omit `targeting_automation` (Advantage+ audience on) and omit placements (all placements)
- **no** `daily_min_spend_target` on pack 1

**Retention.** Campaign `retention`, CBO ≤10% of prospecting, then two ad sets:
- `purchase_180 days`: include Purchasers 180d
- `purchase_all time`: include the all-time CRM list, exclude Purchasers 180d

These ad sets deliver only to a custom audience, so send `targeting_automation.advantage_audience=0` with `advantage_audience_off_reason=CUSTOM_AUDIENCE_ONLY`. Then add both purchaser audiences as exclusions on **every** prospecting ad set.

## Step 4: Launch a new pack (the weekly job)

1. Volume check: `ads_per_week {monthly_spend}`. Grouping: avatar first, then concept. **4–8 ads per pack** (2 minimum, 12 maximum). Very different concepts go in separate packs.
2. Pack number N = the count of existing `*_pack*` ad sets + 1.
3. Minimum: `pack_minimum {target_cpa, campaign_daily_budget, pack_number, other_active_minimums, interest_pack, one_pack_per_week}`. Sum `other_active_minimums` from live ad sets whose minimum is still inside its 7 days. If `status` is set or reduced, pass `daily_min_spend_target` (cents) and put the **removal date = launch + 7 days** in the plan. If `optional=true` ($100–1,000/day), ask the buyer.
   - Only new creative goes into a new pack. Never copy the current winner into it.
   - Don't change creative and the checkout/funnel in the same week. Hold spend flat before a big funnel change.
   - After a big consolidation or change, wait about a week; launch only iterations of top ads meanwhile.
4. Duplicate the pack-1 settings (`source_adset_id` or the same fields) with name `avatar_concept_packN`. Same exclusions. Add the retargeting audiences to the exclusions **only** if a Retargeting campaign exists.
5. Ads: `ads_creative_upload_media` → `ads_create_creative` → `ads_create_ad`. Settings (SOP §4.1):
   - single image/video or carousel; 1:1 and 9:16 crops
   - 2–5 completely different primary texts, 2–5 completely different headlines
   - description blank or "+ free shipping"; CTA `SHOP_NOW` (`LEARN_MORE` for high ticket)
   - ≥4 site links
   - UTMs in `url_tags`: `utm_source=paid_social&utm_medium={{adset.name}}&utm_campaign={{campaign.name}}&utm_content={{ad.name}}`
   - **No** flexible format, no multi-advertiser, no media-altering enhancements (touch-ups, animation, music, flex media)
   - partnership ad for creator content
6. Run the **pre-ship check** on every ad: can you say who it's for in one sentence? Does the first line or frame signal that person? The avatar is a role or situation, never a demographic. (SOP §6.4)
   - Check that the multi-advertiser toggle (ad level: Ad setup → Format → *Show more settings*) is **off** on every prospecting ad.
   - Copyrighted trending audio is a compliance risk (fines have happened): use licensed audio.
   - Relaunching an existing ad? Use its post ID so the comments and likes carry over.
7. Interest pack (winners only, from `fb-test` graduation): name `interest_[interest]_winners`, one interest one step removed from the brand (Nike → Range Rover, never Adidas), found with real targeting search. New interest packs go far from the previous ones, not next to them. Duplicated winners, **no minimum**.

## Step 4b: Creative brief (when the buyer asks for briefs)

Use the course brief structure (SOP §6.4), written in your own words:
- **Header:** priority · deadline · formats/sizes
- **Internal:** core concept (template + avatar + outcome) · template or inspo links · avatar wants/needs · call-outs (features, problem → solution, offer) · iterations
- **For the creator:** 3 hooks · important call-outs that must be captured · additional shot list (images and video)

Brief only the very top (the avatar's problem → product as the unique solution) and the very bottom (objection-answering statics). A new offer gets almost all top-of-funnel creative. When spend is below what the account used to run, brief fewer concepts and raise the quality: diverse hand-written hooks, not AI-written ones.

## Step 5: Sale campaign (SOP §9.5)

New CBO campaign with a lifetime or dedicated budget for the sale window. Ad sets by avatar (or concept). Minimal exclusions. Never put sale ads into the evergreen CBO. Black Friday/Cyber Monday is a mega event: one campaign for the life of the event.

## Step 5b: Lead gen deltas (SOP §10)

- Objective Leads; conversion location Website by default. Instant forms only track the form fill, so prefer a landing page.
- Optimize on a **standard** event (Complete Registration or Purchase) that receives **qualified leads only**, via CAPI/CRM sync. Never pixel disqualified leads, and never mix raw-lead and qualified packs in one CBO.
- Set the target with `reverse_target {value_per_sale, conversion_rate, label}` (cost per call, lead or trial).
- Phone-led local businesses: a separate lifetime-budget campaign with an ad schedule that stops 30 minutes before the phones close. Hand the in-flight management to `fb-optimize`/`fb-scale`, which kill faster and scale with big upward jumps against the sale KPI.

## Step 6: Approve → publish → verify

1. Show the draft summary from `ads_get_ad_entities object_state=draft`, with zero blocking `active_errors`.
2. On explicit approval: `ads_activate_entity` on the campaign.
3. Read back `effective_status`, budgets and minimums.
4. Output the **launch log** (below) and the calendar item "remove minimum on <date>" (`fb-optimize` checks it daily).

## Output: launch log

```
LAUNCH LOG: <account> · <date>
King Goal: ROAS 2.2 (break-even 2.0 + 10%) · target CPA $45
Preflight: PASS (8/8)
Built: prospecting CBO / avatar_concept_pack7 (6 ads) · min $45/day until <date+7> (pool 20% of $1,500 = $300, used $180)
Exclusions: Purchasers 180d, Purchasers all-time
Rules applied: SOP §5.2, §5.4, §4.1 (engine: pack_minimum, ads_per_week)
Next: fb-test reads this pack on <launch+7 or +14> (judgment_window)
```
