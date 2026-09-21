INSERT INTO staging.sales (
    transaction_id,
    transaction_date,
    customer_id,
    product_id,
    quantity,
    unit_price,
    total_amount
)
SELECT
    transaction_id,
    transaction_date,
    customer_id,
    product_id,
    quantity,
    unit_price,
    quantity * unit_price AS total_amount
FROM raw.sales;
