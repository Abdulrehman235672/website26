#!/usr/bin/env python3
"""
HIGHPEAKSPORTS — SEO + PRODUCT PAGE MANAGER
===========================================

Run from the root of your website:

    python seo_manager.py

What it does:
1. Creates product detail pages using your existing HighPeakSports design.
2. Updates the homepage product cards to point to those pages.
3. Creates /products/index.html.
4. Adds/repairs SEO tags on index.html, about.html and contact.html.
5. Generates sitemap.xml and robots.txt.
6. Generates seo-report.html.
7. Creates a backup before modifying existing HTML files.
8. Lets you add future products by editing PRODUCTS below.

IMPORTANT:
- This script does NOT delete your CSS, JS, images or existing pages.
- Product detail pages use your existing style.css.
- Review the generated files before deploying to production.
"""

from pathlib import Path
from datetime import datetime, date
import html
import re
import shutil
import json

# ============================================================
# SETTINGS
# ============================================================

SITE_URL = "https://highpeaksports.us".rstrip("/")
SITE_NAME = "HighPeakSports"

ROOT = Path(__file__).resolve().parent
PRODUCTS_DIR = ROOT / "products"
ASSETS_DIR = ROOT / "assets"
BACKUP_DIR = ROOT / f"_seo_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# ============================================================
# PRODUCTS
# Add/edit products here.
# slug becomes: /products/SLUG/
# ============================================================

PRODUCTS = [
    {
        "slug": "custom-pvc-patches",
        "name": "Custom PVC Patches",
        "short_name": "PVC Patches",
        "category": "CUSTOM PATCHES",
        "keyword": "custom PVC patches",
        "title": "Custom PVC Patches | Hook & Loop PVC Patch Manufacturer",
        "description": (
            "Custom PVC patches with hook-and-loop backing, made to your design "
            "for brands, teams, businesses and organizations worldwide."
        ),
        "intro": (
            "Custom PVC patches manufactured to your design with durable "
            "hook-and-loop backing."
        ),
        "image": "patch.jpeg",
        "alt": "Custom PVC patches manufactured by HighPeakSports",
        "moq": "25–30 pieces",
        "features": [
            "Custom shapes and designs",
            "2D and 3D PVC options",
            "Hook-and-loop backing",
            "Custom colors",
            "Bulk manufacturing",
            "Worldwide delivery"
        ],
        "applications": [
            "Brand and logo patches",
            "Tactical and security patches",
            "Morale patches",
            "Team and organization patches"
        ]
    },
    {
        "slug": "goalkeeper-gloves",
        "name": "Goalkeeper Gloves",
        "short_name": "Goalkeeper Gloves",
        "category": "GOALKEEPER",
        "keyword": "custom goalkeeper gloves",
        "title": "Custom Goalkeeper Gloves Manufacturer | HighPeakSports",
        "description": (
            "Custom goalkeeper gloves manufactured for brands, teams and "
            "private-label businesses worldwide."
        ),
        "intro": (
            "Custom goalkeeper gloves manufactured for brands, teams and "
            "private-label businesses."
        ),
        "image": "goalkeeper.jpeg",
        "alt": "Custom goalkeeper gloves by HighPeakSports",
        "moq": "Contact us for MOQ",
        "features": [
            "Custom glove designs",
            "Multiple glove cuts",
            "Custom branding",
            "Custom strap designs",
            "Private-label production"
        ],
        "applications": [
            "Goalkeeper brands",
            "Football academies and teams",
            "Private-label sports brands",
            "Custom team equipment"
        ]
    },
    {
        "slug": "sportswear",
        "name": "Custom Sportswear",
        "short_name": "Sportswear",
        "category": "TEAMWEAR",
        "keyword": "custom sportswear manufacturer",
        "title": "Custom Sportswear Manufacturer | HighPeakSports",
        "description": (
            "Custom sportswear manufactured for teams, brands and businesses "
            "with private-label customization options."
        ),
        "intro": (
            "Custom sportswear manufactured for teams and private-label businesses."
        ),
        "image": "sportswear.jpeg",
        "alt": "Custom sportswear manufactured by HighPeakSports",
        "moq": "Contact us for MOQ",
        "features": [
            "Custom designs",
            "Teamwear",
            "Private labeling",
            "Performance fabrics",
            "Custom branding"
        ],
        "applications": [
            "Football and sports teams",
            "Sports brands",
            "Training apparel",
            "Private-label collections"
        ]
    }
]

