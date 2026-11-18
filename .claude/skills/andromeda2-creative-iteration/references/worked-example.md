# Worked example: one complete iteration report

A made-up brand ("Halden", senior-dog hip & joint chews, AOV $68) so the shape of the deliverable is concrete. The
account numbers below are real `scripts/a2.py` output on a sample export, but the brand, ads, review counts, results and
mechanism names are **placeholders**: replace every one with the brand's real, provable data before anything ships. Pet
supplements may not make disease or treatment claims; the copy describes the experience and the brand's documented
formulation only.

Inputs the user gave: 30-day and 7-day ad-level exports, target CPA $45 (from `a2.py economics`), prospecting CBO at
$2,600/day (~$78k/month), capacity of ~8 good ads a week (one in-house editor, two UGC creators, customers willing to
film), links to the three top ads. Saved as `ads/halden-joint-chews/creative-iteration-2027-01-11.md`.

---

# Creative iteration · Halden hip & joint chews · 2027-01-11

## 1. Account read

```bash
python3 scripts/a2.py analyze halden_30d.csv --target-cpa 45
python3 scripts/a2.py analyze halden_7d.csv  --target-cpa 45
python3 scripts/a2.py testing-plan --campaign-budget 2600 --target-cpa 45 --monthly-spend 78000 --new-packs 3
```

| Metric (30 days) | Account | | Metric (7 days) | Account |
|---|---|---|---|---|
| Spend | $77,030 | | Spend | $16,020 |
| CPA | $50.51 (target $45: **OFF**, 12% over) | | CPA | $46.43 (OFF, 3% over) |
| CPM | $13.57 | | CPM | $13.32 |
| CTR (link) | 1.1% | | CTR | 1.1% |
| Hook / hold | 31.2% / 18.8% | | Hook / hold | 33.0% / 20.0% |
| Cost per ATC / IC | $10.89 / $22.07 | | Cost per ATC / IC | $10.81 / $21.11 |
| Click → purchase CVR | 2.5% | | CVR | 2.6% |

Context: budget went from $2,000 to $2,600/day three weeks ago; four weak packs from batches 13-16 dragged the 30-day
CPA; the 7-day read is recovering but still above target.

**This week: 8 ads = 5 iterations + 3 new-concept ads (3 concepts).** The calculator says 8 ads at a 50/50 split
($75-150k tier). The account is below its King goal, so "more, then new": one slot moves from new concepts to
iterations of what is above target. No budget raise this week (`andromeda2-scaling`: 0-25% below target → hold or trim
and ship iterations of the winners first).

## 2. Winners, near-winners, losers (30 days unless noted)

| Ad | Verdict | Spend (share) | CPA | Hook | Hold | CTR | CVR | Fix first | Class |
|---|---|---|---|---|---|---|---|---|---|
| W1 `A01_C01_N1-stairs-ugc_VID_maya_B12` | WINNER | $21,400 (28%) | $38.01 | 34% | 22% | 1.21% | 3.0% | none | Winning |
| W2 `A01_C02_N1-glucosamine-myth_STA_B14` | WINNER | $12,600 (16%) | $38.18 | — | — | 1.00% | 3.1% | none | Winning |
| `A01_C01_I1-hook-carride_VID_maya_B15` | KEEP | $6,200 (8%) | $38.75 | 31% | 21% | 1.15% | 3.3% | none | Winning (hook iteration of W1) |
| `A02_C06_N1-usvsthem_STA_B16` | KEEP | $4,400 (6%) | $43.56 | — | — | 0.98% | 2.9% | none | Poor spend, great CPA |
| `A01_C11_N1-native-post_STA_B17` | KEEP | $650 (1%) | $36.11 | — | — | 1.10% | 2.5% | none | Poor spend, great CPA |
| NW1 `A02_C05_N1-mile3-pov_VID_B16` | WATCH | $9,900 (13%) | $79.20 | 41% | 19% | 1.41% | 1.4% | clicks but no buyers | Great spend, poor CPA |
| `A01_C03_N1-founder-story_VID_B13` | WATCH | $5,800 (8%) | $72.50 | 22% | 12% | 0.80% | 2.2% | body loses them | Great spend, poor CPA |
| `A01_C01_I2-hook-textonly_VID_B15` | WATCH | $2,300 (3%) | $74.19 | 24% | 20% | 0.90% | 2.1% | none | Poor spend, poor CPA (so far) |
| L1 `A01_C04_N1-vet-explainer_VID_B13` | PAUSE | $4,200 (5%) | $140.00 | 18% | 9% | 0.70% | 1.4% | weak first 3 s | Poor spend, poor CPA |
| L2 `A02_C08_N1-agility-ugc_VID_B14` | PAUSE | $3,300 (4%) | $126.92 | 30% | 10% | 1.05% | 1.1% | body loses them | Poor spend, poor CPA |
| L3 `A03_C07_N1-rescue-senior_VID_B15` | PAUSE | $3,100 (4%) | $147.62 | 27% | 13% | 0.85% | 1.3% | clicks but no buyers | Poor spend, poor CPA |
| L4 `A02_C10_N1-carousel-hikes_CAR_B16` | PAUSE | $1,200 (2%) | $133.33 | — | — | 0.75% | 1.2% | watched, not clicked | Poor spend, poor CPA |

