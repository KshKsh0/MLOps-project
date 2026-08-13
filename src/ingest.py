import pandas as pd

from .config import DATA_DIR

from .db import get_engine


# ============================================================
# Dataset configuration
# ============================================================

DATASETS = {

    "customers": {

        "filename":
            "olist_customers_dataset.csv",

        "int_columns": [
            "customer_zip_code_prefix",
        ],
    },


    "geolocation": {

        "filename":
            "olist_geolocation_dataset.csv",

        "int_columns": [
            "geolocation_zip_code_prefix",
        ],
    },


    "products": {

        "filename":
            "olist_products_dataset.csv",

        "int_columns": [

            "product_name_lenght",

            "product_description_lenght",

            "product_photos_qty",

            "product_weight_g",

            "product_length_cm",

            "product_height_cm",

            "product_width_cm",
        ],
    },


    "sellers": {

        "filename":
            "olist_sellers_dataset.csv",

        "int_columns": [
            "seller_zip_code_prefix",
        ],
    },


    "category_translation": {

        "filename":
            "product_category_name_translation.csv",
    },


    "orders": {

        "filename":
            "olist_orders_dataset.csv",

        "parse_dates": [

            "order_purchase_timestamp",

            "order_approved_at",

            "order_delivered_carrier_date",

            "order_delivered_customer_date",

            "order_estimated_delivery_date",
        ],
    },


    "order_items": {

        "filename":
            "olist_order_items_dataset.csv",

        "parse_dates": [
            "shipping_limit_date",
        ],

        "int_columns": [
            "order_item_id",
        ],
    },


    "order_payments": {

        "filename":
            "olist_order_payments_dataset.csv",

        "int_columns": [

            "payment_sequential",

            "payment_installments",
        ],
    },


    "order_reviews": {

        "filename":
            "olist_order_reviews_dataset.csv",

        "parse_dates": [

            "review_creation_date",

            "review_answer_timestamp",
        ],

        "int_columns": [
            "review_score",
        ],
    },
}



LOAD_ORDER = [

    "customers",

    "geolocation",

    "products",

    "sellers",

    "category_translation",

    "orders",

    "order_items",

    "order_payments",

    "order_reviews",
]


def prepare_chunk(
    chunk,
    config,
):

    for column in config.get(
        "int_columns",
        []
    ):

        if column in chunk.columns:

            chunk[column] = (

                pd.to_numeric(
                    chunk[column],
                    errors="coerce"
                )

                .astype("Int64")
            )


    return chunk



def ingest_dataset(
    engine,
    table_name,
    config,
):

    file_path = (
        DATA_DIR
        / config["filename"]
    )


    if not file_path.exists():

        raise FileNotFoundError(
            f"Missing file: {file_path}"
        )


    print(
        f"\nLoading {table_name}"
    )


    total_rows = 0


    csv_chunks = pd.read_csv(

        file_path,

        parse_dates=config.get(
            "parse_dates"
        ),

        chunksize=50_000,
    )


    for chunk in csv_chunks:

        chunk = prepare_chunk(
            chunk,
            config,
        )


        chunk.to_sql(

            name=table_name,

            con=engine,

            if_exists="append",

            index=False,

            chunksize=5_000,
        )


        total_rows += len(chunk)


        print(
            f"  {total_rows:,} rows inserted"
        )


    print(
        f"Finished {table_name}: "
        f"{total_rows:,} rows"
    )


    return total_rows

def ingest_all():

    engine = get_engine()

    counts = {}


    try:

        for table_name in LOAD_ORDER:

            counts[table_name] = (
                ingest_dataset(

                    engine,

                    table_name,

                    DATASETS[table_name],
                )
            )


    finally:

        engine.dispose()


    return counts