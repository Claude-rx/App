# Winner forensics: reading why an ad wins (and why the others lost)

Used in Step 2 of `andromeda2-creative-iteration`. Fill one card per winner, compare with the losers, and turn every
pattern into a test. Everything here is correlation until a test confirms it.

Contents
1. What to dissect
2. The forensics card
3. Grid A: footage patterns
4. Grid B: psychology · Grid C: script
5. The 5-question script audit and the 3 fixes
6. Find the biggest variable
7. Winners vs losers: procedure and agent prompt
8. Why losers lost: the Ad Review Bible
9. Breakout-winner detector (Blueprint prompt, verbatim)
10. Creative reporting breakdowns

---

## 1. What to dissect

**Winner** = top ~10% of the account by spend, at/above KPI, and an incremental KPI above the account's acceptable
baseline (Blueprint). Rank by spend first, confirm the KPI, then confirm on incremental.
Blueprint worked example (KPI $32 cost per purchase, $35 on incremental): ad #1 spent $56k at $38 incremental CPP, taken
"on the volume play"; ad #2 spent $51k at $33 incremental, "a killer"; ad #3 spent $22k, only $0.90 worse than #1 on
standard attribution but $8 worse than #2 incrementally, so rejected. "This is only provable because of incremental
attribution."

**Breakout winner** = launched in the last 30 days, ≥ 10% of account spend, ROAS above the account average in at least
one 7/14/30-day window; right at the average = borderline, include and flag (Blueprint).

**Test classes** (Evolve, spend × CPA; judge the pack first, then the ad):

| Class | What it means | Iteration move |
|---|---|---|
| Winning ad found (great spend, great CPA) | Meta pushes it and it converts | Parent: forensics, then 3-6 one-layer iterations + concepts for its avatar |
| Poor spend, great CPA | Converts the few it reaches; Meta does not see scale | Keep on. Iterate hook/first frame or port to another format to earn spend; may be a bottom-funnel ad doing its job |
| Great spend, poor CPA | Attention without conversion; "something about it got a lot of engagement" | Keep the hook and lead; rebuild the back half: offer, mechanism, CTA, page match ("make it more conversion driven") |
| Poor spend, poor CPA | Meta and buyers both passed | Log the reason (section 8), retire; zombie candidate later |

**Awkward ads** (Blueprint live calls): non-winners with "super strong engagement… really low CPCs, really low CPMs,
really strong comments… that aren't converting" → new bodies, hooks or CTAs.

**Funnel role.** The highest-delivery ad is often the first touch; under last-click-style credit it can look below target
while ads further down the funnel show huge ROAS on small spend (Blueprint live calls). Judge first-touch winners on
spend at KPI and incremental, not on raw ROAS. The agency's highest-delivery ads: 52.8% video, 31.9% image; 55.2%
problem-solution; median video 34 s (8 s-1:45). Top-of-funnel ads "get recycled quicker"; some brands run on 3-4 true
TOF ads plus 12-36 bottom-funnel ads (objection-handling statics).

**Losers for contrast** = the highest-spend ads with ROAS < 1 (Pellegrini) or PAUSE verdicts from `analyze`. Low-spend
losers say little: Meta never showed them enough.

**Data hygiene.** 7-14 day windows (30 and 90 days for patterns); no sale or post-sale days; group variants of one
asset as one creative; ignore ads below a minimum spend (e.g. 2× target CPA).

## 2. The forensics card