No breakout winner this week (nothing launched in the last 30 days holds ≥ 10% of spend above the account average).
Incremental column not available in this export: treat W1/W2's incrementality as **not verified**; add the column
before the next read.

## 3. Forensics

**W1 · `A01_C01_N1-stairs-ugc_VID_maya_B12`** (28 s UGC, creator Maya and her 11-year-old Labrador)
- Side: **A01 "Dana and the stairs"**: owner of a large senior dog who has started hesitating; moment = the evening
  climb to bed, the dog stopping at step one. Template: UGC testimonial at home. On screen: a woman in her 50s, a large dog.
- Angle: the moment you notice he's slowing. Desire: life regained ("he races me up again"), not "supports joints".
- Mechanism (placeholder, brand to supply its real named cause and fix): line at 0:14 "the treats he had were mostly
  [filler]; this has [named active] at the amount for his weight."
- Awareness: problem aware. Self-concept: ought ("I owe him easy last years"). Zone: FATIGUE (quiet commiseration):
  green with problem aware.
- Hook 0-3 s: visual = the dog stops at the first step, her hand on his back (first shot 2.1 s, no face until 0:05);
  spoken = "Eleven years old, and last spring he started stopping right here."; text = "He stopped racing me up the
  stairs." Loop: will he climb? Paid at 0:24 when he climbs the stairs (customer-reported week-3 result: placeholder).
- Body: story lead; 11 shots in the first 15 s, longest 2.4 s, motion in every shot, one shot per line. Patterns: no
  face before the action, emotional element (his look back at her), hands, fast cuts.
- Proof: "[X,XXX] reviews" (placeholder), her dated timeline "week 3" (placeholder). Offer + CTA: first bag 30% off on
  subscription + 60-day guarantee (placeholder); "Tap to see the 60-day guarantee." Page: product page; headline matches.
- Comments: "mine does exactly this at the car door", "how long until you saw a difference?", "is it ok with his meds?"
- **Why it wins:** Dana, at the bottom of the stairs at night, sees her own dog's hesitation, believes it because the
  ad names why the treats didn't work and shows a dated result, and wants the dog who raced her back. The tension (will
  he climb?) is opened at 0:01 and paid at 0:24.
- **Biggest variable:** message + moment (the stairs hesitation). Its hook iteration I1 (car door) also hit at $38.75,
  so the "first-person moment of noticing" carries, not Maya herself.
- **Locked DNA:** A01 + UGC testimonial + a recognisable moment of hesitation in 0-3 s with the result paid late.

**W2 · `A01_C02_N1-glucosamine-myth_STA_B14`** (static): A01, solution aware; headline "Why the joint treats stopped
working after his 10th birthday" (placeholder claim; must match the brand's evidence); product bag on a plain
background. Why it wins: it answers the tried-and-failed buyer's question ("why would this work this time?"). Biggest
variable: the message (myth-bust). Locked DNA: A01 + named-mechanism static + the myth-bust headline. CTR 1.00% is
below the account's 1.1%: the image is the weak part.

