"""Official New York records -> one table of food businesses (data/ny/official.pkl)

Jurisdictions (`jur`):
- dohmh    NYC DOHMH "Restaurant Inspection Results": one row per CAMIS (permit). The dataset lists only places in an active status.
           Carries the posted letter grade and its date (official: A/B/C; N not yet graded, Z grade pending, P pending on re-opening),
           the latest inspection, its score and critical citations, pest evidence cited (04K rats, 04L mice, 04M roaches; 08A
           "conditions conducive" is NOT pest evidence) and DOHMH closures. Never a grade computed from the score.
- nysdoh   NYSDOH "Food Service Establishment: Last Inspection" (all of the state except NYC, Suffolk and Erie): restaurant-type
           facilities only (restaurants, taverns, delis, bakeries, frozen desserts, ice cream, food service establishments).
           Schools, day care, camps, colleges, SOFA, SED and institutional sites are left out. Critical / not-corrected counts only;
           no grade (NYSDOH says grading built on this data "is not supported or endorsed").
- suffolk  Suffolk County "Restaurant Violations: 2025": violations cited in 2025, grouped by facility. No score, no grade.
- buffalo  City of Buffalo "Restaurant Licenses" (active).
- sla      State Liquor Authority active licenses, on-premises classes (restaurants, taverns, hotels, clubs, caterers, brewers...);
           inactive licenses only to flag closures.

Only trade names (DBA) are ever kept. Legal names, permittees and operators were never downloaded (fetch_official.py).
"""
import os, re, json, math
import numpy as np, pandas as pd
from common import norm_name, RAW, NY, canon_city, name_sim, _stems, GENERIC

OFF = os.path.join(RAW, "official")
DIRS = {"N": "N", "S": "S", "E": "E", "W": "W", "NORTH": "N", "SOUTH": "S", "EAST": "E", "WEST": "W"}
TYPES = set("""ST STREET AVE AV AVENUE BLVD BOULEVARD RD ROAD DR DRIVE LN LANE CT COURT PL PLACE PKWY PARKWAY TER TERRACE TRL TRAIL WAY
HWY HIGHWAY CIR CIRCLE PLZ PLAZA SQ SQUARE MALL BND PASS XING RUN ROW WALK RDG TPKE TPK TURNPIKE PIKE EXT EXTENSION GRN GREEN CRES
COMMONS CMNS LNDG LANDING EXPY EXPRESSWAY""".split())
ORD = {"FIRST": "1", "SECOND": "2", "THIRD": "3", "FOURTH": "4", "FIFTH": "5", "SIXTH": "6", "SEVENTH": "7", "EIGHTH": "8", "NINTH": "9",
       "TENTH": "10", "ELEVENTH": "11", "TWELFTH": "12"}
SLA_KIND = {"Restaurant": "restaurant", "Summer Restaurant": "restaurant", "Winter Restaurant": "restaurant",
            "Food & Beverage Business": "tavern", "Summer Food & beverage business": "tavern", "Summer Food & Beverage Business": "tavern",
            "Winter Food & Beverage Business": "tavern", "Summer - Tavern Miscellaneous": "tavern", "Cabaret": "bar", "Night Club": "bar",
            "Hotel": "hotel", "Summer Hotel Liquor": "hotel", "Summer Hotel": "hotel", "Bed & Breakfast": "hotel",
            "Club": "club", "Summer Club": "club", "Winter Club": "club", "For-profit Club": "club", "Bottle Club": "club",
            "Golf Club": "club", "Summer Golf Club": "club",
            "Catering Establishment": "caterer", "Summer Catering Establishment": "caterer", "Off Premises Caterer Establishment": "caterer",
            "Restaurant Brewer": "brewery", "Micro-Brewer": "maker", "Micro-Brewer 3 Year": "maker", "Farm Brewer": "maker", "Brewer": "maker",
            "Farm winery": "maker", "Winery": "maker", "MicroFarm Winery": "maker", "Special Farm Winery": "maker", "Special Winery": "maker",
            "Farm Cidery": "maker", "Cider Producer": "maker", "Farm Meadery": "maker", "Combined Craft Status": "maker",
            "Distiller Class D (Farm Distiller)": "maker", "Distiller Class A-1 (Micro-distiller)": "maker",
            "Vessel": "venue", "Summer Vessel": "venue", "Summer Excursion & Sight Seeing Vessel": "venue", "Bowling Establishment": "venue",
            "Golf Venue": "venue", "Summer Golf Venue": "venue", "Legitimate theatre": "venue", "Legitimate Theatre": "venue",
            "Winter Legitimate Theatre": "venue", "Outdoor Athletic Fields and Stadiums": "venue", "Concert Hall": "venue",
            "Athletic/Sporting Event/Expositions/Large Gathering Venue": "venue", "Skiing Venue": "venue", "Tennis Venue": "venue",
            "Ice Skating Venue": "venue", "Summer Athletic/Sporting Event/Expositions/Large Gathering Venue": "venue"}
