{{ config(materialized='view') }}

with sales as (
    select * from {{ ref('stg_sales') }}
),

daily_agg as (
    select
        transaction_date,
        count(*) as transaction_count,
        sum(quantity) as units_sold,
        sum(total_amount) as revenue
    from sales
    group by transaction_date
)

select * from daily_agg