"""Download the Overture Maps extract the New York pipeline reads -> data/ny/

- overture_ny.parquet   every place Overture addresses to New York State (any category: restaurants, and the inns, farms, marinas,
                        groceries and gas stations hand-checked places or counters sit in), with the datasets each listing came from

Reads the public Overture bucket over S3 with DuckDB (no account needed). The bounding box is New York State plus a small margin;
`region = 'NY'` keeps New York's own listings (a margin listing from New Jersey or Vermont is dropped here). County outlines come
from the Census (pipeline/fetch_counties.py), not from Overture's divisions.
"""
import os, time
import duckdb

RELEASE = "2026-09-23.1"
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "ny")
BBOX = "bbox.xmin BETWEEN -79.80 AND -71.80 AND bbox.ymin BETWEEN 40.45 AND 45.05"
os.makedirs(OUT, exist_ok=True)

con = duckdb.connect()
con.execute("INSTALL httpfs; LOAD httpfs; INSTALL spatial; LOAD spatial; SET s3_region='us-west-2'; SET threads=4;")
places = f"s3://overturemaps-us-west-2/release/{RELEASE}/theme=places/type=place/*.parquet"

t = time.time()
if not os.path.exists(f"{OUT}/overture_ny.parquet"):
    con.execute(f"""
COPY (
  SELECT id, names.primary AS name, basic_category AS cat, taxonomy.primary AS tax, confidence,
         operating_status AS status, brand.names.primary AS brand, addresses[1].freeform AS street, addresses[1].locality AS city,
         addresses[1].postcode AS zip, addresses[1].region AS region, ST_Y(geometry) AS lat, ST_X(geometry) AS lon, websites[1] AS web,
         phones[1] AS phone, list_transform(sources, x -> x.dataset) AS ds, list_transform(sources, x -> x.update_time) AS ut,
         len(socials) AS n_soc, len(websites) AS n_web, len(phones) AS n_ph
  FROM read_parquet('{places}', hive_partitioning=1) WHERE {BBOX} AND addresses[1].region = 'NY'
) TO '{OUT}/overture_ny.parquet' (FORMAT PARQUET, COMPRESSION ZSTD)""")
    print("places", round(time.time() - t), "s", flush=True)
EAT = "('restaurant','casual_eatery','bar','fast_food_restaurant','coffee_shop','cafe','smoothie_juice_bar','brewery','food_court')"
print(con.execute(f"SELECT count(*), count(*) FILTER (WHERE cat IN {EAT}) FROM '{OUT}/overture_ny.parquet'").fetchall(),
      round(time.time() - t), "s total")
