---
name: andromeda2-creative-iteration
description: Iterating winning Meta (Facebook/Instagram) ads in the Andromeda 2 era — explains why each winner wins against the losers (avatar, template, angle, mechanism, hook, footage, proof, offer), decides iterate vs new concept from spend tier and fatigue, gives the top winner at least 3 one-layer iterations with a hypothesis and target metric each, adds new concepts, writes a mini-brief per ad, and sets naming, launch pack, judging window and weekly cadence; reads an Ads Manager CSV with scripts/a2.py analyze. Use this whenever the user shares an ads export or a winning ad and asks what to make next, why an ad is winning, for variations, iterations, new hooks or more of a winner, plans next week's creative batch, or says a winner is fatiguing, frequency is climbing, ROAS slides as spend rises or they are out of creative. Prefer this over generic ad-creative or hook skills for Meta. Finished scripts, statics and copy go to the andromeda2 video, static and copy skills; dead ads go to andromeda2-zombie-campaigns.
---

# Creative iteration: turn winners into the next batch

This skill takes the ads that win (or nearly win) and produces next week's batch: a forensic read of why each winner
wins, the iterate-vs-new-concept call, one-layer iterations with a hypothesis and a target metric, 1-3 new concepts per
winning avatar, a mini-brief per ad, and the launch-and-learn loop. Andromeda 2 reads every phrase of the full ad, so an
iteration must be a genuinely different ad that keeps the winning avatar and template, while new concepts open new
pockets of people. Iterations sustain spend; concepts unlock it. Ship both every week.

## Before you start

Read `references/andromeda2-doctrine.md` every time (R4 diversity of intent, R5 spend signal, R8 volume with context, the
scorecard). Open `references/metrics-and-diagnosis.md` §3-4, §6 and §8 when reading numbers, and
`references/psychology-toolkit.md` §2 and §4-10 during forensics and when writing new angles.

Gather only what is missing and cannot be inferred:
1. **Ad-level Ads Manager export (CSV)** for the last 30 days and the last 7 days. Columns: ad name, ad set name, amount
   spent, impressions, reach, frequency, link clicks, purchases, purchase conversion value, adds to cart, checkouts
   initiated, 3-second video plays, ThruPlays. Add an Incremental ROAS column (Columns → Compare attribution settings) if
   available; `analyze` uses it. Treat variants of one asset as one creative.
2. **King goal**: target CPA and/or ROAS. Unknown → `python3 scripts/a2.py economics --aov <AOV> --cogs-pct <%>`.
3. **Monthly spend** and the prospecting CBO's daily budget.
4. **The winners themselves**: video files or links (or a transcript plus a description of the first 15 s), statics,
   primary texts and headlines, landing page, top comments.
5. **Capacity and context**: ads the team can make well per week, sources (creators, founder, customers, AI tools), the
   existing avatar/concept library (A01…, C01…), category compliance limits.

If you only get descriptions or screenshots, proceed: mark every metric "not verified" and every guess "assumed".

## Workflow

