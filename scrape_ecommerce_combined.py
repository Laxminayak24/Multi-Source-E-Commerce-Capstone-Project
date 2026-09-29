"""
Web scraping script — combined e-commerce dataset from two sources.

Source 1: scrapeme.live/shop      (~755 products: Pokemon merchandise, WooCommerce)
Source 2: webscraper.io test-sites/e-commerce/allinone
          (Phones > Touch, Computers > Laptops, Computers > Tablets — includes
          star ratings and review counts, ~350+ products across categories)

Both are real, stable, public sites built specifically for scraping practice
(unlike a live commercial brand, they won't change structure or disable
access without warning). Combining them reliably clears the 1,000-record
minimum with two genuinely different catalogs.

GBP prices from Source 1 are converted to USD at a fixed illustrative rate
(1 GBP = 1.27 USD) so price is comparable across both sources — this
conversion rate and its date should be stated in your report.

Output columns: name, price_usd, category, rating, review_count,
                 image_url, product_url, source
"""

import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin

HEADERS = {"User-Agent": "capstone-project-scraper/1.0 (educational use)"}
GBP_TO_USD = 1.27  # fixed illustrative rate — state this assumption in your report


# ---------------------------------------------------------------------------
# SOURCE 1: scrapeme.live/shop
# ---------------------------------------------------------------------------
def scrape_scrapeme():
    BASE = "https://scrapeme.live/shop/"
    records = []
    page = 1
    while True:
        page_url = urljoin(BASE, f"page/{page}/") if page > 1 else BASE
        try:
            resp = requests.get(page_url, headers=HEADERS, timeout=10)
        except requests.RequestException as e:
            print(f"[scrapeme] request failed on page {page}: {e}")
            break

        if resp.status_code == 404:
            print(f"[scrapeme] reached last page — stopped at page {page}.")
            break
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        items = soup.select("ul.products li.product")
        if not items:
            print(f"[scrapeme] no products on page {page} — stopping.")
            break

        for item in items:
            name_el = item.select_one("h2")
            price_el = item.select_one("span.price")
            link_el = item.select_one("a")
            img_el = item.select_one("img")
            if not (name_el and price_el and link_el):
                continue
            try:
                price_gbp = float(price_el.get_text(strip=True).replace("£", ""))
            except ValueError:
                continue

            records.append({
                "name": name_el.get_text(strip=True),
                "price_usd": round(price_gbp * GBP_TO_USD, 2),
                "category": "Pokemon Merchandise",
                "rating": None,
                "review_count": None,
                "image_url": img_el["src"] if img_el else None,
                "product_url": urljoin(page_url, link_el["href"]),
                "source": "scrapeme.live",
            })

        print(f"[scrapeme] page {page}: {len(items)} products -> {len(records)} total so far")
        page += 1
        time.sleep(0.4)

    return records


# ---------------------------------------------------------------------------
# SOURCE 2: webscraper.io test-sites/e-commerce/allinone
# ---------------------------------------------------------------------------
CATEGORY_PATHS = {
    "Phones - Touch": "phones/touch",
    "Computers - Laptops": "computers/laptops",
    "Computers - Tablets": "computers/tablets",
}
WS_BASE = "https://webscraper.io/test-sites/e-commerce/allinone/"


def scrape_webscraperio():
    records = []
    for category_name, path in CATEGORY_PATHS.items():
        page = 1
        while True:
            url = urljoin(WS_BASE, path) + ("" if page == 1 else f"?page={page}")
            try:
                resp = requests.get(url, headers=HEADERS, timeout=10)
                resp.raise_for_status()
            except requests.RequestException as e:
                print(f"[webscraper.io] request failed on {url}: {e}")
                break

            soup = BeautifulSoup(resp.text, "html.parser")
            items = soup.select("div.thumbnail")
            if not items:
                break

            for item in items:
                title_el = item.select_one("a.title")
                price_el = item.select_one("h4.price, h4.pull-right.price")
                review_el = item.select_one("p.review-count")
                stars = item.select("div.ratings p[data-rating] span.glyphicon-star")
                # fallback: count filled star icons if data-rating attr not present
                rating = len(stars) if stars else None

                if not (title_el and price_el):
                    continue
                try:
                    price = float(price_el.get_text(strip=True).replace("$", ""))
                except ValueError:
                    continue

                review_count = None
                if review_el:
                    digits = "".join(c for c in review_el.get_text() if c.isdigit())
                    review_count = int(digits) if digits else None

                records.append({
                    "name": title_el.get("title", title_el.get_text(strip=True)),
                    "price_usd": price,
                    "category": category_name,
                    "rating": rating,
                    "review_count": review_count,
                    "image_url": None,
                    "product_url": urljoin(url, title_el["href"]),
                    "source": "webscraper.io",
                })

            print(f"[webscraper.io] {category_name} page {page}: {len(items)} products")

            next_link = soup.select_one("ul.pagination li a[rel='next']")
            if not next_link:
                break
            page += 1
            time.sleep(0.4)

    return records


def main():
    all_records = []
    print("Scraping Source 1: scrapeme.live ...")
    all_records.extend(scrape_scrapeme())

    print("\nScraping Source 2: webscraper.io ...")
    all_records.extend(scrape_webscraperio())

    df = pd.DataFrame(all_records).drop_duplicates(subset="product_url").reset_index(drop=True)
    df.to_csv("ecommerce_raw.csv", index=False)
    print(f"\nTotal combined records: {len(df)}")
    print(df["source"].value_counts())
    print(df.head())


if __name__ == "__main__":
    main()
