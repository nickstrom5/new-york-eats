"""QA for the website in docs/: every sitemap page in headless Chrome at phone and desktop widths, served under the same path GitHub
Pages will use (/new-york-eats/ until the custom domain is live).

Page checks: loads with 200, no horizontal scroll, no console errors, no Content-Security-Policy violations, no requests to any other
host, one <h1>, a 50-60 character title and 140-160 character description, valid JSON-LD with no ratings or reviews, no broken
internal links (including #anchors) or images.
Static checks (every page, 404 included): the CSP meta tag first in <head> with a hash per inline script; JSON-LD has no raw "<",
every list item points at its #p- anchor, no empty address, phones are +1 numbers, own sites are sameAs; no "google", no star
characters, no "James Beard finalist", the MICHELIN and James Beard trademark lines; NYSDOH's disclaimer verbatim (and ours) on every
page that shows NYSDOH counts; every NYC grade shown is the place's own official grade with its own date, and every state inspection
date and count is the place's own (checked against docs/data); records-through dates match the data index; Erie places say there is
no inspection data; each guide page lists exactly the hand-checked places of its kinds; website links only where the link check (or
our research) vouches for them.
Web app checks (explore/): each classic guide lists exactly its hand-checked places; the region picker loads a region's file and
lists only that region; "Katz's" finds Katz's Delicatessen and its panel shows its official grade and date; Save survives a reload; a
shared #p= link opens the place on a cold load; a NYSDOH place quotes NYSDOH's disclaimer with its own dates and counts; a Suffolk
place shows "violations cited in 2025"; an Erie place says there's no inspection data; an emoji search lists nothing; Near me sorts by
distance; Back closes a place; the phone panel is a modal dialog and the desktop panel covers no control; search rules shared with the
app ("dim sum in flushing", "pizza near me", "route 9", "bleecker street", "flushing"); a search for a town in another region moves
there; #g=constructor; the skip link; rank numbers only on ranking sorts; Confirmed only / Hide chains keep hand-checked places;
Featured order from outside New York; the map draws the state and the dots, a slow drag opens nothing, stacked dots open a chooser;
no layout shift while the list loads; a dish search ("riggies", "spiedies", "tomato pie") lists that dish and offers the region that
has it; saved places stay under the nye- localStorage prefix (nickstrom5.github.io is shared by every state's site).
Site-wide checks (check_site_seo): nick@eatsranked.com and never the old address in any file under docs/; the "Part of Eats Ranked"
footer line and one #org Organization naming Eats Ranked as its parent on every page; canonical = og:url = the sitemap entry, unique
titles and descriptions; breadcrumbs list real pages only; no "confirmed/verified open"; every root-relative link carries the
github.io path; no CNAME while on github.io; city pages promise nearby classics only when they show them; city and region titles
lead with the guide they have most places on; city "what it eats" pill counts equal what the web search lists; the privacy page
names every key the web app stores; no other state's site, app or repo named in page text, comments or explore.js.
Copy checks (check_copy_claims): one colon per title; ", NY" in titles of cities outside New York City, "Hudson Valley" for Mid-Hudson;
no address repeating its town or carrying a PO box; descriptions keep place names capitalized; "the Bronx"; a claim that each NYC
place carries its grade only where each one does; no "every list works without location"; no "all/every N restaurants".
Web app, Addendum 2: form fields 16px or more on a phone; a junk nye-saved/savedr/guide value doesn't stop the app; no "Nearest"
label before there's a location fix; Near me takes a fresh fix on every tap.
Round 3 (2026-10-12): no website on pipeline/website_blocklist.json (hacked, expired or another business's) anywhere in docs/, and a
missing or empty list fails (check_blocklist); a search inside a guide that finds nothing ("carbone" in Slices) offers "Search all
restaurants" with a count the list then keeps, and one tap finds the place; a famous place in another region ("anchor bar" from New
York City) is offered in its region; the search field's placeholder fits, uncut, at phone widths from 320 to 430 px and at 1280.

Usage: .venv/bin/python scripts/qa-site.py      (serves docs/ itself on a free localhost port; exits 1 on any problem)
  QA_DOCS=<dir>   check another copy of docs/ (used to confirm that each check can fail)
  QA_SHOTS=<dir>  also save a few screenshots there
  QA_PAGES=<n>    check only the first n sitemap pages in the browser (a quick run; the static checks still read every page)
  QA_WIDTHS=1280  only these viewport widths (default 375,1280)
  QA_PORT=<n>     serve on this localhost port (default: any free one)
  QA_BLOCKLIST=<file>  read another website blocklist (used to confirm that check_blocklist fails on a missing or empty one)
Ported from ct-eats/scripts/qa-site.py. Never drives anyone's own browser: headless Chrome only.
"""
import base64
import datetime
import functools
import hashlib
import html as H
import http.server
import json
import math
import os
import re
import sys
import threading
import time
import urllib.parse
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS = os.path.abspath(os.environ.get("QA_DOCS") or os.path.join(ROOT, "docs"))
SHOTS = os.environ.get("QA_SHOTS")
NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
SITEMAP = [e.text for e in ET.parse(os.path.join(DOCS, "sitemap.xml")).getroot().findall("s:url/s:loc", NS)]
HOME = urllib.parse.urlparse(SITEMAP[0])
DOMAIN_HOST = HOME.netloc
BASE = HOME.path.rstrip("/")                        # "/new-york-eats" on github.io, "" on a custom domain
LOWER_EAST_SIDE = {"latitude": 40.7223, "longitude": -73.9874}
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
BANNED_LD = {"aggregateRating", "review", "reviews", "reviewRating", "ratingValue"}
NYSDOH_DISCLAIMER = ("Any use of this data to develop a restaurant grading system is not supported or endorsed by the New York State "
                     "Department of Health.")
NYSDOH_OURS = "Any analyses, interpretations or conclusions here are ours, not NYSDOH's."
MICHELIN_TM = "MICHELIN and the MICHELIN Guide are trademarks of Michelin."
JBF_TM = "James Beard Foundation and James Beard Award are trademarks of the James Beard Foundation."
INIT = """window.__csp = []; window.__cls = 0;
document.addEventListener('securitypolicyviolation', e => window.__csp.push(e.violatedDirective + ' ' + (e.blockedURI || '')));
try { new PerformanceObserver(l => { for (const e of l.getEntries()) if (!e.hadRecentInput) window.__cls += e.value; })
  .observe({type: 'layout-shift', buffered: true}); } catch (e) {}"""
PRIVATE_DIGESTS = {
    "4a7e25559b2ffc162afaef2b1680778c6e77d8c2982c3870595f6ee8fea7a455",
    "ff8ea15b513b5561b1c48b725aff52338eddb8ecdd46af58759e2f2c554b0582",
    "31b7679e2f02e2b0561693acc0c78f067633b6713ac53fb5980dcb0f7c2ea237",
    "928009cbd52e0a32a3542c0f41efa0ac8feef2e05974b8126f26c7d4f9b593e3",
}
CSP_REST = ("style-src 'unsafe-inline'; img-src 'self' data:; connect-src 'self'; manifest-src 'self'; base-uri 'none'; "
            "form-action 'none'; upgrade-insecure-requests")
GUIDE_KINDS = {"new-york-pizza-slices.html": ("slices", ["slice", "buffalo pizza", "tomato pie"]),
               "new-york-bagels-delis.html": ("bagels", ["bagel", "deli", "appetizing"]),
               "buffalo-wings-beef-on-weck.html": ("wings", ["wings", "beef on weck"]),
               "new-york-hots-plates.html": ("hots", ["hots", "plate"]),
               "utica-binghamton-classics.html": ("upstate", ["riggies", "greens", "half-moon", "spiedie"]),
               "new-york-dim-sum.html": ("dimsum", ["dim sum"])}
ICONS_PAGE, OLDEST_PAGE = "new-york-icons.html", "new-york-oldest-restaurants.html"
PANEL_READY = "!document.querySelector('#ex-panel').hidden && document.querySelector('#ex-panel').dataset.ready === '1'"
ENTRY = re.compile(r'<li id="p-([^"]+)"><h3>(.*?)</h3>(.*?)</li>', re.S)   # a full place entry ("listed above" pointers aren't)


class Handler(http.server.SimpleHTTPRequestHandler):
    """Serves DOCS at BASE/, the way GitHub Pages serves the project site; anything outside BASE is a 404."""

    def translate_path(self, path):
        p = urllib.parse.urlsplit(path).path
        if BASE and p != BASE and not p.startswith(BASE + "/"):
            return os.path.join(DOCS, "__not_under_base__")
        return super().translate_path(path[len(BASE):] if BASE else path)

    def log_message(self, *a):
        pass


def serve():
    port = int(os.environ.get("QA_PORT") or 0)   # a fixed port when the machine is shared (each session has its own range)
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), functools.partial(Handler, directory=DOCS))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{srv.server_address[1]}"


def local_file(path):
    path = urllib.parse.unquote(path)
    if BASE and path != BASE and not path.startswith(BASE + "/"):
        return None
    f = os.path.join(DOCS, path[len(BASE):].lstrip("/"))
    if os.path.isfile(f):
        return f
    if os.path.isfile(os.path.join(f, "index.html")):
        return os.path.join(f, "index.html")
    return None


def banned_keys(obj):
    if isinstance(obj, dict):
        return [k for k in obj if k in BANNED_LD] + [x for v in obj.values() for x in banned_keys(v)]
    if isinstance(obj, list):
        return [x for v in obj for x in banned_keys(v)]
    return []


def nice_date(iso):
    y, m, d = iso.split("-")
    return f"{MONTHS[int(m) - 1]} {int(d)}, {y}"


def private_words(text):
    t = text.lower()
    words = set(re.findall(r"[\w.%+-]+@[\w.-]+", t)) | set(re.findall(r"[a-z0-9]+(?:\.[a-z0-9]+)*", t)) | set(re.findall(r"[a-z0-9]+", t))
    return [w for w in words if hashlib.sha256(w.encode()).hexdigest() in PRIVATE_DIGESTS]


