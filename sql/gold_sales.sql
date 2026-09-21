DROP TABLE IF EXISTS mart.sales_daily;

CREATE TABLE mart.sales_daily AS

SELECT
    transaction_date,
    COUNT(*) AS transaction_count,
    SUM(quantity) AS units_sold,
    SUM(total_amount) AS revenue

FROM staging.sales

GROUP BY transaction_date

ORDER BY transaction_date;