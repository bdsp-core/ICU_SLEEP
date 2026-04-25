import pandas as pd
import numpy as np
import h5py
import os
import import_ipynb
from datetime import timedelta
import sys
sys.path.append('C:/Users/wg984/Wolfgang/repos/sleep_research_io')
from sleep_research_functions import index_to_datetime_sleepdata, load_sleep_data, write_to_hdf5_file #, format_bm_airgo_to_10Hz_icusleep_data
sys.path.append('C:/Users/wg984/Wolfgang/repos/Bedmaster-ICU-tools/code')
from bmresearch_tools import BMR_load, get_metadata
from resample_BMR import remove_non_monotonic_data

def format_bm_airgo_to_10Hz_icusleep_data(bm_data, airgo_data):
    '''
    Input: AirGo and bedmaster data, original sampling rates.
    Output: 10Hz merged data, :='research format'
    '''
    data_list = [bm_data[signal_tmp] for signal_tmp in bm_data.keys()]
    data_list.append(airgo_data)
    data = pd.concat(data_list, join='outer', axis=1, sort=True)
    data = data.resample("0.1S").mean()

    for signal_tmp in bm_data.keys():
        data[signal_tmp] = data[signal_tmp].interpolate(method='pchip', order=3, limit_area='inside',
                              limit=50)
        data[signal_tmp + '_event'] = data[signal_tmp + '_event'].interpolate(method='pchip', order=3, limit_area='inside',
                              limit=50)

        data.loc[np.isnan(data[signal_tmp + '_event']), signal_tmp + '_event'] = 99 # replace nan with 99 because data gets saved as int in hdf5, nan not supported.

    return data
# limit considerations: 0.5Hz bedmaster to 10 Hz: for each datapoint, 19 NaNs.
# datagaps less than 5 seconds will be interpolated, if larger than 5 seconds, it is NaN. i.e. limit 50.


# load table containing time alignment information (offset to be applied)
tablefile = 'C:/Users/wg984/Wolfgang/repos/ICU-Sleep/data/bedmaster_airgo_timealignment.csv'
table = pd.read_csv(tablefile, sep=';')
table = table.dropna(subset=['TS_manual'])

# airgo features dir:
# airgo_features_dir = 'E:/Boston_MGH/ICU-Sleep/airgo_features/'
airgo_features_dir = 'M:/Projects/ICU_SLEEP_STUDY/data/data_analysis/AirGo/airgo_features/'
# bedmaster research dir
# bm_research_dir = 'E:/Boston_MGH/ICU-Sleep/bm_research/'
bm_research_dir = 'M:/Projects/ICU_SLEEP_STUDY/data/data_analysis/BMR_studyID/'
output_dir = 'M:/Projects/ICU_SLEEP_STUDY/data/data_analysis/biosignals_10Hz_data/'
output_dir_daynight = 'M:/Projects/ICU_SLEEP_STUDY/data/data_analysis/biosignals_10Hz_data_daynight/'

# get night id information:
data_partitions_id = 'M:/Projects/ICU_SLEEP_STUDY/data/data_analysis/Study/data_partitions_id.csv'
data_partitions_id = pd.read_csv(data_partitions_id)
data_partitions_id

