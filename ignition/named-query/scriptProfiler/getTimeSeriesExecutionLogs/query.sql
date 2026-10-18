DECLARE @row_limit INT = :limit;

SELECT TOP (@row_limit)
    started_at AS t_stamp,
    script_name,
    duration_ms
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
ORDER BY started_at DESC