# ============================================================
# GENERAL HELPERS
# ============================================================

def esc(value):
    return html.escape(str(value), quote=True)


def slug_url(slug):
    return f"{SITE_URL}/products/{slug}/"


def relative_product_asset(filename):
    return f"../../assets/{filename}"


def backup_file(path):
    if not path.exists():
        return
    target = BACKUP_DIR / path.relative_to(ROOT)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target)


def write_text(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ============================================================
# SEO TAG REPAIR
# ============================================================

def replace_or_add_tag(head, pattern, replacement, fallback_marker=None):
    new_head, count = re.subn(pattern, replacement, head, count=1, flags=re.I | re.S)
    if count:
        return new_head

    marker = fallback_marker or "</head>"
    if marker in new_head:
        return new_head.replace(marker, replacement + "\n" + marker, 1)

    return new_head


def optimize_existing_page(filename, title, description, canonical, og_image):
    path = ROOT / filename
    if not path.exists():
        print(f"[SKIP] {filename} not found")
        return

    backup_file(path)
    content = path.read_text(encoding="utf-8", errors="ignore")

    # Remove duplicate/old title tags, then insert one.
    content = re.sub(r"<title\b[^>]*>.*?</title>\s*", "", content,
                     flags=re.I | re.S)

    # Remove all standard description tags.
    content = re.sub(
        r'<meta\b[^>]*name=["\']description["\'][^>]*>\s*',
        "",
        content,
        flags=re.I | re.S
    )

    # Remove canonical tags.
    content = re.sub(
        r'<link\b[^>]*rel=["\']canonical["\'][^>]*>\s*',
        "",
        content,
        flags=re.I | re.S
    )

    # Remove common duplicate OG URL/title/description tags.
    for prop in ("og:title", "og:description", "og:url", "og:image"):
        content = re.sub(
            rf'<meta\b[^>]*property=["\']{re.escape(prop)}["\'][^>]*>\s*',
            "",
            content,
            flags=re.I | re.S
        )

    # Insert canonical/description/title after charset or viewport.
    seo_block = f"""
    <title>{esc(title)}</title>
    <meta name="description" content="{esc(description)}">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="{esc(canonical)}">

    <meta property="og:type" content="website">
    <meta property="og:title" content="{esc(title)}">
    <meta property="og:description" content="{esc(description)}">
    <meta property="og:url" content="{esc(canonical)}">
    <meta property="og:site_name" content="{esc(SITE_NAME)}">
    <meta property="og:image" content="{esc(og_image)}">

    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{esc(title)}">
    <meta name="twitter:description" content="{esc(description)}">
    <meta name="twitter:image" content="{esc(og_image)}">
"""

    head_match = re.search(r"<head\b[^>]*>(.*?)</head>", content,
                           flags=re.I | re.S)
    if not head_match:
        print(f"[WARN] No <head> found in {filename}")
        return

    head = head_match.group(1)

    # Put our canonical SEO block near the beginning of <head>.
    new_head = seo_block + "\n" + head.strip()

    content = (
        content[:head_match.start(1)]
        + "\n"
        + new_head
        + "\n"
        + content[head_match.end(1):]
    )

    path.write_text(content, encoding="utf-8")
    print(f"[OK] Optimized SEO tags: {filename}")


# ============================================================
# PRODUCT PAGE TEMPLATE
# ============================================================

PRODUCT_CSS = r"""
/* HighPeakSports generated product page */
.product-page {
    max-width: 1500px;
    margin: 0 auto;
    padding: 120px 6vw 80px;
}

.product-hero {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 70px;
    align-items: center;
    min-height: 65vh;
}

.product-hero-image {
    position: relative;
    overflow: hidden;
    background: #111311;
    border: 1px solid rgba(255,255,255,.12);
}

.product-hero-image img {
    width: 100%;
    aspect-ratio: 1 / 1;
    object-fit: cover;
}

.product-eyebrow {
    color: var(--green);
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 22px;
}

.product-page h1 {
    font-family: "Space Grotesk", sans-serif;
    font-size: clamp(48px, 7vw, 92px);
    line-height: .9;
    letter-spacing: -.06em;
    margin-bottom: 28px;
}

.product-lead {
    color: #b2b6af;
    max-width: 600px;
    line-height: 1.7;
    font-size: 16px;
}

.product-cta {
    display: inline-flex;
    margin-top: 30px;
    padding: 15px 20px;
    background: var(--green);
    color: #000;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

.product-section {
    padding: 90px 0 0;
}

.product-section h2 {
    font-family: "Space Grotesk", sans-serif;
    font-size: clamp(34px, 5vw, 64px);
    letter-spacing: -.05em;
    line-height: .95;
    margin-bottom: 28px;
}

.product-grid-two {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}

.product-info-card {
    background: #111311;
    border: 1px solid rgba(255,255,255,.10);
    padding: 30px;
}

.product-info-card h3 {
    font-family: "Space Grotesk", sans-serif;
    font-size: 22px;
    margin-bottom: 14px;
}

.product-info-card p,
.product-info-card li {
    color: #aeb2ac;
    line-height: 1.7;
}

.product-info-card ul {
    padding-left: 20px;
}

.product-moq {
    font-size: 28px;
    font-weight: 700;
    color: var(--green);
}

.related-products {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
}

.related-product {
    display: block;
    padding: 26px;
    background: #111311;
    border: 1px solid rgba(255,255,255,.10);
    transition: transform .2s, border-color .2s;
}

.related-product:hover {
    transform: translateY(-4px);
    border-color: var(--green);
}

.related-product h3 {
    font-family: "Space Grotesk", sans-serif;
    margin-bottom: 10px;
}

.related-product p {
    color: #999e97;
    font-size: 14px;
    line-height: 1.6;
}

@media (max-width: 800px) {
    .product-page {
        padding: 90px 5vw 60px;
    }

    .product-hero,
    .product-grid-two {
        grid-template-columns: 1fr;
        gap: 35px;
    }

    .related-products {
        grid-template-columns: 1fr;
    }

    .product-page h1 {
        font-size: clamp(45px, 14vw, 70px);
    }
}
"""


def product_page_html(product, products):
    slug = product["slug"]
    canonical = slug_url(slug)
    image = relative_product_asset(product["image"])

    features = "\n".join(
        f"<li>{esc(item)}</li>" for item in product["features"]
    )

    applications = "\n".join(
        f"<li>{esc(item)}</li>" for item in product["applications"]
    )

    related = []

    for other in products:
        if other["slug"] == slug:
            continue

        related.append(f"""
        <a class="related-product" href="/products/{esc(other['slug'])}/">
            <h3>{esc(other['name'])}</h3>
            <p>{esc(other['intro'])}</p>
        </a>
        """)

    related_html = "\n".join(related)

    # Product schema is used because this is a real product/category page.
    schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product["name"],
        "description": product["description"],
        "image": [f"{SITE_URL}/assets/{product['image']}"],
        "brand": {
            "@type": "Brand",
            "name": SITE_NAME
        },
        "manufacturer": {
            "@type": "Organization",
            "name": SITE_NAME,
            "url": SITE_URL
        },
        "url": canonical
    }

    schema_json = json.dumps(schema, indent=4)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>{esc(product['title'])}</title>
    <meta name="description" content="{esc(product['description'])}">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="{esc(canonical)}">

    <meta property="og:type" content="website">
    <meta property="og:title" content="{esc(product['title'])}">
    <meta property="og:description" content="{esc(product['description'])}">
    <meta property="og:url" content="{esc(canonical)}">
    <meta property="og:site_name" content="{esc(SITE_NAME)}">
    <meta property="og:image" content="{esc(SITE_URL + '/assets/' + product['image'])}">

    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{esc(product['title'])}">
    <meta name="twitter:description" content="{esc(product['description'])}">
    <meta name="twitter:image" content="{esc(SITE_URL + '/assets/' + product['image'])}">

    <link rel="icon" type="image/png" sizes="32x32" href="../../assets/favicon-32x32.png">
    <link rel="stylesheet" href="../../style.css">

    <style>{PRODUCT_CSS}</style>

    <script type="application/ld+json">
{schema_json}
    </script>