# ---------------------------------------------------------------- the web app's data, decoded the way explore.js reads it
def read_cols(d):
    n, C = d["count"], {}
    for k, v in d["cols"].items():
        if isinstance(v, list):
            C[k] = v
            continue
        a, r = [None] * n, 0
        for gap, val in zip(v["i"], v["v"]):
            r += gap
            a[r] = val
        C[k] = a
    lk = lambda t, v: None if v is None else d[t][v]
    rows = []
    for i in range(n):
        g = lambda k: C[k][i] if k in C else None
        gd = g("gd")
        rows.append({"id": g("id"), "n": g("n"), "c": lk("cities", g("c")), "co": g("co"), "cu": lk("cuisines", g("cu")), "t": g("t") or 0,
                     "la": None if g("la") is None else (g("la") + d["la0"]) / 1e5, "lo": None if g("lo") is None else (g("lo") + d["lo0"]) / 1e5,
                     "a": g("a"), "pl": lk("mailing", g("pl")), "hd": lk("hoods", g("hd")), "ch": g("ch") or 1, "v": g("v") == 1, "hc": g("hc") or 0, "k": g("k") or 0, "ip": g("ip"), "f": g("f"),
                     "br": g("br"), "ng": g("ng"), "gd": None if gd is None else (datetime.date(2000, 1, 1) + datetime.timedelta(days=gd)).isoformat(),
                     "ri": g("ri"), "rr": g("rr") if g("rr") is not None else i})
    return rows


class Data:
    def __init__(self):
        dd = os.path.join(DOCS, "data")
        self.ix = json.load(open(os.path.join(dd, "index.json")))
        self.slugs = self.ix["slugs"]
        self.kbit = {k: 1 << i for i, k in enumerate(self.ix["kinds"])}
        self.guides = read_cols(json.load(open(os.path.join(dd, "guides.json"))))
        self.region_rows, self.details = {}, {}
        self.by_id = {}
        for ri, f in enumerate(self.ix["files"]):
            rows = read_cols(json.load(open(os.path.join(dd, f["core"]))))
            det = json.load(open(os.path.join(dd, f["detail"])))
            assert len(det["ids"]) == len(rows) == len(det["d"]), f
            for i, r in enumerate(rows):
                r["id"], r["ri"], r["rr"], r["d"] = det["ids"][i], ri, i, det["d"][i] or {}
                self.by_id[r["id"]] = r
            self.region_rows[ri] = rows
        self.all = [r for ri in sorted(self.region_rows) for r in self.region_rows[ri]]

    def guide_ids(self, kinds):
        mask = sum(self.kbit[k] for k in kinds)
        return {r["id"] for r in self.guides if r["hc"] == 1 and r["k"] & mask and not r["v"]}


def check_static_guides(data, problems):
    """Each guide page lists exactly the hand-checked places of its kinds (a place merely named "... Bagels" is not enough); the
    icons page the honored places; the oldest page the hand-checked places with a year at the same address."""
    pages = {name: data.guide_ids(kinds) for name, (_, kinds) in GUIDE_KINDS.items()}
    pages[ICONS_PAGE] = {r["id"] for r in data.guides if r["ip"] is not None and not r["v"]}
    pages[OLDEST_PAGE] = {r["id"] for r in data.guides if r["f"] is not None and r["hc"] == 1 and not r["v"]}
    for name, want in pages.items():
        f = os.path.join(DOCS, name)
        if not os.path.exists(f):
            problems.append(f"{name}: missing")
            continue
        got = [m.group(1) for m in ENTRY.finditer(open(f).read())]
        if Counter(got) != Counter(want):
            extra = [data.by_id[i]["n"] + ("" if data.by_id.get(i, {}).get("hc") == 1 else " (NOT hand-checked)") for i in set(got) - want if i in data.by_id]
            problems.append(f"{name}: lists {len(got)} places, expected {len(want)} (extra {sorted(extra)[:4]}, "
                            f"missing {sorted(data.by_id[i]['n'] for i in want - set(got))[:4]})")
        if any(data.by_id[i]["hc"] != 1 for i in got if i in data.by_id) and name != ICONS_PAGE:
            problems.append(f"{name}: lists places that aren't hand-checked")


def all_html():
    out = []
    for d, _, files in os.walk(DOCS):
        out += [os.path.join(d, x) for x in files if x.endswith(".html")]
    return sorted(out)


def check_static_pages(data, problems):
    rt = data.ix["records_through"]
    rt_ok = {nice_date(v) for v in rt.values()}
    wc_file = os.path.join(ROOT, "data", "ny", "website_check.json")
    link_ok = json.load(open(wc_file)) if os.path.exists(wc_file) else None   # pipeline/check_websites.py's verdict per link
    vouched = lambda r, href: (link_ok.get(href) or {}).get("ok") if link_ok is not None else (r["hc"] == 1 and r["k"])
    for f in all_html():
        name = os.path.relpath(f, DOCS)
        doc = open(f, encoding="utf-8").read()
        low = doc.lower()
        m = re.search(r"<head>\s*<meta http-equiv=\"Content-Security-Policy\" content=\"([^\"]+)\">", doc)
        scripts = re.findall(r"<script>(.*?)</script>", doc, re.S)
        hashes = " ".join(f"'sha256-{base64.b64encode(hashlib.sha256(x.encode()).digest()).decode()}'" for x in scripts) or "'none'"
        want = f"default-src 'none'; script-src {hashes}; {CSP_REST}"
        if not m:
            problems.append(f"{name}: no Content-Security-Policy meta tag first in <head>")
        elif m.group(1) != want:
            problems.append(f"{name}: CSP is {m.group(1)[:100]!r}…, expected {want[:100]!r}…")
        if re.search(r"<script(?![^>]*application/ld\+json)[^>]*\bsrc=", doc) or re.search(r"\son[a-z]+=\"", doc):
            problems.append(f"{name}: an external script or an inline event handler")
        ids = set(re.findall(r'\bid="([^"]+)"', doc))
        for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', doc, re.S):
            if "<" in raw or ">" in raw:
                problems.append(f"{name}: JSON-LD has a raw < or >")
            try:
                ld = json.loads(raw)
            except ValueError:
                continue
            if ld.get("@type") == "ItemList":
                for it in ld["itemListElement"]:
                    frag = urllib.parse.urlparse(it.get("url", "")).fragment
                    r = it.get("item", {})
                    if not frag.startswith("p-") or frag not in ids or r.get("url") != it.get("url"):
                        problems.append(f"{name}: list item {r.get('name')!r} doesn't point at its #p- entry ({it.get('url')})")
                    if any(v == "" for v in r.get("address", {}).values()):
                        problems.append(f"{name}: {r.get('name')!r} has an empty address field")
                    if "telephone" in r and not re.fullmatch(r"\+1[2-9]\d{9}", r["telephone"]):
                        problems.append(f"{name}: {r.get('name')!r} has telephone {r['telephone']!r}")
                    if "sameAs" in r and urllib.parse.urlsplit(r["sameAs"]).scheme not in ("http", "https"):
                        problems.append(f"{name}: {r.get('name')!r} sameAs {r['sameAs']!r}")
        text = H.unescape(re.sub(r"<[^>]+>", " ", doc))
        for bad in ("James Beard finalist", "Every New York restaurant", "every restaurant in New York", "Garbage Plates"):
            if bad.lower() in text.lower():
                problems.append(f"{name}: says {bad!r}")
        if "google" in low:
            problems.append(f"{name}: mentions Google")
        if "★" in doc or "&#9733;" in doc:
            problems.append(f"{name}: a star character (honors are written out, never stars)")
        if MICHELIN_TM not in doc or JBF_TM not in doc:
            problems.append(f"{name}: no MICHELIN or James Beard trademark line")
        if 'class="insp st-insp' in doc or re.search(r"critical violation", text, re.I):
            if NYSDOH_DISCLAIMER not in H.unescape(doc) or NYSDOH_OURS not in H.unescape(doc):
                problems.append(f"{name}: shows NYSDOH counts without NYSDOH's disclaimer (verbatim) and ours")
        for d in re.findall(r"records through ([A-Z][a-z]{2} \d{1,2}, \d{4})", text):
            if d not in rt_ok:
                problems.append(f"{name}: says records through {d}, but the data says {sorted(rt_ok)}")
        # every inspection result on a static page is the place's own
        for pid, pname, rest in ENTRY.findall(doc):
            r = data.by_id.get(pid)
            if not r:
                problems.append(f"{name}: entry #p-{pid} isn't in the data")
                continue
            g = re.search(r'class="insp nyc-insp"><span class="gb gb-([ABC])"[^>]*>[ABC]</span><span><b>Grade ([ABC]) · graded ([A-Z][a-z]{2} \d{1,2}, \d{4})</b>', rest)
            if 'class="gb gb-' in rest and not g:
                problems.append(f"{name}: {H.unescape(pname)!r} shows a letter grade without 'graded <date>'")
            if g and (g.group(1) != r["ng"] or g.group(2) != r["ng"] or not r["gd"] or g.group(3) != nice_date(r["gd"])):
                problems.append(f"{name}: {H.unescape(pname)!r} shows grade {g.group(1)} graded {g.group(3)}, the data says {r['ng']} {r['gd']}")
            if not g and r["ng"] in ("A", "B", "C"):
                problems.append(f"{name}: {H.unescape(pname)!r} has an official grade in the data that the page doesn't show")
            s = re.search(r'class="insp st-insp"><span><b>Latest state inspection ([A-Z][a-z]{2} \d{1,2}, \d{4})</b><small>(\d+) critical violations?', rest)
            st = r["d"].get("st")
            if s and (not st or s.group(1) != nice_date(st["d"]) or int(s.group(2)) != st["c"]):
                problems.append(f"{name}: {H.unescape(pname)!r} shows a state inspection {s.group(1)} ({s.group(2)} critical); the data says {st}")
            if st and not r["ng"] and not r["d"].get("nyc") and not s:
                problems.append(f"{name}: {H.unescape(pname)!r} has a state inspection in the data that the page doesn't show")
            if data.ix["counties"][r["co"]] == "Erie" and not st and 'erie-insp' not in rest:
                problems.append(f"{name}: {H.unescape(pname)!r} is in Erie County but doesn't say there's no inspection data")
            for href in re.findall(r'<p class="link"><a href="([^"]+)"', rest):
                if not vouched(r, H.unescape(href)):
                    problems.append(f"{name}: {H.unescape(pname)!r} links {href}, which the link check didn't pass")
        if private_words(doc):
            problems.append(f"{name}: contains a private email address or part of one")
        if "M16.4 12.6c0-2.5" in doc:
            problems.append(f"{name}: draws the Apple logo")
        if 'name="twitter:image:alt"' not in doc:
            problems.append(f"{name}: no twitter:image:alt")
        if name == "404.html" and ('rel="canonical"' in doc or 'property="og:url"' in doc):
            problems.append("404.html: has a canonical URL or og:url")
    for p in ("regions/western-new-york.html", "cities/buffalo.html"):
        f = os.path.join(DOCS, p)
        if os.path.exists(f) and "no inspection data" not in H.unescape(open(f).read()):
            problems.append(f"{p}: doesn't say plainly that Erie County has no inspection data here")
    for d, _, files in os.walk(DOCS):   # the data files, license texts, sitemap and manifest are public too
        for x in files:
            if x.endswith((".json", ".txt", ".xml", ".webmanifest")):
                body = open(os.path.join(d, x), encoding="utf-8", errors="replace").read()
                if private_words(body):
                    problems.append(f"{os.path.relpath(os.path.join(d, x), DOCS)}: contains a private email address or part of one")
                if x.endswith(".json") and "google" in body.lower():
                    problems.append(f"{os.path.relpath(os.path.join(d, x), DOCS)}: mentions Google")
    bad = [r["n"] for r in data.all if r["d"].get("w") and not vouched(r, r["d"]["w"])]   # the web app's links, same rule
    if bad:
        problems.append(f"data: {len(bad)} website links the link check didn't pass ({bad[:3]})")


