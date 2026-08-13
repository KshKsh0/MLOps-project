
# Brazilian E-Commerce Public Dataset by Olist

This project builds a reproducible data pipeline for the **Brazilian E-Commerce Public Dataset by Olist**.

The goal of this stage is to:

- Load the original CSV files into PostgreSQL.
- Define a proper relational database schema.
- Create primary and foreign key relationships.
- Create reusable analytical views.
- Aggregate data to the order level.
- Validate database integrity.
- Prepare the data for future EDA and machine learning.

The future supervised-learning task is:

> **Predict whether an order will be delivered late or on time.**

---

## Project Structure

```text
Brazilian E-Commerce Public Dataset by Olist/
│
├── data/
│   ├── olist_customers_dataset.csv
│   ├── olist_geolocation_dataset.csv
│   ├── olist_order_items_dataset.csv
│   ├── olist_order_payments_dataset.csv
│   ├── olist_order_reviews_dataset.csv
│   ├── olist_orders_dataset.csv
│   ├── olist_products_dataset.csv
│   ├── olist_sellers_dataset.csv
│   └── product_category_name_translation.csv
│
├── sql/
│   ├── schema.sql
│   └── features.sql
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── db.py
│   ├── schema.py
│   ├── ingest.py
│   ├── validate.py
│   └── pipeline.py
│
├── notebooks/
│   └── database_test.ipynb
│
├── .env
├── .gitignore
├── docker-compose.yml
├── requirements.txt
└── README.md
````

---

# Technologies

The project currently uses:

* Python
* Pandas
* PostgreSQL
* Docker
* Docker Compose
* SQLAlchemy
* Psycopg
* python-dotenv
* Jupyter Notebook

---

# Dataset

The project uses the **Brazilian E-Commerce Public Dataset by Olist**.

The data is provided as multiple related CSV files instead of one flat machine-learning dataset.

The main datasets are:

| Table                  | Description                                 |
| ---------------------- | ------------------------------------------- |
| `customers`            | Customer information                        |
| `orders`               | Order lifecycle and delivery information    |
| `order_items`          | Products and sellers associated with orders |
| `order_payments`       | Payment information                         |
| `order_reviews`        | Customer reviews                            |
| `products`             | Product information                         |
| `sellers`              | Seller information                          |
| `geolocation`          | Brazilian ZIP-code coordinates              |
| `category_translation` | Portuguese-to-English category translation  |

---

# Database Schema

## Customers

One row represents a customer record associated with an order.

```text
customers
────────────────────────────────
PK  customer_id
    customer_unique_id
    customer_zip_code_prefix
    customer_city
    customer_state
```

### Important distinction

`customer_id` identifies the customer record connected to an order.

`customer_unique_id` can identify the same real customer across multiple purchases.

Relationship:

```text
customers.customer_id
        │
        ▼
orders.customer_id
```

---

## Orders

One row represents one order.

```text
orders
────────────────────────────────────────────
PK  order_id
FK  customer_id

    order_status
    order_purchase_timestamp
    order_approved_at
    order_delivered_carrier_date
    order_delivered_customer_date
    order_estimated_delivery_date
```

`orders` is the central table in the database.

The delivery target is derived using:

```text
order_delivered_customer_date
            VS
order_estimated_delivery_date
```

Target definition:

```text
Actual delivery <= Estimated delivery
→ On Time

Actual delivery > Estimated delivery
→ Late
```

---

## Order Items

One row represents one item inside an order.

```text
order_items
────────────────────────────────
PK/FK  order_id
PK     order_item_id

FK     product_id
FK     seller_id

       shipping_limit_date
       price
       freight_value
```

The primary key is composite:

```text
(order_id, order_item_id)
```

This is necessary because one order can contain multiple items.

Example:

```text
order_id   order_item_id   product_id
A          1               P1
A          2               P2
A          3               P3
```

Relationships:

```text
orders        1 ───── N order_items
products      1 ───── N order_items
sellers       1 ───── N order_items
```

---

## Products

One row represents one product.

```text
products
──────────────────────────────────────
PK  product_id

    product_category_name
    product_name_lenght
    product_description_lenght
    product_photos_qty
    product_weight_g
    product_length_cm
    product_height_cm
    product_width_cm
```

Relationship:

```text
products.product_id
        │
        ▼
order_items.product_id
```

---

## Sellers

One row represents one seller.

```text
sellers
────────────────────────────────
PK  seller_id

    seller_zip_code_prefix
    seller_city
    seller_state
```

Relationship:

```text
sellers.seller_id
        │
        ▼
order_items.seller_id
```

One seller can appear in many order items.

One order can also contain items from multiple sellers.

---

## Order Payments

One row represents one payment record associated with an order.

```text
order_payments
────────────────────────────────
PK/FK  order_id
PK     payment_sequential

       payment_type
       payment_installments
       payment_value
