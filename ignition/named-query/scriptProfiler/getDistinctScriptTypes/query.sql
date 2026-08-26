SELECT DISTINCT script_type AS value
FROM script_execution_logs
WHERE script_type IS NOT NULL
ORDER BY script_type ASC