BLOCKLIST = os.path.abspath(os.environ.get("QA_BLOCKLIST") or os.path.join(ROOT, "pipeline", "website_blocklist.json"))


def blocklist_patterns(entries):
    """One case-insensitive pattern per pipeline/website_blocklist.json entry. A "domain" entry matches the domain and every subdomain,
    with or without www. or a scheme ("HTTP://WWW.Example.com", "shop.example.com", "//example.com"), but not a longer name that ends
    the same way ("dellaroccospizza.com" isn't "roccospizza.com"). A "url" entry matches that page with http or https, with or
    without www. and its trailing slash, and nothing else on its (shared) host."""
    out = []
    for b in entries:
        if b.get("match", "domain") == "url":
            u = urllib.parse.urlsplit(b["url"].strip() if "://" in b["url"] else "//" + b["url"].strip())
            host, path = re.escape((u.hostname or "").lower().rstrip(".").removeprefix("www.")), re.escape(u.path.rstrip("/"))
            out.append((b, re.compile(rf"(?<![a-z0-9.-])(?:www\.)?{host}{path}/?(?![a-z0-9/_%-]|\.[a-z0-9])", re.I)))
        else:
            d = re.escape(b["domain"].strip().lower().rstrip(".").removeprefix("www."))
            out.append((b, re.compile(rf"(?<![a-z0-9-])(?:[a-z0-9-]+\.)*{d}(?![a-z0-9-])", re.I)))
    return out


def check_blocklist(problems):
    """No blocklisted website (hacked, expired or another business's; pipeline/website_blocklist.json) anywhere in docs/: pages,
    JSON-LD, the web app's data files, sitemap, manifest. Fails on a missing, empty or malformed list too, so it can't pass by having
    nothing to look for."""
    try:
        entries = json.load(open(BLOCKLIST, encoding="utf-8"))
    except FileNotFoundError:
        problems.append(f"{BLOCKLIST}: missing (make-site.py drops the websites listed there; the link sweep found hacked ones)")
        return
    except ValueError as ex:
        problems.append(f"{BLOCKLIST}: not JSON ({ex})")
        return
    if not isinstance(entries, list) or not entries:
        problems.append(f"{BLOCKLIST}: empty or not a list, so there is nothing to check (New York's sweep found hacked sites)")
        return
    good = []
    for b in entries:
        if not isinstance(b, dict) or not b.get("domain") or b.get("match", "domain") not in ("domain", "url") or not b.get("reason") \
                or (b.get("match") == "url" and not b.get("url")):
            problems.append(f"website_blocklist.json: malformed entry {b!r}")
        else:
            good.append(b)
    pats = blocklist_patterns(good)
    for d, _, files in os.walk(DOCS):
        for x in sorted(files):
            if x.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif", ".ico", ".woff", ".woff2")):
                continue
            raw = open(os.path.join(d, x), encoding="utf-8", errors="replace").read()
            flat = H.unescape(raw.replace("\\/", "/"))   # JSON-escaped slashes and HTML entities read as what they say
            for b, pat in pats:
                hits = pat.findall(flat)
                if hits:
                    problems.append(f"{os.path.relpath(os.path.join(d, x), DOCS)}: publishes the blocklisted website "
                                    f"{b.get('url') if b.get('match') == 'url' else b['domain']} ({b.get('place', '')}; {b['reason'][:60]}) x{len(hits)}")


OLD_EMAIL, EMAIL = "work-with-nick@gmail.com", "nick@eatsranked.com"   # Nick, 2026-10-12: the site's contact is nick@eatsranked.com
FAMILY = 'Part of <a href="https://eatsranked.com/">Eats Ranked</a>, restaurant apps state by state.'
PARENT = {"@type": "Organization", "@id": "https://eatsranked.com/#organization", "name": "Eats Ranked", "url": "https://eatsranked.com/"}
UPSTATE_WORDS = {"Riggies": ["riggies", "greens"], "Spiedies": ["spiedie"], "Half-Moons": ["half-moon"]}
TITLE_WORDS = {"Slices": ["slice", "buffalo pizza", "tomato pie"], "Bagels": ["bagel", "deli", "appetizing"], "Wings": ["wings", "beef on weck"],
               "Hots": ["hots", "plate"], "Dim Sum": ["dim sum"], **UPSTATE_WORDS}


def page_meta(doc):
    title = H.unescape((re.search(r"<title>(.*?)</title>", doc, re.S) or [None, ""])[1])
    desc = H.unescape((re.search(r'<meta name="description" content="([^"]*)"', doc) or [None, ""])[1])
    canon = (re.search(r'<link rel="canonical" href="([^"]+)"', doc) or [None, None])[1]
    og = (re.search(r'<meta property="og:url" content="([^"]+)"', doc) or [None, None])[1]
    return title, desc, canon, og


