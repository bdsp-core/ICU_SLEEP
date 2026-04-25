#!/usr/bin/python3

import sys


# sys.path.append('C:/Users/wg984/Wolfgang/repos/ICU-Sleep/code1/')
# sys.path.append('C:/Users/wg984/Wolfgang/repos/Bedmaster-ICU-tools/code/')
sys.path.append('/home/wolfgang/repos/ICU-Sleep/code1/')
sys.path.append('/home/wolfgang/repos/Bedmaster-ICU-tools/code/')


sys.path.append('C:/Users/wg984/Wolfgang/repos/ICU-Sleep/code1/')
sys.path.append('C:/Users/wg984/Wolfgang/repos/Bedmaster-ICU-tools/code/')

# from Datetime_DateNum_Conversion  import datetime_to_DateNum
from DateTime_DateNum_Conversion import DateNum_to_DateTime

import os
import time
from time import mktime
from datetime import datetime
from datetime import timedelta
import pytz
import numpy as np
import pandas as pd
# import hdf5storage

import plotly
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot
import plotly.io as pio
from plotly import tools
# plotly.io.orca.config.executable  = 'C:/Users/wg984/AppData/Local/conda/conda/envs/plotly3/orca_app/orca.exe'
from dropTimeZone_forPlotly import dropTimeZone
from dropTimeZone_forPlotly import AddNaNs
from bmresearch_tools import *
import gc
import time





