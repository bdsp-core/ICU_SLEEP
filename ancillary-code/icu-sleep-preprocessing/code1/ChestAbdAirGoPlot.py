import pandas as pd
import numpy as np

# import hdf5storage

import plotly
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.io as pio
from plotly import tools
# plotly.io.orca.config.executable  = 'C:/Users/wg984/AppData/Local/conda/conda/envs/plotly3/orca_app/orca.exe'

import os
import datetime
import matplotlib.pyplot as plt
from scipy.signal import correlate
import time

#### PARAMETERS TO SET: 

subjectIDsel = [357]		# range(326,343) 			# subject/studyID
do_crosscorrelation = 1		# 1 if automatic alignment via cross correlation should be done.
do_manual_timeshift = 0		# 1 if you want to add a manual timeshift (i.e. when automatic alone failed)
minutes = 0#-66				# minutes to shift (- if AirGo should be shifted to the left, +if AirGo should be shifted to the right)
seconds = 0 # -28					# seconds to shift (- if AirGo should be shifted to the left, +if AirGo should be shifted to the right)
remove_durationSec = 0		# DEFAULT: 0. if a part of the AirGo needs to be removed, specify the number of seconds that should be removed. This might be needed if there is a break in the recording. Then it seems sometimes (not always!) PSG signal shows too little data for the break (when PSG respiration trace is totally flat).
remove_start_point = datetime.datetime(2019,4,4,3,15,0)		# if remove_durationSec is > 0, then also select the starting point from where x seconds (remove_durationSec) shall be removed.

# ad remove_durationSec:
# looks like recording stop in PSG can still cause troubles, even though EDF+ reader takes those into account. 
# we want to 'shift' time data sometimes from a certain point, e.g. 20 seconds: remove 20 seconds in break of PSG and shift all data after that 20sec 'to the left'.


# time.sleep(60*60)
subjectIDsel = [
 # '344',
 # '346',
 # '347',
 # '348',
 # '349',
 # '350',
 # '352',
 # '353',
 # '355',
 # '359',
 # '361',
 # '362',
 # '363',
 # '364',
 # '377',
 # '378',
 # '379',
 # '380',
 # '401',
 # '403',
 # '405',
 # '415',
 # '416',
 # '417',
 # '419',
 # '423',
 # '424',
 # '425',
 # '426',
 # '427',
 # '429',
 # '431',
 '433',
 '435',
 '440',
 '441',
 '449',
 '451',
 '452',
 '453',
 '462']

