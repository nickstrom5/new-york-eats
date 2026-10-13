"""New York's counties, towns and cities, and NYC neighborhoods -> data/ny/

Sources (all public domain or open):
- Census cartographic boundary files 2025 (500k, shoreline-clipped): counties (cb_2025_us_county_500k, NY only) and county
  subdivisions (cb_2025_36_cousub_500k: New York's 932 towns, 62 cities and the 5 boroughs).
- NYC Department of City Planning "2020 Neighborhood Tabulation Areas" (NYC Open Data 9nt8-h7nd): neighborhoods, matching DOHMH's `nta`.

Regions are New York State's ten Regional Economic Development Council regions (Empire State Development), by county.

Writes
- ny_counties.geojson   62 counties, full detail, with region
- ny_cousub.geojson     towns/cities/boroughs, full detail, with county and type (town, city, borough)
- ny_places.geojson     Census places (cb_2025_36_place_500k): cities, villages and hamlets (CDPs)
- nta.geojson           NYC neighborhoods (NTA 2020)
- ny_state_detail.geojson  the state outline (for the "outside New York" check)
- ny_shapes.json        simplified state and county outlines for the maps
"""
import os, io, json, zipfile, urllib.request
import duckdb
from shapely import wkb
from shapely.geometry import mapping, shape, Polygon
from shapely.ops import unary_union

NY = os.path.join(os.path.dirname(__file__), "..", "data", "ny")
GEO = os.path.join(NY, "geo")
os.makedirs(GEO, exist_ok=True)
UA = {"User-Agent": "ny-eats data pipeline (work-with-nick@gmail.com)"}

REGIONS = {
    "New York City": ["Bronx", "Kings", "New York", "Queens", "Richmond"],
    "Long Island": ["Nassau", "Suffolk"],
    "Mid-Hudson": ["Dutchess", "Orange", "Putnam", "Rockland", "Sullivan", "Ulster", "Westchester"],
    "Capital Region": ["Albany", "Columbia", "Greene", "Rensselaer", "Saratoga", "Schenectady", "Warren", "Washington"],
    "Mohawk Valley": ["Fulton", "Herkimer", "Montgomery", "Oneida", "Otsego", "Schoharie"],
    "North Country": ["Clinton", "Essex", "Franklin", "Hamilton", "Jefferson", "Lewis", "St. Lawrence"],
    "Central New York": ["Cayuga", "Cortland", "Madison", "Onondaga", "Oswego"],
    "Southern Tier": ["Broome", "Chemung", "Chenango", "Delaware", "Schuyler", "Steuben", "Tioga", "Tompkins"],
    "Finger Lakes": ["Genesee", "Livingston", "Monroe", "Ontario", "Orleans", "Seneca", "Wayne", "Wyoming", "Yates"],
    "Western New York": ["Allegany", "Cattaraugus", "Chautauqua", "Erie", "Niagara"],
}
REGION_OF = {c: r for r, cs in REGIONS.items() for c in cs}
BOROUGH = {"Bronx": "Bronx", "Kings": "Brooklyn", "New York": "Manhattan", "Queens": "Queens", "Richmond": "Staten Island"}


def get(url, dest):
    if not os.path.exists(dest):
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r:
            open(dest, "wb").write(r.read())
    return dest


for name in ("cb_2025_us_county_500k", "cb_2025_36_cousub_500k", "cb_2025_36_place_500k"):
    z = get(f"https://www2.census.gov/geo/tiger/GENZ2025/shp/{name}.zip", f"{GEO}/{name}.zip")
    if not os.path.exists(f"{GEO}/{name}.shp"):
        zipfile.ZipFile(z).extractall(GEO)
get("https://data.cityofnewyork.us/api/geospatial/9nt8-h7nd?method=export&format=GeoJSON", f"{GEO}/nta2020.geojson")