ON_PREMISE = {"restaurant", "tavern", "bar", "hotel", "brewery"}   # the licenses a restaurant or bar holds
NYSDOH_KEEP = {"Food Service Establishment - Restaurant": "restaurant", "Food Service Establishment - Food Service Establishment": "food",
               "Food Service Establishment - Restaurant/Catering Operation": "restaurant", "Food Service Establishment - Frozen Desserts": "sweets",
               "Food Service Establishment - Tavern": "tavern", "Food Service Establishment - Bakery": "bakery",
               "Food Service Establishment - Delicatessen": "deli", "Food Service Establishment - Ice Cream Store": "sweets"}
BORO = {"Manhattan": "New York", "Brooklyn": "Kings", "Queens": "Queens", "Bronx": "Bronx", "Staten Island": "Richmond"}
ENTITY_RX = re.compile(r"\b(?:INC|LLC|L\.L\.C|CORP|CORPORATION|LTD|CO|ENTERPRISES?|HOLDINGS?|GROUP|SPORTSERVICE|ASSOCIATES|PARTNERS|MANAGEMENT|INTERESTS)\b\.?", re.I)
PEST = {"04K": "rats", "04L": "mice", "04M": "roaches"}   # evidence of live pests or their signs; 08A (conditions conducive) is not


def road(a):
    """One spelling for numbered roads: 'ROUTE 9W' = 'RT 9W' = 'NY-9W' = 'STATE ROUTE 9W' = 'US ROUTE 9' = 'US-9'."""
    a = re.sub(r"(\d)\s*&\s*(\d)", r"\1-\2", a.upper())
    a = re.sub(r"\b(?:U\.?\s?S\.?|NY|N\.Y\.|STATE|COUNTY|CO)[-\s]+(?:ROUTE|RTE|RT|HIGHWAY|HWY|ROAD|RD)?\s*-?\s*(\d+[A-Z]?)\b", r"RT \1", a)
    a = re.sub(r"\b(?:ROUTE|RTE|RT)\.?\s*#?\s*(\d+[A-Z]?)\b", r"RT \1", a)
    a = re.sub(r"\bTPKE\b|\bTPK\b", "TURNPIKE", a)
    a = re.sub(r"\bAVENUE OF THE AMERICAS\b", "6 AVE", a)
    a = re.sub(r"\bST\.?\s+(?=MARKS|NICHOLAS|JAMES|JOHNS|PAULS|ANNS|FELIX|EDWARDS|LAWRENCE)", "SAINT ", a)
    return re.sub(r"\bHIGHWAY\b", "HWY", a)


def _ordinal(w):
    w = ORD.get(w, w)
    m = re.fullmatch(r"(\d+)(?:ST|ND|RD|TH)", w)
    return m.group(1) if m else w


