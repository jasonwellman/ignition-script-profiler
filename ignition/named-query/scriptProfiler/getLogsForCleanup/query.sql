SELECT id, script_name, script_type, duration_ms, status, started_at, comment
FROM script_execution_logs
WHERE (:days_to_keep IS NULL OR started_at < DATEADD(day, -:days_to_keep, GETDATE()))
  AND (:script_name IS NULL OR script_name = :script_name)
  AND (:script_type IS NULL OR script_type = :script_type)
  AND (:comment_filter IS NULL OR comment LIKE '%' + :comment_filter + '%')
ORDER BY started_at ASC