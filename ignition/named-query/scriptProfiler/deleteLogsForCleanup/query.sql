DELETE FROM script_execution_logs
WHERE (NULLIF(:date_start, '') IS NULL OR started_at >= :date_start)
  AND (NULLIF(:date_end, '') IS NULL OR started_at <= :date_end)
  AND (
        NULLIF(:script_name, '') IS NULL 
        OR script_name IN (SELECT TRIM(value) FROM STRING_SPLIT(:script_name, ','))
      )
  AND (
        NULLIF(:script_type, '') IS NULL 
        OR script_type IN (SELECT TRIM(value) FROM STRING_SPLIT(:script_type, ','))
      )
  AND (
        NULLIF(:comment_filter, '') IS NULL 
        OR EXISTS (
            SELECT 1 
            FROM STRING_SPLIT(:comment_filter, ',') 
            WHERE comment LIKE '%' + TRIM(value) + '%'
        )
      )