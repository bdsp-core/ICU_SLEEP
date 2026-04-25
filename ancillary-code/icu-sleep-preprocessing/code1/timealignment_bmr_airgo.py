import sys

<<<<<<< HEAD
# sys.path.append('C:/Users/wg984/Wolfgang/repos/ICU-Sleep/code1/')
# sys.path.append('C:/Users/wg984/Wolfgang/repos/Bedmaster-ICU-tools/code/')

sys.path.append('/home/wolfgang/repos/ICU-Sleep/code1/')
sys.path.append('/home/wolfgang/repos/Bedmaster-ICU-tools/code/')


=======
sys.path.append('C:/Users/wg984/Wolfgang/repos/ICU-Sleep/code1/')
sys.path.append('C:/Users/wg984/Wolfgang/repos/Bedmaster-ICU-tools/code/')
>>>>>>> 7df50e71c4295b81010916d223060dd5ec58bf82
import numpy as np
import pandas as pd
from bmresearch_tools import BMR_load, BMR_plot, get_metadata
from resample_BMR import remove_non_monotonic_data
import matplotlib.pyplot as plt
import os
from scipy.signal import find_peaks

<<<<<<< HEAD
doc_path = '/home/wolfgang/repos/ICU-Sleep/timealignment.csv'



# airgo_features_dir = '//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/data_analysis/AirGo/airgo_features/'
# bmr_studyid_dir = '//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/data_analysis/BMR_studyID/'
airgo_features_dir = '/media/mad3/Projects/ICU_SLEEP_STUDY/data/data_analysis/AirGo/airgo_features/'
bmr_studyid_dir = '/media/mad3/Projects/ICU_SLEEP_STUDY/data/data_analysis/BMR_studyID/'

=======



doc_path = 'C:/Users/wg984/Dropbox (Partners HealthCare)/ICU-SLEEP-MATERIALS/TimeAlignmentAirGoBedmaster/timealignment.csv'
airgo_features_dir = '//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/data_analysis/AirGo/airgo_features/'
bmr_studyid_dir = '//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/data_analysis/BMR_studyID/'
>>>>>>> 7df50e71c4295b81010916d223060dd5ec58bf82

doc = pd.read_csv(doc_path)
# doc['study_id'] = doc['study_id'].apply(lambda x: str(x).zfill(3))


<<<<<<< HEAD
for study_id in range(20, 190):

	try:
		# if 1:
=======
for study_id in range(1, 190):

	try:
	# if 1:
>>>>>>> 7df50e71c4295b81010916d223060dd5ec58bf82
		study_id = str(study_id).zfill(3)
		print(study_id)
		airgo_exists = 0
		bmr_exists = 0

<<<<<<< HEAD
		airgo_path = os.path.join(airgo_features_dir, 'airgo_' + study_id + '.csv')
		bmr_path = os.path.join(bmr_studyid_dir, 'BMR_' + study_id + '.h5')
=======
		airgo_path = os.path.join(airgo_features_dir, 'airgo_'+study_id+'.csv')
		bmr_path = os.path.join(bmr_studyid_dir, 'BMR_'+study_id+'.h5')
>>>>>>> 7df50e71c4295b81010916d223060dd5ec58bf82

		airgo_exists = os.path.exists(airgo_path)
		doc.loc[doc.study_id == study_id, 'airgo_available'] = airgo_exists

		bmr_exists = os.path.exists(bmr_path)
		doc.loc[doc.study_id == study_id, 'bmr_available'] = bmr_exists

		# if data is missing, skip the patient
<<<<<<< HEAD
		if airgo_exists == 0 or bmr_exists == 0:
			doc.loc[doc.study_id == study_id, 'code_successful'] = 1
			continue

=======
		if airgo_exists==0 or bmr_exists==0:
			doc.loc[doc.study_id == study_id, 'code_successful'] = 1
			continue


>>>>>>> 7df50e71c4295b81010916d223060dd5ec58bf82
		# otherwise run the lag-finding code:

		# load airgo:
		airgo_data = pd.read_csv(airgo_path)
		if 'DateTime' in airgo_data.columns:
			airgo_data.rename(columns={'DateTime': 'datetime'}, inplace=True)
		airgo_data.set_index('datetime', inplace=True)
		airgo_data.index = pd.to_datetime(airgo_data.index, infer_datetime_format=1)

		# load BMR SPO2%:
		spo2_data = BMR_load(bmr_path, signals=['SPO2%'], loadEvents=0)
		spo2_data = remove_non_monotonic_data(spo2_data)
		spo2_data = spo2_data['SPO2%']
		spo2_data.set_index('datetime', inplace=True)
<<<<<<< HEAD
		spo2_data.drop('posix', axis=1, inplace=True)
		spo2_data.rename(columns={'signal': 'spo2'}, inplace=True)
		# only select subset where AirGo:
		spo2_data = spo2_data.loc[airgo_data.index[0]: airgo_data.index[-1], :]
=======
		spo2_data.drop('posix',axis=1, inplace=True)
		spo2_data.rename(columns={'signal': 'spo2'}, inplace=True)
		# only select subset where AirGo:
		spo2_data = spo2_data.loc[airgo_data.index[0] : airgo_data.index[-1],:]
