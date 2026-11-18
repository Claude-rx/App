# Andromeda 2 suite — evaluation record

How the nine skills were tested with Anthropic's skill-creator method, and what changed because of it.

## 1. Output quality: with skill vs without (iteration 1, 18 Nov 2026)

One realistic case per skill (`.claude/skills/<skill>/evals/<case>/`), each run twice on the same model (Sonnet 5.5):
once reading the skill, once as a no-skill baseline told not to open it. An independent grader agent scored every
deliverable against the case's assertions, quoting evidence.

| Skill | Case | With skill | Without skill |
|---|---|---|---|
| `andromeda2-core` | audit-and-side-cards-knee-insole | 8/8 (96.9s, 136k tok) | 7/8 (63.2s, 113k tok) |
| `andromeda2-ad-copy` | copy-deck-lymphatic-brush | 8/8 (89.7s, 139k tok) | 8/8 (31.8s, 109k tok) |
| `andromeda2-video-scripts` | ugc-script-sleep-spray | 8/8 (92.4s, 138k tok) | 8/8 (48.6s, 111k tok) |
| `andromeda2-static-ads` | static-batch-protein-cookie | 7/7 (119.6s, 151k tok) | 5/7 (42.1s, 110k tok) |
| `andromeda2-launch-testing` | launch-plan-300-day | 8/8 (67.8s, 131k tok) | 7/8 (60.0s, 113k tok) |
| `andromeda2-scaling` | scale-plan-2k-day | 7/7 (64.2s, 124k tok) | 7/7 (49.1s, 112k tok) |
| `andromeda2-hard-scaling` | cost-cap-diagnosis-60k | 7/7 (89.3s, 133k tok) | 7/7 (50.2s, 112k tok) |
| `andromeda2-zombie-campaigns` | zombie-plan-from-export | 8/8 (42.8s, 121k tok) | 3/8 (43.5s, 111k tok) |
| `andromeda2-creative-iteration` | next-batch-from-export | 6/7 → **7/7 after fix** (iteration 2) | 6/7 (58.3s, 113k tok) |
| **Total** | | **67/68 → 68/68 (98.4% → 100%)** | **59/68 (85.5%)** |

What the numbers hide:
- **Where the baseline failed** is exactly the specialist doctrine: the zombie baseline used a $50 *cost* cap it planned
  to loosen, skipped the ad hogging 94% of its pack and never excluded purchasers; the launch baseline forced 48% of the
  budget through untimed minimums; the static baseline gave no 9:16 safe zones and wrote a second-person GLP-1 callout.
- **Compliance**: three baseline outputs broke their own stated rules with second-person condition callouts (video hook,
  iteration hook, static headline). The skills' compliance passes avoid that pattern.
- **Honesty**: skill outputs leave `[REPLACE]` / `[VERIFY]` placeholders instead of inventing proof; baselines invented
  specifics (a named creator, "best seller").
- **Equal scores ≠ equal work**: in copy, video, scaling and hard-scaling the Sonnet baseline already passes the
  structural checks; the skill runs add research (side card, mechanism), scorecards, computed budgets and stop rules. The
  next round of assertions should test the skill-specific rules (variant tags, budget ÷ 0.8 sizing, ~2.9 words/second).
- **Cost**: ~+41 s and ~+24k tokens per task (~22%) for reading references and running `a2.py`.

**Fix made from the evals** (iteration 2): `andromeda2-creative-iteration` capped the batch at the calculator count, so
the top winner got only one iteration, and it postponed the launch past Black Friday. Now the top winner always gets ≥ 3
of its own iterations (the weekly count is a floor when a clear winner exists) and sale weeks change the judging window,
not the launch. Re-run: 7/7, three iterations of the winner, launch on the normal Monday cadence.

## 2. Triggering (description quality)

`tools/andromeda2/trigger-evals/<skill>.json` holds 6 queries per skill: 3 that should trigger it and 3 near-misses that
belong to a sibling. Run with skill-creator's `run_eval.py` (1 run per query, Sonnet 5.5) in an isolated project, in an
environment with **395 other skills** listed — including generic `ad-copy`, `tiktok-ad-script`, `video-script`,
`facebook-ad-campaign` and persona skills that compete for the same requests.

TRIGGER_RESULTS

## 3. How to re-run

```bash
# structure, links, YAML, eval layout, shared-copy sync + a2.py unit tests
python3 -I tools/andromeda2/check_skills.py
python3 -I -m unittest discover -s tools/andromeda2/tests -v
# output-quality benchmark for one skill, with and without it (Claude Code >= 2.1.269)
claude plugin eval .claude/skills/andromeda2-zombie-campaigns --allow-tools Write,Edit,Bash --scaffold
# trigger check for one skill (from skill-creator's directory)
python -m scripts.run_eval --eval-set tools/andromeda2/trigger-evals/andromeda2-scaling.json \
  --skill-path .claude/skills/andromeda2-scaling --runs-per-query 3
```
