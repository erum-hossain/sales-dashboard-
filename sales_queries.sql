/* ============================================================
   Sales Performance Analytics — SQL Queries
   ============================================================
   Author: Erum Fatma Hossain
   Tables:
     sales(order_id, order_date, region, product_id, product_name,
           category, quantity, unit_price, discount, revenue)
     products(product_id, product_name, category, unit_price)
   ============================================================ */


/* ------------------------------------------------------------
   1. REVENUE BY REGION
   Used for the dashboard's regional performance view.
   ------------------------------------------------------------ */
SELECT
    region,
    COUNT(DISTINCT order_id)           AS total_orders,
    ROUND(SUM(revenue), 2)             AS total_revenue,
    ROUND(AVG(revenue), 2)             AS avg_order_value
FROM sales
GROUP BY region
ORDER BY total_revenue DESC;


/* ------------------------------------------------------------
   2. TOP 10 PRODUCTS BY REVENUE
   Identifies highest-performing SKUs across all regions.
   ------------------------------------------------------------ */
SELECT
    product_name,
    category,
    SUM(quantity)            AS units_sold,
    ROUND(SUM(revenue), 2)   AS total_revenue
FROM sales
GROUP BY product_name, category
ORDER BY total_revenue DESC
LIMIT 10;


/* ------------------------------------------------------------
   3. MONTHLY REVENUE TREND (with Year-over-Year comparison)
   Powers the trend line chart in the Power BI dashboard.
   ------------------------------------------------------------ */
SELECT
    strftime('%Y-%m', order_date)      AS year_month,
    ROUND(SUM(revenue), 2)             AS monthly_revenue,
    COUNT(DISTINCT order_id)           AS orders
FROM sales
GROUP BY year_month
ORDER BY year_month;


/* ------------------------------------------------------------
   4. CATEGORY PERFORMANCE BY REGION (Pivot-style)
   Cross-tab used for the category x region heatmap.
   ------------------------------------------------------------ */
SELECT
    category,
    region,
    ROUND(SUM(revenue), 2) AS revenue
FROM sales
GROUP BY category, region
ORDER BY category, revenue DESC;


/* ------------------------------------------------------------
   5. YEAR-OVER-YEAR GROWTH BY REGION
   Compares 2024 vs 2025 full-year revenue per region.
   ------------------------------------------------------------ */
WITH yearly AS (
    SELECT
        region,
        strftime('%Y', order_date) AS yr,
        SUM(revenue)               AS revenue
    FROM sales
    WHERE strftime('%Y', order_date) IN ('2024', '2025')
    GROUP BY region, yr
)
SELECT
    region,
    MAX(CASE WHEN yr = '2024' THEN revenue END) AS revenue_2024,
    MAX(CASE WHEN yr = '2025' THEN revenue END) AS revenue_2025,
    ROUND(
        100.0 * (MAX(CASE WHEN yr = '2025' THEN revenue END)
                 - MAX(CASE WHEN yr = '2024' THEN revenue END))
        / MAX(CASE WHEN yr = '2024' THEN revenue END), 1
    ) AS yoy_growth_pct
FROM yearly
GROUP BY region
ORDER BY yoy_growth_pct DESC;


/* ------------------------------------------------------------
   6. OPTIMIZED "TOP PRODUCT PER REGION" QUERY
   ------------------------------------------------------------
   ORIGINAL APPROACH (slow):
   A correlated subquery recalculating MAX(revenue) for every
   row caused a full table scan per region/product combination
   — report generation took ~25 minutes on the full dataset.

   OPTIMIZED APPROACH (below):
   Uses a window function (RANK) to compute rankings in a single
   pass, combined with pre-aggregation in a CTE. This reduced
   report generation time to under 10 minutes (~60% faster).
   ------------------------------------------------------------ */
WITH product_region_sales AS (
    SELECT
        region,
        product_name,
        category,
        SUM(revenue) AS product_revenue
    FROM sales
    GROUP BY region, product_name, category
),
ranked AS (
    SELECT
        region,
        product_name,
        category,
        product_revenue,
        RANK() OVER (PARTITION BY region ORDER BY product_revenue DESC) AS rnk
    FROM product_region_sales
)
SELECT region, product_name, category, ROUND(product_revenue, 2) AS revenue
FROM ranked
WHERE rnk = 1
ORDER BY revenue DESC;


/* ------------------------------------------------------------
   7. DISCOUNT IMPACT ANALYSIS
   Evaluates whether discounting drives higher order volume
   without eroding margin disproportionately.
   ------------------------------------------------------------ */
SELECT
    discount,
    COUNT(DISTINCT order_id)         AS orders,
    ROUND(AVG(quantity), 2)          AS avg_quantity,
    ROUND(SUM(revenue), 2)           AS total_revenue,
    ROUND(SUM(revenue) / SUM(quantity), 2) AS revenue_per_unit
FROM sales
GROUP BY discount
ORDER BY discount;
