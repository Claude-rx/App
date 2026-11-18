---
name: andromeda2-static-ads
description: Designs static image ads for Meta (Facebook/Instagram) built for Andromeda 2: a balanced batch where every image is a named concept (avatar + template) or a labelled iteration, speaks to one side of one person in one specific moment, sells desire and the dream outcome rather than features, and ships in 1:1 and 9:16. Delivers a saved batch brief: angle matrix, format pick from 30+ proven formats, on-image headline and copy, layout and safe zones, AI image prompts (Nano Banana, GPT Image) that keep the product accurate, copy seeds and an iteration plan. Use this whenever someone asks for static or image ads, ad graphics, carousels, us-vs-them or comparison images, review cards, native-post or tweet-style ads, mechanism diagrams, offer, bundle or Black Friday images, back-in-stock or sale-ending ads, objection or retention statics, AI ad images, or wants to iterate a winning static or turn a winning video into statics. Not for video scripts (andromeda2-video-scripts) or copy only (andromeda2-ad-copy).
---

# Andromeda 2 static ads

Produces a static (image) ad batch brief: for every image, the side it speaks to, the one question it answers, the format, the
on-image copy, the 1:1 and 9:16 layouts, an AI image prompt that keeps the product exact, copy seeds and the next iterations.
Andromeda 2 reads every ad and routes it to the side of a person it matches, so a static wins by being specific to one person in
one moment, by selling the moment they get back, and by asking a question no other live ad asks. Statics are also the cheapest
bench for testing an angle before it becomes a video (Pellegrini).

## Before you start

Read `references/andromeda2-doctrine.md` every time (eight requirements, concept vs iteration, scorecard) and
`references/psychology-toolkit.md` §2-§8 and §12 (side card, desire, mechanism, proof, awareness, self-concept, Mood ×
Intensity, compliance). Open `references/metrics-and-diagnosis.md` only when iterating from performance data.

Gather — ask only for what is missing and cannot be inferred:
1. **Product, price, offer, guarantee, landing page.** The image must carry the page's promise and offer (message match).
2. **Side cards** (A01, A02…). None? Build two from reviews, comments and competitor comment sections (psychology toolkit §1-§2,
   or `andromeda2-core` for full research).
3. **Proof inventory** — real numbers, rating and review count, golden-nugget reviews (verbatim), press, named experts, tests,
   guarantees. Only what is true and documented.
4. **Mechanism** — named cause (UMP) and named solution (UMS); if the product has none, the one feature that explains why it works.
5. **Objections** — price, size/fit, effort, "will it work for me", durability, mess.
6. **Assets** — real product photos (packaging, label, texture close-ups) as AI references; brand colours/fonts; customer photos
   with permission.
7. **Context** — what is live or already won (to avoid duplicates and decide concept vs iteration), monthly spend, category
   (health, supplements, weight loss, telehealth = strict rules), season or promo.

