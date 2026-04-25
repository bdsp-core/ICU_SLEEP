import sys
sys.path.append('C:/Users/wg984/Wolfgang/repos/Bedmaster-ICU-tools/code')

# %matplotlib widget

import matplotlib 
matplotlib.use('TKAgg')

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

import numpy as np
import pandas as pd
import pickle
from EDW_data import *
from matplotlib.dates import DateFormatter
from pandas.plotting import register_matplotlib_converters

register_matplotlib_converters()

import os
from bmresearch_tools import *
from datetime import timedelta

###
bmr_studyid_dir = '//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/data_analysis/BMR_studyID/'
airgo_research_dir = '//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/data_analysis/AirGo/airgo_research/'

plot_savepath = 'C:/Users/wg984/Dropbox (Partners HealthCare)/ICU-SLEEP-MATERIALS/PlottingData/EDW_Bedmaster_Airgo_Plots/OnlyICU'

patientclass_folder = 'M:/Projects/ICU_SLEEP_STUDY/data/data_analysis/patient_class/'
patient_object_fname = os.path.join(patientclass_folder,'patient_objects_08282019.pickle') # for all subjects <= 135
patient_object_fname2 = os.path.join(patientclass_folder,'patient_objects_12142019.p') # for all subjects >= 136
patient_object_fname3 = os.path.join(patientclass_folder,'patient_objects_02102019.p') # for subject 187, 188, 189

# study table including cam dates:
tablefile = 'M:/Projects/ICU_SLEEP_STUDY/data/data_analysis/Study/ICUSleep_DataTable_ICUonly.csv'
table= pd.read_csv(tablefile)

study_id_list = range(1,190)
# study_id_list = range(80,190)

# errors occured:
# study_id_list = [31, 39]
# study_id_list = [138]
study_id_list = list(range(1, 95)) + list(range(100, 190))
#
study_id_list = range(1, 190)


# study_id_list  = [3, 8, 15, 16, 18, 25, 27, 36, 43, 44, 45, 47, 64, 67, 68, 71, 163, 168, 185, 187]
study_id_list  = [43, 44, 45, 47, 64, 67, 68, 71, 163, 168, 185]
study_id_list = [2, 4, 5, 12, 16, 23, 25, 28, 31, 33, 41, 49, 64, 70, 71, 92, 100, 106, 113, 116, 137, 147, 150, 163, 170, 174, 185]

study_id_list = [76, 99, 146, 155]

