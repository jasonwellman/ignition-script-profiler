def handleTimerEvent():
	import time
	import random
	from scriptProfiler import profiler

	@profiler(script_type="Timer Script", debug=False, comment="Moderate OEE calculation cycle")
	def calculate_oee():
		row_count = system.db.runScalarQuery("SELECT COUNT(*) FROM script_execution_logs")
		artificial_delay = 0.05 + (row_count * 0.00005)
		time.sleep(min(artificial_delay, 1.5))
		return "OEE calculated"

	try:
		calculate_oee()      # Place in your 15s timer script block
	except Exception as e:
		print("Timer script execution error: %s" % str(e))