def main():
	# print('sleep')
	# time.sleep(3600)



	# print('sleep')
	# time.sleep(3600)


	

	################################################
	################	SETTINGS 	################
	################################################
	signals_to_plot = {

		'band': {'use': 1, 'sensor': 'AirGo_4Hz', 'label': 'AirGo', 'yaxis_title': 'AirGo', 'trace': 1},
		'accx': {'use': 1, 'sensor': 'AirGo_4Hz', 'label': 'acc. X', 'yaxis_title': 'Acceler.', 'trace': 5},
		'accy': {'use': 1, 'sensor': 'AirGo_4Hz', 'label': 'acc. Y', 'yaxis_title': 'Acceler', 'trace': 5},
		'accz': {'use': 1, 'sensor': 'AirGo_4Hz', 'label': 'acc. Z', 'yaxis_title': 'Acceler', 'trace': 5},
		'deriv1': {'use': 0, 'sensor': 'AirGo_4Hz', 'label': 'AirGo 1st deriv.', 'yaxis_title': 'Deriv', 'trace': 6},
		'deriv2': {'use': 0, 'sensor': 'AirGo_4Hz', 'label': 'AirGo 2nd deriv.', 'yaxis_title': 'Deriv', 'trace': 6},
		'ventilation_3s': {'use': 0, 'sensor': 'AirGo_4Hz', 'label': 'Ventilation (3sec)', 'yaxis_title': 'Ventilation',
						   'trace': 10},
		'ventilation_10s': {'use': 0, 'sensor': 'AirGo_4Hz', 'label': 'Ventilation (10sec)',
							'yaxis_title': 'Ventilation', 'trace': 8},
		'ventilation_60s': {'use': 0, 'sensor': 'AirGo_4Hz', 'label': 'Ventilation (60sec)',
							'yaxis_title': 'Ventilation', 'trace': 10},
		'hypo_10_60': {'use': 1, 'sensor': 'AirGo_4Hz', 'label': 'Hypopnea indication', 'yaxis_title': 'Hypopnea ind.',
					   'trace': 2},
		'movavg_1s': {'use': 0, 'sensor': 'AirGo_4Hz', 'label': 'AirGo Mov.Avg. (1sec)', 'yaxis_title': 'AirGo Avg',
					  'trace': 8},
		'movavg_1_2s': {'use': 0, 'sensor': 'AirGo_4Hz', 'label': 'AirGo Mov.Avg. (1.2sec)', 'yaxis_title': 'AirGo Avg',
						'trace': 8},
		'movavg_2s': {'use': 0, 'sensor': 'AirGo_4Hz', 'label': 'AirGo Mov.Avg. (2sec)', 'yaxis_title': 'AirGo Avg',
					  'trace': 8},
		'movavg_3s': {'use': 0, 'sensor': 'AirGo_4Hz', 'label': 'AirGo Mov.Avg. (3sec)', 'yaxis_title': 'AirGo Avg',
					  'trace': 8},
		'movavg_5s': {'use': 0, 'sensor': 'AirGo_4Hz', 'label': 'AirGo Mov.Avg. (5sec)', 'yaxis_title': 'AirGo Avg',
					  'trace': 8},
		'movavg_10s': {'use': 0, 'sensor': 'AirGo_4Hz', 'label': 'AirGo Mov.Avg. (10sec)', 'yaxis_title': 'AirGo Avg',
					   'trace': 8},
		'movavg_60s': {'use': 0, 'sensor': 'AirGo_4Hz', 'label': 'AirGo Mov.Avg. (60sec)', 'yaxis_title': 'AirGo Avg',
					   'trace': 8},
		'rr_10s': {'use': 1, 'sensor': 'AirGo_4Hz', 'label': 'Respiration rate (10sec)', 'yaxis_title': 'RR',
				   'trace': 6},
		'rr_60s': {'use': 0, 'sensor': 'AirGo_4Hz', 'label': 'Respiration rate (60sec)', 'yaxis_title': 'RR',
				   'trace': 9},
		# Bedmaster data:
		'SPO2%': {'use': 1, 'sensor': 'Bedmaster', 'label': 'SPO2(%)', 'yaxis_title': 'SPO2%', 'trace': 2},
		# peripheral capillary oxygen saturation - usually pulse oximetry
		# 'AR1_systolic': 	{'use': 1, 'sensor': 'Bedmaster', 'label': 'A.BP-sys','yaxis_title':'RR',		'trace': 2},
		# 'AR1_mean': 		{'use': 1, 'sensor': 'Bedmaster', 'label': 'A.BP-mean','yaxis_title':'RR', 	'trace': 2},
		# 'AR1_diastolic': 	{'use': 1, 'sensor': 'Bedmaster', 'label': 'A.BP-dia','yaxis_title':'RR', 		'trace': 2},
		'ART1S': {'use': 1, 'sensor': 'Bedmaster', 'label': 'A.BP-sys', 'yaxis_title': 'BP', 'trace': 4},
		'ART1M': {'use': 1, 'sensor': 'Bedmaster', 'label': 'A.BP-mean', 'yaxis_title': 'BP', 'trace': 4},
		'ART1D': {'use': 1, 'sensor': 'Bedmaster', 'label': 'A.BP-dia', 'yaxis_title': 'BP', 'trace': 4},
		'NBPS': {'use': 1, 'sensor': 'Bedmaster', 'label': 'BP-sys', 'yaxis_title': 'BP', 'trace': 4},
		# Non invase blood pressure systolic
		'NBPD': {'use': 1, 'sensor': 'Bedmaster', 'label': 'BP-dia', 'yaxis_title': 'BP', 'trace': 4},
		# Non invase blood pressure diastolic
		'HR': {'use': 1, 'sensor': 'Bedmaster', 'label': 'HR', 'yaxis_title': 'HR', 'trace': 3},  # Heart Rate
		# HRV data:
		'r_peaks': {'use': 0, 'sensor': 'HRV', 'label': 'ECG R-peak', 'yaxis_title': 'R-peak', 'trace': 1},
		'HRV_TimeDomain': {'use': 0, 'sensor': 'HRV', 'label': '', 'yaxis_title': 'RR', 'trace': 4},
		'HRV_FreqDomain': {'use': 0, 'sensor': 'HRV', 'label': '', 'yaxis_title': 'RR', 'trace': 5},
		'HRV_Poincare': {'use': 0, 'sensor': 'HRV', 'label': '', 'yaxis_title': 'RR', 'trace': 6},
		'HRV_Entropy': {'use': 0, 'sensor': 'HRV', 'label': '', 'yaxis_title': 'RR', 'trace': 7},

	'band':					{'use': 1, 'sensor': 'AirGo_4Hz', 'label': 'AirGo','yaxis_title':'AirGo',						'trace': 1},
	'accx':				{'use': 1, 'sensor': 'AirGo_4Hz', 'label': 'acc. X', 'yaxis_title':'Acceler.',						'trace': 5},
	'accy':				{'use': 1, 'sensor': 'AirGo_4Hz', 'label': 'acc. Y', 'yaxis_title':'Acceler',						'trace': 5},
	'accz':				{'use': 1, 'sensor': 'AirGo_4Hz', 'label': 'acc. Z', 'yaxis_title':'Acceler',						'trace': 5},
	'deriv1':				{'use': 0, 'sensor': 'AirGo_4Hz', 'label': 'AirGo 1st deriv.', 'yaxis_title':'Deriv',			'trace': 6},
	'deriv2':				{'use': 0, 'sensor': 'AirGo_4Hz', 'label': 'AirGo 2nd deriv.', 'yaxis_title':'Deriv',			'trace': 6},
	'ventilation_3s':		{'use': 0, 'sensor': 'AirGo_4Hz', 'label': 'Ventilation (3sec)', 'yaxis_title':'Ventilation',					'trace': 10},
	'ventilation_10s':		{'use': 0, 'sensor': 'AirGo_4Hz', 'label': 'Ventilation (10sec)','yaxis_title':'Ventilation',					'trace': 8},
	'ventilation_60s':		{'use': 0, 'sensor': 'AirGo_4Hz', 'label': 'Ventilation (60sec)', 'yaxis_title':'Ventilation',					'trace': 10},
	'hypo_10_60':			{'use': 1, 'sensor': 'AirGo_4Hz', 'label': 'Hypopnea indication', 'yaxis_title':'Hypopnea ind.',				'trace': 2},
	'movavg_1s':			{'use': 0, 'sensor': 'AirGo_4Hz', 'label': 'AirGo Mov.Avg. (1sec)',	'yaxis_title':'AirGo Avg',					'trace': 8},
	'movavg_1_2s':			{'use': 0, 'sensor': 'AirGo_4Hz', 'label': 'AirGo Mov.Avg. (1.2sec)', 'yaxis_title':'AirGo Avg',				'trace': 8},
	'movavg_2s':			{'use': 0, 'sensor': 'AirGo_4Hz', 'label': 'AirGo Mov.Avg. (2sec)',	'yaxis_title':'AirGo Avg',					'trace': 8},
	'movavg_3s':			{'use': 0, 'sensor': 'AirGo_4Hz', 'label': 'AirGo Mov.Avg. (3sec)',	'yaxis_title':'AirGo Avg',					'trace': 8},
	'movavg_5s':			{'use': 0, 'sensor': 'AirGo_4Hz', 'label': 'AirGo Mov.Avg. (5sec)',	'yaxis_title':'AirGo Avg',					'trace': 8},
	'movavg_10s':			{'use': 0, 'sensor': 'AirGo_4Hz', 'label': 'AirGo Mov.Avg. (10sec)','yaxis_title':'AirGo Avg',					'trace': 8},
	'movavg_60s':			{'use': 0, 'sensor': 'AirGo_4Hz', 'label': 'AirGo Mov.Avg. (60sec)','yaxis_title':'AirGo Avg',					'trace': 8},
	'rr_10s':				{'use': 1, 'sensor': 'AirGo_4Hz', 'label': 'Respiration rate (10sec)','yaxis_title':'RR',						'trace': 6},
	'rr_60s':				{'use': 0, 'sensor': 'AirGo_4Hz', 'label': 'Respiration rate (60sec)','yaxis_title':'RR',						'trace': 9},
	# Bedmaster data:
	'SPO2%': 			{'use': 1, 'sensor': 'Bedmaster', 'label': 'SPO2(%)','yaxis_title':'SPO2%', 		'trace': 2},			# peripheral capillary oxygen saturation - usually pulse oximetry
	# 'AR1_systolic': 	{'use': 1, 'sensor': 'Bedmaster', 'label': 'A.BP-sys','yaxis_title':'RR',		'trace': 2},
	# 'AR1_mean': 		{'use': 1, 'sensor': 'Bedmaster', 'label': 'A.BP-mean','yaxis_title':'RR', 	'trace': 2},
	# 'AR1_diastolic': 	{'use': 1, 'sensor': 'Bedmaster', 'label': 'A.BP-dia','yaxis_title':'RR', 		'trace': 2},
	'ART1S': 			{'use': 1, 'sensor': 'Bedmaster', 'label': 'A.BP-sys','yaxis_title':'BP',		'trace': 4},
	'ART1M': 			{'use': 1, 'sensor': 'Bedmaster', 'label': 'A.BP-mean', 'yaxis_title':'BP',	'trace': 4},
	'ART1D': 			{'use': 1, 'sensor': 'Bedmaster', 'label': 'A.BP-dia', 'yaxis_title':'BP',		'trace': 4},
	'NBPS': 			{'use': 1, 'sensor': 'Bedmaster', 'label': 'BP-sys','yaxis_title':'BP',		'trace': 4},			# Non invase blood pressure systolic
	'NBPD': 			{'use': 1, 'sensor': 'Bedmaster', 'label': 'BP-dia','yaxis_title':'BP',		'trace': 4},			# Non invase blood pressure diastolic
	'HR': 				{'use': 1, 'sensor': 'Bedmaster', 'label': 'HR','yaxis_title':'HR',			'trace': 3},			# Heart Rate
	# HRV data:
	'r_peaks': 			{'use': 0, 'sensor': 'HRV', 'label': 'ECG R-peak', 'yaxis_title': 'R-peak', 'trace': 1},
	'HRV_TimeDomain':	{'use': 0, 'sensor': 'HRV', 'label': '','yaxis_title':'RR',						'trace': 4},
	'HRV_FreqDomain':	{'use': 0, 'sensor': 'HRV', 'label': '','yaxis_title':'RR',						'trace': 5},
	'HRV_Poincare':		{'use': 0, 'sensor': 'HRV', 'label': '','yaxis_title':'RR',						'trace': 6},
	'HRV_Entropy':		{'use': 0, 'sensor': 'HRV', 'label': '','yaxis_title':'RR',						'trace': 7},

	}

	style_settings = set_PlotStyle('A')

	# study_ids = range(35,76)

	study_ids = [25, 27, 36, 43, 44, 45, 47, 64, 67, 68, 71, 163] # list(range(180, 190)) + [3, 8, 15, 16, 18,

	study_ids = [63, 64, 67, 68, 69, 71, 72] # , 76, 77, 78, 79, 90, 81, 85, 87, 89, 90, 93, 97, 100] # 50

	study_ids = list(range(190))

	study_ids = [sys.argv[1]]

	for study_id in study_ids:
		# missing data pateints:
		# if study_id in [3, 3, 8, 15, 16, 18, 25, 27, 36, 43, 44, 45, 47, 64, 67, 68, 71, 163, 168, 185, 187]: continue
		# non category A and B patients:
		if study_id in [132, 5, 134, 136, 9, 138, 141, 144, 147, 148, 22, 23, 150, 26, 27, 28, 159, 162, 166, 40, 41,
						170, 174, 55, 184, 57, 58, 59, 60, 62, 65, 66, 70, 73, 75, 94, 96, 99, 124, 127]: continue

		print(study_id)
		try:
			# if 1:

	# study_ids = range(113,190)
	study_ids = [sys.argv[1]]


	for study_id in study_ids:
		# missing data pateints:
		# if study_id in [3, 8, 15, 16, 18, 25, 27, 36, 43, 44, 45, 47, 64, 67, 68, 71, 163, 168, 185, 187]: continue
		# non category A and B patients:
		# if study_id in [132, 5, 134, 136, 9, 138, 141, 144, 147, 148, 22, 23, 150, 26, 27, 28, 159, 162, 166, 40, 41, 170, 174, 55, 184, 57, 58, 59, 60, 62, 65, 66, 70, 73, 75, 94, 96, 99, 124, 127]: continue

		print(study_id)

		try:
		# if 1:

			gc.collect()

			strstudy_id = str(study_id).zfill(3)


			# plot_path = os.path.join(
			# 	'C:/Users/wg984/Dropbox (Partners HealthCare)/ICU-SLEEP-MATERIALS/TimeAlignmentAirGoBedmaster/Plots/',
			# 	strstudy_id)
			# plot_path = os.path.join('E:/Dropbox (Partners HealthCare)/ICU-SLEEP-MATERIALS/TimeAlignmentAirGoBedmaster/Plots/',strstudy_id)
			plot_path = os.path.join('/home/wolfgang/repos/ICU-Sleep/Plots',strstudy_id)


			plot_path = os.path.join('M:/Projects/AirGoSleepStaging/TimeAlignmentAirGoBedmasterNew/Plots/',strstudy_id)
			# plot_path = os.path.join('C:/Users/wg984/Dropbox (Partners HealthCare)/UndiagnosedOSA_Project/TimeAlignmentAirGoBedmasterNew/Plots/',strstudy_id)
			# plot_path = os.path.join('E:/Dropbox (Partners HealthCare)/ICU-SLEEP-MATERIALS/TimeAlignmentAirGoBedmaster/Plots/',strstudy_id)


			if not os.path.exists(plot_path):
				os.mkdir(plot_path)

			# specify for each signal 'parameter-dict' with:
			# - use (should the signal be used and plotted)
			# - sensor: signals are usually not all in one sensorectory, specify sensor that gets added to datadir
			# - trace: specify the trace (#of subplot) to which the signal should be added.

			# get the data:
			signals_collection = read_in_data(signals_to_plot, strstudy_id)

			# plot routine:
			ICUsignals_visualization(signals_to_plot, signals_collection, style_settings, subject=strstudy_id,
									 segments_duration=1)

			code_successful = 1





		# multiline plot
			# ICUsignals_visualizationMultiline(signals_collection, style_settings, dayNo = 999, dayt = 'night', subject = strstudy_id)

		except Exception as e:
			code_successful = 0
			print(e)
			print('FAILED.')
			continue


		# multiline plot
		# ICUsignals_visualizationMultiline(signals_collection, style_settings, dayNo = 999, dayt = 'night', subject = strstudy_id)

		except Exception as e:
			code_successful = 0
			print(e)
			print('FAILED.')
			continue


