

DROP SCHEMA IF EXISTS analytics CASCADE;

CREATE SCHEMA analytics;


CREATE VIEW analytics.order_item_features AS

SELECT

    order_id,

    COUNT(*)::INTEGER
        AS number_of_items,

    COUNT(DISTINCT product_id)::INTEGER
        AS unique_products,

    COUNT(DISTINCT seller_id)::INTEGER
        AS number_of_sellers,

    SUM(price)
        AS total_item_price,

    AVG(price)
        AS average_item_price,

    MAX(price)
        AS maximum_item_price,

    SUM(freight_value)
        AS total_freight

FROM order_items

GROUP BY order_id;


CREATE VIEW analytics.payment_features AS

SELECT

    order_id,

    COUNT(*)::INTEGER
        AS payment_records,

    SUM(payment_value)
        AS total_payment_value,

    MAX(payment_installments)
        AS maximum_installments,

    COUNT(*) FILTER (
        WHERE payment_type = 'credit_card'
    )::INTEGER
        AS credit_card_payments,

    COUNT(*) FILTER (
        WHERE payment_type = 'voucher'
    )::INTEGER
        AS voucher_payments,

    COUNT(*) FILTER (
        WHERE payment_type = 'boleto'
    )::INTEGER
        AS boleto_payments,

    COUNT(*) FILTER (
        WHERE payment_type = 'debit_card'
    )::INTEGER
        AS debit_card_payments

FROM order_payments

GROUP BY order_id;


CREATE VIEW analytics.ml_order_dataset AS

SELECT

    o.order_id,

    o.customer_id,

    c.customer_unique_id,


    o.order_purchase_timestamp,

    EXTRACT(
        YEAR
        FROM o.order_purchase_timestamp
    )::INTEGER
        AS purchase_year,

    EXTRACT(
        MONTH
        FROM o.order_purchase_timestamp
    )::INTEGER
        AS purchase_month,

    EXTRACT(
        DOW
        FROM o.order_purchase_timestamp
    )::INTEGER
        AS purchase_day_of_week,

    EXTRACT(
        HOUR
        FROM o.order_purchase_timestamp
    )::INTEGER
        AS purchase_hour,



    EXTRACT(
        EPOCH
        FROM (
            o.order_estimated_delivery_date
            -
            o.order_purchase_timestamp
        )
    ) / 86400.0
        AS promised_delivery_days,

    c.customer_zip_code_prefix,

    c.customer_city,

    c.customer_state,

    COALESCE(
        i.number_of_items,
        0
    )
        AS number_of_items,

    COALESCE(
        i.unique_products,
        0
    )
        AS unique_products,

    COALESCE(
        i.number_of_sellers,
        0
    )
        AS number_of_sellers,

    COALESCE(
        i.total_item_price,
        0
    )
        AS total_item_price,

    COALESCE(
        i.average_item_price,
        0
    )
        AS average_item_price,

    COALESCE(
        i.maximum_item_price,
        0
    )
        AS maximum_item_price,

    COALESCE(
        i.total_freight,
        0
    )
        AS total_freight,


    COALESCE(
        p.payment_records,
        0
    )
        AS payment_records,

    COALESCE(
        p.total_payment_value,
        0
    )
        AS total_payment_value,

    COALESCE(
        p.maximum_installments,
        0
    )
        AS maximum_installments,



    CASE

        WHEN
            o.order_delivered_customer_date
            IS NULL

        THEN NULL


        WHEN
            o.order_delivered_customer_date
            >
            o.order_estimated_delivery_date

        THEN 1


        ELSE 0

    END AS is_late


FROM orders o


JOIN customers c

    ON
        o.customer_id
        =
        c.customer_id


LEFT JOIN analytics.order_item_features i

    ON
        o.order_id
        =
        i.order_id


LEFT JOIN analytics.payment_features p

    ON
        o.order_id
        =
        p.order_id;