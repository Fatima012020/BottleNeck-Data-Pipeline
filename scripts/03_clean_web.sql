INSTALL excel;
LOAD excel;

-- 1. Nettoyage : suppression des lignes sans SKU
CREATE OR REPLACE TABLE web_cleaned AS
SELECT
    NULLIF(TRIM(sku), '') AS sku,
    TRY_CAST(total_sales AS DOUBLE) AS total_sales,
    CAST(post_title AS VARCHAR) AS post_title,
    CAST(post_status AS VARCHAR) AS post_status,
    CAST(post_type AS VARCHAR) AS post_type
FROM read_xlsx(
    'data/web.xlsx',
    header = true,
    all_varchar = true
)
WHERE NULLIF(TRIM(sku), '') IS NOT NULL;

-- 2. Dédoublonnage : conserver une seule ligne par SKU,
-- en privilégiant la ligne de type 'product'
CREATE OR REPLACE TABLE web_clean AS
SELECT
    sku,
    total_sales,
    post_title,
    post_status,
    post_type
FROM (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY sku
            ORDER BY
                CASE
                    WHEN post_type = 'product' THEN 1
                    ELSE 2
                END
        ) AS rn
    FROM web_cleaned
)
WHERE rn = 1;