**NW1 · `A02_C05_N1-mile3-pov_VID_B16`** (POV hike video): A02 "weekend hiker" (owner of an active 7-year-old shepherd
who lags on mile 3). Hook 41% and CTR 1.41% are the account's best, so Meta likes the attention; CVR 1.4% vs 2.5% and
cost per IC far above average = the back half and the page leak. The page is the senior-dog product page ("Help your
old friend"): the active-dog promise is lost on click. Class: great spend, poor CPA → keep the hook and lead, fix the
offer and page match.

## 4. Winners vs losers (correlations, not proof; fewer than 5 creatives per pattern, so hypotheses only)

| Pattern | Winners + keepers (5) | Losers (4) | Test it becomes |
|---|---|---|---|
| Opens on a specific moment of the dog (0-3 s) | 4/5 | 1/4 | every new A01 hook opens on a dog moment (I3) |
| Face or credentials before the action | 0/5 | 2/4 (vet explainer, agility) | brief rule: no face before the action in hooks |
| Named cause/fix in the first 15 s | 2/5 | 0/4 | education-layer lead on W1 (I5) |
| FATIGUE zone with a problem-aware side | 3/5 | 0/4 | keep A01 in FATIGUE; test ideal-self JOY later |
| Montage of generic scenery, no single moment | 0/5 | 2/4 (carousel, agility) | retire montage templates for now |

Losers, tagged with the Ad Review Bible: L1 vet explainer #5 visual hook (talking head + credentials first) and #4 text
length; L2 agility #1 editing (montage, shots 4-6 s) and #3 benefits (agility is not the active owner's problem); L3
rescue senior #7 belief (no reason it works for a newly adopted dog) and page mismatch; L4 carousel #9 desire (scenery,
no desire).

## 5. Fatigue watch

| Ad | 30d → 7d | Read | Action |
|---|---|---|---|
| W1 stairs UGC | hook 34% → 29%; CTR 1.21% → 1.01%; CPM $14.0 → $14.2; CPA $38.01 → $43.88; 7-day frequency 3.6 (was ~2.4 four weeks ago, placeholder) | early fatigue: attention falling at flat CPM, still at KPI | keep on, no edits, no floor; ship I3-I5 now; re-read in 7 days |
| W2 glucosamine static | CPA $38.18 → $38.75; CTR flat | healthy | one visual iteration (I6) |
| Four PAUSE ads | ≥ 3× CPA spent, 50%+ off KPI, account off target | pausing tree: pause | pause; queue for the zombie "dud" or "no_efficiency" bucket (`a2.py zombie` decides) (`andromeda2-zombie-campaigns`) |

## 6. Next batch