def read_in_data(signal_to_plot, study_id):
	################################################
	################    Read In Function  	########
	################################################

	# 1. group signals_to_plot by their sensor type (i.e. airgo, bedmaster, noise light and sampling rates)
	# 2. read the data and save it to a SignalCollection dictionary


	airgo_research_10Hz_dir = '//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/data_analysis/AirGo/airgo_features'
	airgo_research_4Hz_dir = '//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/data_analysis/AirGo/airgo_features_4Hz'
	bmr_dir = '//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/data_analysis/BMR_studyID'
	hrv_dir = '//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/data_analysis/HRV_analysis'

	airgo_research_10Hz_dir = '/media/mad3/Projects/ICU_SLEEP_STUDY/data/data_analysis/AirGo/airgo_features'
	airgo_research_4Hz_dir = '/media/mad3/Projects/ICU_SLEEP_STUDY/data/data_analysis/AirGo/airgo_features_4Hz'
	bmr_dir = '/media/mad3/Projects/ICU_SLEEP_STUDY/data/data_analysis/BMR_studyID'
	hrv_dir = '/media/mad3/Projects/ICU_SLEEP_STUDY/data/data_analysis/HRV_analysis'

	airgo_research_10Hz_dir 		= '//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/data_analysis/AirGo/airgo_features'
	airgo_research_4Hz_dir 			= '//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/data_analysis/AirGo/airgo_features_4Hz'
	bmr_dir 						= '//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/data_analysis/BMR_studyID'
	hrv_dir 						= '//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/data_analysis/HRV_analysis'


	signals_collection = {}
	traces_setting = pd.DataFrame([])
	signal_to_plot_airgo_4Hz = []
	signal_to_plot_airgo_10Hz = []
	signal_to_plot_bedmaster = []
	signal_to_plot_noiselight = []
	signal_to_plot_hrv = []

	# group signals into sensor types:
	for signal in signal_to_plot:
		if signal_to_plot[signal]['sensor'] == 'AirGo_4Hz':
			signal_to_plot_airgo_4Hz.append(signal)
		elif signal_to_plot[signal]['sensor'] == 'AirGo_10Hz':
			signal_to_plot_airgo_10Hz.append(signal)
		elif signal_to_plot[signal]['sensor'] == 'Bedmaster':
			signal_to_plot_bedmaster.append(signal)
		elif signal_to_plot[signal]['sensor'] == 'NoiseLight':
			signal_to_plot_noiselight.append(signal)
		elif signal_to_plot[signal]['sensor'] == 'HRV':
			signal_to_plot_hrv.append(signal)
		else:
			raise ValueError('unknown sensor type.')

	# AirGo 4Hz signals:

	sensor_data = pd.read_csv(os.path.join(airgo_research_4Hz_dir, 'airgo_' + str(study_id) + '.csv'))

	sensor_data = pd.read_csv( os.path.join(airgo_research_4Hz_dir, 'airgo_' + str(study_id) + '.csv') )

	sensor_data['datetime'] = pd.to_datetime(sensor_data.datetime, infer_datetime_format=1)
	sensor_data = sensor_data.set_index('datetime')
	# sensor_data = sensor_data.drop('DateTime',axis=1)

	# only select columns as specified:
	if len(signal_to_plot_airgo_4Hz) > 0:
		signals_collection['airgo_4Hz'] = sensor_data[signal_to_plot_airgo_4Hz]

	# AirGo 10Hz signals:
	sensor_data = pd.read_csv(os.path.join(airgo_research_10Hz_dir, 'airgo_' + str(study_id) + '.csv'))
	sensor_data['datetime'] = pd.to_datetime(sensor_data.datetime, infer_datetime_format=1)
	sensor_data = sensor_data.set_index('datetime')
	# sensor_data = sensor_data.drop('DateTime',axis=1).astype('float16')

	# only select columns as specified:
	if len(signal_to_plot_airgo_10Hz) > 0:
		signals_collection['airgo_10Hz'] = sensor_data[signal_to_plot_airgo_10Hz]

	# Bedmaster signals:


	signals_contained_in_file = get_metadata(os.path.join(bmr_dir, 'BMR_' + study_id + '.h5'))
	signal_to_plot_bedmaster = [x for x in signal_to_plot_bedmaster if x in signals_contained_in_file]

	for signal in signal_to_plot_bedmaster:
		signals_collection[signal] = BMR_load(os.path.join(bmr_dir, 'BMR_' + study_id + '.h5'), signals=[signal])[
			signal].drop(
			'posix', axis=1)
		signals_collection[signal] = signals_collection[signal].set_index('datetime')

	for signal in signal_to_plot_hrv:
		if signal in ['r_peaks'] and False:  # TODO: deactivated for now
			r_peaks = pd.DataFrame(
				pd.read_csv(os.path.join(hrv_dir, str(study_id) + '_NN_RPeaks.csv'))['peak_datetime'])


	signals_contained_in_file = get_metadata(os.path.join(bmr_dir, 'BMR_' + study_id + '.h5'))
	signal_to_plot_bedmaster = [x for x in signal_to_plot_bedmaster if x in signals_contained_in_file]

	for signal in signal_to_plot_bedmaster:

		signals_collection[signal] = BMR_load(os.path.join(bmr_dir, 'BMR_' + study_id + '.h5'), signals=[signal])[signal].drop(
		'posix', axis=1)
		signals_collection[signal] = signals_collection[signal].set_index('datetime')

	for signal in signal_to_plot_hrv:
		if signal in ['r_peaks'] and False: #TODO: deactivated for now
			r_peaks = pd.DataFrame(pd.read_csv(os.path.join(hrv_dir, str(study_id) + '_NN_RPeaks.csv'))['peak_datetime'])

			r_peaks.columns = ['datetime']
			r_peaks['datetime'] = pd.to_datetime(r_peaks['datetime'], infer_datetime_format=1)
			r_peaks['signal'] = 1
			r_peaks.set_index('datetime', inplace=True)
			signals_collection[signal] = r_peaks

	for signal in signals_collection:
		# adding NaNs to the datetime information for missing data gaps. so that plot does not show a line.
		signals_collection[signal] = AddNaNs(signals_collection[signal], signal)

	return signals_collection


def zoom(layout, xrange):
	in_view = df.loc[layout.xaxis.range[0]:layout.xaxis.range[1]]

	layout.yaxis.range = [in_view.High.min(), in_view.High.max()]


	layout.yaxis.range = [in_view.High.min(), in_view.High.max() ]


