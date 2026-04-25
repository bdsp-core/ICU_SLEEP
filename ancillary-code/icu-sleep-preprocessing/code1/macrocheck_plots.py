import sys
sys.path.append('C:/Users/wg984/Wolfgang/repos/Bedmaster-ICU-tools/code')

# %matplotlib widget
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
patient_object_fname = 'patient_objects.pickle'
plot_savepath = 'C:/Users/wg984/Dropbox (Partners HealthCare)/ICU-SLEEP-MATERIALS/PlottingData/EDW_Bedmaster_Plots/1hour_snippet'

# get EDW data:
with open(patient_object_fname, "rb") as f:
	patient_object_list = pickle.load(f)

# study table including cam dates:
tablefile = 'M:/Projects/ICU_SLEEP_STUDY/data/data_analysis/Study/ICUSleep_DataTable_ICUonly.csv'
table= pd.read_csv(tablefile)

# only subset of BMR files for now: manual list
bmr_list = ['BMR_001.h5',
			'BMR_002.h5',
			'BMR_003.h5',
			'BMR_004.h5',
			'BMR_005.h5',
			'BMR_006.h5',
			'BMR_007.h5',
			'BMR_008.h5',
			'BMR_009.h5',
			'BMR_010.h5',
			'BMR_011.h5',
			'BMR_012.h5',
			'BMR_013.h5',
			'BMR_014.h5',
			'BMR_015.h5',
			'BMR_016.h5',
			'BMR_017.h5',
			'BMR_018.h5',
			'BMR_019.h5',
			'BMR_020.h5',
			'BMR_021.h5',
			'BMR_022.h5',
			'BMR_023.h5',
			'BMR_024.h5',
			'BMR_025.h5',
			'BMR_026.h5',
			'BMR_027.h5',
			'BMR_028.h5',
			'BMR_029.h5',
			'BMR_030.h5',
			'BMR_032.h5',
			'BMR_033.h5',
			'BMR_034.h5',
			'BMR_035.h5',
			'BMR_036.h5',
			'BMR_037.h5',
			'BMR_038.h5',
			'BMR_040.h5',
			'BMR_041.h5',
			'BMR_043.h5',
			'BMR_044.h5',
			'BMR_045.h5',
			'BMR_046.h5',
			'BMR_047.h5',
			'BMR_048.h5',
			'BMR_049.h5',
			'BMR_050.h5',
			'BMR_051.h5',
			'BMR_052.h5',
			'BMR_054.h5',
			'BMR_055.h5',
			'BMR_056.h5',
			'BMR_057.h5',
			'BMR_058.h5',
			'BMR_059.h5',
			'BMR_060.h5',
			'BMR_061.h5',
			'BMR_062.h5',
			'BMR_063.h5',
			'BMR_073.h5',
			'BMR_074.h5',
			'BMR_075.h5',
			'BMR_076.h5',
			'BMR_077.h5',
			'BMR_078.h5',
			'BMR_079.h5',
			'BMR_080.h5',
			'BMR_081.h5',
			'BMR_082.h5',
			'BMR_083.h5',
			'BMR_084.h5',
			'BMR_085.h5',
			'BMR_086.h5',
			'BMR_087.h5',
			'BMR_088.h5',
			'BMR_089.h5',
			'BMR_090.h5',
			'BMR_092.h5',
			'BMR_093.h5',
			'BMR_094.h5',
			'BMR_095.h5',
			'BMR_096.h5',
			'BMR_097.h5',
			'BMR_098.h5',
			'BMR_099.h5',
			'BMR_100.h5',
			'BMR_101.h5',
			'BMR_102.h5',
			'BMR_103.h5',
			'BMR_104.h5',
			'BMR_105.h5',
			'BMR_107.h5',
			'BMR_108.h5',
			'BMR_109.h5',
			'BMR_110.h5',
			'BMR_111.h5',
			'BMR_112.h5',
			'BMR_113.h5',
			'BMR_114.h5',
			'BMR_115.h5',
			'BMR_116.h5',
			'BMR_117.h5',
			'BMR_119.h5',
			'BMR_120.h5',
			'BMR_121.h5',
			'BMR_122.h5',
			'BMR_123.h5',
			'BMR_124.h5',
			'BMR_125.h5',
			'BMR_126.h5',
			'BMR_127.h5',
			'BMR_128.h5',
			'BMR_129.h5',
			'BMR_130.h5',
			'BMR_131.h5',
			'BMR_132.h5',
			'BMR_133.h5',
			'BMR_134.h5',
			'BMR_135.h5',
			'BMR_136.h5',
			'BMR_137.h5',
			'BMR_138.h5',
			'BMR_140.h5',
			'BMR_141.h5',
			'BMR_142.h5',
			'BMR_143.h5',
			'BMR_145.h5']

