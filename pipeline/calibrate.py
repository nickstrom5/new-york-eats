"""How often is a map listing a real food business? Measured against New York's official lists -> data/ny/calibration.json

Yardsticks (each one a list of every permitted food business in its area, so the rates are absolute):
- NYC: DOHMH inspection permits (CAMIS), the five boroughs.
- NYSDOH: restaurant-type food service establishments, counties outside NYC, Suffolk and Erie (some counties look undercounted
  against BLS QCEW, so the rate is also reported for the counties whose list looks complete).
- Buffalo: the city's active restaurant licenses.
And two partial ones:
- Suffolk: facilities cited for a violation in 2025 (a clean facility isn't on it).
- SLA: on-premises liquor licenses statewide (only places that serve alcohol hold one).
A match = the same business name nearby, or the same street address with a distinctive name word in common (listings_util).
Both directions are reported, plus a per-county table against QCEW's count of restaurants and bars (NAICS 722, 2025).
"""
import json, csv
import numpy as np, pandas as pd
from common import NY, RAW
import official
from official import ON_PREMISE
from listings_util import official_match

o = pd.read_pickle(f"{NY}/stage1.pkl")
F = official.load()
F = F[F.active & (F.name.notna() | F.addr.notna())].reset_index(drop=True)   # nameless records match by address only
o = o[~o.j_junk & ~o.j_outside].reset_index(drop=True)
TOWNWORDS = frozenset(w for t in pd.concat([o.place.dropna(), o.muni.dropna()]).unique() for w in t.upper().split())


def groups_web(L):
    s = L.src.fillna("none")
    return np.select([L.closed21, L.ov_closed, (s == "meta") & L.in21, s == "meta", s.isin(["AllThePlaces", "DAC"]) & L.in21,
                      s.isin(["AllThePlaces", "DAC"]), L.in21, s == "Foursquare", s == "BrightQuery", s == "Microsoft"],
                     ["Google 2021 says closed", "Overture says closed", "Meta + open in Google 2021", "Meta only",
                      "brand feed + Google 2021", "brand feed only", "Foursquare/BrightQuery/Microsoft + Google 2021",
                      "Foursquare only", "BrightQuery only", "Microsoft only"], "other")


def groups_app(L):
    conf, s = L.confidence.fillna(0), L.src.fillna("none")
    return np.select([L.ov_closed, (s == "meta") & (conf >= 0.95), (s == "meta") & (conf >= 0.9), s.isin(["AllThePlaces", "DAC"]),
                      (s == "BrightQuery") & (conf >= 0.95), s == "meta"],
                     ["Overture says closed", "Meta, confidence 0.95+", "Meta, 0.90-0.95", "brand feed", "BrightQuery 0.95+", "Meta, below 0.90"],
                     "other sources")


def measure(L, R, grp_fn, label):
    L = L.reset_index(drop=True)
    m = official_match(L, R.reset_index(drop=True), town_words=TOWNWORDS)
    L["hit"] = L.index.map(lambda i: i in m)
    L["grp"] = grp_fn(L)
    t = L.groupby("grp").hit.agg(["size", "mean"]).sort_values("size", ascending=False)
    print(f"\n== {label}: {len(L)} listings vs {R.biz.nunique()} businesses", flush=True)
    print(t.assign(mean=(t["mean"] * 100).round(1)).rename(columns={"size": "listings", "mean": "% matched"}).to_string(), flush=True)
    got = set(R.reset_index(drop=True).biz.iloc[list(m.values())])
    return L, {g: {"n": int(r["size"]), "matched": round(float(r["mean"]), 3)} for g, r in t.iterrows()}, got