</head>

<body id="product-page">

<header class="header">
    <nav class="nav">
        <a href="/" class="logo" aria-label="HighPeakSports home">
            <img src="../../assets/logo.png"
                 alt="HighPeakSports"
                 width="175"
                 height="auto">
        </a>

        <div class="nav-links">
            <a href="/#products">Products</a>
            <a href="/#process">Process</a>
            <a href="/about.html">About</a>
        </div>

        <a href="/contact.html" class="nav-button">
            Get a Quote <span>&#8599;</span>
        </a>

        <button class="menu-button"
                aria-label="Open menu"
                type="button"
                onclick="document.getElementById('mobileMenu').classList.add('active')">
            &#9776;
        </button>
    </nav>
</header>

<div class="mobile-menu" id="mobileMenu">
    <button class="close-menu"
            type="button"
            aria-label="Close menu"
            onclick="document.getElementById('mobileMenu').classList.remove('active')">
        &times;
    </button>
    <a href="/#products">Products</a>
    <a href="/#process">Process</a>
    <a href="/about.html">About</a>
    <a href="/contact.html">Contact</a>
</div>

<main class="product-page">

    <nav aria-label="Breadcrumb"
         style="margin-bottom:30px;color:#969a93;font-size:12px;">
        <a href="/">Home</a>
        <span aria-hidden="true"> / </span>
        <a href="/products/">Products</a>
        <span aria-hidden="true"> / </span>
        <span>{esc(product['name'])}</span>
    </nav>

    <section class="product-hero">

        <div>
            <div class="product-eyebrow">
                {esc(product['category'])}
            </div>

            <h1>{esc(product['name'])}</h1>

            <p class="product-lead">
                {esc(product['intro'])}
            </p>

            <a class="product-cta" href="/contact.html">
                Request a Quote &#8599;
            </a>
        </div>

        <div class="product-hero-image">
            <img src="{esc(image)}"
                 alt="{esc(product['alt'])}"
                 width="800"
                 height="800"
                 loading="eager">
        </div>

    </section>

    <section class="product-section">

        <h2>Built <span style="color:var(--green)">Your Way.</span></h2>

        <div class="product-grid-two">

            <article class="product-info-card">
                <h3>Features</h3>
                <ul>
                    {features}
                </ul>
            </article>

            <article class="product-info-card">
                <h3>Typical MOQ</h3>
                <p class="product-moq">{esc(product['moq'])}</p>
                <p>
                    Final quantities and production requirements depend on
                    the product, design and specifications.
                </p>
            </article>

            <article class="product-info-card">
                <h3>Applications</h3>
                <ul>
                    {applications}
                </ul>
            </article>

            <article class="product-info-card">
                <h3>Worldwide Supply</h3>
                <p>
                    HighPeakSports works with brands, teams and businesses
                    seeking custom manufacturing and private-label production.
                </p>
            </article>

        </div>

    </section>

    <section class="product-section">

        <h2>Need a <span style="color:var(--green)">Custom Quote?</span></h2>

        <p class="product-lead">
            Send your design, quantity and requirements to HighPeakSports.
            We can discuss the appropriate production specifications for your order.
        </p>

        <a class="product-cta" href="/contact.html">
            Contact HighPeakSports &#8599;
        </a>

    </section>

    <section class="product-section">

        <h2>Explore <span style="color:var(--green)">More Products.</span></h2>

        <div class="related-products">
            {related_html}
        </div>

    </section>

