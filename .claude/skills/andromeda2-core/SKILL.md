---
name: andromeda2-core
description: Meta (Facebook/Instagram) ads strategy for the Andromeda 2 algorithm (Oct 2026) — builds customer avatars and research for ads (side cards with moment, desire, fear, belief, mechanism, awareness, self-concept), audits ad creatives and whole ad accounts against the eight Andromeda 2 requirements, explains what the new Meta algorithm rewards, and routes to the specialist skills for copy, video scripts, statics, testing, scaling, hard scaling, zombie campaigns and creative iteration. Use this whenever the user mentions Andromeda or the new Meta algorithm, asks to build avatars or personas for Meta ads, wants an audit of their Facebook ads or ad account, asks why their ads stopped working or died, wants creative diversity or 'creative is the targeting' explained, or wants an end-to-end Meta ads plan for a brand. Prefer this over generic persona, audit or ads skills whenever the ads run on Meta, and start here when a Meta ads request does not clearly belong to one specialist skill.
---

# Andromeda 2 — the operating system

Andromeda is the first stage of Meta's ad delivery: it decides which ads are even considered for a person. The 2026
version scores **every** eligible ad with near ranking-level quality, models each person as several "experts" (several
sides of the same person), and encodes each ad together with the **moment** it would be shown in. It was rebuilt because
generative AI flooded the system with near-identical ads. What wins now: ads written for one side of one person, in a
recognisable moment, specific enough that no competitor could swap their logo in — launched in volume, with distinct intent,
into an account structure that lets the algorithm choose.

The goal metrics this whole suite serves: **low CPM, high CTR, high hook and hold rate, low CPC, low cost per purchase,
high ROAS.**

## Before you start

Read `references/andromeda2-doctrine.md` (always — it is the source of truth for every rule in this suite), then the parts
of `references/psychology-toolkit.md` and `references/metrics-and-diagnosis.md` the task needs.

## Route the request

| The user wants… | Use |
|---|---|
| To understand Andromeda 2 / what changed / why ads fail now | This skill → "Explain" below |
| Customer research, avatars, angles, a messaging map | This skill → "Research and side cards" |
| An audit of creatives or of an ad account | This skill → "Audit" |
| Primary text, headlines, CTAs | `andromeda2-ad-copy` |
| Video ad scripts (UGC, founder, demo, mini-VSL) | `andromeda2-video-scripts` |
| Static/image ads across angles and formats | `andromeda2-static-ads` |
| To launch ads / structure tests / read a test | `andromeda2-launch-testing` |
| To spend more on a working account | `andromeda2-scaling` |
| $50k+/day, cost caps, bid caps, ROAS goals, value rules | `andromeda2-hard-scaling` |
| To revive fatigued or dead ads / old winning campaigns | `andromeda2-zombie-campaigns` |
| More winners from current winners; fatigue; next creative batch | `andromeda2-creative-iteration` |
| A full plan for a brand | This skill → "End-to-end plan", then hand off step by step |

When you hand off, carry the side cards and the economics forward so the next skill doesn't redo them.

## Explain

