# HBCU Legacy Web

An interactive mind map of every historically Black college and university that has ever existed (operating, closed and merged) and their notable alumni. It leans toward alumni who made their mark in business: founders, owners, executives, bankers and investors.

**Live:** https://alxndrhq.github.io/hbcu-legacy-mind-map/#/map

It's built in the same style as [Algos & Capital](https://alxndrhq.github.io/historical-wealth-mind-map/#/map), from one static `index.html` with D3 and no build step to view it.

## Views

- **Map**: force-directed network of schools, alumni, companies and founding bodies (AMA, AME Church, UNCF, the 1890 land-grant act…). The layouts are Organic (school regions), Clusters (by archetype), By State, By Tier and By Sector (GICS / sector ETF).
- **Schools**: every HBCU grouped by state, with founding year, status, affiliation and how many alumni are mapped.
- **Alumni**: directory of alumni cards grouped by the stock-market sector of their primary business.
- **Overlaps**: companies, deals and schools that two or more alumni share, plus direct person-to-person ties.
- **Dossiers**: click any node. Alumni get their roots, HBCU years, breakthrough, wealth & legacy strategy, connections and sources. Schools get their history, fate, business alumni, other alumni and lineage.

## Data

`data.json` is generated. Edit the regional files in `sources/` instead, then rebuild:

```sh
python3 tools/build.py          # merge sources/*.json → data.json and embed into index.html
python3 tools/build.py --check  # validate only
```

The build merges duplicate ids, fixes near-miss school ids, drops links to unknown ids and reports what it changed. The record schema is documented at the top of the `<script>` in `index.html`.

Profiles are compiled from public sources, which are linked in each dossier. Net-worth tiers marked "est." are estimates. Items tagged PATTERN are interpretive reads, not documented facts.
