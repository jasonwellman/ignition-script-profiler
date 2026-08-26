SELECT 
    script_name AS itemId,
    id AS eventId,
    started_at AS startDate,
    DATEADD(
        millisecond, 
        CAST(CASE WHEN duration_ms < 1000 THEN 1000 ELSE duration_ms END AS INT), 
        started_at
    ) AS endDate,
    script_name + ' (' + status + ' - ' + CAST(CAST(duration_ms AS DECIMAL(10,1)) AS VARCHAR) + 'ms)' AS label,
    'Start: ' + FORMAT(started_at, 'yyyy-MM-dd HH:mm:ss') + CHAR(10) +
    'End: ' + FORMAT(DATEADD(millisecond, CAST(CASE WHEN duration_ms < 1000 THEN 1000 ELSE duration_ms END AS INT), started_at), 'yyyy-MM-dd HH:mm:ss') + CHAR(10) +
    'Duration: ' + CAST(CAST(duration_ms AS DECIMAL(10,1)) AS VARCHAR) + ' ms' AS tooltip
FROM script_execution_logs
WHERE (NULLIF(:date_start, '') IS NULL OR started_at >= :date_start)
  AND (NULLIF(:date_end, '') IS NULL OR started_at <= :date_end)
  AND (
        NULLIF(:script_name, '') IS NULL 
        OR script_name IN (SELECT value FROM STRING_SPLIT(:script_name, ','))
      )
ORDER BY started_at ASC