def street_key(a):
    """'2505 Main St' -> ('2505', 'MAIN'); '37-04 74th St' -> ('3704', '74'); '134 ROUTE 9W' -> ('134', 'RT 9W');
    'W 4 ST' and 'West 4th Street' -> '4'."""
    if not isinstance(a, str):
        return None, None
    a = re.sub(r"[.,#]", " ", road(a))
    m = re.match(r"^\s*(\d+)[A-Z]?(?:\s*-\s*(\d+)[A-Z]?)?\s+(.*)$", a)
    if not m:
        return None, None
    num = m.group(1)
    if m.group(2) and len(m.group(2)) == 2 and len(num) <= 3:   # a Queens-style hyphenated number: "37-04" is house 3704
        num = num + m.group(2)
    words = [w for w in m.group(3).split() if w]
    while len(words) > 1 and words[0] in DIRS:
        words = words[1:]
    core = []
    for w in words:
        if w in TYPES and core:
            break
        core.append(_ordinal(w))
    return num, " ".join(core[:3]) or None


def street_nums(a):
    """'157-159 W Main St' -> {'157', '159'}; '2505 Main St' -> {'2505'}; '37-04 74th St' -> {'3704', '37'}."""
    if not isinstance(a, str):
        return set()
    a = road(a)
    m = re.match(r"^\s*(\d+)[A-Z]?(?:\s*-\s*(\d+)[A-Z]?)?\s", a.upper() + " ")
    if not m:
        return set()
    lo = int(m.group(1)); hi = int(m.group(2)) if m.group(2) else lo
    if m.group(2) and len(m.group(2)) == 2 and len(m.group(1)) <= 3:   # Queens-style "37-04" (or a short range "100-02")
        return {m.group(1) + m.group(2), m.group(1)}
    if hi < lo:   # "1500-02"
        hi = int(str(lo)[: len(str(lo)) - len(m.group(2))] + m.group(2)) if m.group(2) else lo
    return {str(x) for x in range(lo, hi + 1, 2 if (hi - lo) % 2 == 0 else 1)} if 0 <= hi - lo <= 12 else {str(lo)}


def _names(*vals):
    out = []
    for v in vals:
        if not isinstance(v, str):
            continue
        for part in re.split(r"\s*/\s*|\s+\bdba\b\s+|\s+&\s+(?=[A-Z][a-z])", v, flags=re.I):
            k = norm_name(re.sub(r"\b(?:LLC|INC|CORP|CORPORATION|LTD|CO)\b\.?", "", part, flags=re.I))
            if k and k not in out:
                out.append(k)
    return out


def _pt(s):
    """'POINT (-73.5 41.2)' or '(41.2, -73.5)' -> (lat, lon)."""
    if not isinstance(s, str):
        return np.nan, np.nan
    m = re.match(r"POINT \((-?[\d.]+) (-?[\d.]+)\)", s)
    if m:
        return float(m.group(2)), float(m.group(1))
    m = re.match(r"\((-?[\d.]+),\s*(-?[\d.]+)\)", s)
    if m:
        return float(m.group(1)), float(m.group(2))
    return np.nan, np.nan


def _ok(la, lo):
    return la == la and lo == lo and 40.4 < la < 45.1 and -79.9 < lo < -71.7


def _merc(x, y):
    return (2 * math.atan(math.exp(y / 6378137)) - math.pi / 2) * 180 / math.pi, x / 6378137 * 180 / math.pi


def records_through():
    """Publication lag: count only inspections at least 7 days before each feed's own last refresh (data meta), never hard-coded."""
    meta = json.load(open(f"{OFF}/socrata_meta.json"))
    out = {}
    for jur, vid in (("dohmh", "43nn-pn8j"), ("nysdoh", "cnih-y5dw")):
        out[jur] = (pd.Timestamp(meta[vid]["rowsUpdated"]) - pd.Timedelta(days=7)).strftime("%Y-%m-%d")
    return out


