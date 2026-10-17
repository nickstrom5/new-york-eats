"""Builds site/index.html (the private web leaderboard) from wi-eats/site/index.html (read-only reference), with New York's regions,
boards, sources and a provisional palette. Every replacement is asserted, so a change in the Wisconsin page fails loudly instead of
leaving Wisconsin text behind. The data comes split by region (site/ny_index.json + ny-<region>.json), loaded in parallel.
Usage: .venv/bin/python scripts/make-leaderboard.py"""
import os, re, sys
ROOT = os.path.join(os.path.dirname(__file__), "..")
src = open(os.path.join(ROOT, "..", "wi-eats", "site", "index.html")).read()
s = src


def R(a, b, n=1):
    global s
    c = s.count(a)
    if c != n:
        sys.exit(f"expected {n} of {a[:90]!r}, found {c}")
    s = s.replace(a, b)


# ---------------- head, palette, type
R('<title>Wisconsin Restaurant Leaderboard</title>', '<meta charset="utf-8">\n<title>New York Restaurant Leaderboard</title>')
R('<meta name="description" content="Every restaurant in Wisconsin, ranked on ratings, popularity, fish fry, supper clubs, custard, value and estimated sales.">',
  '<meta name="description" content="Every restaurant in New York State, ranked on ratings, popularity, honors, slices, bagels, wings, value, estimated sales and official inspection results.">')
R('family=Saira+Extra+Condensed:wght@600;700;800;900&family=Source+Sans+3:ital,wght@0,400;0,500;0,600;0,700;1,400', 'family=Barlow+Condensed:wght@600;700;800&family=Barlow:ital,wght@0,400;0,500;0,600;0,700;1,400')
R('''  /* Packers: green #203731, gold #FFB612, white. Light-only by design; gold is a fill with green text on it, never text on white. */
  color-scheme:light;
  --bg:#FFFFFF; --surface:#FFFFFF; --surface-2:#F1F5F2; --surface-3:#E1EAE4;
  --ink:#14241D; --ink-2:#2E4238; --muted:#53665B; --rule:#DAE3DD; --rule-2:#B6C6BC;
  --green:#203731; --green-2:#2D5242; --gold:#FFB612; --gold-soft:#FFE7A8; --on-gold:#203731;
  --map-fill:#EEF3EF; --map-line:#C2D1C7; --dot-edge:rgba(20,36,29,.35);
  --seq1:#CFE2D5; --seq2:#9CC4A9; --seq3:#5F9A74; --seq4:#326B4B; --seq5:#203731;
  --scrim:rgba(20,36,29,.38);
  --shadow:0 1px 2px rgba(20,36,29,.06),0 8px 28px rgba(20,36,29,.10);
  --display:"Saira Extra Condensed","Arial Narrow","Roboto Condensed",sans-serif;
  --body:"Source Sans 3",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;''',
'''  /* Layout: sticky leaderboard tabs over a filter rail + ranked list; one New York element, a deep-blue and buff-gold band under the header.
     Provisional state-flag palette (the app palette is Nick's call): deep blue #14325C (12.8:1 on white), buff gold #E0A526 only ever a
     fill under dark text (2.2:1 as text, failing AA), red #B3262E for MICHELIN badges with white text. Light-only by design. */
  color-scheme:light;
  --bg:#FFFFFF; --surface:#FFFFFF; --surface-2:#F1F4F8; --surface-3:#E0E6EF;
  --ink:#0F1A2C; --ink-2:#2A3A55; --muted:#55627A; --rule:#DCE2EC; --rule-2:#B5C0D3;
  --green:#14325C; --green-2:#24497F; --gold:#E0A526; --gold-soft:#F7E3B3; --on-gold:#14325C; --red:#B3262E;
  --map-fill:#F0F3F8; --map-line:#C6D0E0; --dot-edge:rgba(15,26,44,.35);
  --seq1:#CFDAEE; --seq2:#97AEDA; --seq3:#5576B8; --seq4:#2A4C92; --seq5:#14325C;
  --scrim:rgba(15,26,44,.38);
  --shadow:0 1px 2px rgba(15,26,44,.06),0 8px 28px rgba(15,26,44,.10);
  --display:"Barlow Condensed","Arial Narrow","Roboto Condensed",sans-serif;
  --body:"Barlow",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;''')
R('body{margin:0;background:var(--bg);', 'html,body{background:var(--bg)}\nbody{margin:0;background:var(--bg);')
R('.hmid{padding:22px 16px 18px;border-bottom:4px solid var(--gold)}', '.hmid{padding:22px 16px 18px;border-bottom:6px solid var(--gold);box-shadow:0 4px 0 var(--green)}')
R('.tab.wi{border-color:#D9A21A;background:#FFF9EA}', '.tab.wi{border-color:#C98F12;background:#FDF5E2}')
R('.chips.wi .chip[aria-pressed="false"]{background:#FFF9EA;border-color:#D9A21A}', '.chips.wi .chip[aria-pressed="false"]{background:#FDF5E2;border-color:#C98F12}')
R('.badge.sc{background:var(--gold-soft);color:var(--on-gold)}', '''.badge.sc{background:var(--gold-soft);color:var(--on-gold)}
.badge.mi{background:var(--red);color:#fff}
.ng{display:inline-grid;place-items:center;min-width:24px;height:24px;padding:0 5px;border-radius:5px;font:800 15px/1 var(--body);color:#fff;background:#14325C;border:2px solid #14325C}
.ng.sm{min-width:18px;height:18px;font-size:12px;border-width:1px}
.ng.g-A{background:#fff;color:#14325C} .ng.g-B{background:#fff;color:#1B6B3A;border-color:#1B6B3A} .ng.g-C{background:#fff;color:#A04A00;border-color:#A04A00}
.ng.g-N,.ng.g-Z,.ng.g-P{background:#fff;color:#55627A;border-color:#98A3B8;font-size:11px}
.cnt{display:inline-block;padding:1px 7px;border-radius:5px;font:700 12.5px/1.5 var(--body);background:var(--surface-2);color:var(--ink-2);border:1px solid var(--rule-2)}''')
R('.fhint{font-size:12.5px;color:#8A4B00;margin:0}', '.fhint{font-size:12.5px;color:#8A1A2E;margin:0}')
R('#map{display:block;width:100%;max-width:min(760px,max(240px,calc((100dvh - var(--stickyH) - 120px) * 0.95)));margin:0 auto;aspect-ratio:0.95;touch-action:manipulation}',
  '#map{display:block;width:100%;max-width:min(980px,max(260px,calc((100dvh - var(--stickyH) - 120px) * 1.3)));margin:0 auto;aspect-ratio:1.3;touch-action:manipulation}')
R('@media (max-height:500px){#map{max-width:max(160px,calc((100dvh - var(--stickyH) - 70px) * 0.95))}}', '@media (max-height:500px){#map{max-width:max(160px,calc((100dvh - var(--stickyH) - 70px) * 1.3))}}')

