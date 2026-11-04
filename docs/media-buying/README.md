# Media buying: Meta ads system

The team's Meta ads operating system, built from *The Facebook Ads Blueprint* course (all 75 lesson files + 17 live-call transcripts).

| File | What it is |
|---|---|
| [SOP.md](SOP.md) | **The rulebook.** Economics, account setup, M4 structure, creative system, testing, optimization, scaling, lead gen, checklists, and a decisions log for every conflict between lessons. |
| [sources.md](sources.md) | Every course file used, linked to the Drive folder, by module. |
| [`tools/fb-blueprint/`](../../tools/fb-blueprint/) | Decision engine: `rules.py` (every threshold, cited), `engine.py` (25 decision functions), `blueprint.py` (CLI), `test_engine.py` (45 tests built on the course's worked examples). |
| [`.claude/skills/fb-*`](../../.claude/skills/) | Claude skills that run the SOP through the Meta Ads MCP: **fb-launch**, **fb-test**, **fb-optimize**, **fb-scale**. |

## Use it

Ask Claude in plain language inside this repo, for example:
- "Launch this week's 6 creatives for account 123: avatar busy moms, concept us-vs-them" → **fb-launch**
- "Which ads should I pause? Find this week's winners." → **fb-test**
- "Daily check" / "ROAS dropped 30% since Tuesday, why?" → **fb-optimize**
- "We're above target, can I scale?" → **fb-scale**

The skills **read freely and never change spend without your explicit yes**. Creates are staged as Ads Manager drafts and published only after approval.

## Change a rule

1. Edit the value in `tools/fb-blueprint/rules.py`, or put team overrides in `tools/fb-blueprint/rules.local.json` (same nesting; deep-merged).
2. Update the matching SOP section and the **§13 Decisions log**.
3. Run the tests: `python3 -m unittest discover -s tools/fb-blueprint -v`

## Engine quick reference

```bash
python3 tools/fb-blueprint/blueprint.py list          # all commands + signatures
python3 tools/fb-blueprint/blueprint.py rules         # effective thresholds
echo '{"monthly_spend": 45000}' | python3 tools/fb-blueprint/blueprint.py ads_per_week
```