```
W<n> · <ad name>
Verdict <…> · spend <$> (<share>) · CPA/ROAS <…> (incremental <…>) · launched <date> · days live <n>
Metrics vs account median: hook <x> (<med>) · hold <x> (<med>) · CTR <x> (<med>) · CPM <x> (<med>)
                           cost/ATC <x> · cost/IC <x> · CVR <x> · 7-day frequency <x>
WHO
  Side (A0X) + moment:        <person, situation, feeling, desire; the moment they are in>
  Template (form factor):     UGC testimonial | founder | demo | us-vs-them static | named-mechanism static | native post |
                              carousel | mashup | short VSL | listicle/advertorial | post-it note | other
  On screen (casting):        <who appears; Andromeda tends to show an ad to people like the person in it>
  Rooms:                      9:16 / 1:1 · works muted? · Reels-native or Feed-native?
WHAT IT SAYS
  Angle (why this person stops now):
  Desire:                     feature or life regained? the scene:
  Mechanism:                  UMP "<named cause>" → UMS "<named fix>" | none
  Awareness / sophistication: <stage> / <1-5 guess>
  Self-concept:               actual | ideal | ought, shown by the line "<…>"
  Zone:                       COZY | JOY | FATIGUE | PANIC; coherence with awareness: green | yellow | red
  Enemy / belief it busts:
HOW IT OPENS (0-3 s)
  Visual:                     <…> (first shot <n> s)
  Spoken:                     "<…>"
  On-screen text:             "<…>"
  Loop opened:                "<…>" → paid off at <n> s (or never)
BODY
  Lead type:                  agitate | myth-bust | story | value | promise
  Pacing:                     shots in first 15 s <n> · longest shot <n> s · motion in every shot? · one shot per line?
  Footage patterns (Grid A):
PROOF                         each claim → its proof; floating ("100% natural") or anchored (number, name, dated timeline)
OFFER + CTA
COPY                          first line of primary text · headline
LANDING PAGE                  same headline/angle/offer as the ad? where is the price shown?
COMMENTS                      recurring questions, objections, phrases (next hooks come from here)
----
WHY IT WINS:     [side] in [moment] sees [hook], believes [mechanism/proof], wants [desire]; tension = [loop] paid at [s]
BIGGEST VARIABLE: format | imagery | message; evidence:
LOCKED DNA:      avatar + template + <biggest variable> (+ anything the comments credit)
FIRST WEAK STAGE (analyze "Fix first"): <stage> → first layer to iterate
```

## 3. Grid A: footage patterns

Pellegrini's seven patterns that recur in long-running winners (the ROAS column is his sample, illustrative only; build
your own from your account):

| Pattern | Where | Why it holds | ROAS in his sample |
|---|---|---|---|
| Hands demo | 0-3 s | the brain follows the action | 2.14 |
| Product / texture close-up | 0-3 s | instant visual proof | 1.98 |
| No face before 15 s | 0-15 s | action beats a talking head | 2.3 |
| Side-by-side comparison | 3-10 s | proof that is hard to argue with | 1.9 |
| POV, subjective camera | 0-10 s | "I see myself doing it" | 1.7 |
| Emotional element | 0-10 s | a child, a deep desire, how others look at you, safety | 2.4 |
| Fast cuts | throughout | a new shot every 1-3 s | 2.5 |

Example read from his account agent: face shot in the hook → low retention; chest-up shot → high; hands demo → maximum.

**Hard-to-contest visual hooks:** a neutral object everyone knows (egg, sauce, scissors); the demo is real; silence for
0-2 s, the visual demo, then the voice reveals; bonus: a reverse scene right after the hook (eggs on three insoles; the
sauce slides off; scissors on the gutter).

**Editor rules** (put them in every brief): never more than 3 s on one shot; motion in every shot; one piece of footage
per line ("if the voice says Marc bends down, show Marc bending down"). System instruction for an AI editor: "Cut every
2-3 s maximum. Motion in every shot. One footage per line. No static moment." Match footage to the emotion of the line:
dark, close and slow for pain; bright and moving for the outcome; never smiling stock footage under a pain line.

Record for every video: first-shot duration and number of shots in the first 15 s.

## 4. Grid B: psychology · Grid C: script

**Grid B (psychology):** angle (dated result, scarcity, life moment, identity, other) · avatar · mechanism (named cause +
named solution, or none) · awareness stage · self-concept (actual / ideal / ought) · Mood × Intensity zone · zone ×
awareness coherence: green / yellow / red (red example: PANIC on a product-aware audience, which needs proof and a deal,
not a shock).