# ---------------- header and filters
R('''    <p class="kicker" id="kicker">Wisconsin · map listings as of Sep 2026</p>
    <h1 id="h1">Every Wisconsin restaurant, <span class="count">ranked</span></h1>
    <p class="lede" id="lede">Supper clubs, taverns, custard stands, Friday fish fries and the places in between, from Superior to Kenosha. Each one is ranked on ratings, popularity, value and estimated sales, with Wisconsin's own boards for fish fry, supper clubs, custard and cheese curds. Flip any leaderboard to see the bottom.</p>''',
'''    <p class="kicker" id="kicker">New York State · map listings as of Sep 2026</p>
    <h1 id="h1">Every New York restaurant, <span class="count">ranked</span></h1>
    <p class="lede" id="lede">Slice joints, bagel shops, delis, wing bars, Utica riggies, Binghamton spiedies, MICHELIN stars and the places in between, from Montauk to Niagara Falls and Plattsburgh. Each one is ranked on ratings, popularity, value and estimated sales, with New York boards for slices, bagels and delis, wings and weck, hots and upstate classics, dim sum and the oldest places, plus NYC's official letter grades and the state's inspection records, each kept to its own jurisdiction. Flip any leaderboard to see the bottom.</p>''')
R('''      <label class="flabel" for="city">City or town</label>''', '''      <label class="flabel" for="region">Region</label>
      <select id="region"><option value="">All of New York</option></select>
    </div>
    <div class="fgroup">
      <label class="flabel" for="city">Borough, city or town</label>''')
R('<select id="city"><option value="">All of Wisconsin</option></select>', '<select id="city"><option value="">All of New York</option></select>')
R('<span class="flabel" id="l-tags">Wisconsin classics</span>', '<span class="flabel" id="l-tags">New York guides</span>')
R('<label class="toggle"><input type="checkbox" id="confirmed"> Only confirmed places (on a Milwaukee or Dane County license list, or in two sources)</label>',
  '<label class="toggle"><input type="checkbox" id="confirmed"> Only confirmed places (on an official list: a DOHMH or NYSDOH permit, a Buffalo or liquor license, a Suffolk inspection; or in two sources)</label>')
R('<p class="wnote">Each ingredient is a 0–100 percentile across Wisconsin.', '<p class="wnote">Each ingredient is a 0–100 percentile across New York State.')
R('WI Score recipe: <span id="wname">', 'NY Score recipe: <span id="wname">')
R('placeholder="Search name, town, street, zip, “fish fry”…"', 'placeholder="Search name, town, street, zip, “bagels”…"')

# ---------------- constants and state
R('const TAGS = [["supper","Supper clubs",1],["fishfry","Fish fry",2],["custard","Frozen custard",8],["curds","Cheese curds",4]];',
  'const TAGS = [["slice","Slices & regional pizza",1],["bagel","Bagels & appetizing",2],["deli","Delis",4],["wings","Wings",8],["weck","Beef on weck",16],["hots","Hots",32],["dimsum","Dim sum",64],["upstate","Upstate classics",128],["oldest","Oldest places",256]];')
R('const DEFAULT = {board:"overall",dir:"top",view:"list",city:"",', 'const DEFAULT = {board:"overall",dir:"top",view:"list",region:"",city:"",')
R('const JUR = ["", "City of Milwaukee", "Public Health Madison & Dane County"];',
  'const JUR = ["", "NYC DOHMH (restaurant permit)", "NYSDOH (food service permit)", "Suffolk County inspection record", "City of Buffalo restaurant license", "NY State Liquor Authority license"];\n'
  'const GR_TXT = {A:"Grade A", B:"Grade B", C:"Grade C", N:"Not yet graded", Z:"Grade pending", P:"Grade pending (re-opened)"};')
R('research:"our verified list, placed with its Google listing"', 'research:"our hand-checked list, placed on its street address"')
R('try { S = sanitize(JSON.parse(localStorage.getItem("wi-eats") || "null")); }', 'try { S = sanitize(JSON.parse(localStorage.getItem("ny-eats") || "null")); }')
R('localStorage.setItem("wi-eats", JSON.stringify(rest));', 'localStorage.setItem("ny-eats", JSON.stringify(rest));')
R('  if (typeof s.city === "string") o.city = s.city.slice(0, 60);', '  if (typeof s.city === "string") o.city = s.city.slice(0, 60);\n  if (typeof s.region === "string") o.region = s.region.slice(0, 40);')
R('  if (!skip.city && S.city && r.city !== S.city) return false;', '  if (S.region && r.region !== S.region) return false;\n  if (!skip.city && S.city && r.city !== S.city) return false;')
R('  const key = JSON.stringify([S.venues, S.hideChains, S.ratedOnly, S.minRev, S.confirmed, S.city,', '  const key = JSON.stringify([S.venues, S.hideChains, S.ratedOnly, S.minRev, S.confirmed, S.region, S.city,')
R('  if (S.city) f.push(["city", S.city]);', '  if (S.region) f.push(["region", S.region]);\n  if (S.city) f.push(["city", S.city]);')
R('  else if (k === "city") { S.city = ""; $("#cityq").value = ""; cityFromBox = false; }', '  else if (k === "region") { S.region = ""; S.city = ""; }\n  else if (k === "city") { S.city = ""; $("#cityq").value = ""; cityFromBox = false; }')
R('  $("#cuisine").value = S.cuisine; if ($("#city").value !== S.city) $("#city").value = S.city;', '  $("#cuisine").value = S.cuisine; $("#region").value = S.region; if ($("#city").value !== S.city) $("#city").value = S.city;')
R('  $("#city").onchange = e => { S.city = e.target.value; $("#cityq").value = ""; cityFromBox = false; rerender(); };',
  '  $("#region").innerHTML = `<option value="">All of New York</option>` + (META.regions || []).map(g => `<option value="${esc(g)}">${esc(g)}</option>`).join("");\n'
  '  $("#region").onchange = e => { S.region = e.target.value; S.city = ""; $("#cityq").value = ""; cityFromBox = false; rerender(); };\n'
  '  $("#city").onchange = e => { S.city = e.target.value; $("#cityq").value = ""; cityFromBox = false; rerender(); };')
R('  const rk = JSON.stringify([S.w, S.venues, S.hideChains, S.ratedOnly, S.minRev, S.city,', '  const rk = JSON.stringify([S.w, S.venues, S.hideChains, S.ratedOnly, S.minRev, S.region, S.city,')