def ICUsignals_visualization(signals_to_plot, signals_collection, style_settings=None, subject='',
							 segments_duration=None):
	'''

	:param signals_to_plot:
	:param signals_collection:
	:param style_settings:
	:param subject: string. gets used
	:param segments_duration: split full signal into parts with specified duration, in hours.
	:return:
	'''
	################################################
	################    PLOT CODE  	################
	################################################

	airgo_alignment_options = 1
	max_trace = np.max(
		[signals_to_plot[signal]['trace'] for signal in signals_to_plot if signals_to_plot[signal]['use']])

	if segments_duration is not None:
		# split data into segments. for now, we use airgo datetime for min max computation.
		# this is done for airgo alignment, however later we might want to change it to overall min max available in the signalCollection data.
		min_datetime = np.min(signals_collection['airgo_4Hz'].index).replace(minute=0, second=0, microsecond=0)
		max_datetime = np.max(signals_collection['airgo_4Hz'].index).replace(minute=0, second=0,
																			 microsecond=0) + timedelta(hours=1)
		# create the datetime segment boundaries:

		time_segments = [min_datetime + iS * timedelta(hours=segments_duration) for iS in range(1000) if
						 min_datetime + iS * timedelta(hours=segments_duration) < max_datetime]

		time_segments = [min_datetime + iS * timedelta(hours=segments_duration) for iS in range(1000) if min_datetime + iS * timedelta(hours=segments_duration) < max_datetime ]


	else:
		# use full signal:
		time_segments = [np.min(signals_collection['airgo_4Hz'].index), np.max(signals_collection['airgo_4Hz'].index)]

	for i_timesegment in range(len(time_segments) - 1):

		gc.collect()



	for i_timesegment in range(len(time_segments)-1):

		gc.collect()


		bedmaster_signals_in_plot = 0
		time_segment_start = time_segments[i_timesegment]
		time_segment_end = time_segments[i_timesegment + 1]

		# create a figure for this time selection:
		subplots = plotly.subplots.make_subplots(rows=int(max_trace), cols=1, shared_xaxes=True, print_grid=False,
												 specs=[[{"secondary_y": True}]] * int(max_trace))
		fig = go.FigureWidget(subplots)

		idx_start_airgo_4Hz = None  # update index selection only for new timesegment for AirGo
		idx_start_airgo_10Hz = None

		low_perc = [99999] * int(max_trace + 1)
		high_perc = [-99999] * int(max_trace + 1)
		ylabel_trace = [''] * int(max_trace + 1)

		try:

			for signal in signals_to_plot:

				if not signals_to_plot[signal]['use']: continue

				sensor = signals_to_plot[signal]['sensor']
				label = signals_to_plot[signal]['label']
				traceNo = signals_to_plot[signal]['trace']
				yaxis_title = signals_to_plot[signal]['yaxis_title']
				ylabel_trace[traceNo] = yaxis_title

				if signal == 'SPO2%':
					low_perc_value = 5
					high_perc_value = 99
				else:
					low_perc_value = 1
					high_perc_value = 99

				#
				# if sensor == 'AirGo_4Hz':
				#
				# 	if signal == 'band' and airgo_alignment_options ==1:
				#
				# 		if idx_start_airgo_4Hz is None: # first airgo signal in this loop, need to find indices:
				#
				# 		# for band signal, add traces for the timeshifts:
				# 		shift_start = -240
				# 		shift_end = 240
				# 		shift_step = 96
				#
				# 		num_of_airgo_traces = len(range(shift_start, shift_end, shift_step))
				# 		for timeshift in range(shift_start, shift_end, shift_step):
				# 			trace = go.Scattergl(x=signals_collection['airgo_4Hz'].index[idx_start_airgo_4Hz:idx_end_airgo_4Hz] + timedelta(seconds=timeshift),
				# 								 y=signals_collection['airgo_4Hz'][signal].iloc[idx_start_airgo_4Hz:idx_end_airgo_4Hz],
				# 								 name=signal + ' shifted: ' + str(timeshift).rjust(4, ' '), hoverinfo='x+y',
				# 								 opacity=0.8, mode='lines',
				# 								 line=style_settings['Line'][signal],
				# 								 visible=timeshift==0)
				# 			fig.add_trace(trace, int(traceNo), 1 )
				# 		continue

				if sensor == 'Bedmaster':

					if not signal in signals_collection:
						# print(signal + ' not contained in data, therefore not plotted.')
						continue

					# change dtype of signal to float16
					signals_collection[signal].signal = signals_collection[signal].signal.astype('float16', copy=False)

					bedmaster_signals_in_plot += 1
					if airgo_alignment_options == 1:

						idx_start_signal = np.where(signals_collection[signal].index >= time_segment_start)[0]
						idx_end_signal = np.where(signals_collection[signal].index < time_segment_end)[0]
						# print(idx_start_signal.shape)
						# print(idx_end_signal.shape)
						# import pdb;
						# pdb.set_trace()
						if idx_start_signal.shape[0] == 0 or idx_end_signal.shape[0] == 0:
							idx_start_signal = 0
							idx_end_signal = 0

							# continue
							# raise ValueError('No bedmaster data in AirGo selection.')
						else:
							idx_start_signal = idx_start_signal[0]
							idx_end_signal = idx_end_signal[-1]

						# for band signal, add traces for the timeshifts:
						shift_start = -300
						shift_end = 300
						shift_step = 2

						num_of_bedmaster_traces = len(range(shift_start, shift_end, shift_step))

						if idx_end_signal - idx_start_signal <= 1:  # no data for this signal in this segment. add empty traces and then continue with next signal
							print(signal)
							print('idx_end_signal - idx_start_signal <= 1')
							for timeshift in range(shift_start, shift_end, shift_step):
								trace = go.Scattergl(
									x=[],
									y=[])
								# name=signal + ' shifted: ' + str(timeshift).rjust(4, ' '), hoverinfo='x+y',
								# opacity=0.8, mode='lines',
								# line=style_settings['Line'][signal],
								# visible=timeshift == 0)
								fig.add_trace(trace, int(traceNo), 1, secondary_y=False)

							continue

						for timeshift in range(shift_start, shift_end, shift_step):
							trace = go.Scattergl(
								x=signals_collection[signal].index[idx_start_signal:idx_end_signal] + timedelta(
									seconds=timeshift),
								y=signals_collection[signal]['signal'].iloc[idx_start_signal:idx_end_signal],
								name=signal + ' shifted: ' + str(timeshift).rjust(4, ' '), hoverinfo='x+y',
								opacity=0.8, mode='lines',
								line=style_settings['Line'][signal],
								visible=timeshift == 0)

							fig.add_trace(trace, int(traceNo), 1, secondary_y=False)

						low_perc_tmp = np.percentile(
							signals_collection[signal]['signal'].iloc[idx_start_signal:idx_end_signal], low_perc_value)
						high_perc_tmp = np.percentile(
							signals_collection[signal]['signal'].iloc[idx_start_signal:idx_end_signal], high_perc_value)
						if low_perc_tmp < low_perc[traceNo]: low_perc[traceNo] = low_perc_tmp
						if high_perc_tmp > high_perc[traceNo]: high_perc[traceNo] = high_perc_tmp

						fig.update_yaxes(title_text=label, row=int(traceNo), col=1,
										 range=[low_perc[traceNo], high_perc[traceNo]],
										 secondary_y=False)

						continue
				#
				# if signal == 'hypo_10_60' and airgo_alignment_options ==1:
				#
				# 	if idx_start_airgo_4Hz is None: # first airgo signal in this loop, need to find indices:
				# 		idx_start_airgo_4Hz = np.where(signals_collection['airgo_4Hz'].index >= time_segment_start)[0][0]
				# 		idx_end_airgo_4Hz = np.where(signals_collection['airgo_4Hz'].index < time_segment_end)[0][-1]
				#
				# 	for timeshift in range(shift_start, shift_end, shift_step):
				# 		trace = go.Scattergl(x=signals_collection['airgo_4Hz'].index[idx_start_airgo_4Hz:idx_end_airgo_4Hz] + timedelta(seconds=timeshift),
				# 							 y=signals_collection['airgo_4Hz'][signal].iloc[idx_start_airgo_4Hz:idx_end_airgo_4Hz],
				# 							 name=signal + ' shifted: ' + str(timeshift).rjust(4, ' '), hoverinfo='x+y',
				# 							 opacity=0.8, mode='lines',
				# 							 line=style_settings['Line'][signal],
				# 							 visible=timeshift==0)
				# 		fig.add_trace(trace, int(traceNo), 1 )
				# 	continue
				#
				# if signal == 'rr_10s' and airgo_alignment_options ==1:
				#
				# 	if idx_start_airgo_4Hz is None: # first airgo signal in this loop, need to find indices:
				# 		idx_start_airgo_4Hz = np.where(signals_collection['airgo_4Hz'].index >= time_segment_start)[0][0]
				# 		idx_end_airgo_4Hz = np.where(signals_collection['airgo_4Hz'].index < time_segment_end)[0][-1]
				#
				# 	for timeshift in range(shift_start, shift_end, shift_step):
				# 		trace = go.Scattergl(x=signals_collection['airgo_4Hz'].index[idx_start_airgo_4Hz:idx_end_airgo_4Hz] + timedelta(seconds=timeshift),
				# 							 y=signals_collection['airgo_4Hz'][signal].iloc[idx_start_airgo_4Hz:idx_end_airgo_4Hz],
				# 							 name=signal + ' shifted: ' + str(timeshift).rjust(4, ' '), hoverinfo='x+y',
				# 							 opacity=0.8, mode='lines',
				# 							 line=style_settings['Line'][signal],
				# 							 visible=timeshift==0)
				# 		fig.add_trace(trace, int(traceNo), 1 )
				# 	continue

				if sensor == 'AirGo_4Hz':
					if idx_start_airgo_4Hz is None:  # first airgo signal in this loop, need to find indices:
						idx_start_airgo_4Hz = np.where(signals_collection['airgo_4Hz'].index >= time_segment_start)[0][
							0]
						idx_end_airgo_4Hz = np.where(signals_collection['airgo_4Hz'].index < time_segment_end)[0][-1]

					trace = go.Scattergl(x=signals_collection['airgo_4Hz'].index[idx_start_airgo_4Hz:idx_end_airgo_4Hz],
										 y=signals_collection['airgo_4Hz'][signal].iloc[
										   idx_start_airgo_4Hz:idx_end_airgo_4Hz],
										 name=label, hoverinfo='x+y', opacity=0.8, mode='lines',
										 line=style_settings['Line'][signal])
					low_perc_tmp = np.percentile(
						signals_collection['airgo_4Hz'][signal].iloc[idx_start_airgo_4Hz:idx_end_airgo_4Hz], 1)
					high_perc_tmp = np.percentile(
						signals_collection['airgo_4Hz'][signal].iloc[idx_start_airgo_4Hz:idx_end_airgo_4Hz], 99)
					if signal == 'hypo_10_60':
						low_perc_hypo = low_perc_tmp
						high_perc_hypo = high_perc_tmp
					else:
						if low_perc_tmp < low_perc[traceNo]: low_perc[traceNo] = low_perc_tmp
						if high_perc_tmp > high_perc[traceNo]: high_perc[traceNo] = high_perc_tmp

				if sensor == 'AirGo_10Hz':
					if idx_start_airgo_10Hz is None:  # first airgo signal in this loop, need to find indices:
						idx_start_airgo_10Hz = \
						np.where(signals_collection['airgo_10Hz'].index >= time_segment_start)[0][0]
						idx_end_airgo_10Hz = np.where(signals_collection['airgo_10Hz'].index < time_segment_end)[0][-1]

					trace = go.Scattergl(
						x=signals_collection['airgo_10Hz'].index[idx_start_airgo_10Hz:idx_end_airgo_10Hz],
						y=signals_collection['airgo_10Hz'][signal].iloc[idx_start_airgo_10Hz:idx_end_airgo_10Hz],
						name=label, hoverinfo='x+y', opacity=0.8, mode='lines', line=style_settings['Line'][signal])

					low_perc_tmp = np.percentile(
						signals_collection['airgo_10Hz'][signal].iloc[idx_start_airgo_10Hz:idx_end_airgo_10Hz],
						low_perc_value)
					high_perc_tmp = np.percentile(
						signals_collection['airgo_10Hz'][signal].iloc[idx_start_airgo_10Hz:idx_end_airgo_10Hz],
						high_perc_value)
					# this is a 'manual fix' for 2nd axis for hypo_10_60, if more 2nd axis will follow this can be done better, more automatic.
					if signal == 'hypo_10_60':
						low_perc_hypo = low_perc_tmp
						high_perc_hypo = high_perc_tmp
					else:
						if low_perc_tmp < low_perc[traceNo]: low_perc[traceNo] = low_perc_tmp
						if high_perc_tmp > high_perc[traceNo]: high_perc[traceNo] = high_perc_tmp

				if sensor == 'Bedmaster':
					idx_start_signal = np.where(signals_collection[signal].index >= time_segment_start)[0][0]
					idx_end_signal = np.where(signals_collection[signal].index < time_segment_end)[0][-1]

					trace = go.Scattergl(x=signals_collection[signal].index[idx_start_signal: idx_end_signal],
										 y=signals_collection[signal]['signal'].iloc[idx_start_signal: idx_end_signal],
										 name=label, hoverinfo='x+y', opacity=0.8, mode='lines',
										 line=style_settings['Line'][signal])

					low_perc_tmp = np.percentile(
						signals_collection[signal]['signal'].iloc[idx_start_signal:idx_end_signal], low_perc_value)
					high_perc_tmp = np.percentile(
						signals_collection[signal]['signal'].iloc[idx_start_signal:idx_end_signal], high_perc_value)
					if low_perc_tmp < low_perc[traceNo]: low_perc[traceNo] = low_perc_tmp
					if high_perc_tmp > high_perc[traceNo]: high_perc[traceNo] = high_perc_tmp

				if sensor == 'HRV':
					# idx_start_signal = np.where(signals_collection[signal].index >= time_segment_start)[0][0]
					# idx_end_signal = np.where(signals_collection[signal].index < time_segment_end)[0][-1]

					trace = go.Scattergl(x=signals_collection[signal].index[idx_start_signal: idx_end_signal],
										 y=signals_collection[signal]['signal'].iloc[idx_start_signal: idx_end_signal],
										 name=label, hoverinfo='x+y', opacity=0.8, mode='markers',
										 marker=dict(color='red'))

				if signal == 'SPO2%':
					print('here')
					fig.add_trace(trace, int(traceNo), 1, secondary_y=False)
				# fig.update_yaxes(title_text="SPO2%", range=[90, 95], row=int(traceNo), col=1, secondary_y=False)
				elif signal == 'hypo_10_60':
					fig.add_trace(trace, int(traceNo), 1, secondary_y=True)
				# fig.update_yaxes(title_text="hypopnea ind.", range=[0, 1.5], row=int(traceNo), col=1, secondary_y=True)

				else:
					fig.add_trace(trace, int(traceNo), 1, secondary_y=False)

		low_perc = [99999] * int(max_trace+1)
		high_perc = [-99999] * int(max_trace+1)
		ylabel_trace = [''] * int(max_trace+1)

		try:

			for signal in signals_to_plot:
				if not signals_to_plot[signal]['use']: continue

				sensor = signals_to_plot[signal]['sensor']
				label = signals_to_plot[signal]['label']
				traceNo = signals_to_plot[signal]['trace']
				yaxis_title = signals_to_plot[signal]['yaxis_title']
				ylabel_trace[traceNo] = yaxis_title

				if signal == 'SPO2%':
					low_perc_value = 5
					high_perc_value = 99
				else:
					low_perc_value = 1
					high_perc_value = 99

				#
				# if sensor == 'AirGo_4Hz':
				#
				# 	if signal == 'band' and airgo_alignment_options ==1:
				#
				# 		if idx_start_airgo_4Hz is None: # first airgo signal in this loop, need to find indices:
				#
				# 		# for band signal, add traces for the timeshifts:
				# 		shift_start = -240
				# 		shift_end = 240
				# 		shift_step = 96
				#
				# 		num_of_airgo_traces = len(range(shift_start, shift_end, shift_step))
				# 		for timeshift in range(shift_start, shift_end, shift_step):
				# 			trace = go.Scattergl(x=signals_collection['airgo_4Hz'].index[idx_start_airgo_4Hz:idx_end_airgo_4Hz] + timedelta(seconds=timeshift),
				# 								 y=signals_collection['airgo_4Hz'][signal].iloc[idx_start_airgo_4Hz:idx_end_airgo_4Hz],
				# 								 name=signal + ' shifted: ' + str(timeshift).rjust(4, ' '), hoverinfo='x+y',
				# 								 opacity=0.8, mode='lines',
				# 								 line=style_settings['Line'][signal],
				# 								 visible=timeshift==0)
				# 			fig.add_trace(trace, int(traceNo), 1 )
				# 		continue


				if sensor == 'Bedmaster':

					if not signal in signals_collection:
						# print(signal + ' not contained in data, therefore not plotted.')
						continue

					bedmaster_signals_in_plot += 1
					if airgo_alignment_options ==1:

						idx_start_signal = np.where(signals_collection[signal].index >= time_segment_start)[0]
						idx_end_signal = np.where(signals_collection[signal].index < time_segment_end)[0]
						# print(idx_start_signal.shape)
						# print(idx_end_signal.shape)
						# import pdb;
						# pdb.set_trace()

						if idx_start_signal.shape[0] == 0 or idx_end_signal.shape[0] == 0:
							idx_start_signal = 0
							idx_end_signal = 0
							# continue
							# raise ValueError('No bedmaster data in AirGo selection.')

						else:
							idx_start_signal = idx_start_signal[0]
							idx_end_signal = idx_end_signal[-1]

						# for band signal, add traces for the timeshifts:
						shift_start = -300
						shift_end = 300
						shift_step = 2

						num_of_bedmaster_traces = len(range(shift_start, shift_end, shift_step))

						if idx_end_signal - idx_start_signal <= 1:  # no data for this signal in this segment. add empty traces and then continue with next signal
							print(signal)
							print('idx_end_signal - idx_start_signal <= 1')
							for timeshift in range(shift_start, shift_end, shift_step):
								trace = go.Scattergl(
									x=[],
									y=[] )
									# name=signal + ' shifted: ' + str(timeshift).rjust(4, ' '), hoverinfo='x+y',
									# opacity=0.8, mode='lines',
									# line=style_settings['Line'][signal],
									# visible=timeshift == 0)
								fig.add_trace(trace, int(traceNo), 1, secondary_y=False)

							continue

						for timeshift in range(shift_start, shift_end, shift_step):
							trace = go.Scattergl(x=signals_collection[signal].index[idx_start_signal:idx_end_signal] + timedelta(seconds=timeshift),
												 y=signals_collection[signal]['signal'].iloc[idx_start_signal:idx_end_signal],
												 name=signal + ' shifted: ' + str(timeshift).rjust(4, ' '), hoverinfo='x+y',
												 opacity=0.8, mode='lines',
												 line=style_settings['Line'][signal],
												 visible=timeshift==0)

							fig.add_trace(trace, int(traceNo), 1, secondary_y=False)

						low_perc_tmp = np.percentile(signals_collection[signal]['signal'].iloc[idx_start_signal:idx_end_signal], low_perc_value)
						high_perc_tmp = np.percentile(signals_collection[signal]['signal'].iloc[idx_start_signal:idx_end_signal], high_perc_value)
						if low_perc_tmp < low_perc[traceNo]: low_perc[traceNo] = low_perc_tmp
						if high_perc_tmp > high_perc[traceNo]: high_perc[traceNo] = high_perc_tmp

						fig.update_yaxes(title_text=label, row=int(traceNo), col=1,
										 range=[low_perc[traceNo], high_perc[traceNo]],
										 secondary_y=False)

						continue
					#
					# if signal == 'hypo_10_60' and airgo_alignment_options ==1:
					#
					# 	if idx_start_airgo_4Hz is None: # first airgo signal in this loop, need to find indices:
					# 		idx_start_airgo_4Hz = np.where(signals_collection['airgo_4Hz'].index >= time_segment_start)[0][0]
					# 		idx_end_airgo_4Hz = np.where(signals_collection['airgo_4Hz'].index < time_segment_end)[0][-1]
					#
					# 	for timeshift in range(shift_start, shift_end, shift_step):
					# 		trace = go.Scattergl(x=signals_collection['airgo_4Hz'].index[idx_start_airgo_4Hz:idx_end_airgo_4Hz] + timedelta(seconds=timeshift),
					# 							 y=signals_collection['airgo_4Hz'][signal].iloc[idx_start_airgo_4Hz:idx_end_airgo_4Hz],
					# 							 name=signal + ' shifted: ' + str(timeshift).rjust(4, ' '), hoverinfo='x+y',
					# 							 opacity=0.8, mode='lines',
					# 							 line=style_settings['Line'][signal],
					# 							 visible=timeshift==0)
					# 		fig.add_trace(trace, int(traceNo), 1 )
					# 	continue
					#
					# if signal == 'rr_10s' and airgo_alignment_options ==1:
					#
					# 	if idx_start_airgo_4Hz is None: # first airgo signal in this loop, need to find indices:
					# 		idx_start_airgo_4Hz = np.where(signals_collection['airgo_4Hz'].index >= time_segment_start)[0][0]
					# 		idx_end_airgo_4Hz = np.where(signals_collection['airgo_4Hz'].index < time_segment_end)[0][-1]
					#
					# 	for timeshift in range(shift_start, shift_end, shift_step):
					# 		trace = go.Scattergl(x=signals_collection['airgo_4Hz'].index[idx_start_airgo_4Hz:idx_end_airgo_4Hz] + timedelta(seconds=timeshift),
					# 							 y=signals_collection['airgo_4Hz'][signal].iloc[idx_start_airgo_4Hz:idx_end_airgo_4Hz],
					# 							 name=signal + ' shifted: ' + str(timeshift).rjust(4, ' '), hoverinfo='x+y',
					# 							 opacity=0.8, mode='lines',
					# 							 line=style_settings['Line'][signal],
					# 							 visible=timeshift==0)
					# 		fig.add_trace(trace, int(traceNo), 1 )
					# 	continue

				if sensor == 'AirGo_4Hz':
					if idx_start_airgo_4Hz is None:  # first airgo signal in this loop, need to find indices:
						idx_start_airgo_4Hz = np.where(signals_collection['airgo_4Hz'].index >= time_segment_start)[0][0]
						idx_end_airgo_4Hz = np.where(signals_collection['airgo_4Hz'].index < time_segment_end)[0][-1]

					trace = go.Scattergl(x = signals_collection['airgo_4Hz'].index[idx_start_airgo_4Hz:idx_end_airgo_4Hz],
										 y = signals_collection['airgo_4Hz'][signal].iloc[idx_start_airgo_4Hz:idx_end_airgo_4Hz],
										 name=label, hoverinfo='x+y', opacity=0.8,  mode='lines', line=style_settings['Line'][signal])
					low_perc_tmp = np.percentile(
						signals_collection['airgo_4Hz'][signal].iloc[idx_start_airgo_4Hz:idx_end_airgo_4Hz], 1)
					high_perc_tmp = np.percentile(
						signals_collection['airgo_4Hz'][signal].iloc[idx_start_airgo_4Hz:idx_end_airgo_4Hz], 99)
					if signal == 'hypo_10_60':
						low_perc_hypo = low_perc_tmp
						high_perc_hypo = high_perc_tmp
					else:
						if low_perc_tmp < low_perc[traceNo] : low_perc[traceNo] = low_perc_tmp
						if high_perc_tmp > high_perc[traceNo]: high_perc[traceNo] = high_perc_tmp

				if sensor == 'AirGo_10Hz':
					if idx_start_airgo_10Hz is None:  # first airgo signal in this loop, need to find indices:
						idx_start_airgo_10Hz = np.where(signals_collection['airgo_10Hz'].index >= time_segment_start)[0][0]
						idx_end_airgo_10Hz = np.where(signals_collection['airgo_10Hz'].index < time_segment_end)[0][-1]

					trace = go.Scattergl(x = signals_collection['airgo_10Hz'].index[idx_start_airgo_10Hz:idx_end_airgo_10Hz],
										 y = signals_collection['airgo_10Hz'][signal].iloc[idx_start_airgo_10Hz:idx_end_airgo_10Hz],
										 name=label, hoverinfo='x+y', opacity=0.8, mode='lines', line=style_settings['Line'][signal])

					low_perc_tmp = np.percentile(signals_collection['airgo_10Hz'][signal].iloc[idx_start_airgo_10Hz:idx_end_airgo_10Hz], low_perc_value)
					high_perc_tmp = np.percentile(signals_collection['airgo_10Hz'][signal].iloc[idx_start_airgo_10Hz:idx_end_airgo_10Hz], high_perc_value)
					# this is a 'manual fix' for 2nd axis for hypo_10_60, if more 2nd axis will follow this can be done better, more automatic.
					if signal == 'hypo_10_60':
						low_perc_hypo = low_perc_tmp
						high_perc_hypo = high_perc_tmp
					else:
						if low_perc_tmp < low_perc[traceNo] : low_perc[traceNo] = low_perc_tmp
						if high_perc_tmp > high_perc[traceNo]: high_perc[traceNo] = high_perc_tmp

				if sensor == 'Bedmaster':
					idx_start_signal = np.where(signals_collection[signal].index >= time_segment_start)[0][0]
					idx_end_signal = np.where(signals_collection[signal].index < time_segment_end)[0][-1]

					trace = go.Scattergl(x = signals_collection[signal].index[idx_start_signal: idx_end_signal],
										 y = signals_collection[signal]['signal'].iloc[idx_start_signal: idx_end_signal],
										 name=label, hoverinfo='x+y', opacity=0.8, mode='lines', line=style_settings['Line'][signal])

					low_perc_tmp = np.percentile(signals_collection[signal]['signal'].iloc[idx_start_signal:idx_end_signal], low_perc_value)
					high_perc_tmp = np.percentile(signals_collection[signal]['signal'].iloc[idx_start_signal:idx_end_signal], high_perc_value)
					if low_perc_tmp < low_perc[traceNo] : low_perc[traceNo] = low_perc_tmp
					if high_perc_tmp > high_perc[traceNo]: high_perc[traceNo] = high_perc_tmp

				if sensor == 'HRV':

					# idx_start_signal = np.where(signals_collection[signal].index >= time_segment_start)[0][0]
					# idx_end_signal = np.where(signals_collection[signal].index < time_segment_end)[0][-1]

					trace = go.Scattergl(x = signals_collection[signal].index[idx_start_signal: idx_end_signal],
										 y = signals_collection[signal]['signal'].iloc[idx_start_signal: idx_end_signal],
										 name=label, hoverinfo='x+y', opacity=0.8, mode='markers', marker=dict(color='red'))


				if signal == 'SPO2%':
					print('here')
					fig.add_trace(trace, int(traceNo), 1, secondary_y = False )
					# fig.update_yaxes(title_text="SPO2%", range=[90, 95], row=int(traceNo), col=1, secondary_y=False)
				elif signal == 'hypo_10_60':
					fig.add_trace(trace, int(traceNo), 1, secondary_y = True )
					# fig.update_yaxes(title_text="hypopnea ind.", range=[0, 1.5], row=int(traceNo), col=1, secondary_y=True)

				else:
					fig.add_trace(trace, int(traceNo), 1, secondary_y=False)

		except Exception as e:
			print(e)
			print('Error occured. Potentially no data for chosen time window available. Or unexpected. Continue with next timesegment')
			continue


		except Exception as e:
			print(e)
			print(
				'Error occured. Potentially no data for chosen time window available. Or unexpected. Continue with next timesegment')
			continue

		for itrace in range(max_trace + 1):
			fig.update_yaxes(title_text=ylabel_trace[itrace], row=int(itrace), col=1,
							 range=[low_perc[itrace], high_perc[itrace]],
							 secondary_y=False)

		# manual update for 2nd axis for hypopnea curve:
		fig.update_yaxes(title_text='hypopnea ind.', row=int(2), col=1,
						 range=[0, 1.5],
						 secondary_y=True)

		#### slider part
		if airgo_alignment_options:
			# Create and add slider
			steps = []
			for i in range(num_of_bedmaster_traces):
				step = dict(
					method="restyle",
					label=str(range(shift_start, shift_end, shift_step)[i]),
					args=["visible", [False] * len(fig.data)],
				)
				# step["args"][1][i] = True  # Toggle i'th trace to "visible"		# airgo band
				# # step["args"][1][num_of_airgo_traces+i] = True
				# step["args"][1][num_of_airgo_traces: num_of_airgo_traces+3] = [True]*3   # accX, Y and Z. do not move.
				# step["args"][1][3+num_of_airgo_traces+i] = True  # Toggle i'th trace to "visible"    # airgo hypo
				# step["args"][1][3 + 2*num_of_airgo_traces + i] = True  # Toggle i'th trace to "visible"    # airgo RR10s
				# step["args"][1][3+3*num_of_airgo_traces:] = [True] * (
				# 			len(fig.data) - (3*num_of_airgo_traces+3))  # Toggle all non-airgo traces as true for all steps.
				# steps.append(step)

				step["args"][1][:6] = [True] * 6  # all airgo traces to true.

				for iBedmasterTrace in range(bedmaster_signals_in_plot):
					step["args"][1][
						6 + iBedmasterTrace * num_of_bedmaster_traces + i] = True  # Toggle i'th trace to "visible"		# bedmaster 2 HR

				step["args"][1][:6] = [True]*6   # all airgo traces to true.

				for iBedmasterTrace in range(bedmaster_signals_in_plot):
					step["args"][1][
						6 + iBedmasterTrace* num_of_bedmaster_traces + i] = True  # Toggle i'th trace to "visible"		# bedmaster 2 HR


				# step["args"][1][6+i] = True  # Toggle i'th trace to "visible"									# bedmaster 1 SPO2
				# step["args"][1][6 + num_of_bedmaster_traces + i] = True  # Toggle i'th trace to "visible"		# bedmaster 2 HR
				# step["args"][1][6 + 2*num_of_bedmaster_traces + i] = True  # Toggle i'th trace to "visible"		# bedmaster 3 BP1
				# step["args"][1][6 + 3*num_of_bedmaster_traces + i] = True  # Toggle i'th trace to "visible"		# bedmaster 4 BP2
				# step["args"][1][6 + 4*num_of_bedmaster_traces + i] = True  # Toggle i'th trace to "visible"		# bedmaster 5 BP3
				# step["args"][1][6 + 5*num_of_bedmaster_traces + i] = True  # Toggle i'th trace to "visible"		# bedmaster 6 BP4
				# step["args"][1][6 + 6*num_of_bedmaster_traces + i] = True  # Toggle i'th trace to "visible"		# bedmaster 7 BP5
				steps.append(step)

			sliders = [dict(
				active=np.where(np.array(range(shift_start, shift_end, shift_step)) >= 0)[0][0],
				currentvalue={"prefix": "timeshift (sec): "},
				pad={"t": 50},
				steps=steps
			)]
			#### end of slider part
			fig.update_layout(
				sliders=sliders)

			# fig.layout.xaxis.showspikes = True
			# fig.layout.xaxis.spikemode = 'across'
			# fig.layout.xaxis.spikesnap = 'cursor'
			# fig.layout.xaxis.showline = True
			# fig.layout.xaxis2.showspikes = True
			# fig.layout.xaxis2.spikemode = 'across'
			# fig.layout.xaxis2.spikesnap = 'cursor'
			# fig.layout.xaxis2.showline = True


			# plot(fig,
			# 	 filename='C:/Users/wg984/Dropbox (Partners HealthCare)/ICU-SLEEP-MATERIALS/TimeAlignmentAirGoBedmaster/Plots/{}/subject_{}_multipleSignals_{}.html'.format(
			# 		 subject, subject, i_timesegment), auto_open=False)
			plot(fig,
				 filename='/home/wolfgang/repos/ICU-Sleep/Plots/{}/subject_{}_multipleSignals_{}.html'.format(
					 subject, subject, i_timesegment), auto_open=False)
			f = open("plot_log.txt", "a")
			f.write(str(subject) + ': subject_{}_multipleSignals_{}.html created.'.format(subject, i_timesegment))
			f.close()

			plot(fig, filename='M:/Projects/AirGoSleepStaging/TimeAlignmentAirGoBedmasterNew/Plots/{}/subject_{}_multipleSignals_{}.html'.format(subject, subject, i_timesegment), auto_open=False)
			# plot(fig, filename='E:/Dropbox (Partners HealthCare)/ICU-SLEEP-MATERIALS/TimeAlignmentAirGoBedmaster/Plots/{}/subject_{}_multipleSignals_{}.html'.format(subject, subject, i_timesegment), auto_open=False)


			f = open("plot_log.txt", "a")
			f.write(str(subject) + ': subject_{}_multipleSignals_{}.html created.'.format(subject, i_timesegment))
			f.close()

