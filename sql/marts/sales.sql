INSERT INTO mart.sales
SELECT
    transaction_id,
    transaction_date,
    customer_id,
    product_id,
    quantity,
    unit_price,
    total_amount
FROM staging.sales;