</main>

<footer style="padding:50px 6vw;border-top:1px solid rgba(255,255,255,.1);color:#969a93;">
    <p>&copy; {date.today().year} {SITE_NAME}</p>
</footer>

<script src="../../script.js"></script>

</body>
</html>
"""


# ============================================================
# CREATE PRODUCT PAGES
# ============================================================

def create_product_pages():
    PRODUCTS_DIR.mkdir(exist_ok=True)

    for product in PRODUCTS:
        folder = PRODUCTS_DIR / product["slug"]
        folder.mkdir(parents=True, exist_ok=True)

        target = folder / "index.html"

        # Never overwrite an existing custom product page silently.
        if target.exists():
            backup_file(target)

        write_text(target, product_page_html(product, PRODUCTS))
        print(f"[OK] Product page: /products/{product['slug']}/")


# ============================================================
# PRODUCTS INDEX
# ============================================================

def create_products_index():
    target = PRODUCTS_DIR / "index.html"

    if target.exists():
        backup_file(target)

    cards = []

    for i, product in enumerate(PRODUCTS, 1):
        cards.append(f"""
        <article class="product-card">
            <div class="product-image">
                <img src="../assets/{esc(product['image'])}"
                     alt="{esc(product['alt'])}"
                     loading="lazy"
                     width="600"
                     height="600">
            </div>

            <div class="product-bottom">
                <div>
                    <span class="product-category">
                        {esc(product['category'])}
                    </span>
                    <h2>{esc(product['name'])}</h2>
                </div>

                <a href="/products/{esc(product['slug'])}/"
                   class="round-arrow"
                   aria-label="View {esc(product['name'])}">
                    &#8599;
                </a>
            </div>
        </article>
        """)

    html_doc = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>Products | HighPeakSports</title>
    <meta name="description"
          content="Explore custom products manufactured by HighPeakSports for brands, teams and businesses worldwide.">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="{SITE_URL}/products/">

    <meta property="og:type" content="website">
    <meta property="og:title" content="Products | HighPeakSports">
    <meta property="og:description"
          content="Explore custom products manufactured by HighPeakSports.">
    <meta property="og:url" content="{SITE_URL}/products/">
    <meta property="og:site_name" content="{SITE_NAME}">

    <link rel="icon" type="image/png" sizes="32x32"
          href="../assets/favicon-32x32.png">
    <link rel="stylesheet" href="../style.css">

    <style>{PRODUCT_CSS}</style>
</head>

<body>

<header class="header">
    <nav class="nav">
        <a href="/" class="logo">
            <img src="../assets/logo.png"
                 alt="HighPeakSports"
                 width="175"
                 height="auto">
        </a>

        <div class="nav-links">
            <a href="/#products">Products</a>
            <a href="/#process">Process</a>
            <a href="/about.html">About</a>
        </div>

        <a href="/contact.html" class="nav-button">
            Get a Quote <span>&#8599;</span>
        </a>
    </nav>
</header>

<main class="product-page">

    <div class="product-eyebrow">HIGHPEAKSPORTS</div>

    <h1>Our <span style="color:var(--green)">Products.</span></h1>

    <p class="product-lead">
        Explore the products and custom manufacturing categories
        available from HighPeakSports.
    </p>

    <section class="product-section">
        <div class="related-products">
            {"".join(cards)}
        </div>
    </section>

</main>

</body>
</html>
"""

    write_text(target, html_doc)
    print("[OK] Products index: /products/")


