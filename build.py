#!/usr/bin/env python3
"""Build the Luton Accountants funnel from config.json + src/funnel.html.

Outputs (in ./dist):
  elementor-html-widget.html  -> paste into ONE Elementor "HTML" widget
  elementor-template.json     -> or import via Elementor > Templates > Import
  preview.html                -> open in a browser to preview locally

Usage: python3 build.py
"""
import datetime
import html
import json
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
cfg = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
tpl = (ROOT / "src" / "funnel.html").read_text(encoding="utf-8")
e = lambda s: html.escape(str(s), quote=True)

# ---------- Icons ----------
def stroke(paths):
    return ('<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + paths + "</svg>")

ICONS = {
    "ICON_WA": '<svg class="ico" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/></svg>',
    "ICON_PHONE": stroke('<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92z"/>'),
    "ICON_CHECK": stroke('<polyline points="20 6 9 17 4 12"/>'),
    "ICON_CAL": stroke('<rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>'),
    "ICON_LOCK": stroke('<rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>'),
    "ICON_PIN": stroke('<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>'),
    "ICON_MAIL": stroke('<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 6-10 7L2 6"/>'),
    "ICON_CLOCK": stroke('<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>'),
}

# ---------- Pricing cards ----------
cards = []
for p in cfg["plans"]:
    pop = bool(p.get("popular"))
    feats = "".join(f'<li>{ICONS["ICON_CHECK"]}<span>{e(f)}</span></li>' for f in p["features"])
    cards.append(
        f'<div class="plan{" pop" if pop else ""}">'
        + ('<span class="badge">Most popular</span>' if pop else "")
        + f'<h3>{e(p["name"])}</h3><p class="tag">{e(p["tagline"])}</p>'
        f'<div class="price"><span class="from">from</span><span class="amt">£{e(p["price"])}</span><span class="unit">{e(p["unit"])}</span></div>'
        f'<ul>{feats}</ul>'
        f'<a class="btn {"btn-amber" if pop else "btn-navy"}" href="#book" data-plan="{e(p["name"])}" data-laf-track="plan_{e(p["id"])}">{e(p["cta"])}</a>'
        "</div>"
    )

extra_services = ["VAT returns", "Payroll", "Bookkeeping", "CIS returns", "Company formation", "Not sure yet"]
plan_options = "".join(f'<option value="{e(n)}">{e(n)}</option>' for n in [p["name"] for p in cfg["plans"]] + extra_services)

calc = cfg["calculator"]
default_type = "sole" if any(t["id"] == "sole" for t in calc["types"]) else calc["types"][0]["id"]
calc_types = "".join(
    f'<option value="{e(t["id"])}"{" selected" if t["id"] == default_type else ""}>{e(t["label"])}</option>' for t in calc["types"]
)
calc_turnover = "".join(
    f'<label class="chip"><input type="radio" name="laf-turnover" value="{i}"{" checked" if i == 0 else ""}><span>{e(b["label"])}</span></label>'
    for i, b in enumerate(calc["turnover"])
)

# ---------- Reviews ----------
reviews = cfg.get("reviews") or []
if reviews:
    items = "".join(
        f'<figure class="review"><div class="stars" aria-label="5 out of 5 stars">★★★★★</div>'
        f'<blockquote>“{e(r["quote"])}”</blockquote><figcaption class="who">{e(r["name"])}<span>{e(r["detail"])}</span></figcaption></figure>'
        for r in reviews
    )
    gr = cfg.get("google_reviews_url")
    gr_html = (f'<p class="gr"><a class="btn btn-outline" href="{e(gr)}" target="_blank" rel="noopener" data-laf-track="google_reviews">Read our Google reviews →</a></p>' if gr else "")
    reviews_section = (
        '  <!-- ============ REVIEWS (use genuine reviews only) ============ -->\n'
        '  <section id="reviews"><div class="wrap"><div class="center"><span class="eyebrow">Reviews</span>'
        '<h2 class="h2">What Luton clients say</h2></div>'
        f'<div class="reviews">{items}</div>{gr_html}</div></section>'
    )
else:
    reviews_section = ""

# ---------- FAQ ----------
faq_items = "".join(
    f'<details{" open" if i == 0 else ""}><summary>{e(f["q"])}</summary><div class="ans"><p>{e(f["a"])}</p></div></details>'
    for i, f in enumerate(cfg["faqs"])
)

# ---------- Optional online booking link (Calendly etc.) ----------
booking_link = ""
if cfg.get("booking_url"):
    booking_link = (
        f'          <a class="copt" href="{e(cfg["booking_url"])}" target="_blank" rel="noopener" data-laf-track="book_online">'
        f'<span class="ci cal">{ICONS["ICON_CAL"]}</span><span><b>Pick a time online</b><span>See live availability and book instantly</span></span></a>'
    )

# ---------- Structured data ----------
a = cfg["address"]
schema_local = {
    "@context": "https://schema.org",
    "@type": "AccountingService",
    "@id": cfg["site_url"].rstrip("/") + "/#business",
    "name": cfg["brand"],
    "url": cfg["site_url"],
    "telephone": cfg["phone_e164"],
    "email": cfg["email"],
    "priceRange": "££",
    "currenciesAccepted": "GBP",
    "address": {
        "@type": "PostalAddress",
        "streetAddress": a["street"],
        "addressLocality": a["locality"],
        "addressRegion": a["region"],
        "postalCode": a["postcode"],
        "addressCountry": a["country"],
    },
    "geo": {"@type": "GeoCoordinates", "latitude": cfg["geo"]["lat"], "longitude": cfg["geo"]["lng"]},
    "openingHoursSpecification": [
        {"@type": "OpeningHoursSpecification", "dayOfWeek": h["days"], "opens": h["opens"], "closes": h["closes"]}
        for h in cfg["opening_hours"]
    ],
    "areaServed": [{"@type": "City", "name": n} for n in
                   ["Luton", "Dunstable", "Houghton Regis", "Harpenden", "Leighton Buzzard", "Toddington", "Caddington", "Barton-le-Clay"]],
    "hasOfferCatalog": {
        "@type": "OfferCatalog",
        "name": "Accountancy packages",
        "itemListElement": [
            {
                "@type": "Offer",
                "name": p["name"],
                "description": p["tagline"],
                "priceSpecification": {
                    "@type": "UnitPriceSpecification",
                    "price": p["price"],
                    "priceCurrency": "GBP",
                    **({"unitText": "MONTH"} if "month" in p["unit"] else {}),
                },
            }
            for p in cfg["plans"]
        ],
    },
}
schema_faq = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
        {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in cfg["faqs"]
    ],
}