**Grid C (script):** Does the hook surprise and open a loop? Is the desire a feature or the life regained? Is the proof
floating claims or precise numbers, names and timeframes?

## 5. The 5-question script audit and the 3 fixes (Pellegrini)

A typical script that will not scale: HOOK "I finally relieved my back pain." LEAD "Thanks to this new turmeric
supplement… one a day with my coffee. The results are incredible." MECHANISM "Thanks to its anti-inflammatory properties.
100% natural, expert approved." CTA "Try our product today."

| # | Question | That script's answer |
|---|---|---|
| 1 | Who are we talking to? | Nobody: no persona, belief or story, just "you" |
| 2 | Mood × Intensity? | Positive, low = COZY, in a pharma-brochure tone with zero complicity |
| 3 | Which awareness stage? | Unclear: tried four products, or just discovering the problem? |
| 4 | Which self-concept? | Actual self by default ("finally relieved"); never names the self she wants back |
| 5 | How do we prove it? | "Turmeric", "anti-inflammatory": claims 500 brands make; no named mechanism |

Verdict: "a script any brand could sign."
- **Fix 1: desire, not feature.** Not "relieves joint pain" but tying a grandson's laces without wincing, golf all
  weekend, sleeping through the night, two hours of gardening.
- **Fix 2: name the cause, name the solution.** UMP "Joint Drought: the 3 cartilage layers dehydrate" → UMS
  "Triple-Zone Rehydration: rehydrates the 3 layers in 14 days". Link rule: A causes B, so C solves B, obvious in 2 s.
- **Fix 3: anchor the proof.** Numbers (7 days, 2,847 people), names (a named expert, a named study), timeframes
  (visible on day 7, peak on day 30). The bigger the promise, the more specific the proof; every number true and provable.
After the fixes the hook became: "I burst out laughing when my daughter told me 'hydrating my back' would make my chronic
pain go away." (Pellegrini's fictional exercise script: brands and numbers are examples, not real data.)

**The 522-day lesson.** Two videos, same brand, same product, same format; one ran 522 days. Only the tension changed:
a clear, visible result in the first seconds, and a hook that opens a loop you want closed. In the loser, the reveal
disappoints and the promise falls flat. When you dissect a winner, look for the tension before the surface features.

## 6. Find the biggest variable (Denney)

"Determine the thing that is likely having the biggest impact on performance. Is it the imagery or the messaging or the
format?" Use the pack's variations (run at least 3 per test):
- All variations got decent spend and CPA/ROAS → the **format** is working: make more of that format.
- One variation took most of the spend → zoom in. If its imagery is nearly identical to the others, imagery is not the
  variable; the **message** is. Confirm it by testing that message on other statics and in other formats.
- Example (Mott & Bow statistics ad): variables were message (statistics), imagery (the shot) and format (image with a
  statistic). The test as a whole performed → make more statistics images; then carry the statistic message into video
  hooks.
The biggest variable is what the locked DNA protects and what a new concept carries into a new template.

## 7. Winners vs losers: procedure and agent prompt

**Procedure:** pick the winners and losers (section 1) → fill Grids A-C for each (watch them; where you cannot, write
"not verified" and invent nothing) → count each pattern among winners and among losers → keep patterns present in 5+
creatives → table → one test per pattern. With fewer than ~10 creatives per side, present patterns as hypotheses only.

| Pattern | % of winners | % of losers | Spend-weighted ROAS | Hook rate | Hold rate | Test it becomes |
|---|---|---|---|---|---|---|

Also mine the account the way Evolve's creative audit does: top creatives of the last 30 days and last 6 months by spend
and CPA/ROAS, then by hook rate ("which imagery and messaging did the best job at hooking the audience") and by hold and
CTR ("which imagery and messaging retained the user and drove them to take action").

**Agent prompt** (adapted from Pellegrini's Claude prompt; needs read-only access to the Meta account, e.g. the Meta Ads
MCP; otherwise run it on the exported CSV plus the video files you have):

