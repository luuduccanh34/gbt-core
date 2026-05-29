{{ config(
    connector = 'trino'
) }}

SELECT
  package_id,
  package_code,
  name,
  target_customer,
  price,
  duration_value,
  status
FROM {{ source('landing', 'product', 'package') }}
