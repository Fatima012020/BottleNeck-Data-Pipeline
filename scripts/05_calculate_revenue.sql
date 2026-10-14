CREATE OR REPLACE TABLE revenue_products AS
SELECT
    product_id,
    sku,
    post_title,
    price,
    total_sales,
    stock_quantity,
    stock_status,
    price * total_sales AS chiffre_affaires
FROM merged_products;

CREATE OR REPLACE TABLE revenue_total AS
SELECT
    SUM(chiffre_affaires) AS chiffre_affaires_total
FROM revenue_products;