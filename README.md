# ny-eats

New York State's version of the state restaurant products (models: `../wi-eats/`, `../ct-eats/`, `../chi-eats/`; read-only):

1. **New York Eats**, a free iPhone and iPad app (App Store name "New York Eats: Restaurants", subtitle "Statewide Slice & Bagel
   Guide", home screen "NY Eats"), and its generated website in `docs/` (GitHub Pages; planned newyork.eatsranked.com).
2. **The web leaderboard** of every restaurant in New York State, a private claude.ai Artifact from `site/index.html`
   (https://claude.ai/artifact/JZoCmV1QaebNNDuhf4Snxv). Its JSON is not committed: it carries Google 2021-derived ratings.

| Path | What |
|---|---|
| `pipeline/` | Data: official records (NYC DOHMH, NYSDOH, Suffolk, Buffalo, SLA), Overture listings, Census geography, calibration, the two exports, link check |
| `data/research/` | Hand-checked guides (`app/*.json`), MICHELIN and James Beard honors, verified closures, leads (`app/LEADS_*.md`) |
| `NewYorkEats/` | SwiftUI app (XcodeGen: `project.yml`); region data bundled in `Resources/Data/` |
| `NewYorkEatsTests/`, `NewYorkEatsUITests/` | Unit tests (region files, guides, search, jurisdictions) and the UI smoke tour |
| `scripts/` | `make-leaderboard.py` (private page), `make-brand.swift` (icon, og image), `make-outline.py` (state outline), `make-site.py` + `explore.js` (website and web app), `qa-site.py`, `icon-concepts.swift` |
| `playbook/` | Sources, coverage and calibration (`12-sources.md`), listing (`06`), App Review reply (`13`), icon concepts |

See `CLAUDE.md` for the rebuild commands and rules, and `playbook/12-sources.md` for every source, its terms and how reliable the map
listings proved against New York's official lists.