def check_site_seo(data, problems):
    """The site-wide promises a push depends on: one contact address and never the old one (any file in docs/); every page says it's
    part of Eats Ranked and the Organization names its parent; canonical = og:url = its sitemap entry, unique titles and descriptions;
    breadcrumbs list real pages; no "confirmed/verified open"; city pages claim nearby classics only when they show some, and a
    city's or region's title leads with the guide it has most places on; the web app keeps its storage under its own prefix."""
    for d, _, files in os.walk(DOCS):
        for x in files:
            f = os.path.join(d, x)
            if OLD_EMAIL.encode() in open(f, "rb").read():
                problems.append(f"{os.path.relpath(f, DOCS)}: still has {OLD_EMAIL}")
    if os.path.exists(os.path.join(DOCS, "CNAME")) and BASE:
        problems.append("docs/CNAME exists while the sitemap is on github.io (Pages would forward to a name with no DNS)")
    if not os.path.exists(os.path.join(DOCS, ".nojekyll")):
        problems.append("docs/.nojekyll is missing")
    seen_t, seen_d = defaultdict(list), defaultdict(list)
    sitemap = set(SITEMAP)
    for f in all_html():
        name = os.path.relpath(f, DOCS)
        doc = open(f, encoding="utf-8").read()
        title, desc, canon, og = page_meta(doc)
        text = H.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>", " ", doc, flags=re.S)))
        if FAMILY not in doc:
            problems.append(f"{name}: no 'Part of Eats Ranked' line in the footer")
        if f'href="mailto:{EMAIL}' not in doc:
            problems.append(f"{name}: no mailto:{EMAIL}")
        if re.search(r"\b(confirmed|verified) open\b", text, re.I):
            problems.append(f"{name}: says 'confirmed/verified open' (we checked each place open; we can't confirm it)")
        if BASE and re.search(rf'(?:href|src|srcset)="/(?!{re.escape(BASE.strip("/"))}/)', doc):
            problems.append(f"{name}: a root-relative link without {BASE}/ (it would 404 on github.io)")
        orgs = []
        for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', doc, re.S):
            ld = json.loads(raw)
            for node in ld.get("@graph", [ld]):
                if node.get("@type") == "Organization" and node.get("@id") == f"{HOME.scheme}://{HOME.netloc}{BASE}/#org":
                    orgs.append(node)
        if len(orgs) != 1 or orgs[0].get("parentOrganization") != PARENT:
            problems.append(f"{name}: {len(orgs)} #org Organization nodes; it should be one, naming Eats Ranked as its parent")
        elif orgs[0].get("email") != EMAIL or (orgs[0].get("contactPoint") or {}).get("email") != EMAIL:
            problems.append(f"{name}: the Organization's email isn't {EMAIL}")
        if name == "404.html":
            continue
        seen_t[title].append(name)
        seen_d[desc].append(name)
        want = f"{HOME.scheme}://{HOME.netloc}{BASE}/" + ("" if name == "index.html" else name.removesuffix("index.html"))
        if canon != want or og != want or want not in sitemap:
            problems.append(f"{name}: canonical {canon}, og:url {og}, in sitemap {want in sitemap}; expected {want}")
        for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', doc, re.S):
            ld = json.loads(raw)
            if ld.get("@type") == "BreadcrumbList":
                for it in ld["itemListElement"]:
                    if "#" in it["item"] or not local_file(urllib.parse.urlparse(it["item"]).path):
                        problems.append(f"{name}: breadcrumb item {it['item']} isn't a page of its own")
                if ld["itemListElement"][-1]["item"] != want:
                    problems.append(f"{name}: the last breadcrumb isn't this page")
        if name.startswith("cities/"):
            if ("Classics Nearby" in title or "the nearest ones are below" in text or "the nearest hand-checked classics" in desc) \
                    and 'id="nearby"' not in doc:
                problems.append(f"{name}: promises nearby classics but shows none ({title!r})")
        if name.startswith(("cities/", "regions/")):
            m = re.match(r"(.+?)(?:, NY)? Restaurants(?:: ([A-Za-z -]+?)(?: & ([A-Za-z -]+?))?(?: Guide| &| \||$))?", title)
            place = H.unescape(re.search(r"<h1>(.*?)</h1>", doc).group(1)).split(" restaurants")[0]
            if not m or m.group(1) not in (place, {"Mid-Hudson": "Hudson Valley"}.get(place)):   # what searchers call it
                problems.append(f"{name}: title {title!r} doesn't start with '{place} Restaurants'")
                continue
            if name.startswith("cities/"):
                here = [r for r in data.guides if r["c"] == place and r["hc"] == 1 and not r["v"]]
            else:
                ri = data.ix["slugs"].index(name[len("regions/"):-len(".html")])
                here = [r for r in data.guides if r["ri"] == ri and r["hc"] == 1 and not r["v"]]
            # a title word stands for its whole guide (Spiedies, Riggies or Half-Moons for the Utica & Binghamton guide)
            guide_of = lambda w: ["riggies", "greens", "half-moon", "spiedie"] if w in UPSTATE_WORDS else TITLE_WORDS[w]
            per = {w: sum(1 for r in here if r["k"] & sum(data.kbit[k] for k in guide_of(w))) for w in TITLE_WORDS}
            first = m.group(2)
            if first and first in per and per[first] < max(per.values()):
                problems.append(f"{name}: title leads with {first!r} ({per[first]} places) but the page has more of another guide ({per})")
    for t, ns in seen_t.items():
        if len(ns) > 1:
            problems.append(f"title {t!r} on {len(ns)} pages: {ns[:3]}")
    for d, ns in seen_d.items():
        if len(ns) > 1:
            problems.append(f"description {d[:50]!r}… on {len(ns)} pages: {ns[:3]}")
    js = open(os.path.join(ROOT, "scripts", "explore.js"), encoding="utf-8").read()
    calls = re.findall(r"localStorage\.(?:getItem|setItem|removeItem)\(([^,)]+)", js)
    if not calls or any(not c.strip().startswith('"nye-"') for c in calls) or re.search(r"localStorage\.clear|sessionStorage|document\.cookie", js):
        problems.append(f"explore.js: storage outside the nye- prefix ({calls}); several state sites share nickstrom5.github.io")
    # the FAQPage structured data mirrors the visible questions and answers exactly (Google's rule; the FAQ was rewritten 2026-10-12)
    home = open(os.path.join(DOCS, "index.html"), encoding="utf-8").read()
    squash = lambda t: " ".join(H.unescape(re.sub(r"<[^>]+>", " ", t)).split())
    seen_qa = [(squash(q), squash(a)) for q, a in re.findall(r"<details><summary>(.*?)</summary><p>(.*?)</p></details>", home, re.S)]
    ld_qa = []
    for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', home, re.S):
        ld = json.loads(raw)
        if ld.get("@type") == "FAQPage":
            ld_qa = [(" ".join(x["name"].split()), " ".join(x["acceptedAnswer"]["text"].split())) for x in ld["mainEntity"]]
    if not seen_qa or seen_qa != ld_qa:
        problems.append(f"index.html: the FAQPage JSON-LD doesn't mirror the visible FAQ ({len(seen_qa)} shown, {len(ld_qa)} in JSON-LD; "
                        f"first difference {next(((a, b) for a, b in zip(seen_qa, ld_qa) if a != b), None)})")
    # a city page's "what it eats" pills open the web search filtered to the region, the town and the kind: the count on each pill is
    # what that search lists (a listing named for a town across a county line isn't in that town's region file)
    for f in all_html():
        name = os.path.relpath(f, DOCS)
        if not name.startswith("cities/"):
            continue
        doc = open(f, encoding="utf-8").read()
        sec = re.search(r'<section id="cuisines">(.*?)</section>', doc, re.S)
        for href, label, n in re.findall(r'<a href="([^"]+)">([^<]+) \(([\d,]+)\)</a>', sec.group(1) if sec else ""):
            h = urllib.parse.parse_qs(urllib.parse.urlparse(H.unescape(href)).fragment)
            ri = data.ix["slugs"].index(h["r"][0])
            got = sum(1 for r in data.region_rows[ri] if not r["v"] and r["c"] == h["town"][0] and r["cu"] == h["kind"][0])
            if got != int(n.replace(",", "")):
                problems.append(f"{name}: the {H.unescape(label)!r} pill says {n}, the web search lists {got}")
    # the privacy page names everything the web app keeps in the browser (each store.set key, in plain words)
    said = {"saved": "the places you save", "savedr": "the region each saved place is in", "guide": "the last guide you opened"}
    privacy = H.unescape(re.sub(r"<[^>]+>", " ", open(os.path.join(DOCS, "privacy.html"), encoding="utf-8").read()))
    for k in sorted(set(re.findall(r'store\.set\("([^"]+)"', js))):
        if k not in said or said[k] not in " ".join(privacy.split()):
            problems.append(f"privacy.html: doesn't say the web app keeps {k!r} in the browser ({said.get(k, 'no wording for it yet')})")
    # each state's site stands on its own (App Store 4.3(a)): no other state's app, repo or name in page text, comments or scripts;
    # a place's own name or address ("402 Connecticut St", "California Brew Haus", Florida, NY) is fine, so place entries, place
    # data and structured data are left out
    other = re.compile(r"\b(Wisconsin|Connecticut|Colorado|Florida|California|Washington State|Maine|Idaho|Illinois|Chicago|"
                       r"(?:wi|ct|co|fl|ca|wa|me|id|chi|il)-eats|(?:wisconsin|connecticut|colorado|florida|california|washington|maine|idaho)-eats|"
                       r"(?:ce|we|wae|cae|me|coeats|fleats|ideats)-(?:saved|guide))\b")
    for f in all_html():
        doc = open(f, encoding="utf-8").read()
        doc = re.sub(r'<li id="p-[^"]+">.*?</li>|<li class="again">.*?</li>|<script type="application/ld\+json">.*?</script>', " ", doc, flags=re.S)
        doc = re.sub(r'<section id="(?:streets|cuisines|neighborhoods)">.*?</section>', " ", doc, flags=re.S)   # street and place-kind names
        for m in other.finditer(doc):
            problems.append(f"{os.path.relpath(f, DOCS)}: names another state's site: …{doc[max(0, m.start() - 40):m.end() + 30]!r}…")
    for m in other.finditer(js):
        problems.append(f"explore.js: names another state's site: …{js[max(0, m.start() - 40):m.end() + 30]!r}…")


BOROUGHS = {"Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"}


def check_copy_claims(data, problems):
    """Guards from the 2026-10-12 verification pass: a title has at most one colon; a city outside New York City says ", NY" in its
    title and the Mid-Hudson region goes by "Hudson Valley"; an address never repeats its town or carries a PO box; descriptions keep
    place names capitalized and never say "hand-checked the nearest hand-checked"; "the Bronx", never "in Bronx"; a page that says
    every New York City place carries its grade shows one on each; the FAQ never says every list works without location (Near me
    needs it); no "all/every <N> restaurants" (the copy rule)."""
    for f in all_html():
        name = os.path.relpath(f, DOCS)
        doc = open(f, encoding="utf-8").read()
        title, desc, _, _ = page_meta(doc)
        text = " ".join(H.unescape(re.sub(r"<[^>]+>", " ", re.sub(r"<script.*?</script>|<style.*?</style>", " ", doc, flags=re.S))).split())
        if title.count(":") > 1:
            problems.append(f"{name}: two colons in the title {title!r}")
        if name.startswith("cities/"):
            place = H.unescape(re.search(r"<h1>(.*?)</h1>", doc).group(1)).split(" restaurants")[0]
            if place not in BOROUGHS and not title.startswith(f"{place}, NY "):
                problems.append(f"{name}: title {title!r} doesn't say '{place}, NY' (the name is shared with other states)")
        if name == "regions/mid-hudson.html" and not title.startswith("Hudson Valley Restaurants"):
            problems.append(f"{name}: title {title!r} doesn't use 'Hudson Valley', the name people search for")
        for addr in re.findall(r'<p class="where">(.*?)</p>', doc, re.S) + re.findall(r'"streetAddress":\s*"([^"]*)"', doc):
            a = H.unescape(re.sub(r"<[^>]+>", "", addr))
            if re.search(r"\bP\.?\s?O\.?\s?Box\b", a, re.I) or re.search(r",\s*([A-Z][\w.' -]+?),\s*\1\b", a):
                problems.append(f"{name}: address repeats its town or carries a PO box: {a!r}")
        if re.search(r"hand-checked the\b", desc) or re.search(r"\b(utica|binghamton)\b", desc):
            problems.append(f"{name}: description reads wrong: {desc!r}")
        if re.search(r"\b(in|near|outside) Bronx\b", text):
            problems.append(f"{name}: says 'in Bronx' (it's 'the Bronx')")
        m = re.search(r"\b(?:all|every) (?:of (?:our |the )?)?\d[\d,]* (?:restaurants|places)\b", text, re.I)
        if m:
            problems.append(f"{name}: 'all/every N restaurants' ({m.group(0)!r})")
        if re.search(r"\b(?:Each|Every) New York City place carries\b", text):
            nyc = [li for li in re.findall(r'<li id="p-[0-9a-f]+">(.*?)</li>', doc, re.S)
                   if re.search(r"(Manhattan|Brooklyn|Queens|Bronx|Staten Island)</a></p>", li)]
            bare = [H.unescape(re.search(r"<h3>(.*?)</h3>", li).group(1)) for li in nyc if "nyc-insp" not in li]
            if bare:
                problems.append(f"{name}: says each New York City place carries its grade, but {len(bare)} show none ({bare[:3]})")
        if re.search(r"\b(the|a|an|and|of|in|to|region) \1\b", text, re.I):
            problems.append(f"{name}: a doubled word: {re.search(r'.{0,30}\b(the|a|an|and|of|in|to|region) \1\b.{0,20}', text, re.I).group(0)!r}")
        if re.search(r"each NYC-permitted place with its official letter grade", text):   # thousands have none on file
            problems.append(f"{name}: says each NYC-permitted place has its official grade")
        if name == "index.html" and re.search(r"every list[^.]{0,40}still works?\b", text, re.I):
            problems.append(f"{name}: says every list works without location (Near me needs it)")