>>>>>>> 7df50e71c4295b81010916d223060dd5ec58bf82

		if spo2_data.shape[0] == 0:
			doc.loc[doc.study_id == study_id, 'code_successful'] = 1
			doc.loc[doc.study_id == study_id, 'bmr_available'] = 2
			continue

		# join and resample
		data = pd.concat([spo2_data, airgo_data], join='outer', axis=1, sort=True)
		data.spo2 = data.spo2.interpolate(method='pchip', order=3, limit_area='inside',
<<<<<<< HEAD
										  limit=None)

		data = data.loc[(1 - np.isnan(data.spo2.values)).astype('bool'), :]
		data['hypo_10_60_movavg8sec'] = data.hypo_10_60.rolling('8s').mean()
		data['hypo_10_60_movavg8sec'] = np.minimum(data['hypo_10_60_movavg8sec'].values,
												   np.ones(data['hypo_10_60_movavg8sec'].shape))
=======
								  limit=None)

		data = data.loc[(1- np.isnan(data.spo2.values)).astype('bool'),:]
		data['hypo_10_60_movavg8sec'] = data.hypo_10_60.rolling('8s').mean()
		data['hypo_10_60_movavg8sec'] = np.minimum(data['hypo_10_60_movavg8sec'].values,np.ones(data['hypo_10_60_movavg8sec'].shape))
>>>>>>> 7df50e71c4295b81010916d223060dd5ec58bf82

		lagrange = range(-9000, 9000, 10)
		# lagrange = range(-800, 0, 10)
		# print('tempsetting')
		# idx_start = 380000
		# idx_end = 400000

		searchrange = range(0, data.shape[0] - 5001, 5000)
		# searchrange = range(380000, data.shape[0] - 5001, 5000)

		maxspearman = []
		maxpearson = []

<<<<<<< HEAD
		for [i, idx_start] in enumerate(searchrange):
			# if i > 50: continue

=======

		for [i, idx_start] in enumerate(searchrange):
			if i > 50: continue
			
>>>>>>> 7df50e71c4295b81010916d223060dd5ec58bf82
			spearman = []
			# pearson = []
			idx_end = idx_start + 20000

			for lag in lagrange:
				hypo = pd.Series(np.diff(data.hypo_10_60_movavg8sec.iloc[idx_start:idx_end]))
				spo2 = pd.Series(np.diff(data.spo2.iloc[idx_start - lag:idx_end - lag]))
				spearman.append(spo2.corr(hypo, method='spearman'))
<<<<<<< HEAD
			# pearson.append(spo2.corr(hypo, method='pearson'))
=======
				# pearson.append(spo2.corr(hypo, method='pearson'))
>>>>>>> 7df50e71c4295b81010916d223060dd5ec58bf82

			maxspearman.append(lagrange[np.argmax(spearman)] / 10)

		maxspearman = np.array(maxspearman)
<<<<<<< HEAD
		counts, lag = np.histogram(maxspearman, len(lagrange) // 2)
=======
		counts, lag = np.histogram(maxspearman, len(lagrange)//2)
>>>>>>> 7df50e71c4295b81010916d223060dd5ec58bf82
		# print(counts)
		local_max = find_peaks(counts, distance=5)[0]
		local_max_lag = lag[local_max]
		local_max_count = counts[local_max]
		print(local_max_count)
		idx_candidates = np.argsort(local_max_count)[::-1][:3]

		for ic, candidate_idx in enumerate(idx_candidates):
<<<<<<< HEAD
=======

>>>>>>> 7df50e71c4295b81010916d223060dd5ec58bf82
			lag_best_correlation = local_max_lag[candidate_idx]
			# here, we got the lag that maximizes correlation to hypopnea indication curve.
			# however, hypopnea indication curve might have a small lag (last 10 sec / last 60sec)
			# then, we take the 8sec moving average of hypopnea indication curve to compute the correlation.
			# next, there is a approximate 30second time delay of actual blood desaturation and
			# when it is visible in the pulse oximeter at the fingertip.
			# therefore -8seconds lag for 'technical' issues and +30seconds lag for physiological lag.
			# results in +24 seconds lag in total.

			# print(lag_best_correlation)
			lag_correction = int(np.round(lag_best_correlation)) + 24
<<<<<<< HEAD
			print(lag_correction)
			doc.loc[doc.study_id == int(study_id), 'TS_auto' + str(int(ic + 1))] = lag_correction
=======
			# print(lag_correction)
			doc.loc[doc.study_id == study_id, 'TS_auto' +str(int(ic+1))] = lag_correction
>>>>>>> 7df50e71c4295b81010916d223060dd5ec58bf82
			# doc.loc[doc.study_id == study_id, 'TS_auto2'] = idx_candidates[1]
			# doc.loc[doc.study_id == study_id, 'TS_auto3'] = idx_candidates[2]
			doc.loc[doc.study_id == study_id, 'code_successful'] = 1

		doc.to_csv(doc_path, index=False)
<<<<<<< HEAD
		doc.to_csv(str(study_id) + '_timealignment_airgobmr.csv', index=False)
=======
		doc.to_csv(str(study_id)+'_timealignment_airgobmr.csv', index=False)
>>>>>>> 7df50e71c4295b81010916d223060dd5ec58bf82

	except Exception as e:
		doc.loc[doc.study_id == study_id, 'code_successful'] = 0
		print(e)
		continue