# ---------------- boards
a = s.index('const sigShow = '); b = s.index('const board = () =>')
BOARDS = r'''const ratedShow = r => [stars(r.rating), revs(r)+(r.reviews === 1 ? " review" : " reviews")+" ('21)"];
const MI_TXT = ["", "MICHELIN Recommended", "Bib Gourmand", "1 MICHELIN Star", "2 MICHELIN Stars", "3 MICHELIN Stars"];
const ngPill = (g, sm) => `<span class="ng${sm ? " sm" : ""} g-${g}" title="${esc(GR_TXT[g] || g)} (official NYC grade)">${g}</span>`;
const guide = (id, tab, bits, what) => ({id, wi:true, tab, top:tab + ", highest rated", bottom:tab + ", lowest rated", metric:"rating", val:r=>r.bayes,
  need:r=>(r.tags & bits) && r.rating!=null, sub:what + " Ranked by Google rating (Sep 2021), adjusted for review count; places that opened later aren't rated yet and aren't listed here.",
  show:ratedShow, dup:"rating"});
const B = [
  {id:"overall", tab:"NY Score", top:"Top NY Score", bottom:"Lowest NY Score", metric:"NY Score", val:r=>r.score,
   sub:()=>"A blend of rating, popularity, value and estimated profit, weighted by the NY Score recipe in the filters. Places missing some data are pulled toward 40, a little below the middle.",
   show:r=>[Math.round(r.score), "NY Score"]},
  {id:"rating", tab:"Rating", top:"Highest rated", bottom:"Lowest rated", metric:"rating", val:r=>r.bayes, need:(r,d)=>r.reviews >= (d==="top"?15:40),
   sub:"Google star rating as of the Sep 2021 snapshot, adjusted for review count so a 5.0 from three friends doesn't beat a 4.8 from 3,000 strangers.",
   show:ratedShow, dup:"rating"},
  {id:"popular", tab:"Popularity", top:"Most popular", bottom:"Least popular", metric:"reviews", val:r=>r.reviews, need:r=>r.reviews!=null,
   sub:"Total Google reviews as of Sep 2021: the best public stand-in for how many people walk through the door. Places opened since aren't in the snapshot, and the snapshot caps counts at 9,998 (shown as 9,998+).",
   show:r=>[revs(r), (r.reviews === 1 ? "review" : "reviews")+" ('21) · "+stars(r.rating)], dup:"rating"},
  {id:"gems", tab:"Hidden gems", top:"Hidden gems", bottom:"Popular but panned", metric:"rating", val:r=>r.gem, need:(r,d)=> d==="top" ? (r.reviews>=20 && r.reviews<=250 && r.chain_n<5) : r.reviews>=600,
   sub:"Top: independents with 20–250 reviews and great ratings. Bottom: places with 600+ reviews and the lowest ratings. Both from the Sep 2021 snapshot.",
   show:ratedShow, dup:"rating"},
  guide("slice", "Slices", 1, "Slice pizzerias, Buffalo-style pizza and Utica tomato pie: places we hand-checked in Oct 2026 (each with a 2025–26 source), plus places named for slices."),
  guide("bagel", "Bagels & delis", 2|4, "Bagel shops, appetizing stores and Jewish delis: hand-checked places (each with a 2025–26 source) plus places with bagels, appetizing or delicatessen in the name."),
  guide("wings", "Wings & weck", 8|16, "Buffalo wings and beef on weck: hand-checked Western New York places (each with a 2025–26 source) plus Western New York wing places by name."),
  guide("hots", "Hots & upstate", 32|128, "Rochester white hots and plates, Plattsburgh michigans, Texas hots, Capital Region mini dogs, Utica riggies and greens, half-moon cookies and Binghamton spiedies: hand-checked places (each with a 2025–26 source) plus hot dog places by name."),
  guide("dimsum", "Dim sum", 64, "Dim sum in Manhattan's Chinatown, Flushing, Sunset Park and beyond: hand-checked places (each with a 2025–26 source) plus places named for dim sum."),
  {id:"iconic", tab:"Iconic", top:"Most iconic", bottom:"Least iconic", metric:"iconic points", val:r=>r.s_icon, need:r=>r.s_icon!=null,
   sub:"Only places with an honor or a long, verified history: the MICHELIN Guide New York selection (stars, Bib Gourmand), James Beard awards and nominations 2023–26, America's Classics, and places we verified open at the same address since before 1920. Points for honors, years open and how many people know it.",
   show:r=>[Math.round(r.s_icon), "iconic pts" + (r.founded ? " · since " + r.founded : "")]},
  {id:"value", tab:"Value", top:"Best bang for buck", bottom:"Worst value", metric:"value score", val:r=>r.value_raw, need:r=>r.rating!=null,
   sub:"Rating (2021) relative to price level: a 4.7 at $ beats a 4.7 at $$$.",
   show:r=>[stars(r.rating)+" "+dollars(r.price)+(r.price_est?ESTTAG:""), "value "+Math.round(r.i_value)+" · rating '21"], dup:"rating"},
  {id:"price", tab:"Price", top:"Priciest", bottom:"Cheapest", metric:"price", val:r=>r.spend,
   sub:"Google price level (filled in from the chain or cuisine when missing, and marked est.) with typical spend per person. Within a price level, ties are ordered by NY Score.",
   show:r=>[dollars(r.price)+(r.price_est?ESTTAG:""), "~$"+r.spend+"/person "+ESTTAG]},
  {id:"sales", tab:"Sales", top:"Highest sales", bottom:"Lowest sales", metric:"sales", val:r=>r.rev, need:(r,d)=>r.rev!=null && (d==="top" || r.rev_src!=="model-low"), est:true,
   sub:d=>`Estimated yearly sales. Locations of chains with a published average (${META.model?.n_chains ?? "50+"} brands) use that average scaled by how busy the location is; independents use a model.` + (d==="bottom" ? " This end leaves out places with no review data (their figures are rough placeholders). The model never goes below $100K a year, so the very bottom is a tie, ordered by NY Score." : ""),
   show:r=>[money(r.rev), "sales/yr · " + src(r)], dup:"sales"},
  {id:"profit", tab:"Profit", top:"Most profitable", bottom:"Least profitable", metric:"profit", val:r=>r.profit, need:(r,d)=>r.profit!=null && (d==="top" || r.rev_src!=="model-low"), est:true,
   sub:d=>"Estimated yearly pre-tax profit: estimated sales × a typical margin for the segment, nudged by how well-loved the place is." + (d==="bottom" ? " This end leaves out places with no review data (their figures are rough placeholders). The sales model never goes below $100K a year, so the very bottom is mostly places at that floor, ordered by margin and then NY Score." : ""),
   show:r=>[money(r.profit), "profit/yr "+ESTTAG]},
  {id:"food", tab:"Food cost", top:"Biggest food bill", bottom:"Smallest food bill", metric:"food bill", val:r=>r.rev*r.food_cost/100, need:(r,d)=>r.rev!=null && (d==="top" || r.rev_src!=="model-low"), est:true,
   sub:d=>"Estimated yearly food purchases: estimated sales × the typical food-cost share for the cuisine (steak ~38%, pizza ~26%)." + (d==="bottom" ? " This end leaves out places with no review data. The sales model never goes below $100K a year, so the very bottom is mostly places at that floor." : ""),
   show:r=>[money(r.rev*r.food_cost/100), r.food_cost+"% food cost "+ESTTAG]},
  {id:"nycgrade", tab:"NYC grades", top:"Lowest NYC inspection scores", bottom:"Highest NYC inspection scores", metric:"inspection score", val:r=>r.ns == null || r.ng == null || r.ng > 2 ? null : -r.ns, need:r=>r.ng!=null && r.ng <= 2,
   tie:(a,b,d)=> (a.ng - b.ng) * (d==="top" ? 1 : -1) || String(b.nd).localeCompare(String(a.nd)),
   sub:d=>`New York City only, by the Health Department's (DOHMH) own numbers. Each row shows the official letter grade posted at the restaurant and its date, and the score at the latest inspection (violation points: lower is better). Grades are DOHMH's, never computed here: a grade comes from a graded inspection, so it can be older than the latest visit. Records through ${esc(META.records_through?.nyc || "")}.`,
   show:r=>[`${ngPill(r.gl)}`, `score ${r.ns} · inspected ${esc(r.nd || "")} · ${esc(r.addr || "")}`], dup:"grade"},
  {id:"statecrit", tab:"State inspections", top:"Fewest critical violations (state data)", bottom:"Most critical violations (state data)", metric:"critical violations", val:r=>r.sc == null ? null : -(r.sc * 100 + r.snc * 10) - r.sn / 100, need:r=>r.sc!=null,
   tie:(a,b,d)=> String(b.sd).localeCompare(String(a.sd)),
   sub:d=>`Counties outside NYC, Suffolk and Erie, from the New York State Department of Health's last-inspection data (records through ${esc(META.records_through?.nysdoh || "")}). Each row shows the latest inspection date and its critical violations (and how many weren't corrected on the spot), then non-critical ones. There is no official grade outside NYC and we don't make one. NYSDOH: “Any use of this data to develop a restaurant grading system is not supported or endorsed by the New York State Department of Health.” Any analyses, interpretations or conclusions here are ours, not NYSDOH's.`,
   show:r=>[`<span class="cnt">${plural(r.sc, "critical", "critical")}</span>`, `${r.snc ? r.snc + " not corrected · " : ""}${plural(r.sn, "other violation", "other violations")} · inspected ${esc(r.sd)} · ${esc(r.addr || "")}`], dup:"grade"},
];'''
s = s[:a] + BOARDS + "\n" + s[b:]

