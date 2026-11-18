# Andromeda 2 skill suite

Nine Claude Code skills for Meta (Facebook/Instagram) ads built on the requirements of Meta's next-generation Andromeda
retrieval engine (Engineering at Meta, 28 Oct 2026). Goal metrics: **low CPM, high CTR, high hook and hold rate, low CPC,
low cost per purchase, high ROAS.**

| Skill | What it produces | Ask it… |
|---|---|---|
| `andromeda2-core` | Doctrine, customer research + side cards (avatars), creative and account audits, routing | "Audit our ads against Andromeda 2", "build our avatars" |
| `andromeda2-ad-copy` | Paste-ready primary texts, headlines, descriptions, CTAs | "Write the copy for this winning video" |
| `andromeda2-video-scripts` | Time-coded video scripts (UGC, founder, demo, mini-VSL), hooks, creator + editor briefs | "Write a 45 s UGC script for…" |
| `andromeda2-static-ads` | Static batch briefs across angles and 40 formats, on-image copy, AI image prompts | "Make 6 statics for…" |
| `andromeda2-launch-testing` | Launch structure (prospecting CBO + packs), settings, creative calendar, kill rules | "How do we launch/test these ads?" |
| `andromeda2-scaling` | Twin Engine scaling plan: budget steps + creative engine + monitoring | "Scale us from $2k to $5k a day" |
| `andromeda2-hard-scaling` | $50k+/day: cost caps, ROAS goals, bid caps, value rules, architecture, cadence | "Our cost caps won't spend" |
| `andromeda2-zombie-campaigns` | Bid-capped zombie campaign reviving fatigued and dead ads | "Make our old winners work again" |
| `andromeda2-creative-iteration` | Winner forensics, iteration plan by layer, next batch briefs | "What do we make next from this winner?" |

They live in `.claude/skills/` (project scope) so every Claude Code session in this repo loads them; the packaged
`.skill` files can also be added to a personal profile.

## Layout

```
tools/andromeda2/
  shared/references/   andromeda2-doctrine.md · psychology-toolkit.md · metrics-and-diagnosis.md   (masters)
  shared/scripts/a2.py the calculator/analyzer every skill uses
  sync_shared.py       copies the masters into each skill (skills must be self-contained)
  check_skills.py      validates frontmatter, links, evals and that the copies are in sync
  tests/               unit tests for a2.py + fixture Ads Manager exports
.claude/skills/andromeda2-*/
  SKILL.md · references/ (skill-specific + synced shared copies) · scripts/a2.py (synced) · evals/<case>/
```

**Edit the shared files only in `tools/andromeda2/shared/`, then run `python3 tools/andromeda2/sync_shared.py`.**
CI (`.github/workflows/andromeda2-skills.yml`) fails if a copy drifts.

## a2.py

```bash
python3 tools/andromeda2/shared/scripts/a2.py economics --aov 72 --cogs-pct 30 --shipping 6 --fees-pct 3
python3 tools/andromeda2/shared/scripts/a2.py testing-plan --campaign-budget 300 --target-cpa 38
python3 tools/andromeda2/shared/scripts/a2.py analyze export.csv --target-roas 2.0     # per-ad verdict + weakest funnel stage
python3 tools/andromeda2/shared/scripts/a2.py scale --budget 2000 --kpi-3d 3.3 --kpi-7d 3.1 --kpi-14d 2.9 --target 2.4
python3 tools/andromeda2/shared/scripts/a2.py cost-controls --expected-spend 40000 --target-cpa 48 --monthly-spend 1800000
python3 tools/andromeda2/shared/scripts/a2.py cap-diagnose --cap 48 --actual 46 --budget 10000 --avg-spend 9950
python3 tools/andromeda2/shared/scripts/a2.py zombie lifetime.csv --breakeven-cpa 55 --account-daily-spend 8000
```

`analyze` and `zombie` read Ads Manager CSV exports at ad level (US or EU number formats, `,` `;` or tab separated). Useful
columns: ad set name, ad name, delivery, amount spent, impressions, reach, frequency, link clicks, purchases, purchases
conversion value, adds to cart, checkouts initiated, 3-second video plays, ThruPlays.

## Tests

```bash
python3 -I -m unittest discover -s tools/andromeda2/tests -v
python3 -I tools/andromeda2/check_skills.py
```

Each skill also ships an eval case (`evals/<case>/`: prompt, expected outcome, graders) in the format
`claude plugin eval` reads — run `claude plugin eval .claude/skills/<skill> --allow-tools Write,Edit,Bash` (add `--scaffold`
for cases with input files) to re-benchmark a skill with and without it.

## Sources

Meta Engineering (28 Oct 2026) for the system facts; Spencer Pawliw "Next Gen Andromeda Is Here" (16 Nov 2026); *The Facebook
Ads Blueprint* course and 2026 live calls (M4 structure, packs, scaling, cost controls, zombie campaigns); Matteo Pellegrini,
*Comment scaler Meta Ads grâce et sans l'IA* (2026); Spencer Pawliw's Evolve + Evolve CRO; Dara Denney's Performance Creative
course; Peter Kell's VSL Masterclass and VSL Bible 5.0; Fernando Oliver's Direct Response Ecom Blueprint and swipe files;
Telehealth media-buying bonuses; Foundr Ecommerce Masters 2020 (dated tactics flagged). Numbers are practitioner heuristics —
the account's own baseline wins.
