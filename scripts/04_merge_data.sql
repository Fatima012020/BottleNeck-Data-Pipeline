CREATE OR REPLACE TABLE merged_products AS
SELECT
    e.product_id,
    l.id_web,
    w.sku,
    w.post_title,
    e.price,
    e.stock_quantity,
    e.stock_status,
    w.total_sales
FROM erp_clean e
INNER JOIN liaison_clean l
    ON e.product_id = l.product_id
INNER JOIN web_clean w
    ON CAST(l.id_web AS VARCHAR) = CAST(w.sku AS VARCHAR);