{{ config(materialized='table') }}

select * from {{ ref('int_sales_daily') }}