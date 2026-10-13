"""Writes playbook/06-app-store-listing.md and playbook/13-app-review-reply.md with every number taken from the app data
(data/app/index.json + places-*.json), and fails if a field breaks Apple's limits (name/subtitle 30, keywords 100, promo 170,
description 4,000, review notes 4,000) or the keywords repeat a word from the name or subtitle.
Usage (from ny-eats/): .venv/bin/python scripts/listing-copy.py   (re-run after every data rebuild, before pasting anything)"""
import os, re, json, glob, collections

ROOT = os.path.join(os.path.dirname(__file__), "..")
ix = json.load(open(f"{ROOT}/data/app/index.json"))
P = [p for f in ix["files"] for p in json.load(open(f"{ROOT}/data/app/{f['file']}"))["places"]]
KIND = {k: 1 << i for i, k in enumerate(ix["kinds"])}
REST = [p for p in P if not p.get("v")]
hc = [p for p in REST if p.get("hc")]
kinds = lambda *ks: [p for p in hc if any(p.get("k", 0) & KIND[k] for k in ks)]
n = {
    "rest": len(REST), "places": len({p.get("c") for p in REST if p.get("c") is not None}),
    "slices": len(kinds("slice", "buffalo pizza", "tomato pie")), "bagels": len(kinds("bagel", "deli", "appetizing")),
    "wings": len(kinds("wings", "beef on weck")), "hots": len(kinds("hots", "plate")), "upstate": len(kinds("riggies", "greens", "half-moon", "spiedie")),
    "dimsum": len(kinds("dim sum")), "hc": len([p for p in hc if p.get("k")]), "icons": len([p for p in REST if p.get("ip") is not None]),
    "nyc_graded": len([p for p in REST if (p.get("nyc") or {}).get("g") in ("A", "B", "C")]),
    "michelin": len([p for p in REST if p.get("mi", 0) >= 2]), "regions": len(ix["regions"]),
}
fmt = lambda k: f"{n[k]:,}"
rt = ix["records_through"]
NAME, SUB, HOME = "New York Eats: Restaurants", "Statewide Slice & Bagel Guide", "NY Eats"
KEYWORDS = "nyc,brooklyn,queens,buffalo,rochester,syracuse,albany,pizza,deli,wings,dim sum,diner,food,grade"
PROMO = (f"Hand-checked slice shops, bagels and delis, Buffalo wings, upstate hots and dim sum, plus {n['rest']:,} New York restaurants "
         f"statewide and NYC's official letter grades.")