# ---------------- rows, badges, stats
R('''  if (r.hon & 1) h += `<span class="badge jbf">America's Classic</span>`;''',
  '''  if (r.mi) h += `<span class="badge mi">${MI_TXT[r.mi]}</span>`;
  if (r.hon & 1) h += `<span class="badge jbf">America's Classic</span>`;''')
R('''  if ((r.hon & 16) && !(r.hon & 7)) h += `<span class="badge icon">Icon</span>`;
  if ((r.tags & 1) && !/supper ?club/i.test(r.name)) h += `<span class="badge sc">Supper club</span>`;''',
  '''  if ((r.hon & 16) && r.founded) h += `<span class="badge icon">Since ${esc(r.founded)}</span>`;
  if (r.hc && r.tags) h += `<span class="badge sc">Hand-checked</span>`;''')
R('''  if (r.ff_n >= 3 && b.id !== "fishfry") bits.push(`<span>${r.ff_n} <i>fish fry mentions</i></span>`);
  if (r.grade) bits.push(`<span class="${dup("grade")}" title="Our grade from Dane County inspection results, not an official grade"><span class="grade sm g-${r.grade}">${r.grade}</span> <i>our inspection grade</i></span>`);''',
  '''  if (r.gl) bits.push(`<span class="${dup("grade")}" title="Official NYC letter grade (DOHMH)">${ngPill(r.gl, true)} <i>NYC grade ${esc(r.gd || "")}</i></span>`);
  else if (r.sc != null) bits.push(`<span class="${dup("grade")}" title="NYSDOH latest inspection">${plural(r.sc, "critical", "critical")} <i>state inspection ${esc(r.sd)}</i></span>`);''')
R('''  if (S.board !== "overall" && r.score != null) bits.push(`<span>${Math.round(r.score)} <i>WI Score</i></span>`);''',
  '''  if (S.board !== "overall" && r.score != null) bits.push(`<span>${Math.round(r.score)} <i>NY Score</i></span>`);''')
R('''const TAG_PH = [["friday fish fry","fishfry"],["fish fries","fishfry"],["fish fry","fishfry"],["fishfry","fishfry"],["supper clubs","supper"],["supper club","supper"],
  ["supperclub","supper"],["frozen custard","custard"],["custard","custard"],["cheese curds","curds"],["cheese curd","curds"],["curds","curds"]].map(([p, t]) => [norm(p), t]);''',
  '''const TAG_PH = [["dim sum","dimsum"],["dimsum","dimsum"],["beef on weck","weck"],["weck","weck"],["buffalo wings","wings"],["chicken wings","wings"],
  ["white hots","hots"],["white hot","hots"],["michigans","hots"],["texas hots","hots"],["garbage plate","hots"],["riggies","upstate"],["utica greens","upstate"],
  ["spiedies","upstate"],["spiedie","upstate"],["half moons","upstate"],["half moon","upstate"],["tomato pie","slice"],["slices","slice"],["pizza slice","slice"],
  ["appetizing","bagel"],["delicatessen","deli"],["jewish deli","deli"],["oldest","oldest"]].map(([p, t]) => [norm(p), t]);''')
R('''  // "fish fry", "supper club", "custard", "cheese curds" mean the Wisconsin tags, not words in a name''', '''  // "dim sum", "beef on weck", "riggies" mean the New York guides, not words in a name''')
R('''  // "fond du lac fish fry" means the town; "green bay rd" or "madison st" is a street, not the town''', '''  // "buffalo wings" is the guide; "flushing dim sum" means the town; "flushing ave" or "queens blvd" is a street, not the town''')
R('''  // a town named in the search ("fond du lac fish fry") narrows to it; a place NAMED that way still counts''', '''  // a town named in the search ("flushing dim sum") narrows to it; a place NAMED that way still counts''')
R('''    return `No places match “${esc(S.q.trim())}” in Wisconsin.''', '''    return `No places match “${esc(S.q.trim())}” in New York.''')
R('''  const setPh = () => { $("#q").placeholder = innerWidth < 400 ? "Search name, town, street…" : "Search name, town, street, zip, “fish fry”…"; };''', '''  const setPh = () => { $("#q").placeholder = innerWidth < 400 ? "Search name, town, street…" : "Search name, town, street, zip, “bagels”…"; };''')
R('''  if (S.board === "overall" && !weightTotal) return `The WI Score recipe is empty.''', '''  if (S.board === "overall" && !weightTotal) return `The NY Score recipe is empty.''')
R('''  if (pool.length && board().id === "clean") return `${plural(pool.length, "place matches", "places match")} ${what}, but inspection results are only published for Dane County (Madison and its suburbs). ${f.length ? undo + " to see them." : ""}`;''',
  '''  if (pool.length && board().id === "nycgrade") return `${plural(pool.length, "place matches", "places match")} ${what}, but NYC letter grades only exist in the five boroughs. ${f.length ? undo + " to see them." : ""}`;
  if (pool.length && board().id === "statecrit") return `${plural(pool.length, "place matches", "places match")} ${what}, but the state's inspection data covers counties outside NYC, Suffolk and Erie only. ${f.length ? undo + " to see them." : ""}`;''')
