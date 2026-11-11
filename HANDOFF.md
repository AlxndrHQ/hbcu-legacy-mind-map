# HBCU Legacy Web: Handoff

HBCU Legacy Web is an interactive mind map of every historically Black college and university that has ever existed, whether operating, closed or merged, along with their notable alumni. It leans toward alumni who made their mark in business: founders, owners, executives, bankers and investors. It is a public learning and research site. It copies the look of the user's earlier "Algos & Capital" historical wealth mind map.

## Links

- Live site: https://alxndrhq.github.io/hbcu-legacy-mind-map/#/map
- GitHub repo: https://github.com/AlxndrHQ/hbcu-legacy-mind-map (public, branch `main`, served by GitHub Pages)
- Sister project whose style it copies: https://alxndrhq.github.io/historical-wealth-mind-map/#/map (repo AlxndrHQ/historical-wealth-mind-map)

## Current state (as of the last session, 2026-10-11)

The site is live and complete. Local `main` matches `origin/main` at commit `82bc27a`. The only untracked file is `.DS_Store`. Running `python3 tools/build.py --check` on 2026-11-10 reported:

- **1,442 records:** 190 HBCUs (107 operating, 83 closed or merged, across 23 states plus DC and the U.S. Virgin Islands), 32 networks (founding bodies plus the Divine Nine and NPHC), 675 alumni and 545 companies or entities.
- **210 documented Divine Nine memberships.** Alpha Phi Alpha has the most (64). Iota Phi Theta has none, because nobody on its member list is in the dataset.
- **Founding bodies** include the Freedmen's Bureau, the Freedman's Savings Bank (1865 to 1874, with its own dossier), the American Missionary Association, the AME Church, UNCF and the 1890 land-grant act.

These views work. They were tested in headless Chrome in light and dark themes and at phone width.

- **Map (`#/map`):** a force-directed network with five layouts. Organic places school regions roughly by geography. The others group by Clusters (archetype), By State, By Tier and By Sector (GICS / sector ETF). It has filters for school status (operating vs. closed/merged) and Divine Nine (All, Any or one organization), plus a toggle that hides the Divine Nine hubs.
- **Schools (`#/schools`):** every HBCU grouped by state, with its founding year, status, affiliation and mapped-alumni count.
- **Alumni (`#/grid`):** alumni cards grouped by the stock-market sector of each person's main business. Cards show Greek letters for members.
- **Overlaps (`#/overlaps`):** companies, deals, Divine Nine organizations and schools that two or more alumni share, plus direct person-to-person ties.
- **Dossiers (click any node):** alumni dossiers cover roots, "The HBCU Years", breakthrough, wealth and legacy strategy, connections and sources. School dossiers cover history, fate, business alumni, other alumni and lineage, such as Clark College and Atlanta University merging into Clark Atlanta. Organization dossiers list members, business members first.

The `--check` run still prints three known, harmless notices:
- John Thompson (basketball) and John W. Thompson (Symantec) share a name but are different people, so they are kept apart.
- The id `lincoln-university-missouri` is auto-merged into `lincoln-university-of-missouri`.
- `cathy-hughes` has no alumni link, on purpose. She was Howard staff, faculty and WHUR general manager, not a student, so she has only a faculty edge.

## How it's built

- **Stack:** one static `index.html` with D3 v7.9.0 from cdnjs. There is no framework, and no build step is needed just to view it. The data is embedded in the page between `/*DATA-START*/` and `/*DATA-END*/` markers.
- **Hosting:** GitHub Pages serves the root of `main`. To deploy, push to `main`. A hard refresh may be needed afterwards.

Key files:

