"""
Step 5 — Interactive Dashboard (E-commerce project)
Run this from a terminal (NOT inside Jupyter) with:
    streamlit run dashboard_ecommerce.py
Needs ecommerce_clean.csv (produced by ecommerce_clean_eda_model.py) in the
same folder.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="E-Commerce Analytics", layout="wide")

df = pd.read_csv("ecommerce_clean.csv")

st.title("🛒 Multi-Source E-Commerce Analytics Dashboard")
st.caption(
    "Data sources: scrapeme.live, webscraper.io, dummyjson.com — "
    "1,096 products combined. Price shown on a log10 scale because the "
    "catalog spans $0.79 collectibles to $36,999.99 vehicles."
)

# ---- Sidebar filters ("slicer") ----
st.sidebar.header("Filters")
source_filter = st.sidebar.multiselect(
    "Source", sorted(df["source"].unique()), default=sorted(df["source"].unique())
)
category_filter = st.sidebar.multiselect(
    "Category", sorted(df["category"].unique()), default=sorted(df["category"].unique())
)
price_range = st.sidebar.slider(
    "Price range (log10 USD)",
    float(df["price_log"].min()), float(df["price_log"].max()),
    (float(df["price_log"].min()), float(df["price_log"].max())),
)
rated_only_toggle = st.sidebar.checkbox("Only show items with a real rating", value=False)

filtered = df[df["source"].isin(source_filter) & df["category"].isin(category_filter)]
filtered = filtered[filtered["price_log"].between(*price_range)]
if rated_only_toggle:
    filtered = filtered[filtered["rating"].notna()]

# ---- KPI cards ----
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Products", len(filtered))
col2.metric("Median Price", f"${filtered['price_usd'].median():,.2f}" if len(filtered) else "—")
rated_subset = filtered.dropna(subset=["rating"])
col3.metric(
    "Avg Rating (rated items only)",
    f"{rated_subset['rating'].mean():.2f} ★" if len(rated_subset) else "—",
)
col4.metric("Sources Included", filtered["source"].nunique())

st.divider()

# ---- Charts ----
left, right = st.columns(2)

with left:
    fig1 = px.histogram(filtered, x="price_log", nbins=30, title="Price Distribution (log10 USD)")
    st.plotly_chart(fig1, use_container_width=True)

with right:
    avg_by_cat = (
        filtered.groupby("category")["price_usd"]
        .median()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    fig2 = px.bar(avg_by_cat, x="category", y="price_usd", title="Top 10 Categories by Median Price ($)")
    st.plotly_chart(fig2, use_container_width=True)

if len(rated_subset) > 0:
    fig3 = px.scatter(
        rated_subset, x="price_log", y="rating", color="source",
        title="Rating vs Price (items with a real rating only)",
        hover_data=["name"],
    )
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("No rated items in the current filter selection.")

if "segment_label" in filtered.columns:
    fig4 = px.scatter(
        filtered.dropna(subset=["segment_label"]), x="price_log", y="name_length",
        color="segment_label", title="Catalog Segments: Price vs Name Length",
        hover_data=["name"],
    )
    st.plotly_chart(fig4, use_container_width=True)

# ---- Drill-through ----
st.divider()
st.subheader("Drill into a category")
if len(filtered) > 0:
    selected_cat = st.selectbox("Choose a category", sorted(filtered["category"].unique()))
    drill = filtered[filtered["category"] == selected_cat][
        ["name", "price_usd", "rating", "source", "product_url"]
    ]
    st.dataframe(drill, use_container_width=True)
else:
    st.info("No products match the current filters.")