def _dohmh(through):
    d = pd.read_csv(f"{OFF}/dohmh.csv", dtype=str)
    d["idate"] = pd.to_datetime(d.inspection_date)
    d = d[(d.idate <= through) | (d.idate.dt.year == 1900)]
    d["gdate"] = pd.to_datetime(d.grade_date)
    rows = []
    insp = d[d.idate.dt.year > 1900].sort_values("idate")
    last = insp.groupby("camis").idate.max()
    graded = d[d.grade.notna() & d.gdate.notna()].sort_values("gdate").groupby("camis").tail(1).set_index("camis")
    lastrows = insp[insp.idate == insp.camis.map(last)]
    crit = lastrows[lastrows.critical_flag.eq("Critical")].drop_duplicates(["camis", "violation_code"]).groupby("camis").size()
    score = lastrows.drop_duplicates("camis").set_index("camis").score
    itype = lastrows.drop_duplicates("camis").set_index("camis").inspection_type
    # pests cited in the last 12 months of inspections (each code once per place)
    yr = insp[insp.idate > insp.camis.map(last) - pd.Timedelta(days=365)]
    pests = yr[yr.violation_code.isin(list(PEST))].groupby("camis").violation_code.agg(lambda s: ",".join(sorted(set(s))))
    closed = insp[insp.action.fillna("").str.startswith("Establishment Closed by DOHMH")].groupby("camis").idate.max()
    reopened = insp[insp.action.fillna("").str.startswith("Establishment re-opened")].groupby("camis").idate.max()
    first = d.sort_values("idate").drop_duplicates("camis", keep="last").set_index("camis").fillna("")
    for camis, r in first.iterrows():
        boro = r.boro if r.boro in BORO else None
        la, lo = pd.to_numeric(r.latitude, errors="coerce"), pd.to_numeric(r.longitude, errors="coerce")
        g = graded.loc[camis] if camis in graded.index else None
        li = last.get(camis)
        rows.append({"jur": "dohmh", "lic": "CAMIS-" + camis, "name": r.dba, "keys": _names(r.dba),
                     "addr": f"{r.building or ''} {r.street or ''}".strip(), "city": boro, "county": BORO.get(boro), "zip": (r.zipcode or "")[:5],
                     "kind": "food", "cred": r.cuisine_description, "active": True, "since": None,
                     "lat": la if _ok(la, lo) else np.nan, "lon": lo if _ok(la, lo) else np.nan, "phone": r.phone, "nta": r.nta, "bbl": r.bbl,
                     "grade": g.grade if g is not None else None, "grade_date": g.gdate.strftime("%Y-%m-%d") if g is not None else None,
                     "last_insp": li.strftime("%Y-%m-%d") if isinstance(li, pd.Timestamp) else None,
                     "score": pd.to_numeric(score.get(camis), errors="coerce"), "insp_type": itype.get(camis),
                     "crit": int(crit.get(camis, 0)) if li is not None else None, "pests": pests.get(camis),
                     "dohmh_closed": closed.get(camis).strftime("%Y-%m-%d") if camis in closed.index else None,
                     "dohmh_reopened": reopened.get(camis).strftime("%Y-%m-%d") if camis in reopened.index else None})
    return rows