# ============================================================
# HOMEPAGE PRODUCT CARD LINKING
# ============================================================

def update_homepage_links():
    path = ROOT / "index.html"

    if not path.exists():
        print("[WARN] index.html not found")
        return

    backup_file(path)
    content = path.read_text(encoding="utf-8", errors="ignore")

    replacements = {
        "pvc-patches": "custom-pvc-patches",
        "goalkeeper-gloves": "goalkeeper-gloves",
        "sportswear": "sportswear"
    }

    for card_id, slug in replacements.items():

        # Restrict replacement to the article with that ID.
        pattern = (
            rf'(<article\b[^>]*\bid=["\']{re.escape(card_id)}["\'][^>]*>.*?)'
            rf'(<a\b[^>]*href=["\'])contact\.html(["\'])'
        )

        def repl(match):
            return (
                match.group(1)
                + match.group(2)
                + f"products/{slug}/"
                + match.group(3)
            )

        content, count = re.subn(
            pattern, repl, content,
            count=1,
            flags=re.I | re.S
        )

        if count:
            print(f"[OK] Homepage link: {card_id} -> /products/{slug}/")
        else:
            print(f"[WARN] Could not update homepage card: {card_id}")

    path.write_text(content, encoding="utf-8")


# ============================================================
# SITEMAP
# ============================================================

