{{ config(
    connector = 'trino'
) }}

SELECT
    gid,
    created_date,
    district,
    status
FROM {{ source('landing', 'mdm', 'customer') }}