def js_json(obj):
    # Safe to embed inside <script>
    return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")

runtime_cfg = {
    "brand": cfg["brand"],
    "whatsapp": re.sub(r"\D", "", cfg["whatsapp_number"]),
    "formEndpoint": cfg.get("form_endpoint", ""),
    "calc": calc,
}

sole = next((p for p in cfg["plans"] if p["id"] == "sole-trader"), cfg["plans"][0])
wa_num = re.sub(r"\D", "", cfg["whatsapp_number"])

tokens = {
    **ICONS,
    "BRAND": e(cfg["brand"]),
    "PHONE_DISPLAY": e(cfg["phone_display"]),
    "PHONE_TEL": e(cfg["phone_e164"]),
    "WA_LINK": f"https://wa.me/{wa_num}",
    "EMAIL": e(cfg["email"]),
    "PRIVACY_URL": e(cfg["privacy_url"]),
    "ADDR_STREET": e(a["street"]),
    "ADDR_LOCALITY": e(a["locality"]),
    "ADDR_POSTCODE": e(a["postcode"]),
    "HOURS_TEXT": e(cfg["hours_text"]),
    "RESPONSE": e(cfg["response_promise"]),
    "VAT_NOTE": e(cfg["vat_note"]),
    "ADDONS_TEXT": e(cfg["addons_text"]),
    "FROM_PRICE_SOLE": e(sole["price"]),
    "PRICING_CARDS": "".join(cards),
    "PLAN_OPTIONS": plan_options,
    "CALC_TYPE_OPTIONS": calc_types,
    "CALC_TURNOVER_OPTIONS": calc_turnover,
    "REVIEWS_SECTION": reviews_section,
    "FAQ_ITEMS": faq_items,
    "BOOKING_LINK": booking_link,
    "SCHEMA_LOCAL": js_json(schema_local),
    "SCHEMA_FAQ": js_json(schema_faq),
    "CONFIG_JSON": js_json(runtime_cfg),
    "YEAR": str(datetime.date.today().year),
}

