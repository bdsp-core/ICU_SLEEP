import numpy as np
import pandas as pd
import os
import sys
import h5py
import traceback
sys.path.append('/home/wolfgang/repos/sleep_research_io')
from sleep_research_functions import load_sleep_data, write_to_hdf5_file, get_metadata, read_in_routine
from HRV_and_CPC_analysis_functions import ecg_hrv_cpc_routine, cpc_routine, spectrum_plot_dt, cpc_and_signals_plot
from tqdm import tqdm
import matplotlib.pyplot as plt
from HRV_and_CPC_analysis_functions import load_ecg_data

def main():


	# print('sleep 6 hours')
	import time
	# time.sleep(3600*6)

	do_plots = 1
	redo_cpc = 1
	print(f'redo_cpc option is set to : {redo_cpc}')
	# redo_cpc if 1: assume it ecg peak detection has been performed before already.
	# and we want to recompute cpc (changed code a bit). so, existing 10hz data with NN info
	# gets read in and cpc features/columns are newly computed, cpc_df gets newly saved.
	# default is 0, where ECG+CPC routine are carried out.

	# directories with ECGs and 10hz vital signs (containing respiration signal)
	ecg_dir = '/media/mad3/Projects/ICU_SLEEP_STUDY/data/data_analysis/BMR_resampled_ECG'
	vitals_dir = '/media/mad3/Projects/ICU_SLEEP_STUDY/Sleep_And_Breathing/icu_files_v2'

	# save folders:
	cpc_spectrograms_dir = '/media/mad3/Projects/ICU_SLEEP_STUDY/data/data_analysis/CPC_spectrograms'
	cpc_plots_dir = '/media/mad3/Projects/ICU_SLEEP_STUDY/data/data_analysis/CPC_plots'
	ecg_r_peak_dir = '/media/mad3/Projects/ICU_SLEEP_STUDY/data/data_analysis/BMR_resampled_ECG_and_rpeaks'
	vitals_hrv_dir = '/media/mad3/Projects/ICU_SLEEP_STUDY/Sleep_And_Breathing/icu_files_v2_hrv'

	if redo_cpc:
		vitals_dir = '/scr/wolfgang/Sleep_And_Breathing/icu_files_step5'
		# save folder
		vitals_hrv_dir = '/scr/wolfgang/Sleep_And_Breathing/icu_files_step5_2'

	if not os.path.exists(vitals_hrv_dir):
		os.makedirs(vitals_hrv_dir)

	# print quick summary of what files are available:
	ecg_files_available = os.listdir(ecg_dir)
	vitals_files_available = os.listdir(vitals_dir)
	vitals_files_available = [x.replace('icusleep_', '').replace('.h5','') for x in vitals_files_available]
	ecg_files_available = [x.replace('ECG_', '').replace('.h5','') for x in ecg_files_available]

	vitals_but_no_ecg = list(set(vitals_files_available) - set(ecg_files_available))
	vitals_but_no_ecg.sort()
	print(f'10Hz vitals sign dataframe available but no ECG: {len(vitals_but_no_ecg)} files.')
	print(vitals_but_no_ecg)
	both_available = list(set(vitals_files_available).intersection(set(ecg_files_available)))
	print(f'\nBoth vitals and ECG available: {len(both_available)}')
	study_ids = both_available
	study_ids.sort()

	files_done = os.listdir(vitals_hrv_dir)
	study_ids_done = [x.replace('icusleep_', '').replace('.h5', '') for x in files_done]

	study_ids = list(set(study_ids) - set(study_ids_done))
	study_ids.sort()
	print(f'\nTo Do: {len(study_ids)}')

	for study_id in tqdm(study_ids[1::2]):

		try:
			# savepaths for this study_id:
			cpc_spectrogram_path = os.path.join(cpc_spectrograms_dir, 'CPC_spectrogram_' + str(study_id).zfill(3) + '.csv')
			ecg_rpeak_path = os.path.join(ecg_r_peak_dir, 'ECG_' + str(study_id).zfill(3) + '.h5')
			vitals_hrv_path = os.path.join(vitals_hrv_dir, f'icusleep_{str(study_id).zfill(3)}.h5')

			if os.path.exists(vitals_hrv_path):
				print(f'{study_id} exists, continue.')
				continue

			print(study_id)

			path_ecg_data = os.path.join(ecg_dir, f'ECG_{study_id}.h5')
			path_vitals_data = os.path.join(vitals_dir, f'icusleep_{study_id}.h5')

			signals_contained_ecg = get_metadata(path_ecg_data)
			# print(signals_contained_ecg)
			signals_contained_vitals = get_metadata(path_vitals_data)

			if 0:
				print("DEBUGGING")
				fs = 240  # by default, after resampling
				data = load_ecg_data(path_ecg_data)

				leads = [x for x in data.keys() if '_startdatetime' not in x]
				assert leads[0] == 'I'
				ecg_lead = leads[0]
				signal_ecg_lead = pd.DataFrame(data[ecg_lead], columns=['signal'])
				signal_ecg_lead['signal'] = signal_ecg_lead['signal'] * 0.00243

				plt.figure(figsize=(10,6))
				plt.plot(signal_ecg_lead.signal)
				plt.show()

				plt.figure(figsize=(10,6))
				plt.plot(signal_ecg_lead.signal.iloc[:fs*3600])
				plt.savefig(str(study_id)+'_1.jpg')

				plt.figure(figsize=(10,6))
				plt.plot(signal_ecg_lead.signal.iloc[fs*3600:fs*7200])
				plt.savefig(str(study_id)+'_2.jpg')

				plt.figure(figsize=(10,6))
				plt.plot(signal_ecg_lead.signal.iloc[10000*fs:])
				plt.savefig(str(study_id)+'_3.jpg')

				plt.figure(figsize=(10,6))
				plt.plot(signal_ecg_lead.signal.iloc[fs*3500:fs*3600])
				plt.savefig(str(study_id)+'_4.jpg')

				plt.figure(figsize=(10,6))
				plt.plot(signal_ecg_lead.signal.iloc[10000*fs:10100*fs])
				plt.savefig(str(study_id)+'_5.jpg')

				continue

			if redo_cpc == 0:
				fs_hrv = 10
				hrv_10hz.rename({'signal' : 'ecg_signal'}, axis=1, inplace=True)
				hrv_10hz, signal_ecg_lead, cpc_df = ecg_hrv_cpc_routine(path_ecg_data, path_vitals_data, fs_hrv=fs_hrv, source='bedmaster')

			elif redo_cpc == 1:
				vitals_data, hdr, fs_hrv = read_in_routine(path_vitals_data)
				fs = fs_hrv
				vitals_data, cpc_df = cpc_routine(vitals_data, fs_hrv = fs_hrv)
				signal_ecg_lead = None
				hrv_10hz = None

			if redo_cpc == 0:
				try:

					start_idx = 240 * 30
					dur = 240 * 60
					if signal_ecg_lead.iloc[start_idx : start_idx + dur].shape[0] > 0:
						fig, ax = plt.subplots(2, 1, figsize=(14,9), sharex=True)
						ax[0].plot(signal_ecg_lead.signal.iloc[start_idx : start_idx + dur])
						r_peaks_loc = signal_ecg_lead.iloc[start_idx : start_idx + dur]
						r_peaks_loc = r_peaks_loc[r_peaks_loc.r_peak == 1].index
						ax[0].scatter(r_peaks_loc, signal_ecg_lead.loc[r_peaks_loc, 'signal'], color='r', s=5, zorder=3)
						ax[1].plot(signal_ecg_lead.sqi.iloc[start_idx : start_idx + dur])
						plt.savefig(f'./plots_peak_detection/{study_id}_1.jpg', dpi=400)

					start_idx = 240 * 60 * 50
					dur = 240 * 60
					if signal_ecg_lead.iloc[start_idx : start_idx + dur].shape[0] > 0:
						fig, ax = plt.subplots(2, 1, figsize=(14,9), sharex=True)
						ax[0].plot(signal_ecg_lead.signal.iloc[start_idx : start_idx + dur])
						r_peaks_loc = signal_ecg_lead.iloc[start_idx : start_idx + dur]
						r_peaks_loc = r_peaks_loc[r_peaks_loc.r_peak == 1].index
						ax[0].scatter(r_peaks_loc, signal_ecg_lead.loc[r_peaks_loc, 'signal'], color='r', s=5, zorder=3)
						ax[1].plot(signal_ecg_lead.sqi.iloc[start_idx : start_idx + dur])
						plt.savefig(f'./plots_peak_detection/{study_id}_2.jpg', dpi=400)

					start_idx = 240 * 30
					dur = 240 * 60 * 30
					if signal_ecg_lead.iloc[start_idx : start_idx + dur].shape[0] > 0:
						fig, ax = plt.subplots(2, 1, figsize=(14,9), sharex=True)
						ax[0].plot(signal_ecg_lead.signal.iloc[start_idx : start_idx + dur])
						r_peaks_loc = signal_ecg_lead.iloc[start_idx : start_idx + dur]
						r_peaks_loc = r_peaks_loc[r_peaks_loc.r_peak == 1].index
						ax[0].scatter(r_peaks_loc, signal_ecg_lead.loc[r_peaks_loc, 'signal'], color='r', s=5, zorder=3)
						ax[1].plot(signal_ecg_lead.sqi.iloc[start_idx : start_idx + dur])
						plt.savefig(f'./plots_peak_detection/{study_id}_3.jpg', dpi=500)

					plt.close('all')

				except Exception as e:
					print(e)
					print('plot failed.')

			# save CPC spectrograms in own folder:
			if not cpc_df is None:
				cpc_df.to_csv(cpc_spectrogram_path) # index: DateTime, columnnames: frequency.

			if not signal_ecg_lead is None:
				# save ECG and r peak detection:
				hdr = {}
				dt = signal_ecg_lead.index[0]
				hdr['start_datetime'] = np.array([dt.year, dt.month, dt.day,
						 dt.hour, dt.minute,
						 dt.second, dt.microsecond])
				hdr['study_id'] = int(study_id)
				hdr['fs'] = 240
				write_to_hdf5_file(signal_ecg_lead, ecg_rpeak_path, hdr = hdr, overwrite=True)

			if not hrv_10hz is None:

				# merge 10hz vitals data and hrv analysis results, save it:
				vitals_data, hdr, fs = read_in_routine(path_vitals_data)
				hrv_10hz.rename({'signal' : 'ecg_signal'}, axis=1, inplace=True)

				vitals_data = vitals_data.join(hrv_10hz, how='outer')
				write_to_hdf5_file(vitals_data, vitals_hrv_path, hdr = hdr, overwrite=True)

				if do_plots & (cpc_df is not None):

					resp = vitals_data['movavg_0_5s']
					hfc_lfc_ratio = hrv_10hz[['cpc_hfc_lfc_ratio']]
					fig = cpc_and_signals_plot(cpc_df, hfc_lfc_ratio, resp, hrv_10hz['nn'])
					fig.savefig(os.path.join(cpc_plots_dir, f'signals_cpc_{str(study_id).zfill(3)}.jpg'), dpi=300)
					fig.savefig(os.path.join(cpc_plots_dir, f'signals_cpc_{str(study_id).zfill(3)}.pdf'), dpi=300)
					fig = cpc_and_signals_plot(cpc_df, hfc_lfc_ratio)
					fig.savefig(os.path.join(cpc_plots_dir, f'cpc_{str(study_id).zfill(3)}.jpg'), dpi=300)
					fig.savefig(os.path.join(cpc_plots_dir, f'cpc_{str(study_id).zfill(3)}.pdf'), dpi=300)

					plt.close('all')

				del vitals_data, hrv_10hz, signal_ecg_lead, cpc_df

			if redo_cpc == 1:
				cols_to_drop = ['apnea_binary', 'apnea_end']
				for col_to_drop in cols_to_drop:
					if col_to_drop in vitals_data.columns:
						vitals_data.drop(col_to_drop, axis=1, inplace=True)

				write_to_hdf5_file(vitals_data, vitals_hrv_path, hdr=hdr, overwrite=True)

				if do_plots & (cpc_df is not None):

					resp = vitals_data['movavg_0_5s']
					hfc_lfc_ratio = vitals_data[['cpc_hfc_lfc_ratio']]
					fig = cpc_and_signals_plot(cpc_df, hfc_lfc_ratio, resp, vitals_data['hrv_nn'])
					fig.savefig(os.path.join(cpc_plots_dir, f'signals_cpc_{str(study_id).zfill(3)}.jpg'), dpi=300)
					fig.savefig(os.path.join(cpc_plots_dir, f'signals_cpc_{str(study_id).zfill(3)}.pdf'), dpi=300)
					fig = cpc_and_signals_plot(cpc_df, hfc_lfc_ratio)
					fig.savefig(os.path.join(cpc_plots_dir, f'cpc_{str(study_id).zfill(3)}.jpg'), dpi=300)
					fig.savefig(os.path.join(cpc_plots_dir, f'cpc_{str(study_id).zfill(3)}.pdf'), dpi=300)

					plt.close('all')

				del vitals_data, hrv_10hz, signal_ecg_lead, cpc_df


		except Exception as e:
			print(e)
			print(''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)))
			continue


if __name__ == '__main__':
	main()