### 1. Read the account and pick what to dissect
```bash
python3 scripts/a2.py analyze last30.csv --target-cpa 45     # or --target-roas 2.2; both if you have both
python3 scripts/a2.py analyze last7.csv  --target-cpa 45     # same targets: the trend read
python3 scripts/a2.py testing-plan --campaign-budget 2600 --target-cpa 45 --monthly-spend 78000 --new-packs 3
```
`analyze` returns the account baseline (CPM, CTR, hook, hold, cost per ATC/IC, CVR), a verdict per ad (WINNER, KEEP,
CAP, WATCH, TOO-EARLY, PAUSE), the first weak funnel stage per ad ("Fix first": hook → hold → click → purchase against
the account's own medians) and flags (frequency, incremental drop, viral anomalies). `testing-plan` gives this week's ad
count and iteration share. Sort ads into four lists:
- **Winners**: WINNER rows (top ~10% by spend, at KPI, incremental holding). A 9 ROAS on $48 is not a winner (Blueprint).
- **Breakout winners**: launched in the last 30 days, ≥ 10% of account spend in a 7/14/30-day window, ROAS above the
  account average for that window; at the average = borderline, include and flag (Blueprint). The script does not know
  launch dates; check them.
- **Near-winners**: *great spend, poor CPA* (Meta likes the attention, the back half leaks: WATCH rows with a "Fix
  first" stage); *poor spend, great CPA* (KEEP rows with a small share: needs a stronger hook or another format to earn
  spend); "awkward ads" with strong engagement, cheap CPC/CPM and good comments but no sales (Blueprint live calls).
- **Losers for contrast**: the highest-spend ads with ROAS < 1 or PAUSE verdicts (Pellegrini compares the 30
  highest-spend winners with the 30 highest-spend ROAS < 1 ads over 90 days).
Why: iterate what Meta proved with spend and what is incremental. An ad whose incremental cost per purchase is far worse
than its reported one is not worth iterating (Blueprint).

### 2. Winner forensics: say why it wins
For each winner (usually the top 1-3), watch the first 15 s frame by frame, transcribe it and fill the forensics card in
`references/winner-forensics.md`: side (A0X) and moment, template (form factor), angle, mechanism (UMP/UMS), awareness,
self-concept, Mood × Intensity zone and its coherence with awareness, desire (feature or life regained), hook (visual
0-3 s + spoken line + on-screen text), lead and pacing (first-shot length, shots in the first 15 s), footage patterns,
proof (floating or anchored), offer, CTA, copy, landing page, metrics vs account medians, funnel role, comments.
Then write three lines per winner:
- **Why it wins**: "[Side] in [moment] sees [hook], believes [mechanism/proof] and wants [desire]." Name the tension:
  which loop the opening opens and when it pays off.
- **Biggest variable**: format, imagery or message, whichever most likely carries performance (Denney). If all its
  variations spent, the format is working; if one variation took the spend, look at that variation's message and image.
- **Locked DNA**: what every iteration keeps (avatar + template + the biggest variable).

Compare winners with losers on the same grids (footage, psychology, script): each pattern's share among winners vs
losers, keeping patterns seen in 5+ creatives. Every pattern is a correlation, not proof, so each becomes one test
(Pellegrini). Name why losers lost with the 5-question script audit and the Ad Review Bible (both in the reference).
Why: Pellegrini's 522-day winner shared brand, product and format with the loser; only the tension changed (a visible
result early, a hook that opens a loop, a reveal that pays off). AI tests fast; your brain works out why. Without a
"why", iterations are random.

### 3. Decide the mix: iterate vs new concept
Volume: 1 new ad per week per $10k of monthly spend, rounded up, floor 2 (Blueprint). Capacity for quality caps it: if
the team can make three good ads, ship three, not nine medium ones. Base split from `testing-plan`:

| Monthly spend | < $5k | $5-25k | $25-75k | $75-150k | $150-200k | $200k+ |
|---|---|---|---|---|---|---|
| Iterations of proven concepts | ~0% | 15% | 35% | 50% | 65% | 80% |

(Blueprint calculator anchors: ~13/87 at $10k, ~50/50 at $100k, 80/20 at $200k+.) Move it by the account's state:

| State (read on 7-14 days) | Lean | Why |
|---|---|---|
| Below the King goal | "More, then new": iterate what is above target first, then concepts | iterations have the high hit rate; make money first (Blueprint live calls) |
| At/above goal, ROAS flat while spend rises | base split | Twin Engine: the pipeline never stops, above or below goal |
| ROAS or incremental ROAS drifting down as spend rises | more iterations of winning angles and avatars; slow vertical (`andromeda2-scaling`) | the pipeline isn't keeping pace with spend |
| Plateau: one ad carries the account, new packs don't take spend, prospecting 7-day frequency ~5 | more new concepts (new avatars, templates) | iterations sustain but rarely unlock growth; new pockets do |
| A winner shows fatigue | its iterations first (hook, visual) + concepts for its avatar | extend its life while the next one is found |
| Cost-capped, cap missed, budget spent | iterate | the creative has signal (Blueprint) |
| Cost-capped, cap missed, budget not spent | new creative | |
| Cost-capped, cap hit at the true target, budget not spent | iterate hardest | "you're so close" |
| No proven winner yet | new concepts only, angles validated as statics first | nothing to iterate (Pellegrini: static first, then video) |

Plan 3-6 iterations per winner; ship what this week's count allows and queue the rest as later weekly packs (a backlog
goes out week by week, not all at once). Blueprint's range is 1-6 per concept per round; beyond six only at large
spend. Even brands with thousands of live ads run ~10-50 concepts: depth comes from iterations.