R('''"All of Wisconsin"}</option>`''', '''(S.region || "All of New York")}</option>`''')
R('''$("#cityhint").textContent = `No Wisconsin town matches''', '''$("#cityhint").textContent = `No New York town matches''')
R('''    else if (cityFromBox && S.city) { S.city = ""; cityFromBox = false; rerender(); }   // "Wausauk" is no longer Wausau''', '''    else if (cityFromBox && S.city) { S.city = ""; cityFromBox = false; rerender(); }   // "Uticaa" is no longer Utica''')
R('''    const hit = CITY_N.get(v) || (CITIES.find(([c]) => (" " + norm(c)).includes(" " + v)) || [])[0];   // CITIES is biggest first: "bay" -> Green Bay''',
  '''    const hit = CITY_N.get(v) || (CITIES.find(([c]) => (" " + norm(c)).includes(" " + v)) || [])[0];   // CITIES is biggest first: "falls" -> Niagara Falls''')
R('''const cols = [["name","City or town"],["n","Places","r"],["score","Avg WI Score","r"]''', '''const cols = [["name","Borough, city or town"],["n","Places","r"],["score","Avg NY Score","r"]''')

# ---------------- map
R('shapesPending = fetchJSON("wi_shapes.json").then(j => {', 'shapesPending = fetchJSON("ny_shapes.json").then(j => {')
R("WI_BOUNDS = a[0] < a[1] ? a : [-92.9, -86.8, 42.49, 47.08];", "WI_BOUNDS = a[0] < a[1] ? a : [-79.77, -71.85, 40.49, 45.02];")
R("const w = c.clientWidth || 600, h = Math.round(w / 0.95);", "const w = c.clientWidth || 600, h = Math.round(w / 1.3);")
R("  ctx.save(); land(); ctx.clip(\"evenodd\");   // county lines stop at the shore", "  ctx.save(); land(); ctx.clip(\"evenodd\");   // county lines stop at the shore and the state line")
R('''  $("#live").textContent = pool.length === 1 ? `Only one place matches your filters: ${r.name}.` : `Random pick: ${r.name}, ${r.city || "Wisconsin"}.`;''',
  '''  $("#live").textContent = pool.length === 1 ? `Only one place matches your filters: ${r.name}.` : `Random pick: ${r.name}, ${r.city || "New York"}.`;''')

# ---------------- drawer
a = s.index('function calibNote(r) {'); b = s.index('function sigCard(n, rt, what)')
s = s[:a] + r'''function calibNote(r) {
  const c = (META.calibration || {}).web || {}, g = k => [c.nyc_dohmh?.[k], c.state_nysdoh?.[k], c.buffalo?.[k]].filter(Boolean);
  const range = k => { const v = g(k).map(x => x.matched); if (!v.length) return null; const lo = Math.min(...v), hi = Math.max(...v); return lo === hi ? pctTxt(lo) : `${pctTxt(lo)}–${pctTxt(hi)}`; };
  const feed = r.src === "AllThePlaces" || r.src === "DAC", checked = r.hc ? " It's also on our hand-checked list, confirmed open with a 2025–26 source." : "";
  if (r.src === "research") return "This place isn't in the map listings as a place to eat (it's listed as a shop, bakery or inn, or not at all). It's on our hand-checked list, confirmed open with a 2025–26 source, and placed on its street address.";
  if (r.tier === 2) return (r.src === "official" ? `This place comes straight from the ${esc(JUR[r.jur])} list. The map listings we use didn't have it, so its location comes from the record.` : `Matched to an active ${esc(JUR[r.jur])}, so it's confirmed as a permitted or licensed business.`) + checked;
  const via = feed ? (r.tier === 1 ? "brand feed + Google 2021" : "brand feed only") : r.src === "meta" ? (r.tier === 1 ? "Meta + open in Google 2021" : "Meta only") : null;
  const rate = via ? range(via) : null, kind = feed ? "chain store-list listings" : "listings";
  if (!via) return "Kept because it's on our hand-checked list, confirmed open with a 2025–26 source, even though its only map listing comes from a source that's usually unreliable.";
  if (r.tier === 1) return `Found in two independent sources: a map listing and Google's 2021 data. Checked against NYC's DOHMH permits, NYSDOH's food service list and Buffalo's licenses, ${kind} like this matched a permitted business ${rate || "most"} of the time.` + checked;
  return `Found in one map source only. Checked against NYC's DOHMH permits, NYSDOH's food service list and Buffalo's licenses, single-source ${kind} like this matched a permitted business ${rate || "less than half"} of the time, so this one may be closed or misfiled.` + checked;
}
''' + s[b:]
R('''  const gq = encodeURIComponent(`${r.name} ${r.addr || ""} ${r.city || ""} WI`);''', '''  const gq = encodeURIComponent(`${r.name} ${r.addr || ""} ${r.city || ""} NY`);''')
R('''  const heroLbl = r.score == null ? (weightTotal ? "No WI Score: not enough data" : "WI Score recipe is empty")
    : ri >= 0 ? `WI Score · #${fmtN(ri+1)} of ${fmtN(L.length)} with your filters (ignoring search)` : "WI Score · outside your current filters";''',
  '''  const heroLbl = r.score == null ? (weightTotal ? "No NY Score: not enough data" : "NY Score recipe is empty")
    : ri >= 0 ? `NY Score · #${fmtN(ri+1)} of ${fmtN(L.length)} with your filters (ignoring search)` : "NY Score · outside your current filters";''')
R('''  const cats = `<div class="dsec"><h3>Category scores (percentile vs. all Wisconsin places)</h3>''', '''  const cats = `<div class="dsec"><h3>Category scores (percentile vs. all New York places)</h3>''')
a = s.index('  const sig = [sigCard('); b = s.index('  const moneyNote = {')
s = s[:a] + s[b:]
R('''This location isn't in the 2021 review snapshot, so this uses 85% of the chain's published U.S. average sales per location." : "Based on the chain's published U.S. average sales per location, scaled up or down by how busy this location was (2021 reviews) compared with the chain's other Wisconsin locations.",''',
  '''This location isn't in the 2021 review snapshot, so this uses 85% of the chain's published U.S. average sales per location." : "Based on the chain's published U.S. average sales per location, scaled up or down by how busy this location was (2021 reviews) compared with the chain's other New York locations.",''')
