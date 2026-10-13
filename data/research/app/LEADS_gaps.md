# Leads: gap-filling pass (Staten Island, upstate bagels, LI/Westchester delis and bagels, Rochester hots, Plattsburgh, dim sum outside NYC)

These places probably belong in a guide but couldn't be verified under the README rules. Each entry gives the reason and what would settle it.

"DOH" means NYSDOH food-service inspections. `cnih-y5dw` is the last-inspection table. `2hcc-shji` holds active inspections since 2005 and is
more complete: it has rows that cnih-y5dw lacks, such as Clare & Carl's, Rain, Manhasset Bagels and Aberdeen. `aaxz-j6pj` holds inactive
facilities. "DOHMH" means NYC inspections. "SLA" means the State Liquor Authority license tables. "AgM" means Ag & Markets inspections
(`d6dy-3h7r`). Dates are the latest inspection.

**Blocked or unusable hosts in this pass.**
- Newsday: the fetch and search tools refuse it, although its robots.txt doesn't name Claude.
- These hosts disallow ClaudeBot in robots.txt: bupipedream.com, hvmag.com, westchestermagazine.com and kensingtonkosherdeli.com.
- These returned a 403 on robots or the page: visitbuffalo.com, bensdeli.net, bagelemporium.com, bagelboss.com, manhassetbagels.com,
  hudsonvalleysojourner.com, liherald.com, luckytolivehererealty.com and theorientrestaurant.com.
- liebmansdeli.com sits behind mod_security.
- nassaucountytourism.com shows a JavaScript "checking crawler" page to plain curl. WebFetch was served its pages normally, and those
  pages are cited, but none of them carries a date.

## slice (Staten Island)
- **Brother's Pizzeria**, 750 Port Richmond Ave, 10302.
  - Evidence: DOHMH lists it as "BROTHER PIZZA" (camis 50013726, 2026-04-30). Untapped (2015) says Filippo, Bart and Pietro Giove opened
    it in 1975.
  - Problem: no readable source says it sells slices. brotherspizzasi.com is a template page that mentions San Francisco.
  - *Settle:* a dated menu or story that mentions slices or Sicilian squares.
- **Pier 76**, 76 Bay St, St. George, 10301.
  - Evidence: DOHMH 2026-08-25. Its site says it serves "the same pizza as Staten Island's legendary Joe and Pat's".
  - Problem: it's a sit-down restaurant and lounge, and slices aren't confirmed.
- **Lee's Tavern**, 60 Hancock St, Dongan Hills, 10305.
  - Evidence: an SLA license that is active through Feb 2027.
  - Problem: DOHMH files it under Brooklyn with ZIP 11216 (camis 41397316, inspected 2025-09-29), apparently a data-entry slip. It's a bar,
    and no readable source shows slices.
- **Nunzio's Pizza**, 2155 Hylan Blvd, 10306.
  - Possibly closed: its SLA license expired 2024-06-30 and is listed as inactive, and DOHMH has no record since 2025.
  - *Settle:* local news on whether it closed. If it did, add it to closed_gaps.json.
- **The Pizza Parlor** (965 Jewett Ave and 6 Sneden Ave; both DOHMH 2026-06) and **Rosebank Pizza** (1372 Bay St; DOHMH 2026-07; its
  site, © 2026, has no slice items). No source shows slices or any history.
- **Denino's**: whole pies only. Same as the earlier leads.

## oldest (Staten Island)
- **The Historic Old Bermuda Inn**, 2512 Arthur Kill Rd.
  - Evidence: DOHMH 2025-07-25.
  - *Settle:* the first year it served food or drink at this address. The building is old, but a restaurant there before 1920 isn't shown.
- **Basilio Inn**, 6 Galesville Ct (DOHMH 2025-10-24). A search snippet gives 1921, which misses the pre-1920 rule.
- **Killmeyer's** is in gaps.json as `oldest` on the strength of its own history (bar from 1890). An independent source on continuous
  service through Prohibition would strengthen it.

## bagel (upstate)
- **Collegetown Bagels**, Ithaca. Established 1976. DOH shows 420 College Ave (2026-02-19), 301 E State St and 329 Pine Tree Rd.
  - Problem: the company runs seven locations with Ithaca Bakery, its site doesn't say which shop was the original, and it doesn't
    describe how the bagels are made. That makes it a chain under the brief.
  - *Settle:* the original's address, if wanted.
- **Uncommon Grounds** (Albany, Saratoga Springs, Clifton Park, Delmar, Queensbury, Rensselaer).
  - Evidence: its site says "We bake our bagels daily on premises".
  - Problem: NYSDOH lists about nine permits, so it's a chain, and the original location isn't identified. The old lead "Uncommon Bagels
    (Saratoga Springs)" is probably the shop at 402 Broadway (DOH 2026-01-30).
