from sqlalchemy import text

from .db import get_engine


TABLES = [

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


ORPHAN_CHECKS = {

    "orders -> customers":

        """
        SELECT COUNT(*)
        FROM orders o

        LEFT JOIN customers c
            ON o.customer_id = c.customer_id

        WHERE c.customer_id IS NULL
        """,


    "items -> orders":

        """
        SELECT COUNT(*)
        FROM order_items i

        LEFT JOIN orders o
            ON i.order_id = o.order_id

        WHERE o.order_id IS NULL
        """,


    "items -> products":

        """
        SELECT COUNT(*)
        FROM order_items i

        LEFT JOIN products p
            ON i.product_id = p.product_id

        WHERE p.product_id IS NULL
        """,


    "items -> sellers":

        """
        SELECT COUNT(*)
        FROM order_items i

        LEFT JOIN sellers s
            ON i.seller_id = s.seller_id

        WHERE s.seller_id IS NULL
        """,


    "payments -> orders":

        """
        SELECT COUNT(*)
        FROM order_payments p

        LEFT JOIN orders o
            ON p.order_id = o.order_id

        WHERE o.order_id IS NULL
        """,


    "reviews -> orders":

        """
        SELECT COUNT(*)
        FROM order_reviews r

        LEFT JOIN orders o
            ON r.order_id = o.order_id

        WHERE o.order_id IS NULL
        """,
}


def validate():

    engine = get_engine()


    try:

        with engine.connect() as conn:

            print(
                "\n=============================="
            )

            print(
                "DATABASE VALIDATION"
            )

            print(
                "==============================\n"
            )


            # ------------------------------------------------
            # Table counts
            # ------------------------------------------------

            print("TABLE COUNTS\n")


            for table in TABLES:

                count = conn.execute(

                    text(
                        f"""
                        SELECT COUNT(*)
                        FROM {table}
                        """
                    )

                ).scalar()


                print(
                    f"{table:<25}"
                    f"{count:>12,}"
                )


                if count == 0:

                    raise ValueError(
                        f"{table} is empty"
                    )


            # ------------------------------------------------
            # Foreign-key consistency
            # ------------------------------------------------

            print(
                "\nRELATIONSHIP CHECKS\n"
            )


            for name, query in (
                ORPHAN_CHECKS.items()
            ):

                count = conn.execute(
                    text(query)
                ).scalar()


                print(
                    f"{name:<25}"
                    f"{count:>12,}"
                )


                if count != 0:

                    raise ValueError(
                        f"Broken relationship: {name}"
                    )


            # ------------------------------------------------
            # ML table granularity
            # ------------------------------------------------

            result = conn.execute(

                text(
                    """
                    SELECT
                        COUNT(*) AS rows,
                        COUNT(
                            DISTINCT order_id
                        ) AS unique_orders

                    FROM analytics.ml_order_dataset
                    """
                )

            ).fetchone()


            rows = result[0]

            unique_orders = result[1]


            print(
                "\nML DATASET GRANULARITY\n"
            )


            print(
                f"Rows:          {rows:,}"
            )

            print(
                f"Unique orders: {unique_orders:,}"
            )


            if rows != unique_orders:

                raise ValueError(
                    "ML dataset contains "
                    "duplicate orders"
                )


            # ------------------------------------------------
            # Target
            # ------------------------------------------------

            print(
                "\nTARGET DISTRIBUTION\n"
            )


            results = conn.execute(

                text(
                    """
                    SELECT
                        is_late,
                        COUNT(*)

                    FROM analytics.ml_order_dataset

                    WHERE is_late IS NOT NULL

                    GROUP BY is_late

                    ORDER BY is_late
                    """
                )
            )


            for target, count in results:

                label = (
                    "Late"
                    if target == 1
                    else "On Time"
                )


                print(
                    f"{label:<15}"
                    f"{count:>12,}"
                )


            print(
                "\nValidation passed."
            )


    finally:

        engine.dispose()