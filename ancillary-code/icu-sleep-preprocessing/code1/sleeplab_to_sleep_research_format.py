import pandas as pd
import numpy as np
import h5py
import os
import matplotlib.pyplot as plt
import import_ipynb
import sys
sys.path.append('C:/Users/wg984/Wolfgang/repos/sleep_research_io')
from sleep_research_functions import sleeplab_to_sleep_research_format, index_to_datetime_sleepdata, load_sleep_data, write_to_hdf5_file
from tqdm import tqdm

# airgo_dir = 'C:/Users/wg984/Dropbox (Partners HealthCare)/AirGoSleepLabData/ShareWithDavidKuller/AirGo_PSG_TimeAligned/AirGo_Files_FormatBB/'
airgo_dir = 'M:/Projects/AirGo_PSG/AirGo_PSG_TimeAligned_SleepStageOnly/AirGo_Files'

psg_dir = 'C:/Users/wg984/Dropbox (Partners HealthCare)/AirGoSleepLabData/ShareWithDavidKuller/AirGo_PSG_TimeAligned/PSG_Files/'
annotations_dir = 'C:/Users/wg984/Dropbox (Partners HealthCare)/AirGoSleepLabData/ShareWithDavidKuller/AirGo_PSG_TimeAligned/Annotations/'

psg_dir = 'M:/Projects/AirGoSleepStaging/TimeAlignedDataNew/PSG_Files/'
masterlist_path = 'C:/Users/wg984/Dropbox (Partners HealthCare)/AirGoSleepLabData/MasterList_Main_1.23.20.csv'
output_dir = 'M:/Projects/AirGo_PSG/10Hz_data'

masterlist = pd.read_csv(masterlist_path)
masterlist = masterlist[masterlist.IncludedInStudy==1]
studyids_to_process = masterlist.SID.apply(lambda x: x.split('Air')[1]).values

for study_id in tqdm(studyids_to_process):

	# print(study_id)
	# try:
	if 1:

		output_h5_path = os.path.join(output_dir, 'psg_airgo_10hz_' + study_id + '.h5')
		if os.path.exists(output_h5_path): continue

		# load AirGo
		airgo = pd.read_csv(os.path.join(airgo_dir, 'AirGo_'+study_id+'.csv'))
		airgo.DateTime = pd.to_datetime(airgo.DateTime)

		if 'CRCStatus' in airgo.columns:
			airgo = airgo[pd.isna(airgo.CRCStatus)]
			airgo.drop('CRCStatus', axis=1, inplace=True)
		if 'Unnamed: 0' in airgo.columns:
			airgo.drop('Unnamed: 0', axis=1, inplace=True)

		airgo.drop_duplicates(subset='DateTime', inplace=True)
		airgo.set_index('DateTime', inplace=True)

		# load PSG
		psg = pd.read_csv(os.path.join(psg_dir, 'PSG_Air'+study_id+'_10Hz.csv'))
		psg.DateTime = pd.to_datetime(psg.DateTime)
		psg.set_index('DateTime', inplace=True)

		# load annotation and create datetime array::
		annotation = pd.read_csv(os.path.join(annotations_dir,'annotations_' + 'Air'+study_id+'.csv'))

		time1 = pd.to_datetime(annotation.time, format = '%H:%M:%S')
		before_midnight = np.where(time1.apply(lambda x: x.hour>12))[0]
		assert([0] in before_midnight)
		before_midnight = before_midnight.shape[0]
		after_midnight = time1.shape[0]-before_midnight
		before_midnight = [str(psg.iloc[0].name.date())]*before_midnight
		after_midnight = [str(psg.iloc[-1].name.date())]*after_midnight
		date_array = before_midnight + after_midnight

		annotation.time = pd.to_datetime([x[0] +' ' + x[1] for x in list(zip(date_array, annotation.time))], format='%Y-%m-%d %H:%M:%S')
		annotation.drop('epoch', axis=1,inplace=True)
		# annotation.drop('Epoch', axis=1,inplace=True)

		for iPotentialDuplicateRound in range(1,9):
		    if sum(annotation.time.duplicated()) == 0: break
		    new_time = np.array([x.replace(microsecond=iPotentialDuplicateRound*100000) for x in annotation.time[annotation.time.duplicated()]])
		    if new_time.shape[0]==1:
		        annotation.time[annotation.time.duplicated()] = new_time[0]
		    else:
		        annotation.time[annotation.time.duplicated()] = new_time
		assert sum(annotation.time.duplicated()) == 0, "Not all duplicates solved."

		if 'duration' in annotation.columns:
			annotation.drop('duration', axis=1, inplace=True)
		annotation.set_index('time', inplace=True)
		annotation.columns = ['Annotation']

		data = sleeplab_to_sleep_research_format(airgo, psg, annotation = annotation)

		hdr = {
	    'study_id': np.int32(study_id),
	    'MRN': np.int32(1),
	    'fs': np.int32(10),
	    'start_datetime': np.array([data.index[0].year,data.index[0].month,data.index[0].day, data.index[0].hour, data.index[0].minute, data.index[0].second, data.index[0].microsecond])
		}


		write_to_hdf5_file(data, output_h5_path , hdr = hdr)
	#
	# except Exception as e:
	# 	print(study_id)
	# 	print(e)