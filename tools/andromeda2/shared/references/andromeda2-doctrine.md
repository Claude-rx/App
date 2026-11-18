# Andromeda 2 doctrine — what the system rewards and the rules that follow

Shared by every `andromeda2-*` skill. Read it once per session before producing creative, copy, a launch plan or a
scaling plan. Edit the master copy in `tools/andromeda2/shared/` and run `tools/andromeda2/sync_shared.py`; the copies
inside each skill are generated.

Contents
1. What Andromeda 2 is (facts)
2. What changed for advertisers
3. The eight requirements
4. The goal metrics and the levers that move them
5. The Andromeda 2 pre-launch scorecard
6. Vocabulary
7. Sources and confidence

---

## 1. What Andromeda 2 is (facts)

"Andromeda 2" is our name for the next-generation Meta Andromeda that Meta described on 28 October 2026
(*Meta Andromeda: Powering the Next Generation of Ads Retrieval Through Model-System Co-Design*, Engineering at Meta).
Facts from that post:

- Andromeda is the **retrieval** stage: the first step of ad delivery. It narrows every eligible ad down to a short list
  in milliseconds; a heavier **ranking** model then scores the short list and the auction picks the winner.
  Stage 0 before it is eligibility ("housekeeping"): location, age, placement fit, exclusions, targeting rules.
- It now **scores every eligible ad** with "near ranking-level" quality, at over one billion ads per second per GPU server
  (about 100x the 2024 system). In 2024 it evaluated tens of millions of ads per second and could not look at every ad in depth.
- Why it was rebuilt: generative-AI creative tools let advertisers produce "hundreds of millions of new ads", so the
  candidate pool exploded. Meta says the system is built to keep absorbing more ads (Advantage+ and genAI volume).
- **User side — a mixture of experts.** A single user tower became "an ensemble of specialized user towers as experts"
  capturing "diverse, time-evolving, and contextualized user interests" from: sequential ad-engagement events,
  user-cohort representations, **LLM-derived semantic features**, and cross-surface co-engagement signals.
- **Ad side — context-aware.** Each candidate ad is encoded jointly with **real-time serving context**.
- **Matching — routing.** An attention-based MoE gating network routes each candidate ad to the most relevant user
  experts (top-K) to produce the user-ad relevance score.
- Reported result: +2.4% conversions on Facebook since 2025 attributed to Andromeda.

## 2. What changed for advertisers

| Before (2024 Andromeda) | Andromeda 2 (2026) | So we… |
|---|---|---|
| Could not read every ad deeply; good ads were missed, weak ads slipped through | Reads every eligible ad nearly as well as the ranking model | Treat "Meta won't spend on it" as a verdict, not bad luck |
| One blended profile per person | Several expert views of the same person ("sides": the tired parent, the dog owner, the gym-goer…) | Write each ad for one side of a person, not a demographic average |
| Ad scored on ad × person | Ad scored on ad × person × **moment** (app, placement, sound on/off, time, what they just did) | Make versions for different rooms and moments |
| Pool of tens of millions | Pool of hundreds of millions, many near-identical AI ads | Generic = invisible; specificity is the only way to win retrieval |
| Volume alone added "shots on goal" | Volume is absorbed easily; near-duplicates compete with each other | Diversity of intent, not diversity of volume |

Practitioner reading (Spencer Pawliw, "Next Gen Andromeda Is Here", 16 Nov 2026), in his analogy: the scouts (retrieval)
used to watch the first quarter of a fraction of the tapes; now they watch every tape start to finish and are almost as
good as the GM (ranking). Bottom line from him: "the strategy doesn't change. You still need more creatives and better
creatives" — but research deeper, write for one side of a person, think about when and how they will see it, and trust
the spend signal. "Meta is just now rewarding good marketing more than ever."

## 3. The eight requirements

Each requirement: the mechanism, the rule, and how to check it.

### R1. One ad = one side of one person
*Mechanism:* separate user experts per interest/identity; the router sends an ad to the experts it matches.
*Rule:* every ad names (internally) the exact side it speaks to — a person in a situation with a feeling and a desire —
never "women 25-45". To reach five different people you need five psychologically distinct ads (Pellegrini: "Une ad = une
personne touchée"). Different sides of the same buyer (a 26-year-old man and a 68-year-old grandmother both whose dog
limps at the curb) are reached by the same ad because the side is shared, not the demographic.
*Check:* can you say in one sentence who this is for, what moment they are in, what they feel, and what they want?

### R2. Write for the moment ("a version for every room")
*Mechanism:* the ad is scored with real-time serving context — placement, app, sound on/off, time of day, recent behaviour.
*Rule:* every concept ships in the formats its rooms need: 9:16 and 1:1 (4:5 is no longer the standard), sound-off proof
(burned-in captions / text carries the message), Reels-native and Feed-native cuts, and — for a strong concept — versions
for different trigger moments (3 a.m. pain vs Saturday-morning ambition). Do not schedule ads to times; let Meta place them.
*Check:* does the ad still work muted, in 9:16, in the first 2 seconds, and does it put the viewer in a recognisable moment?