for subjectID in subjectIDsel: #range(163,164):

	# try:
	if 1:

		print(subjectID)

		savedir = 'M:/Projects/AirGoSleepStaging/TimeAlignedDataNew/AirGo_Files/'
		savedirForPlots = 'M:/Projects/AirGoSleepStaging/TimeAlignedDataNew/Plots/'

		strsubjectID = str(subjectID).zfill(3)
		
		# load AirGo file
		AirGoDir = 'C:/Users/wg984/Dropbox (Partners HealthCare)/AirGoSleepLabData/ShareWithDavidKuller/Recordings_StudyID_4David/'
		AirGoFile = 'David_Air'+ strsubjectID +'.csv'

		AirGoData = pd.read_csv( os.path.join(AirGoDir,AirGoFile))

		AirGoData = AirGoData.drop(['date','time','DateNum'],axis=1)
		AirGoData = AirGoData[['DateTime','Band','accX','accY','accZ','CRCStatus']]
		AirGoData.DateTime = pd.to_datetime(AirGoData.DateTime, infer_datetime_format=1)

		# load PSG file
		# PSGDir = 'C:/Users/wg984/Dropbox (Partners HealthCare)/AirGoSleepLabData/ShareWithDavidKuller/TimeAlignedData/PSG_Files/'
		PSGDir = 'M:/Projects/AirGoSleepStaging/TimeAlignedDataNew/PSG_Files/'
		PSGFile = 'PSG_Air' + strsubjectID + '_10Hz.csv'

		PSGData = pd.read_csv( os.path.join(PSGDir,PSGFile))
		PSGData.DateTime = pd.to_datetime(PSGData.DateTime, infer_datetime_format=1)

		PSGStartTime = PSGData.DateTime.iloc[0]
		PSGEndTime = PSGData.DateTime.iloc[-1]


		# pick 3 hour slot:
		ABD_selection = PSGData.ABD[(PSGData.DateTime >= PSGStartTime) & (PSGData.DateTime <= PSGStartTime + datetime.timedelta(hours=3))          ]
		CHEST_selection = PSGData.ABD[(PSGData.DateTime >= PSGStartTime) & (PSGData.DateTime <= PSGStartTime + datetime.timedelta(hours=3))          ]
		AirGo_selection = AirGoData.Band[(AirGoData.DateTime >= PSGStartTime) & (AirGoData.DateTime <= PSGStartTime + datetime.timedelta(hours=3))          ]
		if ABD_selection.shape[0] > AirGo_selection.shape[0]:
			ABD_selection = ABD_selection.iloc[:-1]
			CHEST_selection= CHEST_selection.iloc[:-1]


		if do_crosscorrelation:	
			# compute CrossCorr and Lag:
			crosscorr = correlate(ABD_selection.values, AirGo_selection.values, mode='same')
			lag = np.argmax(crosscorr)


			AirGoOffset = len(ABD_selection.values)/2 - lag
			AirGoOffsetInSeconds = AirGoOffset/10
			AirGoOffsetInSeconds
			
			plt.figure()
			plt.plot(crosscorr)
			plt.savefig( os.path.join(savedirForPlots,'AirGo_PSG_' + strsubjectID + '_CrossCorrelation'))
			plt.close()

			AirGoData.DateTime = AirGoData.DateTime - datetime.timedelta(seconds = AirGoOffsetInSeconds)

		if do_manual_timeshift == 1:
			print('manual shift on')
			# additional timeshift. usually workflow works like this: first round don't do any timeshift. look at results. for those where manual timeshift is needed, specify it for each subject and then run this code again with do_manual_timeshift = 1.
			manualShiftInSeconds = minutes*60+seconds
			AirGoData.DateTime = AirGoData.DateTime + datetime.timedelta(seconds = manualShiftInSeconds)

			if remove_durationSec != 0:
				print('remove part of the AirGo signal on!')

				AirGoData = AirGoData.mask((AirGoData.DateTime >= remove_start_point) & (AirGoData.DateTime < remove_start_point + datetime.timedelta(seconds=remove_durationSec)  ))
				AirGoData = AirGoData.dropna(axis=0,how='all')

				AirGoData.DateTime.loc[AirGoData.DateTime >= remove_start_point] = AirGoData.DateTime.loc[AirGoData.DateTime >= remove_start_point] - datetime.timedelta(seconds = remove_durationSec)


		# restrict AirGo Data to PSG start and End
		AirGoData = AirGoData[(AirGoData.DateTime >= PSGStartTime - datetime.timedelta(minutes = 15) ) & (AirGoData.DateTime <= PSGEndTime + datetime.timedelta(minutes = 15) ) ]

		fig = tools.make_subplots(rows=3, cols=1, shared_xaxes=True, shared_yaxes=False) # , subplot_titles=('HR', 'BP diastolic')

		traces = []

		trace_ABD = go.Scatter(x=PSGData.DateTime, y=PSGData.ABD, name = 'ABD', hoverinfo = 'x+y', line = dict(color = 'blue', width = 1), opacity = 0.8 )
		trace_CHEST = go.Scatter(x=PSGData.DateTime, y=PSGData.CHEST, name = 'CHEST', hoverinfo = 'x+y', line = dict(color = 'green', width = 1), opacity = 0.8 )

		trace_AirGo = go.Scatter(x=AirGoData.DateTime, y=AirGoData.Band, name = 'AirGo', hoverinfo = 'x+y', line = dict(color = 'orange', width = 1), opacity = 0.8 )

		trace_Apnea = go.Scatter(x=PSGData.DateTime, y=PSGData.Apnea, name = 'Apnea', hoverinfo = 'x+y', line = dict(color = 'DeepSkyBlue', width = 1), opacity = 0.8 )
		trace_Sleep = go.Scatter(x=PSGData.DateTime, y=PSGData.Stage, name = 'Stage', hoverinfo = 'x+y', line = dict(color = 'Crimson', width = 1), opacity = 0.8 )


		fig.append_trace(trace_Apnea, 1, 1)
		fig.append_trace(trace_Sleep, 1, 1)

		fig.append_trace(trace_AirGo, 2, 1)

		fig.append_trace(trace_ABD, 3, 1)
		fig.append_trace(trace_CHEST, 3, 1)

		fig['layout']['yaxis1'].update(tickvals=[5,4,3,2,1], ticktext =['W','R','N1','N2','N3'])


		plot(fig, filename = savedirForPlots+'AirGo_PSG_Annot_' + strsubjectID + '_Alignment.html', auto_open=False)

		AirGoData.to_csv( os.path.join(savedir,'AirGo_'+strsubjectID+'.csv'), index=False)

	# except:
	# 	print('error for this one')
	# 	continue



	