def ICUsignals_visualizationMultiline(signals_collection, style_settings=None, dayNo=0, dayt='night', subject=''):
	################################################
	################    PLOT CODE  	################
	################################################
	### change for displaying full night or full day.
	# Night: 8pm - 8am
	# Day: 8am - 8pm

	dates = getDatesOfSignal(signals_collection)
	if dayNo == 999:  # 'use all dates':
		dates = dates
	else:
		dates = [dates[dayNo]]

	for date in dates:

		hours = get_hours(dayt)

		trace_setting = signals_collection['traces']
		traces_specified = np.unique(trace_setting.iloc[0, :])

		subplots = plotly.subplots.make_subplots(rows=len(traces_specified) * 12, cols=1, shared_xaxes=False,
												 shared_yaxes=True, print_grid=False, vertical_spacing=0)

		layout = get_layout(date)

		fig = go.FigureWidget(subplots, layout)

		traces = {}

		for traceNo in traces_specified:

			# plot an hour of signal each line:
			for ihour, hour in enumerate(hours[:-1]):

				[datetimeMin, datetimeMax] = datetimeMinAndMax4Line(date, hour, hours[ihour + 1])

				# which signals for which trace:
				signals_for_trace = trace_setting.where(trace_setting == traceNo).dropna(axis=1).columns
				# append all signals specified for a certain trace:
				for signal in signals_for_trace:

					signal_data = signals_collection[signal]

					# limit signal_data to only 1 hour:
					signal_data = signal_data.loc[
								  (signal_data.datetime >= datetimeMin) & (signal_data.datetime <= datetimeMax), :]

					# version with traces dict necessary?
					# traces[traceNo].append( go.Scatter(x=signal_data['datetime'], y=signal_data[signal], name = signal, hoverinfo = 'x+y', line = dict(color = '#17BECF'), opacity = 0.8, mode='lines')	)
					# for now, just add it to figure:

					if ihour == 0:  # only show label for first axis.
						trace = go.Scattergl(x=signal_data['datetime'], y=signal_data[signal], legendgroup=signal,
											 name=signal, hoverinfo='x+y', opacity=0.8, mode='lines',
											 line=style_settings['Line'][signal])  # , line = dict(color = '#17BECF')
					else:
						trace = go.Scattergl(x=signal_data['datetime'], y=signal_data[signal], legendgroup=signal,
											 showlegend=False, hoverinfo='x+y', opacity=0.8, mode='lines',
											 line=style_settings['Line'][signal])  # , line = dict(color = '#17BECF')

					# except:
					# 	print('style failed for ' + signal)
					# 	trace = go.Scattergl(x=signal_data['datetime'], y=signal_data[signal], name = signal, hoverinfo = 'x+y', opacity = 0.8, mode='lines')	# default version, e.g. if no style defined.
					fig.add_trace(trace, int(ihour + 1), 1)

		fig = update_layoutMultiline(fig, hours)
		fig['layout'].update(height=1000, width=2000, title='subject: {}, '.format(subject) + dayt + ' ' + str(date))

		plot(fig, filename='subject_{}_{}_{}.html'.format(subject, dayt, date))


