#!/usr/bin/env python3
"""Generates the static Extera site from shared templates. Run: python3 build.py"""
import hashlib
import json
import re
from pathlib import Path

from seo_data import BRAND, SEO, H2_RENAMES, LOCAL_NOTES

OUT = Path(__file__).parent
CSS_VERSION = hashlib.md5((OUT / "assets" / "styles.css").read_bytes()).hexdigest()[:8]  # changes whenever the CSS does, so browsers fetch the new file
PHONE, TEL = "01295 220 600", "01295220600"
EMAIL = "customer.services@extera.co.uk"
ADDR = "10 Manor Park, Banbury, OX16 3TB"
COMPANY_NO = "04299169"  # fill in the Companies House number to show it on the legal pages
ICO_NO = "ZC041870"      # fill in the ICO registration number to show it on the privacy policy
SITE = "Extera Limited"
DOMAIN = "https://www.extera.co.uk"  # change here if the live domain differs
PAGES = []
NOINDEX = {"styleguide.html", "thanks.html"}
FACEBOOK = "https://www.facebook.com/exteralimited"
LINKEDIN = "https://www.linkedin.com/company/exteralimited"
SOCIAL_ICONS = {
    "Facebook": '<path d="M9.101 23.691v-7.98H6.627v-3.667h2.474v-1.58c0-4.085 1.848-5.978 5.858-5.978.401 0 .955.042 1.468.103a8.68 8.68 0 0 1 1.141.195v3.325a8.623 8.623 0 0 0-.653-.036 26.805 26.805 0 0 0-.733-.009c-.707 0-1.259.096-1.675.309a1.686 1.686 0 0 0-.679.622c-.258.42-.374.995-.374 1.752v1.297h3.919l-.386 2.103-.287 1.564h-3.246v8.245C19.396 23.238 24 18.179 24 12.044c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.628 3.874 10.35 9.101 11.647Z"/>',
    "LinkedIn": '<path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>',
}


def social_links():
    items = "".join(
        f'<a href="{url}" rel="noopener" target="_blank" aria-label="Extera on {name} (opens in a new tab)"><svg viewBox="0 0 24 24" aria-hidden="true" fill="currentColor">{SOCIAL_ICONS[name]}</svg></a>'
        for name, url in (("Facebook", FACEBOOK), ("LinkedIn", LINKEDIN)))
    return f'<p class="social">{items}</p>'

NAV = [
    ("Home", "index.html", None),
    ("Phone Systems", "phone-systems.html", [("Phone systems overview", "phone-systems.html"), ("3CX Phone Systems", "3cx.html"), ("8x8 Cloud Phone Systems", "8x8.html"), ("Gamma Horizon", "gamma-horizon.html"), ("Avaya IP Office", "avaya-ip-office.html"), ("3CX vs 8x8", "3cx-vs-8x8.html"), ("Contact Centres", "contact-centres.html")]),
    ("Connectivity", "connectivity.html", [("Connectivity overview", "connectivity.html"), ("Fibre Broadband", "fibre-broadband.html"), ("Leased Lines", "leased-lines.html"), ("MPLS", "mpls.html"), ("SIP Trunks", "sip-trunks.html"), ("Lines and Calls", "business-lines.html"), ("4G/5G Backup", "backup-connectivity.html")]),
    ("Mobile", "mobile.html", None),
    ("Data Cabling", "data-cabling.html", None),
    ("Support", "support.html", None),
    ("Extera Direct", "extera-direct.html", None),
    ("About", "about.html", None),
    ("Contact", "contact.html", None),
]

ICONS = {
    "phone": '<path d="M5 4h4l2 5-2.5 1.5a11 11 0 0 0 5 5L15 13l5 2v4a2 2 0 0 1-2 2A16 16 0 0 1 3 6a2 2 0 0 1 2-2z"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
    "mobile": '<rect x="7" y="2" width="10" height="20" rx="2"/><path d="M11 18h2"/>',
    "cable": '<rect x="9" y="3" width="6" height="6" rx="1"/><rect x="3" y="15" width="6" height="6" rx="1"/><rect x="15" y="15" width="6" height="6" rx="1"/><path d="M12 9v3M6 15v-3h12v3"/>',
    "headset": '<path d="M4 14v-2a8 8 0 0 1 16 0v2"/><rect x="3" y="14" width="4" height="6" rx="1.5"/><rect x="17" y="14" width="4" height="6" rx="1.5"/><path d="M19 20a4 4 0 0 1-4 2h-2"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
    "wrench": '<path d="M14.5 6.5a4 4 0 0 0 5 5L21 13l-8 8-4-4 8-8z" transform="translate(-2 -2)"/><path d="M7 17l-3 3"/>',
    "cart": '<circle cx="9" cy="20" r="1.5"/><circle cx="18" cy="20" r="1.5"/><path d="M2 3h3l2.5 12h11L21 7H6"/>',
    "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2 20a7 7 0 0 1 14 0"/><circle cx="17" cy="9" r="2.5"/><path d="M17 14a5 5 0 0 1 5 5"/>',
    "chat": '<path d="M4 5h16v11H9l-5 4z"/>',
    "cloud": '<path d="M7 18a4.5 4.5 0 0 1-.5-9A6 6 0 0 1 18 9.5 4 4 0 0 1 17.5 18z"/>',
    "server": '<rect x="3" y="4" width="18" height="6" rx="1.5"/><rect x="3" y="14" width="18" height="6" rx="1.5"/><path d="M7 7h.01M7 17h.01"/>',
    "signal": '<path d="M4 20v-3M9 20v-7M14 20V9M19 20V4"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "clip": '<rect x="5" y="4" width="14" height="17" rx="2"/><path d="M9 4h6v3H9zM8 12h8M8 16h5"/>',
    "route": '<circle cx="6" cy="6" r="2.5"/><circle cx="18" cy="18" r="2.5"/><path d="M8.5 6H14a3 3 0 0 1 0 6h-4a3 3 0 0 0 0 6h5.5"/>',
    "building": '<rect x="5" y="3" width="14" height="18" rx="1"/><path d="M9 8h2M13 8h2M9 12h2M13 12h2M9 16h2M13 16h2"/>',
    "bolt": '<path d="M13 2L5 14h6l-1 8 8-12h-6z"/>',
    "headphones": '<path d="M4 15v-3a8 8 0 0 1 16 0v3"/><rect x="3" y="14" width="4" height="7" rx="1.5"/><rect x="17" y="14" width="4" height="7" rx="1.5"/>',
    "wifi": '<path d="M2 9a15 15 0 0 1 20 0M5 12.5a10.5 10.5 0 0 1 14 0M8.5 16a5.5 5.5 0 0 1 7 0"/><circle cx="12" cy="19" r="1"/>',
}


def ico(name):
    return f'<span class="ico"><svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg></span>'


TCX_PAGES = [("3cx.html", "Overview"), ("3cx-apps.html", "Apps"), ("3cx-video-chat.html", "Video and Chat"),
             ("3cx-integrations.html", "Integrations"), ("3cx-ai-analytics.html", "AI and Analytics")]
X8_PAGES = [("8x8.html", "Overview"), ("8x8-voice.html", "Voice and Messaging"), ("8x8-meetings.html", "Meetings"),
            ("8x8-contact-centre.html", "Contact Centre"), ("8x8-integrations.html", "Integrations"), ("8x8-security.html", "Security and Reliability")]
GH_PAGES = [("gamma-horizon.html", "Overview"), ("gamma-horizon-apps.html", "Apps and Collaboration"), ("gamma-horizon-teams.html", "Teams and Webex"),
            ("gamma-horizon-contact.html", "Contact Centre"), ("gamma-horizon-analytics.html", "Analytics and Integrations"), ("gamma-horizon-network.html", "Network and Resilience")]
IPO_PAGES = [("avaya-ip-office.html", "Overview"), ("avaya-ipo-editions.html", "Editions and Scale"), ("avaya-ipo-apps.html", "Apps and Mobility"),
             ("avaya-ipo-contact-centre.html", "Contact Centre"), ("avaya-ipo-resilience.html", "Resilience and Support")]
SYSTEM_OVERVIEWS = {"3cx.html", "8x8.html", "gamma-horizon.html", "avaya-ip-office.html", "3cx-vs-8x8.html", "contact-centres.html"}
TAB_GROUPS = [("3CX", TCX_PAGES), ("8x8", X8_PAGES), ("Gamma Horizon", GH_PAGES), ("Avaya IP Office", IPO_PAGES)]


def subnav(current):
    """Local tab bar shown on the 3CX and 8x8 pages, so the detail pages are reachable without extra menu items."""
    for title, pages in TAB_GROUPS:
        if current in [p[0] for p in pages]:
            links = "".join(f'<li><a href="{h}"{" aria-current=page" if h == current else ""}>{l}</a></li>' for h, l in pages)
            return f'<nav class="subnav" aria-label="{title} sections"><div class="wrap"><span class="subnav-title">{title}</span><ul>{links}</ul></div></nav>'
    return ""


def nav(current):
    items = []
    for label, href, sub in NAV:
        group = [x[1] for x in sub] if sub else []
        if href == "phone-systems.html":  # each system's tabbed pages sit under Phone Systems but are reached from their overview pages
            group += [p[0] for _, pages in TAB_GROUPS for p in pages]
        cur = ' aria-current="page"' if href == current or current in group else ""
        s = ""
        toggle = ""
        if sub:
            s = '<ul class="sub">' + "".join(f'<li><a href="{h}">{l}</a></li>' for l, h in sub) + "</ul>"
            toggle = f'<button class="sub-toggle" type="button" aria-expanded="false" aria-label="Show {label} pages"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg></button>'
        items.append(f'<li{" data-current" if cur else ""}><a href="{href}"{cur}>{label}</a>{toggle}{s}</li>')
    return "\n".join(items)


HERO_LOGOS = {  # key: (file, width, height, tile style)
    "3cx": ("3cx-grey.jpg", 200, 84, "bare"),
    "8x8": ("8x8-dark.svg", 130, 62, ""),
    "gamma": ("gamma.svg", 170, 38, ""),
    "avaya": ("avaya.jpg", 190, 60, ""),
}
HERO_LOGO_PAGES = {}
for _key, _pages in (("3cx", TCX_PAGES), ("8x8", X8_PAGES), ("gamma", GH_PAGES), ("avaya", IPO_PAGES)):
    for _file, _label in _pages:
        HERO_LOGO_PAGES[_file] = [_key]
HERO_LOGO_PAGES["3cx-vs-8x8.html"] = ["3cx", "8x8"]


def hero_logos(fname):
    keys = HERO_LOGO_PAGES.get(fname)
    if not keys:
        return ""
    tiles = ""
    for k in keys:
        f, w, h, style = HERO_LOGOS[k]
        tiles += f'<span class="tile {style}"><img src="assets/logos/{f}" width="{w}" height="{h}" alt=""></span>'
    return f'<div class="hero-logo">{tiles}</div>'


def slugify(text, used):
    base = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "section"
    slug, n = base, 2
    while slug in used:
        slug, n = f"{base}-{n}", n + 1
    used.add(slug)
    return slug


def spec_table(head, rows, first_links=None):
    th = "".join(f'<th scope="col">{h}</th>' for h in head)
    body_rows = ""
    for r in rows:
        body_rows += f'<tr><th scope="row">{r[0]}</th>' + "".join(f"<td>{c}</td>" for c in r[1:]) + "</tr>"
    return f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{body_rows}</tbody></table></div>'


def prepare_body(body, fname):
    """Adds ids to section headings, builds an 'On this page' row for long pages and marks secondary illustrations."""
    used, links = set(), []

    def tag(m):
        label, heading_text = m.group(1), m.group(2)
        slug = slugify(label, used)
        if not (heading_text.startswith("More about") or heading_text.startswith("Explore more") or label == "Related"):
            links.append((label, slug))
        return f'<span class="eyebrow">{label}</span><h2 id="{slug}">{heading_text}</h2>'

    body = re.sub(r'<span class="eyebrow">([^<]+)</span><h2>([^<]*)</h2>', tag, body)
    toc = ""
    if len(links) >= 9:
        chips = "".join(f'<li><a href="#{slug}">{label}</a></li>' for label, slug in links)
        toc = f'<nav class="subnav toc" aria-label="On this page"><div class="wrap"><span class="subnav-title">On this page</span><ul>{chips}</ul></div></nav>'
    # keep the first illustration on a page, and mark the rest so phones can skip them
    first = body.find('<div class="split feature')
    if first != -1:
        head, rest = body[: first + 1], body[first + 1:]
        rest = rest.replace('<div class="split feature', '<div class="split feature secondary')
        body = head + rest
    return toc + body


def apply_seo(fname, title, desc, body):
    key = fname[:-5] if fname.endswith(".html") else fname
    if key in SEO:
        title, desc = SEO[key][0] + BRAND, SEO[key][1]
    for old, new in H2_RENAMES.get(key, {}).items():
        body = body.replace(f"<h2>{old}</h2>", f"<h2>{new}</h2>")
    note = LOCAL_NOTES.get(key)
    if note:
        i = body.find("<h2")
        j = body.find("</p>", i) if i != -1 else -1
        if j != -1:
            body = body[: j + 4] + f"<p>{note}</p>" + body[j + 4:]
    return title, desc, body