| File | Purpose |
|---|---|
| `index.html` | The whole app: CSS, HTML shell, JS, the `GICS` sector table and the embedded data (~62k lines). The record schema is documented at the top of its `<script>`. |
| `data.json` | **Generated** merged dataset (1,442 records). Never hand-edit it. |
| `sources/*.json` | Hand-edited source data, one file per region: `al-ms`, `dc`, `georgia`, `north-carolina`, `northeast`, `sc-fl-vi`, `tn-ky-ar-mo-ok`, `tx-la` and `virginia-midwest`. Plus `orgs.json` (founding bodies and the Freedman's Bank) and `divine-nine.json` (D9 and NPHC records, with `member` edges stored on the org records). |
| `tools/build.py` | Merges `sources/*.json`, dedupes by id and by name, fixes near-miss school ids, drops links to unknown ids, validates enums and GICS values, then writes `data.json` and embeds it into `index.html`. Its `ALIASES` table maps duplicate ids to a canonical one. |
| `README.md` | Public description of the views and the data workflow. |

Run and build:

```sh
python3 tools/build.py --check   # validate only, prints problems and counts
python3 tools/build.py           # rebuild data.json and re-embed it in index.html
open index.html                  # or serve the folder with any static server
```

The rules `build.py` enforces:
- **Categories:** Founders & Owners, Corporate Executives, Finance & Investors, Media & Entertainment, Science & Medicine, Public Service, Arts & Athletics.
- **Net-worth tiers:** Undisclosed, $500K-$5M, $5M-$100M, $100M-$500M, $500M-$1B, $1B+.
- **Edge types:** member, alumni, ownership, executive, supply, capital, board, mentorship, civic, family, deal, origin, lineage, faculty, parallel.
- **School status:** Operating, Closed or Merged.
- **Merging:** two people whose birth years differ are never auto-merged. Name matching keeps Jr./Sr./III, because the first build wrongly merged Martin Luther King Sr., Jr. and III.

## Decisions and conventions

- **Same style as the historical wealth mind map.** The user asked to "remake… in the same exact style". The app was built from that site's engine, with an HBCU layer added on top.
- **Emphasize business alumni.** The user asked for alumni "especially… notable in business". Keep that emphasis when adding people. About half of the alumni are in the four business categories.
- **Cover every HBCU that ever existed,** including closed and merged schools such as Bishop College, Storer College, Roger Williams University, Leland College and Florida's 12 Black junior colleges. Predecessors are linked to their successors with `lineage` edges. Bordentown was left out because it was a high school.
- **Sourcing rules.**
  - Every alumni profile needs at least 2 sources, preferably independent ones, and they are linked in the dossier.
  - Candidates with only one source, or only a school's own page, were left out: about 30.
  - Net-worth estimates are labelled "est.".
  - Items tagged PATTERN are interpretive reads, not documented facts.
  - Disputed facts are flagged in the profile itself. For example, Ann Walton Kroenke's Lincoln University (Missouri) link rests on Forbes, Bloomberg and Black Enterprise, while Wikipedia's categories say Columbia College.
- **Divine Nine memberships must be documented,** with the chapter, school and year where a source gives them, or marked "honorary member". Look-alike names were kept separate, such as BET's Robert L. Johnson and Jesse Jackson Jr.
- **Edit `sources/`, never `data.json`,** then rebuild.

## Open items

1. **Thin schools.** These have few or no verifiable alumni: Lane, Langston, UAPB, Shorter, Payne Theological Seminary, Pensole Lewis, St. Philip's, Southwestern Christian, and the Alabama and Mississippi community colleges. Virginia State, Kentucky State and Harris-Stowe were also thin on business alumni at launch. The research agents ran out of their shared web-search budget, so another research pass could fill these in.
2. **About 30 candidates were left out for lack of a second source.** They could be revisited with fresh searches. The rejected names are listed only in the agents' reports from the old chat, not in the repo.
3. **Iota Phi Theta has 0 members on the map.** Adding notable Iota alumni who attended HBCUs would fill it in.
4. **Missing birth years.** Many living business alumni show "living" with no birth year published.
5. **Thin sourcing.** Many shorter profiles still cite Wikipedia plus only one other link.
6. **Dense default map.** About 1,400 nodes crowd the zoomed-out view, so search, filters and zoom are the way in. A less crowded default view could help.
7. **No favicon.** The browser logs one harmless 404 for it.
8. **Question: the operational-challenges explainer.** The user asked why HBCUs like Saint Paul's College closed. The answer covered thin endowments, high Pell share, the 2011 Parent PLUS change, state underfunding of 1890 schools (about $12.8B), accreditation loss, and deferred maintenance and debt. It was given in chat only and is not on the site. Should it become a section or appear in school "fate" dossiers?
9. **Untracked `.DS_Store`.** Consider adding a `.gitignore`.

## Session log

- **2026-10-11 (session `90478a52`, about 16:27 to 18:26 UTC), first build.**
  - The user asked for an HBCU version of the historical wealth mind map, with a new repo and GitHub Pages.
  - Nine regional research agents compiled the schools and alumni.
  - The app was adapted: Schools tab, school dossiers, status filter, By State layout, geographic Organic layout.
  - `tools/build.py` was written.
  - Published at commit `c7674f0` with 190 HBCUs and 541 alumni.
- **2026-10-11 (same session), second pass.** The user asked about the Freedmen's Bureau and the Freedman's Bank, asked for the Divine Nine to be added and asked for a cleanup pass.
  - Added the Divine Nine and NPHC with 210 memberships, plus the Freedman's Savings Bank.
  - Five cleanup agents added 134 alumni (675 total), gave about 110 profiles an independent source and corrected facts (Cummings's MBA, Percy Sutton's station WLIB, Strahan's company founding year, Oprah's net worth).
  - Coppin State went from zero alumni to three.
  - Pushed as commit `82bc27a`.