for study_id in range(1,190): # [76, 155, 158, 185]: # range(1, 190):

	print(study_id)

	if os.path.exists(os.path.join(output_dir, 'icusleep_' + str(study_id).zfill(3) + '.h5')):
		print('already exists. continue.')
		continue

	# try:
	if 1:

		if table.loc[table.study_id == study_id, 'TS_manual'].shape[0] == 0:
			print('No timeshift in tablefile. continue')
			continue

		time_offset_to_be_applied = int(
			table.loc[table.study_id == study_id, 'TS_manual'].values[0])  # -60*60*24*3 # in seconds

		# load AirGo
		airgo_data = pd.read_csv(os.path.join(airgo_features_dir, 'airgo_' + str(study_id).zfill(3)) + '.csv')
		airgo_data.datetime = pd.to_datetime(airgo_data.datetime, infer_datetime_format=1)
		airgo_data.set_index('datetime', inplace=True)
		airgo_data.drop('crcstatus', axis=1, inplace=True)

		# load bedmaster data
		bmr_file = os.path.join(bm_research_dir, 'BMR_' + str(study_id).zfill(3) + '.h5')
		signals_in_bm_file = get_metadata(bmr_file)
		signals_to_load = ['NBPD', 'NBPS', 'HR', 'SPO2%', 'ART1S', 'ART1D', 'CUFF']
		signals_to_load = [x for x in signals_to_load if x in signals_in_bm_file]
		bm_data = BMR_load(bmr_file, signals=signals_to_load, loadEvents=1)

		bm_data = remove_non_monotonic_data(bm_data)

		for signal_tmp in signals_to_load:
			bm_data[signal_tmp].set_index('datetime', inplace=True)
			bm_data[signal_tmp].drop('posix', inplace=True, axis=1)
			bm_data[signal_tmp].rename(columns={'signal': signal_tmp}, inplace=True)
			bm_data[signal_tmp].rename(columns={'event': signal_tmp + '_event'}, inplace=True)

		#     # select only data from min(enrollment_day, first_cam_day) until last_cam_day+1 midnight.
		#     datetime_start =
		#     datetime_end =
		#     bm_data[signal_tmp] = bm_data[signal_tmp].loc[datetime_start : datetime_end,:]

		# remove duplicate indices if still occuring:
		for signal in bm_data.keys():
			num_of_duplicates = bm_data[signal].index.duplicated().sum()
			bm_data[signal] = bm_data[signal].loc[~bm_data[signal].index.duplicated(keep='first')]

			if num_of_duplicates > 0:
				print(f' bedmaster data still contains duplicated indices before resampling. simply drop them.'
					  f' # of duplicates = {num_of_duplicates}.')


		if 1:  # correct AirGo time so that it aligns with bedmaster
			airgo_data.index = airgo_data.index - timedelta(seconds=time_offset_to_be_applied)

			# somehow index can still have duplicates. if just a small number, drop the indices.
			if airgo_data.index.duplicated().sum() < 10:
				airgo_data = airgo_data.loc[~airgo_data.index.duplicated(keep='first')]

			else:
				raise ValueError('>10 duplicates in AirGo signal. To check.')

		data = format_bm_airgo_to_10Hz_icusleep_data(bm_data, airgo_data)

		hdr = {
			'study_id': np.int32(study_id),
			'MRN': np.int32(1),
			'fs': np.int32(10),
			'start_datetime': np.array(
				[data.index[0].year, data.index[0].month, data.index[0].day, data.index[0].hour, data.index[0].minute,
				 data.index[0].second, data.index[0].microsecond])
		}

		output_h5_path = os.path.join(output_dir, 'icusleep_' + str(study_id).zfill(3) + '.h5')
		# save full data of study_id:
		write_to_hdf5_file(data, output_h5_path, hdr=hdr)

		# save night/day partitions
		partitions_studyid = data_partitions_id.loc[data_partitions_id.study_id == study_id]

		for irow in range(partitions_studyid.shape[0]):

			# get start and end datetime for selected day_night:
			di = partitions_studyid.iloc[irow].copy()
			start = pd.to_datetime(di.date, infer_datetime_format=1)
			if di.day_night == 'day':
				start = start.replace(hour=8)
			elif di.day_night == 'night':
				start = start.replace(hour=20)
			end = start + timedelta(hours=12)

			# save the datetime-selected data with day_night_id name info:
			output_h5_path = f'icusleep_{di.id}.h5'
			output_h5_path = os.path.join(output_dir_daynight, output_h5_path)

			hdr = {
				'study_id': np.int32(study_id),
				'MRN': np.int32(1),
				'fs': np.int32(10),
				'start_datetime': np.array(
					[data.loc[start:end].index[0].year, data.loc[start:end].index[0].month, start.day,
					 data.loc[start:end].index[0].hour, data.loc[start:end].index[0].minute,
					 data.loc[start:end].index[0].second, data.loc[start:end].index[0].microsecond]),
				'day_night_id': di.id}

			write_to_hdf5_file(data.loc[start:end], output_h5_path, hdr=hdr)

	# except Exception as e:
	# 	print(e)


