# New York sources, coverage and calibration (checked 2026-10-07)

All figures re-verified on 2026-10-07 against the live sources (the state prompt's late-September research was the starting point).

## Official sources

| Source | What we use | Terms | Cadence (rows updated) | Notes |
|---|---|---|---|---|
| NYC DOHMH "New York City Restaurant Inspection Results", data.cityofnewyork.us `43nn-pn8j` | One row per CAMIS (permit): trade name (DBA), address, borough, zip, phone, DOHMH cuisine, coordinates, NTA, BBL; the **posted letter grade and its date** (official), the latest inspection, its score and critical citations, pests cited (04K rats, 04L mice, 04M roaches), DOHMH closures and re-openings | NYC Open Data Terms of Use (free reuse; no warranty) | Daily (2026-10-06) | 296,270 violation rows, 31,469 CAMIS (31,425 after the 7-day cut). 3,858 permits never inspected (1900-01-01) are not added on their own. Grades on file: A 21,789, B 1,848, C 552, Z 1,190, N 6, P 3; 6,037 have none. Verified: 2025–26 rows have C at score 0 and B from 7 to 34, so **grades are never derived from scores**. 08A ("conditions conducive to" pests) is not pest evidence and is never counted. Link ABCEats for history; never scrape it. |
| NYSDOH "Food Service Establishment: Last Inspection", health.data.ny.gov `cnih-y5dw` | Restaurant-type facilities (Restaurant, Food Service Establishment, Restaurant/Catering, Tavern, Delicatessen, Bakery, Frozen Desserts, Ice Cream): name, address, city, municipality, county, coordinates, latest inspection date, critical / not-corrected / non-critical counts | OPEN-NY Terms of Use (permissive, no attribution required) **plus the dataset's own notes**: "Researchers agree to: Use the data for statistical reporting and analysis only" and to state that "any analyses, interpretations or conclusions were reached by the author and not the NYSDOH" | Posted monthly (2026-10-01; latest inspection 2026-09-25) | 21,615 facilities; 16,869 restaurant-type kept (schools, day care, camps, colleges, SOFA and SED sites dropped). **Excludes NYC, Suffolk and Erie.** No grade exists; the dataset says grading built on it "is not supported or endorsed by the New York State Department of Health" (quoted verbatim wherever counts appear). `perm_operator_*` and `permitted_corp_name` are never downloaded. 14A "Insects, rodents present" is coded *not critical*. |
| NYSDOH inspections history (ACTIVE) `2hcc-shji`, (INACTIVE) `aaxz-j6pj` | Up to six earlier inspections per facility since 2023 (date, counts); inactive facilities since 2023 (closures) | Same | Monthly | 451,299 violation rows since 2023-01-01; 10,529 inactive facilities. |
| Suffolk County "Restaurant Violations: 2025", opendata.suffolkcountyny.gov (ArcGIS item `a3663c06871e422b9ba6f972bb54a332`) | Violations cited in 2025 per facility (count, inspections with a citation, latest date), name, address, point | County open data portal (no license stated; public records) | Yearly (published 2026-01-21) | 52,277 rows, 3,941 facilities. No score, no grade, no 2026; a clean inspection isn't on the list. Shown as "violations cited in 2025", never ranked. |
| City of Buffalo "Restaurant Licenses", data.buffalony.gov `4pp3-qkuj` | Active licenses: DBA, address, type (Restaurant, Restaurant / Dance, Take Out), coordinates | Public Domain U.S. Government | Weekly (2026-10-02) | 1,440 active. `businessname` (legal name) never downloaded. Erie County inspections are on HealthSpace (search only, 403 to our fetch): not collected. |
| NYS Liquor Authority "Current Liquor Authority Active Licenses", data.ny.gov `9s3h-dpkz` | On-premises licenses (Restaurant, Food & Beverage Business, Hotel, Club, Cabaret, Restaurant Brewer, summer/winter variants, caterers, makers): DBA, class, address, original issue date, point | OPEN-NY | Daily (2026-10-07) | 59,907 active (17,226 restaurant-class kept as "restaurant"). 18,258 records have no DBA: they confirm nothing by name and are never shown. `legalname` never downloaded. |
| SLA "Current SLA Inactive Licenses" `6dg3-2z7i` | Expired/ended since 2023 (closure signal) | OPEN-NY | Daily | 22,432 rows. |
| Ag & Markets food safety ratings `d6dy-3h7r`, retail food stores `9a8c-vfzj` | Downloaded to flag grocery counters only; nothing shown | OPEN-NY | Quarterly / annually | `owner_name`, `entity_name` never downloaded. |
| BLS QCEW 2025 annual, NAICS 722, private (data.bls.gov/cew) | Restaurants and bars per county, for calibration | Public domain | Annual | 50,666 statewide; 24,208 in NYC; Nassau 3,756, Westchester 2,440, Suffolk 3,715, Erie 2,094. |
| U.S. Census cartographic boundary files 2025 (counties, county subdivisions) | 62 counties, 933 towns, 61 cities, 5 boroughs | Public domain | 2025 | Regions = the ten Regional Economic Development Council regions (Empire State Development). |
| NYC DCP 2020 Neighborhood Tabulation Areas (NYC Open Data `9nt8-h7nd`) | 262 neighborhoods for NYC places (searchable alias) | NYC Open Data | 2020 | Matches DOHMH's `nta`. |

Nassau's own food service lookup (app.nassaucountyny.gov/doh/fsei) and Westchester's are search-only views of the same NYSDOH data:
not scraped.

### Records-through dates (publication lag)
Derived from each feed's own refresh date minus 7 days (`pipeline/official.py: records_through`), never hard-coded:
NYC through 2026-09-29, NYSDOH through 2026-09-24 (posted monthly), Suffolk = calendar 2025.

## Map listings (Overture Maps 2026-09-23.1)

1,054,125 places addressed to New York; **107,043 eating/drinking listings** (Meta 57,922, BrightQuery 20,533, Foursquare 19,829,
Microsoft 7,906, AllThePlaces 713, DAC 139). By region: NYC 53,268, Long Island 14,654, Mid-Hudson 11,606, Western NY 6,453,
Capital 5,489, Finger Lakes 5,287, Central NY 3,434, Southern Tier 2,716, Mohawk Valley 2,157, North Country 1,956.
2,507 are marked permanently closed by Overture. Google 2021 snapshot (UCSD, web leaderboard only): 69,681 food listings.

## Calibration and coverage

### Calibration: share of each kind of listing that matched an official list

Web grouping (the leaderboard's keep rule):

| Kind of listing | NYC (DOHMH permits) | NYSDOH counties (all) | Buffalo (licenses, address-matched) | Suffolk (2025 violations) | SLA on-premises (statewide) |
|---|---:|---:|---:|---:|---:|
| Meta + open in Google 2021 | 83% of 12,867 | 50% of 13,642 | 46% of 415 | 65% of 2,505 | 34% of 30,454 |
| Meta only | 48% of 12,022 | 19% of 11,695 | 19% of 465 | 35% of 1,817 | 19% of 26,725 |
| brand feed + Google 2021 | 83% of 48 | 59% of 64 | 0% of 1 | 50% of 10 | 27% of 134 |
| brand feed only | 70% of 249 | 17% of 356 | 50% of 4 | 23% of 70 | 5% of 713 |
| Foursquare/BrightQuery/Microsoft + Google 2021 | 26% of 8,147 | 13% of 4,594 | 18% of 176 | 29% of 897 | 7% of 14,128 |
| Foursquare only | 13% of 6,499 | 4% of 3,997 | 8% of 165 | 7% of 726 | 4% of 11,625 |
| BrightQuery only | 15% of 6,669 | 7% of 3,593 | 7% of 129 | 12% of 745 | 4% of 11,410 |
| Microsoft only | 35% of 1,977 | 7% of 1,496 | 12% of 43 | 28% of 310 | 6% of 3,934 |
| Google 2021 says closed | 3% of 3,135 | 2% of 1,597 | 7% of 60 | 4% of 223 | 2% of 5,141 |
| Overture says closed | 5% of 1,364 | 3% of 771 | 11% of 28 | 6% of 133 | 3% of 2,347 |

App grouping (no Google data; Overture confidence):

| Kind of listing | NYC (DOHMH permits) | NYSDOH counties (all) | NYSDOH, 37 complete counties | Buffalo (licenses, address-matched) | Suffolk (2025 violations) | SLA on-premises (statewide) |
|---|---:|---:|---:|---:|---:|---:|
| Meta, confidence 0.95+ | 82% of 17,574 | 46% of 15,832 | 64% of 6,794 | 43% of 565 | 64% of 2,944 | 35% of 38,070 |
| Meta, 0.90-0.95 | 35% of 2,653 | 30% of 4,895 | 39% of 2,667 | 18% of 141 | 40% of 736 | 16% of 8,731 |
| Meta, below 0.90 | 23% of 4,877 | 9% of 4,786 | 14% of 2,350 | 7% of 177 | 13% of 684 | 7% of 10,828 |
| brand feed | 72% of 297 | 23% of 420 | 33% of 207 | 40% of 5 | 26% of 80 | 8% of 847 |
| BrightQuery 0.95+ | 29% of 5,753 | 13% of 3,238 | 19% of 1,155 | 14% of 120 | 24% of 703 | 8% of 10,060 |
| other sources | 15% of 20,372 | 6% of 11,811 | 8% of 4,855 | 10% of 445 | 15% of 2,152 | 4% of 35,579 |
| Overture says closed | 5% of 1,451 | 3% of 823 | 4% of 349 | 9% of 33 | 6% of 137 | 3% of 2,496 |

Coverage the other way (official businesses found among the map listings; the rest are added from the lists, except Buffalo's and nameless SLA records, which never add places):

- NYC DOHMH permits: 66% of 30,108
- NYSDOH restaurant-type facilities: 63% of 15,583
- Suffolk 2025 facilities: 67% of 3,860
- Buffalo licenses: 24% of 1,421
- SLA on-premises licensees: 65% of 25,383

### Coverage by county (BLS QCEW 2025 restaurants and bars vs each county's official list)

| County | Region | QCEW 722 | Inspection list | On it | List ÷ QCEW | SLA on-premises | Map listings | Meta ≥0.95 on NYSDOH list |
|---|---|---:|---|---:|---:|---:|---:|---:|
| New York | New York City | 9,694 | NYC DOHMH | 11,937 | 1.23 | 2,063 | 23,169 | — |
| Kings | New York City | 6,121 | NYC DOHMH | 7,770 | 1.27 | 1,203 | 13,196 | — |
| Queens | New York City | 5,716 | NYC DOHMH | 6,692 | 1.17 | 1,354 | 10,423 | — |
| Nassau | Long Island | 3,756 | NYSDOH | 1,014 | 0.27 | 1,364 | 7,178 | 26% |
| Suffolk | Long Island | 3,715 | Suffolk 2025 violations | 3,860 | 1.04 | 1,068 | 7,436 | — |
| Westchester | Mid-Hudson | 2,440 | NYSDOH | 887 | 0.36 | 1,085 | 4,849 | 26% |
| Erie | Western New York | 2,094 | none (HealthSpace search only) | 0 | — | 1,077 | 4,393 | — |
| Bronx | New York City | 1,789 | NYC DOHMH | 2,537 | 1.42 | 320 | 4,213 | — |
| Monroe | Finger Lakes | 1,546 | NYSDOH | 1,909 | 1.23 | 259 | 3,363 | 85% |
| Onondaga | Central New York | 965 | NYSDOH | 1,594 | 1.65 | 213 | 2,166 | 83% |
| Orange | Mid-Hudson | 901 | NYSDOH | 690 | 0.77 | 325 | 1,881 | 48% |
| Richmond | New York City | 888 | NYC DOHMH | 1,081 | 1.22 | 162 | 1,976 | — |
| Albany | Capital Region | 806 | NYSDOH | 374 | 0.46 | 308 | 1,772 | 22% |
| Rockland | Mid-Hudson | 787 | NYSDOH | 683 | 0.87 | 233 | 1,476 | 53% |
| Dutchess | Mid-Hudson | 754 | NYSDOH | 272 | 0.36 | 368 | 1,563 | 23% |
| Saratoga | Capital Region | 503 | NYSDOH | 386 | 0.77 | 198 | 1,013 | 51% |
| Oneida | Mohawk Valley | 481 | NYSDOH | 527 | 1.1 | 144 | 1,065 | 56% |
| Ulster | Mid-Hudson | 474 | NYSDOH | 381 | 0.8 | 264 | 990 | 44% |
| Niagara | Western New York | 444 | NYSDOH | 726 | 1.64 | 97 | 945 | 82% |
| Broome | Southern Tier | 418 | NYSDOH | 443 | 1.06 | 124 | 818 | 63% |
| Schenectady | Capital Region | 321 | NYSDOH | 213 | 0.66 | 107 | 631 | 51% |
| Rensselaer | Capital Region | 304 | NYSDOH | 218 | 0.72 | 100 | 634 | 48% |
| Chautauqua | Western New York | 276 | NYSDOH | 339 | 1.23 | 110 | 607 | 65% |
| Ontario | Finger Lakes | 260 | NYSDOH | 217 | 0.83 | 120 | 607 | 44% |
| Jefferson | North Country | 259 | NYSDOH | 236 | 0.91 | 101 | 587 | 51% |
| Tompkins | Southern Tier | 230 | NYSDOH | 183 | 0.8 | 86 | 526 | 50% |
| Oswego | Central New York | 225 | NYSDOH | 162 | 0.72 | 101 | 438 | 38% |
| Warren | Capital Region | 223 | NYSDOH | 247 | 1.11 | 128 | 563 | 50% |
| Putnam | Mid-Hudson | 216 | NYSDOH | 184 | 0.85 | 99 | 411 | 49% |
| St. Lawrence | North Country | 182 | NYSDOH | 178 | 0.98 | 70 | 386 | 51% |
| Steuben | Southern Tier | 182 | NYSDOH | 176 | 0.97 | 59 | 346 | 50% |
| Sullivan | Mid-Hudson | 181 | NYSDOH | 215 | 1.19 | 110 | 414 | 40% |
| Chemung | Southern Tier | 176 | NYSDOH | 187 | 1.06 | 46 | 352 | 57% |
| Columbia | Capital Region | 164 | NYSDOH | 124 | 0.76 | 101 | 318 | 34% |
| Cattaraugus | Western New York | 158 | NYSDOH | 267 | 1.69 | 59 | 335 | 70% |
| Clinton | North Country | 150 | NYSDOH | 116 | 0.77 | 60 | 304 | 41% |
| Otsego | Mohawk Valley | 142 | NYSDOH | 135 | 0.95 | 70 | 318 | 37% |
| Madison | Central New York | 137 | NYSDOH | 209 | 1.53 | 36 | 353 | 76% |
| Cayuga | Central New York | 133 | NYSDOH | 147 | 1.11 | 55 | 270 | 64% |
| Wayne | Finger Lakes | 133 | NYSDOH | 119 | 0.89 | 49 | 297 | 45% |
| Greene | Capital Region | 129 | NYSDOH | 131 | 1.02 | 122 | 325 | 29% |
| Herkimer | Mohawk Valley | 123 | NYSDOH | 139 | 1.13 | 56 | 247 | 48% |
| Essex | North Country | 119 | NYSDOH | 145 | 1.22 | 100 | 291 | 44% |
| Livingston | Finger Lakes | 115 | NYSDOH | 130 | 1.13 | 53 | 243 | 53% |
| Cortland | Central New York | 111 | NYSDOH | 109 | 0.98 | 35 | 202 | 46% |
| Genesee | Finger Lakes | 106 | NYSDOH | 126 | 1.19 | 36 | 260 | 57% |
| Delaware | Southern Tier | 102 | NYSDOH | 84 | 0.82 | 70 | 224 | 42% |
| Franklin | North Country | 91 | NYSDOH | 70 | 0.77 | 41 | 228 | 40% |
| Montgomery | Mohawk Valley | 90 | NYSDOH | 82 | 0.91 | 32 | 202 | 40% |
| Chenango | Southern Tier | 89 | NYSDOH | 72 | 0.81 | 35 | 162 | 41% |
| Fulton | Mohawk Valley | 87 | NYSDOH | 111 | 1.28 | 39 | 212 | 52% |
| Allegany | Western New York | 77 | NYSDOH | 72 | 0.94 | 31 | 160 | 44% |
| Washington | Capital Region | 75 | NYSDOH | 77 | 1.03 | 42 | 215 | 49% |
| Tioga | Southern Tier | 72 | NYSDOH | 65 | 0.9 | 27 | 156 | 35% |
| Schoharie | Mohawk Valley | 62 | NYSDOH | 41 | 0.66 | 25 | 110 | 42% |
| Seneca | Finger Lakes | 57 | NYSDOH | 78 | 1.37 | 32 | 166 | 36% |
| Orleans | Finger Lakes | 55 | NYSDOH | 54 | 0.98 | 20 | 113 | 40% |
| Schuyler | Southern Tier | 54 | NYSDOH | 57 | 1.06 | 34 | 130 | 42% |
| Wyoming | Finger Lakes | 54 | NYSDOH | 57 | 1.06 | 28 | 115 | 38% |
| Lewis | North Country | 51 | NYSDOH | 55 | 1.08 | 38 | 95 | 42% |
| Yates | Finger Lakes | 51 | NYSDOH | 44 | 0.86 | 23 | 114 | 40% |
| Hamilton | North Country | 26 | NYSDOH | 26 | 1.0 | 25 | 59 | 29% |

Reading the table:
- NYC's DOHMH list is complete (more permits than QCEW establishments: QCEW counts employers, DOHMH every permit, carts excluded).
- The NYSDOH list is near-complete (≥85% of QCEW) in 37 counties. It is far short in **Nassau (0.27)**, **Westchester (0.36)**, **Dutchess (0.36)** and **Albany (0.46)**: those counties inspect on their own systems and only part of their results reach the state's open data. Listings there lean on the map data and SLA licenses.
- Erie has no bulk inspection data at all (HealthSpace is search-only and refuses our fetch).
- App keep rule (`newyork.py`, NY_APP=1): on an official list, hand-checked, a chain's own store feed, or Meta with Overture confidence
  ≥0.95. Meta ≥0.95 matched an official list 82% of the time in NYC and 64% in the 37 complete NYSDOH counties (Monroe 85%, Onondaga 83%,
  Niagara 82%); Meta 0.90–0.95 matched only 35% / 39%, so it ships only when a list or our research confirms it (stricter than
  Connecticut, where 0.90–0.95 was kept as "listing only"). The web leaderboard keeps Meta listings at any confidence, labeled.

## Honors (data/research/michelin.json, jbf.json, honors_notes.md)
- **MICHELIN Guide New York, 2025 selection** (ceremony Nov 18, 2025; the 2026 ceremony is set for Dec 14, 2026 in New York):
  5 three-star, 15 two-star (including Blue Hill at Stone Barns, Pocantico Hills), 52 one-star, 88 Bib Gourmands confirmed
  (Michelin reported 90; Atla and Bayon closed since, so 86 shown). Every selection is in NYC or Westchester; none upstate or on
  Long Island. Recommended places aren't shown: no complete list on a source we may read (guide.michelin.com's robots.txt disallows
  ClaudeBot, so it was never fetched). The Green Star was retired worldwide on June 1, 2026.
- **James Beard 2023–2026**, New York State: 174 lines over 150 places (winners, nominees, semifinalists exactly as named; never a
  finalist called a winner), plus all 18 America's Classics honorees in the state since 1998. Best Chef: New York State 2025 Vijay
  Kumar (Semma), 2026 Hooni Kim (Meju, Queens); Best New Restaurant 2026 Lei; America's Classics 2026 Eng's (Kingston). Honorees with
  no 2025–26 evidence of being open only annotate a listing that exists; they are never added on their own.

## Hand-checked guides (data/research/app/*.json; 228 places, each with a 2025–26 source)
Five regional agents, 2026-10-07: Manhattan 55, Brooklyn/Queens/Bronx/Staten Island 35, Western NY 38, Central NY/Southern Tier/North
Country 38, Long Island/Hudson Valley/Capital 38. Closures with sources in `data/research/closed_*.json`; leads that couldn't be
verified in `app/LEADS_*.md`. About 128 of the ~200 web searches were used.

2026-10-08: James Beard open-status check (26 open, 13 closed incl. Cadence; `closed_honors.json`), a gaps pass (`app/gaps.json`:
30 places, mostly bagels, Rochester hots and plates, upstate dim sum, Staten Island; 15 searches) and a re-sourcing pass (16
searches); about 172 searches in all. Files now: central_north 35, gaps 29, li_hudson_capital 38, manhattan 55, outer_boroughs 35, western 36.

### Source audit (2026-10-08, `pipeline/check_sources.py`)
Every host the research cites is checked against its robots.txt (ClaudeBot, Claude-User, anthropic-ai) and for bot checks. The first
pass found 11 hosts the first research wave had used that block us: visitbuffalo.com (Cloudflare "Just a moment"), nysenate.gov
(bot check), romesentinel.com, theinfatuation.com, spectrumlocalnews.com, cnycentral.com, thisiscny.com, wcax.com, wktv.com,
bupipedream.com and oysterbarny.com (robots.txt disallows ClaudeBot), plus nassaucountytourism.com pages (JavaScript crawler check).
Their URLs were removed; 64 guide records were flagged and re-sourced from usable hosts and official records (City of Buffalo and state
liquor licenses for Erie County, NYSDOH 2hcc-shji, DOHMH, Ag & Markets, own sites, dated news): 58 kept, 6 moved to leads
(`data/research/removed_sources.json`). Newly failing hosts found while re-sourcing: barbill.com, tavolo315.com, manhassetbagels.com
(bot checks), toasttab.com/local, roadfood.com (403), gingerbreadbakeshop.com, longislandpress.com, buffalospree.com, wivb.com,
robertsietsema.substack.com (robots.txt). Stage 2 drops any source on a blocked host and skips records flagged `recheck`; the audit
must report 0 unusable before a release (2026-10-08: 655 URLs on 216 hosts, 0 unusable).

### Placement QA (2026-10-08)
New York repeats street addresses across boroughs and towns (1501 Broadway is in Midtown and Bushwick; 239 5th Ave in Park Slope
and Midtown). Three guards came out of the QA sweep that found 27 same-name, same-address pairs in two places:
- official matching counts "the same address" only within 1 km, or in the same ZIP code when a record has no coordinates
  (`listings_util.SAME_ADDR_M`); the curated matcher needs the record's own town or ZIP;
- a map listing without an official record is dropped when it's beyond its ZIP code's spread of official records and either the
  ZIP belongs to another county or it's 15+ km away (~360 listings: Shining Rainbow's Albany address geocoded into Brooklyn, a Geneva
  ZIP in Saratoga County);
- an NYC listing without a DOHMH permit whose name and address carry a DOHMH permit in another borough (and none in its own) is a
  geocode onto the other Broadway/Bedford/5th Ave and is dropped (Taco Bell, Bagelsmith, Nora Thai, Egg Shop).