```

The primary key is:

```text
(order_id, payment_sequential)
```

One order can have multiple payment records.

Relationship:

```text
orders 1 ───── N order_payments
```

---

## Order Reviews

One row represents one review record.

```text
order_reviews
────────────────────────────────
PK  review_row_id

    review_id

FK  order_id

    review_score
    review_comment_title
    review_comment_message
    review_creation_date
    review_answer_timestamp
```

Relationship:

```text
orders 1 ───── N order_reviews
```

Reviews happen after the purchase process and should be handled carefully during machine learning because they may cause **data leakage**.

---

## Geolocation

Contains geographical information associated with Brazilian ZIP-code prefixes.

```text
geolocation
────────────────────────────────
geolocation_zip_code_prefix
geolocation_lat
geolocation_lng
geolocation_city
geolocation_state
```

The ZIP-code prefix is not used as a primary key because one prefix may appear multiple times.

Logical relationships exist with:

```text
customers.customer_zip_code_prefix
```

and:

```text
sellers.seller_zip_code_prefix
```

These relationships are not enforced as direct foreign keys.

---

## Category Translation

Contains Portuguese-to-English product category translations.

```text
category_translation
────────────────────────────────────
PK  product_category_name

    product_category_name_english
```

Logical relationship:

```text
products.product_category_name
            │
            ▼
category_translation.product_category_name
```

---

# Main Entity Relationships

```text
                    CUSTOMERS
                        │
                        │ customer_id
                        ▼
                     ORDERS
                  ┌─────┼─────┐
                  │     │     │
                  ▼     ▼     ▼
            ORDER_ITEMS PAYMENTS REVIEWS
              │      │
              │      │
        ┌─────┘      └─────┐
        ▼                  ▼
     PRODUCTS            SELLERS
```

Main cardinalities:

```text
customers       1 ───── 1 orders

orders          1 ───── N order_items
orders          1 ───── N order_payments
orders          1 ───── N order_reviews

products        1 ───── N order_items
sellers         1 ───── N order_items
```

---

# Why Aggregation Is Necessary

The future machine-learning problem operates at the **order level**.

Therefore:

```text
one ML row = one order
```

However, `order_items` may contain multiple rows for the same order.

Example:

```text
order_items

order_id   product_id   price
A          P1           20
A          P2           30
A          P3           10
```

If this table is directly joined with `orders`, order `A` appears three times.

Instead, the data is first aggregated:

```sql
SELECT
    order_id,
    COUNT(*) AS number_of_items,
    SUM(price) AS total_price
FROM order_items
GROUP BY order_id;
```

Result:

```text
order_id   number_of_items   total_price
A          3                 60
```

The aggregated data can then safely be joined with `orders` while maintaining one row per order.

---

# Analytics Views

The project creates an `analytics` schema containing derived SQL views.

## `analytics.order_item_features`

Aggregates `order_items` to one row per order.

Features include:

* Number of items
* Number of unique products
* Number of sellers
* Total item price
* Average item price
* Maximum item price
* Total freight value

---

## `analytics.payment_features`

Aggregates payment data to one row per order.

Features include:

* Number of payment records
* Total payment value
* Maximum number of installments
* Payment-type counts

---

## `analytics.ml_order_dataset`

Combines:

```text
orders
+
customers
+
order_item_features
+
payment_features
```

into one row per order.

It also creates the classification target:

```text
is_late
```

where:

```text
0 = On Time
1 = Late
NULL = Delivery date unavailable
```

The actual delivery date is used to create the target but is not included as a model input feature.

---

# Table vs View

## Table

A PostgreSQL table physically stores its rows.

Examples:

```text
orders
customers
order_items
products
```

## View

A view stores a SQL query that generates data from existing tables.

Examples:

```text
analytics.order_item_features
analytics.payment_features
analytics.ml_order_dataset
```

The view definition is permanently stored in PostgreSQL.

The resulting rows are generated when the view is queried.

---

# Setup

## 1. Open the Project

Navigate to the project root:

```bash
cd "Brazilian E-Commerce Public Dataset by Olist"
```

---

## 2. Create a Conda Environment

```bash
conda create -n olist python=3.11
```

Activate it:

```bash
conda activate olist
```

---

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file in the root directory:

```env
POSTGRES_DB=olist
POSTGRES_USER=olist_user
POSTGRES_PASSWORD=olist_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

The `.env` file should not be committed to Git.

Add it to `.gitignore`:

```gitignore
.env
```

---

# Start PostgreSQL

Make sure Docker Desktop is running.

Start PostgreSQL:

```bash
docker compose up -d
```

Check that the container is running:

```bash
docker compose ps
```

---

# Run the Full Data Pipeline

Run the following command from the **project root**:

```bash
python -m src.pipeline
```

Do not run:

```bash
python src/pipeline.py
```