```
You have read-only access to the [BRAND] Meta ad account. Analyse the last 90 days. Ignore ads under [X] spend. Group
variants of one asset as ONE creative.
Winners = the 30 highest-spend creatives with ROAS above [THRESHOLD]. Losers = the 30 highest-spend creatives with ROAS
below 1. For each: spend, ROAS, CPA, age in days, hook rate (3-second plays / impressions), hold rate (ThruPlays /
3-second plays).
For each video: extract one frame per second for the first 15 seconds and transcribe the voice. If you cannot access a
video, write "not verified". Invent nothing.
Grid A, FOOTAGE: hands demo; product/texture close-up; no face in the first 15 s; side-by-side or before/after; POV;
emotional element in the first 10 s (child, deep desire, others' gaze, safety); fast cuts (a new shot every 1-3 s,
motion in every shot); hard-to-contest visual hook (neutral object everyone knows, real demo, no voice before 2 s,
reverse scene right after). Note the first shot's duration and the number of shots in the first 15 s.
Grid B, PSYCHOLOGY: angle (dated result, scarcity, life moment, identity, other); avatar; mechanism (named cause + named
solution, or none); awareness stage; self-concept (actual/ideal/ought); Mood × Intensity zone (COZY/JOY/FATIGUE/PANIC);
zone × awareness coherence green/yellow/red (red example: PANIC on Product Aware).
Grid C, SCRIPT: does the hook surprise and open a loop? Is the desire a feature or the life regained? Is the proof
floating claims or precise numbers, names and timeframes?
Compare the two lists: for each pattern, count and % of winners vs % of losers; keep patterns present in 5+ creatives.
Table: pattern | % winners | % losers | spend-weighted ROAS | hook rate | hold rate. Remind me these are correlations and
propose one test per pattern. End with: the 3 footage patterns to impose on the editor, the 2 most under-exploited
psychological boxes, and the 3 tests to launch this week.
```

## 8. Why losers lost: the Ad Review Bible (Evolve)

Tag every losing test with one or two reasons; the tag tells you which layer the next attempt changes.

| # | Reason | What it looks like | Next attempt changes |
|---|---|---|---|
| 1 | Editing | style too disruptive or wrong for the audience; text too fast or too slow | visual (pacing) |
| 2 | Product focus | no focal point, too much text, unclear what is sold | visual |
| 3 | Benefits | the problem is not a problem for this user; the benefit does not serve their desire; not believable | message |
| 4 | Text length | lines long-winded, not punchy ("always read the text out loud") | message |
| 5 | Visual hook | does not stop the scroll; study the creators your buyers watch | visual (first frame) |
| 6 | Text hook | headline/first line does not intrigue or pull into the rest | message (hook) |
| 7 | Belief | no belief it will work *for this avatar*; objections differ by avatar | mechanism / proof |
| 8 | Identity | people, scenery, aesthetic or words don't match the identity they buy into ("luxury in a trailer park") | visual / avatar |
| 9 | Desire | no desire, or the wrong one ("a Mustang sold as eco-friendly") | message |
| 10 | Awareness | wrong stage; aware-level ads don't scale like problem-aware or unaware ones | message / avatar slice |
| 11 | Mass objection | the main objection ("it's a scam") is never answered | education |
| 12 | Product utility | how it works is unclear: feature, describe or name the mechanism by market familiarity | mechanism |
| 13 | Product value | looks too expensive: compare with a pricier way to get the same desire | offer / education |
| 14 | Exhausted visuals | the market has seen these visuals too long | new visual or new template |
| 15 | Exhausted messaging | you and competitors repeat the same message | new angle → new concept |