def generate_sitemap():
    urls = [
        f"{SITE_URL}/",
        f"{SITE_URL}/products/",
        f"{SITE_URL}/about.html",
        f"{SITE_URL}/contact.html",
        f"{SITE_URL}/privacy.html",
        f"{SITE_URL}/terms.html",
        f"{SITE_URL}/shipping.html",
        f"{SITE_URL}/refunds.html",
        f"{SITE_URL}/editorial-policy.html"
    ]

    urls += [slug_url(p["slug"]) for p in PRODUCTS]

    today = date.today().isoformat()

    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    for url in dict.fromkeys(urls):
        xml.append("  <url>")
        xml.append(f"    <loc>{esc(url)}</loc>")
        xml.append(f"    <lastmod>{today}</lastmod>")
        xml.append("  </url>")

    xml.append("</urlset>")

    write_text(ROOT / "sitemap.xml", "\n".join(xml) + "\n")
    print("[OK] sitemap.xml generated")


# ============================================================
# ROBOTS
# ============================================================

def generate_robots():
    robots = f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
"""
    write_text(ROOT / "robots.txt", robots)
    print("[OK] robots.txt generated")


# ============================================================
# SEO AUDIT
# ============================================================

def audit():
    html_files = sorted(ROOT.rglob("*.html"))

    rows = []
    for path in html_files:

        if "_seo_backup_" in str(path):
            continue

        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        title_match = re.search(
            r"<title\b[^>]*>(.*?)</title>",
            text,
            flags=re.I | re.S
        )

        desc_match = re.search(
            r'<meta\b[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']',
            text,
            flags=re.I | re.S
        )

        canonical = bool(re.search(
            r'<link\b[^>]*rel=["\']canonical["\']',
            text,
            flags=re.I
        ))
        h1_count = len(re.findall(r"<h1\b", text, flags=re.I))
        img_count = len(re.findall(r"<img\b", text, flags=re.I))
        alt_count = len(re.findall(r"<img\b[^>]*\balt=[\"'][^\"']*[\"']", text, flags=re.I))



        issues = []

        if not title_match:
            issues.append("Missing title")
        elif not title_match.group(1).strip():
            issues.append("Empty title")
        elif len(title_match.group(1).strip()) > 65:
            issues.append("Title may be too long")

        if not desc_match:
            issues.append("Missing meta description")
        elif len(desc_match.group(1).strip()) < 70:
            issues.append("Meta description may be short")
        elif len(desc_match.group(1).strip()) > 165:
            issues.append("Meta description may be long")

        if not canonical:
            issues.append("Missing canonical")

        if h1_count == 0:
            issues.append("Missing H1")
        elif h1_count > 1:
            issues.append(f"{h1_count} H1 tags")

        if alt_count < img_count:
            issues.append(f"{img_count - alt_count} image(s) without alt")

        rel = str(path.relative_to(ROOT))

        rows.append({
            "page": rel,
            "title": title_match.group(1).strip() if title_match else "",
            "description": desc_match.group(1).strip() if desc_match else "",
            "h1": h1_count,
            "canonical": "YES" if canonical else "NO",
            "images": f"{alt_count}/{img_count}",
            "issues": issues
        })

    # Duplicate title/description checks
    title_map = {}
    desc_map = {}

    for row in rows:
        if row["title"]:
            title_map.setdefault(row["title"], []).append(row["page"])
        if row["description"]:
            desc_map.setdefault(row["description"], []).append(row["page"])

    for row in rows:
        if len(title_map.get(row["title"], [])) > 1:
            row["issues"].append("Duplicate title")

        if len(desc_map.get(row["description"], [])) > 1:
            row["issues"].append("Duplicate description")

    total_issues = sum(len(r["issues"]) for r in rows)

    cards = []

    for row in rows:
        status = "PASS" if not row["issues"] else "CHECK"
        issue_text = "<br>".join(esc(x) for x in row["issues"]) or "None"

        cards.append(f"""
        <tr>
            <td>{esc(row['page'])}</td>
            <td>{esc(row['title'])}</td>
            <td>{row['h1']}</td>
            <td>{row['canonical']}</td>
            <td>{esc(row['images'])}</td>
            <td>{status}</td>
            <td>{issue_text}</td>
        </tr>
        """)

    report = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>HighPeakSports SEO Report</title>
<style>
body {{
    font-family: Arial, sans-serif;
    margin: 30px;
    background: #0b0b0b;
    color: #eee;
}}
table {{
    width: 100%;
    border-collapse: collapse;
    margin-top: 25px;
}}
th, td {{
    border: 1px solid #333;
    padding: 10px;
    text-align: left;
    vertical-align: top;
}}
th {{ background: #171717; }}
td {{ background: #101010; }}
.good {{ color: #baff00; }}
</style>
</head>
<body>
<h1>HighPeakSports SEO Report</h1>
<p>Generated: {datetime.now().isoformat(timespec='seconds')}</p>
<p><strong>Total pages checked:</strong> {len(rows)}</p>
<p><strong>Total checks requiring attention:</strong> {total_issues}</p>

<table>
<thead>
<tr>
<th>Page</th>
<th>Title</th>
<th>H1</th>
<th>Canonical</th>
<th>Images ALT</th>
<th>Status</th>
<th>Issues</th>
</tr>
</thead>
<tbody>
{''.join(cards)}
</tbody>
</table>

</body>
</html>
"""

    write_text(ROOT / "seo-report.html", report)
    print(f"[OK] seo-report.html generated — {total_issues} issue(s)")