- **The Bagel Factory**, 9 Glenwood Ave, Binghamton.
  - Evidence: DOH 2026-05-14.
  - Problem: mybagelfactory.com no longer resolves, and Pipe Dream's bagel guide disallows ClaudeBot.
  - *Settle:* any readable dated source on its bagels.
- **Best Bagels in Town** (526 Hooper Rd, Endwell; DOH 2026-02-19) and **BC Bagel Shop** (1435 Upper Front St, Binghamton; DOH 2026-01-08).
  The Best Bagels site is JavaScript-only, and no readable source describes either shop's bagels.
- **Bagel Jay's** (Buffalo): its site is JavaScript-only. **Logan's Bagels** (27 Chandler St, Buffalo) has an AgM food-processing license
  (2025-12-23), but its site is JavaScript-only and a retail counter isn't confirmed.
- **Skeleton Bee Coffee and Bagels**, 250 S Clinton St, Syracuse (DOH 2026-08-18). Its site says only "made fresh in Syracuse".
- **Bagel Shop by Fox's** (360 Park Ave, Rochester; DOH 2025-12) and **Oneonta Bagel Company** (171 Main St, Oneonta; DOH 2026-01).
  No readable description of either.
- **Breadhive's** street address comes from its own site. The AgM bakery row is for its production bakery at 123 Baynes St.
- **Excluded on purpose:** Dewitt Bagel (4320 E Genesee St). Its site says its bagels are shipped from NYC, then thawed and baked.
  **Bagels & Blarney** (Horseheads) shows only a "launching soon" page.

## bagel (Long Island, Westchester, Rockland)
- **Bagel Emporium**, 391 Main St, Armonk (DOH 2026-04-20).
  - Evidence: Goldbelly says Mike Rozins founded it in 1983, it has six locations, and its bagels are hand-rolled and kettle-boiled.
  - Problem: it's a chain under the brief. Include the Armonk shop only if a source confirms it's the original. DOH also lists Chappaqua,
    Port Chester, Scarsdale (20 Chase Rd), Tarrytown and Yorktown Heights.
- **Bagel Boss**, 432 S Oyster Bay Rd, Hicksville (DOH 2026-03-26). It's a chain, and the Hicksville original's address is still
  unconfirmed.
- **H&R Bialys**, New Rochelle.
  - Evidence: Westfair (Feb 2025) says it has rolled and boiled bagels for almost 50 years.
  - Problem: no street address and no official row.
  - *Settle:* its address plus any dated record.
- **High Ridge Bagel Factory** (1805 Central Park Ave, Yonkers; DOH 2026-02-03) and **Bedford Bagel & Bakery** (720 N Bedford Rd,
  Bedford Hills; DOH 2026-02-06). Both appear in Westfair (Feb 2025), but nothing says they make their own bagels.
- **Village Square Bagels**, 1262 Boston Post Rd, Larchmont (DOH 2026-03-17). No readable description.
- **My Three Sons Bagel Café** (Garden City, Stewart Manor and Garden City South; DOH 2025–26). Nassau tourism names it without saying
  how the bagels are made.
- **Schmear Bagel & Cafe** is at 83 Main St, Port Washington (new DOH permit, 2026-03-03). **Life's a Bagel** is at 76 W Park Ave, Long
  Beach (DOH 2026-02-26). Both addresses are now settled. Whether either makes its own bagels is still open.
- **Goldberg's Famous Bagels** (New City, Yonkers) is a chain and was skipped.

## deli (Long Island, Westchester, Rockland)
- **Kensington Kosher Deli**, 27A Middle Neck Rd, Great Neck (DOH 2025-07-09).
  - Problem: its own site disallows Claude bots in robots.txt.
  - *Settle:* a readable dated menu or story listing its deli staples.
- **New City Kosher Deli & Restaurant**, 282 S Main St, New City (DOH 2026-08-14).
  - Problem: Hudson Valley Magazine and Hudson Valley Sojourner cover it but are blocked, and no site of its own was found.
  - *Settle:* a readable source for its menu (search snippets mention pastrami, corned beef, stuffed cabbage, matzo ball soup and knishes).
- **Rye Ridge Delicatessen**, 126 S Ridge St, Rye Brook (DOH 2026-03-20).
  - Problem: ryeridgedeli.com has no readable text, and its Jewish or kosher-style status is unconfirmed.
- **Woodro Kosher Deli**, 1441 Broadway, Hewlett (a new DOH permit, inspected 2026-08-31).
  - Problem: woodrokosherdeli.com now serves a gambling spam page.
  - *Settle:* a dated menu or story.