**Top-winner priority.** The account's top winner (largest spend at KPI) gets at least 3 of its own iterations in this
week's batch — "You have a winner. Make another one" (Blueprint live calls); it is the highest-hit-rate bet you have.
When a clear winner exists, the `testing-plan` count is a floor, not a ceiling: add its iterations on top if the team can
make them well. If capacity is tight, cut lesser near-winners and extra concepts first, never the top winner's iterations.
Iterations of near-winners (fixing a weak hook on a good body) are welcome, but they count as their own parent's
iterations, not the top winner's.

### 4. Plan the iterations and the new concepts
**Labels.** *New concept (N)* = a new avatar (side), a new template (form factor) or a new angle carried through the
whole ad (a different problem, moment or mechanism). *Iteration (I)* = same avatar + template + angle, one layer of
emphasis changed. *Imitation (M)* = someone else's proven concept rebuilt for us (Evolve).
Avatar-layer conflict: Blueprint's iteration list includes an "avatar layer", while its Andromeda lesson calls a new
avatar on a proven template a new concept. Default: if a different person would see themselves (gym Tom vs dad David),
label it N and give it its own pack; if it is the same person through another lens (awareness stage, price- vs
status-driven, actual vs ideal self), label it I.

**One layer per iteration**, named, chosen from the parent's weakest stage (six layers: message, mechanism, avatar,
education, offer, visual):

| Parent's first weak stage | Layer | Change | Metric that should move | Keep |
|---|---|---|---|---|
| Hook rate < 80% of median | Message (hook) or Visual (first frame) | new visual hook + first line; 3-5 hooks (Oliver) | hook rate | body, CTA |
| Hold < 80% of median, hook fine | Education (lead) or Visual (pacing) | new lead: agitate, myth-bust, story from the climax; a cut every 1-3 s, one shot per line | hold rate | hook |
| CTR < 80% of median, watch fine | Message (desire/promise), Mechanism or Offer | sell the moment regained, name cause and fix, anchored proof, offer + risk reversal, direct CTA | link CTR | hook + lead |
| CVR < 60% of account, cost/ATC high | Offer (incl. landing page) | the page repeats the ad's headline, angle and offer; price reveal; pre-qualify in the ad | CVR, cost per IC | the ad |
| CPA fine, ROAS low | Offer (AOV) | bundle, BOGO, free-shipping threshold | AOV, ROAS | the ad |
| No weak stage (a true winner) | Message (new trigger, self-concept, zone), Visual (new actor/scene), Avatar slice | reach new pockets of the same avatar | spend share at KPI | locked DNA |

**Distinct, not duplicate.** Meta reads "every phrase" of the full ad, not the thumbnail; a new lead-in + hook on the
same body, or a new body behind the same hook, is read as a different ad (Blueprint live calls). Human test: watch
parent then child; if it feels like the same ad twice, it is noise. Colour swaps, filters, mirrored shots and "15
versions of one idea" add volume, not intent (Selena). Swapping hooks between two live winners did nothing in their
tests, so write new hooks instead. Change one layer, and change it boldly.

**Menus** (full lists in `references/iteration-layers-and-menu.md`): Denney's 13-item menu; Nick's ways to milk a
high-delivery winner (voiceover swaps, music, a recut that starts on a new hook, statics from the video, landing-page
tests, price anchoring, new copy, interest-winners, splicing two winners, a winning voiceover moved onto another video);
Selena's prompt "produce 10 big swing variations, changing one element at a time"; keep the hook and inject an offer
segment when the back half leaks; the same script re-shot with a new creator or a real customer.

**New concepts, 1-3 per winning avatar**, from: the winning avatar in a new template; the winning avatar's other problems
("one winning avatar opens the door to multiple angles for that same person": GLP-1 users → hair loss, metabolism,
digestion); a new avatar on the winning template; a sub-problem or new mechanism (back pain → degenerative discs,
Oliver); a competitor concept seen running many variations ("steal like an artist"); 1-of-1 content only you can make
(real customers, your wins log). When production is the bottleneck, prove a new angle as a static first.

### 5. Spec every new ad
Write a mini-brief per ad (template under Output format): label and parent, the one layer changed, the locked DNA, a
hypothesis with a metric and threshold ("hook rate 29% → ≥ 31%, the account median"), side + awareness + self-concept +
zone, 2-3 hooks (visual 0-3 s, spoken, on-screen text), body and visual notes (footage patterns, a cut every 1-3 s, one
shot per line, no face before the action when the action is the hook), anchored proof, offer + CTA, copy seeds, sizes
(9:16 and 1:1, burned-in captions) and compliance notes. Run Evolve's pre-brief questions and the doctrine scorecard;
ship at 15+. Hand production off: video → `andromeda2-video-scripts`; statics → `andromeda2-static-ads`; primary texts
and headlines → `andromeda2-ad-copy`. Pass them the brief; they write the finished script, design and copy.