def update_layoutMultiline(fig, hours):
	for hour in range(1, 13):
		fig['layout']['xaxis' + str(hour)].update(showticklabels=False)
		fig['layout']['yaxis' + str(hour)].update(
			title=str(hours[hour - 1]) + ':00')  # ,scaleanchor = "x", scaleratio = 0.2
	return fig



def get_layout(date):
	layout = go.Layout(xaxis=dict(ticks='',
								  showticklabels=False,
								  #         rangeselector=dict(
								  #             buttons=list([
								  #                 dict(count=1,
								  #                      label='1h',
								  #                      step='hour',
								  #                      stepmode='backward'),
								  #                 dict(count=6,
								  #                      label='6h',
								  #                      step='hour',
								  #                      stepmode='backward'),
								  #                 dict(step='all')
								  #             ])
								  #         ),
								  #         rangeslider=dict(
								  #             visible = True
								  #         ),
								  # type='date'
								  ),
					   autosize=False,
					   width=100,
					   height=100,
					   margin=go.layout.Margin(
						   l=50,
						   r=50,
						   b=100,
						   t=100,
						   pad=4),
					   # title=go.layout.title(
					   #    text=str(date),
					   #    xref='paper',
					   #    x=0),
					   showlegend=True)

	layout = go.Layout( xaxis=dict( ticks='',
		showticklabels=False,
#         rangeselector=dict(
#             buttons=list([
#                 dict(count=1,
#                      label='1h',
#                      step='hour',
#                      stepmode='backward'),
#                 dict(count=6,
#                      label='6h',
#                      step='hour',
#                      stepmode='backward'),
#                 dict(step='all')
#             ])
#         ),
#         rangeslider=dict(
#             visible = True
#         ),
		# type='date'
		),
		autosize = False,
		width=100,
		height=100,
		margin=go.layout.Margin(
		l=50,
		r=50,
		b=100,
		t=100,
		pad=4),
		# title=go.layout.title(
	 #    text=str(date),
	 #    xref='paper',
	 #    x=0),
		showlegend=True)


	return layout