- **Pastrami Plus**, 2568 Hempstead Tpke, East Meadow (DOH 2026-09-18). Its site is © 2026, but the menu is JavaScript-only. There's
  still no evidence of matzo ball soup or knishes, the earlier lead's test. **Pastrami Express** (Seaford) has a DOH record from
  2026-04-15, but its owner says it isn't a Jewish deli.
- **Ben's Kosher Deli, Scarsdale** (718 Central Ave, per a search snippet).
  - Problem: Westchester Magazine is blocked, bensdeli.net returns 403, and there's no DOH row.
- **Liebman's Westchester location**: the site is behind mod_security. **Epstein's Somers location**: the only source is a syndicated
  lohud story, and Epstein's own site lists only Hartsdale.
- **Zan's Deli**, Lake Grove (Suffolk). Named in a search summary, but no site was found and Suffolk has no inspection table we use.

## hots / plate (Rochester)
- **The Original Charbroil House**, 1395 Island Cottage Rd. It has a Visit Rochester listing, but there's no DOH row under that name and
  charbroilcatering.com returns 403.
- **Rochester hots shops with 2026 DOH rows but no source on hots style or plates:** Empire Hots (2209 Empire Blvd, Webster), Webster Hots
  & Catering (55 E Main St), Spencerport Hots (500 S Union St), Chili Hots (3774 Chili Ave), Lakeside Hots (3345 Lake Ave), Gourmet Hots
  (295 E Ridge Rd), South Wedge Hots & Subs (492 Monroe Ave) and Ian's Neighborhood Hots (94 McCall Rd).
- **Vasko's on Park**, 266 Park Ave. It's on Visit Rochester's 2026 plate list, but it's a bar. Include it only if bars with a plate
  qualify.
- **West Ridge Hots** is in gaps.json under its DOH name. Visit Rochester spells it "Westridge Hots". A photo of the sign would settle
  the name.

## hots (Plattsburgh)
- **McSweeney's Red Hots North**, 4704 State Route 9. There's still no DOH row (only "McSweeney's Red Hots #2" on Route 3, which is in the
  guide), and it isn't on the town's 2026 list beyond the McSweeney's name.
- **Clare & Carl's** is settled in gaps.json at 4731 State Route 9, NYSDOH's address with a 2026-09-08 inspection. Its season is still
  unknown.

## dim sum (outside NYC)
- **Rain Modern Chinese**, 259 Lark St, Albany.
  - Evidence: DOH 2025-11-19. Its site, which has no date, says "on the weekends, dim sum brunch served on carts" and that it opened in
    November 2013.
  - *Settle:* a dated 2025–26 source on weekend dim sum.
- **Jia**, 84 Old Shore Rd, Port Washington.
  - Evidence: DOH 2025-03-06. Its site and Nassau tourism stress dim sum, but neither page has a date.
- **The Orient**, 623 Hicksville Rd, Bethpage (DOH 2026-04-01).
  - Problem: the only claim of daily dim sum is on a realty blog that returns 403, and its site returns 403.
- **Ala Shanghai** (Latham) and **Hong Kong Bakery & Bistro** (Wolf Rd, Colonie): only older blog mentions, and no DOH rows were found.
- **China Cafe**, 227 W Fayette St, Syracuse (DOH 2026-03-25). It has an online dim sum sampler item, but no dated source on dim sum
  service.
- **Zhou's** at Asia Food Market, Syracuse (search summary: Hong Kong-style dim sum seven days a week). asiafoodmkt.com timed out.
- **Hong Kong One at I-Square**, 400 Bakers Park, Irondequoit (DOH 2026-09-02). Visit Rochester describes it only as Chinese.
- **Ms. DimSum** (Yorktown Heights): still no 2025–26 source.
- **Skipped on purpose as chains:** Dim Sum Bloom (Rockville Centre and Stony Brook, plus three NYC shops) and Nana's Dim Sum & Dumplings
  (Scarsdale; a Colorado-based chain).
- **Royal Dim Sum** (Westbury, already in li_hudson_capital.json) is not closed. Its first NYSDOH permit (1166649) went dormant in March
  2025, but a new permit (1202250) was inspected 2026-02-24, so that record's evidence can move to 2026-02.

## Moved out of the guide after the 2026-10-08 source audit (their facts came from nassaucountytourism.com, which runs a crawler check)
- **Manhasset Bagels** (bagel), 510 Plandome Rd, Manhasset 11030.
  - Evidence: NYSDOH inspection 2026-04-16 (operation 1053970), so it is open.
  - Problem: its own site (manhassetbagels.com) and its online ordering page both answer with a bot check, and a design-preview copy of the site returns 403. Only delivery apps say the bagels are hand-rolled and kettle-boiled.
  - *Settle:* a readable source (own menu, dated news) that it makes its own bagels.
