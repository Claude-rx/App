# SKINOFAB funnels: handoff for Next Commerce

Everything is in this repo (`Claude-rx/App`): the funnel sources, the build, the deploy into the store theme, and the
checks. This page is the map.

## What's live

| Funnel | Page Kit slug | Entry page | Campaign (Campaigns App) |
|---|---|---|---|
| SKINOFAB Adaptive Peptide Foundation | `apf-funnel` | `try.skinofab.com/10-reasons-adaptive-foundation/` | 2221 |
| SKINOFAB Foundation Stick | `stick-funnel` | `try.skinofab.com/10-reasons-foundation-stick/` | 2211 |

Both run Campaign Cart SDK **0.4.43**, with AXON (event key in `_data/campaigns.json`) wired through
`next-forwarder-core.js` + `axon.adapter.js`. GTM / Meta keys are present but empty.

## Where things are

| Path | What |
|---|---|
| `campaigns/skinofab/` | **The funnel project** (Campaign Page Kit 0.3.0). Sources: `src/apf-funnel/`, `src/stick-funnel/`. Config: `_data/campaigns.json`. Specs/briefs: `campaign-spec*.json`, `campaign-build-brief*.json` |
| `campaigns/skinofab/src/*/assets/js/axon.adapter.js` | AXON mapping (dl_* → AXON events), with the SKINOFAB patches: `user_data` on purchase, numeric `item_category_id` |
| `tools/funnel/` | Funnel tooling: `deploy_theme.py` (built site → theme templates), `check_funnel.py` / `apf/check_apf.py` (build gates), `check_live_axon.sh` (live guard) |
| `skinofab-theme/` | Theme 34 as deployed. `assets/sfa/` = APF funnel, `assets/sfc/` = Stick funnel, `templates/pages/page.<page>.html` = one per funnel page. **Generated, never edited by hand** |
| `fixes/axon-purchase-user-data/` | The AXON fix as a standalone file + original (rollback) + unit tests |
| `.claude/skills/` | Next Commerce agent skills (NextCommerceCo/skills + campaigns-os) |

## Build and deploy (how it works today)

```bash
cd campaigns/skinofab && npm ci && npm run build          # → _site/apf-funnel/, _site/stick-funnel/
cd ../.. && python3 -I tools/funnel/check_funnel.py        # Stick gates
python3 -I tools/funnel/apf/check_apf.py                   # APF gates
FUNNEL=apf python3 -I tools/funnel/deploy_theme.py campaigns/skinofab/_site/apf-funnel skinofab-theme
python3 -I tools/funnel/deploy_theme.py campaigns/skinofab/_site/stick-funnel skinofab-theme
cd skinofab-theme && ntk push                               # theme 34 (store skinofab.29next.store)
```

Each built page becomes a standalone theme template (no base layout; the SDK owns the page), served by a store page of
the same slug. Local assets are renamed `assets/sf{a,c}/<name>-<hash6>.<ext>`.

## Moving to standalone hosting (Next Commerce's recommendation)

The Page Kit build is already a static site, so nothing in the funnel needs to change:

1. Deploy `campaigns/skinofab/_site/` to Vercel / Netlify / Cloudflare Pages (build command `npm ci && npm run build`,
   root `campaigns/skinofab`, output `_site`).
2. Point `try.skinofab.com` at the new host. Routes become `/<slug>/<page>/` (e.g. `/apf-funnel/foundation-checkout/`)
   unless the host rewrites `/<page>/` → `/<slug>/<page>/`; keep the old paths working, since ads link to them.
3. Add the domain to **Allowed Domains** for campaigns 2221 and 2211 in the Campaigns App.
4. Keep `axon_event_key` in `_data/campaigns.json`.
5. Retire `tools/funnel/deploy_theme.py` and the funnel templates in theme 34.

## Guard rails

`.github/workflows/funnel.yml` runs on every push: AXON unit tests → Page Kit build → both funnel checks. Daily at
06:17 UTC it also checks that the live pages still load the fixed AXON adapter (`tools/funnel/check_live_axon.sh`).
A failure emails the repo owner.