| # | Ad name | Type | Parent | Layer changed | Stays | Hypothesis | Metric → target | Hook (visual / spoken / text) | Format | Hand-off |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `A01_C01_I3-hook-lastup_VID_maya_B18` | I | W1 | Message (hook: new moment) | body 0:04-0:28, CTA, creator | a fresh moment restores attention lost to frequency | hook 29% → ≥ 31% | dog pushing up from his bed, back legs slow / "He used to be first at the door. Now he's the last one up." / "Last one up now." | 9:16 + 1:1 video | video-scripts |
| 2 | `A01_C01_I4-visual-newowner_VID_tom_B18` | I | W1 | Visual (new owner + dog) | script word for word, pacing | a man in his 60s with a senior shepherd reaches owners who don't see themselves in Maya | hook ≥ 31%, spend share in pack at KPI | his dog stopping at the porch step / same line / same text | video | video-scripts |
| 3 | `A01_C01_I5-edu-mythlead_VID_maya_B18` | I | W1 | Education (new lead 0:04-0:12) | hook, ending, CTA | busting "it's just age" holds the problem-aware viewer longer | hold 22% → ≥ 24% | W1 hook / then "The vet said 'he's just getting old.' That's not the whole story." | video | video-scripts |
| 4 | `A01_C02_I1-visual-stairsimg_STA_B18` | I | W2 | Visual (image) | headline, layout, offer | the stairs moment (W1's DNA) beats a product shot | CTR 1.00% → ≥ 1.1% | senior dog lying at the foot of the stairs, looking up / — / same headline | 1:1 + 9:16 static | static-ads |
| 5 | `A02_C05_I1-page-hikerpage_VID_B18` | I | NW1 | Offer (page + offer framing) | the whole video | a page that repeats "keep up on mile 3" + the guarantee recovers the lost buyers | CVR 1.4% → ≥ 2.5%; cost/IC ≤ $22 | unchanged | same video, new URL | ad-copy (page headline) |
| 6 | `A01_C13_N1-checkin-1of1_VID_custJ_B18` | N (template: real-customer interview) | — | — | A01 | a real repeat buyer's six-month check-in is proof no competitor can copy | spend at CPA ≤ $45 | the dog trotting up the stairs at month 6 / "Six months ago I filmed him stopping here. Watch." / "Month 6." | video | video-scripts |
| 7 | `A01_C14_N1-sidebyside_STA_B18` | N (template: side-by-side static) | — | — | A01 + W2 message | side-by-side proof carries the myth-bust further than a single image | CTR ≥ 1.1%, CPA ≤ $45 | left "his old treats: [label facts]" / right "Halden: [label facts]" (real label data only) | static | static-ads |
| 8 | `A01_C15_N1-shrinkingwalk_VID_maya_B18` | N (angle: another problem of A01) | — | — | A01 + UGC | "the walk that shrank" opens a pocket the stairs story doesn't reach | spend at CPA ≤ $45 | her watch showing 9 minutes / "Our walks went from 40 minutes to the end of the block." / "40 min → 9 min." | video | video-scripts |

Planned 3-6 per winner, shipped as the count allows; the rest is queued in section 10.

## 7. Mini-briefs (two shown in full; the others follow the same template)

### `A01_C01_I3-hook-lastup_VID_maya_B18`
Type: I of W1 · Side: A01 Dana, the morning moment (he's the last one up) · Problem aware · Ought self · FATIGUE
Layer changed: message (hook): a new moment of noticing in 0-4 s | Stays: W1's body 0:04-0:28, the climb payoff, CTA, Maya
Hypothesis: W1's hook rate fell 34% → 29% at flat CPM as frequency rose; a fresh moment from the same day should bring it back to ≥ 31% (account median) without touching what converts.
Hooks:
1) dog pushing up from his bed, back legs slow (no face) / "He used to be first at the door. Now he's the last one up." / "Last one up now."
2) his lead hanging by the door, he doesn't get up / "He used to hear the lead and run." / "He used to run for this."
3) close-up of paws on the kitchen tiles, slipping / "This is the sound I started hearing every morning." / "Every morning."
Body and visual notes: reuse W1 from 0:04; cut every 1-3 s; one shot per line; burned-in captions; no face before 0:04.
Proof: same dated timeline and review count as W1 (placeholders until verified) · Offer + CTA: unchanged.
Copy seeds: keep W1's primary text; one headline variant "He's not 'just old'" (`andromeda2-ad-copy`).
Compliance: no claims beyond W1's approved claims; no "Is your dog arthritic?" style call-out.
Hand-off: `andromeda2-video-scripts` (hook options + editor notes).

