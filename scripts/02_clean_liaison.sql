INSTALL excel;
LOAD excel;

CREATE OR REPLACE TABLE liaison_clean AS
SELECT DISTINCT
    TRY_CAST(product_id AS INTEGER) AS product_id,
    NULLIF(TRIM(id_web), '') AS id_web
FROM read_xlsx(
    'data/liaison.xlsx',
    header = true,
    all_varchar = true
)
WHERE TRY_CAST(product_id AS INTEGER) IS NOT NULL;