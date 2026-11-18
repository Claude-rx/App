# Research prompts

Prompts from the source courses, cleaned up for reuse. Paste the brand's raw research (reviews, Reddit threads, survey
answers, product facts) above each prompt. Treat every output as a starting point: run it 2-3 times, keep only what matches
real customer language, and never present generated "customer quotes" as real testimonials.

Contents
1. Brand guidelines brief (input for every prompt)
2. Avatar mega-prompt — 20 problems → solutions → 5 avatars (Blueprint)
3. Deep buyer persona — the "$100k avatar" genie prompt (Evolve)
4. 3 a.m. anxieties ladder (Kell)
5. Hook discovery scoring (Evolve CRO)
6. Footage-pattern analysis of winners vs losers (Pellegrini)
7. Daily breakout-winner detector (Blueprint, Claude + Meta Ads MCP)
8. Native-post generator (Pellegrini)

---

## 1. Brand guidelines brief

Fill this first (15-20 minutes; "lackluster input → lackluster output"):
- Homepage + top 3 product links
- Key brand message (the headline you'd put on an ad)
- Starting avatar (good enough to launch the AI)
- Main desire the product serves
- Education: the problems customers have / why the brand exists
- Mechanisms: the unique way the product solves each problem
- Top 3 competitors
- Words and claims we cannot use

## 2. Avatar mega-prompt (Blueprint)

```
You are a direct-response strategist with deep research access. Using the brand brief below and live research of the
brand site, competitor sites, Reddit, forums and reviews in this category:

STAGE 1 — List the 20 most common, specific problems customers in this category have, in their own words, with the source
type for each (e.g. Reddit: "greens powder, hate the taste, can't stick to it").
STAGE 2 — For each problem, the solution our brand/products provide (mechanism + proof we can actually show).
STAGE 3 — Build 5 distinct avatars (identity, situation, aspiration or behaviour — not demographics). For each:
- primary problems
- unknown problems they are not aware of (each a possible hook)
- primary mechanisms and unique solutions that fit them
- current alternatives they use and why those disappoint
- buying objections
- 5 messaging hooks in their language
- 5 creative angle ideas (format + idea)

[BRAND BRIEF]
```
Example output avatar (greens gummies): "the reluctant AG1 refugee" — hook "You've been choking down greens powder for years.
You don't have to anymore." — angles: "The day I finally quit choking", side-by-side monthly cost AG1 vs the gummies, blind taste
test. Modify hooks to the brand's tone; drop avatars that are too sensitive to target.

## 3. Deep buyer persona — the "$100k avatar" genie prompt (Evolve)

Two-part flow: paste the research documents, then:

```
You are a world-class marketing analyst who uncovers a prospect's REAL motivations — not the socially acceptable answers
they'd give in public, but what they think privately. People buy on emotion and justify with logic. Using the documents
above, build a buyer persona with these sections, written in the prospect's own raw, conversational language:

DEMOGRAPHIC — name, age, brief description.
CORE PROBLEM — the central urgent problem; top 5 emotions around it; top 5 fears they would only admit at 3 a.m.; 5 ways
those fears affect specific relationships (spouse, children, friends, co-workers, in-laws); 5 conversational but hurtful
things those people might say (label who says each; include well-meaning supporters and antagonists).
OTHER SOLUTIONS — 5 things they tried, with soundbites about why each failed; what they refuse to do to fix it, with soundbites.
PRIMARY TRANSFORMATION — if a genie gave them the perfect solution: 5 vivid, specific outcomes in their words; how it would
change their emotions, activities, relationships, confidence, how others see them (vanity and superiority are allowed here —
these are drivers they would never admit); post-transformation soundbites from supporters AND doubters forced to admit it.
MARKET SPECIFICS — what they believe their success hinges on; what comfort they would have to give up with the problem;
who/what they blame (internal and external); top 5 objections.
Guidelines: pains, outcomes and past products must be common and widely shared in the audience. Then combine everything
into one comprehensive summary of the persona's deep emotional drivers.
```

## 4. 3 a.m. anxieties ladder (Kell)

Run as a short conversation:
1. "List 20 things [avatar] lies awake anxious about regarding [problem]."
2. "Make them more emotional — things they would never admit publicly."
3. "Tell me a story of one specific night when [avatar] couldn't sleep because of this, in first person, with the room,
   the time, what they did and what they thought."
Use the story for lead scenes in scripts and copy; never as a fake testimonial.

## 5. Hook discovery scoring (Evolve CRO)

List 10-20 customer pain statements (verbatim). Score each 1-5 on Appeal (how many care), Exclusivity (how specific to our
product), Clarity (understood instantly), Motivation (how urgently it moves them). Keep the top scorers (max 20) and turn
each into four hook forms:
- Pain / obvious-yes question ("Still waking up at 3 a.m. with that knee?" — keep it first-person or situational for policy)
- Desired future state ("Tie your grandson's laces without wincing.")
- First-person direct ("I quit glucosamine after 2 years. Here's what I take now.")
- If/then ("If your knee fires every time you stand up, watch this.")

## 6. Footage-pattern analysis of winners vs losers (Pellegrini)

For an agent with read-only access to the Meta account (Meta Ads MCP):
```
You are my media-buying analyst. Connect to my Meta account READ-ONLY; change nothing.
1. Last 90 days. Ignore ads under [X] spend. Group variants of one asset (same video, different hook) as ONE creative.
2. Winners = the 30 highest-spend creatives with ROAS above [threshold]. Losers = the 30 highest-spend creatives with ROAS < 1.
   For each: spend, ROAS, CPA, age in days, hook rate (3-s plays / impressions), hold rate (ThruPlays / 3-s plays).
3. For each video: download it, extract 1 frame per second for the first 15 s, transcribe the voice. If you cannot access
   the video, write "not verified". Invent nothing. Classify each creative:
   A. FOOTAGE (all that apply): hands demo; product/texture close-up; no face in first 15 s; side-by-side or before/after;
      POV; emotional element in first 10 s (child, deep desire, others' gaze, safety); fast cuts (new shot every 1-3 s,
      movement in every shot); hard-to-contest visual hook (neutral everyday object, real demo, no voice before 2 s, reverse
      scene right after). Also: first-shot duration and number of shots in the first 15 s.
   B. PSYCHOLOGY: angle; avatar; mechanism (named cause + named solution, or none); awareness stage; self-concept
      (actual/ideal/ought); Mood × Intensity zone (COZY/JOY/FATIGUE/PANIC); zone × awareness coherence (green/yellow/red —
      e.g. PANIC on a product-aware audience is red).
   C. SCRIPT: does the hook surprise and open a loop? desire = feature or life regained? proof = floating claims or precise
      numbers, names, timeframes?
4. Compare the lists: per pattern, count, % of winners, % of losers; keep patterns present in 5+ creatives.
5. Table: pattern | % winners | % losers | spend-weighted ROAS | hook rate | hold rate.
6. These are correlations: propose one test per pattern that would prove it.
7. End with: the 3 footage patterns to impose on my editor; the 2 most under-used psychological boxes; 3 tests for this week.
```
Reference patterns from his accounts (spend-weighted ROAS): hands demo 0-3 s (2.14), product/texture close-up 0-3 s (1.98),
no face before 15 s (2.3), side-by-side 3-10 s (1.9), POV 0-10 s (1.7), emotional element 0-10 s (2.4), fast cuts throughout (2.5).

## 7. Daily breakout-winner detector (Blueprint)

```
Using the Facebook Ads MCP, build a daily "winning ads" detector for [BRAND] and schedule it every day at 4 a.m.
Pull the last 7, 14 and 30 days: account total spend and average ROAS (account level) and per-ad spend, purchase_roas and
created_time (ad level, sorted by spend). A clear breakout winner = an ad that, in at least one window, (1) was launched in
the last 30 days, (2) took >= 10% of total account spend, (3) beat the account's average ROAS for that window (flag ads right
at the average as borderline). Send one short message per day: brand + date, then one bullet per winner (ad name, top spend
share, ROAS, Ads Manager link) or "No new breakout winners today." For each winner, open an iteration task: analyse what works
and build new iterations that keep the winning concept and hook while testing fresh hooks, angles and formats.
Before scheduling, do one live validation run and show me the result.
```
Tool permissions: allow "get/find" tools always; require approval for "create/update/delete".

## 8. Native-post generator (Pellegrini)

Native Facebook posts bring real comments (your customers' exact words), engagement that lowers CPM, and good buyers.
```
Write 10 native Facebook posts of 3 lines in the voice of an ordinary customer. They tell the pain [X] in their own words.
Zero advertising words. End with a question that invites a comment.
```
Run them as ads from the brand page or a real ambassador. Do not fake comments with fake profiles (a tactic mentioned in the
source) — it breaks Meta's authenticity rules and risks the account.