# ---------------------------------------------------------------- the web app
def rows(page):
    return page.evaluate("""[...document.querySelectorAll('#ex-list .ex-row')].map(b => ({
        key: b.dataset.key, name: b.querySelector('.ex-name')?.textContent || '', town: b.querySelector('.ex-town')?.textContent || '',
        grade: b.querySelector('.ex-gline')?.textContent || '', metric: b.querySelector('.ex-metric b')?.textContent || ''}))""")


def all_rows(page):
    while page.locator("#ex-more").is_visible():
        page.locator("#ex-more").click()
        page.wait_for_timeout(80)
    return rows(page)


def wait_js(page, expr, timeout=30000, arg=None, every=150):
    """Polls a page expression until it's truthy; False on timeout. Not page.wait_for_function: that evaluates a string predicate
    with eval inside the page, which the site's Content-Security-Policy (rightly, no 'unsafe-eval') blocks, so it threw at once and
    every wait silently became no wait. page.evaluate goes through the DevTools protocol, which the CSP doesn't govern."""
    end = time.time() + timeout / 1000
    while True:
        try:
            ok = page.evaluate(expr, arg) if arg is not None else page.evaluate(expr)
        except Exception:   # the page was between documents
            ok = False
        if ok:
            return True
        if time.time() > end:
            return False
        page.wait_for_timeout(every)


def search(page, text):
    before = page.locator("#ex-count").text_content()
    page.locator("#ex-q").fill(text)
    wait_js(page, "b => document.querySelector('#ex-count').textContent !== b", 4000, arg=before)   # the same count is a fair result too
    page.wait_for_timeout(300)


def close_panel(page):
    if page.locator("#ex-close").count() and page.locator("#ex-close").is_visible():
        page.locator("#ex-close").click()
        page.wait_for_timeout(200)


def pick_guide(page, g):
    page.locator(f'.ex-guides button[data-g="{g}"]').click()
    page.wait_for_timeout(300)


def wait_list(page, timeout=60000):   # a region file can take a while to parse on a busy machine
    ok = wait_js(page, "document.querySelector('#ex-app').getAttribute('aria-busy') === 'false' && "
                       "!/^Loading/.test(document.querySelector('#ex-count').textContent)", timeout)
    page.wait_for_timeout(250)
    return ok


def open_by_key(page, key):
    page.locator(f'#ex-list .ex-row[data-key="{key}"]').click()
    wait_js(page, PANEL_READY)
    page.wait_for_timeout(200)