def page(fname, title, desc, body, hero=None, crumb=None, jsonld=None):
    title, desc, body = apply_seo(fname, title, desc, body)
    body = prepare_body(body, fname)
    if crumb and fname in SYSTEM_OVERVIEWS:
        crumb = f'<a href="phone-systems.html">Phone Systems</a> / {crumb}'
    crumbs = ""
    if crumb:
        trail = f'<a href="index.html">Home</a> / {crumb}'
        if hero and 'class="hero page-hero"' in hero:
            # the breadcrumb lives inside the banner, so inner pages do not spend a separate row on it
            hero = hero.replace('<div class="wrap">', f'<div class="wrap"><nav class="crumbs-in" aria-label="Breadcrumb">{trail}</nav>', 1)
        else:
            crumbs = f'<div class="crumbs"><div class="wrap">You are here: {trail}</div></div>'
    logo_html = hero_logos(fname)
    if logo_html and hero and 'class="hero page-hero"' in hero:
        hero = hero.replace('<div class="wrap">', '<div class="wrap has-logo' + (' two' if len(HERO_LOGO_PAGES[fname]) > 1 else '') + '">', 1)
        hero = hero[: hero.rindex("</div></section>")] + logo_html + "</div></section>"
    ld = f'<script type="application/ld+json">{json.dumps(jsonld)}</script>' if jsonld else ""
    url = DOMAIN + "/" + ("" if fname == "index.html" else fname)
    if fname not in NOINDEX:
        PAGES.append(url)
    if crumb and fname != "index.html":
        items = [("Home", DOMAIN + "/")]
        parts = crumb.split(" / ")
        for n, p in enumerate(parts):
            name = re.sub(r"<[^>]+>", "", p).strip()
            href = re.search(r'href="([^"]+)"', p)
            items.append((name, url if n == len(parts) - 1 else DOMAIN + "/" + href.group(1) if href else None))
        crumb_ld = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": nm, **({"item": u} if u else {})} for i, (nm, u) in enumerate(items)]}
        ld += f'<script type="application/ld+json">{json.dumps(crumb_ld)}</script>'
    robots = '<meta name="robots" content="noindex, nofollow">\n' if fname in NOINDEX else ""
    social = (f'<link rel="canonical" href="{url}">\n{robots}'
              f'<meta property="og:type" content="website">\n<meta property="og:site_name" content="{SITE}">\n'
              f'<meta property="og:locale" content="en_GB">\n<meta property="og:title" content="{title}">\n'
              f'<meta property="og:description" content="{desc}">\n<meta property="og:url" content="{url}">\n'
              f'<meta property="og:image" content="{DOMAIN}/assets/hero-london.jpg">\n'
              f'<meta name="twitter:card" content="summary_large_image">\n')
    html = f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
{social}<link rel="preload" href="assets/fonts/open-sans-1.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/styles.css?v={CSS_VERSION}">
{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="topbar"><div class="wrap"><span>Business telecoms, Banbury</span><span>Call: <a href="tel:{TEL}">{PHONE}</a></span></div></div>
<header class="site-header"><div class="wrap">
<a class="logo" href="index.html"><img src="assets/extera-logo.png" width="144" height="88" alt="Extera Limited"></a>
<button class="menu-toggle" aria-expanded="false" aria-controls="nav" onclick="exteraMenu(this)">Menu</button>
<nav aria-label="Main"><ul class="nav" id="nav">
{nav(fname)}
</ul></nav>
<a class="btn nav-cta" href="contact.html">Get a quote</a>
</div></header>
{crumbs}
{subnav(fname)}
<main id="main">
{hero or ""}
{body}
</main>
<footer class="site-footer"><div class="wrap">
<div><h3>Solutions</h3><ul>
<li><a href="phone-systems.html">Phone Systems</a></li>
<li><a href="3cx.html">3CX Phone Systems</a></li>
<li><a href="8x8.html">8x8 Cloud Phone Systems</a></li>
<li><a href="gamma-horizon.html">Gamma Horizon</a></li>
<li><a href="avaya-ip-office.html">Avaya IP Office</a></li>
<li><a href="contact-centres.html">Contact Centres</a></li>
<li><a href="connectivity.html">Connectivity</a></li>
<li><a href="mobile.html">Business Mobile</a></li>
<li><a href="data-cabling.html">Data Cabling</a></li>
</ul></div>
<div><h3>Company</h3><ul>
<li><a href="about.html">About Extera</a></li>
<li><a href="support.html">Support</a></li>
<li><a href="extera-direct.html">Extera Direct</a></li>
<li><a href="contact.html">Contact</a></li>
</ul></div>
<div><h3>Contact us</h3>
<p>Phone: <a href="tel:{TEL}">{PHONE}</a><br>Email: <a href="mailto:{EMAIL}">{EMAIL}</a></p>
<p>{ADDR.replace(", ", "<br>")}</p>
<h3 class="follow">Follow us</h3>{social_links()}</div>
<div><h3>Accreditations</h3><div class="accred small"><img src="assets/iso9001.jpg" width="80" height="80" alt="ISO 9001:2015 certified"><img src="assets/chas.jpg" width="114" height="80" alt="CHAS Accredited Contractor"></div></div>
</div>
<div class="socket"><div class="wrap"><span>&copy; Copyright - Extera Limited</span><span><a href="privacy.html">Privacy</a> &middot; <a href="cookies.html">Cookies</a> &middot; <a href="terms.html">Terms</a> &middot; <a href="styleguide.html">Design system</a></span></div></div>
</footer>
<div class="mobile-cta" aria-label="Quick contact"><a class="btn outline dark" href="tel:{TEL}">Call us</a><a class="btn" href="contact.html">Get a quote</a></div>
<button class="to-top" type="button" aria-label="Back to top" hidden><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 15l6-6 6 6"/></svg></button>
<script>
function exteraMenu(btn) {{
  var n = document.getElementById('nav'), open = n.classList.toggle('open');
  btn.setAttribute('aria-expanded', open);
  document.body.classList.toggle('menu-open', open);
}}
(function () {{
  document.querySelectorAll('.sub-toggle').forEach(function (b) {{
    var li = b.closest('li');
    if (li.hasAttribute('data-current')) {{ li.classList.add('open'); b.setAttribute('aria-expanded', 'true'); }}
    b.addEventListener('click', function () {{ var o = li.classList.toggle('open'); b.setAttribute('aria-expanded', o); }});
  }});
  document.querySelectorAll('.subnav').forEach(function (nav) {{
    var ul = nav.querySelector('ul'), cur = ul.querySelector('[aria-current]');
    if (cur) ul.scrollLeft = cur.offsetLeft - 16;
    function edge() {{ var end = ul.scrollLeft + ul.clientWidth >= ul.scrollWidth - 4; nav.classList.toggle('at-end', end); nav.classList.toggle('scrollable', ul.scrollWidth > ul.clientWidth + 4); nav.classList.toggle('at-start', ul.scrollLeft < 4); }}
    ul.addEventListener('scroll', edge, {{ passive: true }}); window.addEventListener('resize', edge); edge();
  }});
  var top = document.querySelector('.to-top');
  function showTop() {{ top.hidden = window.scrollY < 1200; }}
  window.addEventListener('scroll', showTop, {{ passive: true }}); showTop();
  top.addEventListener('click', function () {{ window.scrollTo({{ top: 0, behavior: 'smooth' }}); }});
}})();
</script>
</body>
</html>
"""
    (OUT / fname).write_text(html, encoding="utf-8")


# ---------- building blocks ----------
def hero(h1_bold, h1_rest, text, ctas=True, small=False, eyebrow=None, actions=None):
    if actions:  # custom buttons: (label, href, outline, opens_new_tab)
        cta = '<div class="actions">' + "".join(
            f'<a class="btn{" outline" if o else ""}" href="{h}"{" rel=noopener target=_blank" if ext else ""}>{l}{"<span class=sr-only> (opens in a new tab)</span>" if ext else ""}</a>'
            for l, h, o, ext in actions) + "</div>"
    else:
        cta = (
            '<div class="actions"><a class="btn" href="contact.html">Get a quote</a>'
            f'<a class="btn outline" href="tel:{TEL}">Call {PHONE}</a></div>'
            if ctas else ""
        )
    # inner-page banners already show a breadcrumb and a title, so the extra label would only repeat them
    eb = f'<span class="eyebrow light">{eyebrow}</span><br>' if eyebrow and not small else ""
    cls = "hero page-hero" if small else "hero"
    return f'<section class="{cls}"><div class="wrap">{eb}<h1><b>{h1_bold}</b> {h1_rest}</h1><p>{text}</p>{cta}</div></section>'


def heading(eyebrow, title, lead=None, center=False):
    c = " center" if center else ""
    ld = f'<p class="lead{" mx" if center else ""}">{lead}</p>' if lead else ""
    return f'<div class="sec-head{c}"><span class="eyebrow">{eyebrow}</span><h2>{title}</h2>{ld}</div>'


def cards(items, cols="g3", link=False):
    out = []
    for it in items:
        icon, title, text = it[0], it[1], it[2]
        more = f'<a class="more" href="{it[3]}">{it[4]} &rarr;</a>' if len(it) > 3 else ""
        h = f'<a href="{it[3]}">{title}</a>' if link and len(it) > 3 else title
        out.append(f'<div class="service">{ico(icon)}<h3>{h}</h3><p>{text}</p>{more}</div>')
    carousel = " carousel" if len(items) >= 5 and "compact" not in cols else ""  # long grids become swipeable rows on phones
    return f'<div class="grid {cols}{carousel}">{"".join(out)}</div>'


def steps(items):
    li = "".join(f"<li><h3>{t}</h3><p>{d}</p></li>" for t, d in items)
    return f'<ol class="steps">{li}</ol>'


def ticks(items):
    return '<ul class="ticks">' + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def shot(src, w, h, alt, caption=None, cls=""):
    cap = f"<figcaption>{caption}</figcaption>" if caption else ""
    return f'<figure class="shot {cls}"><img src="assets/3cx/{src}" width="{w}" height="{h}" loading="lazy" alt="{alt}">{cap}</figure>'


# Illustration for each feature block, chosen by its eyebrow label (files in assets/art/).
ART = {
    "One supplier": "devices.png", "8x8": "cloud-video.png", "Business mobile": "mobile.png", "Data cabling": "cabling.png",
    "Leased lines": "leased-line.png", "SIP trunks": "sip.svg", "ISDN switch-off": "switch-off.svg", "ISDN and PSTN switch-off": "switch-off.svg",
    "Lines and calls": "lines.svg", "Backup connectivity": "failover.svg", "Beyond backup": "pop-up.svg", "Resilience": "diverse.svg",
    "MPLS": "mpls.svg", "Best fit": "multi-site.svg", "Fibre broadband": "fibre.svg", "Full fibre": "full-fibre.svg",
    "Need guaranteed speed?": "lanes.svg", "Contact centres": "contact-centre.svg", "Approved installers": "certified.svg",
    "Online store": "store.svg", "CRM": "crm.svg", "Call Flow Designer": "flow.svg", "Hotels and hospitality": "hotel.svg",
    "Security": "security.svg", "In the car": "car.svg", "Our story": "story.svg",
    "Voice and messaging": "devices.png", "Team messaging": "voice-chat.svg", "Contact centre": "contact-centre.svg",
    "Routing and self-service": "flow.svg", "Outbound": "lines.svg", "Quality and workforce": "crm.svg", "Integrations": "integrations.svg",
    "Headsets": "headset-types.svg", "Speakerphones and audio": "speakerphone.svg", "Meeting room video": "video-bar-room.svg", "Room size guide": "room-sizes.svg",
    "Gamma Horizon": "portal.svg", "Handsets and headsets": "hardware.svg", "Accessibility": "accessibility.svg", "Horizon Collaborate": "collab-apps.svg",
    "Horizon Contact": "contact-centre.svg", "CRM and apps": "crm.svg", "Network and resilience": "reliability.svg", "If a site goes offline": "multi-site.svg",
    "Avaya IP Office": "pbx-box.svg", "Scale": "multi-site.svg",
    "Microsoft Teams": "cloud-video.png", "Security and reliability": "reliability.svg", "Get the room right": "devices.png",
}


def feature(eyebrow, title, text, bullets, icon, flip=False, cta=None, img=None):
    c = " flip" if flip else ""
    btn = f'<div class="actions left"><a class="btn" href="{cta[1]}">{cta[0]}</a></div>' if cta else ""
    if img:
        side = img
    elif eyebrow in ART:
        side = f'<figure class="art"><img src="assets/art/{ART[eyebrow]}" width="1920" height="1080" loading="lazy" alt=""></figure>'
    else:
        side = f'<div class="panel">{ico(icon)}<p class="panel-title">{eyebrow}</p></div>'
    return f"""<div class="split feature{c}"><div><span class="eyebrow">{eyebrow}</span><h2>{title}</h2><p>{text}</p>{ticks(bullets)}{btn}</div>
{side}</div>"""


def facts(items):
    return '<section class="factbar"><div class="wrap"><ul>' + "".join(
        f"<li><b>{a}</b><span>{b}</span></li>" for a, b in items) + "</ul></div></section>"


ACCRED = """<div class="accred">
<figure><img src="assets/iso9001.jpg" width="220" height="160" alt="ISO 9001:2015 quality management certification, British Assessment Bureau, UKAS 8289"><figcaption>ISO 9001:2015 quality management</figcaption></figure>
<figure><img src="assets/chas.jpg" width="220" height="160" alt="CHAS Accredited Contractor, Contractors Health and Safety Assessment Scheme"><figcaption>CHAS Accredited Contractor</figcaption></figure>
</div>"""


def accreditations():
    return f"""<section><div class="wrap narrow center">
{heading("Trust", "Accredited and certified", "Quality and safety you can check. Extera is certified to ISO 9001:2015 for quality management and is a CHAS Accredited Contractor, which matters when our engineers work on your site.", True)}
{ACCRED}
<ul class="badges"><li>Investors in People</li><li>Achilles member</li><li>Constructionline member</li></ul>
</div></section>"""


def partner_certs():
    return f"""<section class="alt"><div class="wrap narrow center">
{heading("Partners", "Vendor partners and certified installers", "Trained and approved by the manufacturers whose equipment we install.", True)}
<ul class="badges"><li>3CX Gold Partner</li><li>Avaya Silver Partner (Mid-Market &amp; Contact Centre)</li><li>Mitel Partner</li><li>Jabra Gold Partner</li><li>Plantronics Partner</li><li>IDAC (Datwyler) Certified Installer</li><li>Brand-Rex Certified Installer</li></ul>
</div></section>"""


def cta_band(text="Tell us what you need and an engineer will get back to you.", title="Talk to Extera"):
    return f"""<section class="cta-band"><div class="wrap narrow">
<h2>{title}</h2><p>{text}</p>
<div class="actions"><a class="btn outline" href="contact.html">Get a quote</a><a class="btn outline" href="tel:{TEL}">Call {PHONE}</a></div>
</div></section>"""


def faq(items, alt=False):
    qa = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in items)
    return f'<section{" class=alt" if alt else ""}><div class="wrap narrow">{heading("FAQ", "Common questions")}{qa}</div></section>'


def contact_card():
    return f"""<div class="card"><h3>Contact details</h3>
<p>Phone: <a href="tel:{TEL}">{PHONE}</a><br>Email: <a href="mailto:{EMAIL}">{EMAIL}</a></p>
<p>{ADDR.replace(", ", "<br>")}</p></div>"""


def related(title, items):
    return f'<section class="alt"><div class="wrap">{heading("Related", title)}{cards(items)}</div></section>'


# ---------- HOME ----------
home_ld = {
    "@context": "https://schema.org", "@type": "LocalBusiness", "name": SITE,
    "description": "Business telecommunication specialists: phone systems, connectivity, mobile and data cabling.",
    "telephone": "+441295220600", "email": EMAIL,
    "address": {"@type": "PostalAddress", "streetAddress": "10 Manor Park", "addressLocality": "Banbury", "postalCode": "OX16 3TB", "addressCountry": "GB"},
    "foundingDate": "2001", "sameAs": [FACEBOOK, LINKEDIN],
}
body = f"""
{facts([("Since 2001", "Trusted UK telecoms specialist"), ("Own engineers", "Covering mainland UK"), ("ISO 9001:2015", "Certified quality management"), ("CHAS", "Accredited Contractor")])}

<section><div class="wrap">
{heading("What we do", "Everything your business needs to communicate", "Phones, internet, mobiles and cabling normally means four suppliers and four bills. Extera brings them together under one team.")}
{cards([
 ("phone", "Phone systems", "3CX, 8x8, Gamma Horizon and Avaya IP Office systems, onsite or hosted, for one office or many sites.", "phone-systems.html", "All phone systems"),
 ("headset", "Contact centres", "Queues, call recording, reporting and agent tools for teams that live on the phone.", "contact-centres.html", "Contact centres"),
 ("globe", "Connectivity", "Fibre broadband, leased lines, MPLS and SIP trunks from a range of UK carriers, matched to your sites.", "connectivity.html", "Connectivity"),
 ("mobile", "Business mobile", "Mobile contracts and SIMs managed alongside your phone system and lines.", "mobile.html", "Business mobile"),
 ("cable", "Data cabling", "Structured copper and fibre cabling that handles the needs of today and tomorrow.", "data-cabling.html", "Data cabling"),
 ("cart", "Extera Direct", "Our online store for phones, headsets, conference phones and networking products.", "extera-direct.html", "Visit Extera Direct"),
])}
</div></section>

<section class="alt"><div class="wrap">
{feature("One supplier", "One team, one point of contact", "When something needs to change, you should not have to work out which supplier to call. Extera supplies, installs and supports your whole telecoms estate, so there is one team to ring.", ["Systems for 5 users or 500", "Onsite, hosted or a mix of both", "Supplied, installed and supported by one team", "Own engineers covering mainland UK"], "users", cta=("Get a quote", "contact.html"))}
</div></section>

<section><div class="wrap">
{heading("How we work", "From first call to going live", "A straightforward process with no surprises.", True)}
{steps([("Listen", "We learn how your business communicates today, what is not working, and where you want to be."), ("Design and quote", "A clear proposal with options, prices and timescales. No jargon, no obligation."), ("Install", "Trained engineers install and configure everything, and make sure it works for your people."), ("Support", "Maintenance and support contracts with SLAs, or ad-hoc help when you need it.")])}
</div></section>

<section class="alt"><div class="wrap">
{heading("Who we help", "From a two-person office to a multi-site organisation", "We began with managed services for large blue-chip companies and now look after businesses of every size.")}
{cards([
 ("building", "Small businesses", "Simple, affordable phones and broadband that just work, with someone to call when they do not.", "contact.html", "Talk to us"),
 ("route", "Growing and multi-site", "Join sites together with MPLS and a single phone system so staff feel like one team.", "connectivity.html", "See connectivity"),
 ("server", "Larger organisations", "Resilient connectivity, contact centres and structured cabling delivered as managed projects.", "contact-centres.html", "See contact centres"),
])}
</div></section>

{accreditations()}
{partner_certs()}

<section><div class="wrap narrow center">
{heading("Carriers", "Connectivity from the networks you know", "We work with a wide range of suppliers so we can recommend the right one for each site.", True)}
<ul class="badges"><li>Openreach</li><li>Virgin</li><li>TalkTalk</li><li>Vodafone</li><li>Virtual1</li><li>Gamma</li><li>Daisy</li></ul>
</div></section>

{faq([
 ("Should I choose 3CX or 8x8?", "3CX suits businesses that want control of their own system, onsite or in their own cloud. 8x8 is a fully hosted service with the platform run for you. We will recommend whichever fits, and the comparison on our <a href='8x8.html'>8x8 page</a> sets out the differences."),
 ("Can you handle the ISDN switch-off?", "Yes. We move businesses from ISDN and analogue lines to SIP trunks and broadband-based voice, keeping your numbers."),
 ("Do you cover the whole UK?", "We are based in Banbury, near the M40, with our own engineers covering mainland UK. Contact us with your sites and we will confirm cover."),
 ("Do I need a contract to get support?", "No. We offer SLA-backed maintenance contracts, and you can also call us for help without one, including urgent outages."),
], alt=True)}
{cta_band()}
"""
page("index.html", "Extera Limited | Business Telecommunication Specialists",
     "Extera supplies and supports business phone systems (3CX and 8x8), connectivity, mobiles and data cabling from Banbury, UK.",
     body,
     hero("One UK supplier", "for your phones, internet, mobiles and cabling", "Extera supplies, installs and supports business telecoms with its own engineers across mainland UK.", eyebrow="Extera Limited &middot; Banbury, Oxfordshire"),
     jsonld=home_ld)

# ---------- 3CX ----------
# Content adapted from the 3CX partner website pack (figures are 3CX's own, shown as such).
TCX = [
    ("3cx-apps.html", "phone", "Apps for every device", "Mobile, desktop and browser apps so your team can work from anywhere on their business number.", "3CX apps"),
    ("3cx-video-chat.html", "users", "Video, chat and messaging", "Video meetings, website live chat, WhatsApp, Facebook and SMS in one place.", "Video and chat"),
    ("3cx-integrations.html", "route", "Integrations", "Link 3CX to your CRM, Microsoft 365, Google Workspace and more, and build your own call flows.", "Integrations"),
    ("3cx-ai-analytics.html", "signal", "AI and analytics", "Sentiment, call summaries, transcription and real-time dashboards for managers.", "AI and analytics"),
]


def tcx_related(exclude):
    items = [(i, t, b, f, "Read more") for f, i, t, b, _ in TCX if f != exclude]
    if exclude != "3cx.html":
        items.insert(0, ("phone", "3CX phone systems", "The full overview: deployment, security, costs and how a project works.", "3cx.html", "Read more"))
    return f'<section class="alt"><div class="wrap">{heading("3CX", "More about 3CX", None)}{cards(items[:3], link=True)}</div></section>'


def partner_badge():
    return """<div class="partner-badge"><img src="assets/3cx/3cx-partner.jpg" width="120" height="100" loading="lazy" alt="3CX Partner logo">
<p><b>3CX Gold Partner.</b> Extera supplies, installs and supports 3CX systems. 3CX sells only through its partner network, so you buy from a team that knows the product.</p></div>"""


TRIAL = ("Request a free trial", "contact.html")

# --- 3CX hub ---
body = f"""
{facts([("3CX Gold Partner", "Installed and supported by Extera"), ("Since 2001", "Extera, UK telecoms specialist"), ("350,000+", "businesses use 3CX, says 3CX"), ("Up to 80%", "lower costs, says 3CX")])}

<section><div class="wrap">
{feature("3CX", "Unified communications that fit how you work", "3CX is a complete communications system: voice, video, live chat and messaging on one platform. It works for office, hybrid and remote teams, and you choose whether it runs onsite, in your own cloud or hosted for you.", ["Phone calls, video meetings, chat and messaging in one system", "Free apps for mobile, desktop and browser", "Keep your numbers, your lines and often your existing handsets", "Built-in contact centre tools, with no add-ons"], "phone", cta=TRIAL, img=shot("web-client.jpg", 1400, 794, "The 3CX web client showing a contacts list"))}
<p class="vendor-note">Statistics are supplied by 3CX and describe its global business.</p>
</div></section>

<section class="alt"><div class="wrap">
{heading("Explore 3CX", "Everything included in one system", "3CX bundles features that are often separate products. Choose a topic to see what it can do.")}
{cards([(i, t, b, f, m) for f, i, t, b, m in TCX], cols="g4", link=True)}
</div></section>

<section><div class="wrap">
{heading("See it in action", "A clean, simple interface", "The same tools on every device, so staff pick it up quickly.")}
<div class="shots">
{shot("mobile-apps.png", 1000, 757, "3CX mobile app on Android and iPhone", "Mobile apps", "bare")}
{shot("wallboard.jpg", 875, 596, "3CX wallboard showing queue statistics", "Live wallboard")}
{shot("management-console.jpg", 1382, 852, "3CX management console dashboard", "Management console")}
</div>
</div></section>

<section class="alt"><div class="wrap">
{heading("Why 3CX", "Simple, affordable and flexible")}
<div class="grid g3">
<div class="card"><h3>Simple</h3><p>Easy to install, use and manage. Much of the complexity of VoIP is taken out, and the apps and web client are quick for staff to learn.</p></div>
<div class="card"><h3>Affordable</h3><p>Licensing is based on simultaneous calls rather than the number of users, and calls between your staff, sites and remote workers are free. 3CX says this can cut costs by up to 80% compared with similar systems.</p></div>
<div class="card"><h3>Flexible</h3><p>Choose your own SIP trunks, handsets and where it runs. Keep your numbers, and use existing equipment where it is suitable.</p></div>
</div></div></section>

<section><div class="wrap">
{heading("Deployment", "Choose where your phone system lives")}
<div class="grid g3">
<div class="card"><h3>Onsite</h3><p>A server in your office or comms room, or a virtual machine on Hyper-V, VMware or KVM. Full control, and calls stay local if the internet drops.</p></div>
<div class="card"><h3>Hosted</h3><p>We run the system in the cloud for you. No hardware to look after, and quick to scale.</p></div>
<div class="card"><h3>Your own cloud</h3><p>Run 3CX in your own cloud account for control with less hardware in the office.</p></div>
</div></div></section>

<section class="alt"><div class="wrap">
{feature("Security", "Built-in security and resilience", "3CX includes protection that many phone systems leave to extras, so your calls and data are safer by default.", ["Protection against SIP attacks and a regularly updated blocklist of malicious IPs", "Encrypted voice (SRTP), app traffic and web access", "Automatic SSL certificate management", "Built-in automatic failover and backup options", "Admin access can be restricted by IP address"], "shield", flip=True)}
<p class="vendor-note">3CX reports security ratings of A+ from Qualys and A from Immunilabs.</p>
</div></section>

<section><div class="wrap">
{heading("Cutting costs", "Where the savings come from")}
{cards([
 ("clock", "Pay per call, not per user", "Licences are based on simultaneous calls, not the total number of staff."),
 ("users", "Free internal calls", "No cost for calls between staff, sites or home workers."),
 ("route", "Your choice of SIP trunks", "Use low-cost providers for outbound calls and keep your numbers. See our <a href='sip-trunks.html'>SIP trunks</a>."),
 ("globe", "Click to call", "Let customers call from your website or emails, with no freephone number needed."),
 ("cloud", "Fewer tools", "Voice, video, chat and contact centre in one system instead of several subscriptions."),
 ("wrench", "Easy to manage", "Simple administration means less time and cost looking after the system."),
])}
</div></section>

<section class="alt"><div class="wrap">
{heading("Compare", "3CX or 8x8?", "Both are good phone systems. The right choice depends on how you want to run it.")}
<div class="table-wrap"><table><thead><tr><th scope="col"></th><th scope="col">3CX</th><th scope="col">8x8</th></tr></thead><tbody>
<tr><th scope="row">Model</th><td>Software you run onsite, in your cloud, or hosted</td><td>Fully hosted service</td></tr>
<tr><th scope="row">Best for</th><td>Control, flexibility and mixed environments</td><td>Simple hosted calling and a full contact centre</td></tr>
<tr><th scope="row">Management</th><td>By you or by Extera</td><td>By 8x8, with Extera as your support contact</td></tr>
<tr><th scope="row">Costs</th><td>Licence, handsets, hosting or server</td><td>Monthly per-user subscription</td></tr>
<tr><th scope="row">Hardware</th><td>Optional server, SIP handsets</td><td>Handsets or apps only</td></tr>
<tr><th scope="row">Contact centre</th><td>Built-in queues, wallboards and reports for small to mid teams</td><td>Full omnichannel contact centre with quality, workforce management and AI</td></tr>
</tbody></table></div>
<p style="margin-top:16px" class="actions left"><a class="btn" href="3cx-vs-8x8.html">See the full comparison</a><a class="btn outline dark" href="8x8.html">See 8x8 details</a></p></div></section>

<section><div class="wrap">
{heading("Moving over", "How a 3CX project works")}
{steps([("Survey", "We review your users, sites, numbers, lines and handsets."), ("Design", "We agree the deployment, handsets and call flows with you."), ("Install", "We build, configure and test the system and set up your phones."), ("Go live", "Numbers are ported and we are on hand to support your team.")])}
</div></section>

<section><div class="wrap narrow">{partner_badge()}</div></section>

{faq([
 ("Can I keep my phone numbers?", "Yes. Numbers are ported to your new system, and we plan the cutover to avoid downtime."),
 ("Do I need new handsets?", "Not always. 3CX works with a wide range of SIP handsets, and with softphone apps on computers and mobiles."),
 ("Can staff work from home?", "Yes. The apps give home workers the same extension, voicemail and features as the office. See <a href='3cx-apps.html'>3CX apps</a>."),
 ("Is video conferencing included?", "Yes. Video meetings for up to 250 participants are included, with no per-user fees. See <a href='3cx-video-chat.html'>video and chat</a>."),
 ("Does 3CX work with Microsoft 365 or our CRM?", "Yes. 3CX integrates with Microsoft 365 and with major CRMs. See <a href='3cx-integrations.html'>integrations</a>."),
 ("What does it cost?", "It depends on simultaneous calls, hosting and handsets. Send us your requirements and we will quote."),
 ("Who supports it afterwards?", "We do. Support ranges from ad-hoc help to SLA-backed maintenance. See our <a href='support.html'>support page</a>."),
], alt=True)}
{related("Pairs well with", [("globe", "SIP trunks and connectivity", "Replace ISDN with SIP trunks and free-calls bundles.", "sip-trunks.html", "SIP trunks"), ("mobile", "Business mobile", "Mobiles on the same account as your office phones.", "mobile.html", "Mobile"), ("cable", "Data cabling", "Network cabling installed with the system.", "data-cabling.html", "Cabling")])}
{cta_band("Tell us how many users and sites you have and we will put together a 3CX quote, or set you up with a free trial.", "Try 3CX with Extera")}
"""
page("3cx.html", "3CX Phone Systems | Extera Limited",
     "3CX business phone systems supplied, installed and supported by Extera, a 3CX Gold Partner: voice, video, chat and contact centre tools, onsite, cloud or hosted.",
     body, hero("3CX", "Phone Systems", "One system for calls, video, chat and contact centre, with some of the lowest running costs around. Installed and supported by Extera, a 3CX Gold Partner.", small=True, eyebrow="3CX Gold Partner"), "3CX Phone Systems")


def tcx_page(fname, title, desc, h1a, h1b, hero_text, crumb, intro, extra, faqs, cta_text):
    body = f"""
<section><div class="wrap">{intro}</div></section>
{extra}
{faq(faqs)}
{tcx_related(fname)}
{cta_band(cta_text, "Try 3CX with Extera")}
"""
    page(fname, title, desc, body, hero(h1a, h1b, hero_text, small=True, eyebrow="3CX"),
         f'<a href="3cx.html">3CX Phone Systems</a> / {crumb}')


# --- Apps ---
tcx_page("3cx-apps.html", "3CX Apps for Mobile, Desktop and Browser | Extera Limited",
    "3CX apps for iPhone, Android, Windows and browser: take business calls, chat and meetings from anywhere on your business number.",
    "3CX", "Apps", "Take your business number anywhere: calls, chat and meetings on your phone, laptop or browser, with no VPN.", "Apps",
    feature("Work from anywhere", "Your office phone, wherever you are", "Your extension follows you on your mobile, laptop or browser. Staff make and receive calls on the company number, check voicemail, chat and join meetings, without switching between tools or giving out personal numbers.", ["Use your office number on iPhone and Android", "Browser and desktop apps, with no VPN needed", "Calls, chat, video and WhatsApp in one app", "Calls over Wi-Fi or mobile data, so you can cut mobile call costs"], "mobile", cta=TRIAL, img=shot("mobile-apps.png", 1000, 757, "3CX apps on Android and iPhone", None, "bare")),
    f"""<section class="alt"><div class="wrap">
{heading("Mobile apps", "Enterprise communication on the move")}
{cards([
 ("phone", "Business calls anywhere", "Make and receive calls with your office number, and transfer, hold and conference from your phone."),
 ("chat", "Team chat", "Secure internal messaging in real time, with group chats and status."),
 ("users", "Video meetings", "Start or join video conferences from the app with no extra software."),
 ("shield", "Secure", "End-to-end encrypted calls and messages keep business communication on approved tools."),
 ("route", "WhatsApp and SMS", "Reply to customer WhatsApp and SMS messages from the 3CX app using your business identity."),
 ("clock", "Voicemail and presence", "Read voicemail, set your status and see who is available."),
])}
</div></section>
<section><div class="wrap">
{feature("In the car", "Safe and hands-free on the road", "3CX works with Apple CarPlay and Android Auto, so staff who drive can stay connected without taking their eyes off the road.", ["Hands-free calls with voice commands or car controls", "Reply to messages by voice", "Access contacts, call history and voicemail on the dashboard", "Improved Bluetooth support on Android"], "signal", flip=True)}
</div></section>
<section class="alt"><div class="wrap">
{feature("Web and desktop", "Use 3CX from any browser or computer", "The web client and desktop app give you full access to calls, chat and meetings, with no VPN. You can make calls from your browser or control your desk phone from your computer.", ["Browser calling and desk phone control", "Omnichannel messaging for live chat, WhatsApp, Facebook and SMS", "One-click video meetings", "Microsoft 365 sync for users, calendars, contacts and Teams presence", "Real-time team presence and click-to-call from your CRM"], "users", img=shot("web-client.jpg", 1400, 794, "The 3CX web client contacts view"))}
</div></section>""",
    [("Do staff need to use their personal mobile number?", "No. Calls and messages use the business number, so personal numbers stay private."),
     ("Does it work on Wi-Fi and mobile data?", "Yes. The app makes calls over Wi-Fi or mobile data, and can be used from anywhere with a good connection."),
     ("Which devices are supported?", "iPhone and Android phones, Windows computers and modern web browsers."),
     ("Can staff use it in the car?", "Yes. 3CX works with Apple CarPlay and Android Auto for hands-free use.")],
    "Tell us how your team works and we will plan the right apps and devices.")

# --- Video and chat ---
tcx_page("3cx-video-chat.html", "3CX Video Conferencing, Live Chat and Messaging | Extera Limited",
    "3CX video conferencing for up to 250 people, website live chat, WhatsApp, Facebook Messenger and SMS: included in your phone system.",
    "Video", "and Chat", "Video meetings for up to 250 people, plus website chat, WhatsApp and SMS, all included in the system.", "Video and Chat",
    feature("Video conferencing", "Video meetings, included", "3CX includes video conferencing, with no per-user fees or time limits. Staff and guests join from a link in the browser, or dial in by phone, so there is nothing to install.", ["Up to 250 participants, with no time limits", "One-click joining from a browser or app, or dial in by phone", "Screen sharing, whiteboard, polls, reactions and chat", "Meeting recording and background blur", "Meetings run on your 3CX server, so your data stays with you"], "users", cta=TRIAL, img=shot("video-meeting.jpg", 1400, 754, "A 3CX video meeting with four participants")),
    f"""<section class="alt"><div class="wrap">
{heading("More meeting tools", "Everything you need for meetings and webinars")}
{cards([
 ("users", "Large events", "Run meetings and webinars for large audiences with no extra licences."),
 ("globe", "Global dial-in", "Participants can join by phone from anywhere."),
 ("signal", "Stream and record", "Record for training and compliance, or stream live to YouTube."),
 ("wrench", "Remote control", "Give or take control of a desktop to support colleagues and customers."),
 ("clip", "Share files", "Upload files before the meeting starts so everyone has what they need."),
 ("wifi", "Optimised for low bandwidth", "Built on Google WebRTC for stable HD video, even on slower connections."),
])}
</div></section>
<section><div class="wrap">
{feature("Live chat", "Talk to website visitors instantly", "Add live chat to your website and answer from the same system as your calls. Switch to a voice or video call with one click when a chat needs a conversation.", ["Works with WordPress, Drupal, Joomla and custom sites", "Chat queues route by department or priority", "Transfer chats between colleagues", "Chat reports on response times, volumes and satisfaction", "Managers can monitor chats and team performance live"], "chat", flip=True, img=shot("live-chat.jpg", 900, 881, "3CX website live chat with video call", None, "bare"))}
</div></section>
<section class="alt"><div class="wrap">
{heading("One inbox", "WhatsApp, Facebook and SMS, handled properly")}
{cards([
 ("chat", "WhatsApp Business", "Manage customer WhatsApp messages inside 3CX. Replies use business IDs, not personal numbers, and every conversation is logged and auditable."),
 ("users", "Facebook Messenger", "Facebook messages land in the 3CX web client, so agents answer without logging in to Facebook, with queues and reporting."),
 ("mobile", "SMS and MMS", "Send and receive business texts under your company identity, and share them across a team so none go unanswered."),
], cols="g3")}
</div></section>""",
    [("Is video conferencing really included?", "Yes. It is part of 3CX, with no per-user fees or time caps, for up to 250 participants."),
     ("Do guests need to install anything?", "No. Guests join from a link in their browser, or dial in by phone."),
     ("Can we run webinars?", "Yes. You can run large meetings and webinars, record them, and stream to YouTube."),
     ("Can several agents share WhatsApp or SMS?", "Yes. Messages can be routed to a queue of agents so the workload is shared and none are missed."),
     ("Does live chat work with our website?", "Yes. It works with WordPress, Drupal and Joomla sites, and with custom websites.")],
    "Tell us how you meet and talk to customers and we will set up the right tools.")

# --- Integrations ---
tcx_page("3cx-integrations.html", "3CX Integrations: CRM, Microsoft 365 and Call Flows | Extera Limited",
    "3CX integrates with Salesforce, HubSpot, Dynamics, Zoho, Microsoft 365 and Google Workspace, with Call Flow Designer for custom call handling.",
    "3CX", "Integrations", "Show the customer record as the phone rings, and link 3CX to Microsoft 365, your CRM and your own call flows.", "Integrations",
    feature("CRM", "Know who is calling before you answer", "3CX connects to your CRM so customer details appear as the phone rings. Calls and chats are logged automatically, so staff spend their time with customers instead of typing notes.", ["Works with Salesforce, HubSpot, Dynamics, Zoho and others", "Caller ID lookup shows the customer record as the call arrives", "New numbers are added as contacts automatically", "Click to call straight from the CRM", "Calls and chats are logged against the customer, with transcription and journaling where enabled"], "clip", cta=TRIAL),
    f"""<section class="alt"><div class="wrap">
{heading("More integrations", "Fits in with the tools you already use")}
{cards([
 ("cloud", "Microsoft 365", "Sync users and contacts, sign in with single sign-on, and see Teams presence. The Enterprise edition supports Teams Direct Routing."),
 ("globe", "Google Workspace", "Sync users and contacts from Google Workspace."),
 ("headset", "Helpdesks", "Connect to helpdesk and ticketing tools such as Freshdesk and Zendesk."),
 ("wrench", "Custom integrations", "A CRM wizard and API let you integrate systems that are not supported out of the box."),
 ("route", "SIP trunk choice", "Pick your own SIP trunk provider. 3CX includes a checker that tests whether a provider will work. See <a href='sip-trunks.html'>SIP trunks</a>."),
 ("signal", "Reporting tools", "Export reporting data to dashboards, including a Grafana integration (beta)."),
])}
</div></section>
<section><div class="wrap">
{feature("Call Flow Designer", "Design call handling that fits your business", "Call Flow Designer is a visual tool for building voice applications and routing, so calls reach the right place faster without writing code.", ["Route calls based on customer authentication", "Callback scheduler and automatic outbound dialler", "Surveys and phone orders", "Card payment authentication", "Text to speech and speech to text in 120 languages"], "route", flip=True)}
</div></section>
<section class="alt"><div class="wrap">
{feature("Hotels and hospitality", "Hotel PBX included", "3CX includes a hotel module with features hotels expect, built into the same system as your other communications.", ["Check-in and check-out from your property management system or the web client", "Guest extensions with Do Not Disturb", "Block outside calls on vacant rooms and schedule wake-up calls", "Room billing and housekeeping status by phone", "Works with systems such as Micros-Fidelio, Protel and roomMaster"], "building")}
</div></section>""",
    [("Which CRMs does 3CX work with?", "Major CRMs including Salesforce, HubSpot, Microsoft Dynamics and Zoho, and helpdesks such as Freshdesk. A wizard and API cover others."),
     ("Does it work with Microsoft Teams?", "Yes. 3CX syncs with Microsoft 365, shows Teams presence, and the Enterprise edition supports Teams Direct Routing."),
     ("Can we choose our own SIP trunk provider?", "Yes. You can use your own provider, and 3CX includes a checker to test whether it is supported."),
     ("Can 3CX be used in a hotel?", "Yes. It includes a hotel module that integrates with common property management systems.")],
    "Tell us about your CRM and Microsoft 365 set-up and we will plan the integration.")

# --- AI and analytics ---
tcx_page("3cx-ai-analytics.html", "3CX AI, Reporting and Contact Centre Tools | Extera Limited",
    "3CX AI features, call summaries, sentiment analysis, transcription, real-time wallboards and contact centre tools included in the phone system.",
    "AI", "and Analytics", "See how every call went with sentiment, summaries and live dashboards, and run a contact centre without add-ons.", "AI and Analytics",
    feature("Analytics", "Clear insight into every call", "3CX gives managers a clear view of performance and customer satisfaction. AI tools highlight problems early, so you can improve response quality and coach your team.", ["Sentiment analysis by call, agent, queue and ring group", "AI call summaries, so you do not have to listen to whole recordings", "Call logs with sentiment, summary and transcript in one view", "Dashboards for agent performance, ring group trends and queue wait times"], "signal", cta=TRIAL, img=shot("management-console.jpg", 1382, 852, "The 3CX management console dashboard")),
    f"""<section class="alt"><div class="wrap">
{heading("AI features", "AI that does real work")}
{cards([
 ("chat", "Call summaries", "Short summaries highlight the key points of each call and speed up follow-up."),
 ("signal", "Sentiment analysis", "See how customers feel, find top-performing agents and flag calls that need follow-up."),
 ("clip", "Transcription", "Transcribe calls using Google, OpenAI or 3CX's own engine, depending on your cost, compliance and privacy needs."),
 ("headset", "AI receptionist", "Recent 3CX releases add AI agents that can answer and route calls and handle common requests. Ask us which edition you need."),
 ("users", "Boss and secretary", "Screen calls for executives with a human or AI assistant, with selected callers able to bypass."),
 ("shield", "Privacy options", "Choose cloud transcription, or run it onboard where your data must stay in-house (this needs suitable hardware)."),
])}
</div></section>
<section><div class="wrap">
{feature("Contact centre", "Contact centre tools, built in", "3CX includes contact centre features with no add-ons or extra licensing, so you can run queues, wallboards and reports from the same system as your phones.", ["Call queues, ring groups, IVR and callback", "Round robin, hunt groups and skill-based routing", "Switchboard and live wallboard", "Listen in, whisper and barge for managers", "Call recording and quality assurance", "Hot desking, and reports on agents, queues and SLAs"], "headset", flip=True, img=shot("wallboard.jpg", 875, 596, "A 3CX wallboard showing live queue statistics"), cta=("See contact centres", "contact-centres.html"))}
</div></section>
<section class="alt"><div class="wrap">
{feature("Switchboard", "A live view for receptionists and supervisors", "The switchboard shows everyone's availability and live calls in one screen, so calls are answered and transferred quickly.", ["See who is free, busy or away", "Drag and drop to transfer calls", "Works for receptionists and busy teams"], "users", img=shot("switchboard.jpg", 900, 979, "The 3CX switchboard view"))}
</div></section>""",
    [("Is the contact centre a separate product?", "No. The contact centre tools are included with 3CX, with no separate licences. For larger operations we can also advise on other platforms. See <a href='contact-centres.html'>contact centres</a>."),
     ("Do AI features cost extra?", "Some features depend on the edition and, for transcription, on how you run it. We will confirm what is included when we quote."),
     ("Can we keep transcripts private?", "Yes. You can choose cloud transcription or an onboard option, depending on your privacy needs."),
     ("Which reports are available?", "Reports on calls, agents, queues and SLAs, plus sentiment where AI features are enabled.")],
    "Tell us about your team and what you want to measure and we will recommend a set-up.")


# ---------- 8x8 ----------
# Content is original copy based on 8x8 product information published by 8x8 and UK resellers (figures are 8x8's own claims).
X8 = [
    ("8x8-voice.html", "phone", "Voice and messaging", "A cloud business phone system with team messaging, on desktop, mobile and browser.", "Voice and messaging"),
    ("8x8-meetings.html", "users", "Video meetings", "HD meetings that guests join from a browser, with screen sharing, recording and calendar links.", "Meetings"),
    ("8x8-contact-centre.html", "headset", "Contact centre", "Omnichannel routing, IVR, quality and workforce management, analytics and AI on the same platform.", "Contact centre"),
    ("8x8-integrations.html", "route", "Integrations", "Microsoft Teams, Salesforce, Dynamics, Zendesk and open APIs, so 8x8 fits how you already work.", "Integrations"),
    ("8x8-security.html", "shield", "Security and reliability", "A 99.999% uptime SLA, mandatory multi-factor authentication and recognised certifications, as stated by 8x8.", "Security and reliability"),
]


def x8_related(exclude):
    items = [(i, t, b, f, "Read more") for f, i, t, b, _ in X8 if f != exclude]
    if exclude != "8x8.html":
        items.insert(0, ("cloud", "8x8 cloud phone systems", "The overview: what 8x8 is, how it compares with 3CX and how a project works.", "8x8.html", "Read more"))
    return f'<section class="alt"><div class="wrap">{heading("8x8", "More about 8x8", None)}{cards(items[:3], link=True)}</div></section>'


def x8_page(fname, title, desc, h1a, h1b, hero_text, crumb, intro, extra, faqs, cta_text):
    body = f"""
<section><div class="wrap">{intro}</div></section>
{extra}
{faq(faqs)}
{x8_related(fname)}
{cta_band(cta_text, "Talk to us about 8x8")}
"""
    page(fname, title, desc, body, hero(h1a, h1b, hero_text, small=True, eyebrow="8x8"),
         f'<a href="8x8.html">8x8 Cloud Phone Systems</a> / {crumb}')


QUOTE8 = ("Get an 8x8 quote", "contact.html")

# --- 8x8 overview ---
body = f"""
{facts([("Since 2001", "Extera, UK telecoms specialist"), ("ISO 9001:2015", "Certified quality management"), ("99.999%", "uptime SLA, says 8x8"), ("Per user", "simple monthly pricing")])}

<section><div class="wrap">
{feature("8x8", "Hosted calling, meetings and messaging in one", "8x8 is a cloud communications platform. Voice, video meetings, team chat and contact centre tools run together as a monthly per-user service, with nothing to host and no phone system hardware to look after.", ["No phone system hardware to maintain", "Works from the office, home or mobile app", "Scales up or down as your team changes", "We handle setup, number porting and ongoing support"], "cloud", cta=QUOTE8)}
<p class="vendor-note">Figures are published by 8x8 and describe its own platform.</p>
</div></section>

<section class="alt"><div class="wrap">
{heading("Explore 8x8", "What is included", "Choose a topic to see how it works, and what to check before you commit.")}
{cards([(i, t, b, f, m) for f, i, t, b, m in X8] + [("clip", "Not sure where to start?", "Tell us how your team works and we will recommend the right plan and a realistic migration route.", "contact.html", "Talk to us")], link=True)}
</div></section>

<section><div class="wrap">
{heading("Why 8x8", "Built for flexible, hybrid teams")}
{cards([
 ("cloud", "Always up to date", "8x8 runs and updates the platform, so new features arrive without upgrade projects or weekend call-outs."),
 ("users", "One app", "Calls, video meetings and team chat in a single app on desktop and mobile."),
 ("building", "Multi-site made simple", "Add sites and users in minutes, with one system and one dial plan across every office."),
 ("headset", "Contact centre ready", "Add queues, routing, recording and reporting when your team starts handling customer calls."),
 ("shield", "Resilient by design", "Hosted across many data centres, so your phones do not depend on a single office."),
 ("wrench", "Supported by Extera", "We set it up and look after it, so you have a local team to call."),
], cols="g3 compact")}
</div></section>

<section class="alt"><div class="wrap">
{heading("Compare", "3CX or 8x8?", "Both are good phone systems. The right choice depends on how you want to run it.")}
<div class="table-wrap"><table><thead><tr><th scope="col"></th><th scope="col">3CX</th><th scope="col">8x8</th></tr></thead><tbody>
<tr><th scope="row">Model</th><td>Software you run onsite, in your cloud, or hosted</td><td>Fully hosted service</td></tr>
<tr><th scope="row">Best for</th><td>Control, flexibility and mixed environments</td><td>Simple hosted calling and a full contact centre</td></tr>
<tr><th scope="row">Management</th><td>By you or by Extera</td><td>By 8x8, with Extera as your support contact</td></tr>
<tr><th scope="row">Costs</th><td>Licence, handsets, hosting or server</td><td>Monthly per-user subscription</td></tr>
<tr><th scope="row">Hardware</th><td>Optional server, SIP handsets</td><td>Handsets or apps only</td></tr>
<tr><th scope="row">Contact centre</th><td>Built-in queues, wallboards and reports for small to mid teams</td><td>Full omnichannel contact centre with quality, workforce management and AI</td></tr>
</tbody></table></div>
<p style="margin-top:16px" class="actions left"><a class="btn" href="3cx-vs-8x8.html">See the full comparison</a><a class="btn outline dark" href="3cx.html">See 3CX details</a></p></div></section>

<section><div class="wrap">
{heading("Moving over", "How an 8x8 project works")}
{steps([("Survey", "We review users, numbers, sites and your internet connection."), ("Design", "We agree your call flows, handsets and any contact centre needs."), ("Set up", "We configure the platform, users and phones, and port your numbers."), ("Support", "We train your team and support you after go-live.")])}
</div></section>

{faq([
 ("Do I need good internet for 8x8?", "Hosted voice depends on your connection. We check your broadband or leased line during the survey and can add a backup connection. See <a href='8x8-security.html'>security and reliability</a>."),
 ("Can I use my own phones?", "You can use the 8x8 app on computers and mobiles, or desk phones. We will advise on handsets."),
 ("Can I keep my numbers?", "Yes. We port your existing numbers to the new platform."),
 ("Is there a contact centre?", "Yes. A full contact centre sits on the same platform. See the <a href='8x8-contact-centre.html'>8x8 contact centre page</a>."),
 ("Does 8x8 work with Microsoft Teams?", "Yes. See <a href='8x8-integrations.html'>integrations</a>."),
], alt=True)}
{cta_band("Not sure which suits you? We will compare 8x8 and 3CX against your requirements.", "Talk to us about 8x8")}
"""
page("8x8.html", "8x8 Cloud Phone Systems | Extera Limited",
     "8x8 cloud phone systems, meetings and contact centre supplied and supported by Extera, with a comparison against 3CX.",
     body, hero("8x8", "Cloud Phone Systems", "One hosted platform for calls, meetings and contact centre, with nothing to run yourself. Set up and supported by Extera.", small=True, eyebrow="Phone systems"), "8x8 Cloud Phone Systems")

# --- Voice and messaging ---
x8_page("8x8-voice.html", "8x8 Business Phone and Team Messaging | Extera Limited",
    "8x8 cloud business phone system and team messaging: auto attendants, queues, call recording, voicemail transcription and apps for desktop and mobile.",
    "Voice", "and Messaging", "A phone system that lives in the cloud: calls, voicemail and team chat in one app on any device.", "Voice and Messaging",
    feature("Voice and messaging", "A business phone system that lives in the cloud", "Each person gets a direct-dial extension and the same features on a desk phone, a computer, a browser or a mobile. Calls, voicemail and team chat sit in one app, so staff stop switching between tools.", ["Direct-dial extensions and your existing numbers", "The same experience on desktop, mobile and browser", "Auto attendant, ring groups and call queues built in", "Call recording and voicemail with transcription"], "phone", cta=QUOTE8),
    f"""<section class="alt"><div class="wrap">
{heading("Calling features", "Everything a modern phone system needs")}
{cards([
 ("route", "Auto attendant", "Welcome callers with a menu that sends them to the right person or team, with different greetings out of hours."),
 ("users", "Ring groups and queues", "Share incoming calls across a team, with queues so no caller is left unanswered."),
 ("clip", "Voicemail with transcription", "Read your voicemails as text, and get a notification without having to dial in."),
 ("shield", "Call recording", "Record calls for training and compliance, with recordings stored and searchable."),
 ("building", "Reception tools", "A dedicated receptionist app shows who is free and lets operators transfer calls quickly."),
 ("globe", "Calling bundles", "Plans include UK calling, with international bundles available depending on the plan you choose."),
])}
</div></section>
<section><div class="wrap">
{feature("Team messaging", "Chat that keeps conversations in one place", "Team messaging sits in the same app as your calls. Start a conversation, share a file, and move to a call or video meeting with one click, without leaving the thread.", ["Public and private rooms, with @mentions and read receipts", "File sharing and a searchable history", "Presence, so you can see who is available", "Start or join a meeting from any conversation", "Connects to some third-party chat tools, such as Slack, so guests are not left out"], "chat", flip=True)}
</div></section>
<section class="alt"><div class="wrap">
{heading("Choosing a plan", "Plans for different kinds of user", "8x8 sells its plans in tiers. Names and inclusions change from time to time, so we confirm the current options when we quote.")}
<div class="table-wrap"><table><thead><tr><th scope="col">Level</th><th scope="col">Who it suits</th><th scope="col">What it adds</th></tr></thead><tbody>
<tr><th scope="row">Calling essentials</th><td>Staff who mainly need a phone</td><td>Business calling, voicemail, call recording and team messaging</td></tr>
<tr><th scope="row">One app</th><td>Most office and hybrid staff</td><td>Voice, messaging and meetings in one application, with wider calling bundles</td></tr>
<tr><th scope="row">Power user</th><td>Reception, sales and heavy callers</td><td>Switchboard tools, extra recording and storage and larger calling bundles</td></tr>
<tr><th scope="row">Supervisor</th><td>Team leaders and managers</td><td>Analytics and dashboards, advanced call handling and quality control tools such as monitor, whisper and barge</td></tr>
</tbody></table></div>
<p class="vendor-note">Mix plans across your team, so people only pay for the features they need.</p>
</div></section>""",
    [("Can I keep my existing numbers?", "Yes. We port your numbers to 8x8 and plan the cutover with you."),
     ("Can I still use desk phones?", "Yes. 8x8 supports desk phones as well as the apps. We can supply and set up handsets."),
     ("Do staff need separate chat and phone apps?", "No. Calling and team messaging are in the same app."),
     ("Can calls be recorded?", "Yes. Call recording is available, and recordings can be stored and searched. We will advise on retention and compliance."),
     ("How is it priced?", "8x8 is charged per user per month, and you can mix plans across your team. We quote by number of users and plan.")],
    "Tell us how many people you have and how they work, and we will recommend an 8x8 plan mix.")

# --- Meetings ---
x8_page("8x8-meetings.html", "8x8 Video Meetings | Extera Limited",
    "8x8 video meetings that guests join from a browser: HD video, screen sharing, recording, calendar integration and live streaming.",
    "Video", "Meetings", "Video meetings that guests join from a link, with no downloads, plus screen sharing and recording.", "Meetings",
    feature("Meetings", "Video meetings without the setup", "8x8 meetings run in the browser, so guests join from a link with no plug-ins to install. Staff start a meeting from a chat, a calendar invite or their personal meeting link.", ["Guests join from a browser, with no downloads", "HD audio and video on any device", "Up to 100 participants in a meeting, according to 8x8's documents", "Start a meeting straight from a team chat"], "users", cta=QUOTE8, img=f'<figure class="art"><img src="assets/art/meeting.svg" width="1920" height="1080" loading="lazy" alt=""></figure>'),
    f"""<section class="alt"><div class="wrap">
{heading("Meeting tools", "Everything for a productive meeting")}
{cards([
 ("users", "Easy for guests", "Anyone with the link can join in their browser, so clients and suppliers are never blocked by software."),
 ("signal", "Screen sharing", "Share a screen or an application instantly so everyone sees the same thing."),
 ("clock", "Calendar links", "Schedule from Microsoft or Google calendars, and keep a personal meeting link for quick calls."),
 ("clip", "Recording and transcripts", "Record meetings for people who could not attend. AI transcription and summaries are available depending on plan."),
 ("chat", "Whiteboard and chat", "Brainstorm on a shared whiteboard and keep the conversation alongside the video."),
 ("globe", "Live streaming", "Broadcast larger events to YouTube when more people need to watch than can take part."),
])}
</div></section>
<section><div class="wrap">
{feature("Get the room right", "Good meetings need good equipment and connection", "Great video needs clear audio and a connection that does not drop. We can supply conference phones, headsets and room equipment, and a connection sized for video.", ["Headsets and conference phones from our range", "Room set-ups for meeting rooms and boardrooms", "Fibre or a leased line for steady video", "4G/5G backup so meetings keep going"], "headset", flip=True, cta=("See Extera Direct", "extera-direct.html"))}
</div></section>
<section class="alt"><div class="wrap">
{heading("Connection", "What video needs from your network")}
{cards([
 ("wifi", "Enough upload speed", "Video uses upload as well as download. Full fibre or a leased line gives plenty of headroom. See <a href='fibre-broadband.html'>fibre broadband</a>."),
 ("bolt", "A dedicated line", "For large meetings and busy offices a dedicated connection keeps video smooth. See <a href='leased-lines.html'>leased lines</a>."),
 ("signal", "Backup", "Automatic failover keeps calls running if the main line fails. See <a href='backup-connectivity.html'>4G/5G backup</a>."),
], cols="g3")}
</div></section>""",
    [("Do guests need an account or software?", "No. Guests can join from a link in their browser."),
     ("How many people can join?", "8x8's documents describe up to 100 participants in a meeting. Limits can depend on plan and change over time, so we confirm the current limit when we quote."),
     ("Can I record meetings?", "Yes. Meetings can be recorded, and AI transcription and summaries are available depending on your plan."),
     ("Does it work with my calendar?", "Yes. It integrates with Microsoft and Google calendars."),
     ("Can we stream events?", "Yes. Larger events can be streamed live to YouTube.")],
    "Tell us how your teams meet and we will plan the equipment and connection to match.")

# --- Contact centre (detailed) ---
x8_page("8x8-contact-centre.html", "8x8 Contact Centre: Features and Functionality | Extera Limited",
    "8x8 cloud contact centre features: omnichannel routing, IVR, dialler, agent assist, quality and workforce management, analytics and AI.",
    "8x8", "Contact Centre", "Serve customers on every channel from one screen, with routing, quality tools, planning and AI built in.", "Contact Centre",
    feature("Contact centre", "A complete cloud contact centre on one platform", "8x8 puts your contact centre on the same platform as your phones, meetings and chat. Agents work in one screen, supervisors see everything live, and managers get the quality and planning tools to run a team well.", ["Voice, chat, email, SMS, video and messaging apps in one agent view", "Skills-based and CRM-based routing, IVR and queued callback", "Real-time wallboards, quality scoring and workforce planning", "AI to guide agents, summarise calls and handle simple requests"], "headset", cta=("Get a contact centre quote", "contact.html")),
    f"""<section class="alt"><div class="wrap">
{heading("Channels", "Meet customers wherever they are", "8x8 describes a single platform that brings every channel into one interface.")}
{cards([
 ("phone", "Voice", "Inbound and outbound calls with routing, recording and queues."),
 ("chat", "Web chat", "Chat from your website, with transfers and a switch to voice or video."),
 ("clip", "Email", "Email handled alongside calls and chats in the same queues."),
 ("mobile", "SMS and messaging apps", "SMS and messaging channels such as WhatsApp, Facebook Messenger, Viber and RCS."),
 ("users", "Video and co-browsing", "Video support and co-browsing to move customers to the best channel."),
 ("globe", "Social", "Social media enquiries brought in through supported integrations."),
])}
<p class="vendor-note">Agents can handle several interactions at once, with 8x8 stating up to 13 across channels.</p>
</div></section>

<section><div class="wrap">
{feature("Routing and self-service", "Get every customer to the right agent first time", "Routing decides who answers each contact. The right set-up reduces transfers, shortens waits and keeps customers away from queues they do not need to be in.", ["Automatic call distribution (ACD) and queues", "Skills-based routing, plus routing based on CRM data", "Intelligent routing using details such as caller ID and reason for contact", "Standard and intelligent IVR, with a builder for custom call paths", "Queued callback so customers keep their place without waiting on the line", "Multilingual support for mixed audiences"], "route", flip=True)}
</div></section>

<section class="alt"><div class="wrap">
{heading("Agents", "Tools that help agents do their best work")}
{cards([
 ("users", "One desktop", "Calls, chats, emails and messages in one omnichannel screen, so agents do not hunt between tools."),
 ("clip", "CRM screen pop", "Customer details appear as a contact arrives, with calls logged against the record. Works with Salesforce, Dynamics, NetSuite and Zendesk."),
 ("chat", "Collaboration", "Agents can message, call or video colleagues and experts without leaving the contact."),
 ("signal", "Agent assist", "AI offers real-time guidance, dynamic scripting, sentiment insight and automatic call summaries."),
 ("mobile", "Work from anywhere", "Use an IP phone, a computer or a mobile app, so home and hybrid agents get the same tools."),
 ("shield", "Secure payments", "PCI-compliant payment handling lets agents take card payments without hearing or storing card details."),
])}
</div></section>

<section><div class="wrap">
{feature("Outbound", "A dialler for sales and campaigns", "An auto dialler helps outbound teams make more conversations from the same number of agents.", ["Predictive, progressive and preview dialling modes", "Calls placed from a contact list and connected calls routed to the next free agent", "Campaign reporting alongside your inbound statistics"], "phone")}
</div></section>

<section class="alt"><div class="wrap">
{heading("Supervisors", "A live view of every queue and every agent")}
{cards([
 ("signal", "Real-time monitoring", "Watch queues and agent status live, and react before service levels slip."),
 ("users", "Wallboards and dashboards", "Customisable wallboards and dashboards put the numbers that matter in front of the whole team."),
 ("headset", "Listen, whisper and barge", "Supervisors can listen in, coach an agent privately or join a call when needed."),
 ("mobile", "Supervise on the go", "A mobile supervisor app keeps managers connected away from the desk."),
 ("clip", "Reports", "Template and customisable reports on history, exportable in several formats, with API access to live and historic data."),
 ("clock", "Customer journey analytics", "See what happens across a customer's contacts, not just a single call."),
])}
</div></section>

<section><div class="wrap">
{feature("Quality and workforce", "Raise quality and plan the right team", "Quality and workforce tools turn contact centre data into better coaching and better rotas. 8x8 states that workforce management is now included in its contact centre packages, so check the current terms when you choose.", ["Agent scoring, plus call and screen recording", "AI scoring of eligible interactions, so quality checks cover far more than a small sample", "Forecasting and scheduling to match staff to demand", "Holiday planning and shift patterns", "Adherence and historic data to learn from past demand"], "clip", flip=True)}
</div></section>

<section class="alt"><div class="wrap">
{heading("Analytics and AI", "Understand every conversation, and automate the easy ones")}
{cards([
 ("signal", "Conversation analytics", "Capture every conversation to spot trends, understand sentiment, coach agents and support compliance."),
 ("chat", "Speech analytics", "Search and analyse what is said, not just who called."),
 ("cloud", "Virtual agent", "An intelligent customer assistant offers voice and digital self-service, so routine requests are handled around the clock."),
 ("route", "AI-powered IVR", "Let callers say what they need instead of pressing through menus."),
 ("users", "Sentiment insight", "Spot frustrated customers early and guide agents in the moment."),
 ("wrench", "Open APIs", "Pull live and historic data into your own dashboards or connect other systems."),
])}
<p class="vendor-note">AI features are described by 8x8 and depend on package and configuration. We confirm what is included in your quote.</p>
</div></section>

<section><div class="wrap">
{heading("Where it fits", "8x8, 3CX or a larger platform?", "Contact centre needs range from a small queue to a large multi-channel operation.")}
<div class="table-wrap"><table><thead><tr><th scope="col">Option</th><th scope="col">Best for</th><th scope="col">Highlights</th></tr></thead><tbody>
<tr><th scope="row"><a href="3cx-ai-analytics.html">3CX built-in</a></th><td>Smaller teams</td><td>Queues, wallboard, recording and reports included with the phone system</td></tr>
<tr><th scope="row">8x8 contact centre</th><td>Growing and mid-size teams that want omnichannel, quality and workforce tools</td><td>Omnichannel, quality management, workforce management, analytics and AI</td></tr>
<tr><th scope="row"><a href="contact-centres.html">Avaya and others</a></th><td>Large or complex operations</td><td>Tailored design and integration for demanding requirements</td></tr>
</tbody></table></div>
</div></section>

<section class="alt"><div class="wrap">
{heading("Resilience", "Built to scale and stay up")}
<div class="grid g3">
<div class="card"><h3>Scales with demand</h3><p>A cloud design adds capacity as demand rises, so busy periods do not need extra hardware.</p></div>
<div class="card"><h3>Reliable</h3><p>8x8 states a 99.999% uptime SLA across its platform. <a href="8x8-security.html">Security and reliability</a></p></div>
<div class="card"><h3>UK-aware</h3><p>Recordings and data handling can be discussed against your compliance needs. Tell us your requirements and we will confirm.</p></div>
</div></div></section>

<section><div class="wrap">
{heading("The process", "How a contact centre project works")}
{steps([("Plan", "We review contact volumes, channels, opening hours and the systems you use."), ("Design", "We design queues, IVR menus and routing rules with your team."), ("Build and connect", "We configure the platform and link your CRM and other tools."), ("Train and go live", "We train agents and supervisors, then support the launch and tune reports.")])}
</div></section>""",
    [("Which channels does the 8x8 contact centre support?", "Voice, web chat, email, SMS and messaging channels such as WhatsApp, Facebook Messenger, Viber and RCS, plus video, in a single agent interface."),
     ("Can agents work from home?", "Yes. Agents can use a computer, an IP phone or a mobile app, so home and hybrid agents get the same tools as the office."),
     ("Does it integrate with our CRM?", "Yes. It integrates with Salesforce, Dynamics, NetSuite and Zendesk, and open APIs cover others. See <a href='8x8-integrations.html'>integrations</a>."),
     ("What is the difference between quality management and workforce management?", "Quality management scores and reviews interactions to improve how agents handle customers. Workforce management forecasts demand and schedules staff to meet it."),
     ("Can it make outbound calls?", "Yes. An auto dialler supports predictive, progressive and preview modes for campaigns."),
     ("When would 3CX be a better fit?", "For smaller teams that mainly need queues, wallboards and recording, the contact centre tools in 3CX may be enough. See <a href='3cx-ai-analytics.html'>3CX AI and analytics</a>.")],
    "Tell us about your team, channels and call volumes and we will recommend an 8x8 contact centre set-up.")

# --- Integrations ---
x8_page("8x8-integrations.html", "8x8 Integrations: Microsoft Teams, CRM and APIs | Extera Limited",
    "8x8 integrates with Microsoft Teams, Salesforce, Dynamics 365, Zendesk, NetSuite and calendars, with open APIs for your own tools.",
    "8x8", "Integrations", "Keep using Microsoft Teams, Salesforce and the tools you know, with 8x8 calling built in.", "Integrations",
    feature("Integrations", "8x8 that works alongside your other tools", "8x8 connects to the systems your team already uses. Keep your main workspace, whether that is Microsoft Teams or your CRM, and bring calling, recordings and contact centre tools into it.", ["Microsoft Teams calling through direct routing", "Salesforce, Dynamics 365, Zendesk and NetSuite", "Microsoft and Google calendars", "Open APIs for custom integrations"], "route", cta=QUOTE8),
    f"""<section class="alt"><div class="wrap">
{feature("Microsoft Teams", "Keep Teams, add 8x8 calling", "8x8 Voice for Microsoft Teams uses cloud-to-cloud direct routing, so staff make and receive 8x8 calls from the Teams interface they already use.", ["Call from inside Teams using your business numbers", "Access 8x8 voicemail, transcripts and call recordings in Teams", "Contact centre agents can handle contacts without leaving Teams", "Calls analysed with 8x8 speech analytics where enabled"], "users", flip=True)}
<p class="vendor-note">Teams calling needs a suitable Microsoft licence. Requirements change, so we check them with you first.</p>
</div></section>
<section><div class="wrap">
{heading("Business apps", "CRM and helpdesk integrations")}
{cards([
 ("clip", "Salesforce", "Show customer records on incoming calls and log calls and recordings against the contact."),
 ("building", "Microsoft Dynamics 365", "Link calls, contacts and cases between 8x8 and Dynamics."),
 ("headset", "Zendesk", "Connect support tickets with phone and chat contacts."),
 ("cart", "NetSuite", "Bring customer and order context into the conversation."),
 ("clock", "Calendars", "Schedule meetings from Microsoft and Google calendars."),
 ("wrench", "Open APIs", "Connect other systems or build your own tools using documented APIs."),
])}
</div></section>
<section class="alt"><div class="wrap">
{heading("What it saves", "Less typing, better records")}
<div class="grid g3">
<div class="card"><h3>Screen pop</h3><p>The customer record opens as the call arrives, so agents are ready before they answer.</p></div>
<div class="card"><h3>Automatic logging</h3><p>Calls, transcripts and recordings link back to the CRM record without manual notes.</p></div>
<div class="card"><h3>One workspace</h3><p>Staff stay in the app they know, with 8x8 adding calling and contact centre power underneath.</p></div>
</div></div></section>""",
    [("Do I need to leave Microsoft Teams to use 8x8?", "No. 8x8 Voice for Microsoft Teams lets you call from inside Teams, using 8x8 as the phone service."),
     ("Which CRMs does 8x8 connect to?", "Salesforce, Microsoft Dynamics 365, Zendesk and NetSuite, with open APIs for others."),
     ("Can calls be logged automatically?", "Yes. Calls, recordings and, where enabled, transcripts can be attached to CRM records."),
     ("Is 3CX better for integrations?", "Both integrate well. 3CX also works with Microsoft 365 and major CRMs. See <a href='3cx-integrations.html'>3CX integrations</a>.")],
    "Tell us which tools you use and we will plan how 8x8 connects to them.")

# --- Security and reliability ---
x8_page("8x8-security.html", "8x8 Security, Reliability and Support | Extera Limited",
    "8x8 security and reliability: a 99.999% uptime SLA, multi-factor authentication, recognised certifications and what your network needs.",
    "Security", "and Reliability", "A platform built to stay up and stay secure, and a clear view of what it means for your network.", "Security and Reliability",
    feature("Security and reliability", "A platform built to stay secure and stay up", "8x8 runs its platform across many data centres with a stated 99.999% uptime SLA. Security measures are designed into access, data transfer and testing. These figures are 8x8's own, so we show you the detail and check it against your requirements.", ["A financially backed 99.999% uptime SLA, as stated by 8x8", "Mandatory multi-factor authentication for access", "Encrypted data in transit using TLS 1.2 or higher", "External penetration testing at least every six months"], "shield", cta=QUOTE8),
    f"""<section class="alt"><div class="wrap">
{heading("Certifications", "Recognised standards", "8x8 lists these certifications and assessments. We can obtain current certificates for your due diligence.")}
<ul class="badges"><li>ISO/IEC 27001</li><li>PCI DSS</li><li>Cyber Essentials and Cyber Essentials Plus</li><li>SOC 2</li><li>ISO 9001</li><li>CSA STAR (self-assessment)</li></ul>
<p class="vendor-note" style="text-align:center">The scope of each certification differs. Ask us for the current certificates and what they cover.</p>
</div></section>
<section><div class="wrap">
{heading("Reliability", "What the SLA means in practice")}
{cards([
 ("cloud", "Many data centres", "8x8 states that it runs from 35+ data centres, so no single site is a point of failure."),
 ("clock", "Service credits", "If the SLA is missed you can claim service credits, within the time limits in your contract. We help you check the terms."),
 ("wrench", "No downtime for upgrades", "8x8 states that planned maintenance is designed not to disrupt service."),
])}
</div></section>
<section class="alt"><div class="wrap">
{heading("Your side", "What your network needs", "Cloud voice depends on your own network. We check these in the survey.")}
{cards([
 ("wifi", "Bandwidth", "Enough upload and download for your calls and video. See <a href='fibre-broadband.html'>fibre broadband</a> and <a href='leased-lines.html'>leased lines</a>."),
 ("route", "Quality of service", "Router and firewall settings that give voice priority so calls stay clear."),
 ("shield", "Firewall rules", "The correct rules and whitelisting for 8x8 traffic, so nothing is blocked."),
 ("signal", "Backup", "A second route or automatic failover for sites that cannot be offline. See <a href='backup-connectivity.html'>4G/5G backup</a>."),
 ("phone", "Handsets and browsers", "Supported desk phones, browsers and devices, checked before go-live."),
 ("clip", "Number porting", "A planned cutover of your numbers, so nothing is missed. See <a href='business-lines.html'>lines and calls</a>."),
])}
</div></section>
<section><div class="wrap">
{heading("Going live", "How onboarding and support work")}
{steps([("Kick-off", "We confirm scope, timescales and who does what."), ("Design", "We plan call flows, users, devices and number porting."), ("Configure and test", "We build the system, train administrators and test it."), ("Go live and support", "We cut over, port numbers and move you onto ongoing support.")])}
<p class="vendor-note" style="margin-top:24px">8x8 provides its own tiered support, and we remain your first point of contact. Response targets vary by tier and issue priority, so ask us for the service levels that apply to you.</p>
</div></section>""",
    [("Where is my data stored?", "8x8 may store or process data in the UK, the EEA or other locations, and customers cannot always choose the location. If you have residency requirements, tell us and we will confirm before you commit."),
     ("How is access secured?", "Multi-factor authentication is mandatory, and data in transit is encrypted with TLS 1.2 or higher."),
     ("What happens to my data when I leave?", "You can export data before your contract ends using built-in tools or APIs. Timescales for deletion and any fees depend on your contract, so we check these with you."),
     ("Who do I call for support?", "Call us first. We handle issues with you and escalate to 8x8 where needed."),
     ("Is 99.999% uptime guaranteed?", "It is 8x8's stated SLA, with service credits if it is missed. It applies to the 8x8 platform, so a reliable connection and backup at your end still matter.")],
    "Tell us your security and compliance requirements and we will check them against 8x8.")


# ---------- 3CX vs 8x8 ----------
# Written from G2 review data and each vendor's own published pages (cited in the References list on the page).
def cite(*nums):
    return "<sup class=\"cite\">" + ",".join(f'<a href="#ref-{n}" aria-label="Reference {n}">{n}</a>' for n in nums) + "</sup>"


G2_ROWS = [
    # label, [3CX, 8x8 Work, 8x8 Contact Center], True if higher is better
    ("Overall rating (out of 5)", [4.4, 4.2, 4.1], True),
    ("Number of reviews", [548, 939, 261], None),
    ("Ease of use", [9.0, 8.6, 8.3], True),
    ("Ease of setup", [8.8, 8.3, 7.8], True),
    ("Ease of admin", [9.0, 8.4, 8.2], True),
    ("Meets requirements", [8.9, 8.6, 8.4], True),
    ("Quality of support", [7.9, 8.1, 8.1], True),
    ("Good partner in doing business", [8.6, 8.5, 8.5], True),
    ("Product direction (% positive)", [8.4, 7.9, 7.9], True),
    ("Time to implement (months)", [1, 2, 2], False),
    ("Time to see a return (months)", [11, 13, 16], False),
]


def g2_table():
    """Tabulated G2 scores. The best value in each row is highlighted; ties are all highlighted."""
    rows = ""
    for label, vals, higher in G2_ROWS:
        best = None if higher is None else (max(vals) if higher else min(vals))
        cells = ""
        for v in vals:
            txt = f"{v:,}" if isinstance(v, int) else f"{v:.1f}"
            cells += f'<td class="{"best" if best is not None and v == best else ""}">{txt}</td>'
        rows += f'<tr><th scope="row">{label}</th>{cells}</tr>'
    return (f'<div class="table-wrap"><table class="g2"><caption class="sr-only">G2 review scores for 3CX, 8x8 Work and 8x8 Contact Center</caption>'
            f'<thead><tr><th scope="col">G2 measure</th><th scope="col">3CX</th><th scope="col">8x8 Work</th><th scope="col">8x8 Contact Center</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div>')


REFS = [
    ("G2", "3CX vs. 8x8 Work comparison", "https://www.g2.com/compare/3cx-vs-8x8-work"),
    ("G2", "3CX vs. 8x8 Contact Center comparison", "https://www.g2.com/compare/3cx-vs-8x8-contact-center"),
    ("G2", "3CX reviews", "https://www.g2.com/products/3cx/reviews"),
    ("3CX", "3CX as an 8x8 alternative", "https://www.3cx.com/phone-system/8x8-alternative/"),
    ("3CX", "3CX licensing: size the system, not the user count", "https://www.3cx.com/blog/channel-partners/how-licensing-works/"),
    ("8x8", "Platform resilience for your business", "https://www.8x8.com/solutions/business-continuity"),
    ("8x8", "8x8 product features", "https://www.8x8.com/products/features"),
    ("8x8", "8x8 communications solutions for UK healthcare", "https://www.8x8.com/en-gb/solutions/uk-health-and-care"),
]
refs_html = "".join(
    f'<li id="ref-{i}"><b>{src}:</b> <a href="{url}" rel="noopener" target="_blank">{title}</a></li>' for i, (src, title, url) in enumerate(REFS, 1))

body = f"""
<section><div class="wrap">
{heading("The short answer", "Which one is right for you?", "Both are good business phone systems. They suit different businesses, and the right choice usually comes down to who looks after the system and how much your team lives on the phone.")}
<div class="grid g2">
<div class="card verdict"><h3>Choose 3CX if&hellip;</h3>{ticks(["You want the lowest running cost and predictable pricing", "You want control over where it runs, your handsets and your SIP trunks", "You have IT help, or a partner like Extera to look after it", "Your contact centre needs are queues, wallboards and reporting", "You want to keep existing phones, lines or equipment"])}<div class="actions left"><a class="btn outline dark" href="3cx.html">See 3CX</a></div></div>
<div class="card verdict"><h3>Choose 8x8 if&hellip;</h3>{ticks(["You want one hosted service with nothing to run or maintain", "You want a full omnichannel contact centre with quality and workforce tools", "You make a lot of international calls and want bundled calling", "You live in Microsoft Teams and want calling inside it", "You prefer a predictable per-user monthly price"])}<div class="actions left"><a class="btn outline dark" href="8x8.html">See 8x8</a></div></div>
</div>
</div></section>

<section class="alt"><div class="wrap">
{heading("Side by side", "How they compare", "A plain-English comparison. Numbers in brackets point to the sources listed at the end.")}
<div class="table-wrap"><table><thead><tr><th scope="col"></th><th scope="col">3CX</th><th scope="col">8x8</th></tr></thead><tbody>
<tr><th scope="row">How it runs</th><td>Software you run onsite, in your own cloud or hosted by a partner</td><td>A fully hosted cloud service run by 8x8</td></tr>
<tr><th scope="row">How it is priced</th><td>A flat annual licence sized by the number of simultaneous calls, not users{cite(4, 5)}</td><td>A monthly price per user, depending on the plan you choose{cite(4)}</td></tr>
<tr><th scope="row">What is included</th><td>3CX lists telephony, video, live chat, contact centre tools, AI transcription, apps and CRM integration in the licence{cite(4)}</td><td>Voice, meetings and team chat, with contact centre, AI and some calling bundles in higher tiers{cite(7)}</td></tr>
<tr><th scope="row">Handsets</th><td>Choose your own SIP phones{cite(4)}</td><td>Handsets or the app, and we advise on what to buy</td></tr>
<tr><th scope="row">Calls and numbers</th><td>Bring your own SIP trunk and numbers, so you choose the provider</td><td>Calling plans bundled, with the amount depending on your plan</td></tr>
<tr><th scope="row">Contact centre</th><td>Queues, ring groups, wallboards, recording and reporting built in; best for smaller inbound teams</td><td>A full contact centre platform with routing, IVR, quality and workforce management and AI{cite(7)}</td></tr>
<tr><th scope="row">Reliability</th><td>Depends on how and where you host it, and on your trunks</td><td>A financially backed, platform-wide uptime SLA of 99.999% for both voice and contact centre, on mirrored data centres{cite(6)}</td></tr>
<tr><th scope="row">Data location</th><td>You decide where it runs</td><td>Mirrored data centres in many regions, with local data residency options, and ring-fenced UK data for UK healthcare{cite(9, 8)}</td></tr>
<tr><th scope="row">Upkeep</th><td>You or your partner manage updates and monitoring (a hosted option reduces this)</td><td>8x8 runs and updates the platform</td></tr>
<tr><th scope="row">Best suited to</th><td>Small and medium UK businesses focused on domestic calling, and teams that want flexibility</td><td>Multi-site and international businesses, and multichannel contact centres</td></tr>
</tbody></table></div>
</div></section>

<section><div class="wrap">
{heading("What reviewers say", "Independent review scores from G2", "G2 collects verified user reviews. Scores are shown as listed on G2 and change over time.")}
{g2_table()}
<p class="vendor-note">Scores are from G2{cite(1, 2)}. Ratings are out of 5, and the measures below them are scored out of 10. The best result in each row is highlighted, and shorter is better for the two time measures. Reviewers are mostly mid-sized businesses for 3CX (55%) and small businesses for 8x8 Work (54%), so the scores reflect slightly different customers. Implementation and return times are typical reviewer experiences, not promises.</p>
<div class="grid g3" style="margin-top:32px">
<div class="card"><h3>3CX reviewers mention</h3><p>Ease of use and reliability come up most often. The most common complaints are complex processes and difficult configuration{cite(1, 3)}, which is where a partner who sets it up for you helps.</p></div>
<div class="card"><h3>8x8 Work reviewers mention</h3><p>Ease of use and easy communication lead the praise, followed by customer service and customer support{cite(1)}. It is most popular with small businesses and distributed teams.</p></div>
<div class="card"><h3>8x8 Contact Center reviewers mention</h3><p>Ease of use and helpfulness are the strongest themes. Missing features and poor customer support are the most common complaints{cite(2)}, so it is worth testing support response before you commit.</p></div>
</div>
</div></section>

<section class="alt"><div class="wrap">
{heading("What the vendors say", "In their own words", "Each vendor describes its strengths. Treat these as claims, and check them against your own quotes.")}
<div class="grid g2">
<div class="card"><h3>3CX says</h3><ul class="ticks"><li>It is licensed by simultaneous calls on a flat annual fee per system, so you can support more users without buying a licence per person{cite(4, 5)}</li><li>A single licence covers telephony, video, live chat, contact centre tools, AI transcription, apps and CRM integration, with no add-on or activation fees{cite(4)}</li><li>You can choose your own IP phones{cite(4)}</li><li>It is typically cheaper than per-user cloud pricing. 3CX's own illustration compares a 16-call system for up to 80 users with a per-user system at an assumed $15 per user per month, so check this against real quotes{cite(4)}</li></ul><p class="vendor-note">The licensing page also cautions that fewer licences does not mean unlimited extensions: you still size the system for the calls it must handle.{cite(5)}</p></div>
<div class="card"><h3>8x8 says</h3><ul class="ticks"><li>Its platform carries a 99.999% uptime commitment for both unified communications and contact centre, described as financially backed{cite(6, 7)}</li><li>Services run from mirrored, geographically diverse data centres with four levels of redundancy, across 34 cloud regions on five continents{cite(6, 7)}. Its contact centre page lists 35 data centre locations{cite(9)}</li><li>It offers voice, meetings, messaging and a contact centre on one platform, with free calling to up to 48 countries on higher plans, excluding mobile and special numbers in some countries{cite(7)}</li><li>For UK healthcare it highlights ring-fenced UK data{cite(8)}</li></ul><p class="vendor-note">Always confirm the SLA, service credits and any conditions in your contract, as the headline figure is a platform commitment.{cite(6, 7)}</p></div>
</div>
</div></section>

<section><div class="wrap">
{heading("The real cost", "Compare the whole bill, not just the licence", "The licence is only part of what you pay over three years. Ask for quotes that include everything on this list.")}
<div class="table-wrap"><table><thead><tr><th scope="col">Cost</th><th scope="col">3CX</th><th scope="col">8x8</th></tr></thead><tbody>
<tr><th scope="row">Licence or subscription</th><td>Annual licence sized by simultaneous calls</td><td>Monthly per user, by plan</td></tr>
<tr><th scope="row">Calls and numbers</th><td>SIP trunk, numbers and call charges from your chosen provider</td><td>Mostly bundled, with extra voice lines and some destinations charged separately</td></tr>
<tr><th scope="row">Hosting</th><td>Hosted fee, or your own server and upkeep</td><td>Included</td></tr>
<tr><th scope="row">Handsets</th><td>Your choice of SIP phones</td><td>Handsets or app</td></tr>
<tr><th scope="row">Set-up</th><td>Partner project fee</td><td>Deployment or project fee</td></tr>
<tr><th scope="row">Extras</th><td>Few; most features are in the licence</td><td>AI tools and some contact centre options may be priced separately</td></tr>
<tr><th scope="row">Support</th><td>Partner support or maintenance contract</td><td>Included in tiers, with higher tiers adding extra cover</td></tr>
<tr><th scope="row">Internet and backup</th><td>Needed for any VoIP: see <a href="connectivity.html">connectivity</a></td><td>Needed for any VoIP: see <a href="connectivity.html">connectivity</a></td></tr>
</tbody></table></div>
<p class="vendor-note">We show prices in pounds and with the same assumptions side by side when we quote, so you can compare like with like.</p>
</div></section>

<section class="alt"><div class="wrap">
{heading("By situation", "What we would recommend")}
<div class="table-wrap"><table><thead><tr><th scope="col">Your situation</th><th scope="col">Our usual advice</th></tr></thead><tbody>
<tr><th scope="row">Small office, mostly UK calls, someone to manage it</th><td>3CX, hosted or onsite</td></tr>
<tr><th scope="row">No IT staff and you want nothing to look after</th><td>8x8, or hosted 3CX that we manage for you</td></tr>
<tr><th scope="row">A small inbound team handling customer calls</th><td>3CX, with its built-in queues and wallboard</td></tr>
<tr><th scope="row">A multichannel contact centre or a larger team</th><td>8x8 contact centre, or a larger platform. See <a href="contact-centres.html">contact centres</a></td></tr>
<tr><th scope="row">Lots of international calls</th><td>8x8 with bundled international calling</td></tr>
<tr><th scope="row">Calling inside Microsoft Teams</th><td>8x8 for Teams, or 3CX with Microsoft 365 sync</td></tr>
<tr><th scope="row">You want to keep your existing handsets and lines</th><td>3CX</td></tr>
<tr><th scope="row">Hotels and hospitality</th><td>3CX, which includes a hotel module</td></tr>
</tbody></table></div>
</div></section>

<section><div class="wrap narrow">
{heading("Our view", "We supply both, so we have no reason to push one")}
<p>Extera supplies, installs and supports 3CX and 8x8. We would rather you chose the right one than the one with the biggest margin. If you tell us how many people you have, how much you rely on calls and who will look after the system, we will tell you honestly which fits, and quote both so you can compare.</p>
<div class="actions left"><a class="btn" href="contact.html">Get a side-by-side quote</a><a class="btn outline dark" href="3cx.html">See 3CX</a><a class="btn outline dark" href="8x8.html">See 8x8</a></div>
</div></section>

{faq([
 ("Is 3CX or 8x8 cheaper?", "3CX usually costs less in licence fees, because it is a flat annual licence rather than a per-user subscription. The gap narrows once you add hosting, SIP calling, handsets and support, so compare the full cost over three years."),
 ("Which is easier to manage?", "8x8, because 8x8 runs the platform. 3CX scores highly for ease of use and admin on G2, and we can manage it for you if you do not want to look after it yourself."),
 ("Which has the better contact centre?", "8x8 has a fuller contact centre, with omnichannel routing, quality and workforce management and AI. 3CX has solid built-in queues, wallboards and reporting, which suit smaller teams."),
 ("Can I move from one to the other later?", "Yes. Numbers can be ported between them, though it is a project, so it helps to choose well first."),
 ("Can you quote both?", "Yes. We quote both with the same assumptions so the figures are directly comparable."),
], alt=True)}

<section><div class="wrap narrow">
{heading("Sources", "References")}
<ol class="refs">{refs_html}</ol>
<p class="vendor-note">Compiled from G2 review pages and each vendor's published pages. G2 scores and 8x8 figures were read from the live pages in October 2026. Ratings, prices and vendor claims change, so check the sources for the latest. Where a figure is a vendor claim we say so.</p>
</div></section>
{cta_band("Tell us about your team and we will quote 3CX and 8x8 side by side.", "Get a side-by-side quote")}
"""
page("3cx-vs-8x8.html", "3CX vs 8x8: Which Business Phone System Is Right for You? | Extera Limited",
     "A plain-English comparison of 3CX and 8x8: pricing, contact centre, reliability and support, with G2 review scores and vendor information.",
     body, hero("3CX", "vs 8x8", "Which one suits your business? A plain-English comparison with independent review scores and vendor facts.", small=True, actions=[("Get a side-by-side quote", "contact.html", False, False), (f"Call {PHONE}", f"tel:{TEL}", True, False)], eyebrow="Comparison"), "3CX vs 8x8")


# ---------- Contact centres ----------
body = f"""
<section><div class="wrap">
{feature("Contact centres", "Built for teams that live on the phone", "A contact centre system helps you answer every call, route it to the right person and see how your team is performing. We design, install and support solutions from basic call queues to full multichannel contact centres.", ["Call queues and intelligent routing", "Call recording and quality monitoring", "Real-time wallboards and reporting", "Integration with your CRM"], "headset", cta=("Talk to a specialist", "contact.html"))}
</div></section>
<section class="alt"><div class="wrap">
{heading("Capabilities", "What a modern contact centre can do")}
{cards([
 ("route", "Skills-based routing", "Send callers to the agent best placed to help, and reduce transfers."),
 ("chat", "Multichannel", "Handle calls, chat and email in a single agent view."),
 ("signal", "Live reporting", "Wallboards and reports for supervisors and managers."),
 ("shield", "Recording and compliance", "Record, store and search calls to support training and compliance."),
 ("users", "Home and remote agents", "Let agents work from anywhere on the same system."),
 ("clip", "CRM screen pop", "Show customer details to the agent as the call arrives."),
])}
</div></section>
<section><div class="wrap">
{heading("Platforms", "Choose the platform that fits")}
<div class="grid g3">
<div class="card"><h3>Avaya</h3><p>Mid-market and contact centre solutions from a long-standing Avaya Silver Partner.</p></div>
<div class="card"><h3>8x8</h3><p>Cloud contact centre alongside hosted voice, with nothing to host yourself. <a href="8x8.html">8x8 details</a></p></div>
<div class="card"><h3>3CX</h3><p>Call queues, wallboards, recording and reporting are built in. <a href="3cx-ai-analytics.html">3CX contact centre tools</a></p></div>
</div></div></section>
<section class="alt"><div class="wrap">
{heading("Call queue or contact centre?", "Contact centre software or a simple call queue?", "Most phone systems include basic queues. A contact centre adds the tools to manage people and customer experience.")}
{spec_table(["", "Call queue (phone system)", "Contact centre"], [
 ("Routing", "Ring groups and simple queues", "Skills-based, priority and time-of-day routing"),
 ("Channels", "Voice", "Voice, chat, email, SMS and social in one view"),
 ("Supervision", "Basic call lists", "Live wallboards, listen-in, whisper and barge"),
 ("Reporting", "Call logs", "Service levels, abandoned calls, agent and queue trends"),
 ("Customer data", "Caller ID only", "CRM screen pop and a history of past contact"),
 ("Best for", "Small teams answering general calls", "Teams where every call and every minute counts"),
])}
</div></section>
<section><div class="wrap">
{heading("Measuring success", "Contact centre metrics that matter")}
{cards([
 ("clock", "Average wait time", "How long callers wait before an agent answers, by queue and hour of day."),
 ("phone", "Abandoned calls", "Callers who hang up before they are answered, a direct sign you need more cover or better routing."),
 ("users", "First-contact resolution", "How often a customer is helped without a second call, supported by CRM history."),
 ("signal", "Service level", "The share of calls answered within your target time, tracked live on a wallboard."),
 ("shield", "Quality scores", "Recorded calls reviewed against a checklist to coach agents and protect compliance."),
 ("clip", "Occupancy and shrinkage", "How busy agents are and how much time is lost to breaks and training, so rotas match demand."),
])}
</div></section>
<section class="alt"><div class="wrap">
{heading("Getting started", "How a contact centre project works")}
{steps([("Understand", "We look at call volumes, opening hours, channels and the systems agents use."), ("Recommend", "We match your needs to Avaya, 8x8 or 3CX and explain the trade-offs."), ("Build", "We configure queues, IVR menus, reporting and CRM links, and supply headsets."), ("Train and support", "We train supervisors and agents, then support the system after go-live.")])}
</div></section>
{faq([("How big does a team need to be?", "We work with teams from a handful of agents to larger operations. Tell us your numbers and we will recommend a platform."), ("Can agents work from home?", "Yes. Modern platforms support remote agents with the same features as the office."), ("Do you provide headsets?", "Yes. We are Jabra and Plantronics partners and also supply headsets through <a href='extera-direct.html'>Extera Direct</a>."), ("Can we add a contact centre to our existing phone system?", "Often, yes. 3CX, 8x8 and Avaya IP Office all have contact centre options. We check what you have and tell you whether to add to it or replace it."), ("What does call recording involve for compliance?", "You need to tell callers they may be recorded and decide how long to keep recordings. We set up announcements, retention and access controls, but you should take your own advice on regulatory requirements."), ("How long does a contact centre take to set up?", "A basic queue can be live quickly. A full multichannel set-up with CRM integration takes longer, and we agree a timeline when we quote.")], alt=True)}
{cta_band("Tell us about your team and call volumes and we will recommend a contact centre solution.")}
"""
page("contact-centres.html", "Contact Centre Solutions | Extera Limited",
     "Contact centre systems from Extera: call queues, routing, recording and reporting on Avaya, 8x8 and 3CX platforms.",
     body, hero("Contact", "Centres", "Answer every call and serve every customer, with queues, routing, recording and reporting that fit your team.", small=True, eyebrow="Phone systems"), "Contact Centres")

# ---------- Connectivity ----------
CONN = [
    # (slug file, nav label, icon, card title, card blurb)
    ("fibre-broadband.html", "Fibre Broadband", "wifi", "Fibre broadband", "FTTC, SOGEA and full fibre (FTTP) broadband for offices of any size."),
    ("leased-lines.html", "Leased Lines", "bolt", "Leased lines", "Dedicated, uncontended internet and Ethernet circuits with speeds and SLAs to suit."),
    ("mpls.html", "MPLS", "route", "MPLS", "Private networks joining your sites securely with managed quality of service."),
    ("sip-trunks.html", "SIP Trunks", "phone", "SIP trunks", "Voice over IP trunks with free-calls bundles, the modern replacement for ISDN."),
    ("business-lines.html", "Lines and Calls", "clock", "Lines and calls", "PSTN, analogue and ISDN lines, call packages and your move to digital voice."),
    ("backup-connectivity.html", "4G/5G Backup", "signal", "4G/5G backup", "Automatic failover so your phones and internet keep working if your main line drops."),
]


def conn_related(exclude):
    items = [(i, t, b, f, "Read more") for f, _, i, t, b in CONN if f != exclude]
    return f'<section class="alt"><div class="wrap">{heading("Connectivity", "Explore more connectivity", None)}{cards(items, link=True)}</div></section>'


def conn_page(fname, title, desc, h1a, h1b, hero_text, crumb, intro, benefits, detail, steps_list, faqs, cta_text, steps_title="How it works"):
    """Shared layout for connectivity sub-pages: intro, benefits, detail blocks, steps, FAQ, related, CTA."""
    body = f"""
<section><div class="wrap">{intro}</div></section>
<section class="alt"><div class="wrap">
{heading("Benefits", benefits[0], benefits[1])}
{cards(benefits[2])}
</div></section>
{detail}
<section class="alt"><div class="wrap">
{heading("The process", steps_title)}
{steps(steps_list)}
</div></section>
{faq(faqs)}
{conn_related(fname)}
{cta_band(cta_text)}
"""
    page(fname, title, desc, body, hero(h1a, h1b, hero_text, small=True, eyebrow="Connectivity"),
         f'<a href="connectivity.html">Connectivity</a> / {crumb}')


# --- Hub ---
body = f"""
<section><div class="wrap">
{heading("Connectivity", "Every kind of business connection", "Using our range of suppliers (Openreach, Virgin, TalkTalk, Vodafone, Virtual1, Gamma and Daisy) we can supply all your connectivity needs, and work out which combination suits each site.")}
{cards([(i, t, b, f, "Learn more") for f, _, i, t, b in CONN], link=True)}
</div></section>

<section class="alt"><div class="wrap">
{heading("Choosing", "Which connection is right for you?", "A guide, not a promise. Speeds and availability depend on your address, and we confirm what is available when we quote.")}
{spec_table(["Connection", "Best for", "Typical features"], [
 ('<a href="fibre-broadband.html">Fibre broadband (FTTC, SOGEA)</a>', "Small offices on a budget", "Shared, up to around 80Mbps download"),
 ('<a href="fibre-broadband.html#fttp">Full fibre (FTTP)</a>', "Most small and medium businesses", "Faster, with much higher upload, where available"),
 ('<a href="leased-lines.html">Leased line</a>', "Cloud-dependent or larger offices, hosted voice", "Dedicated, same speed up and down, SLA-backed fix times"),
 ('<a href="mpls.html">MPLS</a>', "Multi-site organisations", "Private network between sites with quality of service"),
 ('<a href="sip-trunks.html">SIP trunk</a>', "Replacing ISDN voice lines", "Phone lines delivered over your internet connection"),
 ('<a href="business-lines.html">Lines and calls</a>', "Sites still on PSTN or ISDN", "Analogue and ISDN lines and call packages while you transition"),
 ('<a href="backup-connectivity.html">4G/5G backup</a>', "Resilience for any site", "Automatic failover if your main line drops"),
])}
</div></section>

<section><div class="wrap">
{feature("ISDN and PSTN switch-off", "Plan your move away from ISDN now", "The UK telephone network is moving from copper lines to digital voice, and ISDN and analogue lines are being retired in stages. We move you to SIP trunks or broadband-based voice, keep your numbers, and time the change around your business.", ["Audit of every line, alarm and lift phone", "Number porting with no downtime", "SIP trunks with free-calls bundles", "Backup connectivity where you need it"], "clock", cta=("See the switch-off guide", "business-lines.html"))}
</div></section>

<section class="alt"><div class="wrap">
{heading("How we choose", "The right connection for each site", "We do not push one product. We look at what each site does, then recommend a connection and a backup.")}
{steps([("Understand", "How many people, which cloud and voice services, and how critical uptime is."), ("Check availability", "We check what is available at each address from our range of carriers."), ("Compare", "Clear options and prices, including backup and contract terms."), ("Install and manage", "We order, track the install and look after the service.")])}
</div></section>
{faq([
 ("How long does a leased line take to install?", "It depends on your address and whether new fibre needs to be laid. We give you a realistic timescale when we quote. See our <a href='leased-lines.html'>leased lines page</a>."),
 ("Can you provide backup internet?", "Yes. We can add a second line or a 4G/5G failover so your phones and internet keep working. See <a href='backup-connectivity.html'>4G/5G backup</a>."),
 ("Do SIP trunks come with free calls?", "Yes. We offer SIP trunks with free-calls bundles. Ask us for the bundle that suits your call patterns."),
 ("Can you connect all my sites?", "Yes. We can join sites with <a href='mpls.html'>MPLS</a> or other private networks, and add a single phone system across them."),
])}
{cta_band("Send us your postcodes and requirements and we will compare the options.")}
"""
page("connectivity.html", "Business Connectivity | Extera Limited",
     "Business broadband, fibre, leased lines, MPLS, SIP trunks and 4G/5G backup from Extera, using carriers including Openreach, Virgin, Gamma and Daisy.",
     body, hero("Business", "Connectivity", "The right connection for every site, from broadband to leased lines, with backup so you never go offline.", small=True, eyebrow="Connectivity"), "Connectivity")

# --- Fibre broadband ---
conn_page("fibre-broadband.html", "Business Fibre Broadband (FTTC, SOGEA, FTTP) | Extera Limited",
    "Business fibre broadband from Extera: FTTC, SOGEA and full fibre FTTP, with static IPs, backup options and support.",
    "Fibre", "Broadband", "Fast, reliable business broadband with proper support behind it, from FTTC to full fibre.", "Fibre Broadband",
    feature("Fibre broadband", "Fast, reliable broadband for your business", "Business broadband is not the same as home broadband. We supply business-grade fibre with static IP addresses, the right router and proper support, and we help you choose between the three main technologies: FTTC, SOGEA and full fibre (FTTP).", ["Business-grade support and fault handling", "Static IP addresses and routers available", "Options to add backup and phone services", "Clear advice on which technology fits your site"], "wifi", cta=("Check availability", "contact.html")),
    ("What you get", "Business broadband that keeps up", [
        ("bolt", "Faster uploads", "Full fibre gives much higher upload speeds, which matters for cloud backup, video calls and hosted voice."),
        ("shield", "Business support", "Proper fault handling and an account contact, not a call centre queue."),
        ("route", "Static IPs", "Fixed addresses for VPNs, remote access and CCTV."),
        ("phone", "Ready for digital voice", "Run your phones over the same connection with SIP trunks or a hosted system."),
        ("signal", "Add resilience", "Pair with 4G/5G backup so one fault does not stop the business."),
        ("clip", "One bill", "Broadband alongside phones, mobiles and cabling."),
    ], ),
    f"""<section><div class="wrap">
{heading("Technologies", "FTTC, SOGEA and FTTP compared", "Speeds depend on your line and address. We check availability before we quote.")}
{spec_table(["Technology", "How it works", "Typical speeds", "Best for"], [
 ("FTTC", "Fibre to the street cabinet, then copper to your premises. Ordered with a phone line.", "Up to around 80Mbps down and 20Mbps up", "Small offices on a budget"),
 ("SOGEA", "The same technology as FTTC, but ordered without the analogue phone line.", "Similar to FTTC", "Businesses moving to VoIP and away from the old phone line"),
 ('<span id="fttp">FTTP</span>', "Fibre all the way to your premises, with no copper in the final stretch.", "Around 100Mbps up to 1Gbps and beyond, depending on availability", "Most businesses, especially cloud-heavy teams"),
])}
</div></section>
<section class="alt"><div class="wrap">
{feature("Full fibre", "Why many businesses are moving to FTTP", "Full fibre runs fibre cable straight into your building. That gives more consistent speeds and much better upload speeds than copper-based services, and it future-proofs you as cloud and video use grows.", ["Consistent speeds, less affected by distance", "Much higher upload speeds than FTTC", "Supports hosted phone systems, cloud backup and video", "Often similar in price to FTTC"], "bolt", flip=True)}
</div></section>
<section><div class="wrap">
{feature("Need guaranteed speed?", "When broadband is not enough", "Broadband is shared and does not come with the guaranteed speed and fix times of a dedicated line. If your business depends on the internet all day, a leased line may be the better choice.", ["Dedicated, uncontended bandwidth", "Same speed up and down", "SLA-backed fix times"], "shield", cta=("See leased lines", "leased-lines.html"))}
</div></section>""",
    [("Check your address", "Send us your postcode and we check which technologies are available."), ("Choose", "We explain the options, speeds and prices in plain English."), ("Order and install", "We place the order and track the installation."), ("Connect", "We set up your router and look after the service.")],
    [("What is the difference between FTTC and FTTP?", "FTTC uses fibre to the street cabinet and copper from there to your premises. FTTP uses fibre the whole way, which is faster, more consistent and offers much better upload speeds."),
     ("What is SOGEA?", "SOGEA is FTTC broadband without the analogue phone line. Because there is no phone line, you make calls over the internet using VoIP or SIP."),
     ("Will I lose my phone number?", "No. Numbers can be moved to a SIP trunk or a hosted phone system. See our <a href='sip-trunks.html'>SIP trunks page</a>."),
     ("How long does installation take?", "It depends on the technology and your address. Where the building is already connected it can be quick; if new fibre or work needing landlord or council approval is needed it can take longer. We give you an honest estimate when we quote."),
     ("Is broadband good enough for hosted phones?", "Often yes, particularly full fibre. For larger teams, or where uptime is critical, we recommend a leased line or a backup connection.")],
    "Send us your postcode and we will tell you what is available.")

# --- Leased lines ---
conn_page("leased-lines.html", "Business Leased Lines | Extera Limited",
    "Business leased lines from Extera: dedicated, uncontended Ethernet and internet access with symmetrical speeds and SLA-backed support.",
    "Leased", "Lines", "A connection that is yours alone: dedicated speed, the same up and down, and fix times you can hold us to.", "Leased Lines",
    feature("Leased lines", "Your own dedicated connection", "A leased line is a private connection between your premises and the network, used by your business alone. It is not shared with other customers, so you get the speed you pay for, at the same speed uploading and downloading, with fix times backed by an SLA.", ["Dedicated and uncontended bandwidth", "Symmetrical speeds, the same up and down", "SLA-backed fault repair", "Easily scaled as you grow"], "bolt", cta=("Get a leased line quote", "contact.html")),
    ("Why choose a leased line", "Built for businesses that cannot afford downtime", [
        ("bolt", "Symmetrical speeds", "Upload as fast as you download, ideal for cloud, backups and video conferencing."),
        ("shield", "Guaranteed performance", "Dedicated bandwidth and an SLA, even at peak times."),
        ("phone", "Perfect for hosted voice", "Clear, low-latency calls for hosted phone systems and SIP trunks."),
        ("route", "Secure", "A private line, with support for firewalls, VPNs and encryption."),
        ("signal", "Scalable", "Increase bandwidth as your needs grow, without major changes."),
        ("headset", "Managed", "A supplied and configured router, with our team handling faults for you."),
    ]),
    f"""<section><div class="wrap">
{heading("Types", "Leased line options", "The right type depends on your location and how much bandwidth you need.")}
{spec_table(["Type", "What it is", "Best for"], [
 ("Fibre Ethernet leased line", "A dedicated fibre circuit, typically from 100Mbps up to 10Gbps.", "Larger offices, cloud-heavy and hosted voice users"),
 ("Dedicated internet access (DIA)", "A leased line carrying internet access, with a static IP range.", "Most businesses wanting reliable internet"),
 ("EFM (Ethernet in the First Mile)", "A dedicated service over bonded copper pairs, with lower speeds and often faster to install.", "Sites where fibre is not yet available"),
 ("Point-to-point Ethernet", "A private circuit connecting two of your sites.", "Linking offices or a data centre"),
])}
</div></section>
<section class="alt"><div class="wrap">
{heading("Understanding the quote", "Bearer and committed data rate", None)}
<div class="split"><div><p>Leased lines are quoted with two figures. The <b>bearer</b> is the maximum capacity of the circuit. The <b>committed data rate (CDR)</b> is the bandwidth you choose and pay for. For example, a 100Mbps service on a 1Gbps bearer can be upgraded later without new infrastructure.</p><p>That is why a leased line is easy to scale: increasing your bandwidth is often a simple change rather than a new install.</p></div>
<div class="card"><h3>Leased line or broadband?</h3><p>Choose a leased line if your team relies on cloud apps, hosted voice or video all day, or if you need guaranteed fix times. Broadband is fine for lighter use and tighter budgets. <a href="fibre-broadband.html">See fibre broadband</a>.</p></div></div>
</div></section>
<section><div class="wrap">
{feature("Resilience", "Add backup for true resilience", "Even a leased line can be cut by a digger. For sites that cannot go offline, we pair a leased line with a second connection or an automatic 4G/5G failover.", ["Second leased line on a diverse route", "Broadband backup", "4G/5G automatic failover"], "shield", flip=True, cta=("See 4G/5G backup", "backup-connectivity.html"))}
</div></section>""",
    [("Survey", "We check availability and the route to your building."), ("Quote", "A clear price, with speed, term and SLA options."), ("Build", "The carrier installs the circuit. Installation can take some weeks, longer if new fibre or landlord approval is needed."), ("Connect", "We configure the router and hand over a working service.")],
    [("How fast are leased lines?", "Common speeds range from 100Mbps up to 10Gbps, depending on location and need."),
     ("How long does installation take?", "Often a number of weeks, and longer where new fibre has to be laid or landlord or council permission is needed. We give you a realistic timescale in the quote."),
     ("Can I change my speed later?", "Usually you can increase bandwidth during the contract. Reductions are normally limited, so check the terms."),
     ("What equipment do I need?", "We supply a configured router with the service, and can add firewalls and switches as needed."),
     ("What if I move premises?", "Moving a leased line depends on the new address and the remaining contract term. Talk to us early.")],
    "Tell us your sites and what you use the internet for and we will quote.")

# --- MPLS ---
conn_page("mpls.html", "Business MPLS Networks | Extera Limited",
    "MPLS private networks from Extera for multi-site businesses: secure, managed connections with quality of service for voice and data.",
    "MPLS", "Networks", "One private network for all your sites, with voice and key applications given priority.", "MPLS",
    feature("MPLS", "One private network for all your sites", "MPLS (Multiprotocol Label Switching) links your offices over a carrier-managed private network rather than the public internet. Traffic is kept separate from other customers, and voice and critical applications can be prioritised.", ["Private, isolated connectivity between sites", "Quality of service for voice and video", "SLA-backed performance and repair", "One network manager to call"], "route", cta=("Discuss your sites", "contact.html")),
    ("Why MPLS", "Predictable performance across every site", [
        ("route", "Private network", "Your traffic is kept apart from the public internet and other customers."),
        ("phone", "Voice prioritised", "Quality of service keeps calls clear, even when the network is busy."),
        ("shield", "SLA-backed", "Committed performance and repair times you can hold us to."),
        ("building", "Sites work as one", "Any office can reach any other, as if on one network."),
        ("cloud", "Cloud connections", "Add secure access to cloud and data centre services."),
        ("wrench", "Managed for you", "We handle design, ordering and ongoing changes."),
    ]),
    f"""<section><div class="wrap">
{heading("Options", "MPLS, VPN or SD-WAN?", "MPLS is not the only way to link sites. We help you choose.")}
{spec_table(["Option", "How it works", "Strengths", "Watch out for"], [
 ("MPLS", "A private carrier-run network between sites.", "Quality of service, SLAs, privacy", "Slower to provision and change; usually costs more"),
 ("Site-to-site VPN", "Encrypted tunnels over normal internet connections.", "Low cost and quick to set up", "No guaranteed quality or SLA"),
 ("SD-WAN", "Software that manages several links, such as broadband, MPLS and 4G.", "Flexible, can combine links", "Performance depends on the underlying links"),
])}
<p style="margin-top:16px">Many organisations use a hybrid: MPLS or leased lines for critical sites, with broadband and 4G/5G links managed alongside. We will recommend whichever combination fits your sites and budget.</p>
</div></section>
<section class="alt"><div class="wrap">
{feature("Best fit", "When MPLS makes sense", "MPLS is a strong choice where voice quality and uptime across several sites really matter, or where you have compliance requirements for private networks.", ["Several offices sharing one phone system", "Voice and video between sites", "Regulated data that must stay off the public internet", "Branches that need guaranteed performance"], "building", flip=True)}
</div></section>""",
    [("Map your sites", "We list each site, its users and what it needs."), ("Design", "We design the network and agree the service levels."), ("Install", "Circuits are ordered, installed and tested."), ("Manage", "We support the network and handle changes.")],
    [("Is MPLS the same as a leased line?", "No. A leased line is a dedicated circuit from one site to the network or internet. MPLS is the private network that joins several sites together, and each site connects to it with a circuit such as a leased line."),
     ("Is MPLS secure?", "Traffic is carried over a private carrier network, kept separate from other customers. You can add encryption and firewalls where needed."),
     ("Is SD-WAN better than MPLS?", "It depends. SD-WAN is more flexible and often cheaper, while MPLS gives stronger guarantees for real-time traffic. Many businesses use both."),
     ("Can new sites be added easily?", "Yes, but provisioning a new circuit takes time, so plan ahead. We manage the process for you.")],
    "Tell us about your sites and we will recommend a network design.")

# --- SIP trunks ---
conn_page("sip-trunks.html", "SIP Trunks for Business | Extera Limited",
    "SIP trunks from Extera: replace ISDN lines with voice over IP, keep your numbers and get free-calls bundles.",
    "SIP", "Trunks", "Replace ISDN with phone lines over the internet, keep your numbers and often cut your call costs.", "SIP Trunks",
    feature("SIP trunks", "Replace ISDN with voice over IP", "A SIP trunk carries your phone calls over your internet connection instead of an ISDN or analogue line. You keep your numbers and your phone system, and you add or remove channels as needed without waiting for a new line.", ["Keep your existing phone numbers", "Add channels in minutes, not weeks", "Free-calls bundles to reduce call costs", "Reroute calls if a site is unavailable"], "phone", cta=("Get a SIP trunk quote", "contact.html")),
    ("Why SIP", "Lower costs, more flexibility", [
        ("clock", "No more line rental", "Move away from ISDN line rental and channel limits."),
        ("users", "Scale easily", "Add or remove channels as your call volumes change."),
        ("route", "Number portability", "Keep your numbers, even if you move premises."),
        ("shield", "Business continuity", "Divert calls to another site or mobile if your office is unavailable."),
        ("cloud", "Works with modern systems", "Compatible with 3CX and most IP-capable phone systems."),
        ("headset", "Remote-ready", "Route calls to home workers and mobiles."),
    ]),
    f"""<section><div class="wrap">
{heading("What you need", "What to check before you move")}
<div class="grid g3">
<div class="card"><h3>A SIP-compatible phone system</h3><p>SIP trunks replace the lines, not the phone system. Most modern IP systems, including <a href="3cx.html">3CX</a>, work with SIP. Older systems may need an adapter or an upgrade.</p></div>
<div class="card"><h3>Enough bandwidth</h3><p>Each simultaneous call needs roughly 100Kbps. We size your connection to your busiest call periods, and check upload speed too.</p></div>
<div class="card"><h3>A stable connection</h3><p>Call quality depends on your internet. We recommend a good broadband or <a href="leased-lines.html">leased line</a>, with <a href="backup-connectivity.html">backup</a> for critical sites.</p></div>
</div></div></section>
<section class="alt"><div class="wrap">
{heading("Channels", "How many channels do you need?", "A channel is one simultaneous call. Most small and medium businesses need somewhere between 4 and 20.")}
{spec_table(["Business size", "Typical channels", "Notes"], [
 ("Small office, up to 10 users", "2 to 6", "Depends on how many people are on calls at once"),
 ("Medium office, 10 to 50 users", "6 to 20", "Add more if you run a busy sales or support team"),
 ("Contact centre or large site", "20 and above", "Sized to peak call volumes"),
])}
</div></section>
<section><div class="wrap">
{feature("ISDN switch-off", "SIP is your route off ISDN", "ISDN and analogue lines are being retired by the telephone network operators. SIP trunks are the usual replacement, and we manage the move so your numbers carry on working.", ["Audit of every line and what depends on it", "Number porting without downtime", "Advice on alarms, lifts and card machines"], "clock", cta=("See the switch-off guide", "business-lines.html"))}
</div></section>""",
    [("Audit", "We review your lines, numbers, phone system and internet connection."), ("Design", "We agree the channels, bundles and any backup."), ("Set up and port", "We configure the trunks and move your numbers."), ("Switch over", "We cut over, test and support your team.")],
    [("Can I keep my phone numbers?", "Yes. Numbers are ported to your new service, including when you move to a different area. Porting takes a little time, so we plan it with you."),
     ("Do SIP trunks replace my phone system?", "No. They replace the telephone lines. You still need a phone system that supports SIP, such as <a href='3cx.html'>3CX</a>."),
     ("Is it cheaper than ISDN?", "Usually yes, because you pay no line rental per channel and calls are often cheaper or bundled. We show the comparison when we quote."),
     ("What if my internet goes down?", "Calls can be redirected to another number or site, and a backup connection keeps trunks running. See <a href='backup-connectivity.html'>4G/5G backup</a>."),
     ("How long does set-up take?", "Configuration is quick. Number porting is usually the longest part, so we plan the cutover date together.")],
    "Send us your current lines and we will price a SIP trunk replacement.")

# --- Lines and calls ---
conn_page("business-lines.html", "Business Phone Lines and ISDN Switch-Off | Extera Limited",
    "Business phone lines, call packages and ISDN/PSTN switch-off guidance from Extera. We audit your lines and move you to digital voice.",
    "Lines", "and Calls", "Keep your phone lines working today and plan a calm move to digital voice before the switch-off.", "Lines and Calls",
    feature("Lines and calls", "Phone lines, calls and the move to digital", "Many businesses still rely on analogue and ISDN lines. We keep them running while you need them, supply call packages, and plan your move to digital voice before the lines are switched off.", ["Analogue (PSTN) and ISDN lines", "Call packages and bundles", "Number porting to SIP or hosted voice", "Help with alarms, lifts and card machines"], "clock", cta=("Check your lines", "contact.html")),
    ("What we supply", "Lines and calls for every business", [
        ("phone", "Analogue lines", "Single PSTN lines for sites that still need them."),
        ("server", "ISDN lines", "ISDN2 and ISDN30 for existing phone systems while you transition."),
        ("clock", "Call packages", "Bundles of included minutes to control your call costs."),
        ("route", "Number porting", "Move your numbers to SIP trunks or a hosted system."),
        ("wifi", "Broadband", "Add broadband and, where needed, an internet-only connection."),
        ("clip", "Line audits", "A full list of what is on each line and what depends on it."),
    ]),
    f"""<section><div class="wrap">
{heading("The switch-off", "What is happening to ISDN and analogue lines", "The telephone network operators are retiring the old copper-based voice network in stages and replacing it with digital services.")}
<div class="grid g3">
<div class="card"><h3>Selling has stopped</h3><p>New analogue and ISDN lines can no longer be freely ordered, so existing lines are being kept going while the network is wound down.</p></div>
<div class="card"><h3>Retirement is underway</h3><p>The network is being closed in stages and is currently scheduled to be fully retired by early 2027. Dates have moved before, so we always check the latest position.</p></div>
<div class="card"><h3>Planning takes time</h3><p>Larger and multi-site migrations take longer, so the sooner you plan, the less risk of a rushed move.</p></div>
</div>
<p style="margin-top:16px"><b>Note:</b> check current dates with us or your network operator before you plan. This page is guidance, not a guarantee of timings.</p>
</div></section>
<section class="alt"><div class="wrap">
{heading("What it affects", "More than just your phone lines", "Anything that uses a traditional phone line needs to be checked.")}
{cards([
 ("shield", "Alarms", "Intruder and fire alarms that dial out over a phone line."),
 ("building", "Lift phones", "Emergency lift phones connected to analogue lines."),
 ("cart", "Card machines", "Payment terminals and EPOS that dial through a phone line."),
 ("chat", "Fax and telecare", "Fax machines and telecare devices."),
 ("headset", "Conference lines", "Dedicated conferencing and call-in lines."),
 ("globe", "Broadband on a phone line", "Internet that still relies on a PSTN line."),
])}
<p style="margin-top:16px">Alarm, lift and card-machine suppliers should be contacted too. We can help you identify what is on each line.</p>
</div></section>
<section><div class="wrap">
{heading("Your options", "Where to move to")}
<div class="grid g3">
<div class="card"><h3>SIP trunks</h3><p>Keep your phone system and numbers, and carry calls over your internet. <a href="sip-trunks.html">SIP trunks</a></p></div>
<div class="card"><h3>Hosted phone system</h3><p>Move to a cloud system such as <a href="8x8.html">8x8</a> or hosted <a href="3cx.html">3CX</a>, with nothing to host.</p></div>
<div class="card"><h3>Better internet</h3><p>Pair your new voice with <a href="fibre-broadband.html">full fibre</a> or a <a href="leased-lines.html">leased line</a>, with <a href="backup-connectivity.html">backup</a>.</p></div>
</div></div></section>""",
    [("Audit", "We list every line, number and service that depends on it."), ("Plan", "We recommend a replacement and a timeline."), ("Move", "We migrate and port numbers with minimal disruption."), ("Support", "We test, train your team and look after the new service.")],
    [("Do I have to move now?", "Existing lines continue for now, but the network is being retired. Planning early avoids a rushed, more expensive move."),
     ("Will I keep my numbers?", "Yes. We port your numbers to the new service."),
     ("What about my alarms and lift phones?", "These often use phone lines. Speak to the suppliers as well as us, and we will help identify what is connected."),
     ("Will there be downtime?", "A well-planned migration should involve little or none. We time the changeover around your business."),
     ("What will it cost?", "Costs vary with lines, channels and equipment. Many businesses save on line rental and calls. We quote after an audit.")],
    "Ask for a free line audit and we will tell you what needs to move and when.", steps_title="How we move you")

# --- 4G/5G backup ---
conn_page("backup-connectivity.html", "4G/5G Backup Internet and Failover | Extera Limited",
    "4G/5G backup connectivity from Extera: automatic failover keeps phones, card machines and cloud apps working if your main line goes down.",
    "4G/5G", "Backup", "Stay online when your main line fails, with automatic failover to a mobile network.", "4G/5G Backup",
    feature("Backup connectivity", "Stay online when your main line fails", "Lines get cut and exchanges fail. A 4G/5G backup connection watches your main line, and when it detects a problem it switches your traffic to a mobile network automatically. When the main line returns, it switches back.", ["Automatic failover with no manual steps", "Keeps phones, card payments and cloud apps running", "Quick to install, with no new cable", "Works alongside any main connection"], "signal", cta=("Get a backup quote", "contact.html")),
    ("Why add backup", "One fault should not stop your business", [
        ("shield", "Keep taking payments", "Card terminals and EPOS keep working during an outage."),
        ("phone", "Keep phones working", "Hosted phones and SIP trunks stay online."),
        ("cloud", "Keep cloud apps running", "Email, CRM and remote access continue."),
        ("bolt", "Fast to deploy", "Often installed with no engineer visit to the street."),
        ("clock", "Automatic", "Switch over and back happen without anyone stepping in."),
        ("globe", "Different path", "A mobile link avoids a fault on your fixed line."),
    ]),
    f"""<section><div class="wrap">
{heading("How it works", "Failover in four moves")}
{steps([("Monitor", "A failover router continually tests your main connection."), ("Detect", "If tests fail repeatedly, it treats the line as down."), ("Switch", "Traffic is moved to the 4G/5G SIM automatically."), ("Return", "When the main line is healthy again, traffic moves back.")])}
</div></section>
<section class="alt"><div class="wrap">
{heading("Choosing", "4G or 5G backup?")}
{spec_table(["", "4G", "5G"], [
 ("Best for", "Email, cloud apps, card payments and calls", "Heavier use, or where backup also carries a lot of traffic"),
 ("Speed", "Typically enough to keep a small office running", "Faster, depending on local coverage"),
 ("Coverage", "Widely available", "Growing, but varies by location"),
])}
</div></section>
<section><div class="wrap">
{heading("Things we check", "Getting the details right")}
<div class="grid g3">
<div class="card"><h3>Signal</h3><p>Placement of the router and antenna affects speeds, so we test signal on site.</p></div>
<div class="card"><h3>Data allowance</h3><p>Backup SIMs carry data limits. We recommend plans and alerts so a long outage does not cause bill shock.</p></div>
<div class="card"><h3>Keeping services connected</h3><p>Some services, such as VPNs and hosted phones, can drop when the address changes. We configure failover to handle this.</p></div>
</div>
<div class="actions left" style="margin-top:24px"><a class="btn outline dark" href="mobile.html">See business mobile</a></div>
</div></section>
<section class="alt"><div class="wrap">
{feature("Beyond backup", "4G/5G as a main connection", "Mobile broadband can also be your main connection where fixed lines are not available, such as for temporary sites, pop-up offices and events.", ["Temporary and pop-up sites", "Rural locations with limited broadband", "Quick starts while a fixed line is ordered"], "globe", flip=True)}
</div></section>""",
    [("Assess", "We look at your main connection and what must stay online."), ("Specify", "We recommend the router, SIP and data plan."), ("Install", "We install, test the signal and configure failover."), ("Monitor", "We support the service and handle any changes.")],
    [("Will I notice when it switches?", "Short interruptions can happen, but most services carry on. We configure the router to keep important services connected."),
     ("Can it back up a leased line?", "Yes. Many customers pair a leased line or fibre with 4G/5G backup for resilience."),
     ("What does it cost?", "Typically a router plus a monthly SIM plan. We quote based on how much data you need."),
     ("What about data limits?", "Backup SIMs usually have data allowances. We help you choose a plan and set usage alerts."),
     ("Is it a replacement for a second fixed line?", "It is a quick, cost-effective backup. For critical sites, a second fixed line on a separate route may also be worth considering.")],
    "Tell us what must stay online and we will recommend a backup.")


# ---------- Gamma Horizon and Avaya IP Office ----------
# Original copy based on published product information from the vendors and UK partners (figures are the vendors' own claims).
def grp_related(pages, exclude, label, hub, hub_card):
    items = [(i, t, b, f, "Read more") for f, i, t, b, _ in pages if f != exclude]
    if exclude != hub:
        items.insert(0, hub_card)
    return f'<section class="alt"><div class="wrap">{heading(label, "More about " + label, None)}{cards(items[:3], link=True)}</div></section>'


def tab_page(fname, title, desc, h1a, h1b, hero_text, eyebrow, parent, crumb, intro, extra, faqs, cta_text, cta_title, related_html):
    body = f"""
<section><div class="wrap">{intro}</div></section>
{extra}
{faq(faqs)}
{related_html}
{cta_band(cta_text, cta_title)}
"""
    page(fname, title, desc, body, hero(h1a, h1b, hero_text, small=True, eyebrow=eyebrow),
         f'<a href="{parent[0]}">{parent[1]}</a> / {crumb}')


# =================== Gamma Horizon ===================
GH = [
    ("gamma-horizon-apps.html", "mobile", "Apps and collaboration", "Collaborate, a mobile app and a browser client, so staff can work from anywhere.", "Apps"),
    ("gamma-horizon-teams.html", "users", "Microsoft Teams and Webex", "Add Horizon calling to Microsoft Teams, or choose Horizon with Webex for one collaboration platform.", "Teams and Webex"),
    ("gamma-horizon-contact.html", "headset", "Contact centre", "Horizon Contact for omnichannel customer service, linked to your phone system.", "Contact centre"),
    ("gamma-horizon-analytics.html", "signal", "Analytics and integrations", "Call and contact analytics, a receptionist console and links to 200+ CRM packages.", "Analytics"),
    ("gamma-horizon-network.html", "shield", "Network and resilience", "Gamma's own UK network, multiple data centres and 24/7 first-line support.", "Network"),
]
GH_CARD = ("cloud", "Gamma Horizon", "The overview: what Horizon is, what is included and how it compares.", "gamma-horizon.html", "Read more")


def gh_related(exclude):
    return grp_related(GH, exclude, "Gamma Horizon", "gamma-horizon.html", GH_CARD)


def gh_page(fname, title, desc, h1a, h1b, hero_text, crumb, intro, extra, faqs, cta_text):
    extra = extra + f"""<section class="alt"><div class="wrap">
{heading("Getting started", "How a Horizon project works with Extera", "We handle the planning and the paperwork, and stay on hand once you are live.")}
{steps([("Discuss", "We learn how your team works, where they work and what you use today."), ("Design", "We recommend the Horizon package, handsets and apps, and quote clearly."), ("Move", "We port your numbers, set up users and train your team."), ("Support", "Extera is your first call for changes, faults and new starters.")])}
<p>Extera is based in Banbury, Oxfordshire. You get one team for your phones, your connectivity and your mobiles, instead of chasing several suppliers.</p>
</div></section>"""
    tab_page(fname, title, desc, h1a, h1b, hero_text, "Gamma Horizon", ("gamma-horizon.html", "Gamma Horizon"), crumb, intro, extra, faqs, cta_text,
             "Talk to us about Horizon", gh_related(fname))


QGH = ("Get a Horizon quote", "contact.html")

# --- Horizon overview ---
body = f"""
{facts([("Since 2001", "Extera, UK telecoms specialist"), ("ISO 9001:2015", "Certified quality management"), ("60,000+", "UK companies use Gamma, says Gamma"), ("200+", "CRM packages supported, says Gamma")])}

<section><div class="wrap">
{feature("Gamma Horizon", "A hosted phone system on a UK carrier's own network", "Horizon is a cloud business phone system from Gamma, a UK telecoms carrier. Calls run over Gamma's own network, you manage the system in a web portal, and there is no phone system hardware to buy or maintain.", ["Fully hosted, with nothing to install onsite", "Managed through an easy web portal", "Fixed and mobile telephony in one system", "Add collaboration, contact centre and analytics as you need them"], "cloud", cta=QGH)}
<p class="vendor-note">Figures are published by Gamma and describe its own business and platform.</p>
</div></section>

<section class="alt"><div class="wrap">
{heading("Explore Horizon", "What is included", "Choose a topic to see how it works and what to check.")}
{cards([(i, t, b, f, m) for f, i, t, b, m in GH] + [("clip", "Not sure where to start?", "Tell us how your team works and we will recommend the right Horizon package.", "contact.html", "Talk to us")], link=True)}
</div></section>

<section><div class="wrap">
{heading("Core features", "The phone system essentials, ready to use", "Set up and changed by you in the web portal, or by us on your behalf.")}
{cards([
 ("route", "Auto attendant and IVR", "Build menus that send callers to the right team, with different routing in and out of hours."),
 ("users", "Hunt groups", "Ring a team in the order you choose so every call is picked up."),
 ("clip", "Voicemail to email", "Voicemails arrive as audio files in your inbox so you never miss one."),
 ("shield", "Call recording", "Record calls for training and compliance. The recording level depends on your tier."),
 ("chat", "Conferencing", "Hold conference calls from the same system, with a built-in conference bridge."),
 ("clock", "Scheduling and failover", "Schedule routing for opening hours and holidays, with automatic failover if a site goes down."),
])}
</div></section>

<section class="alt"><div class="wrap">
{feature("Handsets and headsets", "Equipment to suit every desk and room", "Horizon works with desk phones, headsets and conference equipment from well-known makers, and with the app on a computer or mobile. We help you choose what fits, and supply it.", ["Desk phones and cordless handsets", "Headsets for office and contact centre use", "Conference phones for meeting rooms", "Partners include Yealink, EPOS, Sennheiser, Poly and Cisco"], "phone", flip=True, cta=("See Extera Direct", "extera-direct.html"))}
</div></section>

<section><div class="wrap">
{feature("Accessibility", "Designed to work for everyone", "Gamma highlights accessibility features for people with hearing, vision or mobility impairments. If someone on your team needs adjustments, tell us early and we will check what is available.", ["Options for staff with hearing impairments", "Options for staff with vision impairments", "Options for staff with mobility needs", "Advice on handsets and software settings"], "users")}
</div></section>

<section class="alt"><div class="wrap">
{heading("Fit", "Is Horizon right for you?")}
<div class="grid g2">
<div class="card verdict"><h3>A good fit if&hellip;</h3>{ticks(["You want a hosted system with nothing to maintain onsite", "You value a UK carrier's own network behind your calls", "You have hybrid or home workers and several sites", "You are moving off ISDN or PSTN lines", "You use Microsoft Teams or want one collaboration platform"])}</div>
<div class="card verdict"><h3>Think about&hellip;</h3>{ticks(["It is cloud only, so there is no onsite option", "Some features depend on your tier, such as call recording and CRM integration", "Teams and collaboration features can be separate add-ons", "Very large enterprises may want a different platform"])}</div>
</div>
</div></section>

<section><div class="wrap">
{heading("Compare", "Horizon, 3CX and 8x8 at a glance", "All three are strong systems. They suit different ways of working.")}
<div class="table-wrap"><table><thead><tr><th scope="col"></th><th scope="col">Gamma Horizon</th><th scope="col"><a href="3cx.html">3CX</a></th><th scope="col"><a href="8x8.html">8x8</a></th></tr></thead><tbody>
<tr><th scope="row">How it runs</th><td>Hosted on Gamma's UK network</td><td>Onsite, your cloud or hosted</td><td>Hosted on 8x8's global platform</td></tr>
<tr><th scope="row">Pricing</th><td>Per user per month, in tiers</td><td>Annual licence by simultaneous calls</td><td>Per user per month, in plans</td></tr>
<tr><th scope="row">Contact centre</th><td>Horizon Contact, with Akixi analytics</td><td>Built-in queues and wallboards</td><td>Full omnichannel contact centre</td></tr>
<tr><th scope="row">Microsoft Teams</th><td>Horizon for Teams</td><td>Microsoft 365 sync</td><td>8x8 Voice for Teams</td></tr>
<tr><th scope="row">Best for</th><td>UK businesses wanting a carrier-backed hosted system</td><td>Control and low running cost</td><td>International and multichannel</td></tr>
</tbody></table></div>
<p style="margin-top:16px"><a class="btn outline dark" href="3cx-vs-8x8.html">See our 3CX vs 8x8 comparison</a></p>
</div></section>

<section class="alt"><div class="wrap">
{heading("Moving over", "How a Horizon project works")}
{steps([("Survey", "We review your users, numbers, sites, lines and handsets."), ("Design", "We agree your call flows, packages, add-ons and equipment."), ("Set up", "We configure Horizon, provision phones and prepare your numbers."), ("Go live", "We port numbers, train your team and support you after launch.")])}
</div></section>

{faq([
 ("What is Gamma Horizon?", "A hosted business phone system from Gamma that runs over Gamma's UK network. You manage it in a web portal, and there is no hardware to install onsite."),
 ("Can I keep my phone numbers?", "Yes. We port your numbers to Horizon and plan the cutover with you."),
 ("Does Horizon work with Microsoft Teams?", "Yes. See <a href='gamma-horizon-teams.html'>Microsoft Teams and Webex</a>."),
 ("Is there a contact centre?", "Yes. Horizon Contact works with Horizon. See <a href='gamma-horizon-contact.html'>contact centre</a>."),
 ("Does it replace my ISDN lines?", "Yes. Horizon is internet-based, so it replaces ISDN and analogue lines. See <a href='business-lines.html'>lines and calls</a>."),
])}
"""
page("gamma-horizon.html", "Gamma Horizon Hosted Phone System | Extera Limited",
     "Gamma Horizon hosted business phone system supplied and supported by Extera: UK network, collaboration, contact centre and analytics.",
     body, hero("Gamma", "Horizon", "A hosted phone system on a UK carrier's own network, with Teams, Webex and a contact centre when you need them. Supplied and supported by Extera.", small=True, eyebrow="Phone systems"), "Gamma Horizon")

# --- Apps ---
gh_page("gamma-horizon-apps.html", "Gamma Horizon Apps and Collaboration | Extera Limited",
    "Horizon Collaborate, the Horizon mobile app and browser calling: chat, voice, video and file sharing from any device.",
    "Apps", "and Collaboration", "Chat, call and meet from one app on a computer, phone or browser, so staff can work from anywhere.", "Apps and Collaboration",
    feature("Horizon Collaborate", "Chat, calls and video in one place", "Collaborate is the unified communications layer for Horizon. Staff see who is available, chat, call, share their screen and join video meetings from the same app, on a computer or in a browser.", ["Presence shows who is online and free", "Chat, voice and video calls in one client", "Built-in conference bridge and desktop sharing", "Guests join calls from their browser, with nothing to install"], "users", cta=QGH),
    f"""<section class="alt"><div class="wrap">
{heading("The everywhere office", "Work from anywhere on the same number")}
{cards([
 ("phone", "Softphone", "Use your computer as your phone, with the same features as a desk phone."),
 ("mobile", "Mobile app", "Make and take calls, check contacts and read voicemail on iPhone and Android."),
 ("globe", "Browser calling", "WebRTC lets guests and staff call from a browser, with an API for custom builds."),
 ("clock", "Mobile as an extension", "Your mobile or laptop works as an extension of the office system."),
 ("clip", "Outlook call preview", "See caller details from your Outlook contacts as the phone rings."),
 ("route", "Redirect calls", "Send calls to a mobile, PC or another site if you are away from your desk."),
])}
</div></section>
<section><div class="wrap">
{feature("Horizon mobile", "Your office phone in your pocket", "The Horizon app turns a mobile into a business extension. Calls use your business number, and staff can move between desk phone, app and softphone without losing a call.", ["Business calls on your own number", "Contacts and voicemail in the app", "Works over Wi-Fi or mobile data", "Business and personal calls kept separate"], "mobile", flip=True, img=f'<figure class="art"><img src="assets/art/mobile.png" width="1920" height="1080" loading="lazy" alt=""></figure>')}
</div></section>
<section class="alt"><div class="wrap">
{heading("Good to know", "What affects your set-up")}
<div class="grid g3">
<div class="card"><h3>Add-on or included?</h3><p>Collaborate is usually a paid-for add-on to the core phone system. We confirm exactly what each tier includes when we quote.</p></div>
<div class="card"><h3>Connection quality</h3><p>Video and softphone calls need a stable connection. See <a href="fibre-broadband.html">fibre broadband</a> and <a href="leased-lines.html">leased lines</a>.</p></div>
<div class="card"><h3>Hybrid teams</h3><p>Pair the apps with a decent headset and the experience matches the office. See <a href="extera-direct.html">Extera Direct</a>.</p></div>
</div></div></section>""",
    [("Do I need a separate chat app?", "No. Collaborate includes chat, presence, voice and video in the same client as your calls."),
     ("Can guests join calls without software?", "Yes. External guests can join from a browser, using WebRTC."),
     ("Does the mobile app use my personal number?", "No. It uses your business number, so personal and business calls stay separate."),
     ("Is Collaborate included in every package?", "It is generally an add-on. We confirm what is included in your chosen tier.")],
    "Tell us how your team works and we will plan the right apps and devices.")

# --- Teams and Webex ---
gh_page("gamma-horizon-teams.html", "Gamma Horizon for Microsoft Teams and Webex | Extera Limited",
    "Horizon for Teams adds Gamma calling to Microsoft Teams, and Horizon with Webex combines Horizon with Webex collaboration.",
    "Teams", "and Webex", "Keep Microsoft Teams and add proper business calling, or move to one platform with Webex.", "Teams and Webex",
    feature("Horizon for Teams", "Keep Microsoft Teams, add proper business calling", "Horizon for Teams connects Teams to Gamma's voice network. Staff keep the Teams app they know, while Horizon provides the phone numbers, call routing and carrier quality underneath.", ["Make and take calls from Microsoft Teams", "Teams becomes a Horizon endpoint on desktop, mobile and web", "An alternative to Microsoft's own calling plans", "Call control, statistics and recording through Horizon"], "users", cta=QGH, img=f'<figure class="art"><img src="assets/art/teams-direct.svg" width="1920" height="1080" loading="lazy" alt=""></figure>'),
    f"""<section class="alt"><div class="wrap">
{feature("Horizon with Webex", "One platform for voice, video and messaging", "Horizon with Webex combines the Horizon cloud phone system with Webex collaboration tools, so voice, video, messaging and file sharing sit in one platform with dedicated mobile apps.", ["Voice, video, messaging and file sharing together", "Dedicated apps for Android and iOS", "AI features such as real-time transcription and intelligent call routing", "Built on the Horizon phone system and Gamma's network"], "cloud", flip=True, img=f'<figure class="art"><img src="assets/art/cloud-video.png" width="1920" height="1080" loading="lazy" alt=""></figure>')}
<p class="vendor-note">Gamma's offers change over time, so we confirm which Webex and Teams options are current when we quote.</p>
</div></section>
<section><div class="wrap">
{heading("Which route?", "Collaborate, Teams or Webex", "All three work with Horizon. The right one depends on the tools your team already uses.")}
<div class="table-wrap"><table><thead><tr><th scope="col"></th><th scope="col">Horizon Collaborate</th><th scope="col">Horizon for Teams</th><th scope="col">Horizon with Webex</th></tr></thead><tbody>
<tr><th scope="row">Best for</th><td>Teams without an existing collaboration tool</td><td>Businesses already living in Microsoft Teams</td><td>Businesses wanting a full collaboration suite from one supplier</td></tr>
<tr><th scope="row">Staff use</th><td>The Horizon app</td><td>The Teams app</td><td>The Webex app</td></tr>
<tr><th scope="row">Calling by</th><td>Horizon</td><td>Horizon, via Gamma's network</td><td>Horizon</td></tr>
<tr><th scope="row">Extra to check</th><td>Add-on licence</td><td>Microsoft licences needed</td><td>Webex licences needed</td></tr>
</tbody></table></div>
</div></section>""",
    [("Do I need Microsoft calling plans as well?", "No. Horizon for Teams is an alternative, so calling comes from Gamma's network instead."),
     ("Can staff still use the Teams app?", "Yes. They keep the Teams interface and add business calling to it."),
     ("What does Webex add?", "Voice, video, messaging and file sharing in one platform, with mobile apps and AI features such as transcription."),
     ("Which licences do I need?", "That depends on the route. We check Microsoft or Webex licensing with you before you commit.")],
    "Tell us what your team uses today and we will recommend the best route.")

# --- Contact centre ---
gh_page("gamma-horizon-contact.html", "Gamma Horizon Contact Centre | Extera Limited",
    "Horizon Contact is a cloud contact centre that works alongside Gamma Horizon: omnichannel, CRM integration and analytics.",
    "Horizon", "Contact", "A cloud contact centre that works alongside your phone system, so customers reach the right person first time.", "Contact Centre",
    feature("Horizon Contact", "A cloud contact centre alongside your phones", "Horizon Contact gives teams that handle customer queries a cloud contact centre that works with Horizon. Users are enabled as agents in the Horizon portal, so you do not run a separate system.", ["Omnichannel contact in one platform", "A fully integrated CRM", "Integrations with Salesforce, Microsoft Dynamics and Zendesk", "Call queues and call-back options"], "headset", cta=("Get a contact centre quote", "contact.html")),
    f"""<section class="alt"><div class="wrap">
{heading("What it does", "Tools for agents and managers")}
{cards([
 ("headset", "Call queues", "Hold callers in queues with sensible routing so none are lost."),
 ("chat", "Omnichannel", "Handle more than voice, so customers can reach you the way they prefer."),
 ("clip", "Integrated CRM", "Customer records and call history in front of the agent as they answer."),
 ("route", "Popular integrations", "Link Horizon Contact to Salesforce, Microsoft Dynamics and Zendesk."),
 ("signal", "Call analytics", "See missed calls and call-back activity. Akixi analytics adds much deeper reporting. See <a href='gamma-horizon-analytics.html'>analytics</a>."),
 ("users", "Flexible teams", "Agents can work from the office or home, and be added from the portal."),
])}
</div></section>
<section><div class="wrap">
{heading("Where it fits", "Choosing a contact centre platform", "Needs range from a small queue to a large operation.")}
<div class="table-wrap"><table><thead><tr><th scope="col">Option</th><th scope="col">Best for</th></tr></thead><tbody>
<tr><th scope="row">Horizon Contact</th><td>Small and mid-size teams already on Horizon that want a contact centre alongside it</td></tr>
<tr><th scope="row"><a href="3cx-ai-analytics.html">3CX built-in</a></th><td>Smaller inbound teams that need queues, wallboards and reporting</td></tr>
<tr><th scope="row"><a href="8x8-contact-centre.html">8x8 contact centre</a></th><td>Growing teams wanting omnichannel, quality and workforce management and AI</td></tr>
<tr><th scope="row"><a href="avaya-ipo-contact-centre.html">Avaya IP Office Contact Center</a></th><td>Businesses on Avaya wanting a multichannel contact centre</td></tr>
</tbody></table></div>
</div></section>""",
    [("Is Horizon Contact separate from Horizon?", "It is a separate module that works with Horizon, sharing the same platform and portal."),
     ("Which CRMs does it work with?", "Salesforce, Microsoft Dynamics and Zendesk, plus an integrated CRM."),
     ("How big a team can it support?", "It is aimed at small and mid-size teams. Larger operations may suit a different platform. See <a href='contact-centres.html'>contact centres</a>."),
     ("Can agents work from home?", "Yes. Agents can be enabled from the Horizon portal and work from any location.")],
    "Tell us about your team and call volumes and we will recommend a contact centre.")

# --- Analytics and integrations ---
gh_page("gamma-horizon-analytics.html", "Gamma Horizon Analytics and CRM Integrations | Extera Limited",
    "Akixi call and contact analytics, a receptionist console, call recording and links to 200+ CRM packages for Gamma Horizon.",
    "Analytics", "and Integrations", "Know what is happening on every call, with live dashboards and links to over 200 CRM packages.", "Analytics and Integrations",
    feature("Analytics", "See what is happening on every call", "Akixi analytics gives you detailed call and contact statistics, live wallboards and alarms, so managers can see problems early and plan their teams.", ["Hundreds of historic and real-time statistics", "Wallboards and alarms for busy teams", "Visibility of missed calls and call-backs", "Scales from small teams to thousands of users"], "signal", cta=QGH, img=f'<figure class="art"><img src="assets/art/analytics.svg" width="1920" height="1080" loading="lazy" alt=""></figure>'),
    f"""<section class="alt"><div class="wrap">
{feature("CRM and apps", "Connect Horizon to the tools you use", "Horizon works with over 200 CRM packages. Calls can open the customer record, and calls can be logged against it, so staff spend less time searching and typing.", ["Works with Salesforce, Zoho, Bullhorn and many more", "Click to dial from your CRM", "Caller details shown as calls arrive", "Outlook call preview for your contacts"], "clip", flip=True)}
</div></section>
<section><div class="wrap">
{heading("More tools", "Everyday helpers")}
{cards([
 ("building", "Receptionist console", "A switchboard-style screen for reception, to see who is free and transfer calls fast."),
 ("shield", "Call recording", "Record calls for quality and compliance. Availability depends on your tier."),
 ("signal", "Call reporting", "Reports on volumes, answer times and missed calls to manage your teams."),
 ("route", "Number and routing control", "Change routing and numbers in the web portal when plans change."),
 ("clock", "Monitoring", "Keep an eye on extensions and live calls without extra hardware."),
 ("wrench", "Open tools", "APIs and integrations so Horizon can fit your own processes."),
])}
<p class="vendor-note">Some analytics, recording and CRM features depend on your tier or are add-ons. We confirm them when we quote.</p>
</div></section>""",
    [("What is Akixi?", "A call and contact analytics tool that works with Horizon, giving historic and real-time statistics, wallboards and alarms."),
     ("Does Horizon work with my CRM?", "Probably. Horizon works with over 200 CRM packages, and we can check yours."),
     ("Is call recording included?", "It is available on some tiers. We confirm what your package includes."),
     ("Can reception see who is available?", "Yes, the receptionist console shows availability and lets staff transfer quickly.")],
    "Tell us which systems you use and we will plan the integrations.")

# --- Network ---
gh_page("gamma-horizon-network.html", "Gamma Horizon Network, Resilience and Support | Extera Limited",
    "Gamma Horizon runs on Gamma's own UK network across multiple data centres, with call failover and 24/7 first-line support.",
    "Network", "and Resilience", "Calls on a UK carrier's own network, with data-centre failover and 24/7 first-line support.", "Network and Resilience",
    feature("Network and resilience", "Built on a carrier's own network", "Horizon runs over Gamma's own network rather than the public internet alone, across multiple data centres. Gamma states a 99.999% uptime figure, and reviews describe very little unplanned downtime.", ["Gamma's own UK network", "Multiple data centres for redundancy", "Calls can switch to another data centre if one fails", "Calls can divert to other sites, mobiles or home workers if your connection fails"], "shield", cta=QGH),
    f"""<section class="alt"><div class="wrap">
{feature("If a site goes offline", "Keep taking calls when something breaks", "If an office loses its connection, calls can be diverted to another site, mobiles or home workers. Pair Horizon with a backup connection for even better protection.", ["Divert calls to mobiles, other offices or home workers", "Automatic failover between data centres", "Add 4G/5G backup so the office stays online", "Plan resilience site by site"], "route", flip=True, cta=("See 4G/5G backup", "backup-connectivity.html"))}
<p class="vendor-note">Gamma's own pages quote more than one availability figure (99.999% uptime and a 99.95% SLA), so we confirm the contractual terms with you.</p>
</div></section>
<section><div class="wrap">
{feature("Support", "UK-based, 24/7 first-line support", "Gamma provides UK-based support teams with 24/7 first-line cover. We remain your first point of contact, handling issues with you and escalating to Gamma where needed.", ["24/7 first-line support from Gamma", "Extera as your own local point of contact", "Optional maintenance and SLA cover from us", "Training for administrators and users"], "headset", img=f'<figure class="art"><img src="assets/art/uk-support.svg" width="1920" height="1080" loading="lazy" alt=""></figure>')}
</div></section>
<section class="alt"><div class="wrap">
{heading("Your side", "What your network needs", "A hosted system relies on your connection. We check these in the survey.")}
{cards([
 ("wifi", "Bandwidth", "Enough upload and download for calls and video. See <a href='fibre-broadband.html'>fibre broadband</a> and <a href='leased-lines.html'>leased lines</a>."),
 ("route", "Quality of service", "Router settings that give voice priority so calls stay clear."),
 ("shield", "Security", "Gamma connectivity can include managed next-generation firewalls to protect against internet threats."),
 ("clock", "ISDN switch-off", "Horizon replaces ISDN lines. See <a href='business-lines.html'>lines and calls</a>."),
])}
</div></section>""",
    [("Is Horizon reliable?", "Gamma states a 99.999% uptime figure and runs Horizon across multiple data centres on its own network. We also advise backup for critical sites."),
     ("What happens if my internet fails?", "Calls can be diverted to other sites, mobiles or home workers. A backup connection keeps the office online."),
     ("Who do I call for support?", "Call us first. We handle issues with you and escalate to Gamma where needed."),
     ("Is my data kept in the UK?", "Horizon runs on Gamma's UK network. If you have specific residency requirements, tell us and we will confirm them.")],
    "Tell us about your sites and uptime needs and we will plan the right resilience.")


# =================== Avaya IP Office ===================
IPO = [
    ("avaya-ipo-editions.html", "server", "Editions and scale", "Basic to Select, from a handful of users to thousands across up to 150 sites.", "Editions"),
    ("avaya-ipo-apps.html", "mobile", "Apps and mobility", "Avaya Workplace, one-X Portal, DECT handsets and remote workers.", "Apps"),
    ("avaya-ipo-contact-centre.html", "headset", "Contact centre", "IP Office Contact Center, call reporting and recording.", "Contact centre"),
    ("avaya-ipo-resilience.html", "shield", "Resilience and support", "Survivability, security, SIP and the upgrade path to the latest release.", "Resilience"),
]
IPO_CARD = ("phone", "Avaya IP Office", "The overview: what IP Office is, why businesses choose it and how it compares.", "avaya-ip-office.html", "Read more")


def ipo_related(exclude):
    return grp_related(IPO, exclude, "Avaya IP Office", "avaya-ip-office.html", IPO_CARD)


def ipo_page(fname, title, desc, h1a, h1b, hero_text, crumb, intro, extra, faqs, cta_text):
    tab_page(fname, title, desc, h1a, h1b, hero_text, "Avaya IP Office", ("avaya-ip-office.html", "Avaya IP Office"), crumb, intro, extra, faqs, cta_text,
             "Talk to us about Avaya", ipo_related(fname))


QIPO = ("Get an Avaya quote", "contact.html")

# --- IP Office overview ---
body = f"""
{facts([("Avaya Silver Partner", "Mid-Market and Contact Centre"), ("Since 2001", "Extera, UK telecoms specialist"), ("5 to 3,000", "users on one system, says Avaya"), ("Up to 150", "networked locations, says Avaya")])}

<section><div class="wrap">
{feature("Avaya IP Office", "A proven phone system for small and mid-size businesses", "IP Office is Avaya's business communications platform. It brings telephony, voicemail, conferencing, video, mobility and a contact centre together in one system, and it is installed on your premises, so you keep control of it.", ["Telephony, messaging, conferencing and contact centre in one platform", "One number that reaches staff on any device", "Scales from a handful of users to thousands, and from one site to many", "Onsite, or paid monthly through subscription"], "phone", cta=QIPO)}
<p class="vendor-note">Capacity figures are published by Avaya and vary by release. We confirm them for the version we quote.</p>
</div></section>

<section class="alt"><div class="wrap">
{heading("Explore IP Office", "What is included", "Choose a topic to see what it offers and what to check.")}
{cards([(i, t, b, f, m) for f, i, t, b, m in IPO] + [("clip", "Already on IP Office?", "We support existing Avaya systems, upgrades and moves to the latest release.", "contact.html", "Talk to us")], cols="g3", link=True)}
</div></section>

<section><div class="wrap">
{heading("Why IP Office", "Why businesses stay with it")}
{cards([
 ("shield", "You control it", "It lives on your premises, so you decide upgrades, access and where your data sits."),
 ("route", "Scales with you", "Start small and grow users, extensions and sites without replacing the system."),
 ("users", "Everyone connected", "Office, home and mobile staff share one number and one directory."),
 ("headset", "Contact centre built in", "Add call reporting, recording and a contact centre when your team needs one."),
 ("wrench", "Keeps your investment", "Many Avaya handsets and wiring can stay, which cuts the cost of an upgrade."),
 ("clock", "Subscription option", "Pay monthly per user instead of buying licences up front."),
])}
</div></section>

<section class="alt"><div class="wrap">
{heading("Fit", "Is IP Office right for you?")}
<div class="grid g2">
<div class="card verdict"><h3>A good fit if&hellip;</h3>{ticks(["You already have Avaya equipment and want to keep building on it", "You want a system on your own premises that you control", "You have several sites and want one networked system", "You need a contact centre alongside your phones", "You want a proven platform with a long track record"])}</div>
<div class="card verdict"><h3>Think about&hellip;</h3>{ticks(["It is installed onsite, so hosted-only buyers may prefer a cloud system", "You need to keep software up to date as Avaya retires older releases", "Some applications and agents are licensed separately", "Cloud-first teams may prefer Horizon, 8x8 or hosted 3CX"])}</div>
</div>
</div></section>

<section><div class="wrap">
{heading("Compare", "Where IP Office sits among the options")}
<div class="table-wrap"><table><thead><tr><th scope="col"></th><th scope="col">Avaya IP Office</th><th scope="col"><a href="3cx.html">3CX</a></th><th scope="col"><a href="gamma-horizon.html">Gamma Horizon</a></th><th scope="col"><a href="8x8.html">8x8</a></th></tr></thead><tbody>
<tr><th scope="row">How it runs</th><td>Onsite, with a subscription option</td><td>Onsite, your cloud or hosted</td><td>Hosted</td><td>Hosted</td></tr>
<tr><th scope="row">Control</th><td>High, on your premises</td><td>High, you choose</td><td>Managed by Gamma</td><td>Managed by 8x8</td></tr>
<tr><th scope="row">Scale</th><td>5 to 3,000 users</td><td>Small to large</td><td>Small to mid</td><td>Small to enterprise</td></tr>
<tr><th scope="row">Best for</th><td>Existing Avaya users and multi-site</td><td>Low running cost and flexibility</td><td>Hosted with a UK carrier</td><td>Hosted, international, multichannel</td></tr>
</tbody></table></div>
</div></section>

<section class="alt"><div class="wrap">
{heading("The process", "How an IP Office project works")}
{steps([("Review", "We look at your sites, users, handsets, wiring and any existing Avaya system."), ("Design", "We choose the edition, applications and equipment, and plan the network."), ("Install", "Our engineers install, configure and test, and port your numbers."), ("Support", "We train your team and offer maintenance and upgrades.")])}
</div></section>

{faq([
 ("Is IP Office a hosted system?", "It is an onsite system, with a subscription option for monthly payment. Cloud-first businesses may prefer a hosted system such as <a href='gamma-horizon.html'>Gamma Horizon</a> or <a href='8x8.html'>8x8</a>."),
 ("Can you support our existing Avaya system?", "Yes. We are an Avaya Silver Partner and can maintain, upgrade and expand existing IP Office systems."),
 ("Can I keep my Avaya handsets?", "Often yes. We check which handsets and wiring can be reused."),
 ("Do I have to upgrade?", "Avaya retires older releases, so staying current matters. See <a href='avaya-ipo-resilience.html'>resilience and support</a>."),
 ("Can I move to the cloud later?", "Yes. We can plan a move to a hosted system when you are ready, and port your numbers."),
], alt=True)}
"""
page("avaya-ip-office.html", "Avaya IP Office Phone Systems | Extera Limited",
     "Avaya IP Office business phone systems supplied, installed and supported by Extera, an Avaya Silver Partner: onsite or subscription, multi-site and contact centre.",
     body, hero("Avaya", "IP Office", "A proven onsite phone system that grows from a few users to thousands, with a built-in contact centre. Supplied and supported by Extera, an Avaya Silver Partner.", small=True, eyebrow="Phone systems"), "Avaya IP Office")

# --- Editions ---
ipo_page("avaya-ipo-editions.html", "Avaya IP Office Editions, Capacity and Subscription | Extera Limited",
    "Avaya IP Office editions explained: Basic, Essential, Preferred, Server Edition, Select and Subscription, with user and site capacity.",
    "Editions", "and Scale", "Pick the right size of system, from a handful of users to thousands, and buy it outright or by subscription.", "Editions and Scale",
    feature("Editions", "Choose the right size and type of system", "IP Office comes in editions that grow with your business. Smaller sites run on a compact control unit. Larger or multi-site businesses run on a software server, with extra capacity and resilience.", ["Compact control unit for smaller businesses", "A Linux-based server for larger or multi-site systems", "A premium Select tier for the highest capacity", "A subscription option that is paid monthly per user"], "server", cta=QIPO, img=f'<figure class="art"><img src="assets/art/scale-up.svg" width="1920" height="1080" loading="lazy" alt=""></figure>'),
    f"""<section class="alt"><div class="wrap">
{heading("The range", "Editions at a glance", "Capacities are published by Avaya and change between releases, so we confirm them for the release we quote.")}
{spec_table(["Edition", "Runs on", "Typical users", "What it adds"], [
 ("Basic Edition", "Compact control unit", "Fewer than 25", "Simple telephony and messaging"),
 ("Essential Edition", "Compact control unit", "Around 20 to 99", "IP telephony on top of the basics"),
 ("Preferred Edition", "Compact control unit", "Around 21 to 250", "Unified communications and Voicemail Pro, including advanced voicemail"),
 ("Advanced Edition", "Added to Preferred", "As Preferred", "Contact centre tools such as analytics, call recording and IVR"),
 ("Server Edition", "Linux-based server", "Around 100 to 2,000", "Larger scale and resilience with a secondary server"),
 ("Select", "Server, premium tier", "Up to around 3,000", "Extended capacity, performance and resilience options"),
 ("Subscription", "Compact unit or server", "Around 21 to 250 (unit), up to about 3,000 (server)", "The same features, paid monthly per user"),
])}
</div></section>
<section><div class="wrap">
{feature("Scale", "Grow without replacing the system", "A Server Edition system can be upgraded to Select later without losing configuration or data. Multiple sites can be networked, with Avaya stating up to 150 locations.", ["Add users and extensions as you grow", "Network sites into one system", "Upgrade Server Edition to Select later", "Keep one dial plan and one directory"], "building", flip=True)}
</div></section>
<section class="alt"><div class="wrap">
{heading("Buying", "Licences or subscription?")}
<div class="grid g2">
<div class="card"><h3>Perpetual licences</h3><p>Pay up front for licences per user and feature. Suited to businesses that prefer a one-off cost and keep systems for many years.</p></div>
<div class="card"><h3>Subscription</h3><p>Pay monthly per user, with the same features as Select. Suited to businesses that prefer predictable monthly costs and an easier route to upgrades.</p></div>
</div>
</div></section>""",
    [("Which edition do I need?", "It depends on your users, sites and whether you need unified communications or a contact centre. We recommend the smallest edition that fits."),
     ("Can I upgrade later?", "Yes. Moving from a smaller edition to a larger one, or from Server Edition to Select, is possible. Moving back down means a rebuild."),
     ("Are the user numbers exact?", "They are Avaya's published ranges and differ between releases and documents, so we confirm them for your release."),
     ("Is subscription more expensive?", "It spreads cost over time and includes the features of Select. We compare it with licences in your quote.")],
    "Tell us your users and sites and we will recommend an edition.")

# --- Apps and mobility ---
ipo_page("avaya-ipo-apps.html", "Avaya IP Office Workplace, Mobility and DECT | Extera Limited",
    "Avaya Workplace, one-X Portal, DECT wireless handsets, hot desking and remote working for Avaya IP Office.",
    "Apps", "and Mobility", "Give staff their office extension on any device, at home or on site, with wireless handsets where they roam.", "Apps and Mobility",
    feature("Avaya Workplace", "Your office phone on your computer and mobile", "Avaya Workplace is the app for IP Office. It runs on Android, iOS, macOS and Windows, giving staff their extension, contacts and presence wherever they are.", ["Android, iOS, macOS and Windows apps", "Basic and Advanced modes to match each user", "One number on every device", "Directory, presence and conference control"], "mobile", cta=QIPO, img=f'<figure class="art"><img src="assets/art/collab-apps.svg" width="1920" height="1080" loading="lazy" alt=""></figure>'),
    f"""<section class="alt"><div class="wrap">
{heading("Mobility", "Work wherever you are")}
{cards([
 ("phone", "One number", "Calls reach you on a desk phone, computer or mobile."),
 ("wifi", "Wi-Fi calling", "Use Wi-Fi to cut carrier charges when staff are away from the office."),
 ("users", "one-X Portal", "A web portal for calls, directory, presence and voicemail."),
 ("clock", "Hot desking", "Log in to any phone and it becomes your extension, with remote hot desking too."),
 ("globe", "Click to call", "WebRTC click-to-call works with Google, Salesforce and Microsoft 365."),
 ("wrench", "Web Manager", "Administer the system from a web browser."),
])}
</div></section>
<section><div class="wrap">
{feature("Wireless DECT", "Cordless handsets that roam the whole site", "Avaya Wireless DECT lets staff in warehouses, shops and clinics take their extension with them. A Linux-based system can support up to 1,500 DECT extensions with Avaya's latest DECT release.", ["Cordless handsets that cover large sites", "Handsets stay on your IP Office system", "Good for roaming roles", "Capacity for large estates"], "phone", flip=True, img=f'<figure class="art"><img src="assets/art/dect.svg" width="1920" height="1080" loading="lazy" alt=""></figure>')}
</div></section>
<section class="alt"><div class="wrap">
{feature("Remote workers", "Home phones without a VPN", "With Avaya's session border controller, home workers can use an IP phone on their home broadband, with no VPN and the same extension as the office.", ["Office extension at home", "No VPN for the phone", "Secured by a session border controller", "Same features as in the office"], "shield", img=f'<figure class="art"><img src="assets/art/remote-worker.svg" width="1920" height="1080" loading="lazy" alt=""></figure>')}
</div></section>""",
    [("What is Avaya Workplace?", "The IP Office app for Android, iOS, macOS and Windows, giving users their extension, contacts and presence."),
     ("Can staff work from home?", "Yes. The app or a home IP phone can use the office extension from anywhere."),
     ("Do I need a VPN for home phones?", "Not for the phone, if you use an Avaya session border controller."),
     ("Can I use cordless handsets?", "Yes. Avaya Wireless DECT handsets work with IP Office.")],
    "Tell us how your team works and we will plan the right apps and handsets.")

# --- Contact centre ---
ipo_page("avaya-ipo-contact-centre.html", "Avaya IP Office Contact Centre | Extera Limited",
    "Avaya IP Office Contact Center, call reporting and recording: multichannel customer service for small and mid-size teams.",
    "Contact", "Centre", "Add call reporting, recording or a full multichannel contact centre when your team needs one.", "Contact Centre",
    feature("Contact centre", "Customer service tools that grow with you", "IP Office can add a contact centre when your team needs one, from simple call reporting and recording to a full multichannel contact centre. It can run in the cloud or onsite.", ["Voice, email, web chat, SMS and fax in one platform", "Real-time agent seats and dashboards", "Call recording, tracking and reporting", "Cloud or onsite deployment"], "headset", cta=("Get a contact centre quote", "contact.html")),
    f"""<section class="alt"><div class="wrap">
{heading("The tiers", "Pick the level that fits")}
{spec_table(["Option", "What it is", "Best for"], [
 ("Call Reporting", "Reports on incoming calls and call recording", "Teams that want to measure and improve call handling"),
 ("Advanced Edition", "Contact centre tools on the IP Office edition, including analytics, recording, IVR and wallboards", "Smaller contact centres"),
 ("IP Office Contact Center", "A multichannel contact centre for small and mid-size businesses", "Teams that handle voice and digital contacts"),
 ("Contact Center Select", "An enterprise-class contact centre with advanced self-service and intelligent routing", "Larger operations"),
])}
<p class="vendor-note">Agent seats are licensed separately from the phone system. We include them in your quote.</p>
</div></section>
<section><div class="wrap">
{heading("What it does", "Tools for agents and managers")}
{cards([
 ("headset", "Multichannel agents", "Handle voice and digital contacts in one agent view."),
 ("signal", "Real-time dashboards", "Live views of queues and agents, with PC wallboards."),
 ("shield", "Recording", "Record calls for training and compliance, with password-protected storage."),
 ("route", "IVR and auto attendant", "Menus and self-service that route callers using Voicemail Pro."),
 ("clip", "Reporting", "Reports on call volumes, answer times and agent activity."),
 ("cloud", "Outbound campaigns", "Use agent downtime for outbound campaigns such as follow-ups."),
])}
</div></section>
<section class="alt"><div class="wrap">
{feature("Reporting", "Call reporting that shows what matters", "Call reporting turns raw call data into clear reports, so managers can see how teams perform and where to improve.", ["Incoming call tracking", "Agent and queue reports", "Call recording linked to the call", "Dashboards for supervisors"], "signal", flip=True, img=f'<figure class="art"><img src="assets/art/analytics.svg" width="1920" height="1080" loading="lazy" alt=""></figure>')}
</div></section>
<section><div class="wrap">
{heading("Compare", "Other contact centre options")}
<div class="table-wrap"><table><thead><tr><th scope="col">Option</th><th scope="col">Best for</th></tr></thead><tbody>
<tr><th scope="row">IP Office contact centre</th><td>Avaya users wanting multichannel service</td></tr>
<tr><th scope="row"><a href="3cx-ai-analytics.html">3CX built-in</a></th><td>Smaller inbound teams</td></tr>
<tr><th scope="row"><a href="gamma-horizon-contact.html">Gamma Horizon Contact</a></th><td>Hosted teams on Horizon</td></tr>
<tr><th scope="row"><a href="8x8-contact-centre.html">8x8 contact centre</a></th><td>Growing multichannel teams wanting AI and workforce tools</td></tr>
</tbody></table></div>
</div></section>""",
    [("What channels does it support?", "Voice, email, web chat, SMS and fax in the multichannel contact centre."),
     ("Do I need Voicemail Pro?", "Contact centre deployments use Voicemail Pro for IVR and auto attendant."),
     ("Is it cloud or onsite?", "It can be delivered either way."),
     ("How are agents licensed?", "Agent seats are licensed separately from the phone system, and we include them in your quote.")],
    "Tell us about your team and call volumes and we will recommend a contact centre.")

# --- Resilience and support ---
ipo_page("avaya-ipo-resilience.html", "Avaya IP Office Resilience, Security and Support | Extera Limited",
    "Avaya IP Office survivability, security, SIP trunks and the upgrade path to the latest release, supported by Extera.",
    "Resilience", "and Support", "Keep calls going when something fails, and keep your system supported and up to date.", "Resilience and Support",
    feature("Survivability", "Keep calls going when a link fails", "IP Office is designed to keep working when something fails. Sites can keep making calls if the link to the main system drops, and server systems can be made resilient with a second server.", ["Survivability for sites that lose the main link", "Secondary server for resilience", "Alternate route selection for outgoing calls", "Resilience options on Select and Subscription systems"], "shield", cta=QIPO, img=f'<figure class="art"><img src="assets/art/failover.svg" width="1920" height="1080" loading="lazy" alt=""></figure>'),
    f"""<section class="alt"><div class="wrap">
{heading("Security and lines", "Built-in security and flexible lines")}
{cards([
 ("shield", "Security built in", "Always-on security features and support for encrypted extensions."),
 ("route", "SIP trunks", "Connect to the telephone network over SIP, the modern replacement for ISDN. See <a href='sip-trunks.html'>SIP trunks</a>."),
 ("clock", "Moving off ISDN", "We plan your move away from ISDN lines. See <a href='business-lines.html'>lines and calls</a>."),
 ("wifi", "Remote access", "A session border controller secures home and mobile users."),
 ("clip", "Voicemail Pro", "Advanced voicemail and call flows for automatic call handling."),
 ("wrench", "Centralised management", "Administer the whole system from a browser, with diagnostics and voice quality monitoring."),
])}
</div></section>
<section><div class="wrap">
{feature("Keeping current", "The upgrade path to the latest release", "Avaya retires older releases. Release 11.1 and earlier lost service pack support in August 2024, and Release 12 is the supported route. Moving on needs a planned path, and we manage it for you.", ["Review your current release and licences", "Move to the supported release in a planned window", "Linux-based systems upgrade via Release 11.1.3 first", "Subscription mode is available for a monthly model"], "clock", flip=True, img=f'<figure class="art"><img src="assets/art/upgrade.svg" width="1920" height="1080" loading="lazy" alt=""></figure>')}
<p class="vendor-note">Release dates and requirements come from Avaya notices and change. We confirm the current position for your system.</p>
</div></section>
<section class="alt"><div class="wrap">
{feature("Support", "Support from Avaya and from us", "Avaya offers support services designed to prevent downtime and restore service quickly, and states that its emergency recovery team restores service in under two hours in 90% of outage incidents. We stay your first point of contact.", ["Maintenance with SLAs, in office hours or 24x7", "Extera as your first call for faults and changes", "Escalation to Avaya where needed", "Upgrades, moves, adds and changes"], "headset", img=f'<figure class="art"><img src="assets/art/uk-support.svg" width="1920" height="1080" loading="lazy" alt=""></figure>')}
<p class="vendor-note">The two-hour recovery figure is Avaya's own claim. See our <a href="support.html">support page</a> for our service options.</p>
</div></section>""",
    [("Is my IP Office release still supported?", "Releases 11.1 and earlier lost service pack support in August 2024, so older systems should plan an upgrade. We check your release."),
     ("What happens if my main site fails?", "Remote sites can keep calling through survivability, and server systems can use a secondary server."),
     ("Does IP Office support SIP trunks?", "Yes. SIP trunks are the usual way to replace ISDN lines."),
     ("Who supports it?", "We do, with escalation to Avaya where needed. See <a href='support.html'>support</a>.")],
    "Tell us your IP Office release and we will check it and plan any upgrade.")


# ---------- Phone systems hub ----------
SYSTEMS = [
    # title, overview file, logo html, summary, bullets, extra links
    ("3CX", "3cx.html", '<span class="logo-tile"><img src="assets/logos/3cx-grey.jpg" width="200" height="84" loading="lazy" alt="3CX logo"></span>',
     "A flexible software phone system that runs onsite, in your own cloud or hosted for you. It brings voice, video, live chat and a built-in contact centre into one licence, with apps for every device.",
     ["Lowest running cost, with licensing by simultaneous calls", "Choose where it runs, and your own handsets and SIP trunks", "3CX Gold Partner, so we install and support it ourselves"],
     [("Apps", "3cx-apps.html"), ("Video and chat", "3cx-video-chat.html"), ("Integrations", "3cx-integrations.html"), ("AI and analytics", "3cx-ai-analytics.html")]),
    ("8x8", "8x8.html", '<span class="logo-tile"><img src="assets/logos/8x8-dark.svg" width="150" height="71" loading="lazy" alt="8x8 logo"></span>',
     "A fully hosted cloud platform that brings calling, video meetings, team chat and a full contact centre together, charged per user per month, with nothing to run yourself.",
     ["Nothing to host or maintain, run by 8x8", "A full omnichannel contact centre with AI and workforce tools", "Strong for international and multi-site businesses"],
     [("Voice and messaging", "8x8-voice.html"), ("Meetings", "8x8-meetings.html"), ("Contact centre", "8x8-contact-centre.html"), ("Security", "8x8-security.html")]),
    ("Gamma Horizon", "gamma-horizon.html", '<span class="logo-tile"><img src="assets/logos/gamma.svg" width="190" height="43" loading="lazy" alt="Gamma logo"></span>',
     "A hosted business phone system from UK carrier Gamma, running on Gamma's own network. Add collaboration, Microsoft Teams or Webex, a contact centre and call analytics as you need them.",
     ["Carrier-backed, with calls on Gamma's own UK network", "Works with Microsoft Teams, Webex or its own Collaborate app", "Akixi analytics and 200+ CRM integrations"],
     [("Apps", "gamma-horizon-apps.html"), ("Teams and Webex", "gamma-horizon-teams.html"), ("Contact centre", "gamma-horizon-contact.html"), ("Network", "gamma-horizon-network.html")]),
    ("Avaya IP Office", "avaya-ip-office.html", '<span class="logo-tile"><img src="assets/logos/avaya.jpg" width="285" height="90" loading="lazy" alt="Avaya logo"></span>',
     "A proven onsite business phone system from Avaya, scaling from a handful of users to thousands across up to 150 sites, with optional monthly subscription and a built-in contact centre.",
     ["Keep control of your system on your own premises", "Scales from small offices to multi-site businesses", "Avaya Silver Partner, so we install and support it ourselves"],
     [("Editions", "avaya-ipo-editions.html"), ("Apps and mobility", "avaya-ipo-apps.html"), ("Contact centre", "avaya-ipo-contact-centre.html"), ("Resilience", "avaya-ipo-resilience.html")]),
]


def system_card(title, href, logo, summary, bullets, links):
    more = " &middot; ".join(f'<a href="{h}">{t}</a>' for t, h in links)
    return (f'<article class="sys-card"><div class="sys-logo">{logo}</div><div class="sys-body"><h3><a href="{href}">{title}</a></h3><p>{summary}</p>{ticks(bullets)}'
            f'<div class="sys-foot"><a class="btn" href="{href}">See {title}</a><p class="sys-links">{more}</p></div></div></article>')


body = f"""
<section><div class="wrap">
{heading("Phone systems", "Four proven systems, one team to look after them", "Extera supplies, installs and supports all four, so we can recommend the one that really fits, not just the one we sell. Here is each system in a few lines, with links to the detail.")}
<div class="sys-grid">{"".join(system_card(*s) for s in SYSTEMS)}</div>
</div></section>

<section class="alt"><div class="wrap">
{heading("Compare", "Which one suits you?", "A quick guide. Each system has strengths, and the right choice depends on who runs it and how your team works.")}
<div class="table-wrap"><table><thead><tr><th scope="col"></th><th scope="col"><a href="3cx.html">3CX</a></th><th scope="col"><a href="8x8.html">8x8</a></th><th scope="col"><a href="gamma-horizon.html">Gamma Horizon</a></th><th scope="col"><a href="avaya-ip-office.html">Avaya IP Office</a></th></tr></thead><tbody>
<tr><th scope="row">How it runs</th><td>Onsite, your cloud or hosted</td><td>Hosted</td><td>Hosted on Gamma's network</td><td>Onsite, or monthly subscription</td></tr>
<tr><th scope="row">How it is charged</th><td>Annual licence by simultaneous calls</td><td>Per user per month</td><td>Per user per month, in tiers</td><td>Licences, or per user per month</td></tr>
<tr><th scope="row">Contact centre</th><td>Built-in queues and wallboards</td><td>Full omnichannel platform</td><td>Horizon Contact and Akixi analytics</td><td>IP Office Contact Center and reporting</td></tr>
<tr><th scope="row">Microsoft Teams</th><td>Microsoft 365 sync</td><td>8x8 Voice for Teams</td><td>Horizon for Teams</td><td>Via integrations</td></tr>
<tr><th scope="row">Scale</th><td>Small to large</td><td>Small to enterprise</td><td>Small to mid-size</td><td>5 to 3,000 users</td></tr>
<tr><th scope="row">Best for</th><td>Low cost and flexibility</td><td>International and multichannel</td><td>UK carrier-backed hosted calling</td><td>Existing Avaya users and multi-site</td></tr>
</tbody></table></div>
<p style="margin-top:16px" class="actions left"><a class="btn outline dark" href="3cx-vs-8x8.html">See our 3CX vs 8x8 comparison</a><a class="btn outline dark" href="contact-centres.html">Contact centre options</a></p>
</div></section>

<section><div class="wrap">
{heading("By situation", "Where to start", "A quick route to the right page.")}
{cards([
 ("wrench", "I want the lowest running cost", "3CX, with licensing by simultaneous calls and your choice of hosting.", "3cx.html", "3CX"),
 ("cloud", "I want nothing to look after", "8x8 or Gamma Horizon, both fully hosted.", "8x8.html", "8x8"),
 ("building", "I already have Avaya", "Keep your investment and upgrade, expand or move at your own pace.", "avaya-ip-office.html", "Avaya IP Office"),
 ("headset", "I run a contact centre", "Compare queues, wallboards and full contact centre platforms.", "contact-centres.html", "Contact centres"),
 ("users", "I live in Microsoft Teams", "Add calling to Teams with 8x8, Gamma Horizon or 3CX.", "gamma-horizon-teams.html", "Teams options"),
 ("globe", "I need to leave ISDN", "Move to a hosted or SIP-based system before the switch-off.", "business-lines.html", "Lines and calls"),
], link=True)}
</div></section>

{cta_band("Tell us about your team and we will recommend the right phone system, and quote it.", "Not sure which to choose?")}
"""
page("phone-systems.html", "Business Phone Systems: 3CX, 8x8, Gamma Horizon, Avaya | Extera Limited",
     "Compare the business phone systems Extera supplies and supports: 3CX, 8x8, Gamma Horizon and Avaya IP Office, with links to each.",
     body, hero("Phone", "Systems", "3CX, 8x8, Gamma Horizon and Avaya IP Office: supplied, installed and supported by Extera.", small=True, eyebrow="Phone systems"), "Phone Systems")


def net_card(name, logo, text, link_label, url):
    return (f'<article class="sys-card net-row"><div class="sys-logo"><span class="logo-tile">{logo}</span></div>'
            f'<div class="sys-body"><h3>{name}</h3><p>{text}</p>'
            f'<div class="sys-foot"><a class="btn outline dark" href="{url}" rel="noopener" target="_blank">{link_label}<span class="sr-only"> (opens in a new tab)</span></a></div></div></article>')


body = f"""
<section><div class="wrap">
{feature("Business mobile", "Mobiles alongside the rest of your telecoms", "Business mobile contracts and SIMs from Extera, managed with your phone system and lines so you have one supplier for everything.", ["Handsets and SIM-only plans", "Mobile apps that link to your office phone system", "One account manager across voice, data and mobile", "Data SIMs for routers and tablets"], "mobile", cta=("Get a mobile quote", "contact.html"))}
</div></section>
<section class="alt"><div class="wrap">
{heading("Networks", "EE, Vodafone and O2, all supplied by Extera", "We supply business mobile on all three major UK networks, so we can recommend the one with the best coverage for your people and places, not just the one we happen to sell.")}
<div class="sys-grid">
{net_card("EE", '<img src="assets/logos/ee.svg" width="96" height="96" loading="lazy" alt="EE logo">', "Business handsets, SIM-only plans and data SIMs on the EE network.", "EE Business", "https://ee.co.uk/business")}
{net_card("Vodafone", '<img src="assets/logos/vodafone.svg" width="220" height="55" loading="lazy" alt="Vodafone logo">', "Business handsets, SIM-only plans and data SIMs on the Vodafone network.", "Vodafone Business", "https://www.vodafone.co.uk/business")}
{net_card("O2", '<img src="assets/logos/o2.svg" width="86" height="82" loading="lazy" alt="O2 logo">', "Business handsets, SIM-only plans and data SIMs on the O2 network.", "O2 Business", "https://www.o2.co.uk/business")}
</div>
<div class="card" style="margin-top:32px"><h3>Check coverage before you choose</h3><p>Coverage differs from postcode to postcode, so we check each network where your staff live and work. You can also use Ofcom's independent <a href="https://checker.ofcom.org.uk" rel="noopener" target="_blank">mobile coverage checker</a>, which compares all the networks.</p></div>
<p class="vendor-note">EE, Vodafone and O2 names and logos are trademarks of their owners.</p>
</div></section>
<section><div class="wrap">
{heading("What we offer", "Mobile, matched to how your team works")}
{cards([
 ("mobile", "Handset contracts", "Latest handsets on business contracts, with upgrades planned for you."),
 ("signal", "SIM only", "Flexible SIM-only plans when you already have the handsets."),
 ("wifi", "Data and failover", "Data SIMs for tablets and routers, including 4G/5G backup for your office broadband."),
 ("phone", "Fixed mobile convergence", "Make mobiles part of your office phone system with the same extension and voicemail."),
 ("users", "Team plans", "Share allowances across your team to avoid paying for unused minutes."),
 ("headset", "Support", "One number to call for contract, billing and faults."),
])}
</div></section>
<section class="alt"><div class="wrap">
{heading("Getting started", "Switching is simpler than you think")}
{steps([("Review", "We look at your current bills and usage."), ("Recommend", "We suggest the right plans and handsets and show the savings."), ("Switch", "We arrange the switch and number porting."), ("Manage", "We look after changes, new starters and leavers.")])}
</div></section>
{faq([("Can I keep my mobile numbers?", "Yes. We port numbers to the new plan."), ("Which networks do you offer?", "We supply EE, Vodafone and O2. We check coverage where your people work and recommend the best fit."), ("Can mobiles work with the office phone system?", "Yes. With fixed mobile convergence and mobile apps, staff can use the same number and features anywhere.")], alt=True)}
{cta_band()}
"""
page("mobile.html", "Business Mobile | Extera Limited",
     "Business mobile contracts and SIMs supplied by Extera, integrated with your phone system and connectivity.",
     body, hero("Business", "Mobile", "Mobiles on EE, Vodafone and O2, managed with your phones and lines under one account.", small=True, eyebrow="Mobile"), "Mobile")

# ---------- Cabling ----------
body = f"""
<section><div class="wrap">
{feature("Data cabling", "Cabling built to last", "The hidden heart of your digital infrastructure. We install structured cabling that handles the needs of today and tomorrow, whether for a new office, a move or an upgrade.", ["Copper and fibre cabling", "New builds, refits and office moves", "Tested and documented on completion", "Installed together with your phones and connectivity"], "cable", cta=("Book a site survey", "contact.html"))}
</div></section>
<section class="alt"><div class="wrap">
{heading("Services", "What we install")}
{cards([
 ("cable", "Copper cabling", "Cat6 and Cat6a structured cabling for desks, meeting rooms and devices."),
 ("bolt", "Fibre optic", "Fibre links between buildings, floors and comms rooms."),
 ("server", "Cabinets and comms rooms", "Racks, patch panels and tidy, labelled cabinets."),
 ("wifi", "Wireless cabling", "Cabling for Wi-Fi access points and wireless site surveys."),
 ("clip", "Testing and certification", "Every link tested and documented so you know what you have."),
 ("wrench", "Moves and changes", "Extra points, rearrangements and fixes without disruption."),
])}
</div></section>
<section><div class="wrap">
{feature("Approved installers", "Manufacturer-approved, safety-accredited", "We are certified installers for IDAC (Datwyler) and Brand-Rex cabling systems, and a CHAS Accredited Contractor, so our engineers are trained, approved and safe to have on your site.", ["IDAC (Datwyler) certified installer", "Brand-Rex certified installer", "CHAS Accredited Contractor", "ISO 9001:2015 quality management"], "shield", flip=True)}
</div></section>
<section class="alt"><div class="wrap">
{heading("Cable types", "Cat5e, Cat6, Cat6a or fibre?", "A quick guide. We recommend a mix based on your equipment, distances and budget for the future.")}
{spec_table(["Cable", "Typical use", "Good to know"], [
 ("Cat5e", "Basic office networks and phones", "Fine for light use, but increasingly the minimum rather than the target."),
 ("Cat6", "Most new office installations", "Supports 1Gbps comfortably and 10Gbps over shorter runs."),
 ("Cat6a", "Busy networks, Wi-Fi access points, future-proofing", "Supports 10Gbps over the full 90 metre link, but is thicker and costs more."),
 ("Fibre optic", "Links between floors, buildings and comms rooms", "High speed over long distances and immune to electrical interference."),
])}
</div></section>
<section><div class="wrap">
{heading("Planning", "What to think about before you cable")}
{cards([
 ("clip", "How many points?", "Count desks, meeting rooms, phones, printers, displays and access points, then add room to grow."),
 ("wifi", "Wi-Fi coverage", "Access points need good cabling and sensible positions. A wireless survey avoids dead spots."),
 ("server", "Where the cabinet goes", "A ventilated, secure comms room with power and space to expand makes the network easier to run."),
 ("clock", "Timing and access", "Out-of-hours or phased work keeps disruption low in an occupied office."),
 ("phone", "Phones and internet", "Cabling, phones and connectivity installed together means one team and one date."),
 ("shield", "Safety and standards", "CHAS accreditation and tested, documented links give you evidence the job was done properly."),
])}
</div></section>
<section class="alt"><div class="wrap">
{heading("How it works", "A cabling project, step by step")}
{steps([("Survey", "We visit, measure up and discuss your requirements."), ("Quote", "A clear, itemised quote and programme."), ("Install", "Our engineers install, label and tidy everything."), ("Test", "Every link is tested, documented and handed over.")])}
</div></section>
{faq([("Can you work around our office hours?", "Yes. We can schedule work out of hours or in phases to keep disruption low."), ("Do you handle office moves?", "Yes. We plan cabling, phones and internet together so you are up and running on day one."), ("Do you cable for Wi-Fi?", "Yes. We install the cabling for access points and can carry out wireless surveys."), ("Is there a warranty on the cabling?", "Our approved-installer status means we can work to the manufacturers' systems. Ask us for the warranty terms that apply to the system you choose."), ("Can you fix or add to existing cabling?", "Yes. We can trace, test and label what you have, add extra points and tidy up cabinets."), ("Do you do structured cabling in Banbury and Oxfordshire?", "Yes. We are based in Banbury and our engineers also cover the rest of mainland UK.")])}
{cta_band("Planning a move or refit? Ask us about a site survey.")}
"""
page("data-cabling.html", "Data Cabling | Extera Limited",
     "Structured data cabling installation by Extera for new offices, refits and moves, alongside phones and connectivity.",
     body, hero("Data", "Cabling", "Neat, tested cabling installed by trained engineers, so your network works properly from day one.", small=True, eyebrow="Data cabling"), "Data Cabling")

# ---------- Support ----------
body = f"""
<section><div class="wrap split top">
<div>{heading("Support", "Support that fits how you buy")}
<p>Extera offers SLA-backed maintenance contracts that include routine system changes (moves, adds and changes). If you prefer ad-hoc support, we can help with that too.</p>
<p>More complex changes and office moves are scoped and quoted by our project team.</p></div>
<div class="card urgent"><h3>System down? Urgent issue?</h3>
<p>Call <a href="tel:{TEL}"><b>{PHONE}</b></a>. No contract is needed to get help.</p>
<div class="actions left"><a class="btn" href="tel:{TEL}">Call {PHONE}</a></div></div>
</div></section>
<section class="alt"><div class="wrap">
{heading("Options", "Choose the level of cover")}
{cards([
 ("clock", "Maintenance contract", "Break-fix cover in office hours or 24x7 with an SLA, including routine changes."),
 ("phone", "Ad-hoc support", "No contract? Call or send a request and we will advise and quote."),
 ("clip", "Projects and moves", "Larger changes and office moves scoped and priced by our project team."),
])}
</div></section>
<section><div class="wrap">
{heading("Contract or ad hoc?", "Maintenance contract compared with ad-hoc support")}
{spec_table(["", "Maintenance contract", "Ad-hoc support"], [
 ("Response", "Agreed in an SLA, in office hours or 24x7", "Best efforts, as engineers are available"),
 ("Routine changes", "Included (moves, adds and changes)", "Quoted when needed"),
 ("Faults", "Covered by the contract", "Diagnosed and quoted"),
 ("Cost", "Fixed and predictable", "Pay only when you need help"),
 ("Best for", "Phones your business depends on", "Smaller or less critical systems"),
])}
</div></section>
<section class="alt"><div class="wrap">
{heading("What we support", "Phone systems we look after")}
{cards([
 ("phone", "3CX", "As a 3CX Gold Partner we support hosted and onsite systems.", "3cx.html", "3CX"),
 ("cloud", "8x8", "Cloud phone system administration and user changes.", "8x8.html", "8x8"),
 ("cloud", "Gamma Horizon", "Hosted telephony, handsets and users.", "gamma-horizon.html", "Gamma Horizon"),
 ("phone", "Avaya IP Office", "Maintenance, upgrades and changes for IP Office systems.", "avaya-ip-office.html", "Avaya IP Office"),
 ("globe", "Connectivity", "Broadband, leased lines and SIP trunks we have supplied.", "connectivity.html", "Connectivity"),
 ("headset", "Handsets and headsets", "Replacements and new equipment via Extera Direct.", "extera-direct.html", "Extera Direct"),
], link=True)}
</div></section>
<section><div class="wrap">
{heading("Before you call", "What to have ready")}
{ticks(["Your company name and the site affected", "The make and model of the phone system, if you know it", "What happened, when it started and who is affected", "Any error messages, or whether the fault is on one handset or everywhere", "A direct number we can call you back on"])}
</div></section>
<section class="alt"><div class="wrap">
{heading("Getting help", "How a support request works")}
{steps([("Contact us", "Call, email or use the form below."), ("We respond", "We triage and agree the next step with you."), ("Fix", "We resolve it and keep you informed."), ("Review", "We confirm everything works and tidy up.")])}
</div></section>
<section class="alt" id="request-support"><div class="wrap split top">
<div>{heading("Request support", "Send us a request")}
<form action="send.php" method="post">
<input type="hidden" name="form" value="support">
<div class="hp" aria-hidden="true"><label>Leave this empty<input name="website" tabindex="-1" autocomplete="off"></label></div>
<label>Name<input name="name" autocomplete="name" required></label>
<label>Email<input type="email" name="email" autocomplete="email" required></label>
<label>Phone<input type="tel" name="phone" autocomplete="tel"></label>
<label>Message<textarea name="message"></textarea></label>
<p class="form-note">By sending this form you agree that we may use your details to reply to you. We do not share them.</p>
<button class="btn" type="submit">Send request</button>
</form></div>
{contact_card()}
</div></section>
{accreditations()}
{faq([("What does a maintenance contract include?", "Break-fix cover to the SLA you choose, plus routine changes to your system. Ask us for the options."), ("Can you support a system you did not install?", "In many cases, yes. Tell us what you have and we will advise."), ("Is out-of-hours cover available?", "Yes. We offer 24x7 cover with SLAs for businesses that need it."), ("Can you support us remotely?", "Yes. Many changes and faults can be fixed remotely and quickly. If an engineer needs to visit, we arrange it."), ("Do you support phone systems in Oxfordshire?", "Yes. We are based in Banbury, so Oxfordshire sites are close, and our engineers cover the rest of mainland UK."), ("What if the fault is with our broadband or phone lines?", "We help find where the fault is. If we supplied the connectivity we chase it for you, and if not we give you the evidence to take to your provider.")], alt=True)}
"""
page("support.html", "Support | Extera Limited",
     "Extera support: SLA maintenance contracts, ad-hoc help and urgent assistance for business phone systems.",
     body, hero("Extera", "Support", "Fast help when something breaks and regular care so it does not: maintenance, changes and urgent support.", small=True, actions=[(f"Call {PHONE} for urgent help", f"tel:{TEL}", False, False), ("Send a request", "#request-support", True, False)], eyebrow="Support"), "Support")

# ---------- Extera Direct ----------
body = f"""
<section><div class="wrap">
{feature("Online store", "Telecoms and office products at great prices", "Extera Direct is our online store, where you can buy a wide range of telecoms and office products without a quote or a call. Headsets, conference phones and meeting room equipment are the most popular, so we have put a buying guide below.", ["Business phone systems", "Telephones, headsets and conference phones", "Video conferencing and meeting room equipment", "Networking, installation and office products"], "cart", cta=("Visit the shop", "https://www.exteradirect.co.uk"))}
</div></section>
<section class="alt"><div class="wrap">
{heading("Categories", "What you can buy")}
{cards([
 ("phone", "Business phone systems", "Systems for small offices and growing teams."),
 ("phone", "Telephones", "Desk phones and cordless handsets."),
 ("headphones", "Headsets", "Corded and cordless headsets for office and contact centre use."),
 ("users", "Conference phones", "Clear audio for meeting rooms."),
 ("cable", "Networking and installation", "Cabling, switches and installation products."),
 ("clip", "Office products", "Everyday office supplies and equipment."),
])}
</div></section>

<section><div class="wrap">
{feature("Headsets", "A headset for every way of working", "A good headset improves call quality, cuts background noise and lets people use both hands. The right one depends on how a person works, so we help you match the headset to the role, the phone system and the budget.", ["Wired USB headsets for desk-based staff", "Wireless DECT headsets for roaming around an office", "Bluetooth headsets for mobiles and flexible working", "Noise-cancelling microphones for open-plan offices and homes"], "headphones", cta=("Shop headsets", "https://www.exteradirect.co.uk"))}
</div></section>

<section class="alt"><div class="wrap">
{heading("Which headset?", "Match the headset to the person", "A quick guide. Ranges and features vary by model, so check the product page for the exact figures.")}
<div class="table-wrap"><table><thead><tr><th scope="col">Type</th><th scope="col">Best for</th><th scope="col">Good to know</th></tr></thead><tbody>
<tr><th scope="row">Wired USB</th><td>Desk-based staff, contact centres, home working</td><td>Plug in and use, no charging. A cable to a computer or desk phone.</td></tr>
<tr><th scope="row">Wireless DECT</th><td>Reception, supervisors, anyone who moves around</td><td>A base station gives stable, long-range wireless, typically across a whole office floor.</td></tr>
<tr><th scope="row">Bluetooth</th><td>Mobile and hybrid workers</td><td>Works with a phone and, via a USB dongle, a computer. Range is shorter than DECT.</td></tr>
<tr><th scope="row">Single ear (mono)</th><td>Staff who need to hear the room around them</td><td>Keeps one ear free for colleagues and visitors.</td></tr>
<tr><th scope="row">Both ears (duo)</th><td>Busy or noisy environments</td><td>Blocks more background noise so calls are easier to hear.</td></tr>
</tbody></table></div>
</div></section>

<section><div class="wrap">
{heading("Choosing well", "What to look for in a business headset")}
{cards([
 ("shield", "Certified for your platform", "Look for headsets certified for Microsoft Teams, Zoom or your phone system, which add one-touch call controls and a tested experience."),
 ("signal", "A good microphone", "Noise reduction on the microphone matters more than on the speakers, because it decides how you sound to callers."),
 ("clock", "Battery life", "For wireless models, check talk time and whether the base can charge the headset."),
 ("users", "Comfort", "Weight, ear cushions and fit matter if someone wears a headset for hours."),
 ("wrench", "Quick disconnect", "A quick-disconnect cable lets a headset work with both a desk phone and a computer."),
 ("headset", "Busy light", "An indicator that shows when someone is on a call reduces interruptions in open-plan offices."),
])}
</div></section>

<section class="alt"><div class="wrap">
{feature("Speakerphones and audio", "Be heard clearly, wherever the call is", "Poor audio is the commonest reason a meeting goes badly. A speakerphone or room audio system with echo cancellation and good microphones lets everyone hear and be heard.", ["Personal USB or Bluetooth speakerphones for desks and huddle rooms", "Larger conference phones for meeting rooms, including SIP models", "Expansion microphones to cover long tables", "Echo cancellation and full-duplex audio for natural conversation"], "users", flip=True, cta=("Shop conference phones", "https://www.exteradirect.co.uk"), img=f'<figure class="art"><img src="assets/art/speakerphone.svg" width="1920" height="1080" loading="lazy" alt=""></figure>')}
</div></section>

<section><div class="wrap">
{feature("Meeting room video", "Video conferencing equipment for any size of room", "Video meetings work best with a camera, microphones and speakers designed for the room, not a laptop on the table. We supply and install complete room systems, from a single video bar to a full boardroom set-up.", ["All-in-one video bars for huddle and small meeting rooms", "Modular systems with extra cameras and microphones for large rooms", "Displays, mounts and cabling supplied and fitted", "Systems for Microsoft Teams, Zoom or your own platform"], "users", img=f'<figure class="art"><img src="assets/art/video-bar-room.svg" width="1920" height="1080" loading="lazy" alt=""></figure>', cta=("Ask about meeting rooms", "contact.html"))}
</div></section>

<section class="alt"><div class="wrap">
{feature("Room size guide", "Choose equipment by the room, not just the price", "As a rule of thumb, small rooms suit a personal speakerphone or a video bar. Larger rooms need extra microphones, a bigger display and sometimes a second camera. We measure the room and the farthest seat before recommending anything.", ["Count how many people will use the room regularly", "Check the distance from the farthest seat to the screen and camera", "Consider echo, windows and background noise", "Plan cabling and power, and the position of the display"], "building", flip=True, img=f'<figure class="art"><img src="assets/art/room-sizes.svg" width="1920" height="1080" loading="lazy" alt=""></figure>')}
<div class="table-wrap" style="margin-top:32px"><table><thead><tr><th scope="col">Room</th><th scope="col">People</th><th scope="col">Audio</th><th scope="col">Video</th></tr></thead><tbody>
<tr><th scope="row">Desk or huddle</th><td>1 to 4</td><td>Personal speakerphone or headset</td><td>Webcam or compact video bar</td></tr>
<tr><th scope="row">Small meeting room</th><td>4 to 8</td><td>Conference phone or the video bar's built-in audio</td><td>All-in-one video bar</td></tr>
<tr><th scope="row">Medium meeting room</th><td>8 to 12</td><td>Conference phone with expansion microphones</td><td>Video bar with extra microphones, or a modular system</td></tr>
<tr><th scope="row">Large room or boardroom</th><td>12 or more</td><td>Ceiling or table microphones and room speakers</td><td>Modular system with one or more cameras</td></tr>
</tbody></table></div>
<p class="vendor-note">These are typical guides, not guarantees. Pickup range and room capacity vary by product, so we check each room.</p>
</div></section>

<section><div class="wrap">
{heading("Compatibility", "Works with your phone system and meeting platform", "We check that equipment works with the systems you use before you buy.")}
{cards([
 ("phone", "Your phone system", "Headsets and handsets for <a href='3cx.html'>3CX</a>, <a href='8x8.html'>8x8</a>, <a href='gamma-horizon.html'>Gamma Horizon</a> and <a href='avaya-ip-office.html'>Avaya IP Office</a>."),
 ("users", "Meeting platforms", "Equipment certified for Microsoft Teams and Zoom, or standard USB equipment for other platforms."),
 ("wifi", "Your connection", "Video needs a steady connection. See <a href='fibre-broadband.html'>fibre broadband</a> and <a href='leased-lines.html'>leased lines</a>."),
 ("cable", "Cabling and power", "We can run network and power cabling for meeting rooms. See <a href='data-cabling.html'>data cabling</a>."),
])}
</div></section>

<section class="alt"><div class="wrap narrow center">
{heading("Brands", "Equipment from trusted makers", "We are partners of leading headset and conferencing brands, so you get advice and support, not just a box.", True)}
<ul class="badges"><li>Jabra Gold Partner</li><li>Plantronics (Poly) Partner</li><li>EPOS</li><li>Sennheiser</li><li>Yealink</li><li>Cisco</li></ul>
</div></section>

<section><div class="wrap">
{heading("Getting it right", "How we help you choose and set up")}
{steps([("Ask", "Tell us how people work, what platform you use and your room sizes."), ("Recommend", "We suggest equipment that suits, with a few options and prices."), ("Supply and install", "We deliver and, for rooms, install, cable and test everything."), ("Support", "We help with set-up, firmware updates and replacements.")])}
</div></section>

{faq([
 ("Will a headset work with my phone system?", "Usually yes. Most business headsets connect by USB, a quick-disconnect cable or a wireless base. We check yours against your handsets and software."),
 ("Is DECT or Bluetooth better?", "DECT suits people who move around an office and need stable, long-range wireless. Bluetooth suits mobile working and personal devices, with a shorter range."),
 ("How many people can one speakerphone cover?", "Personal speakerphones suit small groups. Larger rooms need a conference phone with expansion microphones. We check your room and your farthest seat."),
 ("Do I need a computer in a video-bar room?", "Some video bars run the meeting app themselves, while others use a laptop or a small room computer. We advise on the best set-up for your platform."),
 ("Can you install meeting room equipment?", "Yes. We supply, install and test displays, cameras, microphones and cabling, and can support them afterwards."),
 ("Can I buy online and get advice too?", "Yes. You can order from Extera Direct, and call us for help choosing."),
], alt=True)}

<section><div class="wrap">
<div class="split"><div><h2>Need advice before you buy?</h2><p>If you are not sure what to buy, or want a complete system supplied, installed and supported, talk to the team.</p>
<div class="actions left"><a class="btn" href="contact.html">Get a quote</a><a class="btn outline dark" href="phone-systems.html">See phone systems</a></div></div>
<div class="card"><h3>Buying a whole system?</h3><p>For new phone systems, connectivity and cabling, our <a href="phone-systems.html">phone systems</a> services include installation and support.</p></div></div>
</div></section>
"""
page("extera-direct.html", "Extera Direct | Headsets, Conference Phones and Video Equipment",
     "Extera Direct is Extera's online store, with a buying guide for headsets, speakerphones, video conferencing and meeting room equipment.",
     body, hero("Extera", "Direct", "Headsets, conferencing equipment and office products, with expert advice.", small=True, actions=[("Visit the shop", "https://www.exteradirect.co.uk", False, True), ("Get advice", "contact.html", True, False)], eyebrow="Online store"), "Extera Direct")


# ---------- About ----------
body = f"""
<section><div class="wrap">
{feature("Our story", "Business telecoms since 2001", "Extera Limited was formed in 2001 and has grown steadily every year since. We are based in Banbury, Oxfordshire, close to the M40, with our own engineers covering mainland UK.", ["Started with managed services for large blue-chip companies", "Moved into selling and supporting phone systems", "Now offers communications, connectivity and cabling", "Extera Direct, our online store, has won awards"], "building")}
</div></section>
<section class="alt"><div class="wrap">
{heading("What we offer today", "A full telecoms service under one roof")}
{cards([
 ("phone", "Unified communications", "Cloud and onsite phone systems, from basic telephony to full unified communications.", "3cx.html", "Phone systems"),
 ("headset", "Contact centres", "Queues, recording and reporting.", "contact-centres.html", "Contact centres"),
 ("globe", "Internet connectivity", "Broadband, fibre, leased lines and MPLS.", "connectivity.html", "Connectivity"),
 ("cable", "Data cabling", "Structured copper and fibre cabling.", "data-cabling.html", "Cabling"),
 ("cloud", "Cloud communications", "Hosted voice and collaboration.", "8x8.html", "8x8"),
 ("cart", "Extera Direct", "Telecoms and office products online.", "extera-direct.html", "Extera Direct"),
])}
</div></section>
<section><div class="wrap">
{heading("How we work", "What you can expect from Extera")}
{cards([
 ("users", "One team", "Phones, connectivity, mobiles and cabling from one supplier, with one number to call."),
 ("clip", "Plain advice", "We explain the options and costs in plain English, including when the cheaper option is the right one."),
 ("wrench", "Our own engineers", "People we know install and support your systems, rather than a chain of sub-contractors."),
 ("shield", "Accredited quality", "ISO 9001:2015 quality management and CHAS accredited contractor status."),
 ("clock", "Long-term support", "We stay on after the install with maintenance, changes and help when something breaks."),
 ("route", "Independent choice", "We work with several platforms, so we recommend the one that fits rather than the one we have to sell."),
])}
</div></section>
<section class="alt"><div class="wrap">
{heading("Our partners", "Brands and carriers we work with")}
<p>We are a 3CX Gold Partner and an Avaya Silver Partner, and we supply 8x8, Gamma Horizon, Jabra and Plantronics. For mobiles we supply EE, Vodafone and O2.</p>
{ticks(["3CX Gold Partner", "Avaya Silver Partner", "8x8 and Gamma Horizon cloud telephony", "Jabra and Plantronics headsets", "EE, Vodafone and O2 mobile networks", "IDAC (Datwyler) and Brand-Rex cabling"])}
</div></section>
<section><div class="wrap">
{heading("Who we help", "Businesses of every size, across the UK")}
<p>Our customers range from small offices with a handful of staff to multi-site organisations. We are based in Banbury, Oxfordshire, so local businesses can reach us easily, and our engineers cover the whole of mainland UK. If you are not sure what you need, ask us. We would rather give you a straight answer than sell you the wrong thing.</p>
</div></section>
{accreditations()}
{partner_certs()}
{cta_band("Whether you have two staff or two hundred, we would like to hear from you.", "Work with Extera")}
"""
page("about.html", "About Extera | Business Telecommunication Specialists",
     "Extera Limited has supplied business telecoms from Banbury since 2001: phone systems, connectivity, mobile and data cabling.",
     body, hero("About", "Extera", "A UK telecoms specialist since 2001, with our own engineers, accredited quality and a team you can call.", small=True, eyebrow="About us"), "About")

# ---------- Contact ----------
body = f"""
<section><div class="wrap split top">
<div>{heading("Get in touch", "Get a quote")}
<p>Tell us what you need and we will reply with a clear quote, usually within one working day.</p>
<form action="send.php" method="post">
<input type="hidden" name="form" value="quote">
<div class="hp" aria-hidden="true"><label>Leave this empty<input name="website" tabindex="-1" autocomplete="off"></label></div>
<label>Name<input name="name" autocomplete="name" required></label>
<label>Company<input name="company" autocomplete="organization"></label>
<label>Email<input type="email" name="email" autocomplete="email" required></label>
<label>Phone<input type="tel" name="phone" autocomplete="tel"></label>
<label>Interested in<select name="interest"><option>3CX phone system</option><option>3CX free trial or demo</option><option>8x8 cloud phone system</option><option>Gamma Horizon</option><option>Avaya IP Office</option><option>Contact centre</option><option>Connectivity</option><option>Business mobile</option><option>Data cabling</option><option>Support</option><option>Not sure</option></select></label>
<label>Message<textarea name="message"></textarea></label>
<p class="form-note">By sending this form you agree that we may use your details to reply to you. We do not share them.</p>
<button class="btn" type="submit">Request my quote</button>
</form></div>
<div>{contact_card()}
<div class="card" style="margin-top:24px"><h3>What happens next</h3>{steps([("We reply", "A member of the team gets back to you."), ("We talk it through", "A short call or visit to understand what you need."), ("You get a quote", "A clear proposal with no obligation.")])}</div></div>
</div></section>
<section class="alt"><div class="wrap">
{heading("Other ways to reach us", "Choose what suits you")}
{cards([
 ("phone", "Call us", f"Speak to the team on <a href='tel:{TEL}'>{PHONE}</a>."),
 ("chat", "Email us", f"Write to <a href='mailto:{EMAIL}'>{EMAIL}</a> and we will reply."),
 ("wrench", "Need support?", "Existing customer with a fault or change? Use our <a href='support.html'>support page</a>."),
 ("cart", "Buying equipment?", "Browse headsets and conference phones at <a href='extera-direct.html'>Extera Direct</a>."),
])}
</div></section>
<section><div class="wrap split top">
<div>{heading("Your enquiry", "What to include to get a faster quote")}
{ticks(["How many people, and how many sites", "What you use today (phone system, lines, broadband)", "Any dates you are working to, such as a contract end or office move", "What matters most: cost, features, reliability or simplicity"])}</div>
<div class="card"><h3>Local to Banbury</h3><p>We are based in Banbury, Oxfordshire and cover businesses across Oxfordshire and the rest of the UK. A site visit is often the quickest way to scope cabling and phone system projects.</p></div>
</div></section>
{faq([("How quickly will you reply?", "We aim to reply within one working day."), ("Is there any obligation?", "No. Quotes are free and come with no obligation."), ("Do you only cover Oxfordshire?", "No. We are based in Banbury and our engineers cover mainland UK."), ("Can you visit us?", "Yes. For phone systems and cabling we usually arrange a visit to scope the work.")], alt=True)}
"""
page("contact.html", "Contact Extera | Business Telecommunication Specialists",
     "Contact Extera in Banbury for a quote on phone systems, connectivity, mobile and data cabling.",
     body, hero("Contact", "Extera", "Call us or send an enquiry and we will reply with a clear quote, usually within one working day.", ctas=False, small=True, eyebrow="Contact"), "Contact")


# ---------- Thank you page ----------
body = f"""<section><div class="wrap narrow"><h2>Thank you, your message is on its way</h2>
<p>We aim to reply within one working day. If it is urgent, call <a href="tel:{TEL}">{PHONE}</a>.</p>
<div class="actions left"><a class="btn" href="index.html">Back to the home page</a><a class="btn outline dark" href="phone-systems.html">Explore phone systems</a></div></div></section>"""
page("thanks.html", "Message Sent | Extera Limited", "Thank you for contacting Extera.", body,
     hero("Thank", "you", "We have received your message.", ctas=False, small=True))



# ---------- Legal pages ----------
UPDATED = "October 2026"
co_line = f"Extera Limited{f' (company number {COMPANY_NO})' if COMPANY_NO else ''}, {ADDR}"
ico_line = f" Our ICO registration number is {ICO_NO}." if ICO_NO else ""


def legal_page(fname, title, desc, h1a, h1b, sections, intro):
    secs = "".join(f"<h2>{h}</h2>{t}" for h, t in sections)
    body = f"""<section><div class="wrap narrow legal"><p class="lead">{intro}</p><p class="vendor-note">Last updated {UPDATED}.</p>{secs}</div></section>"""
    page(fname, title, desc, body, hero(h1a, h1b, "How we handle your information and the use of this website.", ctas=False, small=True), h1a + " " + h1b)


legal_page("privacy.html", "Privacy Policy | Extera Limited",
    "How Extera Limited collects, uses and protects personal information from enquiries, customers and website visitors.", "Privacy", "policy", [
    ("Who we are", f"<p>{co_line}, is the controller of the personal information described here.{ico_line} You can contact us at <a href='mailto:{EMAIL}'>{EMAIL}</a> or on <a href='tel:{TEL}'>{PHONE}</a>.</p>"),
    ("What we collect", "<ul><li><b>Enquiry forms:</b> your name, company, email address, phone number, the service you are interested in and your message.</li><li><b>Calls and emails:</b> the details you give us and a record of our conversation.</li><li><b>Business details:</b> your job title and postcode where you give them, and any preferences you tell us about.</li><li><b>Customers:</b> the contact, billing and technical details we need to supply and support your services.</li><li><b>Website visits:</b> our hosting provider may keep standard server logs, such as your IP address and the pages you request.</li></ul>"),
    ("Why we use it, and our legal basis", "<ul><li>To reply to your enquiry and provide a quote, because you asked us to (steps before a contract).</li><li>To supply, install, support and bill for services, to perform our contract with you.</li><li>To keep records, handle complaints and meet legal and accounting duties (legal obligation).</li><li>To tell existing customers about similar services and to keep our website secure and working, in our legitimate interests. You can ask us to stop marketing at any time.</li></ul>"),
    ("Who we share it with", "<p>We do not sell or lease personal information. We share it only where needed to do our job: with the carriers, network operators and vendors that provision your services (for example 3CX, 8x8, Gamma, Avaya, EE, Vodafone and O2), with manufacturers where you buy equipment and need a warranty or product registration, with suppliers who help us run our business such as email, hosting, payment and accounting providers, and where the law requires. These suppliers act on our instructions or under their own privacy terms.</p>"),
    ("Extera Direct", "<p>Extera Direct is a trading name of Extera Limited. Orders placed on the <a href='https://www.exteradirect.co.uk'>Extera Direct shop</a> are covered by the privacy and cookie information on that site, which is run by the same company. We do not store your card details on this site.</p>"),
    ("Third-party content on this site", "<p>The typefaces on this site are served from our own website, so your browser does not contact Google or any other font provider. The site does not use advertising or analytics cookies. If that changes, we will update this policy and ask for consent where the law requires it. See our <a href='cookies.html'>cookie policy</a>.</p>"),
    ("How long we keep it", "<p>We keep enquiries that do not become business for a limited period, then delete them. Customer records are kept for as long as we supply services and afterwards for the period needed for legal, tax and accounting purposes. Ask us if you want details for a particular type of record.</p>"),
    ("Transfers outside the UK", "<p>Some of our suppliers may process information outside the UK. Where they do, we expect appropriate safeguards to be in place, such as the UK adequacy regulations or approved standard contract terms.</p>"),
    ("Your rights", "<p>Under UK data protection law (the UK GDPR and the Data Protection Act 2018) you can ask us, free of charge, for access to the information we hold about you, to correct it, to delete it, to restrict or object to our use of it, and to receive it in a portable format. Where we rely on consent you can withdraw it at any time. To use any of these rights, contact us using the details above.</p>"),
    ("Complaints", "<p>Please tell us first so we can put things right. You also have the right to complain to the Information Commissioner's Office at <a href='https://ico.org.uk/make-a-complaint/'>ico.org.uk</a> or on 0303 123 1113.</p>"),
    ("Changes to this policy", "<p>We may update this policy from time to time. The date at the top shows when it last changed.</p>"),
], "We take care with the personal information you share with Extera. This policy explains what we collect, why, and what your rights are.")

legal_page("cookies.html", "Cookie Policy | Extera Limited",
    "Extera's cookie policy: this website does not set advertising or analytics cookies.", "Cookie", "policy", [
    ("What cookies are", "<p>Cookies are small files a website stores on your device. They are used to remember settings, keep sites working and, in some cases, to track visitors or show advertising.</p>"),
    ("What this website uses", "<p>At the time of writing this website does not set advertising, analytics or social media tracking cookies, so we do not show a cookie consent banner. The site stores no account or login information.</p>"),
    ("Third-party services", "<p>Typefaces are served from this website, so no font provider is contacted. The social links in the footer take you to Facebook and LinkedIn, which have their own privacy and cookie policies once you visit them. Pages for products such as the Extera Direct shop are on a separate site with its own policy.</p>"),
    ("If this changes", "<p>If we add analytics or other non-essential cookies, we will ask for your consent first and update this page.</p>"),
    ("Managing cookies", "<p>You can block or delete cookies in your browser settings. Guidance is available at <a href='https://ico.org.uk/for-the-public/online/cookies/'>ico.org.uk</a>.</p>"),
    ("Questions", f"<p>Contact us at <a href='mailto:{EMAIL}'>{EMAIL}</a>.</p>"),
], "A short explanation of how this website uses, and does not use, cookies.")

legal_page("terms.html", "Website Terms of Use | Extera Limited",
    "Terms for using the Extera Limited website, including information accuracy, links and liability.", "Website", "terms", [
    ("About these terms", f"<p>This website is operated by {co_line}. By using it you agree to these terms. Our services for customers are supplied under separate written terms and quotations.</p>"),
    ("Information on this site", "<p>We try to keep the information accurate and up to date, but it is for general guidance only. Product features, prices, third-party review scores and vendor claims change, and are the vendors' own statements. Check current details with us or the vendor before you buy. Nothing here is a contractual offer. A quotation from us is.</p>"),
    ("Quotes and enquiries", "<p>Sending an enquiry does not create a contract. Quotes are free and carry no obligation. A contract is formed only when you accept a written quotation on our terms.</p>"),
    ("Intellectual property", "<p>The content and design of this site belong to Extera Limited or its licensors. Product names, logos and trademarks (including 3CX, 8x8, Gamma, Avaya, EE, Vodafone, O2, Jabra, ISO and CHAS) belong to their owners and are used to identify the products and services we supply. You may view and print pages for your own business use, but may not copy or republish the site without our permission.</p>"),
    ("Links to other sites", "<p>We link to other websites, including vendor sites and Extera Direct. We do not control them and are not responsible for their content or privacy practices.</p>"),
    ("Liability", "<p>Nothing in these terms limits liability that cannot be limited by law, including for death or personal injury caused by negligence or for fraud. Otherwise, and so far as the law allows, we are not liable for loss arising from your use of, or reliance on, this website. We do not guarantee that the site will always be available or free of errors.</p>"),
    ("Law", "<p>These terms are governed by the law of England and Wales, and the courts of England and Wales have jurisdiction, except where the law of your home country gives you other rights.</p>"),
    ("Contact", f"<p>Questions about these terms: <a href='mailto:{EMAIL}'>{EMAIL}</a>.</p>"),
], "Please read these terms before using the Extera website.")


# ---------- Design system page ----------
def sw(items):
    return "".join(f'<div class="sw"><i style="background:{h};{"border-bottom:1px solid #e2e8f0" if h.lower() in ("#ffffff","#f8fafc") else ""}"></i><span><b>{n}</b><br>{h}<br>{u}</span></div>' for n, h, u in items)


brand = [("--brand-50", "#eef6fc", "Tints, icon tiles"), ("--brand-100", "#d6e9f7", "Borders on blue"), ("--brand-200", "#aed3ef", "Card hover border"),
         ("--brand-300", "#7cc0f0", "Accent on dark"), ("--brand-500", "#1a75bb", "Primary, links"), ("--brand-600", "#155f99", "Button hover"),
         ("--brand-700", "#104a77", "Pressed, badge text"), ("--brand-900", "#0b2a45", "Footer, hero, top bar")]
neutral = [("--ink", "#0f172a", "Headings"), ("--text", "#334155", "Body"), ("--muted", "#475569", "Secondary"), ("--line", "#e2e8f0", "Borders"),
           ("--surface-alt", "#f8fafc", "Alt sections"), ("--surface", "#ffffff", "Page, cards")]
body = f"""
<section><div class="wrap">{heading("Colour", "Brand blue, cool neutrals", "Extera blue stays the only accent. Everything else is a slate neutral, which keeps the page calm and lets the blue do the work.")}
<h3>Brand scale</h3><div class="swatches">{sw(brand)}</div>
<h3 style="margin-top:32px">Neutrals</h3><div class="swatches">{sw(neutral)}</div></div></section>

<section class="alt"><div class="wrap">{heading("Typography", "Poppins for headings, Open Sans for reading")}
<div class="grid g2"><div class="card">
<p style="font:700 clamp(2.25rem,1.4rem + 3.6vw,3.75rem)/1.1 var(--font-head);color:var(--ink);margin:0">Hero, fluid</p>
<h2 style="margin-top:16px">Heading 2, fluid</h2><h3>Heading 3, 18px semibold</h3>
<p>Body text: Open Sans 16px on 1.7, colour slate 700 on white (about 10:1).</p><p class="lead">Lead paragraph, fluid 17 to 20px.</p></div>
<div class="card"><h3>Scale</h3><div class="spec">
<div><i style="width:120px"></i>Hero 36 to 60px, Poppins 600/700</div>
<div><i style="width:96px"></i>H2 28 to 40px, Poppins 600</div>
<div><i style="width:60px"></i>H3 18px, Poppins 600</div>
<div><i style="width:40px"></i>Body 16px, Open Sans 400</div>
<div><i style="width:32px"></i>Small 14px, Open Sans / Poppins 600</div></div></div></div></div></section>

<section><div class="wrap">{heading("Components", "Buttons, cards and badges")}
<div class="actions left"><a class="btn" href="#">Primary</a><a class="btn outline dark" href="#">Outline</a></div>
<div class="grid g3" style="margin-top:32px">
<div class="service">{ico('phone')}<h3>Service card</h3><p>Icon tile, 22px radius, soft shadow, lifts 3px on hover.</p><a class="more" href="#">Link style &rarr;</a></div>
<div class="card"><h3>Plain card</h3><p>White surface, 1px slate border, 22px radius.</p>{ticks(["Tick list item", "Another item"])}</div>
<div class="card"><h3>Badges</h3><ul class="badges" style="justify-content:flex-start;margin-top:0"><li>ISO 9001:2015</li><li>CHAS</li></ul></div></div>
<h3 style="margin-top:40px">Process steps</h3>{steps([("Survey", "Numbered, connected steps."), ("Design", "Used for how-it-works sections."), ("Install", "Stacks on small screens."), ("Support", "Four steps is ideal.")])}
<h3 style="margin-top:40px">Fact bar</h3></div>
{facts([("Since 2001", "Trusted UK telecoms specialist"), ("Own engineers", "Covering mainland UK"), ("ISO 9001:2015", "Certified"), ("CHAS", "Accredited Contractor")])}</section>

<section class="alt"><div class="wrap">{heading("Tokens", "Shape, space and motion")}
<div class="grid g3"><div class="card"><h3>Radius</h3><p>8px inputs, 14px tiles, 22px cards, pill buttons.</p></div>
<div class="card"><h3>Spacing</h3><p>4px base: 8, 16, 24, 40, 64, 96. Sections use a fluid 48 to 96px.</p></div>
<div class="card"><h3>Motion</h3><p>200ms ease-out on hover; scroll fade-up where supported; none under reduced motion.</p></div></div></div></section>
"""
page("styleguide.html", "Design System | Extera Limited", "Extera design system: colour, type, components and tokens.", body,
     hero("Design", "System", "Modern, fresh and responsive tokens and components used across this site.", ctas=False, small=True), "Design System")
(OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /styleguide.html\nDisallow: /thanks.html\nDisallow: /send.php\n\nSitemap: {DOMAIN}/sitemap.xml\n")
(OUT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f"<url><loc>{u}</loc></url>\n" for u in PAGES) + "</urlset>\n")
print("built")
