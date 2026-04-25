import pandas as pd
import numpy as np
import os
import sys

sys.path.append('/home/wolfgang/repos/AirGo_Apnea_Detection')
from apnea_detection_functions import apply_apnea_prediction_models

sys.path.append('/home/wolfgang/repos/ICU-Sleep/code1')
from airgo_features import compute_airgo_features
from sleep_staging_functions import apply_airgo_sleep_staging_models

sys.path.append('/home/wolfgang/repos/sleep_research_io')
from sleep_research_functions import *
from sleep_analysis_functions import *
from edw_functions import * 

import matplotlib.pyplot as plt


def main():


	# import time
	# print('SLEEP 3 hours.')
	# time.sleep(60*60*3)
	# print('go!')

	data_dir = f'/media/ssd2/icu_final_files'
	output_dir = f'/media/mad3/Projects/ICU_SLEEP_STUDY/Sleep_And_Breathing/icu_files_v2'
	overwrite = False

	if not os.path.exists(output_dir):
		os.makedirs(output_dir)

	files = os.listdir(data_dir)
	files.sort()

	LIST = '/media/mad3/Projects/ICU_SLEEP_STUDY/data/data_analysis/ExportedReports/LIST.csv'
	LIST = pd.read_csv(LIST)
	LIST.dropna(subset=['MRN:'], inplace=True)
	LIST['study_id'] = LIST['Study ID:'].apply(lambda x: str(x).zfill(3))
	LIST['mrn'] = LIST['MRN:'].apply(lambda x: int(x))

	for file in files: # ['icusleep_004.h5']:

		study_id = file[-6:-3]

		if study_id == '004':
			continue # needs more RAM?

		mrn = LIST.loc[LIST.study_id==study_id, 'mrn'].values[0]
		input_file_path = os.path.join(data_dir, file)
		output_file_path = os.path.join(output_dir, file)

		if os.path.exists(output_file_path):
			continue

		print(file)
		data, hdr, fs  = read_in_routine(input_file_path, check_airgo_scaling=False)

		data_alt, hdr_alt = load_sleep_data(f'/media/ssd2/icu_breathing/{file}', idx_to_datetime=1)

		if 'band' in data_alt.columns:
			if data_alt.band.dropna().shape[0] > data.band.dropna().shape[0] + 30:

				if int(study_id) < 30:
					print('old/alternative data contains more airgo data. manual fix here. happened to some v14 airgo recordings...')
					data['band'] = data_alt['band'].values
					data['accx'] = data_alt['accx'].values	
					data['accy'] = data_alt['accy'].values	
					data['accz'] = data_alt['accz'].values	
				else:
					print('old/alternative data contains more airgo data for V15 arigo recording!')			

		del data_alt
		del hdr_alt
		data_alt = 0

		# use_mov_avg = False
		# # for some v4 files, there seems to be mov_avg but no 'band'. Manual fix here:
		# if ('band' not in data.columns) & ('movavg_0_5s' in data.columns):
		# 	use_mov_avg = True
		# if 'band' in data.columns:
		# 	if data.band.dropna().shape[0] == 0:
		# 		if 'movavg_0_5s' in data.columns:
		# 			if data.movavg_0_5s.dropna().shape[0] > 0:
		# 				use_mov_avg = True

		# if use_mov_avg:
		# 	print("'band' seems to be missing but mov_avg_0_5 is available, use that instead.")
		# 	data['band'] = data.movavg_0_5s.iloc[:,0] 

		# only keep original files:
		bm_signals = ['hr', 'spo2', 'nbps', 'nbpd', 'art1d', 'art1s', 'art2d', 'art2s']
		original_airgo_signals = ['band', 'accx', 'accy', 'accz']
		signals_to_keep = bm_signals + original_airgo_signals
		signals_to_keep = [x for x in signals_to_keep if x in data.columns]
		data = data[signals_to_keep]

		# print('TMP TODO:')
		# data = data.dropna(how='all')
		# data = data.iloc[int(fs*3600*24*3.3) : int(fs*3600*24*3.4),:]


		# if 'stage_pred_activity10sec' in data.columns:
		#     data.drop(['stage_pred_activity10sec'], axis=1, inplace=True)
		#     if 'stage_pred_vcomb1' in data.columns:
		#     	data.drop(['stage_pred_vcomb1'], axis=1, inplace=True)

		# if 'stage_pred_vcomb1' in data.columns:
		#     data.rename({'stage_pred_vcomb1': 'stage_pred_comb_breath_activity_1'}, axis=1, inplace=True)
		    

		# print(f"Apnea:                  {'apnea_pred_va_a3' in data.columns}")
		# print(f"Sleep Stage Breathing:  {'stage_pred_amendsumeffort' in data.columns}")
		# print(f"Sleep Stage Activity:   {'stage_pred_activity1sec' in data.columns}")
		# print(f"Sleep Stage Comb:       {'stage_pred_comb_breath_activity_1' in data.columns}")
		# print(f"Self Similarity:        {'self_similarity' in data.columns}")
		# print(f"Hypoxic Burden:         {'hypoxic_area' in data.columns}")
		# print(f"Oxygen Flow:            {'oxygen_flow_rate' in data.columns}")
		# print(f"Instability Index:      {'instability_index_30sec' in data.columns}")


		# if not (('stage_pred_amendsumeffort' in data.columns) & ('stage_pred_amendsumeffort' in data.columns) & ('stage_pred_comb_breath_activity_1' in data.columns)):
		#     # do sleep staging. check v4
		#     print('sleep staging...')

		############################
		# add the EDW data:

		vitals_path = '/media/mad3/Projects/ICU_SLEEP_STUDY/data/data_analysis/edw_data/edw_icu_sleep_2020_07_07_vitals.csv'
		oxygen_path = '/media/mad3/Projects/ICU_SLEEP_STUDY/data/data_analysis/edw_data/edw_icu_sleep_2020_07_07_oxygen.csv'
		labs_path = '/media/mad3/Projects/ICU_SLEEP_STUDY/data/data_analysis/edw_data/edw_icu_sleep_2020_07_07_labs.csv'

		# vitals:
		edw_vitals = get_vitals_single_mrn(vitals_path, mrn)
		edw_vitals.columns = ['edw_' + x for x in edw_vitals.columns]
		edw_vitals = edw_vitals.loc[data.index[0] - timedelta(hours=1.5):data.index[-1] + timedelta(hours=1.5)]
		edw_vitals = edw_vitals.asfreq('0.1S')
		data = data.join(edw_vitals, how='outer')

		# oxygen:
		edw_oxygen = get_edw_oxygen_single_mrn(oxygen_path, mrn)
		edw_oxygen = edw_oxygen.loc[data.index[0] - timedelta(hours=1.5):data.index[-1] + timedelta(hours=1.5)]

		columns_of_interest = ['oxygen_device', 'oxygen_flow_rate', 'positioning_frequency', 'repositioned']
		columns_of_interest_available = [x for x in columns_of_interest if x in edw_oxygen.columns]

		if len(columns_of_interest_available) > 0:
		    edw_oxygen = edw_oxygen[columns_of_interest_available]
		    edw_oxygen = edw_oxygen.asfreq('0.1S')
		    data = data.join(edw_oxygen, how='outer')

		# labs # TO BE CHECKED/TESTED TODO
		labs = get_labs_single_mrn(labs_path, mrn)
		labs = labs.loc[str(data.index[0]) : str(data.index[-1]),:]
		data = data.join(labs)

		int_labs = ['hco3_arterial', 'hco3_venous', 'pco2_arterial', 'pco2_venous', 'po2_arterial', 'po2_venous']
		for lab_tmp in int_labs:
		    data.loc[pd.isna(data[lab_tmp]), lab_tmp] = -1
		    data.loc[:, lab_tmp] = data[lab_tmp].round().astype(np.int32)

		############################
		# PERFORM ALGOS:

		fs_manual = 10
		do_resample_and_interpolation = False      # recommended for raw airgo, resampling to 'perfect 10Hz'
		do_compute_airgo_features = True           # all features. by default, complexity features are computed in this code which are the slowest but needed for apnea prediction.
		do_apply_sleep_staging_models = True       # respiration-only, actigraphy-only.
		do_apply_apnea_prediction_models = True    # respiration-only and respiration+spo2 models. if sleep_stage_available, sleep-only apnea versions get computed too.
		do_compute_self_similarity = True          # depends on airgo available
		do_compute_hypoxia_burden = True           # depends on apnea predictions and sleep stages (for hours of sleep)

		# import pdb; pdb.set_trace()

		if do_resample_and_interpolation:
		    data = airgo_resample_preprocess(data)

		if do_compute_airgo_features:
		    data = compute_airgo_features(data, fs=fs, complexity_features=1)

		if do_apply_sleep_staging_models:
		    
		    data = apply_airgo_sleep_staging_models(data, fs=fs)

		if do_apply_apnea_prediction_models:
		    data = apply_apnea_prediction_models(data, fs=fs)
		    
		if do_compute_self_similarity:
		    data = self_similarity_airgo(data)
		    
		if do_compute_hypoxia_burden:
		    
		    ### compute_hypoxia_burden params ###
		    apnea_name = 'apnea_pred_va_a3'  # name of Apnea info column
		    hours_sleep = 'stage_pred_amendsumeffort'  # name of sleep stage column, or int/float for manual setting.
		    hypoxia_name = 'hypoxic_area' + apnea_name.replace('apnea_pred', '')

		    data, hypoxia_burden = compute_hypoxia_burden(data, fs, apnea_name = apnea_name, 
		    	hypoxia_name=hypoxia_name, hours_sleep = hours_sleep)

		    ### compute_hypoxia_burden params ###

		    apnea_name = 'apnea_pred_ro_a3'  # name of Apnea info column
		    hours_sleep = 'stage_pred_amendsumeffort'  # name of sleep stage column, or int/float for manual setting.
		    hypoxia_name = 'hypoxic_area' + apnea_name.replace('apnea_pred', '')

		    data, hypoxia_burden = compute_hypoxia_burden(data, fs, apnea_name = apnea_name, 
		    	hypoxia_name=hypoxia_name, hours_sleep = hours_sleep)

		    apnea_name = 'apnea_pred_rsr_a3'  # name of Apnea info column
		    hours_sleep = 'stage_pred_amendsumeffort'  # name of sleep stage column, or int/float for manual setting.
		    hypoxia_name = 'hypoxic_area' + apnea_name.replace('apnea_pred', '')

		    data, hypoxia_burden = compute_hypoxia_burden(data, fs, apnea_name = apnea_name, 
		    	hypoxia_name=hypoxia_name, hours_sleep = hours_sleep)

		    apnea_name = 'apnea_pred_va_a3'  # name of Apnea info column
		    hours_sleep = 'stage_pred_amendsumeffort'  # name of sleep stage column, or int/float for manual setting.
		    hypoxia_name = 'hypoxic_area' + apnea_name.replace('apnea_pred', '')

		    data, hypoxia_burden = compute_hypoxia_burden(data, fs, apnea_name = apnea_name, 
		    	hypoxia_name=hypoxia_name, hours_sleep = hours_sleep)

		save_data_routine(data, output_file_path, hdr=hdr, overwrite=overwrite)




if __name__ == '__main__':
	main()