# ============================================================
# MAIN
# ============================================================

def main():

    print()
    print("=" * 64)
    print(" HIGHPEAKSPORTS SEO + PRODUCT PAGE MANAGER")
    print("=" * 64)
    print()

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[OK] Backup directory: {BACKUP_DIR.name}")

    # Existing pages
    optimize_existing_page(
        "index.html",
        "Custom Manufacturing & Private Label | HighPeakSports",
        (
            "HighPeakSports manufactures custom PVC patches, goalkeeper gloves "
            "and sportswear for brands, teams and businesses worldwide."
        ),
        f"{SITE_URL}/",
        f"{SITE_URL}/assets/social-cover.jpg"
    )

    optimize_existing_page(
        "about.html",
        "About HighPeakSports | Custom Manufacturer & Supplier",
        (
            "Learn about HighPeakSports, a Sialkot-based custom manufacturer "
            "and private-label supplier serving brands, teams and businesses."
        ),
        f"{SITE_URL}/about.html",
        f"{SITE_URL}/assets/social-cover.jpg"
    )

    optimize_existing_page(
        "contact.html",
        "Contact HighPeakSports | Request a Manufacturing Quote",
        (
            "Contact HighPeakSports for custom PVC patches, goalkeeper gloves, "
            "sportswear and private-label manufacturing inquiries."
        ),
        f"{SITE_URL}/contact.html",
        f"{SITE_URL}/assets/social-cover.jpg"
    )

    print()
    create_product_pages()
    create_products_index()

    print()
    update_homepage_links()

    print()
    generate_sitemap()
    generate_robots()

    print()
    audit()

    print()
    print("=" * 64)
    print(" DONE")
    print("=" * 64)
    print()
    print("Generated:")
    print("  /products/")
    for p in PRODUCTS:
        print(f"  /products/{p['slug']}/")
    print("  /sitemap.xml")
    print("  /robots.txt")
    print("  /seo-report.html")
    print()
    print(f"Backup: {BACKUP_DIR.name}/")
    print()
    print("NEXT:")
    print("1. Open the generated pages locally.")
    print("2. Check the design and links.")
    print("3. Open seo-report.html.")
    print("4. Deploy only after reviewing the changes.")
    print()


if __name__ == "__main__":
    main()