def _nysdoh(through):
    n = pd.read_csv(f"{OFF}/nysdoh_last.csv", dtype=str)
    n = n[n.description.isin(NYSDOH_KEEP)].fillna("")
    h = pd.read_csv(f"{OFF}/nysdoh_hist.csv", dtype=str, usecols=["nys_health_operation_id", "date_of_inspection", "total_critical_violations",
                                                                  "total_crit_not_corrected", "total_noncritical_violations", "inspection_type"])
    h["d"] = pd.to_datetime(h.date_of_inspection)
    for c in ("total_critical_violations", "total_crit_not_corrected", "total_noncritical_violations"):
        h[c] = pd.to_numeric(h[c], errors="coerce").fillna(0).astype(int)
    h = h[h.d <= through].drop_duplicates(["nys_health_operation_id", "date_of_inspection"]).sort_values("d")
    hist = {k: [[r.d.strftime("%Y-%m-%d"), r.total_critical_violations, r.total_crit_not_corrected,
                 r.total_noncritical_violations] for r in g.itertuples()][-6:] for k, g in h.groupby("nys_health_operation_id")}
    rows = []
    for _, r in n.iterrows():
        la, lo = _pt(r.location1)
        name = r.facility or r.operation_name
        d = pd.Timestamp(r.date) if r.date else None
        if d is not None and d > pd.Timestamp(through):   # a newer inspection than the cut-off: use the last one before it, if any
            prev = [x for x in hist.get(r.nys_health_operation_id, []) if x[0] <= through]
            d = pd.Timestamp(prev[-1][0]) if prev else None
            cr = prev[-1][1:] if prev else [None, None, None]
        else:
            cr = [int(r.total_critical_violations or 0), int(r.total_crit_not_corrected or 0), int(r.total_noncritical_violations or 0)]
        rows.append({"jur": "nysdoh", "lic": "NYSDOH-" + r.nys_health_operation_id, "name": name, "keys": _names(name, r.permitted_d_b_a),
                     "addr": r.address, "city": canon_city(r.city), "municipality": canon_city(r.municipality),
                     "county": (r.county or "").title().replace("St Lawrence", "St. Lawrence"), "zip": (r.zip_code or "")[:5],
                     "kind": NYSDOH_KEEP[r.description], "cred": r.description.split(" - ")[-1], "active": True, "since": None,
                     "lat": la if _ok(la, lo) else np.nan, "lon": lo if _ok(la, lo) else np.nan,
                     "last_insp": d.strftime("%Y-%m-%d") if d is not None else None, "insp_type": r.inspection_type,
                     "crit": cr[0], "crit_nc": cr[1], "noncrit": cr[2], "lhd": (r.local_health_department or "").replace("  ", " "),
                     "hist": hist.get(r.nys_health_operation_id), "permit_exp": (r.permit_expiration_date or "")[:10] or None})
    return rows


def _suffolk():
    s = json.load(open(f"{OFF}/suffolk_2025.json"))
    by = {}
    for f in s["features"]:
        a = f["attributes"]
        b = by.setdefault(a["Facility_ID"], {"name": a["FACILITY_NAME"], "addr": a["Address"], "city": a["City"], "zip": a["Zip"],
                                              "dates": set(), "n": 0, "geo": f.get("geometry")})
        b["n"] += 1
        if a.get("Inspection_Date"):
            b["dates"].add(pd.Timestamp(a["Inspection_Date"], unit="ms", tz="UTC").tz_convert("America/New_York").strftime("%Y-%m-%d"))
    rows = []
    for fid, b in by.items():
        g = b["geo"]
        la, lo = _merc(g["x"], g["y"]) if g and g.get("x") else (np.nan, np.nan)
        rows.append({"jur": "suffolk", "lic": "SCDHS-" + fid, "name": b["name"], "keys": _names(b["name"]), "addr": b["addr"],
                     "city": canon_city(b["city"]), "county": "Suffolk", "zip": (b["zip"] or "")[:5], "kind": "food", "cred": None, "active": True,
                     "since": None, "lat": la if _ok(la, lo) else np.nan, "lon": lo if _ok(la, lo) else np.nan,
                     "sf_n": b["n"], "sf_insp": len(b["dates"]), "last_insp": max(b["dates"]) if b["dates"] else None})
    return rows


def _buffalo():
    b = pd.read_csv(f"{OFF}/buffalo.csv", dtype=str)
    b = b[b.licstatus.eq("Active")].fillna("")
    rows = []
    for _, r in b.iterrows():
        la, lo = pd.to_numeric(r.latitude, errors="coerce"), pd.to_numeric(r.longitude, errors="coerce")
        dba = r.dbaname if r.dbaname and not ENTITY_RX.search(r.dbaname) else None   # mostly blank or a legal entity: never shown
        rows.append({"jur": "buffalo", "lic": "BUF-" + str(r.licenseno), "name": dba, "keys": _names(dba), "addr": r.address,
                     "city": "Buffalo", "county": "Erie", "zip": (r.zip or "")[:5], "kind": "food", "cred": r.descript, "active": True,
                     "since": (r.licensedttm or "")[:10] or None, "lat": la if _ok(la, lo) else np.nan, "lon": lo if _ok(la, lo) else np.nan})
    return rows


