"""
Sales Performance Analytics Dashboard
======================================
Loads the sales dataset into SQLite, runs the analysis queries,
and produces a multi-panel results dashboard image.

Author: Erum Fatma Hossain
Tools : Python, SQL (SQLite), pandas, matplotlib, seaborn
"""

import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# 1. LOAD DATA INTO SQLITE
# ─────────────────────────────────────────────
sales = pd.read_csv("sales_data.csv")
conn = sqlite3.connect(":memory:")
sales.to_sql("sales", conn, index=False, if_exists="replace")

print(f"Loaded {len(sales):,} transactions")
print(f"Date range: {sales['order_date'].min()} to {sales['order_date'].max()}")
print(f"Total revenue: ${sales['revenue'].sum():,.2f}")
print(f"Products: {sales['product_name'].nunique()} | Regions: {sales['region'].nunique()}")

# ─────────────────────────────────────────────
# 2. RUN KEY QUERIES
# ─────────────────────────────────────────────

# Revenue by region
q_region = """
SELECT region, COUNT(DISTINCT order_id) AS total_orders,
       ROUND(SUM(revenue), 2) AS total_revenue,
       ROUND(AVG(revenue), 2) AS avg_order_value
FROM sales GROUP BY region ORDER BY total_revenue DESC;
"""
df_region = pd.read_sql(q_region, conn)
print("\n── Revenue by Region ──")
print(df_region)

# Top products
q_top = """
SELECT product_name, category, SUM(quantity) AS units_sold,
       ROUND(SUM(revenue), 2) AS total_revenue
FROM sales GROUP BY product_name, category
ORDER BY total_revenue DESC LIMIT 10;
"""
df_top = pd.read_sql(q_top, conn)
print("\n── Top 10 Products ──")
print(df_top)

# Monthly trend
q_monthly = """
SELECT strftime('%Y-%m', order_date) AS year_month,
       ROUND(SUM(revenue), 2) AS monthly_revenue,
       COUNT(DISTINCT order_id) AS orders
FROM sales GROUP BY year_month ORDER BY year_month;
"""
df_monthly = pd.read_sql(q_monthly, conn)

# Category x Region
q_cat_region = """
SELECT category, region, ROUND(SUM(revenue), 2) AS revenue
FROM sales GROUP BY category, region ORDER BY category, revenue DESC;
"""
df_cat_region = pd.read_sql(q_cat_region, conn)

# Top category by revenue share -> revenue concentration
top_category_share = df_top.groupby("category")["total_revenue"].sum()
top_n_share = top_category_share.sum() / sales["revenue"].sum() * 100
print(f"\nTop 10 products represent {top_n_share:.1f}% of total revenue from top categories shown")

# Overall category revenue
q_cat_total = """
SELECT category, ROUND(SUM(revenue),2) AS revenue
FROM sales GROUP BY category ORDER BY revenue DESC;
"""
df_cat_total = pd.read_sql(q_cat_total, conn)
revenue_concentration = df_cat_total.iloc[0]["revenue"] / sales["revenue"].sum() * 100

# ─────────────────────────────────────────────
# 3. DASHBOARD VISUALIZATION
# ─────────────────────────────────────────────
sns.set_style("whitegrid")
NAVY, CORAL, TEAL, GOLD, GRAY = "#1B3A6B", "#E05C3A", "#2A9D8F", "#E9C46A", "#B0B0B0"
palette = [NAVY, TEAL, CORAL, GOLD, "#8E7CC3"]

fig = plt.figure(figsize=(16, 11))
fig.suptitle("Sales Performance Analytics Dashboard", fontsize=18,
              fontweight="bold", color=NAVY, y=1.01)
gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.5, wspace=0.35)