R('''scaled by 2021 review volume relative to similar Wisconsin places''', '''scaled by 2021 review volume relative to similar New York places''')
a = s.index('  const honorsList = ['); b = s.index('  $("#drawer").innerHTML = `${dhead(')
s = s[:a] + r'''  const honorsList = [...(r.mi ? [MI_TXT[r.mi] + " · MICHELIN Guide New York (2025 selection)"] : []), ...(x.jbf ? x.jbf.split(/;\s(?![^()]*\))/).map(v => "James Beard: " + v) : [])];
  const tagsTxt = TAGS.filter(([, , bit]) => r.tags & bit).map(([, l]) => l);
  const facts = (x.note || x.dishes || x.founded_note || x.season) ? `<div class="dsec"><h3>Hand-checked facts</h3>${x.note ? `<p style="margin:0 0 8px;color:var(--ink-2);font-size:14px">${esc(x.note)}</p>` : ""}
      ${kv([x.dishes ? ["On the menu", esc(x.dishes.split("; ").join(", "))] : null, x.founded ? ["Open here since", esc(x.founded)] : null, x.season ? ["Season", esc(x.season)] : null, x.kinds ? ["Guides", esc(x.kinds.split("; ").join(", "))] : null])}
      ${x.founded_note ? `<p class="note">${esc(x.founded_note)}</p>` : ""}${x.src ? `<p class="note">Source: <a href="${esc(x.src)}" target="_blank" rel="noopener">${esc(x.src.replace(/^https?:\/\/(www\.)?/, "").replace(/\/$/, "").slice(0, 70))}</a>, checked Oct 2026.</p>` : ""}</div>` : "";
  const nyc = r.nd || r.gl ? `<div class="dsec"><h3>Health inspections · NYC Department of Health (DOHMH)</h3>
      ${r.gl ? `<div class="hero" style="margin:0 0 10px">${ngPill(r.gl)}<span class="lbl">${esc(GR_TXT[r.gl] || r.gl)} · official letter grade${r.gd ? ", graded " + esc(r.gd) : ""}</span></div>` : `<p class="note">No letter grade on file yet.</p>`}
      ${kv([r.nd ? ["Latest inspection", esc(r.nd)] : null, r.ns != null ? ["Score at that inspection", fmtN(r.ns) + " violation points (lower is better)"] : null,
            r.nc != null ? ["Critical violations cited", fmtN(r.nc)] : null, r.np ? ["Pests cited in the year up to that inspection", esc(r.np.split(",").map(c => ({"04K":"rats","04L":"mice","04M":"roaches"})[c] || c).join(", "))] : null,
            r.nx ? ["Closed by DOHMH", esc(r.nx) + (x.reopened ? ` · re-opened ${esc(x.reopened)}` : "")] : null])}
      <p class="note">Grades are DOHMH's own, posted at the restaurant (A, B, C; N = not yet graded, Z = grade pending, P = pending on re-opening); we never compute a grade from the score. Source: NYC Open Data “DOHMH New York City Restaurant Inspection Results”, records through ${esc(META.records_through?.nyc || "")}. Full history at <a href="https://a816-health.nyc.gov/ABCEatsRestaurants/" target="_blank" rel="noopener">ABCEats</a>.</p></div>` : "";
  const stt = r.sd ? `<div class="dsec"><h3>Health inspections · NYSDOH ${x.lhd ? "· " + esc(x.lhd) : ""}</h3>
      <div class="hero" style="margin:0 0 10px"><span class="cnt" style="font-size:16px">${plural(r.sc, "critical violation", "critical violations")}</span><span class="lbl">at the latest inspection, ${esc(r.sd)}${r.snc ? ` · ${r.snc} not corrected on the spot` : ""} · ${plural(r.sn, "non-critical", "non-critical")}</span></div>
      ${x.st_hist ? `<ul class="lines">${x.st_hist.slice().reverse().map(([d, c, nc, n]) => `<li>${esc(d)} · ${plural(c, "critical", "critical")}${nc ? ` (${nc} not corrected)` : ""} · ${plural(n, "non-critical", "non-critical")}</li>`).join("")}</ul>` : ""}
      <p class="note">There is no official grade outside New York City, and we don't make one. NYSDOH: “The inspection data contained in this dataset was not collected in a manner intended for use as a restaurant grading system, and should not be construed or interpreted as such. Any use of this data to develop a restaurant grading system is not supported or endorsed by the New York State Department of Health.” Any analyses, interpretations or conclusions here are ours, not NYSDOH's. Source: health.data.ny.gov, records through ${esc(META.records_through?.nysdoh || "")}.</p></div>` : "";
  const sf = r.fn != null ? `<div class="dsec"><h3>Health inspections · Suffolk County, 2025</h3>
      ${kv([["Violations cited in 2025", fmtN(r.fn)], ["Inspections that cited one", fmtN(r.fi)], r.fd ? ["Latest of those", esc(r.fd)] : null])}
      <p class="note">Suffolk publishes the violations its inspectors cited, by year (“Restaurant Violations: 2025”, opendata.suffolkcountyny.gov); there's no score or grade, and an inspection with no violations isn't on the list. Nothing from 2026 is published yet.</p></div>` : "";
  const liq = r.liq ? ["Liquor license", esc(META.liqt[r.liq]) + (x.liq_since ? " · first issued " + esc(x.liq_since) : "")] : ["Liquor license", "— (none matched)"];
''' + s[b:]
R('''  $("#drawer").innerHTML = `${dhead(esc(r.city || "Wisconsin"), random)}''', '''  $("#drawer").innerHTML = `${dhead(esc(r.city || "New York"), random)}''')
R('''    <div class="addr">${r.addr ? esc(r.addr) + ", " : ""}${esc(r.city || "Wisconsin")}''', '''    <div class="addr">${r.addr ? esc(r.addr) + ", " : ""}${esc([r.hood, r.place, r.city].filter(Boolean).filter((v, i, a) => a.indexOf(v) === i).join(", ") || "New York")}''')
R('''    ${sig ? `<div class="dsec"><h3>Wisconsin classics · from Google reviews through Sep 2021</h3><div class="wisig">${sig}</div><p class="note">Average star rating of just the reviews that mention it. Reviews rate the whole visit, so read these as a lean, not a verdict.</p></div>` : ""}
    ${(honorsList.length || x.icon || x.founded) ? `<div class="dsec"><h3>Honors &amp; history</h3>${x.icon?`<p style="margin:0 0 8px;color:var(--ink-2);font-size:14px">${esc(x.icon)}</p>`:""}${honorsList.length?`<ul class="lines">${honorsList.map(v=>`<li>${esc(v)}</li>`).join("")}</ul>`:""}${x.founded ? `<p class="note">Open since ${esc(x.founded)} (verified).</p>` : ""}</div>`
      : (r.hon && !DETAIL ? `<div class="dsec"><h3>Honors &amp; history</h3><p class="note">${detailFailed ? "Couldn't load the honors. Check your connection and reopen this place." : "Loading…"}</p></div>` : "")}
    ${insp}''',
  '''    ${honorsList.length ? `<div class="dsec"><h3>Honors</h3><ul class="lines">${honorsList.map(v=>`<li>${esc(v)}</li>`).join("")}</ul><p class="note">MICHELIN and the MICHELIN Guide are trademarks of Michelin. James Beard Foundation awards are the Foundation's. Honors are facts, not ratings.</p></div>`
      : ((r.hon & 15) && !DETAIL ? `<div class="dsec"><h3>Honors</h3><p class="note">${detailFailed ? "Couldn't load the honors. Check your connection and reopen this place." : "Loading…"}</p></div>` : "")}
    ${facts}
    ${nyc}${stt}${sf}''')
