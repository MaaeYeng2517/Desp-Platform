{{ config(materialized='view') }}

select
    transaction_id,
    transaction_date,
    customer_id,
    product_id,
    quantity,
    unit_price,
    quantity * unit_price as total_amount
from raw.sales