Ways to show the product fulfils the desire (Evolve, for #9 fixes): the product in action; day-1 benefits and benefits
over time; show how to test it; real testimonials and authority; compare and prove superiority; show the dream outcome
is easy; a metaphor or analogy.

Example learning that drove a good iteration (Evolve): "The parent is not worried enough in the hook. We need to show
more of what the 'panic feels like'… The ad also introduces the product too salesy and doesn't build suspense or give the
user a reason to keep watching." → iterate the hook's emotion and delay the product reveal.

## 9. Breakout-winner detector (Blueprint prompt, verbatim)

Runs daily on the Meta Ads MCP and hands each breakout winner to SuperScale (a third-party AI ad tool) for iterations:

> Using the Facebook Ads MCP and Superscale MCP, build me a daily "winning ads" detector for the brand [BRAND NAME] and
> schedule it to run every day at 4am.
> WHAT TO DETECT — Pull data from the [BRAND NAME] ad account for the last 7, 14, and 30 days. For each window get the
> account total spend and account average ROAS (level=account), and per-ad spend, purchase_roas, and created_time
> (level=ad, sorted by spend descending). A "clear breakout winner" = an ad that, in at least one window, was: (1)
> launched in the last 30 days, (2) responsible for >=10% of total account spend, and (3) above the account's average
> ROAS for that window. Treat an ad whose ROAS sits right at the average as borderline (still include, flag it).
> SLACK OUTPUT (keep it simple) — Send ONE simple Slack message to [my DM / #channel] — no per-window tables or day-part
> breakdowns. Just a header with the brand + date, then one bullet per breakout winner: ad name, its top spend share,
> ROAS, and a clickable "View ad" link (use a Facebook Ads Manager deep link to the ad id; the ad-preview tool isn't
> enabled on these accounts). If there are no breakout winners, just say "No new breakout winners today."
> SUPERSCALE HANDOFF — For each clear breakout winner, prompt Superscale to iterate on it: look up the brand's product
> list in Superscale, match the winning ad to the most relevant product by name, then create a Superscale chat under the
> [BRAND NAME] brand + that product. In the prompt, give Superscale the ad ACCOUNT name and the exact AD name, tell it
> the spend share / ROAS, and ask it to find that ad, analyze what's working, and build new iterations keeping the
> winning concept and hook while testing fresh hooks/angles/formats. Post a short Slack follow-up with a link to each
> Superscale task created.
> SETUP NOTES — First confirm the brand exists in both places: find the right Facebook ad account, and confirm the brand
> (and a matching product) exist in Superscale — Superscale requires BOTH a brand and a product or it errors. Before
> scheduling, do one live validation run now and show me the result. Ask me up front: which Slack destination, and
> confirm the ad account if there's more than one for this brand.

Without SuperScale, replace the hand-off paragraph with: "For each clear breakout winner, fill the forensics card and
propose 3-6 one-layer iterations and 1-3 new concepts for its avatar, in the creative-iteration brief table."

## 10. Creative reporting breakdowns (Denney)

| Breakdown | Question it answers | Use for iteration |
|---|---|---|
| Format (static / video / carousel) | Which format earns spend at KPI? | where new concepts should go |
| Video format (UGC / explainer / studio) | Which video style to double down on? | template choice |
| UGC creator (name, demographics, location, single vs compilation, aesthetic) | Which creators and looks convert? | casting for visual-layer iterations |
| Hook (top hooks, 30 days) | Which openings stop the scroll? | message/visual hook iterations |
| Hold (top holds, 30 days) | Which editing styles and post-hook messages retain? | lead and pacing iterations |
| Primary copy (top copy, 30 days) | Which texts carry? | copy seeds; a winning headline is a candidate hook |
| Age | e.g. images and long video skew 45+; TikTok-style, Reels and Stories skew 18-35 | new avatars or rooms |
| Placement | Where it shows; a top-six placement near 1% = a creative gap | port winners to the missing room |
| Lifetime top and bottom performers | Which variables are real learnings? | the concept library |

Analysis, not regurgitation (Denney's example): hook rates above average across a whole test → the format works; the
winning message showed users needed education on *what the product is*, not on how it feels → make more educational UGC;
the highest hold came from pacing and jump cuts; compilations won → people need more social proof → add a social-proof
ad. Listing metrics is not analysis; every observation ends in a next ad.