### `A01_C13_N1-checkin-1of1_VID_custJ_B18`
Type: N, new template (real-customer interview) · Side: A01 · Problem → product aware · Actual self ("I did right by him") · COZY
Concept: a repeat customer (placeholder "Jo", 3 orders, wrote a review) films a six-month check-in at home.
Hypothesis: 1-of-1 proof (a real person, a dated result) wins on belief where creator UGC is fatiguing; success = spend
at CPA ≤ $45 within its pack.
Hooks:
1) dog trotting up the stairs / "Six months ago I filmed him stopping here. Watch." / "Month 6."
2) her phone showing the old clip, then the live dog / "This was him in June." / "June vs now."
3) the empty bag on the counter / "Third bag. Here's why I keep reordering." / "Why I reorder."
Structure (30-45 s): hook → the moment she noticed → what she tried → why she chose it (the brand's real mechanism line)
→ what changed, with her own dates → guarantee → CTA. Interview guide: 30 s answers; "what did you notice first, what
did you try, what changed and when?"
Proof: her real order history and dates only; written consent; she is a real customer, not an actor; disclose free
product if given.
Hand-off: `andromeda2-video-scripts` (interview guide + edit plan).

(Briefs 2-5, 7 and 8 follow the same template; static briefs go to `andromeda2-static-ads`, the page headline for #5
to `andromeda2-ad-copy`.)

## 8. Launch plan

| Pack (ad set) in the prospecting CBO | Ads | Floor (1× CPA, 7 days) | Launch | First read | Judge on |
|---|---|---|---|---|---|
| `broad_A01_C01-C02-iter_P18` | #1-#4 | $45/day | Mon 18 Jan | Fri 22 Jan | Mon 25 Jan (7-day window at $2.6k/day) |
| `broad_A01_newconcepts_P19` | #6-#8 | $45/day | Mon 18 Jan | Fri 22 Jan | Mon 25 Jan |
| `broad_A02_C05-pagetest_P20` | #5 | $45/day | Mon 18 Jan | Fri 22 Jan | Mon 25 Jan |

Total floors $135 ≤ $520 (20% of $2,600). Floors come off after 7 days whatever happens. W1, W2 and every live pack stay
untouched: no edits, no new ads injected, no URL or UTM changes. Earliest ad verdict at $90 spend (2× CPA); pause rule
at $135 and 50%+ off KPI. Success for an iteration = its pack spends above the floor at CPA ≤ $45; it does not need to
beat W1.

## 9. Library and hit rate

- Avatars: A01 Dana and the stairs (validated, 2 winning concepts); A02 weekend hiker (testing: great hook, page
  mismatch); A03 rescue adopter (1 failed concept: belief); A04 "he's not old, he's just slower" (queued).
- Concepts: C01 A01 × UGC testimonial (validated, iterations I1 hit, I2 watch, I3-I5 launching); C02 A01 × named-mechanism
  static (validated); C05 A02 × POV hike video (great spend, poor CPA; page test); C13-C15 new (testing).
- Hit rate, last 90 days (placeholder counts): UGC testimonial 6 launched / 2 winners (33%); named-mechanism static 4/1
  (25%); native post 2/1 (50%, small n); POV video 3/0; talking-head explainer 4/0; carousel 3/0. By layer: hook
  iterations 2/1. Production shifts toward UGC moments and mechanism statics; explainers and carousels pause.
- Hand-offs: the four paused ads → `andromeda2-zombie-campaigns` (`a2.py zombie --breakeven-cpa` sorts them into its dud / no_efficiency buckets); budget hold → `andromeda2-scaling`.

## 10. Queue for the next rounds

- Week of 25 Jan: A04 new-avatar pack on the winning UGC template, 3 hooks (actual / ideal / ought self); W1 as a static
  (the stairs frame + its line) to test the angle in another format; W1 iteration with the offer led by the guarantee.
- If W1's 7-14 day CPA goes above $45 and the pausing tree says pause → zombie hand-off; until then it stays on.
- Add the Incremental ROAS column to the next export; re-check W1/W2 before briefing more of them.

---

**Chat summary for the user (what to send alongside the file):** W1 (stairs UGC) wins because a senior-dog owner sees her
own dog's hesitation in the first second and the result is paid off late; it is fatiguing at KPI (hook 34% → 29%,
frequency 3.6), so it stays on and gets three one-layer iterations. The account is 12% over target CPA, so this week is
5 iterations + 3 new concepts (8 ads, calculator count), in three new packs launching Monday 18 Jan, judged Monday 25
Jan. The near-winner hike video has the best hook in the account but leaks at the page, so it gets a matched landing
page rather than a new edit. Four losers pause and go to the zombie queue. Report saved to
`ads/halden-joint-chews/creative-iteration-2027-01-11.md`.
