"""
Sales Performance Analytics Dashboard — Data Generator
=======================================================
Generates a synthetic sales transactions dataset:
  - 100+ products
  - 5 regions
  - 2+ years of daily transaction data

Author: Erum Fatma Hossain
"""

import pandas as pd
import numpy as np

np.random.seed(42)

# ─────────────────────────────────────────────
# 1. PRODUCT CATALOG (120 products across 6 categories)
# ─────────────────────────────────────────────
categories = {
    "Electronics":     18,
    "Home & Kitchen":  22,
    "Apparel":         25,
    "Sports & Outdoors": 18,
    "Beauty & Personal Care": 17,
    "Office Supplies": 20,
}

# Realistic product name components per category
name_pools = {
    "Electronics": [
        "Wireless Earbuds", "Bluetooth Speaker", "Smart Watch", "USB-C Hub",
        "Noise-Cancelling Headphones", "Portable Charger", "Webcam HD",
        "Wireless Mouse", "Mechanical Keyboard", "Tablet Stand",
        "Smart Plug", "LED Desk Lamp", "Phone Charging Dock", "HDMI Cable",
        "Wireless Router", "Action Camera", "Power Strip", "Laptop Sleeve",
    ],
    "Home & Kitchen": [
        "Stainless Steel Knife Set", "Non-Stick Frying Pan", "Electric Kettle",
        "Glass Food Containers", "Ceramic Mug Set", "Cutting Board Set",
        "Air Fryer", "Coffee Maker", "Blender", "Dish Rack", "Spice Rack",
        "Bamboo Utensil Set", "Storage Bins", "Throw Pillow Set", "Bath Towel Set",
        "Shower Curtain", "Wall Clock", "Picture Frame Set", "Laundry Basket",
        "Vacuum Sealer", "Toaster Oven", "Cookware Set",
    ],
    "Apparel": [
        "Cotton T-Shirt", "Slim Fit Jeans", "Wool Sweater", "Running Shorts",
        "Hooded Sweatshirt", "Denim Jacket", "Athletic Leggings", "Polo Shirt",
        "Winter Parka", "Flannel Shirt", "Yoga Pants", "Crew Socks (3-Pack)",
        "Baseball Cap", "Canvas Belt", "Knit Beanie", "Rain Jacket",
        "Linen Button-Down", "Cargo Pants", "Graphic Tee", "Fleece Vest",
        "Maxi Dress", "Chino Shorts", "Wool Scarf", "Compression Shirt", "Swim Trunks",
    ],
    "Sports & Outdoors": [
        "Yoga Mat", "Adjustable Dumbbell Set", "Camping Tent", "Hiking Backpack",
        "Resistance Bands Set", "Water Bottle", "Foam Roller", "Sleeping Bag",
        "Bike Helmet", "Jump Rope", "Trekking Poles", "Cooler Bag",
        "Tennis Racket", "Soccer Ball", "Fishing Rod", "Camping Chair",
        "Headlamp", "Pull-Up Bar",
    ],
    "Beauty & Personal Care": [
        "Electric Toothbrush", "Hair Dryer", "Facial Cleanser", "Moisturizer Cream",
        "Sunscreen SPF 50", "Shampoo & Conditioner Set", "Lip Balm Set",
        "Makeup Brush Set", "Nail Care Kit", "Electric Shaver", "Body Lotion",
        "Hair Straightener", "Beard Trimmer", "Face Mask Set", "Perfume",
        "Cotton Rounds", "Vitamin C Serum",
    ],
    "Office Supplies": [
        "Ballpoint Pen Set", "Spiral Notebook", "Desk Organizer", "Sticky Notes Pack",
        "Stapler", "Highlighter Set", "Printer Paper Ream", "File Folders (Pack)",
        "Whiteboard", "Label Maker", "Calculator", "Binder Clips",
        "Desk Mat", "Ring Binder", "Sticky Tabs", "Pencil Case",
        "Push Pins", "Laminating Sheets", "Index Cards", "Wall Calendar",
    ],
}

