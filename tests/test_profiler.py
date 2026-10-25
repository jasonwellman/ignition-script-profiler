###  TEST PLAN: Execute in the Ignition Script Console. Designer must be in READ/WRITE mode to execute. ###

import time
import java.lang.Throwable as Throwable

def verify_log_in_db(expected_status, search_value="", test_start_time=None, is_script_name=False, expected_error_keyword=None):
	"""
	Queries the script_execution_logs table to verify that the log entry was created within the testing window.
	"""
	
	if test_start_time is None:
		print("  [VERIFICATION ERROR] test_start_time is None. Cannot verify log without a test window timestamp.")
		return False
	
	timeout_seconds = 5
	if is_script_name:
		col = 'script_name'
	else:
		col = 'comment'
	
	query = """
		SELECT TOP 1 script_name, status, comment, duration_ms, error_message, stack_trace
		FROM script_execution_logs
		WHERE %s = ? AND started_at >= ?
		ORDER BY started_at DESC
	""" % col
	params = [search_value, test_start_time]
	
	start_time = system.date.now()
	
	while system.date.secondsBetween(start_time, system.date.now()) < timeout_seconds:
		results = system.db.runPrepQuery(query, params)
		
		if results.getRowCount() > 0:
			db_script = results.getValueAt(0, "script_name")
			db_status = results.getValueAt(0, "status")
			db_comment = results.getValueAt(0, "comment")
			db_exec_time = results.getValueAt(0, "duration_ms")
			err_val = str(results.getValueAt(0, "error_message") or "")
			stack_val = str(results.getValueAt(0, "stack_trace") or "")
			
			# Validate status matches expectation
			if str(db_status) != str(expected_status):
				time.sleep(0.1)
				continue
			
			if expected_error_keyword:
				if expected_error_keyword not in err_val and expected_error_keyword not in stack_val:
					print("    -> [WAITING] Found log, but keyword '" + str(expected_error_keyword) + "' not yet in error/stack trace...")
					time.sleep(0.1)
					continue
			
			print("  [VERIFICATION PASSED] Log entry found within the test window.")
			print("    -> Script Name      : " + str(db_script))
			print("    -> Status           : " + str(db_status) + " (Expected: " + str(expected_status) + ")")
			print("    -> Comment          : " + str(db_comment))
			print("    -> Duration ms      : " + str(db_exec_time) + " ms")
			if expected_error_keyword:
				print("    -> Error Keyword    : Verified '" + str(expected_error_keyword) + "'")
			return True
		    
		time.sleep(0.25)
	    
	print("  [VERIFICATION FAILED] No matching log entry found within the test window for: " + str(search_value))
	print("                        The search start time window was " + str(test_start_time))
	return False

def run_test(test_func, comment, expected_status="SUCCESS", expected_error_keyword=None, is_script_name=False):
	"""
	Executes a test function and verifies the database log entry.
	"""
	
	print("\n\n--------------------------------------------------")
	print(comment)
	print("--------------------------------------------------")
	
	test_start_time_server = system.db.runScalarPrepQuery("SELECT CURRENT_TIMESTAMP")
	test_start_time = system.date.addSeconds(test_start_time_server,-1)
	execution_success = False
	try:
		result = test_func()
		if expected_status == "SUCCESS":
			print("  [INFO] Function returned successfully with value: " + str(result))
			execution_success = True
		else:
			print("  [WARNING] Test expected an ERROR status, but function executed successfully!")
	except (Exception, Throwable) as e:
	    if expected_status == "ERROR":
			print("  [INFO] Expected exception caught: " + str(e))
			execution_success = True
	    else:
			print("  [UNEXPECTED ERROR] Test failed: " + str(e))
	        
	# If execution meets expectations, verify the database log
	if execution_success:
		search_val = test_func.__name__ if is_script_name else comment
		passed = verify_log_in_db(
			expected_status=expected_status, 
			search_value=search_val, 
			test_start_time=test_start_time, 
			is_script_name=is_script_name, 
			expected_error_keyword=expected_error_keyword
		)
		return passed
	
	return False

def record_test(comment, passed):
	"""Appends test result and auto-increments the test index."""
	global index
	test_results.append((comment, passed))
	index += 1
	return

def get_next_comment(description):
	"""Generates the formatted test case comment and auto-increments the index."""
	global index
	comment = comment_start + str(index) + ": " + description
	return comment

# ====================================================================================
# TESTING
# ====================================================================================

test_results = []
index = 1
comment_start = 'Test Case '
test_script_type = 'Validation Script'