R('''      x.lic ? ["License number", esc(x.lic.replace(/^(MKE|PHMDC)-/, ""))] : null,
      tagsTxt.length ? ["Wisconsin tags", esc(tagsTxt.join(", "))] : null,
      ["Listed as a bar or tavern", r.bar ? "Yes" : "No"], ["Locations in Wisconsin", r.chain_n >= 2 ? fmtN(r.chain_n) : "This one only"],''',
  '''      liq, x.buf ? ["Buffalo license", esc(x.buf)] : null,
      tagsTxt.length ? ["New York guides", esc(tagsTxt.join(", "))] : null,
      ["County", esc(r.county || "—") + (r.region ? " · " + esc(r.region) : "")], x.muni ? ["Town or city government", esc(x.muni)] : null,
      ["Listed as a bar or tavern", r.bar ? "Yes" : "No"], ["Locations in New York", r.chain_n >= 2 ? fmtN(r.chain_n) : "This one only"],''')
R('''  detailPending = fetchJSON("wi_detail.json").then(j => {
    const ex = (j && j.extra) || {}; DETAIL = {};''', '''  detailPending = Promise.all((META.files || []).map(f => fetchJSON(f.detail))).then(js => {
    const ex = Object.assign({}, ...js.map(j => (j && j.extra) || {})); DETAIL = {};''')

# ---------------- method cards
a = s.index('function methodCards() {'); b = s.index('// ---------------- boot ----------------')
s = s[:a] + r'''function methodCards() {
  const m = META, c = (m.calibration || {}).web || {}, cov = (m.calibration || {}).coverage || {}, rt = m.records_through || {};
  const dv = ["Foursquare only", "BrightQuery only", "Microsoft only", "Foursquare/BrightQuery/Microsoft + Google 2021"].flatMap(k => [c.nyc_dohmh?.[k], c.state_nysdoh?.[k]]).filter(Boolean).map(g => g.matched);
  const dropRange = dv.length ? `${Math.round(Math.min(...dv) * 100)}–${Math.round(Math.max(...dv) * 100)}%` : "a small share";
  const cols = [
    ["m", "Official records", [
      ["NYC letter grades", `The NYC Health Department's (DOHMH) restaurant inspection results (NYC Open Data, updated daily; records through ${esc(rt.nyc || "")}). Every permitted restaurant in the five boroughs, with the official letter grade posted at the door and its date, the latest inspection, its score and critical citations, and pests cited (rats, mice, roaches; “conditions conducive to” pests don't count). Places with a permit that the map listings lacked are added from the list.`],
      ["State inspections", `The New York State Department of Health's food service establishment inspections (health.data.ny.gov, posted monthly; records through ${esc(rt.nysdoh || "")}) for every county except NYC, Suffolk and Erie, which inspect on their own. Restaurant-type permits only (no schools, camps or day care). Shown: the latest inspection date with its critical, not-corrected and non-critical counts, and up to six earlier inspections. No grade exists and we don't make one; NYSDOH doesn't support or endorse grading built on its data, and any conclusions here are ours.`],
      ["Suffolk and Erie", "Suffolk County publishes the violations its inspectors cited, one year at a time (2025 is the latest): shown as violations cited in 2025. Erie County (Buffalo) publishes inspections only one search at a time, so we don't collect them; the City of Buffalo's open list of restaurant licenses confirms places inside the city."],
      ["Liquor licenses", `The State Liquor Authority's active licenses (data.ny.gov, daily): on-premises licenses (restaurant, tavern, hotel, brewer) confirm a place statewide and say it serves alcohol. Only trade names are used; legal names are never shown.`]]],
    ["s", "Map listings & 2021 snapshot", [
      ["Places statewide", `Overture Maps' open map listings (${esc(m.overture_release || "Sep 2026")} release, which merges Meta, Foursquare, chain store lists and other sources). We keep listings from Meta and from chains' own store lists, and drop Foursquare, BrightQuery and Microsoft listings: checked against NYC's and the state's permit lists, only ${dropRange} of those matched a permitted business. Each place sits in its county, one of New York's ten economic development regions, and, in NYC, its neighborhood.`],
      ["Ratings, reviews & price level", "Google Maps ratings from the UCSD Google Local research dataset, frozen in September 2021. Each Google listing is matched to one place at most, on a shared distinctive name word nearby. Places that opened later aren't in it, and the rating boards leave them out rather than guess."],
      ["Honors & guides", "Hand-checked in Oct 2026: the MICHELIN Guide New York selection (2025, the latest; stars and Bib Gourmand), James Beard awards and nominations 2023–26 and America's Classics, plus slice pizzerias, bagel shops and delis, Buffalo wings and beef on weck, upstate hots, Utica and Binghamton classics, dim sum and the oldest places, each with a 2025–26 source. Places our research found closed are removed."]]],
    ["e", "Estimated", [
      ["Sales & profit", `Chains use their published U.S. average sales per store (QSR 50, Technomic, company filings and franchise disclosures; ${m.model?.n_chains ?? "50+"} brands found here), scaled by how busy the location is. Independents start from a typical figure for their price level ($600K for $ up to $3.5M for $$$$) and scale with 2021 review volume. Profit applies a typical margin for the segment. Ballparks, not financial statements.`],
      ["Price, cuisine & food cost", "Missing price levels are filled in from the chain's or cuisine's usual New York level and marked est. Cuisine comes from the listing's category, the business name, DOHMH's own cuisine field in NYC and Google categories, so a few will be off. Food cost is the typical share for that cuisine × estimated sales, a benchmark rather than a measurement."]]],
  ];
  $("#srcgrid").innerHTML = cols.map(([t, h, cards]) => `<div class="srccol"><span class="tag ${t}">${h}</span>${cards.map(([h,p]) => `<div class="src"><h3>${h}</h3><p>${p}</p></div>`).join("")}</div>`).join("");
  const G = [["Meta + open in Google 2021","Meta listing, open in Google's 2021 data","kept · two sources"],["Meta only","Meta listing only","kept · listing only"],
    ["brand feed + Google 2021","Chain store list + Google 2021","kept · two sources"],["brand feed only","Chain store list only","kept · listing only"],
    ["Foursquare/BrightQuery/Microsoft + Google 2021","Foursquare / BrightQuery / Microsoft + Google 2021","dropped"],["Foursquare only","Foursquare only","dropped"],
    ["BrightQuery only","BrightQuery only","dropped"],["Microsoft only","Microsoft only","dropped"],["Google 2021 says closed","Google showed it closed in 2021","dropped"]];
  const cell = (j, k) => { const g = c[j]?.[k]; return g ? `${Math.round(g.matched * 100)}% <span style="color:var(--muted)">of ${fmtN(g.n)}</span>` : "—"; };
  const ct = (m.calibration || {}).counties || [];
  const fc = k => cov[k] ? `${Math.round(cov[k].found * 100)}% of ${fmtN(cov[k].n)}` : "—";
  $("#calib").innerHTML = c.nyc_dohmh ? `<div class="src" style="display:grid;gap:10px"><h3>How the map listings were checked</h3>
    <p>In the five boroughs (DOHMH permits every food service establishment), the counties on the state's inspection list, and Buffalo (city restaurant licenses), each map listing was checked against the official list: same business name nearby, or the same street address with a distinctive name word in common. The share that matched decides what's kept. The other way round, the map listings held ${fc("nyc_dohmh")} of NYC's permits, ${fc("state_nysdoh")} of the state list's restaurants, ${fc("buffalo")} of Buffalo's licenses and ${fc("statewide_sla")} of on-premises liquor licensees; the official places they lacked were added from the lists.</p>
    <div class="calib"><table><thead><tr><th scope="col">Kind of listing</th><th scope="col" class="r">NYC (DOHMH)</th><th scope="col" class="r">State list (NYSDOH)</th><th scope="col" class="r">Buffalo</th><th scope="col">Here</th></tr></thead><tbody>
    ${G.map(([k, l, what]) => `<tr><td>${esc(l)}</td><td class="r num">${cell("nyc_dohmh", k)}</td><td class="r num">${cell("state_nysdoh", k)}</td><td class="r num">${cell("buffalo", k)}</td><td>${what}</td></tr>`).join("")}</tbody></table></div>
    <p class="note">Matched = on an active permit or license. These are lower bounds: a real place under a different name on its permit counts as a miss, and some counties' state lists are incomplete (see below). Hand-checked places are kept whatever their source.</p></div>
    <div class="src" style="display:grid;gap:10px"><h3>Coverage by county</h3>
    <p>BLS counts restaurants and bars (NAICS 722, 2025 average) by county; the inspection list is each county's own official list. Where the list is much shorter than the BLS count (Nassau, Westchester), the state data is missing places, and listings there lean more on the map data.</p>
    <div class="calib" style="max-height:420px;overflow:auto"><table><thead><tr><th scope="col">County</th><th scope="col">Region</th><th scope="col" class="r">BLS restaurants & bars</th><th scope="col">Inspection list</th><th scope="col" class="r">On it</th><th scope="col" class="r">Liquor licenses</th><th scope="col" class="r">Map listings</th></tr></thead><tbody>
    ${ct.slice().sort((a, b) => (b.qcew_722 || 0) - (a.qcew_722 || 0)).map(v => `<tr><td>${esc(v.county)}</td><td>${esc(v.region)}</td><td class="r num">${fmtN(v.qcew_722)}</td><td>${esc({dohmh: "NYC DOHMH", nysdoh: "NYSDOH", suffolk: "Suffolk (2025 violations)"}[v.inspection_list] || "none in bulk")}</td><td class="r num">${v.inspection_n ? fmtN(v.inspection_n) : "—"}</td><td class="r num">${fmtN(v.sla_on_premise)}</td><td class="r num">${fmtN(v.listings)}</td></tr>`).join("")}</tbody></table></div></div>` : "";
}

''' + s[b:]