con = duckdb.connect(); con.execute("INSTALL spatial; LOAD spatial;")
rows = con.execute(f"SELECT NAME, GEOID, ST_AsWKB(geom) FROM ST_Read('{GEO}/cb_2025_us_county_500k.shp') WHERE STATEFP = '36' ORDER BY NAME").fetchall()
counties = [(n, g, wkb.loads(bytes(w)).buffer(0)) for n, g, w in rows]
assert len(counties) == 62 and all(n in REGION_OF for n, _, _ in counties), [n for n, _, _ in counties if n not in REGION_OF]
json.dump({"type": "FeatureCollection", "features": [
    {"type": "Feature", "properties": {"county": n, "geoid": g, "region": REGION_OF[n], "borough": BOROUGH.get(n)}, "geometry": mapping(geom)}
    for n, g, geom in counties]}, open(f"{NY}/ny_counties.geojson", "w"))

rows = con.execute(f"SELECT NAME, NAMELSAD, NAMELSADCO, GEOID, ST_AsWKB(geom) FROM ST_Read('{GEO}/cb_2025_36_cousub_500k.shp') ORDER BY GEOID").fetchall()
subs = []
for n, lsad, co, g, w in rows:
    kind = "city" if lsad.endswith(" city") else "borough" if lsad.endswith(" borough") else "town" if lsad.endswith(" town") else lsad.split()[-1]
    subs.append({"type": "Feature", "properties": {"name": n, "kind": kind, "county": co.replace(" County", ""), "geoid": g},
                 "geometry": mapping(wkb.loads(bytes(w)).buffer(0))})
json.dump({"type": "FeatureCollection", "features": subs}, open(f"{NY}/ny_cousub.geojson", "w"))

# Census places: cities, villages and hamlets (census-designated places), so a listing whose mailing name is only its town
# ("Brookhaven", "Islip") can show the hamlet it's in ("Medford", "Bay Shore")
rows = con.execute(f"SELECT NAME, NAMELSAD, GEOID, ST_AsWKB(geom) FROM ST_Read('{GEO}/cb_2025_36_place_500k.shp') ORDER BY GEOID").fetchall()
pl = [{"type": "Feature", "properties": {"name": n, "kind": lsad.split()[-1] if lsad else "", "geoid": g}, "geometry": mapping(wkb.loads(bytes(w)).buffer(0))}
      for n, lsad, g, w in rows]
json.dump({"type": "FeatureCollection", "features": pl}, open(f"{NY}/ny_places.geojson", "w"))
print("census places:", len(pl), {k: sum(1 for f in pl if f["properties"]["kind"] == k) for k in ("city", "village", "CDP")})
nta = json.load(open(f"{GEO}/nta2020.geojson"))
feats = [{"type": "Feature", "properties": {"nta": f["properties"].get("nta2020"), "name": f["properties"].get("ntaname"),
                                            "borough": f["properties"].get("boroname"), "type": f["properties"].get("ntatype")},
          "geometry": f["geometry"]} for f in nta["features"]]
json.dump({"type": "FeatureCollection", "features": feats}, open(f"{NY}/nta.geojson", "w"))


def rings(geom, tol, min_area, holes=False):
    geom = geom.simplify(tol, preserve_topology=True)
    polys = [p for p in getattr(geom, "geoms", [geom]) if p.geom_type == "Polygon" and p.area >= min_area]
    r = lambda ring: [[round(x, 4), round(y, 4)] for x, y in ring.coords]
    if holes:
        return [[r(p.exterior)] + [r(h) for h in p.interiors if abs(Polygon(h).area) >= min_area] for p in polys]
    return [r(p.exterior) for p in polys]


state = unary_union([g for _, _, g in counties]).buffer(0)
json.dump(mapping(state.simplify(0.0003, preserve_topology=True)), open(f"{NY}/ny_state_detail.geojson", "w"))
out = {"state": rings(state, 0.002, 0.00005, holes=True),
       "counties": [{"name": n, "region": REGION_OF[n], "c": rings(geom, 0.003, 0.00005)} for n, _, geom in counties]}
json.dump(out, open(f"{NY}/ny_shapes.json", "w"), separators=(",", ":"))
print("counties:", len(counties), "| county subdivisions:", len(subs), {k: sum(1 for s in subs if s["properties"]["kind"] == k)
      for k in ("town", "city", "borough")}, "| NTAs:", len(feats), "| shapes", os.path.getsize(f"{NY}/ny_shapes.json") // 1024, "KB")