def datetimeMinAndMax4Line(date, hour0, hour1):
	datetimeMin = pd.to_datetime(date).replace(hour=hour0)
	datetimeMax = pd.to_datetime(date).replace(hour=hour1)
	if hour1 == 0:
		datetimeMax = datetimeMax + timedelta(days=1)
	elif hour1 <= 8:  # happens in night mode & that starts already a day earlier.
		datetimeMin = datetimeMin + timedelta(days=1)
		datetimeMax = datetimeMax + timedelta(days=1)

	return [datetimeMin, datetimeMax]


def getDatesOfSignal(signals_collection, dayt='night'):
	# now assumption: get dates from AirGo recording as multiline is used for respiration now. if not airgo, other lines for other signals need to be added.

	# label of AirGo is hardcoded in that instance, might result in errors. Default values are Girth and AirGo for labels. 

	try:
		data = signals_collection['Girth']
	except:
		data = signals_collection['AirGo']

	dates = data.datetime.apply(lambda x: x.date())
	dates = np.unique(dates)

	# if recording end before 8am, do not use last day for day plot
	if (dayt == 'day') & (data.datetime.iloc[-1].hour <= 8):
		dates = dates[:-1]

	return dates


def get_hours(dayt):
	if dayt == 'night':
		hours = [20, 21, 22, 23, 0, 1, 2, 3, 4, 5, 6, 7, 8]
	elif dayt == 'day':
		hours = np.arange(8, 21).tolist()
	return hours


