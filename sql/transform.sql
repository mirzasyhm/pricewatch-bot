-- 1. Ensure Dimension Table Exists (dim_products)
CREATE TABLE IF NOT EXISTS `{project_id}.{dataset}.dim_products` (
    product_id STRING,
    title STRING,
    rating INTEGER,
    current_availability STRING,
    updated_at TIMESTAMP
);

-- 2. Ensure Fact Table Exists (fact_prices)
CREATE TABLE IF NOT EXISTS `{project_id}.{dataset}.fact_prices` (
    price_id STRING,
    product_id STRING,
    price FLOAT64,
    currency STRING,
    captured_at TIMESTAMP
);

-- 3. Upsert into Dimension Table (SCD Type 1 for simplicity)
MERGE `{project_id}.{dataset}.dim_products` T
USING (
    SELECT 
        TO_HEX(MD5(title)) as product_id, -- Generate ID based on title
        title,
        rating,
        availability,
        scraped_at
    FROM `{project_id}.{dataset}.staging_products`
    WHERE DATE(scraped_at) = CURRENT_DATE()
) S
ON T.product_id = S.product_id
WHEN MATCHED THEN
    UPDATE SET 
        rating = S.rating, 
        current_availability = S.availability,
        updated_at = S.scraped_at
WHEN NOT MATCHED THEN
    INSERT (product_id, title, rating, current_availability, updated_at)
    VALUES (S.product_id, S.title, S.rating, S.availability, S.scraped_at);

-- 4. Insert into Fact Table (Append Only)
INSERT INTO `{project_id}.{dataset}.fact_prices` (price_id, product_id, price, currency, captured_at)
SELECT
    GENERATE_UUID() as price_id,
    TO_HEX(MD5(title)) as product_id,
    price,
    currency,
    scraped_at
FROM `{project_id}.{dataset}.staging_products`
WHERE DATE(scraped_at) = CURRENT_DATE();
