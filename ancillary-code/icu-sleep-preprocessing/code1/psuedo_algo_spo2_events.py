# PSEUDO ALGORITHM SPO2 Finding.

# SpO2 is in some way an easy signal, however the difficultity in findings drops is the granularity: 
# you want to detect slowly-happening drops, at the same time you don't want to group together two different drops (that are within a small-ish time window, right next to each other)
# e.g.
# we want to be able to detect a drop that slowly decreases from 100% - 96% within 30 seconds, but also we want to detect 2 individual drops (e.g. both from 100 to 96) that only take 10 seconds but are also only 10 seconds apart from each other.


windowsizes = [10, 15, 20, 25, 30] # seconds
drop_threshold = 4
drop_indices = []

for ws in windowsizes:

	# rolling window with windowsize ws:
	baseline_spo2 		# e.g. with moving 0.9 quantile, moving max, or some other approach.
	min_spo2 			# e.g. moving minimum

	# compute max observed drop in this window:
	drops = baseline_spo2 - min_spo2 # either ignoring timing of max and min locations or take into account.

	drop_indices_end = where(drops>drop_threshold) 
	drop_indices_start = drop_indices_end-ws
	for start_candidate, end_candidate in zip(drop_indices_start, drop_indices_end):
		# check if any index within this start and end window candidate is already contained in the drop_indices list, if not: new spo2 drop found, add it.
		already_contained = np.any(np.isin(np.arange(start_candidate, end_candidate), drop_indices))
		if not already_contained:
			drop_indices.append(np.arange(start_candidate, end_candidate))







# PSEUDO ALGO MATCHING:
# we have two boolean arrays:
# 1. airflow_crit # 1 if airflow criteria is fulfilled
# 2. spo2_crit # 1 if spo2 criteria is fulfilled

# potentially for each start of the spo2 drop start, find closest respiration event.
# closest respiration event has to be 'free', i.e. not already matched to another spo2 drop.
# closest respiration event has to be within a given time. e.g. end of respiration event and start cannot be further apart than 40 seconds.