Answer with the doctrine, not folklore. Structure: what the system does (facts from Meta's engineering post) → what changed
vs 2024 → the eight requirements (R1-R8) that follow → what to do this week for *their* account. Label practitioner
interpretations as such (e.g. "experts = sides of a person" is Pawliw's reading, not Meta's wording). Keep it practical:
every point ends in an action.

## Research and side cards

The quality engine of the whole suite. AI makes quantity and diversity cheap; this step is where quality comes from.

1. **Collect raw voice-of-customer**: reviews (own + competitors' 1-3★), Reddit/forum threads, ad comments, support tickets,
   surveys, TikTok/YouTube comments, sales-call notes. Keep verbatim phrases.
2. **Answer the 12 research questions** per candidate side (`psychology-toolkit.md` §1): pain moments of the day, beliefs,
   hidden desire, dream outcome + acceptable effort, tried-and-failed, horror stories, enemy, why it was better before, fear at
   1 and 5 years, why they'd believe this time, awareness, self-concept.
3. **Run the deep-persona prompts** in `references/research-prompts.md` (Blueprint avatar mega-prompt: 20 problems →
   solutions → 5 avatars; Evolve "$100k avatar" genie prompt; anxieties-at-3-a.m. ladder) on the raw research. Treat outputs as
   launch points, not truth — run them 2-3 times and keep what matches real customer language.
4. **Write the side cards** (template in `psychology-toolkit.md` §2): `A01…A0n`, each a side + moment + desire + fear + belief +
   mechanism fit + awareness + self-concept + best Mood × Intensity zone + signature line. Aim for 3-5 sides with real
   evidence; one product usually has several (HexClad: serious meat eaters / money-conscious / home chefs).
5. **Name the mechanism** (UMP + UMS) and the proof you can actually show (numbers, names, timeframes — true and provable).
6. **Build the messaging map**: sides × angles × levers (offer, mechanism, education) × awareness × format templates → the
   concept list for the first rounds (one concept = one side + one template). Mark which questions each concept answers so
   no two concepts ask the same question.

Output: `ads/<brand-slug>/research-<YYYY-MM-DD>.md` with sources, side cards, mechanism, proof bank, objection list,
verbatim phrase bank, and the concept list.

## Audit

### Creative audit (per ad)
Score each ad 0/1/2 on the doctrine's 10-point scorecard (§5) and name the failure reason from the Ad Review Bible list in
`references/audit-checklists.md` (editing, product focus, benefits, text length, visual hook, text hook, belief, identity,
desire, awareness, mass objection, product utility, product value, exhausted visuals, exhausted messaging). If performance data
exists, run `python3 scripts/a2.py analyze export.csv --target-cpa <CPA>` and put the weakest funnel stage next to the score.
Output per ad: score, the one change that would raise it most, concept/iteration label, side it speaks to.

### Account audit (the eight requirements)
Walk `references/audit-checklists.md` → "Account audit": structure (one competitive prospecting pool, packs, exclusions,
retention ≤ 10%), forced spend share, signal health (pixel/CAPI, EMQ, resets, auto-edited URLs), creative diversity (concept
count, avatars covered, formats per placement — top-six placements present), creative cadence vs spend, frequency by
segment, engaged share, incremental vs reported, MER vs Meta ROAS, kill-rule discipline. Each finding: evidence → impact on
the goal metrics → fix → which skill executes it. Rank fixes by expected impact.

## End-to-end plan

For "plan our Meta ads" requests, produce the sequence and hand off:
1. Economics and King goal (`scripts/a2.py economics`).
2. Research and side cards (above).
3. Concept list for 2-4 weeks (sides × templates), with production split video/static by placement needs.
4. Creative production: `andromeda2-video-scripts`, `andromeda2-static-ads`, `andromeda2-ad-copy`.
5. Launch structure and calendar: `andromeda2-launch-testing`.
6. Weekly flywheel: read (7-14 days) → iterate winners / new concepts (`andromeda2-creative-iteration`) → scale when above the
   King goal (`andromeda2-scaling`, `andromeda2-hard-scaling` past ~$50k/month with cost controls) → feed pruned ads to the
   zombie layer (`andromeda2-zombie-campaigns`) once spend justifies it.

## Quality bar

- Every claim about the algorithm traces to the doctrine; interpretations are labelled.
- Side cards are evidence-based (verbatim customer phrases), not demographic guesses.
- Every recommended ad or concept names its side, moment, lever and whether it is a concept or an iteration.
- Audits end in ranked, owned actions tied to the goal metrics.

## References

- `references/andromeda2-doctrine.md` — facts, the eight requirements, lever map, scorecard, vocabulary, sources.
- `references/psychology-toolkit.md` — research questions, side card, desire, mechanism, proof, awareness, self-concept,
  mood × intensity, dimensionalising, angle generators, selling levers, compliance.
- `references/metrics-and-diagnosis.md` — definitions, ranges, windows, diagnosis ladder, kill/winner rules, attribution, frequency.
- `references/research-prompts.md` — the deep-persona and avatar prompts, the footage-pattern analysis prompt, the daily
  breakout-winner prompt.
- `references/audit-checklists.md` — Ad Review Bible (15 failure reasons), pre-brief questions, the account audit checklist.
- `scripts/a2.py` — economics, testing-plan, analyze, scale, cost-controls, cap-diagnose, zombie.
