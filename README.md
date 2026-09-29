# Multi-Source-E-Commerce-Capstone-Project
# Multi-Source E-Commerce Pricing & Ratings Analytics

A data science capstone project that scrapes, cleans, analyzes, models, and visualizes product data combined from three independent public e-commerce sources — exploring how price, category, and customer rating relate across a heterogeneous catalog spanning collectibles, electronics, groceries, and luxury goods.

## Business Problem

- Does a single "typical price" story hold across a mixed catalog, or does it depend on product domain?
- Which categories command the highest prices, and how consistent is pricing within each category?
- Can a product's rating be predicted from its price and category alone?
- Can products be usefully segmented across catalog sources rather than treated as separate silos?

## Data Sources

| Source | Records | Notes |
|---|---|---|
| [scrapeme.live/shop](https://scrapeme.live/shop/) | 755 | WooCommerce practice store (Pokémon merchandise) |
| [webscraper.io](https://webscraper.io/test-sites/e-commerce/allinone) | 147 | Static practice catalog — phones, laptops, tablets; includes star ratings |
| [dummyjson.com/products](https://dummyjson.com/products) | 194 | Public JSON API — varied real-world categories, includes numeric rating |
| **Total** | **1,096** | Combined, deduplicated, unified schema |

All three sources are public, require no login, and were chosen for reliability after an initial attempt to scrape a live commercial Shopify store (Allbirds) failed when the brand disabled its public product feed mid-project — a reminder that live commercial sites can change without warning.

## Project Structure

```
├── scrape_ecommerce_combined.py   # Step 1: scraping script (all 3 sources)
├── ecommerce_clean_eda_model.py   # Steps 2–4: cleaning, EDA, modeling
├── dashboard_ecommerce.py         # Step 5: Streamlit dashboard
├── ecommerce_raw.csv              # Raw scraped output
├── ecommerce_clean.csv            # Cleaned, feature-engineered dataset
├── Ecommerce_Final_Report.docx    # Step 6: final report
├── chart_*.png                    # Saved EDA/model charts
└── README.md
```

## Methodology

1. **Scraping** — combined pagination-based HTML scraping (BeautifulSoup) and a public JSON API into one unified schema: `name, price_usd, category, rating, review_count, image_url, product_url, source`.
2. **Cleaning** — deduplicated on product URL, collapsed rare categories (<10 items) into `Other`, engineered `name_length`, `price_band`, and a `price_log` (log10) transform to make price comparable across a catalog spanning $0.79–$36,999.99.
3. **EDA** — price distribution, price by source, price by category, and rating vs. price (scoped honestly to the 194 records with a genuine rating).
4. **Modeling** — a Random Forest classifier predicting high ratings (weak result, ROC AUC 0.57 — reported honestly rather than overstated) and a K-Means clustering model (k=4) segmenting the full catalog by price and name length.
5. **Dashboard** — an interactive Streamlit app with KPI cards, source/category/price filters, a "rated items only" toggle, and a category drill-down.

## Key Findings

- The combined catalog's price distribution is **multimodal**, not a single curve — it reflects three overlapping product domains (everyday items ~$150–250, electronics ~$1,000, luxury/vehicle outliers ~$10,000+). A single blended average price across the whole dataset is misleading.
- **Price does not meaningfully predict rating** (classifier ROC AUC 0.57, barely above random) — this independently replicates the same finding from a separate books-domain capstone project using an identical methodology.
- Clustering surfaced a genuine cross-source pattern: higher-priced segments consistently have **longer, more descriptive product names** than lower-priced segments.
- Only 1 of 3 combined sources (dummyjson.com) reliably provided customer ratings — a realistic data-quality issue when aggregating multiple supplier/marketplace feeds, handled here by explicit scoping rather than silently averaging over the gap.

## How to Run

```bash
pip install requests beautifulsoup4 pandas numpy matplotlib seaborn scikit-learn streamlit plotly

# 1. Scrape the data
python scrape_ecommerce_combined.py

# 2. Clean, run EDA, and train models (run cell-by-cell in Jupyter, or as a script)
python ecommerce_clean_eda_model.py

# 3. Launch the dashboard
streamlit run dashboard_ecommerce.py
```

## Limitations

- Rating coverage is limited to 194 of 1,096 records (dummyjson.com only); classifier results should be read with that small sample size in mind.
- Prices are combined across three unrelated product domains — cross-category or cross-source averages should always be interpreted on the log scale, not raw dollars.
- webscraper.io's product images and star ratings were not reliably extractable and are recorded as missing rather than estimated.

## Author

Laxmi Dongre — Data Science PGC Capstone Project
