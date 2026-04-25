import numpy as np
import pandas as pd
import sys
sys.path.append("C:/Users/wg984/Wolfgang/repos/Bedmaster-ICU-tools/code/")
sys.path.append("/home/wolfgang/repos/Bedmaster-ICU-tools/code/")
from research_bm_tools import BMR_load, BMR_plot, get_metadata
import datetime
import h5py
import os
import traceback
import time
import psutil
import matplotlib.pyplot as plt
import re

def main():

	mad3drive = '/media/mad3/'
	bmr_studyid_dir = os.path.join(mad3drive, 'Projects/ICU_SLEEP_STUDY/data/data_analysis/BMR_studyID/')
	ecg_studyid_dir = os.path.join(mad3drive, 'Projects/ICU_SLEEP_STUDY/data/data_analysis/BMR_resampled_ECG/')

	bm_files = os.listdir(bmr_studyid_dir)
	bm_files.sort()
	start_file = 0
	end_file = 12
	print(f'[{start_file} : {end_file}]')
	check_ram = True
	print(f'check_ram is set to {check_ram}')
	# import time
	# print('Sleep 4 hours.')
	# time.sleep(3600*4)


	#### START TEMPORARY 1
	#### For some files that failed with ECG lead I, we'll run again with ECG lead II (see in the main code below).
	#### To identify the files that need to run with ecg lead II, check what files are missing from 'final state':

	# directories with ECGs and 10hz vital signs (containing respiration signal)
	ecg_dir = '/media/mad3/Projects/ICU_SLEEP_STUDY/data/data_analysis/BMR_resampled_ECG'
	vitals_dir = '/media/mad3/Projects/ICU_SLEEP_STUDY/Sleep_And_Breathing/icu_files_v2'

	# save folders:
	cpc_spectrograms_dir = '/media/mad3/Projects/ICU_SLEEP_STUDY/data/data_analysis/CPC_spectrograms'
	vitals_hrv_dir = '/media/mad3/Projects/ICU_SLEEP_STUDY/Sleep_And_Breathing/icu_files_v2_hrv'

	# print quick summary of what files are available:
	ecg_files_available = os.listdir(ecg_dir)
	vitals_files_available = os.listdir(vitals_dir)
	vitals_files_available = [x.replace('icusleep_', '').replace('.h5','') for x in vitals_files_available]
	ecg_files_available = [x.replace('ECG_', '').replace('.h5','') for x in ecg_files_available]

	study_ids = list(set(vitals_files_available).intersection(set(ecg_files_available)))
	study_ids.sort()

	files_done = os.listdir(vitals_hrv_dir)
	study_ids_done = [x.replace('icusleep_', '').replace('.h5', '') for x in files_done]

	study_ids = list(set(study_ids) - set(study_ids_done))
	study_ids.sort()
	print(f'\nTo Do: {len(study_ids)}')

	bm_files = [x for x in bm_files if np.any([y in x for y in study_ids])]
	print(len(bm_files))
	#### END TEMPORARY 1


	for bm_file in bm_files[start_file:end_file]:
		print(bm_file)
		try:
			bm_filepath = os.path.join(bmr_studyid_dir, bm_file)
			output_h5_path = os.path.join(ecg_studyid_dir, bm_file.replace('BMR','ECG'))
			# if os.path.exists(output_h5_path):
			# 	print('exists. continue')
			# 	continue

			if check_ram == True:
				while psutil.virtual_memory().percent > 60:
					print(f'Current RAM usage: {psutil.virtual_memory().percent}. Sleep until more memory is available.')
					time.sleep(60*10)
				# do the resampling for this subject:
				resample_ecg(bm_filepath, output_h5_path, check_ram=check_ram)

		except Exception as e:
			print(e)
			print(''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)))
			continue