out = tpl
# Expand icons first (they contain no tokens), then everything else.
for _ in range(2):
    out = re.sub(r"\{\{([A-Z_]+)\}\}", lambda m: tokens[m.group(1)] if m.group(1) in tokens else m.group(0), out)
left = re.findall(r"\{\{[A-Z_]+\}\}", out)
if left:
    raise SystemExit(f"Unreplaced tokens: {sorted(set(left))}")

dist = ROOT / "dist"
dist.mkdir(exist_ok=True)
(dist / "elementor-html-widget.html").write_text(out, encoding="utf-8")

# ---------- Preview page ----------
seo_title = f"Accountants in Luton | Fixed Fees from £{sole['price']}/month | {cfg['brand']}"
seo_desc = ("Fixed-fee accountants in Luton for sole traders, landlords & limited companies. Tax returns, "
            "VAT, payroll & CIS. Free switching, fast WhatsApp replies. Get your instant quote.")
preview = f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(seo_title)}</title>
<meta name="description" content="{e(seo_desc)}">
<link rel="canonical" href="{e(cfg['site_url'])}/">
<style>html{{scroll-behavior:smooth}}body{{margin:0;background:#F4F7FB}}</style>
</head>
<body>
{out}
</body>
</html>
"""
(dist / "preview.html").write_text(preview, encoding="utf-8")

# ---------- Elementor template (Templates > Saved Templates > Import) ----------
rid = lambda: "%07x" % random.randrange(16 ** 7)
zero = {"unit": "px", "top": "0", "right": "0", "bottom": "0", "left": "0", "isLinked": True}
template = {
    "version": "0.4",
    "title": f"{cfg['brand']} – Funnel",
    "type": "page",
    "page_settings": {"template": "elementor_canvas"},
    "content": [{
        "id": rid(), "elType": "section", "isInner": False,
        "settings": {"layout": "full_width", "stretch_section": "section-stretched", "gap": "no", "padding": zero, "margin": zero},
        "elements": [{
            "id": rid(), "elType": "column", "isInner": False,
            "settings": {"_column_size": 100, "_inline_size": None, "padding": zero, "margin": zero},
            "elements": [{
                "id": rid(), "elType": "widget", "widgetType": "html", "isInner": False,
                "settings": {"html": out}, "elements": [],
            }],
        }],
    }],
}
(dist / "elementor-template.json").write_text(json.dumps(template, ensure_ascii=False, indent=1), encoding="utf-8")

(dist / "seo-settings.txt").write_text(
    "Paste these into Yoast / Rank Math for this page:\n\n"
    f"SEO title ({len(seo_title)} chars):\n{seo_title}\n\n"
    f"Meta description ({len(seo_desc)} chars):\n{seo_desc}\n\n"
    "Focus keyphrase:\naccountants in Luton\n\n"
    "Secondary keyphrases:\naccountant Luton, tax return Luton, self assessment Luton, "
    "limited company accountant Luton, bookkeeping Luton, accountants Dunstable\n",
    encoding="utf-8",
)

print(f"Built {len(out):,} bytes -> dist/elementor-html-widget.html, dist/elementor-template.json, dist/preview.html, dist/seo-settings.txt")
