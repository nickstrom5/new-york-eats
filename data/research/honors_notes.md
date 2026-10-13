# New York honors research notes (checked 2026-10-07)

Files: `michelin.json` (MICHELIN Guide New York, 2025 edition) and `jbf.json` (James Beard Awards, New York State, 2023-2026, plus all
America's Classics). Honors are facts ("1 MICHELIN Star", "Best Chef: New York State winner 2025"), never star ratings.

## How the data was gathered

**MICHELIN**
- We did not fetch guide.michelin.com, because its robots.txt disallows ClaudeBot. Every MICHELIN fact comes from Michelin's press
  site (michelinmedia.com, allowed), Wikipedia, or major press.
- **Edition.** The current New York selection is the 2025 Northeast Cities edition. Michelin's release
  ([a1442](https://michelinmedia.com/pages/blog/detail/article/c0/a1442/)) is dated **Nov 18, 2025**: the ceremony was that evening at
  the Kimmel Center in Philadelphia. Time Out and Fine Dining Lovers reported it on Nov 19.
- **No 2026 selection yet.** Michelin has scheduled the 2026 Northeast Cities ceremony for **Dec 14, 2026** at The Glasshouse, New York
  ([a1479](https://michelinmedia.com/pages/blog/detail/article/c0/a1479/)). As of 2026-10-07, no 2026 New York selection exists.
- **Stars.** The release publishes the full starred list as images, with addresses. We read every image and kept the New York
  addresses: **5 three-star, 15 two-star and 52 one-star**. The list matches the 2025 column of Wikipedia's
  "List of Michelin-starred restaurants in New York City".
- **Bib Gourmands, step 1: the 2024 base list.** The 2025 release lists only the 9 *new* NY Bibs. We started from Michelin's official
  2024 NY Bib list, which has 91 restaurants with addresses (Dec 9, 2024 release,
  [a1383](https://michelinmedia.com/pages/blog/detail/article/c0/a1383/), images).
- **Bib Gourmands, step 2: which 2024 Bibs kept their Bib.** We used the 2025 column of Wikipedia's "List of Michelin Bib Gourmand
  restaurants in the United States" (New York table). It shows 8 of the 2024 Bibs gone in 2025:
  - Dropped: Ammazzacaffè, Chick Chick, Enoteca Maria, Falansai, Saint Julivert Fisherie and Tredici Social.
  - Closed: Cecily and Ugly Baby.
  - Chick Chick's drop is also confirmed by West Side Rag (Dec 1, 2025).
- **Bib Gourmands, step 3: the total.** 91 − 8 + 9 new = **88**, the same as Wikipedia's 2025 count.
- **Westchester Bibs that Wikipedia does not track.** Wikipedia's table has no rows for four Westchester 2024 Bibs: Badageoni Georgian
  Kitchen, RaaSa, Rafele Rye and TVB by Pax Romana. They are in `bib_unconfirmed_2025` and not in `restaurants`.
- **Bibs closed since the edition.** Two 2025 Bibs have since closed and are in `closed_since`:
  - Atla: final service May 31, 2026.
  - Bayon: final service Aug 3, 2026.
- **Neighborhoods.** These come from the two Wikipedia tables. Where Wikipedia gave only "Midtown" or got the area wrong for the street
  address, we corrected it from the address (14 corrections):
  - Greenpoint (zip 11222), not Williamsburg: Oxomoco, Restaurant Yuu, Pierozek, Taqueria El Chato.
  - Hell's Kitchen: Chalong, Kung Fu Little Steamed Buns Ramen.
  - Flatiron District: Coqodaq. Union Square: La Dong.
  - NoHo: Torien, Yoshino.
  - Murray Hill: Little Alley, Norma Gastronomia Siciliana.
  - Koreatown: HanGawi, Cho Dang Gol.

  Blue Hill at Stone Barns is given the hamlet Pocantico Hills (Wikipedia).
- **Scope check.** Every 2025 NY Star, Bib and new Recommended address is in the five boroughs or Westchester County. **No MICHELIN New
  York selection was found upstate or on Long Island.**
- **Green Star.** The Green Star was retired worldwide from June 1, 2026 and replaced by "Mindful Voices", an editorial platform, not an
  award (travellingforbusiness.co.uk, May 19, 2026). The 2025 NY Green Stars (Blue Hill at Stone Barns, Dirt Candy, Family Meal at
  Blue Hill, One White Street) are kept only in `green_star_history`.

**James Beard Foundation**
- We read the official jamesbeard.org story pages for the 2023-2026 semifinalists, nominees and winners (12 pages, none blocked). We
  extracted every entry ending ", NY".
- We read JBF's America's Classics pages for 2022, 2023, 2024, 2025 and 2026, and Wikipedia's "List of James Beard America's Classics"
  for all years.
- We did not query the JBF past-awards search backend.

## Counts

**MICHELIN 2025, New York**
- Stars: 5 three-star, 15 two-star, 52 one-star.
- Bib Gourmand:
  - 88 confirmed. 86 are in `restaurants`; the other 2 (Atla, Bayon) are in `closed_since`.
  - Michelin's own article says 90. We saw that number only as a search-result snippet of guide.michelin.com.
  - The 4 Westchester holdovers above are unconfirmed.
- Recommended: no complete list or per-city count on any allowed source.
  - The release gives only Northeast totals: 6 three-star, 22 two-star, 93 one-star, 9 Green Star, 166 Bib, 377 Recommended, 664 total.
  - It also lists the 31 NY Recommended restaurants that were new in 2025. They are in `recommended_new_2025_ny` as a partial list.
  - For comparison, 2024 NY had 220 Recommended and 385 restaurants in total.
- New in 2025:
  - Stars: Sushi Sho (promoted to 3 Stars), Joo Ok (promoted to 2 Stars), and four new 1 Stars: Bridges, Huso, Muku and Yamada.
  - Masa dropped from 3 Stars to 2 Stars.
  - 9 new Bibs: Bánh Anh Em, Chalong, La Dong, Laliko, Noreetuh, Olmo, Sal Tang's, Taqueria El Chato and Yemenat.
- Special awards for NY: Sommelier Award to Annie Shi (Lei), and Young Chef / Culinary Professional Award to India Doris (Markette).

**JBF, New York State.** One line per category and year, at the highest level reached:

| Year | Winners | Nominees | Semifinalists |
|---|---|---|---|
| 2023 | 1 | 8 | 31 |
| 2024 | 1 | 9 | 30 |
| 2025 | 5 | 7 | 34 |
| 2026 | 3 | 9 | 36 |

- In total there are 174 category-year lines, spread over 150 place records.
- America's Classics: 18 NY places (1998-2026). 17 are on Wikipedia's open list; Prime Burger closed in 2012.

## Checks against the brief

- **Confirmed:**
  - The five three-star restaurants.
  - 15 two-star restaurants, including Blue Hill at Stone Barns (630 Bedford Rd, Pocantico Hills; Michelin's mailing address says
    Tarrytown, NY 10591).
  - JBF 2025 Best Chef: New York State winner Vijay Kumar (Semma).
  - JBF 2026 Best Chef: New York State winner Hooni Kim (Meju, Queens).
  - JBF 2026 Best New Restaurant winner Lei (New York, NY).
  - 2026 America's Classics: New York State honoree Eng's (Kingston).
- **Different from the brief:**
  - **Announcement date:** Nov 18, 2025 (evening), not Nov 19. Nov 19 is when the press coverage ran.
  - **One-star count:** 52, not ~51. We found no 2025 one-star closed since the edition.
  - **Bib count:** 88 confirmed (Michelin reports 90), not ~81. Even after removing the 2 that closed, the open count is 86.
  - **Recommended (~231):** not verified.

## Judgment calls

- **Names.** We use the name on the sign where Michelin's list differs: Jungsik ("Jungsik New York"), Sushi Nakazawa ("Sushi Nakazawa
  New York"), Katz's Delicatessen ("Katz's") and Hometown Bar-B-Que ("Hometown Barbecue New York"). Michelin's name is kept in
  `michelin_name`.
- **`new`** is true when the place was new to that distinction in 2025, including promotions (Sushi Sho, Joo Ok).
  `previous_distinction` is set for Sushi Sho, Joo Ok and Masa.
- **Muku and L'Abeille** both show 412 Greenwich St in Michelin's list. Wikipedia confirms that Muku took over the former Sushi Ichimura
  space at 412 Greenwich St.
- **La Bastide by Andrea Calstier** is at 721 Titicus Rd, North Salem, per Michelin's 2025 list and Wikipedia. Cenadou (new
  Recommended) shares the address.
- **JBF levels.** We use JBF's own word "nominee" for finalists, and never call a nominee a winner.
- **America's Classics** honorees are recorded as winners. Le Veau d'Or carries both America's Classics 2011 and the 2025 Outstanding
  Restaurateur win.
- **Group awards** are attached to every restaurant JBF named in the entry:
  - Lee Hanson and Riad Nasr (2025 Outstanding Restaurateur winners): Frenchette, Le Veau d'Or and Le Rock.
  - Simon Kim (Outstanding Restaurateur semifinalist 2025 and 2026): COTE, Undercote and COQODAQ.
  - Elizabeth Street Hospitality (2026): The Musket Room, Raf's and Cafe Zaffri.
  - Overthrow Hospitality (2024): Cadence, Etérea and Avant Garden.
  - Foster Supply Hospitality (2023): The DeBruce, Arnold House Tavern and Kenoza Hall.
  - Zaab Zaab owners (2024): Zaab Zaab and Zaab Zaab Talay.
- **Restaurants JBF listed under the wrong borough or city:**
  - Zaab Zaab is in Elmhurst, Queens.
  - Dept of Culture is in Brooklyn.
  - Mel the Bakery moved from Manhattan to Hudson in late 2023 and is one record.
- **Other JBF entries listed under "New York, NY"** are recorded as Manhattan unless a source said otherwise.
- **Evidence for `open`.** A place counts as open only with a 2025-26 dated source. We accepted:
  - the MICHELIN 2025 selection (2025-11);
  - a 2025 or 2026 JBF listing (the month that page was published);
  - an own site showing a 2025-26 date.

  `evidence_date` holds the newest of these. Places with no such source have `open: null`.

## Not verified, or weaker evidence

- **Bib retention.** Badageoni Georgian Kitchen, RaaSa, Rafele Rye and TVB by Pax Romana were 2024 Bibs, and their 2025 status is
  unknown. Michelin's 90 suggests two of them kept the Bib. Settle this with the Michelin app or site, viewed by a person.
- **Retention evidence is Wikipedia, not Michelin.** Retained Bibs depend on Wikipedia's 2025 column, which cites only Michelin's
  release of new Bibs. A spot-check against Michelin's own listing would help.
- **38 JBF places have `open: null`.** Most are 2023-24 semifinalists with no 2025-26 source, including:
  - Gage & Tollner, Scarr's Pizza, Lord's, Foul Witch, HAGS, Dante, FIELDTRIP and Ursula;
  - Aldama, Taqueria Ramírez, Karenderya, Brushland Eating House, Good Night, The DeBruce and KRU.
- **America's Classics without dated evidence:** Grand Central Oyster Bar (own site answered 403), Keens, Moosewood, Totonno's (owners
  sought a buyer from May 2024), A&A Bake & Doubles, and Mario's (Bronx; its old domain now serves spam).
- **The Restaurant at Kanopi** (White Plains): the domain we guessed belongs to an unrelated company. Not checked further.
- **Missing addresses.** 67 JBF records have no street address, mostly 2025-26 Manhattan semifinalists. City and county come from JBF,
  and the address is left null rather than guessed. Brooks' House of Bar-B-Q, Sahadi's and Eng's are open per their own sites, but no
  street address was captured from a page we read.
- **Llama Inn** is marked closed only because Wikipedia's Bib table says "Closed" in 2025. We read no dated closure story.
- **Harana Market** (Accord): its own site describes a food project with events and catering and lists the property for sale. Its status
  as a restaurant is unclear.

## Closed or closing (not to be shown)

**MICHELIN 2025 selections closed since the edition (`closed_since`)**
- Atla, Bib: closed May 31, 2026.
- Bayon, Bib: closed Aug 3, 2026; the owners retired.

**JBF honorees closed**
- Al Coro (2023)
- Clover Hill (Oct 2025). Charlie Mitchell, the 2024 Best Chef: NYS winner, had already left for Saga.
- Sushi Ichimura (2025)
- Llama Inn (per Wikipedia)
- Loring Place (July 14, 2026)
- Prime Burger (2012)
- **Lil' Deb's Oasis** (Hudson): final service set for **Oct 12, 2026**, five days after this check. It is marked `open: false`.

**2024 Bibs closed before the 2025 edition:** Cecily and Ugly Baby (in `bib_2024_not_in_2025`).

**People who moved.** Camari Mick (pastry honors 2023-2025 at The Musket Room and Raf's) is opening her own restaurant, Calabash, in the
West Village (Sept 2026).

## Hosts not used or blocked

**Not used, because robots.txt disallows Claude or AI agents**
- guide.michelin.com, Eater (ny.eater.com, eater.com), Grub Street, NY Post, amNY, Boston Globe, Patch, Westchester Magazine.
- westchestercurated.com and theexaminernews.com. A page from each was fetched in the same command as the robots check. It was
  discarded after we saw the disallow, and nothing from it is used or cited.

**Blocked or failed, and not retried**
- blog.resy.com: Cloudflare block.
- cititour.com: Cloudflare challenge.
- helpnewyork.com: block page.
- opentable.com: connection timeout.
- thecaterer.com: 429.
- oysterbarny.com: 403.
- Several own sites did not resolve.

**Closure sweep.** We read all of whatnow.com's New York closing and Michelin stories from Nov 2025 to Oct 2026 (81 articles, using its
sitemap) and matched them against every name in both files. This is not exhaustive: it covers one outlet only.

## Leads

- **Michelin listing check.** Before showing the 2025 Bibs, have a person check the Michelin app or site for the 4 Westchester Bibs,
  and for any 2025 Bib or Star removed during 2026.
- **The 2026 NY selection lands Dec 14, 2026.** Re-run then; that run should also pick up any per-city Recommended count.
- **The OpenTable blog** "2025's MICHELIN Bib Gourmands are out for New York" may have the full list of 90. It timed out from here:
  https://www.opentable.com/blog/michelin-bib-gourmand-nyc/

## WebSearch budget

We used 13 WebSearch calls. One more was rejected by the API before it ran (a blocked domain was in the filter), and one extended
search may have run a second query internally. That leaves about 15 of the 30 shared calls.


## Open-status check of the 38 `open: null` JBF records (2026-10-08)

Only `open`, `evidence_date`, `closed_date`, `address`, `zip` and `sources` were changed, and only on these 38 records. The `note`
fields were left as they were, so some still say "unverified": update them when the notes are next rewritten.

**How.** NYC DOHMH restaurant inspection open data (Socrata, `43nn-pn8j`; cited as `?camis=`), NYSDOH food service inspections
(`cnih-y5dw`; cited as `?nys_health_operation_id=`), NYS Ag & Markets food safety inspections (`d6dy-3h7r`, one bakery), own sites
with a dated 2025-26 event, and dated local news (EV Grieve, Greenpointers, BKMAG). Inspection records with the placeholder date
1900-01-01 (not yet inspected) were not counted. 13 WebSearch calls were used.

**Now open (26).** `evidence_date` is the newest dated source.
- NYC inspection data (17): A&A Bake & Doubles Shop (2026-07, zip 11216), Grand Central Oyster Bar (2025-10), Keens (2026-05),
  Mario's (2026-09; address 2342 Arthur Ave, 10458), Totonno's (2026-03; BKMAG Jan 7, 2026 also shows the family still running it
  while it's for sale), All Night Skate (2026-02, zip 11233), Dante (2026-08, 79 MacDougal St), FIELDTRIP (2026-09: 109 Lenox Ave
  and 30 Rockefeller Plaza), Gage & Tollner (2026-09), HAGS (2026-02, zip 10003), Harlem Hops (2026-04; zip 10030 from its own
  site), KRU (2026-10), La Vara (2026-01), Lord's (2025-09), Scarr's Pizza (2026-09), Taqueria Ramírez (2026-07; 94 Franklin St,
  11222), Ursula (2026-05; 387A Nostrand Ave, 11216, where it moved in April 2023).
- NYSDOH inspections (4): Moosewood (2026-07), Arnold House Tavern (2026-02, zip 12758), Karenderya (2026-08; 248 Main St, Nyack
  10960), The DeBruce (2026-05, zip 12758).
- NYS Ag & Markets inspection (1): She Wolf Bakery (2025-04; 141 Flushing Ave, Suite 103, Brooklyn Navy Yard Building 77, 11205).
  Its own site lists the Navy Yard cafe and 13 Greenmarkets but carries no date.
- Own site with a dated 2025-26 item (3): Avant Garden (Jain dinner Sept 27, 2026; now at 95 Avenue A, 2nd floor, 10009, which
  matches the "Amor y Amargo / Avant Garden" inspection record of Oct 2025), Brushland Eating House (Memorial Day dinner May 24,
  2026; 1927 County Highway 6, 13740), Kenoza Hall (2026 Bethel Woods concert-season dinner packages; 5762 NY State Route 52,
  Kenoza Lake 12750).
- Dated news (1): Foxface Natural (EV Grieve, Mar 20, 2025; 189 Avenue A). **Re-check:** NYC inspection data has no record at
  all for 189 Avenue A. EV Grieve has no closing story, but this is the weakest of the 26.

**Now closed (5).**
- Foul Witch: closed after service Nov 30, 2025 (EV Grieve, Apr 16, 2026); Singapore Social is taking the space.
- Ensenada (168 Borinquen Pl, 11211): announced closing Oct 26, 2025 (Greenpointers, Oct 9, 2025). A new permit ("Kinda Nice") is
  pending at the address.
- Etérea (511 E 5th St): closed March 2024 (EV Grieve, July 2, 2025).
- Aldama (91 S 6th St, 11249): Good Days opened "in the former home of Aldama" on Oct 1, 2025 (Greenpointers, Oct 3, 2025). The
  closing date is not in the source, so `closed_date` is null.
- LittleMad: NYC Tourism's listing marks it "Out of Business". It has no date, so `closed_date` is null. Search snippets disagree
  on the date (May 2024, or 2025).

These 5 belong in `closed_<region>.json`. That file was not touched in this pass.

**Still `open: null` (7).**
- Cadence: not in Overthrow's 2026 venue list. Its last NYC inspection was Nov 2024 (111 E 7th St, which was filled in).
  Snippets from HappyCow and Yelp say it closed Nov 22, 2025, but HappyCow returned 403 and Yelp isn't evidence. Likely closed.
- Zaab Zaab Talay: renamed Zaab Zaab and still at 208 Grand St, **Williamsburg, Brooklyn**, not Manhattan as the record says.
  Its own site answered 403, and there is no NYC inspection record at that address. City and county need fixing; the address was
  not filled because the record's city is wrong.
- Harana Market: in 2026 it runs pre-order pickups (Sept 4-5) and events, and the property is for sale. There is no regular
  restaurant service. Address 5125 Route 209, Accord 12404 was filled from its own site and NYSDOH (inspected Dec 2025).
- Mel the Bakery: its own site is live but shows no visible date, and the articles we found are from 2024. It is not in NYSDOH or
  Ag & Markets data.
- Good Night (Woodstock): its own site is live but undated. It is not in NYSDOH data, which covers only 19 Woodstock places.
- Make My Cake: its own site gives 409 W 125th St (zip 10027, filled) and current hours, but no date. It has no inspection
  record.
- The Restaurant at Kanopi: it's the restaurant on the 42nd-43rd floors of The Opus Westchester. The hotel's own site lists its
  hours (Thursday-Saturday), but nothing on the page is dated. The address 3 Renaissance Square, 10601 comes from the hotel's site;
  iloveny.com says 1 Renaissance Sq.

**Addresses left null.** Dante and FIELDTRIP have several NYC locations, and JBF named only "New York, NY". The original Dante is
at 79 MacDougal St, and FIELDTRIP's Harlem original is at 109 Lenox Ave.

**Hosts skipped.** These were not read: hvmag.com (robots.txt disallows ClaudeBot), corner.inc (robots.txt disallows all bots),
visithudsonny.com and happycow.net (403), and zaabzaabnyc.com (403).

## Closures applied (2026-10-08)

`closed_honors.json` removes the stale listings of 13 honorees that `jbf.json` marks closed: Foul Witch, Ensenada, Etérea, Aldama,
LittleMad, Clover Hill, Loring Place, Sushi Ichimura, Al Coro, Llama Inn, Prime Burger, Lil' Deb's Oasis (last night Oct 12, 2026)
and Cadence. Cadence was moved from unverified to closed: it is not on Overthrow Hospitality's venue list, and NYC DOHMH has no
inspection for it since Nov 7, 2024. LittleMad and Llama Inn have no DOHMH record at all; Ensenada's last one is June 18, 2025.
A closure removes a listing only when the listing carries the closed place's own name, so L'Abeille (which shares Sushi Ichimura's
permit) and new shops in former spaces stay. Zaab Zaab Talay's record was corrected to 208 Grand St, Williamsburg, Brooklyn.