# Ensure the profiler table exists
try:
	scriptProfiler.ensure_table_exists()
	print('[SETUP] Database table check/creation executed successfully.')
except (Exception, Throwable) as e:
	print('[SETUP ERROR] Failed to ensure table exists: ' + str(e))



# ====================================================================================
comment = get_next_comment('Standard Success DB Verification')
@scriptProfiler.profiler(script_type=test_script_type, comment=comment)
def test_success_routine():
	time.sleep(0.05)  # 50 ms delay to test the time recorded in DB. Time will be greater due to processing time, which is expected.
	return "Success Result"
    
test_passed = run_test(test_func=test_success_routine, comment=comment, expected_status="SUCCESS")
record_test(comment, test_passed)



# ====================================================================================
comment = get_next_comment('Python Error & Stack Trace Verification')
@scriptProfiler.profiler(script_type=test_script_type, capture_stack=True, comment=comment)
def test_python_error_routine():
	x = 1 / 0  # Trigger division by zero error
	return x
    
test_passed = run_test(test_func=test_python_error_routine, comment=comment, expected_status="ERROR", expected_error_keyword="ZeroDivisionError")
record_test(comment, test_passed)



# ====================================================================================
comment = get_next_comment('Custom Script Type Verification')
@scriptProfiler.profiler(script_type="Custom Script", comment=comment)
def test_custom_script_type():
	time.sleep(0.02)
	return "Timer Result"
    
test_passed = run_test(test_func=test_custom_script_type, comment=comment, expected_status="SUCCESS")
record_test(comment, test_passed)



# ====================================================================================
comment = get_next_comment('Parameter and Return Value Verification')
@scriptProfiler.profiler(script_type=test_script_type, comment=comment)
def test_arguments_routine():
	x, y = 15, 25 # Verify math, expect 375
	return x * y
    
test_passed = run_test(test_func=test_arguments_routine, comment=comment, expected_status="SUCCESS")
record_test(comment, test_passed)



# ====================================================================================
comment = get_next_comment('Capture Stack set to False Verification')
@scriptProfiler.profiler(script_type=test_script_type, capture_stack=False, comment=comment)
def test_stack_omitted_routine():
	raise ValueError("Intentional value error for omitted stack test")
    
test_passed = run_test(test_func=test_stack_omitted_routine, comment=comment, expected_status="ERROR", expected_error_keyword="Stack trace omitted")
record_test(comment, test_passed)



# ====================================================================================
comment = get_next_comment('Java SQL Exception Verification')
@scriptProfiler.profiler(script_type=test_script_type, capture_stack=True, comment=comment)
def test_java_sql_error_routine():
	query = """
		SELECT * 
		FROM NonExistentTableForProfilerValidationTesting
		"""
	system.db.runPrepQuery(query)
	return True
    
test_passed = run_test(test_func=test_java_sql_error_routine, comment=comment, expected_status="ERROR", expected_error_keyword="NonExistentTable")
record_test(comment, test_passed)



# ====================================================================================
test_time_delay = 0.50
comment = get_next_comment('Extended Duration Measurement ' + str(test_time_delay) + 's')
@scriptProfiler.profiler(script_type=test_script_type, comment=comment)
def test_duration_measurement_routine():
	time.sleep(test_time_delay)
	return "Delayed Result"

test_passed = run_test(test_func=test_duration_measurement_routine, comment=comment, expected_status="SUCCESS")
record_test(comment, test_passed)



# ====================================================================================
comment = get_next_comment('Bare Decorator Syntax, Zero Config')
@scriptProfiler.profiler
def test_bare_decorator_routine():
	return "Bare OK"
    
test_passed = run_test(test_func=test_bare_decorator_routine, comment=comment, expected_status="SUCCESS", is_script_name=True)
record_test(comment, test_passed)



# ====================================================================================
comment = get_next_comment('Name Not Defined')
@scriptProfiler.profiler(script_type=test_script_type, comment=comment)
def test_name_error_routine():
	return what_variable_is_this
    
test_passed = run_test(test_func=test_name_error_routine, comment=comment, expected_status="ERROR", expected_error_keyword="not defined")
record_test(comment, test_passed)


# ====================================================================================
print("\n==================================================")
print("          FINAL SUMMARY")
print("==================================================")

status_str = 'RESULT'
test_comment = comment_start + '#: DESCRIPTION'
print '  ' + status_str + ' -> ' +test_comment

for test_comment, passed in test_results:
	if passed:
		status_str = "PASSED"
	else:
		status_str = "FAILED"
	print '  ' + status_str + ' -> ' +test_comment
	
print("==================================================")