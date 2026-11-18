---
name: andromeda2-ad-copy
description: Writes Meta (Facebook/Instagram) ad copy that wins under Andromeda 2 — primary texts, headlines, descriptions, CTA buttons, display links and site-link labels — as a paste-ready copy deck for one avatar (side card) and one concept, message-matched to the creative and landing page, with genuinely different variants tagged by awareness stage, self-concept, mood x intensity zone and selling lever, first lines that name the right person, a compliance pass and the Andromeda 2 scorecard. Use this whenever someone asks for ad copy, primary text, ad captions, the text under a video, headlines, copy variations to test, a rewrite of weak or low-CTR copy, offer, sale or Black Friday ad text, or copy for a new concept, an iteration or a winner — even if they never say Andromeda. Also use when CTR or CPC is weak while hook and hold rates are fine, or when ad text needs a health or personal-attributes check. For video scripts use andromeda2-video-scripts; for on-image static concepts use andromeda2-static-ads.
---

# Andromeda 2 ad copy

Produces a copy deck per ad: 2-5 primary texts, 2-5 headlines, description, CTA button, display link and site links,
ready to paste into Ads Manager, each variant tagged and scored. Andromeda 2 reads every phrase of an ad and routes it to
the experts for one side of a person, so the copy must name that side in its first line, say the same thing as the
creative and the page, and give Meta genuinely different bets to match to different moments. Specific, provable copy is
also what raises CTR and cuts CPC and cost per purchase: it pre-qualifies the click and makes the page's job easier.

## Before you start

Read `references/andromeda2-doctrine.md` (always) and `references/psychology-toolkit.md` §2-§12 (side card, desire,
mechanism, proof, awareness, self-concept, zones, pain, levers, compliance). When the request is to fix copy on a live
ad, also read `references/metrics-and-diagnosis.md` §4 and run `python3 scripts/a2.py analyze <export.csv>` first —
copy can fix the click stage and part of the purchase stage, not a weak hook rate.

Gather — infer from files, the site and earlier work; ask only for what is missing and blocks the copy:
1. **Side card** for the avatar (A0X). None? Build a minimal one from toolkit §2 and label the guesses; for real
   research route to `andromeda2-core`.
2. **Concept** = avatar + template, and the creative the copy rides on: the video's hook/VO or the static's on-image
   text. New concept or iteration?
3. **Landing page**: URL, type (PDP, advertorial, listicle, quiz), the headline above the fold, offer and price as shown.
4. **Offer**: value exchange + timing + risk reversal (Blueprint), shipping threshold, discount link or code.
5. **Proof inventory**: review count and rating, customers served, survey %, named experts, studies with links, verbatim
   reviews you may quote, demos. This is the input worth asking for explicitly; without it copy runs on placeholders.
6. **Category flags**: health, supplement, weight, beauty/aging, pet health, telehealth, money, special ad category; the
   brand's banned words and claims.
7. **Stage and spend**: new concept, iteration or proven winner; daily spend; copy already live (to avoid duplicates).
8. **Voice**: brand tone; founder or creator speaking?

When the user gives little, proceed: list assumptions at the top of the deck and put every number, name, quote and study
in `[REPLACE: …]`. Never invent proof to fill a gap.

## Workflow

### 1. Anchor the copy to one side and one concept
Write three lines before any copy. **Side**: who, moment, feeling, desire, in one sentence. **Concept**: avatar ×
template + the creative's hook line. **Page**: the above-the-fold headline + the offer. All three must share the same
avatar, angle and offer. Why: Meta reads "every phrase" of the ad (Blueprint) and the page is the second half of the
same message; a mismatch shows as a weak click→purchase rate (diagnosis stage 4) and bounce — the page headline "MUST be
congruent with the messaging and big idea in your ad or … you will have a high bounce rate" (Oliver). If the brief mixes
two avatars, split it: a different avatar is a new concept, a separate ad and a separate deck.

### 2. Build the message spine: one idea, one promise
- Kindergarten pitch (toolkit §11): problem → emotional problem → root problem (UMP) → root solution (UMS) →
  ingredient/technique → physical win → emotional win.