DESC = f"""New York's restaurants, from the slice counter to the wing bar, Montauk to Niagara Falls.

New York Eats is a free guide to eating in New York State: slice shops, bagel bakeries and delis, Buffalo wings and beef on weck, upstate hots, Utica riggies and Binghamton spiedies, and dim sum we checked open by hand, plus {fmt('rest')} restaurants, cafés, bars and bakeries across all {n['regions']} regions of the state. No account, no ads.

NEW YORK GUIDES
• Slices & Pizza Styles: New York slice shops, Buffalo pies and Utica tomato pie ({fmt('slices')} places).
• Bagels, Delis & Appetizing: bagel bakeries, Jewish delis and smoked-fish counters ({fmt('bagels')}).
• Wings & Beef on Weck: Buffalo's wing bars and roast beef on kummelweck ({fmt('wings')}).
• Hots & Plates: Rochester white hots, Plattsburgh michigans, Texas hots and Capital Region mini dogs ({fmt('hots')}).
• Utica & Binghamton Classics: chicken riggies, Utica greens, half-moon cookies and spiedies ({fmt('upstate')}).
• Dim Sum: Manhattan's Chinatown, Flushing, Sunset Park and beyond ({fmt('dimsum')}).
• New York Icons: MICHELIN Stars and Bib Gourmands, James Beard honorees and America's Classics.
• Oldest Places: years at the same address, oldest first.

OFFICIAL INSPECTION RECORDS, WITH THEIR DATES
• New York City: the letter grade the Health Department posts at the door (A, B or C), with the date it was graded and the latest inspection ({fmt('nyc_graded')} places).
• Elsewhere in the state: the date of the latest state Health Department inspection and its critical violations. There is no official grade outside New York City, and this app doesn't make one.
• Suffolk County: violations cited in 2025.

FIND IT FAST
• Sort by distance, or browse the map by guide.
• Search by name, neighborhood, town or street: "dim sum flushing", "bagels buffalo", "beef on weck".
• Filter by region, borough, city or cuisine; hide chains.
• Save places for your next trip, and find hand-checked places from iPhone search (Spotlight).

LIVE DETAILS FROM APPLE MAPS
Tap "Ratings, hours & photos" on a place to open Apple Maps' own place card, with current hours, photos, ratings and directions.

HOW THE LISTS ARE BUILT
Every place in the New York guides was checked by hand in October 2026 against a 2025 or 2026 source: its own website or menu, local news, or a tourism listing. The rest of the restaurants come from Overture Maps open data and official lists: the NYC Health Department's restaurant permits, the New York State Department of Health's food service permits, Suffolk County's inspections and the State Liquor Authority's licenses. Map listings are kept only at high confidence, measured against those lists. Website links are checked too. Nothing is ranked by star ratings.

PRIVATE BY DESIGN
No account, no tracking, no ads. Your location, if you share it, only sorts lists on your device. Saved places stay on your device.

Places open and close, and some upstate stands are seasonal, so check before you go. Spot a mistake? Email work-with-nick@gmail.com.

An independent app, not affiliated with any restaurant or chain, the State or City of New York or any of their agencies, Michelin, or the James Beard Foundation. MICHELIN and the MICHELIN Guide are trademarks of Michelin. James Beard Foundation and James Beard Award are trademarks of the James Beard Foundation. Place data from Overture Maps Foundation (CDLA Permissive 2.0) and others; sources and licenses are on the About tab."""

REPLY = f"""Thank you. Here is the information requested. A screen recording from an iPhone running the latest iOS is attached. It starts at launch and shows the full flow.

1. Screen recording: attached. There is no account, login, user-generated content or paid content.

2. Purpose and audience: New York Eats is a free guide to restaurants across New York State. Its focus is the state's food traditions: New York slice shops ({n['slices']} places), bagels and delis ({n['bagels']}), Buffalo wings and beef on weck ({n['wings']}), upstate hot dogs ({n['hots']}), Utica and Binghamton specialties ({n['upstate']}) and dim sum ({n['dimsum']}). Each was checked by hand in October 2026 against a 2025 or 2026 source: the restaurant's own website or menu, local news, or a tourism listing. It also lists {n['rest']:,} restaurants, cafés, bars and bakeries statewide, with New York City's official letter grades. It is for residents and visitors deciding where to eat, with sourced facts and no ads or tracking.

3. How to use it (no login, no setup, no sample files needed):
- Guides tab (Home) → Bagels, Delis & Appetizing (or Slices & Pizza Styles, Wings & Beef on Weck, Hots & Plates, Utica & Binghamton Classics, Dim Sum, New York Icons, Oldest Places, All Restaurants) → tap a place.
- On a place, tap "Ratings, hours & photos" to open Apple Maps' own place card through MapKit. Directions, Call and Website are below it. A New York City place also shows the Health Department's letter grade and its date.
- Search from the Home search box by name, neighborhood, town or street ("dim sum flushing", "beef on weck").
- The Map tab shows each guide as pins. "My location" and the Nearest sort use location only if allowed, on the device.
- The heart saves a place on the device, under the Saved tab. The About tab lists the data sources, licenses and the independence statement.
- On iPad, a sidebar replaces the tabs; a place opens in the right-hand column.
- Location: if you're outside New York (as App Review usually is), the map says so and stays on New York, and distance sorting still works from where you are.
- "NY Eats" is the short Home Screen name of "New York Eats: Restaurants".

4. External services and data:
- Apple MapKit: maps, local search to find a place's Apple Maps listing, and Apple's place card for live hours, photos and ratings.
- Core Location: optional, on-device only, for distance sorting. Core Spotlight: on-device indexing for iPhone search.
- No backend, accounts, analytics, advertising, payments or AI services. The restaurant data is bundled in the app.
- Bundled data: Overture Maps open place data (CDLA Permissive 2.0 / Apache 2.0 / CC0; licenses in the app); public records from the NYC and New York State health departments, Suffolk County, the State Liquor Authority (trade names only) and the City of Buffalo; Census boundaries; MICHELIN and James Beard records (facts only); and our research.
- The website with the privacy policy and support page is static and hosted on GitHub Pages: https://nickstrom5.github.io/new-york-eats/

5. Regional differences: none. The content covers New York State; the app is offered in the United States and works the same everywhere.

6. Regulated or protected material: the app is not in a regulated industry and includes no protected third-party material. The data is open-licensed or public record, with attribution and licenses on the About tab. Ratings, hours and photos appear only in Apple's own place card through MapKit; the app stores no ratings or reviews. Inspection results are shown as their agencies publish them, each with its date: New York City's official letter grades, and elsewhere the state's inspection counts with the Health Department's own disclaimer; the app computes no grade. Every website link was checked before release; adult venues are excluded. The app is independent and not affiliated with any restaurant, government agency, Michelin or the James Beard Foundation.

Support: work-with-nick@gmail.com"""

