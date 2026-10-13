def onStartup(session):
	session.custom.scriptProfiler.filters.dateStart = system.date.addDays(system.date.now(),-7)
	session.custom.scriptProfiler.filters.dateEnd = system.date.addDays(system.date.now(),1)