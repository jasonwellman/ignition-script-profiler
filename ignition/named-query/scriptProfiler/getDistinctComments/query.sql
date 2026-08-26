SELECT DISTINCT comment AS value
FROM script_execution_logs
WHERE comment IS NOT NULL
ORDER BY comment ASC