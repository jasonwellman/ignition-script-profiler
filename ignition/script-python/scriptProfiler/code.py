import traceback
import java.lang.System as JSystem
import system

def ensure_table_exists():
	"""
	Checks if the script_execution_logs table exists on the default database and creates it if missing.
	"""
	try:
	    create_query = """
	        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='script_execution_logs' and xtype='U')
	        CREATE TABLE script_execution_logs (
	            id INT IDENTITY(1,1) PRIMARY KEY,
	            script_name VARCHAR(255) NOT NULL,
	            script_type VARCHAR(100) NOT NULL,
	            duration_ms FLOAT NOT NULL,
	            status VARCHAR(50) NOT NULL,
	            error_message TEXT NULL,
	            stack_trace TEXT NULL,
	            comment VARCHAR(500) NULL,
	            started_at DATETIME NOT NULL
	        )
	    """
	    system.db.runUpdateQuery(create_query)
	except Exception as e:
	    system.util.getLogger("ScriptProfiler").error("Failed to auto-create log table: " + str(e))

def profiler(_func=None, script_type="General Script", capture_stack=False, debug=False, comment=None):
	"""
	A flexible decorator that measures execution duration, catches errors, and logs script performance metrics.

    Example:
        from scriptProfiler import profiler

        @profiler(script_type="Timer Script", debug=False, comment="My Script")
        def my_script():
            # Execution logic here
            return results
	
	Parameters:
		_func (callable, optional): Internal reference when used as a bare decorator `@profiler`.
		script_type (str, optional): Category for dashboard filtering (default: "General Script").
		capture_stack (bool, optional): If True, logs full stack traces on error (default: False).
		debug (bool, optional): If True, prints telemetry directly to Gateway logs/console (default: False).
		comment (str, optional): Custom string for adding execution notes or context.
	
	Returns:
        callable: Wrapped function that handles execution timing, error handling, and logging.
	
	SUGGESTED SCRIPT TYPES
	--------------------------------
	* "Timer Script"        - For scheduled background polling loops.
	* "Tag Change Script"   - For data-driven tag state updates.
	* "Gateway Event"       - For startup, shutdown, or client session events.
	* "Custom Library"      - For utility and helper script modules.
	* "API Integration"     - For external web service calls or SQL syncs.
	* "General Script"      - Default fallback category.
	"""
	
	def decorator(func):
	    func_name = func.__name__
	    
	    def wrapper(*args, **kwargs):
	        t0 = JSystem.nanoTime()
	        status = "SUCCESS"
	        error_msg = None
	        stack = None
	        
	        try:
	            result = func(*args, **kwargs)
	            return result
	        except Exception as e:
	            status = "ERROR"
	            error_msg = str(e)
	            
	            # Only pay the performance penalty of formatting a stack trace if enabled
	            if capture_stack:
	                stack = traceback.format_exc()
	            else:
	                stack = "[Stack trace omitted. Enable capture_stack=True to view.]"
	            
	            if debug:
	                print("[PROFILER ERROR CAUGHT] in function '%s': %s" % (func_name, error_msg))
	                
	            raise e
	        finally:
	            t1 = JSystem.nanoTime()
	            duration_ms = float(t1 - t0) / 1000000.0
	            
	            # If debug mode is on, print to the console for testing
	            if debug:
	                print("--- SCRIPT TELEMETRY REPORT ---")
	                print("  Script Name   : %s" % func_name)
	                print("  Execution Type: %s" % script_type)
	                print("  Duration (ms) : %.4f ms" % duration_ms)
	                print("  Status        : %s" % status)
	                if comment:
	                    print("  Comment       : %s" % comment)
	                print("--------------------------------")
	            else:
	                # Asynchronous background write to keep the main thread fast in production
	                def async_log():
	                    try:
	                        query = """
	                            INSERT INTO script_execution_logs 
	                            (script_name, script_type, duration_ms, status, error_message, stack_trace, comment, started_at)
	                            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
	                        """
	                        system.db.runPrepUpdate(query, [func_name, script_type, duration_ms, status, error_msg, stack, comment])
	                    except Exception as log_err:
	                        system.util.getLogger("ScriptProfiler").error("Logging failed: " + str(log_err))
	                
	                system.util.invokeAsynchronous(async_log)
	            
	    return wrapper
	
	if _func is None:
	    return decorator
	else:
	    return decorator(_func)
	  