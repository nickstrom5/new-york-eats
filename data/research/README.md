# New York research records (hand-checked guides and honors)

Everything here is **facts only**, each with source URLs. No review text, no ratings or stars from anyone, no readers' polls,
no "best of" votes or rankings, no Yelp/TripAdvisor/Google/Facebook as evidence. A place enters a guide only when a **2025 or 2026
source** shows it open: its own current site or menu (with a 2025–26 date, season or event on it), a dated 2025–26 news story, or
a dated 2025–26 official listing (a city/town/county page, a tourism board). Never bypass bot protection: a 403, a 429/503 on repeat,
a bot check, a login wall or Facebook/Instagram-only means the place goes in `app/LEADS_<region>.md`, not in the guide.
Don't fetch any host whose robots.txt disallows ClaudeBot, Claude-User or anthropic-ai (guide.michelin.com does: use Michelin's
press sites, Wikipedia or major press for MICHELIN facts instead). Search-result snippets may point you to a source, but the
source you cite must be one you could read.

## `app/<region>.json`: a JSON array of places

```json
{
  "name": "Katz's Delicatessen",                 // the name on the place's own sign/site (never a legal entity or a person's legal name)
  "address": "205 E Houston St",                 // street address of THIS location
  "city": "New York",                            // the borough for NYC ("Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island");
                                                 // elsewhere the city, village or hamlet people use in the mailing address
  "municipality": null,                          // outside NYC: the town or city government it's in, if different ("Hempstead" for Levittown)
  "neighborhood": "Lower East Side",             // NYC neighborhood or a well-known area ("Flushing", "Sunset Park"), else null
  "county": "New York",                          // county name (Kings, Queens, New York, Bronx, Richmond, Erie, Monroe, ...)
  "zip": "10002",
  "kinds": ["deli"],                   // from the list below; a place can have several
  "dishes": ["pastrami on rye"],                 // signature dishes, plain words, from its own menu or the source
  "seasonal": false,                             // true for places that close for a season
  "season": null,                                // e.g. "May to October" when the source says so
  "founded": null,                               // year it opened AT THIS ADDRESS (not the brand's founding, not before a move); null if unsure
  "founded_note": "Founded 1888 across Ludlow St; moved to this corner later (sources differ on the year)", // how the sources put it; keep claims as the place's claim
  "branch_of": null,                             // for a branch: the original's name and city
  "note": "One line in our own words: what it is and what it's known for. No superlatives we can't source.",
  "website": "https://www.katzsdelicatessen.com/",
  "open": true,
  "evidence_date": "2026-08",                    // month of the newest source showing it open (YYYY-MM, or YYYY if only a year)
  "sources": ["https://...", "https://..."]      // every fact above must be supported by one of these
}
```

`kinds` (use these exact strings):
- `slice` — a New York slice pizzeria: sells pizza by the slice at a counter (classic plain/cheese slice, Sicilian/grandma squares count).
- `buffalo pizza` — Buffalo-style pizza (thick, sweet sauce, cup-and-char pepperoni): Bocce, La Nova, Imperial, Santora's and peers.
- `tomato pie` — Utica/upstate tomato pie (thick Sicilian-style crust, tomato, little or no cheese, often served at room temp) or a
  bakery that sells it by the square (Utica, Rome, Syracuse, Rochester).
- `bagel` — a bagel shop or bakery that makes its own bagels.
- `appetizing` — an appetizing shop (smoked and cured fish, cream cheese, the Jewish "appetizing" tradition): Russ & Daughters, Barney Greengrass…
- `deli` — a Jewish or kosher-style delicatessen (pastrami, corned beef, matzo ball soup). Not an Italian salumeria, not a corner bodega "deli".
- `wings` — a Buffalo wings place of note (Buffalo/Niagara mainly; a few elsewhere only if a source ties them to the tradition).
- `beef on weck` — serves beef on weck (roast beef on kummelweck roll), Buffalo/Western NY.
- `hots` — a regional hot dog place: Rochester white hots and red hots (Zweigle's), Texas hots (Western NY), Plattsburgh michigans,
  Troy/Albany mini hot dogs, Coney Island hots, NYC hot dog institutions (Nathan's Famous Coney Island, Gray's Papaya).
  Put the style in `dishes` ("white hot", "michigan", "Texas hot", "mini hot dogs").
- `plate` — serves a Rochester-style "plate" (a hot or burger over home fries/mac salad with meat hot sauce). "Garbage Plate" is a
  registered trademark of Nick Tahou Hots: use that name only for Nick Tahou's; elsewhere it's a "plate" (or the place's own name for it).
- `riggies` — chicken riggies (Utica area). `greens` — Utica greens. Add both as kinds when both are served.
- `half-moon` — a bakery known for half-moon cookies (Utica/Binghamton; Hemstrought's, Holland Bakery…). NYC "black and white" cookie
  bakeries can also take this kind (put "black and white cookie" in `dishes`).
- `spiedie` — Binghamton/Southern Tier spiedies (Lupo's, Spiedie & Rib Pit, Sharkey's…).
- `dim sum` — a dim sum restaurant (carts or menu): Manhattan Chinatown, Flushing, Sunset Park, Elmhurst, Bensonhurst, and elsewhere.
- `oldest` — serving food or drink since before 1920 **at this address** (verify the year; say "claims" when only the place says it),
  or a colonial-era inn/tavern still serving food.

## `honors.json` and `michelin.json`: honors (statewide)
- James Beard: the same place fields plus `"james_beard": ["Best Chef: New York State winner 2025 (Vijay Kumar)"]` — the exact award,
  year and level (semifinalist / nominee (finalist) / winner). **Never call a finalist or nominee a winner.** America's Classics honorees
  are winners. Include `"chef"` when the honor is a chef award.
- MICHELIN: `{"name", "address", "city", "neighborhood", "county", "zip", "distinction": "3 Stars" | "2 Stars" | "1 Star" |
  "Bib Gourmand" | "Recommended", "edition": "2025", "new": true|false, "sources": [...]}`. Honors are facts: never a row of ★.
  The Green Star was retired worldwide from June 1, 2026; don't show one.
- No polls, "best of" lists, readers' votes, Yelp/TripAdvisor/Google ratings or any star rating.

## `closed_<region>.json`
Places a source shows closed (prefer 2024–26): `{"name", "address", "city", "county", "closed_reason", "closed_date", "sources"}`.

## `app/LEADS_<region>.md`
Places that probably belong in a guide but couldn't be verified (Facebook-only, stale site, blocked, undated menu), grouped by
kind, each with the reason and what would settle it.