- The mechanism in two sentences, named, cause→effect obvious in two seconds ("the M3 method" beats "a three-step
  process", Blueprint).
- Two or three desire scenes: feature → "so you can [action] [place/time] without [old compromise]" (toolkit §3).
- Pain in three layers in the customer's words: physical → life → emotional (Oliver).
- Proof map: each claim next to the proof that will follow it. A claim with no proof is cut or softened.
- The first 1-3 objections of this side (research; Kell's 10 + 1 in `references/copy-frameworks.md` §9).
Why: brands fail by "piling promise on top of promise rather than building believability and strengthening one
justifiable promise" (Evolve); one idea per ad (Kell); "Most marketing fails for one reason: it's not specific enough to
feel true" (Blueprint) — and specificity is what separates an ad from its AI-made near-twins in retrieval (doctrine R3).

### 3. Set how many variants, by stage
| Stage | Primary texts | Headlines | Description |
|---|---|---|---|
| New concept in a test pack (**default**) | **2**, genuinely different: one long, one short | **2**, different categories | blank or 1 bonus line |
| Add a third | only when it is a different bet (another lever or awareness stage) | 3 | — |
| Proven winner (spend at KPI), its iterations, scaling | **5**: the 1-2 proven texts + 3-4 challengers | **5** | 1 bonus line |
| Whole account | 5-15 primary texts and headlines live in total; most brands find 3-6 that work and lean on them | | |

Sources: 2 + 2 is the Blueprint M4 setup and Evolve's 3:2:2; short vs long "is actually what the main variable is"
(Denney); three at a time, "completely different" (Blueprint Q&A 2026), and Pellegrini tests 3 texts + 3 titles + 1
description; 5 + 5 per ad, then "combine the best of the best" on high performers (Nick, Blueprint); account totals
(Blueprint Q&A). Why 2 by default: each variant must be a different bet, near-duplicates make "the data muddy"
(Blueprint), and a new concept has little spend to split. Alternative: the Blueprint settings dictionary loads 5 texts +
Meta's AI variations from day one — only worth it when you can write five truly different texts.

### 4. Plan the variants on a matrix before writing
One row per primary text: framework (`references/copy-frameworks.md`), length, awareness stage, self-concept, Mood ×
Intensity zone, lever (offer / mechanism / education), proof type, first-line call-out type. Rules:
- Same side, same promise, same offer in every row — they ride one creative. Variants differ in how they sell, not to whom.
- P1 and P2 differ in length and in at least two of: framework, awareness, zone, lever. Swap test: if their first lines
  could trade places unnoticed, they are one variant.
- Zone fits awareness (toolkit §8): no PANIC for product-aware readers.
- Point the long text at problem-aware/unaware readers (these scale) and the short one at product/most aware (these
  convert): aware-level ads "will not be as scalable as 'problem aware' or 'unaware'" (Evolve).
- At most one offer-led text in a launch pair; across the account only "20 to 30% of total marketing directly calls out
  the offer" (Blueprint Q&A).
Default launch pair: **P1** long story/PAS/founder (problem aware, FATIGUE or COZY, mechanism or education) + **P2**
short proof or offer line (product aware, COZY or JOY, offer). The winner bench adds myth-bust, proof stack, offer stack,
objection-killer or native post — each answering a different question.

### 5. Write the first ~125 characters of every primary text first
Feed shows about 125 characters before "…See more"; Reels and Stories show one or two lines. Most people read nothing
else, so these characters must hook the right side on their own:
- **Signal the side** by role/identity, behaviour, situation, aspiration, or the pain/ceiling (Blueprint's seven
  call-outs). "Why switch from pills to gummies" speaks only to pill-takers and skips the convincing.
- Give a **recognisable moment** and **one concrete number or sensory detail** ("I work as a Registered Nurse for up to
  16 hours a day…", C6).
- Open a loop or name the desire; the line must make sense if nothing else is read. Keep the opening paragraph
  (everything before the first line break) at 125 characters or fewer so it is never cut mid-thought.
- Don't open with the brand, "Introducing", a greeting or a floating claim. Name the product later in the text and in a
  headline (transparency, and reviewers check it).
- Echo the creative's angle in new words rather than re-typing the on-screen text the viewer just saw.
- Compliance: first person or the situation, never "Are you [attribute]?" (`references/copy-compliance.md` §2).
- Count, don't estimate: `python3 -c "import sys; print(len(sys.argv[1]))" "<line>"`.
Patterns: `references/headline-and-hook-bank.md` §1-§3.

### 6. Write the body
- **Specific**: numbers, names, places, timeframes ("day 14", never "fast"); every number true and provable.
- **Desire, not feature**: every feature line lands on a moment regained.
- **Named mechanism** with one everyday metaphor; the cause comes before the product.
- **Proof right after each new claim** (promise, mechanism, benefit): the next sentence proves the last one (Oliver).
- **Dimensionalise the pain** (physical → life → emotional), then mirror it in the outcome.
- **Future-pace to tonight**: put the first win close ("tonight's walk", "your next 12-hour shift") because the brain
  treats "you in 3 months" as a stranger (Pellegrini), and block the "later" escape: one tap, code auto-applied, 2-minute quiz.
- **Answer this side's first objection** (Evolve: "mass objection" is a top reason ads fail).
- **One CTA that names the button** and a real reason to act now — "tell them EXACTLY which button to click" (Oliver).
- **Form**: 1-2-line paragraphs; grade 5-6 reading level (Kell, Oliver); read it out loud (Evolve); ✓ bullets for proof
  stacks; emojis only as markers. Long ≈ 150-400 words (C6), short = one sentence to two lines (Denney). Make CTAs and
  phrasing specific to this ad — "We're not going to write shit with AI" (Blueprint Q&A).
In health, weight, aging and supplement copy attach timeframes to the routine ("10 minutes a day", "a 30-night trial"),
not to outcomes (compliance §3).

### 7. Write the headlines
The headline sits under the creative beside the button; placements cut it at roughly 27-40 characters and some hide it,
so put the meaning in the first ~27 and keep it ≤ 40.
- Each headline is a different category: desire/outcome, named mechanism, proof/count, offer/risk reversal, avatar
  call-out, question, "what they get" (Oliver). "Shop now" vs "Shop today" is one headline (Blueprint).
- Not a repeat of a primary text's first line. Product or brand named in at least one headline or the first lines.
- Prices end in .99: "$29.99 not $30.00"; crossing 49→51 or 99→100 shows a drop (Blueprint).
- A headline that wins is the next creative's hook or on-image line: copy is the cheapest test of what to say
  (Blueprint Q&A).
32 patterns with examples: `references/headline-and-hook-bank.md` §4.

### 8. Description, CTA button, links
- **Description**: blank by default ("doesn't even show up all the time", Blueprint) or one bonus line ("+ free shipping
  over $50"); never essential information.
- **CTA button** (the text must name the same button):

| Button | Use when |
|---|---|
| Shop Now | Default for e-com with price and offer on the page — "the most direct … committing in a micro way" (Blueprint) |
| Learn More | Higher ticket; advertorial, listicle or quiz pre-lander; unaware/problem-aware copy; regulated categories (Blueprint; Oliver's advertorial ads; Evolve CRO) |
| Get Offer / Order Now | Offer-led and most-aware copy, sale periods |
| Apply Now / Get Started | Telehealth and lead gen — "See if you qualify" (Blanchard) |

- **Display link**: short, clean, relevant to the ad (brand.com/curb), same domain as the destination (Blueprint).
- **Site links**: at least four (best sellers, new arrivals, key collections, hero product, FAQs, VSL), labels of about
  25 characters written for this side (Blueprint: "It works. It's helpful.").
- **Promotions extension**: a real code only; write "code auto-applied" only when the link applies it
  (`/discount/CODE?redirect=/path`, Evolve CRO).

### 9. Compliance pass
Run `references/copy-compliance.md` §9 on every field, including headlines and site-link labels. Fix, don't flag and ship.

### 10. Score, save, plan the read
- Score the ad (creative + copy) on the doctrine scorecard and the copy checks under Quality bar; ship at 15+.
- Save the deck to `ads/<product-slug>/ad-copy-<YYYY-MM-DD>.md` (or the user's path). In chat give: side, concept, the
  launch first lines, headlines, CTA, compliance flags and the `[REPLACE]` items still open.
- Launch as a new pack in the prospecting CBO (`andromeda2-launch-testing`); never inject into a live pack, and never edit
  the text of a live winner — an edit re-reviews the ad and risks what it has learned (doctrine R7); ship changed copy as
  a new ad. Read Ads Manager → Breakdown → by dynamic creative element → Text / Headline by spend share after 14 days
  (< $1k/day) or 7 days (≥ $1k/day). If the Text breakdown is missing, switch off "optimized text per person"
  (Blueprint Q&A). Winning lines go into the account copy bank and onto the landing page and emails (Nick).

### Fixing copy on a live ad (diagnose first, with `scripts/a2.py analyze`)
- Weak hook rate → the creative's first seconds, not the text: `andromeda2-video-scripts` / `andromeda2-static-ads`.
- CTR < 80% of the account median with fine hook and hold → the sell: desire, mechanism, proof, offer, CTA. Write a
  challenger set (Step 3, winner row) and ship it as new ads.
- High CTR, weak conversion → wrong side or curiosity bait: tighten the call-out and pre-qualify (who it's for, price, offer).
- Weak click→purchase with fine CTR → message match: same headline idea, avatar and offer on page and ad.
- Iterating a winner's copy layer (headline swaps, hook rewrites, emotional trigger, promise framing) is an iteration of
  the same concept (doctrine R4): `andromeda2-creative-iteration` plans it, this skill writes it.

## Output format

Save as Markdown; one deck per ad (one concept). Template:

```markdown
# Copy deck — [Product] — [A0X] × [template] ([concept ID]) — [YYYY-MM-DD]
Assumptions: [what was inferred]. Every [REPLACE: …] must become the brand's real, provable data before launch.

**Side** [A0X "name"] — [moment] · [feeling] · [desire]
**Concept** [avatar × template] · [concept | iteration of …] · creative hook: "[on-screen line / VO]"
**Page** [URL] · above the fold: "[headline]" · offer: [offer, price.99, guarantee]
**Stage** [new concept → 2 + 2 | winner → 5 + 5] · **CTA button** [button] — why: [page type / awareness]
**Display link** [..] · **Description** [blank | line]

## Primary texts
### P1 — [framework] · [awareness] · [self] · [zone + intensity] · lever: [..] · proof: [..] · first line: [N] chars
[paste-ready text]
### P2 — …

## Headlines
H1 — [text] ([chars]) · [category]
H2 — …

## Bench (load when the ad wins: 5 + 5)
P3-P5 — [framework · tags · first line]   H3-H5 — [text · category]

## Site links
[label] → [URL] (×4)

## Message match
| | Creative | Copy | Page |   (rows: avatar, angle, mechanism, offer/price)

## Compliance notes
[what was softened, what must be verified, open REPLACE items]

## Scorecard
[10 doctrine lines 0/1/2 + total] · copy checks: [pass/fail list]

## Read
[pack name, window, what to read, what a win changes next]
```

### Worked example (fictional brand; every bracketed number is a placeholder)

```markdown
# Copy deck — Glide Chews — A02 × owner-POV curb video (C07) — 2026-11-18
Assumptions: Tamsin & Hound is fictional; mechanism, review count, rating and prices are placeholders.

**Side** A02 "Dan, whose 11-year-old retriever stops at the curb" — the 6:40 p.m. walk · tired of watching him slow
down · wants the full park loop back
**Concept** A02 × owner-POV curb video (9:16 + 1:1) · new concept · on-screen hook: "He used to drag me to the park."
**Page** tamsinandhound.com/curb · advertorial "Why senior dogs stop at the curb (it's not just age)" · offer: 3 tubs
[$89.99] (save [$29.98]), free shipping, 60-day empty-tub guarantee
**Stage** new concept → 2 + 2 · **CTA button** Learn More — why: the click lands on an advertorial that explains the
cushion to problem-aware owners · **Display link** tamsinandhound.com/curb · **Description** blank

## Primary texts
### P1 — F1 story · problem aware · ought self · FATIGUE (low) · lever: mechanism · proof: customer timeline, review count · first line: 118 chars
Every evening at 6:40, Bruno and I walk to the park. This spring he started stopping at the curb and looking up at me.

He's 11. A golden who used to drag me down the street. He's given me 11 good years; I owe him easy walks.

The vet said it was his age. I tried two joint chews. He spat one out. The other did nothing I could see in a month.

Then I learned why the curb is where it shows: as dogs age, the fluid that cushions their joints thins out
[REPLACE: source]. The first steps on hard ground are the stiff ones.

Glide Chews are built around that cushion: green-lipped mussel plus hyaluronic acid to support joint comfort and
mobility [REPLACE: dose per chew + reference].

Week 3, he stopped pausing at the curb. Week 5, he beat me to the door.

— [REPLACE: Dan R., verified buyer — real review, used with permission]

[REPLACE: 4,212] owners rate them [REPLACE: 4.8]★. Give them 60 days. If you don't see a difference, we refund you,
even if the tub is empty.

Tonight's walk is a good one to start on. Tap Learn More to see how the cushion works.

### P2 — F14 short · product aware · ideal self · COZY (low) · lever: offer · proof: review count, guarantee · 121 chars
Senior dog waiting at every curb? [REPLACE: 4,212] owners switched to Glide Chews for the old trot back. 60 days or your money back.

## Headlines
H1 — Back to the full park loop (26) · desire
H2 — 60-day empty-tub guarantee (26) · risk reversal

## Bench (load when the ad wins: 5 + 5)
P3 — F5 myth-bust · solution aware · COZY · education · first line (112): "He's just getting old," right? Partly. But the stiffness you see at the curb has a cause most joint chews skip.
P4 — F12 review stack · product aware · JOY (low) · proof: "What [4,212] senior-dog owners say about Glide Chews:" + 3 real quotes
P5 — F7 offer stack · most aware · JOY · offer: "The 90-day Glide Chews bundle: 3 tubs for [$89.99] (save [$29.98]), free shipping, 60-day empty-tub guarantee." (106)
H3 — Why old dogs pause at curbs (27) · curiosity   H4 — [4.8]★ from [4,212] dog owners (26) · proof
H5 — Glide Chews: support the cushion (32) · mechanism

## Site links
Senior-dog 90-day bundle · How the cushion works · [4,212] owner reviews · Guarantee & FAQs

## Message match
| | Creative | Copy | Page |
|---|---|---|---|
| Avatar | owner of a senior dog at the curb | same | hero photo: dog at a curb |
| Angle | "not just age" | thinning cushion | headline: "it's not just age" |
| Offer | end card: 60-day guarantee | P1, P2, H2 | bundle selector, discount pre-applied |

## Compliance notes
- "Supports joint comfort and mobility"; no disease names (arthritis, dysplasia) in any field.
- P1 is a real customer's words with written consent; his timeline is quoted as his experience; "results vary" on page.
- Review count, rating, prices and guarantee terms must match the live site on launch day; mechanism source on file.

## Scorecard
Side 2 · Moment 2 · Specific 2 (once REPLACE items are real) · Desire 2 · Mechanism 2 · Hook 2 (creative) ·
Distinct intent 2 · Proof 2 · Room-ready 1 (1:1 cut pending) · Compliance 2 → 19/20, ship when placeholders are filled.
Copy checks: all pass; open items = 6 REPLACE fields.

## Read
New pack "A02 | C07 curb POV" in the prospecting CBO. At < $1k/day read Breakdown → Text / Headline by spend share after
14 days. If H3-style curiosity wins later, brief "Why old dogs pause at curbs" as the next static's headline.
```

## Quality bar

Run the doctrine scorecard (`references/andromeda2-doctrine.md` §5) on the whole ad: ship at 15+, rework at 11-14, kill
the idea under 11. Then the copy checks — every one must pass:
- [ ] One side: the first ~125 characters name it by role, behaviour, situation, aspiration or pain, and work alone.
- [ ] Variants pass the swap test; tags differ as Step 4 requires; each zone fits its awareness stage.
- [ ] Same avatar, angle, offer and price as the creative and the page (message-match table filled in).
- [ ] Mechanism named in two sentences or fewer; at least one desire scene in a concrete place and time; one near-term win.
- [ ] Every claim is followed by proof; every number, name, quote and study is real or a `[REPLACE: …]`.
- [ ] Headlines are different categories, ≤ 40 characters, meaning in the first ~27; product or brand named somewhere.
- [ ] CTA button fits the page type and the text names it; description blank or a bonus line; four or more site links.
- [ ] Offer-led copy is the minority; scarcity and deadlines are real.
- [ ] Compliance checklist passed on every field (`references/copy-compliance.md` §9).
- [ ] Reads aloud cleanly at grade 5-6; no generic AI phrasing; not a duplicate of copy already live in the account.
- [ ] Character counts measured, not guessed; the deck is saved and the open `[REPLACE]` items are listed in chat.

## References
- `references/copy-frameworks.md` — 15 primary-text frameworks (story, PAS, listicle, us vs them, myth-bust, founder
  note, offer stack, objection-killer, native post, kindergarten pitch, proof-led, belief builders, short form, regulated)
  with fill-in templates and worked examples, plus close stack, transitions, future pacing, AOV seeds and CTA lines.
  Open at Steps 4 and 6.
- `references/headline-and-hook-bank.md` — anatomy of the first 125 characters, seven avatar call-outs, opener banks
  (C6, Kell, Oliver, C7, Evolve hook forms, by awareness/zone/self), 32 headline patterns with ≤ 40-character examples,
  advertorial headline types, descriptions, CTA lines, display link and site-link labels, emotional language bank.
  Open at Steps 5, 7 and 8.
- `references/copy-compliance.md` — Meta's three-tier review, personal-attribute rewrites, health/beauty/pet claim
  language, telehealth rules, proof integrity, transparency, offers and scarcity, the final checklist and the source
  conflicts resolved. Open at Step 9 and before writing in any regulated category.
- Shared: `references/andromeda2-doctrine.md` (requirements, scorecard), `references/psychology-toolkit.md` (side card,
  desire, mechanism, proof, awareness, self-concept, zones, compliance), `references/metrics-and-diagnosis.md` (diagnosis
  ladder), `scripts/a2.py` (`analyze` for live-ad diagnosis, `economics` before writing an offer-led variant).
