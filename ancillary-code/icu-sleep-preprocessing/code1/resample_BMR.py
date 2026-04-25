import numpy as np
import pandas as pd
import sys
sys.path.append("C:/Users/wg984/Wolfgang/repos/Bedmaster-ICU-tools/code/")
sys.path.append('/home/wolfgang/repos/Bedmaster-ICU-tools/code')
from research_bm_tools import BMR_load, BMR_plot, get_metadata
import datetime
import h5py
import os
import pytz

def main():
	study_ids_to_process = range(4,150) # [71]

	bedmaster_resample_waveforms(study_ids_to_process)


def bedmaster_resample_waveforms(study_ids_to_process=None, force_overwrite=0):
	print('bedmaster_resample_waveforms started.')

	# mad3drive = '/media/mad3/'
	mad3drive = 'M:/'
	bmr_studyid_dir = os.path.join(mad3drive, 'Projects/ICU_SLEEP_STUDY/data/data_analysis/BMR_studyID/')
	resampled_studyid_dir = os.path.join(mad3drive, 'Projects/ICU_SLEEP_STUDY/data/data_analysis/BMR_resampled/')

	bm_files = os.listdir(bmr_studyid_dir)
	new_fs = 240
	#interpolation gap limit considerations:
	# some frequencies are potentially 8x larger than slowest one. therefore, a limit of minimum 10 is considered for now.
	interpolation_gap_limit = 12 	# in samples, or None for no limit
	new_filename = 'BMR'

	if study_ids_to_process is not None: # only subset of study ids is processed.
		bm_files = ['BMR_'+str(int(x)).zfill(3)+'.h5' for x in study_ids_to_process]

	for bm_file in bm_files:
		try:
			print(bm_file)
			bm_filepath = os.path.join(bmr_studyid_dir, bm_file)
			output_h5_path = os.path.join(resampled_studyid_dir, bm_file.replace('BMR', new_filename))

			if bm_file.replace('BMR', new_filename) in os.listdir(resampled_studyid_dir) and not force_overwrite:
				continue  # if file already exists, code is not performed, unless force_overwrite is specified.
			if force_overwrite:  # then delete the file that already exists before writing on it.
				os.remove(output_h5_path)

			# what waveforms are in the file to resample:
			signals_in_bm_file = get_metadata(bm_filepath)
			waveform_signals = ['I','II','III', 'IIII','V','VI','VII','VIII','SPO2','CO2','ART1','ART2','RESP']
			# waveform_signals = ['I','SPO2']
			# print('temporary only a subset of signals')
			waveform_signals = [x for x in waveform_signals if x in signals_in_bm_file]
			# print(waveform_signals)

			data = BMR_load(bm_filepath, signals=waveform_signals, loadEvents=0)

			# TEMP
			# datetimeselection = '2019-04-16 23:00:00'
			# datetimeselection = pd.Timestamp(datetimeselection, tzinfo=(pytz.timezone('America/New_York')))
			# data = BMR_load(bm_filepath, signals=waveform_signals, loadEvents=0, DateTimeSelectionTZ = datetimeselection, hours_to_return = 1)

			# print(data['I'].head())
			# print(data['I'].dtypes)

			event = BMR_load(bm_filepath, signals=['I'], loadEvents=1)

			data = remove_non_monotonic_data(data)

			event['I'].drop(['signal'], axis=1, inplace=True)
			event = remove_non_monotonic_data(event, event_data=1)
			event['I'].rename(columns={'event': 'signal'}, inplace=True) # rename so that this array can be treated the same as signals.
			data['event'] = event['I']

			for signal in data.keys():

				data[signal].set_index('datetime', inplace=True)
				data[signal] = data[signal][['signal']]
				data[signal].columns = [signal]

			# join all the different waveform signals. creates NaN for signals with lower sampling rate.
			# print('temp print 1')
			data = [data[x] for x in data]
			data = pd.concat(data, join='outer', axis=1, sort=True)

			data_original_start = data.index[0]
			# resample merged data to new sampling rate
			data = data.resample(datetime.timedelta(seconds=1 / new_fs)).mean()
			# and interpolate, i.e. fills NaNs for lower sampled signals.
			data = data.interpolate(method='pchip', order=3, limit_area='inside',
									  limit=interpolation_gap_limit)  # limit can be used to not interpolate gaps. however, matlab cardiovascular toolbox does expect continuous data. therefore interpolate also gaps.
			data.loc[np.isnan(data['event']),'event'] = 10	# replace nan with 10 for event.
			data['event'] = data['event'].round().astype('int8')

			for signal in data.keys():

				datetime_array = np.array(
					[data_original_start.year, data_original_start.month, data_original_start.day,
					 data_original_start.hour, data_original_start.minute, data_original_start.second,
					 data_original_start.microsecond])

				chunk_size = 64

				if signal == 'event': # use int8 for event
					with h5py.File(output_h5_path, 'a') as f:
						dset = f.create_dataset(signal, shape=(data.shape[0],), maxshape=(None,),
												chunks=(chunk_size,), dtype='int8')
						dset[:] = data[signal].astype('int8')

				else:
					with h5py.File(output_h5_path, 'a') as f:
						dset = f.create_dataset(signal, shape=(data.shape[0],), maxshape=(None,),
													chunks=(chunk_size,), dtype='float32')
						dset[:] = data[signal].astype('float32')

						if not 'startdatetime' in f:
							dset_startdatetime = f.create_dataset('startdatetime', shape=datetime_array.shape,
																dtype='int32')
							dset_startdatetime[:] = datetime_array.astype('int32')

						if not 'fs' in f:
							dset_fs = f.create_dataset('fs', shape=(1,), dtype='int32')
							dset_fs[:] = np.array([new_fs]).astype('int32')

		except Exception as e:
			g = open("resample_BMR_errorlog.txt", "a")
			g.write('\n ' + str(bm_file))
			g.write(str(e))
			g.close()
			continue