def check_explore(page, base, width, data, problems, errors):
    where = f"explore @{width}"
    errors.clear()
    ix = data.ix
    key = lambda r: f"{r['ri']}:{r['rr']}"

    def fresh(hash_):
        page.goto("about:blank")
        page.goto(base + BASE + "/explore/#" + hash_, wait_until="networkidle")
        wait_list(page)

    # 0. nothing moves when the data arrives (the controls and the list's space are there from the first paint)
    slow = lambda route: (time.sleep(1), route.continue_())
    page.route("**/data/guides.json", slow)
    page.goto(base + BASE + "/explore/", wait_until="networkidle")
    loaded = wait_js(page, "document.querySelectorAll('#ex-list .ex-row').length > 0", 30000)
    page.unroute("**/data/guides.json", slow)
    if not loaded:
        problems.append(f"{where}: the list never loaded")
        return
    page.wait_for_timeout(500)
    cls = page.evaluate("window.__cls || 0")
    if cls > 0.1:
        problems.append(f"{where}: layout shift while the list loaded (CLS {cls:.3f})")

    # 1. each classic guide, statewide, lists exactly its hand-checked places (by kind; a name alone is not enough)
    for _, (g, kinds) in GUIDE_KINDS.items():
        fresh(f"g={g}&r=all")
        got = {r["key"] for r in all_rows(page)}
        want = {key(r) for r in data.guides if r["id"] in data.guide_ids(kinds)}
        if got != want:
            problems.append(f"{where}: the {g} guide shows {len(got)} places, expected the {len(want)} hand-checked ones")

    # 2. the region picker loads a region's file and lists only that region; the count is the region's restaurants
    fresh("g=all&r=new-york-city")
    wny = ix["slugs"].index("western-new-york")
    reqs = []
    page.on("request", lambda rq: reqs.append(rq.url))
    page.select_option("#ex-region", "western-new-york")
    wait_list(page)
    rs = rows(page)
    want_n = ix["files"][wny]["restaurants"]
    if not any("core-western-new-york.json" in u for u in reqs):
        problems.append(f"{where}: picking Western New York didn't load its file")
    if not rs or any(not r["key"].startswith(f"{wny}:") for r in rs):
        problems.append(f"{where}: Western New York lists places from other regions ({[r['name'] for r in rs if not r['key'].startswith(f'{wny}:')][:3]})")
    if not page.locator("#ex-count").text_content().startswith(f"{want_n:,} places") or "Western New York" not in page.locator("#ex-count").text_content():
        problems.append(f"{where}: Western New York count says {page.locator('#ex-count').text_content()!r}, expected {want_n:,} places")
    if "r=western-new-york" not in page.url:
        problems.append(f"{where}: the region isn't in the URL ({page.url})")

    # 3. "Katz's" finds Katz's Delicatessen in Manhattan; its panel shows the official grade with its date (the data's own)
    fresh("g=all&r=new-york-city")
    search(page, "Katz's")
    katz = [r for r in data.region_rows[0] if r["n"].startswith("Katz's Delicatessen")]
    hits = [r for r in rows(page) if r["name"].startswith("Katz's Delicatessen") and "Manhattan" in r["town"]]
    if not katz:
        problems.append(f"{where}: no Katz's Delicatessen in the New York City data")
    elif not hits:
        problems.append(f"{where}: search \"Katz's\" didn't find Katz's Delicatessen ({[r['name'] for r in rows(page)][:5]})")
    else:
        k0 = katz[0]
        open_by_key(page, hits[0]["key"])
        panel = page.locator("#ex-panel")
        text = panel.inner_text() if panel.is_visible() else ""
        if not text or "Katz's Delicatessen" not in page.locator("#ex-pname").text_content() or "MANHATTAN" not in page.locator(".ex-kicker").text_content() \
                or not panel.locator("a", has_text="Directions").count():
            problems.append(f"{where}: opening Katz's from the search didn't show its details")
        elif k0["ng"] in ("A", "B", "C") and (f"Grade {k0['ng']} · official" not in text or f"Graded {nice_date(k0['gd'])}" not in text):
            problems.append(f"{where}: Katz's panel doesn't show its official grade {k0['ng']} graded {nice_date(k0['gd'])}: {text[:300]!r}")
        if hits[0]["grade"] and k0["ng"] in ("A", "B", "C") and f"graded {nice_date(k0['gd'])}" not in hits[0]["grade"]:
            problems.append(f"{where}: Katz's list row shows {hits[0]['grade']!r}, not its grade date")
        if text:
            # 4. Save, then the Saved guide lists it, also after a reload (localStorage)
            panel.locator("#ex-save").click()
            keys = page.evaluate("Object.keys(localStorage)")   # nickstrom5.github.io is shared by every state's site
            if not keys or any(not k.startswith("nye-") for k in keys):
                problems.append(f"{where}: localStorage keys outside New York's nye- prefix: {keys}")
            close_panel(page)
            pick_guide(page, "saved")
            page.locator("#ex-q").fill("")
            wait_list(page)
            if hits[0]["key"] not in {r["key"] for r in rows(page)}:
                problems.append(f"{where}: a saved place isn't in the Saved guide")
            page.reload(wait_until="networkidle")
            wait_list(page)
            page.wait_for_timeout(800)
            if hits[0]["key"] not in {r["key"] for r in rows(page)}:
                problems.append(f"{where}: a saved place was gone after a reload")
            if SHOTS and width == 375:
                open_by_key(page, hits[0]["key"])
                page.screenshot(path=os.path.join(SHOTS, "site-explore-panel-375.png"))
                close_panel(page)
        # 5. a shared link (#p=<id>) opens the place on a cold load
        fresh(f"g=all&r=new-york-city&p={k0['id']}")
        wait_js(page, PANEL_READY)
        if not page.locator("#ex-panel").is_visible() or not (page.locator("#ex-pname").text_content() or "").startswith("Katz's Delicatessen"):
            problems.append(f"{where}: a #p= link didn't open the place")
        close_panel(page)

    # 6. a NYSDOH place quotes NYSDOH's disclaimer, verbatim, with its own date and counts; no grade anywhere on it
    st_place = next((r for r in data.region_rows[ix["slugs"].index("capital-region")] if r["d"].get("st") and not r["v"] and r["d"]["st"]["c"] >= 1), None)
    sf_place = next((r for r in data.region_rows[ix["slugs"].index("long-island")] if r["d"].get("sf") and not r["v"]), None)
    erie = [r for r in data.region_rows[wny] if ix["counties"][r["co"]] == "Erie" and not r["v"] and not r["d"].get("st")]
    for label, r, need in (("NYSDOH", st_place, lambda r: [NYSDOH_DISCLAIMER, NYSDOH_OURS, "Latest inspection", nice_date(r["d"]["st"]["d"]),
                                                            "Critical violations", "records through " + nice_date(ix["records_through"]["nysdoh"])]),
                           ("Suffolk", sf_place, lambda r: ["Violations cited in 2025", str(r["d"]["sf"]["n"])]),
                           ("Erie", erie[0] if erie else None, lambda r: ["Erie County", "no inspection data"])):
        if not r:
            problems.append(f"{where}: no {label} place in the data to check")
            continue
        fresh(f"g=all&r={ix['slugs'][r['ri']]}&p={r['id']}")
        wait_js(page, PANEL_READY)
        text = page.locator("#ex-panel").inner_text() if page.locator("#ex-panel").is_visible() else ""
        miss = [w for w in need(r) if w not in text]
        if miss:
            problems.append(f"{where}: the {label} place {r['n']!r} panel is missing {miss}: {text[-400:]!r}")
        if label != "NYC" and (re.search(r"\bGrade [ABC]\b", text) or page.locator("#ex-panel .gb").count()):
            problems.append(f"{where}: the {label} place {r['n']!r} shows a letter grade")
        close_panel(page)

    # 7. an emoji (nothing searchable) lists nothing rather than everything
    fresh("g=all&r=new-york-city")
    search(page, "🍕")
    if page.locator("#ex-list .ex-row").count():
        problems.append(f"{where}: an emoji search listed places")

    # 8. Near me sorts by distance from the browser's location (the context is on the Lower East Side)
    fresh("g=near&r=new-york-city")
    page.locator("#ex-locate").click()
    wait_js(page, "document.querySelectorAll('#ex-list .ex-row .ex-metric').length > 0", 60000)
    rs = rows(page)
    if not rs:
        problems.append(f"{where}: Near me: {page.locator('#ex-count').text_content()!r} / {page.locator('#ex-locmsg').text_content()!r} / "
                        f"list {page.evaluate('document.querySelector(`#ex-list`).innerHTML.slice(0, 300)')!r} / "
                        f"view {page.evaluate('[document.querySelector(`#ex-listwrap`).hidden, document.querySelector(`#ex-mapwrap`).hidden, location.hash]')} / errors {errors[:3]}")
    dists = [float(m.group(1)) if (m := re.match(r"([\d.]+) mi", r["metric"])) else None for r in rs[:40]]
    if not rs or None in dists:
        problems.append(f"{where}: Near me listed {len(rs)} places without distances")
    elif dists != sorted(dists) or dists[0] > 0.5:
        problems.append(f"{where}: Near me isn't sorted by distance from the Lower East Side ({dists[:6]})")

    # 9. Back closes an open place and keeps the search; modal on a phone, a side column on a desktop that covers no control
    fresh("g=all&r=new-york-city&q=katz")
    if not wait_js(page, "document.querySelectorAll('#ex-list .ex-row').length > 0", 30000):
        problems.append(f"{where}: the search 'katz' listed nothing ({page.locator('#ex-count').text_content()!r})")
    # (history.length stops at 50 in Chrome, so the new entry is recognized by its state instead)
    if page.evaluate("history.state && history.state.place"):
        problems.append(f"{where}: the list's own history entry claims to be a place")
    if page.locator("#ex-list .ex-row").count():
        open_by_key(page, page.locator("#ex-list .ex-row").first.get_attribute("data-key"))
    if not page.evaluate("history.state && history.state.place") or "p=" not in page.evaluate("location.hash"):
        problems.append(f"{where}: opening a place didn't add a history entry ({page.evaluate('location.hash')})")
    role, modal = page.get_attribute("#ex-panel", "role"), page.get_attribute("#ex-panel", "aria-modal")
    if width <= 600:
        if role != "dialog" or modal != "true" or not page.evaluate("document.getElementById('ex-app').inert && document.querySelector('header.site').inert"):
            problems.append(f"{where}: the open panel isn't a modal dialog with the page behind it inert (role={role}, aria-modal={modal})")
    else:
        if role == "dialog" or page.evaluate("document.querySelectorAll('[inert]').length"):
            problems.append(f"{where}: the side panel is modal on a wide screen")
        covered = page.evaluate("""[...document.querySelectorAll('.ex-guides button, #ex-q, #ex-locate, .ex-row2 select, .ex-row2 input, .ex-view button, header.site nav a')]
            .filter(el => { const r = el.getBoundingClientRect(); if (!r.width || r.bottom > innerHeight) return false;
              return !el.contains(document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2)); })
            .map(el => el.textContent.trim() || el.id)""")
        if covered:
            problems.append(f"{where}: with a place open, the panel covers {covered[:6]}")
    page.go_back()
    page.wait_for_timeout(600)
    if page.locator("#ex-panel").is_visible() or "/explore/" not in page.url or "p=" in page.url or "q=katz" not in page.url:
        problems.append(f"{where}: Back didn't just close the place ({page.url})")
    if page.evaluate("document.querySelectorAll('[inert]').length"):
        problems.append(f"{where}: part of the page stayed inert after the panel closed")

    # 10. search rules shared with the app: stop words go once a tag or place is found, "near me" is dropped, route numbers and
    # street words read alike, a neighborhood or postal name narrows to it
    fresh("g=all&r=new-york-city")

    def result(q):
        search(page, q)
        return page.locator("#ex-count").text_content(), [r["key"] for r in rows(page)][:40]
    for a, b in (("dim sum in flushing", "dim sum flushing"), ("pizza near me", "pizza"), ("bleecker street", "bleecker st"),
                 ("bagels in williamsburg", "bagels williamsburg")):
        ra, rb = result(a), result(b)
        if ra != rb or not ra[1]:
            problems.append(f"{where}: search {a!r} ({ra[0]}) doesn't give the same places as {b!r} ({rb[0]})")
    search(page, "flushing")
    rs = rows(page)
    by_key = {f"{r['ri']}:{r['rr']}": r for r in data.region_rows[0]}
    off = [r["name"] for r in rs if not (by_key[r["key"]]["pl"] == "Flushing" or by_key[r["key"]]["hd"] == "Flushing" or "flushing" in r["name"].lower())]
    if not rs or off:
        problems.append(f"{where}: search 'flushing' isn't the Flushing postal area ({off[:4]})")
    fresh("g=all&r=mid-hudson")   # route numbers, letter suffixes included, read alike: "route 9w" = "us 9w" = "rte 9w"
    for a, b in (("route 59", "ny 59"), ("rte 9w", "us 9w"), ("route 9w", "rte 9w")):
        ra, rb = result(a), result(b)
        if ra != rb or not ra[1]:
            problems.append(f"{where}: search {a!r} ({ra[0]}) doesn't give the same places as {b!r} ({rb[0]})")

    # 11. a search for a town in another region, with nothing here, moves there
    fresh("g=all&r=new-york-city")
    search(page, "plattsburgh")
    wait_list(page)
    cnt = page.locator("#ex-count").text_content()
    rs = rows(page)
    if "North Country" not in cnt or not rs or any("Plattsburgh" not in r["town"] and "plattsburgh" not in r["name"].lower() for r in rs[:20]):
        problems.append(f"{where}: searching 'plattsburgh' from New York City didn't move to the North Country ({cnt!r})")
    fresh("g=all&r=new-york-city")
    search(page, "union square cafe")
    if "New York City" not in page.locator("#ex-count").text_content():
        problems.append(f"{where}: 'union square cafe' left New York City ({page.locator('#ex-count').text_content()!r})")

    # 11b. a dish search lists that dish, not its whole tag ("riggies" in the Finger Lakes once listed Rochester hot dog stands, and
    # in New York City a black and white cookie bakery); where a region has none, it offers the region that has the most
    def dish_ok(key, kind, stem):
        ri, rr = map(int, key.split(":"))
        r = data.region_rows[ri][rr]
        return bool(r["k"] & data.kbit[kind]) or stem in r["n"].lower()
    for region, q, kind, stem in (("finger-lakes", "riggies", "riggies", "riggie"), ("new-york-city", "spiedies", "spiedie", "spiedie"),
                                  ("new-york-city", "tomato pie", "tomato pie", "tomato pie")):
        fresh(f"g=all&r={region}")
        search(page, q)
        wrong = [r["name"] for r in rows(page) if not dish_ok(r["key"], kind, stem)]
        if wrong:
            problems.append(f"{where}: search {q!r} in {region} lists places without it: {wrong[:4]}")
    fresh("g=all&r=new-york-city")
    search(page, "riggies")
    if not page.locator("#ex-allny").count():
        problems.append(f"{where}: 'riggies' in New York City doesn't offer the region that has them")
    else:
        page.locator("#ex-allny").click()
        wait_list(page)
        rs = rows(page)
        if "r=mohawk-valley" not in page.url or not rs or not all(dish_ok(r["key"], "riggies", "riggie") for r in rs):
            problems.append(f"{where}: the riggies button went to {page.url.split('#')[-1]} with {len(rs)} places")
    # the offer names no count it can't keep (only the hand-checked places of other regions are loaded: "See 14" once led to 40), and a
    # regional hot dog with no kind of its own (michigans) isn't sent to the region with the most hot dogs (Rochester's)
    if width > 600:
        fresh("g=all&r=mohawk-valley")
        search(page, "dim sum")
        label = page.locator("#ex-allny").text_content() if page.locator("#ex-allny").count() else ""
        n = re.search(r"\d[\d,]*", label or "")
        if n:
            page.locator("#ex-allny").click()
            wait_list(page)
            got = page.locator("#ex-count").text_content()
            if not got.startswith(n.group(0) + " "):
                problems.append(f"{where}: the dish offer says {label!r} but the search there lists {got!r}")
        fresh("g=all&r=long-island")
        search(page, "michigans")
        if page.locator("#ex-allny").count():
            problems.append(f"{where}: 'michigans' offers {page.locator('#ex-allny').text_content()!r} (a region of other hot dogs)")

    # 11c. (Round 3, ME-V08 / WI-V-03) the web app opens on a guide, and a search there searches only that guide: a famous place on no
    # guide (Carbone, Manhattan) found nothing at all. Now the empty guide offers every restaurant in the region with a count, the
    # directory then lists that many, and one tap finds the place (focus on the first result). A famous place in another region
    # ("anchor bar", Buffalo, from New York City) is offered in its own region.
    on_guides = {r["id"] for r in data.guides}
    carbone = [r for r in data.region_rows[0] if r["n"] == "Carbone" and r["c"] == "Manhattan" and not r["v"]]
    if not carbone or any(r["id"] in on_guides for r in carbone):
        problems.append(f"{where}: pick another famous place on no guide for the guide-search check (Carbone is gone or on a guide now)")
    else:
        fresh("g=slices&r=new-york-city")
        search(page, "carbone")
        offer = page.locator("#ex-list .ex-wide", has_text="in New York City (")
        offered = wait_js(page, "[...document.querySelectorAll('#ex-list .ex-wide')].some(b => /in New York City \\(\\d[\\d,]* match/.test(b.textContent))", 60000)
        label = offer.first.text_content() if offer.count() else ""
        if rows(page):
            problems.append(f"{where}: 'carbone' lists places on the Slices list ({[r['name'] for r in rows(page)][:3]}); pick another query")
        if not offered:
            problems.append(f"{where}: 'carbone' in the Slices guide finds nothing and offers no search of every restaurant "
                            f"({page.locator('#ex-list').inner_text()[:160]!r})")
        else:
            n = re.search(r"\((\d[\d,]*) match", label).group(1)
            offer.first.click()
            wait_list(page)
            wait_js(page, "document.querySelectorAll('#ex-list .ex-row').length > 0 && document.activeElement?.classList.contains('ex-row')", 30000)
            cnt = page.locator("#ex-count").text_content()
            h = urllib.parse.parse_qs(page.url.split("#", 1)[-1])
            if (h.get("g"), h.get("r"), h.get("q")) != (["all"], ["new-york-city"], ["carbone"]):
                problems.append(f"{where}: {label!r} went to #{page.url.split('#', 1)[-1]}, not every New York City restaurant for 'carbone'")
            if not cnt.startswith(f"{n} place"):
                problems.append(f"{where}: the offer said {label!r}, then the directory listed {cnt!r}")
            if not any(r["name"] == "Carbone" and "Manhattan" in r["town"] for r in rows(page)):
                problems.append(f"{where}: one tap on {label!r} didn't find Carbone ({[r['name'] for r in rows(page)][:5]})")
            if not page.evaluate("document.activeElement?.classList.contains('ex-row')"):
                problems.append(f"{where}: after {label!r}, focus isn't on the first result")
    anchor = [r for r in data.region_rows[wny] if r["n"] == "Anchor Bar" and r["c"] == "Buffalo" and r["id"] in on_guides]
    if anchor and not any("anchor bar" in (r["n"] or "").lower() for r in data.region_rows[0]):
        fresh("g=slices&r=new-york-city")
        search(page, "anchor bar")
        if not wait_js(page, "[...document.querySelectorAll('#ex-list .ex-wide')].some(b => /in Western New York/.test(b.textContent))", 60000):
            problems.append(f"{where}: 'anchor bar' from New York City doesn't offer Western New York's restaurants "
                            f"({page.locator('#ex-list').inner_text()[:160]!r})")
        else:
            page.locator("#ex-list .ex-wide", has_text="in Western New York").first.click()
            wait_list(page)
            if "r=western-new-york" not in page.url or "g=all" not in page.url \
                    or not any(r["name"] == "Anchor Bar" and "Buffalo" in r["town"] for r in rows(page)):
                problems.append(f"{where}: the Western New York offer for 'anchor bar' didn't find the Anchor Bar in Buffalo ({page.url.split('#')[-1]})")

    # 11d. (Round 3) the search field's placeholder isn't cut off ("…street, or dis" at 375 px; half of it beside "Use my location" at
    # 414 px). Chrome leaves a placeholder out of scrollWidth, so the field holds the placeholder's own words for a moment (set without
    # an input event, so nothing is searched): wider than the field means cut off. On a phone it stays 16px or more.
    fresh("g=slices&r=new-york-city")
    for w in ((320, 360, 375, 390, 414, 430) if width <= 600 else (width,)):
        page.set_viewport_size({"width": w, "height": 900})
        page.wait_for_timeout(200)
        m = page.evaluate("""() => { const i = document.querySelector('#ex-q'); if (!i || !i.placeholder) return null;
            const v = i.value; i.value = i.placeholder; const over = i.scrollWidth - i.clientWidth; i.value = v;
            return {ph: i.placeholder, over, w: i.clientWidth, fs: parseFloat(getComputedStyle(i).fontSize)}; }""")
        if not m:
            problems.append(f"{where}: the search field has no placeholder")
            break
        if m["over"] > 0:
            problems.append(f"{where}: at {w}px the search placeholder {m['ph']!r} is cut off ({m['over']}px wider than the {m['w']}px field)")
        if w <= 600 and m["fs"] < 16:
            problems.append(f"{where}: at {w}px the search field's text is {m['fs']}px (under 16px, iOS zooms in)")
    page.set_viewport_size({"width": width, "height": 900})

    # 12. a crafted hash (#g=constructor and friends) is just an unknown guide (errors so far are reported first, not dropped)
    problems.extend(f"{where}: console error: {x}" for x in errors)
    errors.clear()
    fresh("g=constructor&r=__proto__&sort=toString")
    if not page.locator("#ex-list .ex-row").count():
        problems.append(f"{where}: #g=constructor shows no list")
    fresh("g=__proto__&r=constructor&q=constructor&kind=hasOwnProperty")
    problems.extend(f"{where}: crafted hash: page error: {x}" for x in errors)
    errors.clear()

    # 13. the skip link moves focus without resetting the search or the filters
    fresh("g=all&r=new-york-city&q=katz&town=Manhattan")
    page.locator("a.skip").focus()
    page.keyboard.press("Enter")
    page.wait_for_timeout(400)
    if page.locator("#ex-q").input_value() != "katz" or "in Manhattan" not in page.locator("#ex-count").text_content():
        problems.append(f"{where}: the skip link reset the web app")

    # 14. rank numbers only on a ranking sort (iconic, oldest); the Icons explainer; no points shown
    fresh("g=icons&r=all")
    if not page.locator(".ex-rank").count() or not page.evaluate("document.querySelector('.ex-rank .sr')?.textContent === 'Rank '"):
        problems.append(f"{where}: the Icons ranking shows no rank numbers")
    if "not a rating" not in page.locator("#ex-sub").text_content():
        problems.append(f"{where}: the Icons guide doesn't say its points aren't a rating")
    if page.evaluate("[...document.querySelectorAll('.ex-metric small')].some(s => /pts/.test(s.textContent))"):
        problems.append(f"{where}: the Icons list shows iconic points")
    fresh("g=all&r=new-york-city")
    if page.locator(".ex-rank").count():
        problems.append(f"{where}: rank numbers on an A to Z list")
    bad_rows = page.evaluate("""[...document.querySelectorAll('.ex-gline')].map(e => e.textContent).filter(t => /Grade [ABC]/.test(t) && !/graded [A-Z][a-z]{2} \\d{1,2}, \\d{4}/.test(t))""")
    if bad_rows:
        problems.append(f"{where}: list rows show a grade without its date ({bad_rows[:2]})")

    # 15. "Confirmed only" keeps hand-checked places; "Hide chains" keeps hand-checked originals
    slices = data.guide_ids(GUIDE_KINDS["new-york-pizza-slices.html"][1])
    fresh("g=slices&r=all&conf=1")
    if len(all_rows(page)) != len(slices):
        problems.append(f"{where}: Confirmed only drops hand-checked slice places ({len(rows(page))} of {len(slices)})")
    fresh("g=slices&r=all&chains=1")
    want = {key(r) for r in data.guides if r["id"] in slices and not (r["ch"] >= 5 and not (r["hc"] == 1 and not r["br"]))}
    if {r["key"] for r in all_rows(page)} != want:
        problems.append(f"{where}: Hide chains on the slices guide shows {len(rows(page))} places, expected {len(want)}")

    # 16. from outside New York the classics stay in Featured order (and a region with none of a guide offers the whole state)
    page.context.set_geolocation({"latitude": 37.7749, "longitude": -122.4194})
    fresh("g=slices&r=new-york-city")
    page.locator("#ex-locate").click()
    if not wait_js(page, "document.querySelector('#ex-locmsg').textContent.includes('outside New York')", 15000):
        problems.append(f"{where}: from outside New York, Use my location didn't say so ({page.locator('#ex-locmsg').text_content()!r})")
    if "Featured first" not in page.locator("#ex-count").text_content():
        problems.append(f"{where}: from outside New York the slices guide isn't in Featured order ({page.locator('#ex-count').text_content()})")
    page.context.set_geolocation(LOWER_EAST_SIDE)
    empty_region = next((sl for sl in ix["slugs"] if not any(r["ri"] == ix["slugs"].index(sl) for r in data.guides if r["id"] in data.guide_ids(["dim sum"]))), None)
    if empty_region:
        fresh(f"g=dimsum&r={empty_region}")
        if not page.locator("#ex-allny").count():
            problems.append(f"{where}: an empty dim sum guide in {empty_region} doesn't offer the whole state")
        else:
            page.locator("#ex-allny").click()
            wait_list(page)
            if len(rows(page)) != len(data.guide_ids(["dim sum"])) or "r=all" not in page.url:
                problems.append(f"{where}: 'See all in New York State' didn't list every dim sum place")

    # 17. the map: the state drawn, gold dots for a guide, a slow drag opens nothing, stacked dots open a chooser
    fresh("g=slices&r=all&view=map")
    page.wait_for_timeout(1200)
    px = page.evaluate("""() => {
        const cv = document.querySelector('#ex-map'); if (!cv || !cv.width) return null;
        const d = cv.getContext('2d').getImageData(0, 0, cv.width, cv.height).data;
        let white = 0, gold = 0;
        for (let i = 0; i < d.length; i += 4) {
          const [r, g, b, a] = [d[i], d[i + 1], d[i + 2], d[i + 3]];
          if (a < 200) continue;
          if (r > 245 && g > 245 && b > 245) white++;
          else if (Math.abs(r - 224) < 26 && Math.abs(g - 165) < 26 && Math.abs(b - 38) < 30) gold++;
        }
        return { total: cv.width * cv.height, white, gold, hint: document.querySelector('#ex-maphint').textContent };
    }""")
    if not px:
        problems.append(f"{where}: the map canvas has no size")
    else:
        if px["white"] < 0.08 * px["total"]:
            problems.append(f"{where}: the map didn't draw New York ({px['white']} of {px['total']} px)")
        if px["gold"] < 40:
            problems.append(f"{where}: the map drew no guide dots ({px['gold']} px)")
        if not px["hint"].startswith(f"{len(slices)} places"):
            problems.append(f"{where}: map hint says {px['hint']!r}, expected {len(slices)} places")
    if SHOTS and width == 375:
        page.screenshot(path=os.path.join(SHOTS, "site-explore-map-375.png"))
    page.evaluate("document.querySelector('#ex-map').scrollIntoView({block: 'center'})")
    page.wait_for_timeout(300)
    one = next(r for r in data.guides if r["id"] in slices)
    xy = page.evaluate("([la, lo]) => { const p = window.NYE_MAP.at(la, lo), b = document.querySelector('#ex-map').getBoundingClientRect(); return p && [b.left + p[0], b.top + p[1]]; }", [one["la"], one["lo"]])
    if xy:
        page.mouse.move(*xy)
        page.mouse.down()
        for k in range(1, 13):
            page.mouse.move(xy[0] + k, xy[1])
            page.wait_for_timeout(25)
        page.mouse.up()
        page.wait_for_timeout(300)
        if page.locator("#ex-panel").is_visible():
            problems.append(f"{where}: a slow drag on the map opened a place")
    stacks = defaultdict(list)
    for r in data.region_rows[0]:
        if not r["v"] and r["a"]:
            stacks[(r["la"], r["lo"], r["a"], r["c"])].append(r)
    by_spot = Counter((r["la"], r["lo"]) for r in data.region_rows[0] if not r["v"])
    group = next((g for g in stacks.values() if 2 <= len(g) <= 4 and by_spot[(g[0]["la"], g[0]["lo"])] == len(g)
                  and len({r["n"] for r in g}) == len(g)), None)
    if group:
        j = group[0]
        fresh("view=map&" + urllib.parse.urlencode({"g": "all", "r": "new-york-city", "town": j["c"], "q": j["a"]}))
        page.evaluate("document.querySelector('#ex-map').scrollIntoView({block: 'center'})")
        page.wait_for_timeout(500)
        xy = page.evaluate("([la, lo]) => { const p = window.NYE_MAP.at(la, lo), b = document.querySelector('#ex-map').getBoundingClientRect(); return p && [b.left + p[0], b.top + p[1]]; }", [j["la"], j["lo"]])
        if xy:
            page.mouse.click(*xy)
            page.wait_for_timeout(500)
        names = page.evaluate("[...document.querySelectorAll('#ex-chooser button')].map(b => b.textContent)")
        if not page.locator("#ex-chooser").is_visible() or not {r["n"] for r in group} <= set(names):
            problems.append(f"{where}: a tap on {len(group)} places at one spot ({j['a']}) didn't list them ({names})")
        else:
            page.locator("#ex-chooser button").first.click()
            wait_js(page, PANEL_READY)
            if not page.locator("#ex-panel").is_visible() or page.locator("#ex-pname").text_content() != names[0]:
                problems.append(f"{where}: picking a place from the map's chooser didn't open it")

    # 18. (Addendum 2, 2026-10-12) on a phone every form field is 16px or more (iOS Safari zooms into a smaller one, WA-14)
    if width <= 600:
        fresh("g=all&r=new-york-city")
        small = page.evaluate("""[...document.querySelectorAll('#ex-app input:not([type=checkbox]), #ex-app select, #ex-app textarea')]
            .map(e => [e.id || e.name || e.tagName, parseFloat(getComputedStyle(e).fontSize)]).filter(([, px]) => px < 16)""")
        if small:
            problems.append(f"{where}: form fields under 16px on a phone (iOS zooms into them): {small}")
    else:
        browser = page.context.browser
        # 19. a stored value of the wrong shape (any site on nickstrom5.github.io can write any key) doesn't stop the app
        for k, v in (("saved", '{"x":1}'), ("saved", "123"), ("saved", "[null, 5, {}]"), ("savedr", "[1,2]"), ("guide", '{"a":1}')):
            ctx2 = browser.new_context(viewport={"width": 1280, "height": 900})
            p2 = ctx2.new_page()
            errs2 = []
            p2.on("pageerror", lambda e: errs2.append(str(e)))
            p2.goto(base + BASE + "/404-check", wait_until="load")
            p2.evaluate("([k, v]) => localStorage.setItem('nye-' + k, v)", [k, v])
            p2.goto(base + BASE + "/explore/", wait_until="networkidle")
            if not wait_js(p2, "document.querySelectorAll('#ex-list .ex-row').length > 0", 20000) or errs2:
                problems.append(f"{where}: with nye-{k} = {v!r} in localStorage the app didn't load ({errs2[:1]})")
            ctx2.close()
        # 20. no location yet (not granted here): the count never claims distance order (WA-13)
        ctx2 = browser.new_context(viewport={"width": 1280, "height": 900})
        p2 = ctx2.new_page()
        for h in ("g=slices&r=new-york-city&sort=nearest", "g=all&r=new-york-city&sort=nearest", "g=near&r=new-york-city"):
            p2.goto("about:blank")
            p2.goto(base + BASE + "/explore/#" + h, wait_until="networkidle")
            wait_list(p2)
            p2.wait_for_timeout(1200)
            cnt = p2.locator("#ex-count").text_content()
            if "Nearest" in cnt:
                problems.append(f"{where}: with no location fix, #{h} says {cnt!r}")
        ctx2.close()
        # 21. Near me asks for a fresh fix on every tap (playbook: a fix from earlier can be miles off): from the Lower East Side,
        # then from downtown Buffalo, tapping Near me again moves to Western New York
        fresh("g=slices&r=new-york-city")
        pick_guide(page, "near")
        wait_js(page, "document.querySelectorAll('#ex-list .ex-row .ex-metric').length > 0", 60000)
        page.context.set_geolocation({"latitude": 42.8864, "longitude": -78.8784})
        pick_guide(page, "slices")
        pick_guide(page, "near")
        moved = wait_js(page, "document.querySelector('#ex-region').value === 'western-new-york' && "
                              "document.querySelectorAll('#ex-list .ex-row .ex-metric').length > 0", 60000)
        if not moved:
            problems.append(f"{where}: tapping Near me again after a move kept the old fix ({page.locator('#ex-count').text_content()!r})")
        page.context.set_geolocation(LOWER_EAST_SIDE)
    problems.extend(f"{where}: console error: {x}" for x in errors)
    problems.extend(f"{where}: CSP violation: {x}" for x in page.evaluate("window.__csp || []"))


