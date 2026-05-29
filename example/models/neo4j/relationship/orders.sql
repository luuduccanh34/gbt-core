{{ config(
    connector = 'trino'
) }}

SELECT
  purchase_id,
  package_id,
  buyer_gid,
  final_price,
  status,
  created_at,
  cust_type
FROM {{ source('landing', 'transaction', 'orders') }}