res = {"web": {}, "app": {}, "coverage": {}}
EXCL = {"New York", "Kings", "Queens", "Bronx", "Richmond", "Suffolk", "Erie"}
areas = {
    "nyc_dohmh": (o.borough.notna(), F[F.jur == "dohmh"]),
    "state_nysdoh": (~o.county.isin(EXCL) & o.county.notna(), F[F.jur == "nysdoh"]),
    "buffalo": ((o.muni == "Buffalo") & (o.county == "Erie"), F[F.jur == "buffalo"]),
    "suffolk_2025": (o.county == "Suffolk", F[F.jur == "suffolk"]),
    "statewide_sla": (o.county.notna(), F[(F.jur == "sla") & F.kind.isin(ON_PREMISE)]),
}
hits = {}
for area, (sel, R) in areas.items():
    for kind, fn in (("web", groups_web), ("app", groups_app)):
        L, res[kind][area], got = measure(o[sel], R, fn, f"{area}, {kind} grouping")
        if kind == "app":
            hits[area] = (L, got)
    RB = R.drop_duplicates("biz")
    res["coverage"][area] = {"n": int(len(RB)), "found": round(float(RB.biz.isin(got).mean()), 3)}
    if "kind" in RB and RB.kind.nunique() > 1:
        bk = RB.assign(found=RB.biz.isin(got)).groupby("kind").found.agg(["size", "mean"])
        res["coverage"][area]["by_kind"] = {k: {"n": int(r["size"]), "found": round(float(r["mean"]), 3)} for k, r in bk.iterrows()}
    print(f"{area}: official businesses found among the map listings: {res['coverage'][area]['found']:.1%} of {len(RB)}", flush=True)

# ---- per county: QCEW establishments, the official lists, and how many listings each source kind has
q = {r["area_fips"]: int(r["annual_avg_estabs"]) for r in csv.DictReader(open(f"{RAW}/official/qcew_722_2025a.csv"))
     if r["area_fips"].startswith("36") and r["own_code"] == "5"}
cf = {f["properties"]["county"]: f["properties"] for f in json.load(open(f"{NY}/ny_counties.geojson"))["features"]}
Fa = F.drop_duplicates("biz")
nysdoh_hits = hits["state_nysdoh"][0]
rows = []
for c, p in sorted(cf.items()):
    L = o[o.county == c]
    conf = L.confidence.fillna(0)
    insp = {"New York": "dohmh", "Kings": "dohmh", "Queens": "dohmh", "Bronx": "dohmh", "Richmond": "dohmh", "Suffolk": "suffolk"}.get(c, "nysdoh")
    if c == "Erie":
        insp = None
    n_insp = int(((Fa.jur == insp) & (Fa.county == c)).sum()) if insp else 0
    lh = nysdoh_hits[nysdoh_hits.county == c] if insp == "nysdoh" else None
    rows.append({"county": c, "region": p["region"], "qcew_722": q.get(p["geoid"]), "inspection_list": insp or "none (Erie: HealthSpace search only)",
                 "inspection_n": n_insp, "sla_on_premise": int(((Fa.jur == "sla") & Fa.kind.isin(ON_PREMISE) & (Fa.county == c)).sum()),
                 "listings": int(len(L)), "meta_95": int(((L.src == "meta") & (conf >= 0.95)).sum()),
                 "meta_90_95": int(((L.src == "meta") & (conf >= 0.9) & (conf < 0.95)).sum()),
                 "meta95_on_list": round(float(lh[lh.grp == "Meta, confidence 0.95+"].hit.mean()), 3) if lh is not None and len(lh[lh.grp == "Meta, confidence 0.95+"]) else None})
cov = pd.DataFrame(rows)
cov["list_vs_qcew"] = (cov.inspection_n / cov.qcew_722).round(2)
print("\n" + cov.to_string(index=False), flush=True)
res["counties"] = rows
# NYSDOH rate in counties whose list looks complete (inspection list >= 85% of QCEW's count), to set the keep rule
full = set(cov[(cov.inspection_list == "nysdoh") & (cov.list_vs_qcew >= 0.85)].county)
lf = nysdoh_hits[nysdoh_hits.county.isin(full)]
t = lf.groupby("grp").hit.agg(["size", "mean"])
res["app"]["state_nysdoh_complete_counties"] = {g: {"n": int(r["size"]), "matched": round(float(r["mean"]), 3)} for g, r in t.iterrows()}
print(f"\nNYSDOH counties with a near-complete list ({len(full)}):", sorted(full))
print(t.assign(mean=(t["mean"] * 100).round(1)).to_string(), flush=True)
json.dump(res, open(f"{NY}/calibration.json", "w"), indent=1)
print("\nwrote calibration.json")