def MapHRVCategoryToFeatures(signalCategory):
	# signalCategory is a string: 'HRV_TimeDomain' or 'HRV_FreqDomain' or 'HRV_Poincare' or 'HRV_Entropy'
	if signalCategory == 'HRV_TimeDomain':
		features = ['NNmean', 'NNmedian', 'NNmode', 'NNvariance', 'NNskew', 'NNkurt', 'NNiqr', 'SDNN', 'RMSSD', 'pnn50']
	elif signalCategory == 'HRV_FreqDomain':
		features = ['vlf', 'lf', 'hf', 'ttlpwr']
	elif signalCategory == 'HRV_Poincare':
		features = ['SD1', 'SD2']
	elif signalCategory == 'HRV_Entropy':
		features = ['SampEn', 'ApEn']

	return features


def set_PlotStyle(StyleType):
	# dash' options: ['solid', 'dot', 'dash', 'longdash', 'dashdot', 'longdashdot']

	# bit of manual work to do here: keys need to match the labels specified in 'signals_to_plot'

	if StyleType == 'A':
		Line = {
			# AirGo data:
			'band': dict(color=('rgb(0, 0, 204)'), dash='solid', width=1),
			'accx': dict(color=('rgb(0, 0, 190)'), dash='solid', width=1),
			'accy': dict(color=('rgb(150, 150, 0)'), dash='solid', width=1),
			'accz': dict(color=('rgb(33, 233, 33)'), dash='solid', width=1),
			'deriv1': dict(color=('rgb(50, 50, 224)'), dash='solid', width=1),
			'deriv2': dict(color=('rgb(100, 100, 244)'), dash='solid', width=1),
			'ventilation_3s': dict(color=('rgb(153, 51, 255)'), dash='dot', width=2),
			'ventilation_10s': dict(color=('rgb(153, 51, 255)'), dash='solid', width=2),
			'ventilation_60s': dict(color=('rgb(153, 51, 255)'), dash='dashdot', width=2),
			'hypo_10_60': dict(color=('rgb(170, 170, 170)'), dash='longdashdot', width=2),
			'movavg_1s': dict(color=('rgb(0, 0, 204)'), dash='dashdot', width=1),
			'movavg_1_2s': dict(color=('rgb(0, 0, 204)'), dash='dashdot', width=1),
			'movavg_2s': dict(color=('rgb(0, 0, 204)'), dash='dashdot', width=1),
			'movavg_3s': dict(color=('rgb(0, 0, 204)'), dash='dashdot', width=1),
			'movavg_5s': dict(color=('rgb(0, 0, 204)'), dash='dashdot', width=1),
			'movavg_10s': dict(color=('rgb(0, 0, 204)'), dash='dashdot', width=1),
			'movavg_60s': dict(color=('rgb(0, 0, 204)'), dash='dashdot', width=1),
			'rr_10s': dict(color=('rgb(238,130,238)'), dash='dashdot', width=1),
			'rr_60s': dict(color=('rgb(238,130,238)'), dash='longdashdot', width=1),
			# Bedmaster data:
			'SPO2%': dict(color=('rgb(0, 206, 209)'), dash='solid', width=2),
			'ART1S': dict(color=('rgb(153, 255, 51)'), dash='solid', width=2),
			'ART1M': dict(color=('rgb(102, 102, 255)'), dash='solid', width=2),
			'ART1D': dict(color=('rgb(255, 178, 102)'), dash='solid', width=2),
			'NBPS': dict(color=('rgb(153, 255, 51)'), dash='dashdot', width=4),  # Non invase blood pressure systolic
			# Non invase blood pressure systolic
			'NBPD': dict(color=('rgb(255, 178, 102)'), dash='dashdot', width=4),  # Non invase blood pressure diastolic
			# Non invase blood pressure diastolic
			'HR': dict(color=('rgb(204, 0, 0)'), dash='solid', width=2),  # Heart Rate
			# HRV data:
			'r_peaks': dict(color=('rgb(200,100,100'), dash=None, width=None),
			'HRV_TimeDomain': dict(color=('rgb(222, 96, 167)'), dash='dot', width=2),
			'HRV_FreqDomain': dict(color=('rgb(222, 96, 167)'), dash='dot', width=2),
			'HRV_Poincare': dict(color=('rgb(222, 96, 167)'), dash='dot', width=2),
			'HRV_Entropy': dict(color=('rgb(222, 96, 167)'), dash='dot', width=2),
		}

	style_settings = dict(Line=Line)

	return style_settings


if __name__ == '__main__':
	main()