def resample_ecg(bm_filepath, output_h5_path, check_ram=False):

	signals_in_bm_file = get_metadata(bm_filepath)
	print(signals_in_bm_file)
	ekg_leads = ['I','II','III', 'IIII','V','VI','VII','VIII']
	ekg_leads = [x for x in ekg_leads if x in signals_in_bm_file]
	new_fs = 240
	# resample and save bedmaster ecg data for each lead:
	print(bm_filepath)
	study_id = re.search(r'\d\d\d', bm_filepath)[0]
	print(study_id)

	for lead in ['II']: # ekg_leads:
		# load the data:
		print('Load data')
		lead_data = BMR_load(bm_filepath, signals = [lead], loadEvents=0)
		print('Done.')

		lead_data = lead_data[lead]
		lead_data = lead_data

		# resample to 240Hz:
		lead_data.set_index('datetime', inplace=True)
		lead_data = lead_data[['signal']].astype(np.float32)
		lead_data_original_start = lead_data.index[0]

		if 1:
			plt.figure(figsize=(10, 6))
			plt.plot(lead_data.signal)
			plt.savefig('lead_II_' + str(study_id) + '_1.jpg', dpi = 300)
			plt.close()

			plt.figure(figsize=(10, 6))
			plt.plot(lead_data.signal.iloc[3600*new_fs: 3620*new_fs])
			plt.savefig('lead_II_' + str(study_id) + '_2.jpg', dpi=300)
			plt.close()

			plt.figure(figsize=(10, 6))
			plt.plot(lead_data.signal.iloc[7200*new_fs: 7220*new_fs])
			plt.savefig('lead_II_' + str(study_id) + '_3.jpg', dpi=300)
			plt.close()
			# plt.show()

		if 0:
			to_continue = input('Good quality, to continue? 1 or 0')
			if to_continue == 0:
				print('No further computation is performed for this data.')
				return

		print(f'Date Range: {lead_data.index[0]} : {lead_data.index[-1]}, SampleNo: {lead_data.shape[0]}')
		print('Resample...')
		lead_data = lead_data.resample(datetime.timedelta(seconds = 1/new_fs)).mean()
		print('Done.')
		# lead_data_resampled_start = lead_data.index[0]
		# difference_start = lead_data_original_start - lead_data_resampled_start
		if check_ram == True:
			while psutil.virtual_memory().percent > 50:
				print(f'Current RAM usage: {psutil.virtual_memory().percent}. Sleep until more memory is available.')
				time.sleep(60 * 10)

		print('Interpolate...')
		parts = np.max([lead_data.shape[0] // (new_fs * 3600 * 2), 1])
		part_len = lead_data.shape[0] // parts
		print(f'Split data into {parts+1} w/ part_len {part_len}.')
		for ipart in range(parts):
			a = time.time()
			lead_data.iloc[ipart * part_len: (ipart + 1) * part_len] = lead_data.iloc[ipart * part_len : (ipart + 1) * part_len].interpolate(method='pchip', order=3)
			print(f'Part {ipart} done. Comp. Time (seconds): {np.round(time.time() - a)}')

		# lead_data = lead_data.interpolate(method='pchip', order =3)   #  limit = 4. limit can be used to not interpolate gaps. however, matlab cardiovascular toolbox does expect continuous data. therefore interpolate also gaps.
		print('Done.')
		# lead_data.index = lead_data.index + difference_start
		datetime_array = np.array([lead_data_original_start.year, lead_data_original_start.month, lead_data_original_start.day, lead_data_original_start.hour, lead_data_original_start.minute, lead_data_original_start.second, lead_data_original_start.microsecond])

		# and save:
		chunk_size = 64
		chunk_size_fs = 1
		with h5py.File(output_h5_path, 'a') as f:
			dset_ekg = f.create_dataset(lead, shape=(lead_data.shape[0],), maxshape=(None,),
										chunks=(chunk_size,), dtype='float64')
			dset_ekg[:] = lead_data.signal.astype('float64')

			dset_startdatetime = f.create_dataset(lead + '_startdatetime', shape=datetime_array.shape, maxshape=(None,),
												  chunks=(chunk_size,), dtype='int64')
			dset_startdatetime[:] = datetime_array.astype('int64')

			dset_fs = f.create_dataset(lead + '_fs', shape=(1,), maxshape=(1,),
									   chunks=(chunk_size_fs,), dtype='int64')
			dset_fs[:] = np.array([new_fs]).astype('int64')


def resample_all_waveforms(bm_filepath, output_h5_path):

	signals_in_bm_file = get_metadata(bm_filepath)
	wv_signals = ['I','II','III', 'IIII','V','VI','VII','VIII','SPO2','CO2','ART1','ART2','RESP']
	wv_signals = [x for x in wv_signals if x in signals_in_bm_file]
	new_fs = 240
	# resample and save bedmaster ecg data for each lead:

	for lead in wv_signals:
		# load the data:
		lead_data = BMR_load(bm_filepath, signals = lead, loadEvents=0)
		lead_data = lead_data[lead]
		# resample to 240Hz:
		lead_data.set_index('datetime', inplace=True)
		lead_data = lead_data[['signal']]
		lead_data_original_start = lead_data.index[0]
		lead_data = lead_data.resample(datetime.timedelta(seconds = 1/new_fs)).mean()
		# lead_data_resampled_start = lead_data.index[0]
		# difference_start = lead_data_original_start - lead_data_resampled_start
		lead_data = lead_data.interpolate(method='pchip', order =3)   #  limit = 4. limit can be used to not interpolate gaps. however, matlab cardiovascular toolbox does expect continuous data. therefore interpolate also gaps.
		# lead_data.index = lead_data.index + difference_start
		datetime_array = np.array([lead_data_original_start.year, lead_data_original_start.month, lead_data_original_start.day, lead_data_original_start.hour, lead_data_original_start.minute, lead_data_original_start.second, lead_data_original_start.microsecond])

		# and save:
		chunk_size = 64
		with h5py.File(output_h5_path, 'a') as f:
			dset_ekg = f.create_dataset(lead, shape=(lead_data.shape[0],), maxshape=(None,),
										chunks=(chunk_size,), dtype='float64')
			dset_ekg[:] = lead_data.signal.astype('float64')

			dset_startdatetime = f.create_dataset(lead + '_startdatetime', shape=datetime_array.shape, maxshape=(None,),
												  chunks=(chunk_size,), dtype='int64')
			dset_startdatetime[:] = datetime_array.astype('int64')

			dset_fs = f.create_dataset(lead + '_fs', shape=(1,), maxshape=(1,),
									   chunks=(chunk_size,), dtype='int64')
			dset_fs[:] = np.array([new_fs]).astype('int64')



if __name__ == '__main__':
	main()