# A) Revenue by Region
ax0 = fig.add_subplot(gs[0, 0])
bars = ax0.bar(df_region["region"], df_region["total_revenue"], color=palette[:len(df_region)], edgecolor="white")
ax0.set_title("Revenue by Region", fontweight="bold", color=NAVY)
ax0.set_ylabel("Revenue ($)")
ax0.tick_params(axis="x", rotation=30)
for bar, val in zip(bars, df_region["total_revenue"]):
    ax0.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"${val/1000:.0f}K",
             ha="center", va="bottom", fontsize=8)

# B) Monthly Revenue Trend
ax1 = fig.add_subplot(gs[0, 1:])
ax1.plot(df_monthly["year_month"], df_monthly["monthly_revenue"], color=NAVY, marker="o", markersize=3, linewidth=2)
ax1.fill_between(range(len(df_monthly)), df_monthly["monthly_revenue"], alpha=0.08, color=NAVY)
ax1.set_title("Monthly Revenue Trend (2024 – 2026)", fontweight="bold", color=NAVY)
ax1.set_ylabel("Revenue ($)")
ax1.tick_params(axis="x", rotation=60, labelsize=7)
step = max(1, len(df_monthly)//12)
ax1.set_xticks(range(0, len(df_monthly), step))
ax1.set_xticklabels(df_monthly["year_month"][::step], rotation=60, fontsize=7)

# C) Top 10 Products
ax2 = fig.add_subplot(gs[1, 0])
top5 = df_top.head(8).sort_values("total_revenue")
ax2.barh(top5["product_name"], top5["total_revenue"], color=TEAL, edgecolor="white")
ax2.set_title("Top Products by Revenue", fontweight="bold", color=NAVY)
ax2.set_xlabel("Revenue ($)")
ax2.tick_params(axis="y", labelsize=8)

# D) Category Revenue Share (Pie)
ax3 = fig.add_subplot(gs[1, 1])
ax3.pie(df_cat_total["revenue"], labels=df_cat_total["category"], autopct="%1.0f%%",
        colors=palette, textprops={"fontsize": 8}, startangle=90,
        wedgeprops={"edgecolor": "white", "linewidth": 1})
ax3.set_title("Revenue Share by Category", fontweight="bold", color=NAVY)

# E) Category x Region Heatmap
ax4 = fig.add_subplot(gs[1, 2])
pivot = df_cat_region.pivot(index="category", columns="region", values="revenue")
sns.heatmap(pivot, annot=True, fmt=".0f", cmap="Blues", ax=ax4, cbar=False,
            linewidths=0.5, annot_kws={"fontsize": 7})
ax4.set_title("Revenue: Category x Region", fontweight="bold", color=NAVY)
ax4.set_ylabel(""); ax4.set_xlabel("")
ax4.tick_params(axis="x", labelsize=7, rotation=30)
ax4.tick_params(axis="y", labelsize=7)

plt.savefig("sales_dashboard_results.png", dpi=150, bbox_inches="tight")
plt.close()
print("\nSaved → sales_dashboard_results.png")

# ─────────────────────────────────────────────
# 4. SUMMARY STATS FOR README
# ─────────────────────────────────────────────
yoy = pd.read_sql("""
WITH yearly AS (
    SELECT region, strftime('%Y', order_date) AS yr, SUM(revenue) AS revenue
    FROM sales WHERE strftime('%Y', order_date) IN ('2024','2025')
    GROUP BY region, yr
)
SELECT region,
       MAX(CASE WHEN yr='2024' THEN revenue END) AS rev_2024,
       MAX(CASE WHEN yr='2025' THEN revenue END) AS rev_2025
FROM yearly GROUP BY region;
""", conn)
yoy["growth_pct"] = ((yoy["rev_2025"] - yoy["rev_2024"]) / yoy["rev_2024"] * 100).round(1)
print("\n── YoY Growth by Region ──")
print(yoy)

print(f"\nTop category ({df_cat_total.iloc[0]['category']}) drives {revenue_concentration:.1f}% of revenue")
print(f"Total revenue: ${sales['revenue'].sum():,.2f} | Total orders: {sales['order_id'].nunique():,}")