def remove_non_monotonic_data(data, event_data=0):
	"""
	:param data:  BMR data as loaded from BMR_load() function
	:return: data before timestamp non-monotonicities gets removed so that result is monotonic.
	"""
	# find non-monotonicity points:
	# find datapoint after reset ('B')
	# find datapoint 'A' earlier than 'B' that satisfies 'A' < 'B'
	# remove data between A and B.

	for signalsel in data:
		idx_to_remove = []
		non_monoton_ind = np.where(np.diff(data[signalsel].posix) <= 0)[0] + 1
		for point_b_idx in non_monoton_ind:
			point_b_posix = data[signalsel].loc[point_b_idx].posix
			pre_b = data[signalsel].loc[point_b_idx - 30000:point_b_idx]['posix']
			point_a_idx = pre_b.index[pre_b < point_b_posix]
			if len(point_a_idx) == 0:
				# if not found in last 120 seconds (10000 samples, then look further :
				pre_b = data[signalsel].loc[point_b_idx - 5000000:point_b_idx]['posix']
				point_a_idx = pre_b.index[pre_b < point_b_posix]
			if len(point_a_idx) == 0:

				print('unexpected case, no point_a')
				# import pdb; pdb.set_trace()
				import pdb; pdb.set_trace()
				# print('UNEXPECTED. no point_a_idx in removing_non_monotonicity.')
				# raise ValueError
				# print('ToDo check ubuntu version...')
				continue

				point_a_idx = [0]
			# else:
			# 	# usual case
			point_a_idx = point_a_idx[-1]
			idx_to_remove += range(point_a_idx, point_b_idx)
		data[signalsel].drop(idx_to_remove, axis=0, inplace=True)

		if event_data:
			# mark point B's as 6 in event array. first do intersection with indices in case
			# some non-monotonic places have been removed in above procedure.
			non_monoton_ind = list(set(data[signalsel].index).intersection(set(non_monoton_ind)))
			data[signalsel].loc[non_monoton_ind, 'event'] = 6

	return data


if __name__ == '__main__':
	main()


