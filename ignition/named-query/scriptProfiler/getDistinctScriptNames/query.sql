SELECT DISTINCT script_name AS value
FROM script_execution_logs
WHERE script_name IS NOT NULL
ORDER BY script_name ASC