### 6. Launch and learn
- **A new pack every round.** Iterations and concepts go into a new ad set in the prospecting CBO, grouped by avatar
  then concept, 4-8 ads per pack (two is acceptable). Never inject into the winner's live ad set and never edit the
  winner: edits and URL/UTM rewrites reset its learning (one account lost 27% ROAS when an integration rewrote UTMs on
  every ad, Blueprint live calls). Build settings and the optional new-pack floor (1× target CPA/day, all floors ≤ 20%
  of the campaign budget, 7 days, then removed) are in `andromeda2-launch-testing`.
- **Naming** so reports split by layer and category: pack `broad_<A0X>_<C0X>-<concept>_P<nn>`; ad
  `<A0X>_<C0X>_<I|N|M><n>-<layer>-<what>_<VID|STA|CAR>_<creator>_B<batch>` (e.g. `A01_C01_I3-hook-lastup_VID_maya_B18`).
- **Judge** after 14 days below $1k/day and 7 days at $1k+/day; earliest ad verdict at 2× target CPA spent (Blueprint).
  Read the pack first ("does this avatar/concept work?"), then the ads. An iteration succeeds when it earns spend at
  KPI; it does not have to beat its parent ("this is a provable concept", Blueprint live calls). Five of six iterations
  flopping while the parent holds is a normal hit rate; keep batting. Keep sale creative in its own campaign and never
  judge evergreen iterations on sale or post-sale days.
- **Sales and holidays don't pause the pipeline.** Evergreen iterations launch on the normal cadence into the core CBO
  even in Black Friday / holiday weeks ("so evergreen keeps flowing" — Blueprint); exclude the sale and post-sale days
  from the judging window and extend it by that many days. Postpone only if the user asks.
- **Classify** each test (Evolve): Winning (great spend, great CPA) → it becomes a parent; Poor spend, great CPA → keep
  it on, iterate hook or format to earn spend; Great spend, poor CPA → keep the attention, rebuild the back half (offer,
  mechanism, CTA, page); Poor spend, poor CPA → log the reason from the Ad Review Bible and retire it.
- **Log** the round in the concept library (avatars A01…, concepts C01…, test log, hit rate by creative category and by
  layer) and steer next week's production toward what hits. Going from 5% to 10% winners doubles your scaling (Pellegrini).
- **Cadence** (Blueprint flywheel): launch Monday → passive read Friday → final read and briefs the next Monday → 7-14
  days of production → new ads every Monday. Run the breakout-winner check daily or weekly (prompt in
  `references/winner-forensics.md`) so every new winner gets iterated within a week.

### Fatigue vs normal decay
**Not fatigue; leave the creative alone:** a ROAS dip after a budget raise while cost per ATC stays flat (new
impressions convert later: hold the line); one bad day; post-sale days; daily rotation between ads; CPM up 30%+ across
the whole account with no seasonal reason (competition: refresh broadly, not this ad).
**Fatigue on a winner** (7-14 days vs its own prior 14-30 days, at flat or lower budget): prospecting 7-day frequency
past ~3-3.5; hook rate and CTR falling while CPM is flat; CPA rising or ROAS falling at stable spend; Meta moving its
spend share to other ads; the market saturated with the same visual or message (Evolve: exhausted visuals/messaging).
1. Still at KPI → leave it on and unedited, remove any floor left on its pack, ship its iterations now. Never pause a
   winner at KPI, and never the top spender while the account is on target (accounts that do improve for 3-7 days,
   then fall below target).
2. Below KPI → follow the pausing tree in `references/metrics-and-diagnosis.md` §6 (watch within 50% of KPI on 7-14
   days; cap a pack that carries the account; pause at ≥ 3× CPA and 50%+ off).
3. Once paused → hand it to `andromeda2-zombie-campaigns` (fatigued winners are its first bucket, bid cap at breakeven CPA).
4. If a winner's value is its comments and social proof, iterations cannot copy that; reuse its post ID when it is
   duplicated into interest-winners or retention (`andromeda2-scaling`).
"Rotate creatives every 5-7 days" (Blanchard, telehealth 2024) is pre-Andromeda advice: iterate and add concepts
instead, and never rotate out a winner that is still at KPI.

