#!/usr/bin/env python3
"""
Action Point product feed builder (no Shopify apps needed).

Reads the store's public catalog and writes:
  feeds/actionpoint-google-feed.xml   Google Merchant Center / Meta catalogue (RSS 2.0 + g: namespace)
  feeds/actionpoint-products.tsv      the same data as a tab-separated file

Usage:  python3 feeds/build_feed.py            (in-stock variants only)
        python3 feeds/build_feed.py --all      (include sold-out variants as out_of_stock)
The live, always-current version of this feed is the theme template
  /collections/all?view=feed-google   (templates/collection.feed-google.liquid)
"""
import json, sys, time, html, re, urllib.request, os
from xml.sax.saxutils import escape

STORE = "https://actionpoint.sg"
CURRENCY = "SGD"
BRAND_FALLBACK = "Action Point Games"
NM_CONDITION = "new"          # what Near Mint singles are sent as
# Product IDs must match what the Meta pixel reports, or dynamic/retargeting ads lose their match.
#   variant  -> 41234567890123                (Flexify's default, and Google's usual choice)
#   shopify  -> shopify_SG_8123456789_41234567890123   (Shopify's own Facebook channel format)
ID_FORMAT = os.environ.get("FEED_ID_FORMAT", "variant")
COUNTRY = os.environ.get("FEED_COUNTRY", "SG")
MAX_PAGES = int(os.environ.get("FEED_MAX_PAGES", "200"))
INCLUDE_SOLD_OUT = "--all" in sys.argv
OUT = os.environ.get("FEED_OUT") or os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT, exist_ok=True)

def fetch(page):
    url = f"{STORE}/products.json?limit=250&page={page}"
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ActionPointFeedBuilder/1.0"})
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.load(r)["products"]
        except Exception as e:
            time.sleep(2 + attempt * 3)
    raise SystemExit(f"Could not fetch page {page}")

def text(s):
    s = re.sub(r"<[^>]+>", " ", s or "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip()

NO_IMAGE = set()

def item_id(p, v):
    if ID_FORMAT == "shopify":
        return f"shopify_{COUNTRY}_{p['id']}_{v['id']}"
    return str(v["id"])

def rows():
    page = 1
    while page <= MAX_PAGES:
        products = fetch(page)
        if not products: break
        for p in products:
            ptype = p.get("product_type") or ""
            game = "Flesh and Blood" if "Flesh and Blood" in ptype else "Riftbound" if "Riftbound" in ptype else "Trading cards"
            single = "Singles" in ptype
            title = p["title"].replace("(Preorder) ", "", 1)
            desc = text(p.get("body_html"))[:4900] or f"{title} – {p.get('vendor','')} – {game} single from Action Point Games"
            image = (p.get("images") or [{}])[0].get("src", "")
            preorder = "Preorder" in (p.get("tags") or [])
            for v in p["variants"]:
                if not v["available"] and not INCLUDE_SOLD_OUT: continue
                cond = "new"
                if single: cond = NM_CONDITION if "Near Mint" in v["title"] else "used"
                vimg = (v.get("featured_image") or {}).get("src") or image
                if not vimg:
                    NO_IMAGE.add(f"{STORE}/products/{p['handle']}"); continue
                price = float(v["price"])
                was = float(v.get("compare_at_price") or 0)
                yield {
                    "id": item_id(p, v), "item_group_id": str(p["id"]),
                    "title": (title if v["title"] == "Default Title" else f"{title} – {v['title']}")[:150],
                    "description": desc, "link": f"{STORE}/products/{p['handle']}?variant={v['id']}",
                    "image_link": vimg,
                    "availability": "out_of_stock" if not v["available"] else "preorder" if preorder else "in_stock",
                    "price": f"{(was if was > price else price):.2f} {CURRENCY}",
                    "sale_price": f"{price:.2f} {CURRENCY}" if was > price else "",
                    "condition": cond,
                    "brand": p.get("vendor") or BRAND_FALLBACK, "mpn": v.get("sku") or "",
                    "identifier_exists": "no",
                    "google_product_category": "Arts & Entertainment > Hobbies & Creative Arts > Collectibles > Collectible Trading Cards" if single else "Toys & Games > Games > Card Games",
                    "product_type": f"{game} > {p.get('vendor','')}",
                    "custom_label_0": game, "custom_label_1": p.get("vendor") or "",
                    "custom_label_2": "high-end" if price >= 50 else "mid" if price >= 10 else "budget",
                }
        print(f"  page {page}: {len(products)} products", file=sys.stderr)
        page += 1

items = list(rows())
if not items:
    raise SystemExit("No items built; refusing to write an empty feed")
cols = list(items[0].keys())
with open(os.path.join(OUT, "actionpoint-google-feed.xml"), "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:g="http://base.google.com/ns/1.0">\n<channel>\n')
    f.write(f"<title>Action Point Games</title>\n<link>{STORE}</link>\n<description>Action Point Games product feed</description>\n")
    for it in items:
        f.write("<item>\n" + "".join(f"<g:{k}>{escape(v)}</g:{k}>\n" for k, v in it.items() if v) + "</item>\n")
    f.write("</channel>\n</rss>\n")
with open(os.path.join(OUT, "actionpoint-products.tsv"), "w", encoding="utf-8") as f:
    f.write("\t".join(cols) + "\n")
    for it in items:
        f.write("\t".join(it[c].replace("\t", " ").replace("\n", " ") for c in cols) + "\n")
open(os.path.join(OUT, "products-missing-images.txt"), "w").write("\n".join(sorted(NO_IMAGE)) + "\n")
print(f"{len(items)} items written; {len(NO_IMAGE)} products skipped for having no image (see products-missing-images.txt)")
