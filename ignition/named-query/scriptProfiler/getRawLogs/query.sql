SELECT 
    id
    ,script_name
    ,script_type
    ,duration_ms
    ,status
    ,error_message
    ,stack_trace
    ,comment
    ,started_at
FROM script_execution_logs
WHERE (NULLIF(:date_start, '') IS NULL OR started_at >= :date_start)
  AND (NULLIF(:date_end, '') IS NULL OR started_at <= :date_end)
  AND (
        NULLIF(:script_name, '') IS NULL 
        OR script_name IN (SELECT value FROM STRING_SPLIT(:script_name, ','))
      )
	AND (
        NULLIF(:script_type, '') IS NULL 
        OR script_type IN (SELECT value FROM STRING_SPLIT(:script_type, ','))
      )
	AND (
        NULLIF(:comment, '') IS NULL 
        OR comment IN (SELECT value FROM STRING_SPLIT(:comment, ','))
      )
ORDER BY started_at DESC