If the user gives little, proceed: infer two sides from the product's obvious buyers, mark every number `[PLACEHOLDER — replace
with real, provable data]`, list assumptions at the top of the brief. Never stall for data you can label.

## Workflow

### 1. Frame the batch
Decide the job — new concepts, iterations of a winner, promo/seasonal, bottom-of-funnel objections, retention, or statics from
a winning video (modes below) — and the size: one new ad per week per $10k of monthly spend, floor 2/week (doctrine;
`python3 scripts/a2.py testing-plan --campaign-budget <daily> --target-cpa <CPA>`). Blueprint's "IV line": about five statics a
week keeps an account alive — not a magic number, and never pad with images you would not bet on. Default mix: about half
top-of-funnel angle tests, half bottom-of-funnel proof/objection/offer. *Why:* the system absorbs volume easily; what it rewards
is distinct intent, and statics complement video rather than replace it (statics-only accounts give up "60% or 70% of impressions, I
think" — Blueprint live calls).

### 2. Mine the raw material for each side
Per side, write down: the pain moment (time, place, gesture), the desire scene (*[product] so you can [action] [where/when]
without [old pain]*), verbatim phrases, the enemy, UMP → UMS, the proof that answers this side's doubt, its top objections, the
self-concept triple and its zone. Pull golden-nugget reviews — short, specific, slightly too personal (Denney). Scan competitors
in the Ad Library: the statics running longest with the most variants are proven templates ("longevity plus volume" —
Blueprint); visuals and messages everyone runs are exhausted (Evolve). Steal the template, never the message. *Why:* an image
holds about seven words — they must be the side's words, or the ad has tens of thousands of AI twins (Pawliw).

### 3. Fill the angle matrix and pick the batch
Rows = sides; columns = angle families (pain moment, desire, hidden cause, mechanism, enemy, proof, objection, offer, identity,
value gap, trigger). Each cell = the viewer's question in their voice + the specific material that answers it. Then pick cells
so that: no two statics answer the same question (check live ads too); ≥ 2 awareness stages; ≥ 3 of the four levers (offer,
mechanism, education, avatar); ≥ 2 Mood × Intensity zones per side, never PANIC for product-aware; self-concept tested in three
versions when unsure. Run one angle in two formats only on purpose, to learn whether the angle or the format won (Pellegrini).
Method, example grid and batch recipes: `references/angle-matrix-and-prompts.md` §1-§3. *Why:* "Every new ad should answer a
different question"; eight ads with one message are one ad (doctrine R4).

### 4. Choose the format
Concept = avatar + template (Blueprint): the side is fixed by the cell; now pick the template. Order of preference: formats
that already hit in this account's log → the picker in `references/static-formats.md` §1 by awareness and lever → the starter
round for a new account (us vs them, feature call-out, testimonial, headline ad — Denney). "Ugly" statics are weak in 2026 per
Blueprint ("fell off in the last six plus months"), while Pellegrini's illustrative table still shows them hitting (21%) —
build them only if the account's own hit rate supports it. Name the concept: `C07 · A02 Rob-3-beds × Us vs Them`. A new side on
a proven template, or a proven side in a new template, is a new concept; a change of emphasis inside the same side + template
is an iteration — label every static.

### 5. Write the on-image copy
- **Main line ≤ ~7 words** (a verbatim review quote may run to ~12). It carries the side and the hook; it is read in about a
  second (Denney: the hook is now ~1 s).
- Start with what they get or the moment they recognise, not the brand (Oliver). A time, a place, a number, a named mechanism or
  a verbatim phrase — "specific or invisible" (doctrine R3).
- Support line ≤ ~15 words: the proof, the cause → fix link, or the offer. Proof right after the claim.
- Max three text levels + logo; text-native formats (native post, note, review card, table) may carry ~40 short words.
- Sell the moment regained, never the spec; name the mechanism; read it aloud (Evolve); sentence case, no "!!!".
- Situation, behaviour or first person — never a personal-attribute callout ("Overweight?").
Pattern bank by angle: `references/angle-matrix-and-prompts.md` §4.

### 6. Direct the visual
One focal subject (Evolve: "too much going on" and "too much text" are top failure reasons). Casting is targeting — Andromeda
tends to show an ad to people resembling the person in it, so cast the side (Blueprint live calls). Scenery and aesthetic match
the identity the side buys into. Use what holds attention: hands using the product, texture close-up, side-by-side, POV, an
emotional element, a hard-to-argue demo with a neutral object (Pellegrini). Set light and palette from the zone (COZY warm and
soft; JOY bright and bold; FATIGUE dim and real; PANIC stark, one accent). Design the 9:16 as its own layout: text, logo and
product out of the top ~14% and bottom ~35% (Reels) — specs in `references/static-formats.md` §0. Pass the thumb test: at 25%
size the main line and focal subject land in one glance.

### 7. Write the AI image prompt
Fill the framework in `references/angle-matrix-and-prompts.md` §6: format + ratio, scene/moment, focal subject, product, casting,
zone look, composition (negative space for copy, safe zones), style, text, avoid. Product accuracy (Blueprint live calls):
attach close-up reference images; state exact dimensions; keep the product fixed in one position (no orbit shots); say "exactly
like reference image 1"; composite the real packshot if the model distorts it. Default to "no text" in the image and set copy in
a design tool, so call-out swaps take minutes and spelling is exact. Nano Banana (Superscale's default) and GPT Image 2 both
work — keep whichever holds the product. Never present an AI person as a customer or expert; disclose AI people where the law
requires (e.g. New York). Skip Meta's in-platform image generation and media-altering enhancements (Blueprint).

### 8. Seed the copy
Per static: 2 primary-text openers (the first ~125 characters) and 2 headlines, completely different from each other but on the
same side and angle (5 + 5 once the account spends $1k+/day), matching the landing page's headline and offer. Full primary
texts, headlines and descriptions → `andromeda2-ad-copy`. *Why:* headlines are a leading indicator of what to put on the next
image (Blueprint live calls).

### 9. Plan iterations and the video twin
For each concept list the next 2-3 iterations, one layer each (message, mechanism, avatar slice, education, offer, visual) and
the Denney add-ons (review, stat, press, headline bar, carousel, post-it version). 1-6 iterations per concept per round
(Blueprint); a background-colour swap is not an iteration. Launch each concept with 2-3 variants so the pack can tell format
from message (Denney). When a static's angle wins, brief it as a video (Pellegrini: Frøya's "arctic autophagy" ran 485 days as a
static, then 569 as a video) via `andromeda2-video-scripts`. Full loop: `andromeda2-creative-iteration`.

### 10. Score, check compliance, group, save
Score every static on the doctrine scorecard (0/1/2 × 10; ship ≥ 15, rework 11-14, kill < 11) and run the image compliance
checklist (`references/angle-matrix-and-prompts.md` §10). Group into packs by side, then concept, 4-8 ads per pack, new pack
only — never injected into a live pack (final structure: `andromeda2-launch-testing`). Save the brief as Markdown to
`ads/<product-slug>/static-ads-<YYYY-MM-DD>.md` (unless the user names a path) and summarise in chat: the batch table, the
three statics to launch first and why, and every placeholder still to replace.

## Modes

**A. Iterate a winning static.** Find the variable that won first (if all variants spent, the format works; if one took the
spend, compare image vs message). Then 3-6 one-layer iterations in a new pack; keep the winner's copy unless copy is the layer;
add the carousel and video twins. Never edit the live winner. Read statics on CPM, link CTR, CPC, cost per ATC/IC, CPP and spend
share — they have no hook or hold rate (`scripts/a2.py analyze`).

**B. Promo and seasonal (BFCM).** Sell the triumph, not the saving: BF buyers "run to get there before their neighbour"; a deal
for 50 people beats an open deal, even a cheaper one; the more visible and credible the limit, the stronger the win
(Pellegrini). Build a Quadruple Offer static (strike price + free product/kit + mystery gift or voucher + free shipping, bonus
code optional) and Evolve's five: offer graphic, new product photo + offer, best image + offer banner, best ad + banner, new
video. Real limits and deadlines only. Recompute target ROAS/CPA before any offer. Sale ads run in a separate sale campaign.
Details: `references/angle-matrix-and-prompts.md` §8.

**C. Trigger, objection and retention statics.** Trigger statics for real events: back in stock, discount, low stock, sale
ending (Blueprint live calls). Objection engine: list every objection (aim for 100), one static per top objection on a recurring
background — "ads you can crank out in a day". Retention: new arrivals, bestsellers, restock events, cross-sell, plain "buy
again". Details: §9 of the same file.

**D. Statics from a winning video.** Best frame + the winning hook as the main line; a post-it-note version of the winning
script; the same angle in a proof format. Same side and message in a new template = new concept, new reach.

## Output format

```markdown
# Static batch — <Product> — <YYYY-MM-DD>
**Assumptions & placeholders:** <each [PLACEHOLDER] to replace with real, provable data>
**Sides:** A01 <name — moment — desire — awareness — zone> · A02 <…>
**Mechanism:** UMP <name: cause> → UMS <name: fix> · link in one line
**Batch goal:** <concepts | iterations | promo | BOF | retention | from video> · <N concepts, N ads> · mix <TOF n / BOF n>