name_words = set(re.findall(r"[a-z]+", (NAME + " " + SUB).lower()))
kw_words = set(re.findall(r"[a-z]+", KEYWORDS))
checks = {"name": (len(NAME), 30), "subtitle": (len(SUB), 30), "keywords": (len(KEYWORDS), 100), "promo": (len(PROMO), 170),
          "description": (len(DESC), 4000), "review reply": (len(REPLY), 4000)}
for k, (got, lim) in checks.items():
    assert got <= lim, f"{k} is {got} characters (limit {lim})"
assert not (kw_words & name_words), f"keywords repeat the name/subtitle: {kw_words & name_words}"
assert not re.search(r"\b(?:best|top|#1)\b", KEYWORDS + " " + SUB + " " + PROMO, re.I), "no best/top/#1"
assert not re.search(r"\b(?:yankees|mets|bills|giants|jets|knicks|nets|rangers|islanders|sabres|i ❤|i love ny|taste ny)\b", KEYWORDS, re.I)

listing = f"""# App Store listing (ASO): New York Eats

Generated by `scripts/listing-copy.py` from the app data ({ix['generated']} build): every number below is counted from
`data/app/*.json`. **Re-run it after the last rebuild before pasting anything.**

## Name (30 max)
`{NAME}` ({len(NAME)}). Home Screen: `{HOME}`.

## Subtitle (30 max)
`{SUB}` ({len(SUB)})

## Keywords (100 max, commas, no spaces, nothing from the name or subtitle, no trademarks)
`{KEYWORDS}` ({len(KEYWORDS)})

- Borough and city names are the biggest win (Apple combines them with "restaurants" from the name). Rotate after a month of App Store
  Connect search-term data. No restaurant names, no team names, no "I ❤ NY" or "Taste NY" (state marks).

## Promotional text (170 max, editable any time without review)
`{PROMO}` ({len(PROMO)})

## Description ({len(DESC):,} of 4,000)
```
{DESC}
```

## Screenshots (upload one at a time to the 6.9" slot; verify the order after a reload)
| # | File (iPhone 6.9" / iPad 13") | Caption (optional) |
|---|---|---|
| 1 | `home.png` / `ipad-home.png` | {n['rest']:,} New York restaurants |
| 2 | `slices.png` / `ipad-slices.png` | Slice shops, checked open |
| 3 | `detail.png` / `ipad-detail.png` | Live hours & photos from Apple Maps |
| 4 | `bagels.png` / `ipad-bagels.png` | Bagels, delis & appetizing |
| 5 | `map.png` / `ipad-map.png` | The map, by guide |
| 6 | `wings.png` / `ipad-wings.png` | Buffalo wings & beef on weck |
| 7 | `icons.png` / `ipad-icons.png` | MICHELIN & James Beard honorees |
| 8 | `saved.png` / `ipad-saved.png` | Save it for your next trip |

No negative boards and no B or C graded place (or any state inspection count) in any image.

## Category
Primary Food & Drink, secondary Travel. Availability: United States. Price: Free.

## App Store Connect fields
- Version: `1.0.0` (must equal the build's CFBundleShortVersionString; App Store Connect defaults to "1.0"). Bundle ID `com.newyorkeats.ios`.
- Support and Marketing URL: https://nickstrom5.github.io/new-york-eats/ ; Privacy Policy URL (on the App Privacy page):
  https://nickstrom5.github.io/new-york-eats/privacy.html. Switch all three to newyork.eatsranked.com once that CNAME resolves.
- Copyright: `© 2026 Nicholas Soderstrom`. Sign-in required: untick. Contact: Nick's name, email and phone (private to App Review).
- Content rights: Yes, third-party content, with the rights (open data, public records, Apple's place card).
- App Privacy: Data Not Collected. Tracking: No.
- Age rating: Alcohol, Tobacco or Drug Use or References = Infrequent (bars, liquor licenses); everything else None/No → 13+.
- App Review attachment: the screen recording (see 13-app-review-reply.md).

Data dates for the copy: NYC inspections through {rt['nyc']}, state inspections through {rt['nysdoh']}, Suffolk = 2025.
"""
open(f"{ROOT}/playbook/06-app-store-listing.md", "w").write(listing)
review = f"""# App Review: Guideline 2.1 "Information Needed" (prepared before submitting)

Generated by `scripts/listing-copy.py`; numbers from the {ix['generated']} data build. Wisconsin's first submission drew a 2.1 request
for a physical-device screen recording plus six answers (new developer account). Record the screen recording **before** submitting and
upload it in **App Review Information → Attachment**; put the reply below into **App Review Information → Notes** from the start
(only the reply: {len(REPLY):,} of 4,000 characters).

## Screen recording (Nick, on his iPhone, latest iOS)

Install through TestFlight first (internal group; the tester email must be the Apple ID under Settings › your name › Media &
Purchases on the phone, or TestFlight shows "not available"). Record with Control Center → Screen Recording, 60–120 s, no sound:

0. If NY Eats was installed before, delete it and reinstall from TestFlight, so location starts unset.
1. Start on the Home Screen and tap **NY Eats**. The recording must begin with the launch.
2. Home: scroll the guide cards a little.
3. Tap **Bagels, Delis & Appetizing**, then **Katz's Delicatessen** ("Lower East Side, Manhattan").
4. Tap **Ratings, hours & photos**. Apple's place card opens. Close it. Scroll down to the NYC grade and its date.
5. Tap the **heart** (Save), then go back twice.
6. Tap the Home search box and type `dim sum flushing`. Open one result.
7. Tap the **Map** tab, then **Wings**. Tap a numbered circle to zoom in, then a pin, then the ⓘ in its bubble.
8. Tap **Saved**, where the saved place shows. Then **About**, and scroll to the sources.

## Reply text

```
{REPLY}
```
"""
open(f"{ROOT}/playbook/13-app-review-reply.md", "w").write(review)
print(json.dumps(n), "| description", len(DESC), "| reply", len(REPLY), "| promo", len(PROMO), "| keywords", len(KEYWORDS))