and do not run `pipeline.py` from inside the `src` directory.

The pipeline uses package-relative imports and should therefore be executed with `-m`.

---

# Pipeline Steps

Running:

```bash
python -m src.pipeline
```

executes:

```text
1. Create PostgreSQL schema
2. Ingest CSV files
3. Create analytics views
4. Validate the database
```

The complete flow is:

```text
CSV Files
    │
    ▼
schema.sql
    │
    ├── Create tables
    ├── Define data types
    ├── Primary keys
    ├── Foreign keys
    └── Indexes
    │
    ▼
ingest.py
    │
    ├── Read CSV files
    ├── Parse timestamps
    ├── Load in chunks
    └── Insert into PostgreSQL
    │
    ▼
features.sql
    │
    ├── Aggregate order items
    ├── Aggregate payments
    ├── Join order-level data
    └── Create target
    │
    ▼
validate.py
    │
    ├── Validate row counts
    ├── Validate relationships
    ├── Check dataset granularity
    └── Check target distribution
    │
    ▼
Data Ready
```

---

# Expected Pipeline Result

A successful run should produce output similar to:

```text
TABLE COUNTS

customers                      99,441
geolocation                 1,000,163
products                       32,951
sellers                         3,095
category_translation               71
orders                         99,441
order_items                   112,650
order_payments                103,886
order_reviews                  99,224

RELATIONSHIP CHECKS

orders -> customers                 0
items -> orders                     0
items -> products                   0
items -> sellers                    0
payments -> orders                  0
reviews -> orders                   0

ML DATASET GRANULARITY

Rows:          99,441
Unique orders: 99,441
```

The zeros under relationship checks mean:

```text
0 broken relationships
```

They do **not** mean that the tables have no relationships.

---

# Connect to PostgreSQL Manually

Open PostgreSQL inside the Docker container:

```bash
docker exec -it olist_postgres psql -U olist_user -d olist
```

Show tables:

```sql
\dt
```

Show analytics views:

```sql
\dv analytics.*
```

Inspect a table:

```sql
\d orders
```

Exit PostgreSQL:

```sql
\q
```

#### or use an external software like dbeaver
---

# Query PostgreSQL From Python

Instead of reading CSV files directly during analysis, data can now be retrieved from PostgreSQL.

```python
import pandas as pd

from src.db import get_engine

engine = get_engine()
```

Read orders:

```python
orders = pd.read_sql(
    """
    SELECT *
    FROM orders
    LIMIT 10;
    """,
    engine
)

orders
```

---

# Example SQL Join

```python
query = """
SELECT
    o.order_id,
    o.order_status,
    o.order_purchase_timestamp,
    c.customer_city,
    c.customer_state
FROM orders o
JOIN customers c
    ON o.customer_id = c.customer_id
LIMIT 10;
"""

pd.read_sql(query, engine)
```

---

# Example Aggregation

```python
query = """
SELECT
    order_id,
    COUNT(*) AS number_of_items,
    SUM(price) AS total_price,
    SUM(freight_value) AS total_freight
FROM order_items
GROUP BY order_id
LIMIT 10;
"""

pd.read_sql(query, engine)
```

---

# Access the ML Dataset

The order-level analytical dataset can be loaded directly from the PostgreSQL view:

```python
ml_data = pd.read_sql(
    """
    SELECT *
    FROM analytics.ml_order_dataset
    WHERE is_late IS NOT NULL;
    """,
    engine
)

ml_data.head()
```

The resulting Pandas DataFrame can later be used for:

```text
EDA
↓
Data Cleaning
↓
Feature Engineering
↓
Train/Test Split
↓
Model Training
↓
Evaluation
```

---

# Stop PostgreSQL

Stop PostgreSQL while keeping the database:

```bash
docker compose stop
```

Start it again:

```bash
docker compose start
```

You can also remove the container while preserving the Docker volume:

```bash
docker compose down
```

Start it again with:

```bash
docker compose up -d
```

---

# Delete the Database Completely

To delete both the container and PostgreSQL volume:

```bash
docker compose down -v
```

This removes the stored database.

It can be rebuilt using:

```bash
docker compose up -d
python -m src.pipeline
```

---

# Current Pipeline Status

The current pipeline provides:

* Dockerized PostgreSQL
* Reproducible SQL schema
* Correct database data types
* Primary keys
* Foreign keys
* Database indexes
* Chunked CSV ingestion
* Automated relationship validation
* Order-item aggregation
* Payment aggregation
* Late-delivery target creation
* One-row-per-order analytical dataset
* Python and Jupyter database access

---

# Next Steps

The next stages of the project are:

```text
EDA
↓
Data Quality Analysis
↓
Feature Engineering
↓
Dataset Splitting
↓
Model Training
↓
Model Evaluation
↓
Experiment Tracking
↓
Model Deployment
```

```
```
