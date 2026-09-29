"""
Web scraping script — Shopify public product feed
Target store: allbirds.com (public /products.json endpoint — no login,
no API key; this is Shopify's own public storefront feed, used by any
shopping app to list products).

Collects one row PER PRODUCT VARIANT (e.g. each size/color combination),
which is the natural grain of real e-commerce data and comfortably
clears the 1,000-record minimum from a single real brand.

Fields: product_title, vendor, product_type, tags, variant_title,
        price, compare_at_price, on_sale, discount_pct, available,
        sku, image_url, product_url
"""

import time
import requests
import pandas as pd

STORE = "https://www.allbirds.com"
HEADERS = {"User-Agent": "capstone-project-scraper/1.0 (educational use)"}


def fetch_page(page, limit=250):
    url = f"{STORE}/products.json"
    params = {"limit": limit, "page": page}
    resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.json().get("products", [])


def flatten_product(product):
    """Turn one product (with N variants) into N row-dicts, one per variant."""
    rows = []
    tags = ", ".join(product.get("tags", [])) if isinstance(product.get("tags"), list) else product.get("tags", "")
    image_url = product["images"][0]["src"] if product.get("images") else None
    product_url = f"{STORE}/products/{product.get('handle', '')}"

    for variant in product.get("variants", []):
        price = float(variant.get("price", 0) or 0)
        compare_at = variant.get("compare_at_price")
        compare_at = float(compare_at) if compare_at else None
        on_sale = bool(compare_at and compare_at > price)
        discount_pct = round((compare_at - price) / compare_at * 100, 1) if on_sale else 0.0

        rows.append({
            "product_title": product.get("title"),
            "vendor": product.get("vendor"),
            "product_type": product.get("product_type") or "Uncategorized",
            "tags": tags,
            "variant_title": variant.get("title"),
            "price": price,
            "compare_at_price": compare_at,
            "on_sale": on_sale,
            "discount_pct": discount_pct,
            "available": variant.get("available", False),
            "sku": variant.get("sku"),
            "image_url": image_url,
            "product_url": product_url,
        })
    return rows


def main():
    all_rows = []
    page = 1
    while True:
        try:
            products = fetch_page(page)
        except requests.RequestException as e:
            print(f"Request failed on page {page}: {e}")
            break

        if not products:
            print(f"No more products — stopped at page {page}.")
            break

        for product in products:
            all_rows.extend(flatten_product(product))

        print(f"Page {page}: {len(products)} products -> {len(all_rows)} total variant rows so far")
        page += 1
        time.sleep(0.5)  # be polite to the server

    df = pd.DataFrame(all_rows).drop_duplicates(subset=["sku", "product_url"]).reset_index(drop=True)
    df.to_csv("ecommerce_raw.csv", index=False)
    print(f"\nTotal rows scraped: {len(df)}")
    print(df.head())
    print("\nProduct types found:")
    print(df["product_type"].value_counts())


if __name__ == "__main__":
    main()