def _sla():
    rows = []
    for path, active in ((f"{OFF}/sla_active.csv", True), (f"{OFF}/sla_inactive.csv", False)):
        s = pd.read_csv(path, dtype=str)
        s.columns = [c.replace("_", "") for c in s.columns]   # the inactive file spells columns with underscores
        s = s[s.description.isin(SLA_KIND)].fillna("")
        for _, r in s.iterrows():
            la, lo = _pt(r.georeference)
            rows.append({"jur": "sla", "lic": "SLA-" + str(r.licensepermitid), "name": r.dba if isinstance(r.dba, str) and r.dba.strip() else None,
                         "keys": _names(r.dba), "addr": r.actualaddressofpremises, "city": canon_city(r.city),
                         "county": (r.premisescounty or "").title().replace("St Lawrence", "St. Lawrence"), "zip": (r.zipcode or "")[:5],
                         "kind": SLA_KIND[r.description], "cred": r.description, "active": active,
                         "since": (r.originalissuedate or "")[:10] or None, "expires": (r.expirationdate or "")[:10] or None,
                         "lat": la if _ok(la, lo) else np.nan, "lon": lo if _ok(la, lo) else np.nan, "parent": r.get("parentlicenseid")})
    return rows


def load(cache=True):
    path = f"{NY}/official.pkl"
    srcs = [f"{OFF}/{f}" for f in ("dohmh.csv", "nysdoh_last.csv", "suffolk_2025.json", "buffalo.csv", "sla_active.csv")]
    if cache and os.path.exists(path) and os.path.getmtime(path) > max([os.path.getmtime(f) for f in srcs] + [os.path.getmtime(__file__)]):
        return pd.read_pickle(path)
    thr = records_through()
    df = pd.DataFrame(_dohmh(thr["dohmh"]) + _nysdoh(thr["nysdoh"]) + _suffolk() + _buffalo() + _sla())
    df["num"], df["street"] = zip(*[street_key(a) if isinstance(a, str) and re.match(r"\s*\d", a) else (None, None) for a in df.addr])
    # one business can hold several records (a DOHMH permit and a liquor license, a renewal under a new number): same address, a name in common
    parent = list(range(len(df)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    key_town = (df.county.fillna("") + "|" + df.zip.fillna("")).tolist()
    keys = df["keys"].tolist()
    groups = {}
    for i, (kt, num, st) in enumerate(zip(key_town, df.num, df.street)):
        if num and st:
            groups.setdefault((kt, num, st), []).append(i)
    for idx in groups.values():
        for a in range(len(idx)):
            for b in range(a + 1, len(idx)):
                ka, kb = keys[idx[a]], keys[idx[b]]
                if any(name_sim(x, y) >= 85 or ((_stems(x) - GENERIC) & (_stems(y) - GENERIC)) for x in ka for y in kb):
                    ra, rb = find(idx[a]), find(idx[b])
                    if ra != rb:
                        parent[rb] = ra
    df["biz"] = [find(i) for i in range(len(df))]
    df.attrs["through"] = thr
    df.to_pickle(path)
    json.dump(thr, open(f"{NY}/records_through.json", "w"))
    return df


if __name__ == "__main__":
    df = load(cache=False)
    print("records through:", df.attrs.get("through"))
    a = df[df.active]
    print("records:", len(df), "| active:", len(a), "| with coordinates:", f"{a.lat.notna().mean():.1%}", "| with a name:", f"{a.name.notna().mean():.1%}")
    print(a.groupby(["jur", "kind"]).agg(n=("lic", "size"), placed=("lat", lambda s: round(s.notna().mean(), 3))).to_string())
    print("active on-premise liquor businesses:", a[(a.jur == "sla") & a.kind.isin(ON_PREMISE)].biz.nunique())
    print("DOHMH grades:", a[a.jur == "dohmh"].grade.value_counts(dropna=False).to_dict())