products = []
product_id = 1000
for cat, count in categories.items():
    pool = name_pools[cat]
    for i in range(count):
        base_price = {
            "Electronics": np.random.uniform(25, 500),
            "Home & Kitchen": np.random.uniform(10, 150),
            "Apparel": np.random.uniform(8, 90),
            "Sports & Outdoors": np.random.uniform(10, 200),
            "Beauty & Personal Care": np.random.uniform(5, 60),
            "Office Supplies": np.random.uniform(3, 80),
        }[cat]
        name = pool[i % len(pool)]
        products.append({
            "product_id": product_id,
            "product_name": name,
            "category": cat,
            "unit_price": round(base_price, 2),
        })
        product_id += 1

products_df = pd.DataFrame(products)
print(f"Products: {len(products_df)}")

# ─────────────────────────────────────────────
# 2. REGIONS
# ─────────────────────────────────────────────
regions = ["Northeast", "Southeast", "Midwest", "West", "Southwest"]
region_weight = {"Northeast": 0.24, "Southeast": 0.22, "Midwest": 0.18, "West": 0.23, "Southwest": 0.13}

# ─────────────────────────────────────────────
# 3. DATE RANGE (2 years + 3 months for trend visibility)
# ─────────────────────────────────────────────
date_range = pd.date_range(start="2024-01-01", end="2026-03-31", freq="D")
print(f"Date range: {date_range.min().date()} to {date_range.max().date()}  ({len(date_range)} days)")

# ─────────────────────────────────────────────
# 4. GENERATE TRANSACTIONS
# ─────────────────────────────────────────────
records = []
order_id = 500000

for date in date_range:
    # Seasonal multiplier — higher sales in Nov/Dec, lower in Jan/Feb
    month = date.month
    seasonal = 1.0
    if month in [11, 12]:
        seasonal = 1.6
    elif month in [1, 2]:
        seasonal = 0.8
    elif month in [6, 7, 8]:
        seasonal = 1.15

    # Weekend boost
    weekend = 1.25 if date.weekday() >= 5 else 1.0

    # Year-over-year growth trend (~12% YoY)
    year_factor = 1.0 + (date.year - 2024) * 0.12 + (date.month - 1) / 12 * 0.01

    n_orders_today = int(np.random.poisson(12 * seasonal * weekend * year_factor))

    for _ in range(n_orders_today):
        region = np.random.choice(regions, p=list(region_weight.values()))
        product = products_df.sample(1, weights=products_df["category"].map({
            "Electronics": 1.3, "Home & Kitchen": 1.1, "Apparel": 1.4,
            "Sports & Outdoors": 0.9, "Beauty & Personal Care": 1.0, "Office Supplies": 0.7
        })).iloc[0]

        qty = np.random.choice([1, 2, 3, 4], p=[0.6, 0.25, 0.1, 0.05])
        discount = np.random.choice([0, 0.05, 0.10, 0.15, 0.20], p=[0.55, 0.2, 0.15, 0.07, 0.03])
        unit_price = product["unit_price"]
        revenue = round(unit_price * qty * (1 - discount), 2)

        records.append({
            "order_id": order_id,
            "order_date": date.strftime("%Y-%m-%d"),
            "region": region,
            "product_id": product["product_id"],
            "product_name": product["product_name"],
            "category": product["category"],
            "quantity": qty,
            "unit_price": unit_price,
            "discount": discount,
            "revenue": revenue,
        })
        order_id += 1

sales_df = pd.DataFrame(records)
print(f"\nTotal transactions: {len(sales_df):,}")
print(f"Total revenue: ${sales_df['revenue'].sum():,.2f}")

# Save
sales_df.to_csv("sales_data.csv", index=False)
products_df.to_csv("products.csv", index=False)
print("\nSaved → sales_data.csv, products.csv")