## Output format
Save to `ads/<product-slug>/creative-iteration-<YYYY-MM-DD>.md` unless the user names a path, then summarise in chat:
the winners and why they win, the mix, the batch table, the launch date and the judge date.

```markdown
# Creative iteration · <brand/product> · <date>
## 1. Account read
<analyze baseline (30d and 7d), King goal, on/off target, monthly spend>
This week: <n> ads = <i> iterations + <c> new-concept ads (<k> concepts). Why: <tier + state>.
## 2. Winners, near-winners, losers
| Ad | Verdict | Spend (share) | CPA/ROAS | Hook | Hold | CTR | CVR | Fix first | Class |
## 3. Forensics (one card per winner)
<card> · Why it wins · Biggest variable · Locked DNA
## 4. Winners vs losers (correlations, not proof)
| Pattern | Winners | Losers | Test it becomes |
## 5. Fatigue watch
| Ad | 30d → 7d: hook / CTR / CPM / CPA / 7-day frequency | Read | Action |
## 6. Next batch
| # | Ad name | Type | Parent | Layer changed | Stays | Hypothesis | Metric → target | Hook (visual / spoken / text) | Format | Hand-off |
## 7. Mini-briefs
### <ad name>
Type · Parent · Side and moment · Awareness · Self-concept · Zone
Layer changed: <layer>: <what>  |  Stays: <locked DNA>
Hypothesis: because <evidence>, <change> will move <metric> from <a> to ≥ <b>
Hooks: 1) visual / spoken / text  2) …  3) …
Body and visual notes · Proof (real, anchored) · Offer + CTA · Copy seeds · 9:16 + 1:1 · Compliance · Hand-off
## 8. Launch plan
| Pack (ad set) | Ads | Floor (1× CPA, 7 days) | Launch | Judge on |
Winners untouched; nothing injected into live packs; total floors ≤ 20% of the campaign budget.
## 9. Library and hit rate
Avatars and concepts added/updated · test-log rows · hit rate by category and by layer · hand-offs (zombie, scaling)
## 10. Queue for the next rounds
```

A complete worked example (dog joint chews, $78k/month, account 12% off target, a fatiguing UGC winner) is in
`references/worked-example.md`. Read it once before writing your first report.

## Quality bar
- Every new ad passes the doctrine scorecard (ship at 15+/20) and Evolve's pre-brief questions; every AI-made ad
  carries a human insight (a customer phrase, a moment, a mechanism).
- Every winner has a "why it wins" line naming side, moment, tension and belief, not "good hook".
- Each iteration changes exactly one named layer, states what stays, and carries a hypothesis with a metric and a
  target; parent and child would not feel like the same ad twice.
- Each new concept names its avatar + template (+ angle) and answers a question no live ad answers.
- The mix follows the spend tier, moved only for a stated account state; the count fits real production capacity.
- The top winner has at least 3 of its own iterations in this batch, and the batch ships on the normal cadence (sale
  weeks change the judging window, not the launch).
- Winners stay live and unedited; everything new goes into new packs; no floors stay on fatiguing ads; fatigued winners
  below KPI go through the pausing tree to the zombie hand-off.
- Metrics come from the export or are marked "not verified"; winner-vs-loser patterns are labelled correlations, each
  with one test.
- Compliance (`references/psychology-toolkit.md` §12): no personal-attribute call-outs, no invented studies, doctors,
  reviews or numbers, no fake scarcity; every placeholder (review counts, results, mechanism names) is flagged for
  replacement with the brand's provable data.
- The report is saved and summarised in chat.

## References
- `references/andromeda2-doctrine.md`: always; R4 concept vs iteration, R5, R8, the scorecard.
- `references/metrics-and-diagnosis.md`: diagnosis ladder, windows, kill/keep/winner rules, frequency caps.
- `references/psychology-toolkit.md`: side card, mechanism, awareness, self-concept, Mood × Intensity, angle generators, compliance.
- `references/winner-forensics.md`: Step 2. Forensics card, footage/psychology/script grids, winners-vs-losers prompt,
  script audit, Ad Review Bible, test classes, breakout-winner prompt, reporting breakdowns.
- `references/iteration-layers-and-menu.md`: Steps 3-6. The six layers, distinctness rules, iteration menus, hook
  patterns, new-concept generators, mix and cost-cap logic, fatigue table, brief templates, concept library and naming.
- `references/worked-example.md`: one complete iteration report.
- `scripts/a2.py`: `analyze` (verdicts + weakest stage per ad), `testing-plan` (weekly volume and mix), `economics` (targets).