## Batch table
| # | Concept / iteration | Side | Angle → the question it answers | Format | Aware. | Lever | Zone | Self | Main line (≤ 7 words) | Pack |
Balance check: <distinct questions · stages · levers · zones · nothing duplicates a live ad>

## Per-static specs
### S1 — C01 · A01 <side> × <format> — concept | iteration of <ID> (<layer>)
- Question it answers: "<viewer's voice>"
- Side & moment · Awareness · Zone · Self · Lever
- On-image copy: L1 "<≤ 7 words>" · L2 "<≤ 15 words>" · L3 chip "<proof/offer>"
- Visual direction: focal subject · composition · casting · light/palette · type
- 1:1 layout: <…> · 9:16 layout: <…> (nothing in top ~14% / bottom ~35%)
- AI image prompt: <full prompt> · References to attach: <list>
- Variants at launch: v1 <…> · v2 <layer changed>
- Copy seeds: P1 / P2 openers · H1 / H2 → full copy via andromeda2-ad-copy
- Proof & compliance: <source of each number; checks passed>
- If it wins: i1 <layer> · i2 <layer> · i3 <format swap> · video twin <…>
- Score: <10 items> = <total>/20 · Ad names: P<n>-S<n>_<angle>_v<n>

## Pack plan
| Pack (ad set) | Side | Concepts | Ads | Launch |
## Hit-rate log rows
| Ad | Format code | Angle | Side | Zone | Launched | Winner? |
```

**Worked example (excerpt; the complete batch is in `references/worked-example-batch.md`).** Made-up orthopedic dog bed;
numbers are placeholders.

> **S1 — C01 · A01 Dana-2am × Problem–solution split — concept.** Question: "Why does he pick the cold tile over his bed?" ·
> Problem aware · FATIGUE · ought · avatar lever. L1 "2 a.m. Kitchen tile. Again." · L2 "Old dogs leave beds that have gone
> flat. Give him one that doesn't." · L3 "100-night trial". Visual: same grey-muzzled lab both halves — left curled on cream
> tiles in cool 2 a.m. moonlight, right stretched asleep on the bed in warm morning light. 9:16: L1 at 16-24% height, night
> image 24-45%, morning 45-65%, bottom 35% floor only. Prompt: "Square 1:1 photo-realistic split image… the Nestwell Lift Bed
> exactly as in reference image 1 (36 x 28 x 6 in, sage-green zip cover, tag front-left facing camera)… top fifth plain wall
> for a headline… no text." v2 = visual layer (Dana awake at 2:04 a.m., dog pacing in the doorway). Seeds: P1 "It's 2 a.m.
> and you can hear his nails on the kitchen floor again." · H1 "Why old dogs leave their beds". If it wins: education
> headline "He's not restless. His bed is flat." · new breed · story carousel · UGC night-scene video. Score 18/20.

## Quality bar

Before handing over, every static passes:
- **Doctrine scorecard ≥ 15**, with side (1), specificity (3), distinct intent (7) and compliance (10) at 2.
- **One question per static**, written in the viewer's voice; no two statics (or a static and a live ad) answer the same one.
- **Label:** concept (avatar + template) or iteration (which layer); concept name and ad name follow the convention.
- **On-image:** main line ≤ ~7 words in the side's words with a specific; one focal subject; ≤ 3 text levels; passes the 25%
  thumb test; read aloud.
- **Rooms:** separate 1:1 and 9:16 layouts; nothing meaningful in the 9:16 safe zones; no Flexible format, no media-altering
  enhancements.
- **AI image QA:** product shape, colour, label and dimensions match the reference; hands/paws/faces clean; text exact; no AI
  person presented as a customer or expert.
- **Truth:** every number, review, logo, expert, deadline and stock claim is real and sourced, or visibly marked
  `[PLACEHOLDER]`; compliance checklist passed (no personal attributes, health before/after, fake authority, fake scarcity,
  fake comments or profiles).
- **Batch:** ≥ 2 awareness stages, ≥ 3 levers, ≥ 2 zones per side, TOF/BOF mix stated, iterations planned, pack plan and
  hit-rate rows included; landing page carries the same angle and offer.

## References

- `references/static-formats.md` — open at step 4: canvas and safe zones, the picker, and 40 formats (comparison, problem →
  transformation, proof, mechanism, native/lo-fi, product/identity, offer/trigger/retention, carousels) with layouts and rules.
- `references/angle-matrix-and-prompts.md` — open at steps 3, 5, 6, 7, 9 and for the modes: angle families, matrix and batch
  recipes, copy pattern bank, visual direction, AI prompt framework and templates, iteration layers, BFCM/promo, trigger,
  objection and retention statics, image compliance checklist.
- `references/worked-example-batch.md` — open when writing the deliverable: a complete six-concept batch brief.
- `references/andromeda2-doctrine.md` — always: requirements, concept vs iteration, scorecard.
- `references/psychology-toolkit.md` — side cards, desire, mechanism, proof, awareness, self-concept, zones, compliance.
- `references/metrics-and-diagnosis.md` — reading static performance, winner rules, frequency for retention.
- `scripts/a2.py` — `testing-plan` (weekly volume) and `analyze` (which statics won and which stage is weak).
