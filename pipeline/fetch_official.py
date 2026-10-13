"""Official New York records -> data/raw/official/

NYC
- dohmh.csv            DOHMH "New York City Restaurant Inspection Results" (data.cityofnewyork.us 43nn-pn8j, daily). One row per violation,
                       3 years back from each active place's latest inspection. Carries the posted letter grade and its date.
Rest of the state (NYSDOH, health.data.ny.gov; monthly; excludes NYC, Suffolk and Erie)
- nysdoh_last.csv      "Food Service Establishment: Last Inspection" (cnih-y5dw), one row per facility
- nysdoh_hist.csv      "Inspections: Beginning 2005 (ACTIVE)" (2hcc-shji), violation rows since HIST_FROM
- nysdoh_inactive.csv  "Inspections: Beginning 2005 (INACTIVE)" (aaxz-j6pj), one row per closed facility inspected since HIST_FROM
Suffolk
- suffolk_2025.json    "Restaurant Violations: 2025" (opendata.suffolkcountyny.gov ArcGIS layer), violations cited in 2025
Licenses
- sla_active.csv       SLA "Current Liquor Authority Active Licenses" (data.ny.gov 9s3h-dpkz, daily)
- sla_inactive.csv     SLA "Current SLA Inactive Licenses" (6dg3-2z7i), expired or ended since HIST_FROM
- buffalo.csv          City of Buffalo "Restaurant Licenses" (data.buffalony.gov 4pp3-qkuj, public domain)
- agm_ratings.csv      Ag & Markets "Food Safety Inspections - Current Ratings" (d6dy-3h7r): groceries, used only to flag counters
- agm_stores.csv       Ag & Markets "Retail Food Stores" (9a8c-vfzj): groceries, used only to flag counters

Never downloaded: legal and operator names (SLA `legalname`, NYSDOH `permitted_corp_name` and `perm_operator_*`, Buffalo
`businessname`, Ag & Markets `owner_name`/`entity_name`). They can be a person's name and are never shown.

Polite: one request at a time, an honest user agent, paged with $limit/$offset, a pause between pages.
"""
import os, io, csv, json, time, sys
import requests

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "official")
os.makedirs(OUT, exist_ok=True)
S = requests.Session()
S.headers["User-Agent"] = "ny-eats data pipeline (work-with-nick@gmail.com)"
HIST_FROM = "2023-01-01"
ONLY = set(sys.argv[1:])   # e.g. `fetch_official.py dohmh sla_active` refreshes just those


def socrata_csv(host, ds, path, select=None, where=None, group=None, page=50000):
    """Page through a Socrata dataset as CSV and write one file (header once)."""
    off, n, out = 0, 0, None
    with open(path, "w", newline="") as f:
        while True:
            p = {"$limit": page, "$offset": off, "$order": group.split(",")[0] if group else ":id"}
            if select: p["$select"] = select
            if group: p["$group"] = group
            if where: p["$where"] = where
            for attempt in range(4):
                try:
                    r = S.get(f"https://{host}/resource/{ds}.csv", params=p, timeout=300)
                    r.raise_for_status()
                    break
                except requests.RequestException as e:
                    if attempt == 3:
                        raise
                    print("  retry", ds, off, e, flush=True)
                    time.sleep(10 * (attempt + 1))
            rows = list(csv.reader(io.StringIO(r.text)))
            head, body = rows[0], rows[1:]
            if out is None:
                out = csv.writer(f)
                out.writerow(head)
            out.writerows(body)
            n += len(body)
            if len(body) < page:
                return n
            off += page
            time.sleep(1)


def want(name):
    return not ONLY or name in ONLY