### R3. Specific or invisible
*Mechanism:* the candidate pool exploded with look-alike AI ads; LLM-derived semantic features let the system tell
"vet approved, free shipping, shop now" apart from the man "whose retriever hesitates at the curb" — and the generic one
has tens of thousands of near-twins.
*Rule:* every ad carries specific moments, behaviours, emotions, desires, named mechanisms, real numbers, names and
timeframes. Replace floating claims ("100% natural", "fast", "expert approved") with anchors ("visible on day 7, peak at
day 30", "Dr. Martin, University of Grenoble", "2,847 customers"). Every number must be true and provable.
*Check:* could a competitor paste their logo on this ad unchanged? If yes, it is generic.

### R4. Diversity of intent, not volume
*Mechanism:* Meta reads the full ad ("every phrase", not the thumbnail or first frame). Ads that say the same thing to the
same side compete for the same experts and look like noise.
*Rule:* vary the **concept** (avatar/side, angle, mechanism, awareness stage, desire, format family) when you need new
reach; vary **components** (hook, lead, visual, actor, CTA, copy) when you need to extend a winner. Every new ad should
answer a different question. A creator's package or a round of similar statics counts as one concept.
*Check:* label each ad `concept` or `iteration` before launch; a pack of 8 ads with 8 identical messages is one ad.

### R5. Trust the spend signal (don't force spend)
*Mechanism:* retrieval now evaluates every ad; zero or near-zero spend is the system's judgement.
*Rule:* test in a CBO with packs and let Meta allocate. The only forcing tool is a short fairness floor: a new pack may get a
daily minimum of 1x target CPA for 7 days, with all live minimums at most 20% of the campaign budget, then removed
(Blueprint M4). Never test in ABO and "graduate"; never keep minimums on for weeks; never pause an ad on one bad day.
Andromeda 2 makes forced spend even less efficient (Pawliw): "if Meta won't spend on your ad, Meta is more right than it's
ever been."
*Check:* how much of the budget is forced (minimums, ABO budgets, scale campaigns)? Keep it under 20%.

### R6. A hyper-competitive account
*Mechanism:* the system concentrates spend on the few ads it rates best; more good ads give it more to choose from.
*Rule:* broad targeting (Advantage+ audience, all placements), one highest-volume prospecting CBO as the core, every new
round of creative launched as a new pack (ad set) — never injected into a live pack — grouped by avatar then concept, 4-8
ads per pack. Spend concentration (two ads taking 90%) is a feature. Keep most ads on: lower-funnel ads with small spend
do real work. Swim lanes by exclusion: prospecting excludes purchasers (180 days + all-time list); retention targets them.
*Check:* is there exactly one place where new creative competes? Are the best ads free to take the spend?

### R7. Clean, uninterrupted signal
*Mechanism:* learnings attach to the campaign/ad set/ad entities; the pixel looks back 28 days; resets throw away learning.
*Rule:* optimise for Purchase (lead gen: the deepest event with 10+/week). Pixel + Conversions API, Event Match Quality ≥ 8.4,
server purchases within ~10% of Shopify orders. Attribution 7-day click + 1-day engaged-view + 1-day view; read decisions
next to the 7-day-click and incremental columns. Do not move ads between ad sets, do not let tools rewrite URLs/UTMs on live
ads (it resets post IDs), do not merge packs because Meta suggests it, avoid more than ~20% of account changes in 3 days.
Learning-phase share of spend ~10-15% is healthy; 85-90% for weeks means you are touching too much.
*Check:* when did each winning ad last reset? Is anything in the account editing live ads automatically?

### R8. Volume with context (Quality × Quantity × Diversity)
*Mechanism:* the system is built for more ads; so is every competitor.
*Rule:* winners = Quality × Quantity × Diversity. AI makes quantity and diversity cheap; quality comes from human research
and judgement (Pellegrini: "L'IA teste vite. Ton cerveau comprend pourquoi."). Volume target: one new ad per week per $10k
of monthly spend (floor 2/week), mix of new concepts and iterations by spend tier — but never pad with ads you would not bet
on. Measure hit rate by creative category and shift production toward the categories that hit.
*Check:* for every AI-generated ad, which human insight (customer phrase, moment, mechanism) does it carry?

## 4. The goal metrics and the levers that move them

Goal: **low CPM, high CTR, high hook and hold rate, low CPC, low cost per purchase (CPP), high ROAS.**

| Metric | Formula | What moves it (creative) | What moves it (structure) |
|---|---|---|---|
| CPM | spend / impressions × 1000 | Ads people engage with natively (comments, shares, saves); native-looking posts; specific relevance so retrieval routes them to the right experts | Broad audience, all placements, no account-level restrictions, interest-winner ad sets that feed the pixel new pockets, no frequency-heavy retargeting |
| Hook rate | 3-second plays / impressions | First 0-3 s: hands demo, product/texture close-up, emotional element, recognisable moment, visual that is hard to argue with; no talking head before the action | — |
| Hold rate | ThruPlays / 3-second plays | Cuts every 1-3 s, movement in every shot, one shot per spoken line, open loop paid off late, lead that agitates or busts a myth | — |
| CTR (link) | link clicks / impressions | Desire (the life regained, not the feature), named mechanism, specific proof, offer and risk reversal, clear CTA | Right side of the right person (R1) |
| CPC (link) | spend / link clicks | = CPM / CTR: both of the above | Same |
| CPP / CPA | spend / purchases | Message match ad → page, pre-qualify in the ad, price/offer framing, awareness-appropriate claims | Purchase optimisation, exclusions, clean signal, hero product |
| ROAS | purchase value / spend | AOV-raising offers (bundles, BOGO, free shipping threshold), selling the gap when priced above market | Value optimisation and ROAS goals at scale; value rules for better cohorts |

Diagnose top-down: hook rate → hold rate → CTR → click-to-purchase CVR. Fix the first weak stage only
(`scripts/a2.py analyze` does this per ad against the account's own medians).

## 5. The Andromeda 2 pre-launch scorecard

Score every ad 0 / 1 / 2 on each line before it ships. Ship at 15+; rework at 11-14; kill the idea under 11.

| # | Requirement | 2 = | 0 = |
|---|---|---|---|
| 1 | One side of one person (R1) | Named side + situation + feeling + desire | "Everyone who…", demographics only |
| 2 | Moment (R2) | Viewer recognises a specific moment in the first seconds | No time/place/trigger |
| 3 | Specificity (R3) | Real numbers, names, timeframes, sensory detail | Floating claims |
| 4 | Desire, not feature | Sells the life moment regained | Sells the spec |
| 5 | Mechanism | Named cause + named solution, linked in 2 seconds | "Natural, clinically proven formula" |
| 6 | Hook strength | Stops the scroll muted in 0-2 s | Logo, slow intro, generic claim |
| 7 | Distinct intent (R4) | Answers a question no live ad answers | Same message as an existing ad |
| 8 | Proof | Proof right after each new claim | Unbacked promises |
| 9 | Room-ready (R2) | 9:16 + 1:1, captions/text, native feel | One crop, needs sound, looks like a banner |
| 10 | Compliance | No personal-attribute callouts ("Are you overweight?"), no unprovable medical claims, honest before/after | Policy risk |

## 6. Vocabulary

- **Side (of a person)** — one identity/interest/state a person moves through (Pawliw); our unit of targeting. An **avatar**
  is a named side with research behind it (A01, A02…).
- **Moment / room** — the situation the person is in when the ad appears (place, time, mood, sound, task).
- **Angle** — the door into the message: why this person stops, now ("Pourquoi ça me concerne ?").
- **Mechanism** — the named cause of the problem (UMP) and the named solution (UMS): "why would it work this time?"
- **Concept** — an avatar put into a proven template with one angle/message; a new concept = a new question asked.
- **Iteration** — the same concept with one component changed (hook, lead, visual, actor, format, CTA, copy).
- **Pack** — one ad set holding one round of creative (one avatar + concept, 4-8 ads) inside the prospecting CBO.
- **King goal** — the single target the account is run on (blended ROAS/MER or CPA from unit economics).
- **Swim lanes** — new / engaged / existing audiences kept apart with exclusions so spend is attributable.
- **Hook rate** — 3-second plays ÷ impressions. **Hold rate** — ThruPlays ÷ 3-second plays.
- **Zombie** — a separate campaign that re-runs fatigued winners and promising losers as fresh ads under a cost control.

## 7. Sources and confidence

- **Fact:** Meta Engineering post, 28 Oct 2026 (section 1).
- **Practitioner, 2026:** Spencer Pawliw video (16 Nov 2026); *The Facebook Ads Blueprint* course and its 2026 live calls
  (Moonlighters agency: M4 structure, packs, minimums, kill tree, scaling, cost controls, zombie campaigns);
  Matteo Pellegrini, *Comment scaler Meta Ads grâce et sans l'IA* (Mastermind Dubai 2026).
- **Evergreen craft:** direct-response copy and VSL courses (Oliver, Kell), Dara Denney's performance-creative course,
  Evolve (Pawliw), Foundr 2020 (dated tactics flagged where used).
- How the MoE "experts" map to "sides of a person" and how serving context maps to "rooms" is a practitioner
  interpretation of the engineering post, not a statement by Meta. Numbers in the rules are heuristics from agencies'
  accounts; the account's own baseline beats any generic benchmark.