for studyID in bmr_list:
	try:
		print(studyID)
		studyID = int(studyID.split('BMR_')[1].split('.h5')[0]) #TMP

		# edw selection:
		id_list = [patient_object_list[x].ID for x in range(len(patient_object_list))]
		ididx = id_list.index(str(studyID).zfill(3))
		edw_subject = patient_object_list[ididx]
		# get bedmaster data:
		bmr_file = os.path.join(bmr_studyid_dir,'BMR_'+ (str(studyID).zfill(3) +'.h5'))
		# table
		table_studyid = table[table.StudyID == studyID]
		transferin = pd.to_datetime(pd.unique(table_studyid.ADT_TransferIn), infer_datetime_format=1)
		transferout = pd.to_datetime(pd.unique(table_studyid.ADT_TransferOut), infer_datetime_format=1)
		cam_dates = pd.to_datetime(table_studyid.CAM_Date.values, infer_datetime_format=1)
		admission = pd.to_datetime(table_studyid.ADT_Admission, infer_datetime_format=1)
		discharge = pd.to_datetime(table_studyid.ADT_Discharge, infer_datetime_format=1)

		data = BMR_load(bmr_file, signals=['NBPD','NBPS','HR','SPO2%'])

		maxBP = max(data['NBPS'].signal)
		maxHR = max(data['HR'].signal)


		fig, ax = plt.subplots(3,1,figsize = (30,15))


		ax[0].plot(data['NBPS'].datetime, data['NBPS'].signal, linewidth=1, c = 'orange')
		ax[0].plot(data['NBPD'].datetime, data['NBPD'].signal, linewidth=1, c = 'magenta')
		# ax[0].plot(edw_subject.datenums_BP, edw_subject.systolic, c = 'red')
		# ax[0].plot(edw_subject.datenums_BP, edw_subject.diastolic, c = 'blue')
		ax[0].scatter(edw_subject.datenums_BP, edw_subject.systolic, c = 'red',s=10)
		ax[0].scatter(edw_subject.datenums_BP, edw_subject.diastolic, c = 'blue',s=10)

		ax[0].scatter(cam_dates, maxBP * np.ones(len(cam_dates),), c = 'lawngreen',s=16)

		ax[0].scatter(transferin, maxBP * np.ones(len(transferin),), marker='>' , c = 'dimgrey',s=16)
		ax[0].scatter(transferout, maxBP * np.ones(len(transferout),), marker='<', c = 'dimgrey',s=16)

		ax[0].set_title('ICU-Sleep studyID ' + edw_subject.ID, fontdict={'fontsize': 14, 'fontweight': 'medium'})
		ax[0].legend(['BP sys - bedmaster', 'BP dia - bedmaster', 'BP sys - EDW', 'BP dia - EDW', 'CAM ICU done', 'ADT TransferIn', 'ADT TransferOut'])

		ax[1].plot(data['SPO2%'].datetime, data['SPO2%'].signal, c = 'springgreen', linewidth=1,zorder=1)
		# ax[1].plot(edw_subject.datenums_O2, edw_subject.o2, c = 'royalblue')
		ax[1].scatter(edw_subject.datenums_O2, edw_subject.o2, c = 'royalblue',s=12,zorder=2)


		ax[1].legend(['SPO2% - bedmaster', 'SPO2% - EDW'])

		ax[2].plot(data['HR'].datetime, data['HR'].signal, c = 'crimson',linewidth=1,zorder=1)
		# ax[2].plot(edw_subject.datenums_HR, edw_subject.hr, c = 'black')
		ax[2].scatter(edw_subject.datenums_HR, edw_subject.hr, c = 'black', s=12,zorder=2)
		ax[2].scatter(cam_dates, maxHR * np.ones(len(cam_dates),), c = 'lawngreen',s=16)
		ax[2].scatter(transferin, maxHR * np.ones(len(transferin),), marker='>' , c = 'dimgrey',s=16)
		ax[2].scatter(transferout, maxHR * np.ones(len(transferout),), marker='<', c = 'dimgrey',s=16)
		ax[2].legend(['HR - bedmaster', 'HR - EDW', 'CAM ICU done', 'ADT TransferIn', 'ADT TransferOut'])

		for i in range(3):
			ax[i].xaxis.set_major_formatter(DateFormatter('%d %H:%M'))
			ax[i].set_xlim([transferin+timedelta(hours=1), transferin+timedelta(hours=2)])


		plt.savefig(os.path.join(plot_savepath,'bedmaster_edw_' + edw_subject.ID + '.png'), dpi=250)
		plt.close()

	except Exception as e:
		print(e)
		continue