JOBS = [
    ("dohmh", "data.cityofnewyork.us", "43nn-pn8j",
     "camis,dba,boro,building,street,zipcode,phone,cuisine_description,inspection_date,action,violation_code,violation_description,"
     "critical_flag,score,grade,grade_date,record_date,inspection_type,latitude,longitude,community_board,council_district,census_tract,bin,bbl,nta",
     None),
    ("nysdoh_last", "health.data.ny.gov", "cnih-y5dw",
     "facility,address,date,violations,total_critical_violations,total_crit_not_corrected,total_noncritical_violations,description,"
     "local_health_department,county,facility_address,city,zip_code,nysdoh_gazetteer_1980,municipality,operation_name,permit_expiration_date,"
     "permitted_d_b_a,nys_health_operation_id,inspection_type,inspection_comments,food_service_facility_state,location1",
     None),
    ("nysdoh_hist", "health.data.ny.gov", "2hcc-shji",
     "nys_health_operation_id,date_of_inspection,inspection_type,violation_item,violation_description,critical_violation,"
     "total_critical_violations,total_crit_not_corrected,total_noncritical_violations,food_service_type,food_service_description,county",
     f"date_of_inspection >= '{HIST_FROM}'"),
    ("nysdoh_inactive", "health.data.ny.gov", "aaxz-j6pj",
     "nys_health_operation_id,operation_name,facility_address,facility_city,facility_postal_zipcode,facility_municipality,county,"
     "food_service_description,permitted_d_b_a,max(date_of_inspection) AS last_inspection,latitude,longitude",
     f"date_of_inspection >= '{HIST_FROM}'"),
    ("sla_active", "data.ny.gov", "9s3h-dpkz",
     "licensepermitid,premisescounty,type,class,description,dba,actualaddressofpremises,additionaladdressinformation,city,statename,zipcode,"
     "originalissuedate,lastissuedate,effectivedate,expirationdate,parentlicenseid,legacyserialnumber,akaaddress,georeference",
     None),
    ("sla_inactive", "data.ny.gov", "6dg3-2z7i",
     "license_permit_id,premises_county,type,class,description,dba,actual_address_of_premises,additional_address_information,city,"
     "state_name,zip_code,original_issue_date,last_issue_date,effective_date,expiration_date,legacy_serial_number,aka_address,georeference",
     f"expiration_date >= '{HIST_FROM}'"),
    ("buffalo", "data.buffalony.gov", "4pp3-qkuj",
     "licenseno,dbaname,code,descript,licensedttm,licstatus,statusdttm,expdttm,issdttm,address,city,state,zip,latitude,longitude,neighborhood",
     None),
    ("agm_ratings", "data.ny.gov", "d6dy-3h7r",
     "county,inspection_grade,inspection_date,establishment_type,trade_name,street,city,zipcode,georeference", None),
    ("agm_stores", "data.ny.gov", "9a8c-vfzj",
     "county,license_number,operation_type,estab_type,dba_name,street_number,street_name,city,zip_code,square_footage,georeference", None),
]

t = time.time()
for name, host, ds, select, where in JOBS:
    if not want(name):
        continue
    if name == "nysdoh_inactive":   # one row per closed facility (its last inspection since HIST_FROM)
        n = socrata_csv(host, ds, f"{OUT}/{name}.csv", select=select, where=where, group="nys_health_operation_id,operation_name,"
                        "facility_address,facility_city,facility_postal_zipcode,facility_municipality,county,food_service_description,"
                        "permitted_d_b_a,latitude,longitude")
    else:
        n = socrata_csv(host, ds, f"{OUT}/{name}.csv", select=select, where=where)
    print(f"{name}: {n:,} rows ({round(time.time() - t)} s)", flush=True)
    time.sleep(1)

# Suffolk County "Restaurant Violations: 2025" (ArcGIS Online item -> its feature layer; paged by resultOffset)
if want("suffolk"):
    ITEM = "a3663c06871e422b9ba6f972bb54a332"
    meta = S.get(f"https://www.arcgis.com/sharing/rest/content/items/{ITEM}", params={"f": "json"}, timeout=60).json()
    url = meta["url"].rstrip("/")
    if not url.split("/")[-1].isdigit():
        url += "/0"
    lay = S.get(url, params={"f": "json"}, timeout=60).json()
    oid = lay.get("objectIdField") or next(f["name"] for f in lay["fields"] if f["type"] == "esriFieldTypeOID")
    feats, off = [], 0
    while True:
        r = S.get(f"{url}/query", params={"where": "1=1", "outFields": "*", "f": "json", "resultOffset": off, "resultRecordCount": 2000,
                                          "orderByFields": oid}, timeout=180)
        r.raise_for_status()
        j = r.json()
        assert "error" not in j, j
        got = j.get("features", [])
        feats += got
        if not got or not j.get("exceededTransferLimit"):
            break
        off += len(got)
        time.sleep(1)
    json.dump({"item": ITEM, "title": meta.get("title"), "modified": meta.get("modified"), "url": url, "fields": j.get("fields"),
               "features": feats}, open(f"{OUT}/suffolk_2025.json", "w"))
    print("suffolk 2025:", len(feats), "rows", meta.get("title"), flush=True)
print("done", round(time.time() - t), "s")