for studyID in study_id_list:
	print(studyID)
	try:
	# if 1:

		# get EDW data:
		if studyID < 136:
			with open(patient_object_fname, "rb") as f:
				patient_object_list = pickle.load(f)
		elif studyID < 187:
			with open(patient_object_fname2, "rb") as f:
				patient_object_list = pickle.load(f)
		elif studyID < 190:
			with open(patient_object_fname3, "rb") as f:
				patient_object_list = pickle.load(f)

		# edw selection:
		id_list = [patient_object_list[x].ID for x in range(len(patient_object_list))]

		ididx = id_list.index(str(studyID).zfill(3))
		# ididx = id_list.index(str(185).zfill(3))

		edw_subject = patient_object_list[ididx]

		# get bedmaster data:
		bmr_file = os.path.join(bmr_studyid_dir,'BMR_'+ (str(studyID).zfill(3) +'.h5'))
		bmr_exists = os.path.exists(bmr_file)

		airgo_file = os.path.join(airgo_research_dir, 'airgo_' + (str(studyID).zfill(3) + '.csv'))
		airgo_exists = os.path.exists(airgo_file)

		# table
		table_studyid = table[table.StudyID == studyID]
		transferin = pd.to_datetime(pd.unique(table_studyid.ADT_TransferIn), infer_datetime_format=1)
		transferout = pd.to_datetime(pd.unique(table_studyid.ADT_TransferOut), infer_datetime_format=1)
		cam_dates = pd.to_datetime(table_studyid.CAM_Date.values, infer_datetime_format=1)
		admission = pd.to_datetime(table_studyid.ADT_Admission, infer_datetime_format=1)
		discharge = pd.to_datetime(table_studyid.ADT_Discharge, infer_datetime_format=1)

		# create figure:
		fig, ax = plt.subplots(4, 1, figsize=(30, 15), sharex=True)

		# blood bedmaster data if available:
		if bmr_exists:

			signals_in_bm_file = get_metadata(bmr_file)
			signals_to_load = ['NBPD','NBPS','HR','SPO2%','ART1S','ART1D']
			# waveform_signals = ['I','SPO2']
			# print('temporary only a subset of signals')
			signals_to_load = [x for x in signals_to_load if x in signals_in_bm_file]

			data = BMR_load(bmr_file, signals=signals_to_load)

			# add nans to gaps larger than 5 minutes
			for signal_tmp in signals_to_load:
				data[signal_tmp].drop('posix', axis=1, inplace=True)
				data[signal_tmp] = data[signal_tmp].reset_index()

				IdxLargeTimeDif = np.where(data[signal_tmp].datetime.diff() > timedelta(hours=0.1))[0] - 1
				for idx in IdxLargeTimeDif:
					DataLargeTimeDif = data[signal_tmp].iloc[idx, :]
					NaNData = pd.DataFrame([[None, DataLargeTimeDif.datetime + timedelta(seconds=1)]],
										   columns=['signal', 'datetime'])
					data[signal_tmp] = data[signal_tmp].append(NaNData, ignore_index=False, sort=False)

				data[signal_tmp].sort_values(by=['datetime'], inplace=True)



			if 'NBPS' in signals_to_load:
				if data['NBPS'].signal.shape[0] == 0:
					maxBP=100
				else:
					maxBP = max(data['NBPS'].signal)
			elif 'ART1S' in signals_to_load:
				maxBP = max(data['ART1S'].signal)
			else:
				maxBP = 140

			if 'HR' in signals_to_load:
				if data['HR'].signal.shape[0] == 0:
					maxHR=120
				else:
					maxHR = max(data['HR'].signal)
			else:
				maxHR = 120

			if 'NBPS' in signals_to_load:
				ax[0].plot(data['NBPS'].datetime, data['NBPS'].signal, linewidth=1, c = 'orange', linestyle='--')
			if 'ART1S' in signals_to_load:
				ax[0].plot(data['ART1S'].datetime, data['ART1S'].signal, linewidth=1, c='orange')
			if 'NBPD' in signals_to_load:
				ax[0].plot(data['NBPD'].datetime, data['NBPD'].signal, linewidth=1, c = 'magenta', linestyle='--')
			if 'ART1D' in signals_to_load:
				ax[0].plot(data['ART1D'].datetime, data['ART1D'].signal, linewidth=1, c='magenta')

			ax[0].scatter(edw_subject.datenums_BP, edw_subject.systolic, c = 'red',s=10)
			ax[0].scatter(edw_subject.datenums_BP, edw_subject.diastolic, c = 'blue',s=10)
			ax[0].scatter(cam_dates, maxBP * np.ones(len(cam_dates),), c = 'lawngreen',s=16)
			ax[0].scatter(transferin, maxBP * np.ones(len(transferin),), marker='>' , c = 'dimgrey',s=16)
			ax[0].scatter(transferout, maxBP * np.ones(len(transferout),), marker='<', c = 'dimgrey',s=16)
			ax[0].set_title('ICU-Sleep studyID ' + edw_subject.ID + ', MRN: '+ str(int(table_studyid.MRN.iloc[0])) + ', transfer in: ' + str(transferin[0]), fontdict={'fontsize': 14, 'fontweight': 'medium'})
			ax[0].legend(['BP-sys-CUFF', 'BP-sys-ART','BP-dia-CUFF', 'BP-dia-ART', 'BP-sys-EDW', 'BP-dia -EDW', 'CAM ICU done', 'ADT TransferIn', 'ADT TransferOut'])

			if 'SPO2%' in signals_to_load:
				ax[1].plot(data['SPO2%'].datetime, data['SPO2%'].signal, c = 'springgreen', linewidth=1,zorder=1)
				# ax[1].plot(edw_subject.datenums_O2, edw_subject.o2, c = 'royalblue')
				ax[1].scatter(edw_subject.datenums_O2, edw_subject.o2, c = 'royalblue',s=12,zorder=2)
				ax[1].legend(['SPO2% - bedmaster', 'SPO2% - EDW'])

			if 'HR' in signals_to_load:
				ax[2].plot(data['HR'].datetime, data['HR'].signal, c = 'crimson',linewidth=1,zorder=1)
				# ax[2].plot(edw_subject.datenums_HR, edw_subject.hr, c = 'black')
				ax[2].scatter(edw_subject.datenums_HR, edw_subject.hr, c = 'black', s=12,zorder=2)
				ax[2].scatter(cam_dates, maxHR * np.ones(len(cam_dates),), c = 'lawngreen',s=16)
				ax[2].scatter(transferin, maxHR * np.ones(len(transferin),), marker='>' , c = 'dimgrey',s=16)
				ax[2].scatter(transferout, maxHR * np.ones(len(transferout),), marker='<', c = 'dimgrey',s=16)
				ax[2].legend(['HR - bedmaster', 'HR - EDW', 'CAM ICU done', 'ADT TransferIn', 'ADT TransferOut'])

			# print(transferin)
			# print(transferout)

			for i in range(3):
				ax[i].xaxis.set_major_formatter(DateFormatter('%d %H:%M'))
				ax[i].set_xlim([np.min(transferin)-timedelta(hours=1), np.max(transferout)+timedelta(hours=1)])

		if airgo_exists:
			airgo_data = pd.read_csv(airgo_file)
			airgo_data.columns = [x.lower() for x in airgo_data.columns]
			# if 'DateTime' in airgo_data.columns:
			# 	airgo_data['datetime'] = pd.to_datetime(airgo_data.DateTime, infer_datetime_format=1)
			# 	airgo_data = airgo_data.set_index('datetime')
			# 	airgo_data = airgo_data.drop('DateTime', axis=1).astype('float16')
			# else:
			airgo_data['datetime'] = pd.to_datetime(airgo_data.datetime, infer_datetime_format=1)
			airgo_data = airgo_data.set_index('datetime')

			# print(transferin)
			# print(transferout)

			ax[3].plot(airgo_data.index, airgo_data.band, c='blue', linewidth=1, zorder=1)

			ax[3].legend(['AirGo'])
			ax[3].xaxis.set_major_formatter(DateFormatter('%d %H:%M'))
			ax[3].set_xlim([np.min(transferin) - timedelta(hours=1), np.max(transferout) + timedelta(hours=1)])


		plt.savefig(os.path.join(plot_savepath,'bedmaster_edw_airgo_' + str(studyID).zfill(3) + '_new.png'), dpi=250)
		plt.close()

	except Exception as e:
		print('Error for ' + str(studyID))
		print(e)
		continue