# ---------------- build: region files merged in order (sparse rows carry the global row number)
R('''  for (const [i, s, f] of sp.hon || []) if (rows[i]) { rows[i].s_icon = s / 10; rows[i].hon = f; }
  for (const [i, cl, g, ni, nr] of sp.insp || []) if (rows[i]) Object.assign(rows[i], {clean: cl, grade: g, n_insp: ni, n_reinsp: nr});''',
  '''  for (const [i, s, f, mi] of sp.hon || []) if (rows[i]) { rows[i].s_icon = s / 10; rows[i].hon = f; rows[i].mi = mi; }
  const GRL = m.grades || [];
  for (const [i, g, gd, d, sc, c, p, x] of sp.nyc || []) if (rows[i]) Object.assign(rows[i], {ng: g < 0 ? null : g, gl: g < 0 ? null : GRL[g], gd, nd: d, ns: sc, nc: c, np: p || null, nx: x || null});
  for (const [i, d, c, nc, n] of sp.st || []) if (rows[i]) Object.assign(rows[i], {sd: d, sc: c, snc: nc, sn: n});
  for (const [i, n, ins, d] of sp.sf || []) if (rows[i]) Object.assign(rows[i], {fn: n, fi: ins, fd: d});''')
# Wisconsin's dish signals aren't in New York's data: drop that loop
a = s.index('  // Wisconsin signals: Bayes-shrink'); b = s.index('  for (const [i, nn] of sp.sc || []) if (rows[i]) rows[i].sc_n = nn;')
s = s[:a] + s[b:]
R('''    o.src = (m.srcs || [])[C.src[i]] || null;''', '''    o.src = (m.srcs || [])[C.src[i]] || null; o.liq = C.liq[i] || 0; o.hc = C.hc[i] || 0;
    o.county = C.county[i] == null ? null : m.counties[C.county[i]]; o.region = C.county[i] == null ? null : m.regions[m.county_region[C.county[i]]];
    o.place = C.place[i] == null ? null : m.places[C.place[i]]; o.hood = C.hood[i] == null ? null : m.hoods[C.hood[i]];''')
R('''    o._s = " " + normRaw([o.name, o.city, o.zip, o.cuisine, o.brand].join(" ")) + " " + norm(o.addr) + " ";''', '''    o._s = " " + normRaw([o.name, o.city, o.place, o.hood, o.zip, o.cuisine, o.brand, o.county].join(" ")) + " " + norm(o.addr) + " ";''')
R('''  CITY_N = new Map();   // "st germain", "saint germain" and "St. Germain" are one town''', '''  CITY_N = new Map();   // "st albans", "saint albans" and "St. Albans" are one place''')
R('''             "fish", "fry", "custard", "curds", "cheese", "supper", "club", "brats", "tavern", "tap", "brewery", "kringle"]));''',
  '''             "slice", "slices", "bagel", "bagels", "deli", "delis", "pastrami", "knish", "knishes", "appetizing", "dim", "sum", "dumplings", "weck",
             "hots", "riggies", "spiedies", "spiedie", "michigans", "tavern", "tap", "brewery"]));''')
R('''  $("#h1").innerHTML = `<span class="count num">${fmtN(n)}</span> Wisconsin restaurants, ranked`;''', '''  $("#h1").innerHTML = `<span class="count num">${fmtN(n)}</span> New York restaurants, ranked`;''')
R('''  fetchJSON("wisconsin.json").then(j => {''',
  '''  fetchJSON("ny_index.json").then(ix => {
    const files = (ix.meta && ix.meta.files) || [];
    let got = 0;
    return Promise.all(files.map(f => fetchJSON(f.file).then(x => { got++; $("#btitle").textContent = `Loading… ${got} of ${files.length} regions`; return x; }))).then(parts => {
      const cols = {}, sparse = {};
      for (const k of Object.keys(parts[0].cols)) cols[k] = [].concat(...parts.map(p => p.cols[k]));
      for (const k of Object.keys(parts[0].sparse)) sparse[k] = [].concat(...parts.map(p => p.sparse[k]));
      return {n: ix.n, scale: ix.scale, meta: ix.meta, cols, sparse};
    });
  }).then(j => {''')
for word in ("Wisconsin", "Milwaukee", "Dane County", "fish fry", "supper club", "custard", "WI Score", "wi_", "Colorado"):
    hits = [m.start() for m in re.finditer(re.escape(word), s)]
    if hits:
        print(f"note: {len(hits)} '{word}' left, e.g. {s[max(0, hits[0]-60):hits[0]+40]!r}")
open(os.path.join(ROOT, "site", "index.html"), "w").write(s)
print("wrote site/index.html", len(s) // 1024, "KB")