def main():
    base = serve()
    pages = [base + urllib.parse.urlparse(u).path for u in SITEMAP]
    if os.environ.get("QA_PAGES"):
        pages = pages[:int(os.environ["QA_PAGES"])]
    data = Data()
    problems = []
    check_static_guides(data, problems)
    check_static_pages(data, problems)
    check_site_seo(data, problems)
    check_copy_claims(data, problems)
    check_blocklist(problems)
    if SHOTS:
        os.makedirs(SHOTS, exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(channel="chrome")
        for width in [int(w) for w in os.environ.get("QA_WIDTHS", "375,1280").split(",")]:
            ctx = browser.new_context(viewport={"width": width, "height": 900}, geolocation=LOWER_EAST_SIDE, permissions=["geolocation"])
            ctx.add_init_script(INIT)
            page = ctx.new_page()
            page.set_default_timeout(30000)
            errors, offsite = [], []
            page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
            page.on("pageerror", lambda e: errors.append(str(e)))
            local = urllib.parse.urlparse(base).netloc
            page.on("request", lambda r: offsite.append(r.url) if urllib.parse.urlparse(r.url).scheme in ("http", "https")
                    and urllib.parse.urlparse(r.url).netloc != local else None)
            for url in pages:
                errors.clear(); offsite.clear()
                try:
                    resp = page.goto(url, wait_until="networkidle")
                except Exception as ex:
                    problems.append(f"{url} @{width}: didn't load ({str(ex).splitlines()[0]})")
                    continue
                path = urllib.parse.urlparse(url).path
                where = f"{path} @{width}"
                if not resp or resp.status != 200:
                    problems.append(f"{where}: HTTP {resp.status if resp else 'no response'}")
                    continue
                over = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
                if over > 1:
                    problems.append(f"{where}: scrolls sideways by {over}px")
                if page.locator("h1").count() != 1:
                    problems.append(f"{where}: {page.locator('h1').count()} <h1>")
                title = page.title()
                desc = page.evaluate("document.querySelector('meta[name=description]')?.content || ''")
                if not 50 <= len(title) <= 60:
                    problems.append(f"{where}: title is {len(title)} characters")
                if not 140 <= len(desc) <= 160:
                    problems.append(f"{where}: description is {len(desc)} characters")
                for raw in page.locator('script[type="application/ld+json"]').all_text_contents():
                    try:
                        bad = banned_keys(json.loads(raw))
                        if bad:
                            problems.append(f"{where}: JSON-LD has ratings or reviews ({sorted(set(bad))})")
                    except ValueError as ex:
                        problems.append(f"{where}: bad JSON-LD ({ex})")
                if width == 1280:   # links are the same at both widths
                    refs = page.evaluate("""[...document.querySelectorAll('a[href],img[src],link[href],script[src],source[srcset]')]
                        .map(e => e.getAttribute('href') || e.getAttribute('src') || e.getAttribute('srcset'))""")
                    cache = {}
                    for ref in refs:
                        full = urllib.parse.urljoin(url, ref)
                        p = urllib.parse.urlparse(full)
                        if p.scheme in ("mailto", "tel", "data"):
                            continue
                        if p.netloc not in (local, DOMAIN_HOST):
                            continue
                        if p.netloc == DOMAIN_HOST and not p.path.startswith(BASE + "/") and p.path != BASE:
                            continue
                        f = local_file(p.path)
                        if not f:
                            problems.append(f"{where}: broken link {ref}")
                        elif p.fragment and "=" not in p.fragment and f.endswith(".html"):
                            if f not in cache:
                                cache[f] = open(f).read()
                            if not re.search(rf'id="{re.escape(p.fragment)}"', cache[f]):
                                problems.append(f"{where}: link to a missing anchor {ref}")
                    imgs = page.evaluate("[...document.images].filter(i => i.complete && i.naturalWidth === 0).map(i => i.src)")
                    problems += [f"{where}: image didn't load {s}" for s in imgs]
                if SHOTS and path in (BASE + "/", BASE + "/new-york-bagels-delis.html", BASE + "/cities/buffalo.html"):
                    name = {BASE + "/": "home", BASE + "/new-york-bagels-delis.html": "bagels", BASE + "/cities/buffalo.html": "buffalo"}[path]
                    page.screenshot(path=os.path.join(SHOTS, f"site-{name}-{width}.png"), full_page=(name != "home"))
                problems += [f"{where}: console error: {x}" for x in errors]
                problems += [f"{where}: CSP violation: {x}" for x in page.evaluate("window.__csp || []")]
                problems += [f"{where}: request to another site: {u}" for u in offsite]
            offsite.clear()
            try:
                check_explore(page, base, width, data, problems, errors)
            except Exception as ex:   # a broken page shouldn't stop the report
                problems.append(f"explore @{width}: the checks stopped: {str(ex).splitlines()[0]}")
            problems += [f"explore @{width}: request to another site: {u}" for u in offsite]
            ctx.close()
        browser.close()
    print(f"{len(pages)} pages × 2 widths + the web app (served at {BASE or '/'} from {DOCS})")
    for p in problems:
        print("  ✗", p)
    print("OK" if not problems else f"{len(problems)} problems")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
