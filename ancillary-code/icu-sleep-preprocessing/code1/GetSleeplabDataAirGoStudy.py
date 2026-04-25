import pandas as pd
import numpy as np
import os
import datetime
import h5py
import scipy.io as sio
import time
import shutil

# see GetSleeplabDataAirGoStudy.ipynb


# time.sleep(60*60)

SleeplabListFile = 'C:/Users/wg984/Dropbox (Partners HealthCare)/AirGoSleepLabData/MasterList_Main_1.23.20.csv'
SleeplabList = pd.read_csv(SleeplabListFile)

# saveDir = 'C:/Users/wg984/Wolfgang/AirGo_SleepStaging/PSG_csvExtracts/'
saveDir = 'C:/Users/wg984/Dropbox (Partners HealthCare)/AirGoSleepLabData/ShareWithDavidKuller/TimeAlignedDataNew/PSG_Files/'
saveDir = 'M:/Projects/AirGoSleepStaging/TimeAlignedDataNew/PSG_Files/'
logfile_path = 'M:/Projects/AirGoSleepStaging/TimeAlignedDataNew/Log.csv'
saveDirAnnotations = 'M:/Projects/AirGoSleepStaging/TimeAlignedDataNew/Annotations/'

for studyID in range(7, 8): #  467 [455]: # range(387,467): #missing_List:  # SleepLabList.index:

	# if os.path.exists(os.path.join(saveDir,'PSG_Air'+str(studyID).zfill(3)+'_10Hz.csv')):
	# 	continue

	logfile = pd.read_csv(logfile_path)
	logfile_study = pd.DataFrame([], columns = ['studyID','all_signals_available','code_successful'])
	logfile_study['studyID'] = [studyID]

	print(studyID)
	# study = SleeplabList.loc[index]
	study = SleeplabList.where(SleeplabList.SID == 'Air'+str(studyID).zfill(3)).dropna(how='all').squeeze()

	if not isinstance(study.SID, float):

		if study.IncludedInStudy == 0:
			continue

		# print(study)

		try:
			# if 1:
			EdfFileName = study.Path.split('natus_data\\')[1]
			SignalFile = 'M:/Datasets_ConvertedData/sleeplab/natus_data/' + EdfFileName + '/Signal_' + EdfFileName + '.mat'
			LabelsFile = 'M:/Datasets_ConvertedData/sleeplab/natus_data/' + EdfFileName + '/Labels_' + EdfFileName + '.mat'
			AnnotationFile = 'M:/Datasets_ConvertedData/sleeplab/natus_data/' + EdfFileName + '/annotations.csv'

			# copy annotation file to new folder:
			# shutil.copyfile(AnnotationFile, os.path.join(saveDirAnnotations, 'annotations_'+study.SID+'.csv'))

			with h5py.File(LabelsFile,'r') as ffl:
				sleep_stage = ffl['stage'][()]
				apnea = ffl['apnea'][()]
				# features = ffl['features']
				ffl.close()

				print('available sleep stages:')
				print(np.unique(sleep_stage))

				# break

			with h5py.File(SignalFile,'r') as ff:

				hdr = ff['hdr']
				signal_labels = hdr['signal_labels'][:]
				channel_names = [ ''.join(list(map(chr, ff[signal_labels[i,0]][:]))) for i in range(signal_labels.shape[0]) ]
				channel_names = [channel.upper() for channel in channel_names]
				s = ff['s'][()]
				s = np.transpose(s);

				year = int(np.squeeze(ff['recording']['year']))
				month = int(np.squeeze(ff['recording']['month']))
				day = int(np.squeeze(ff['recording']['day']))
				hour = int(np.squeeze(ff['recording']['hour']))
				if (hour >= 7) and (hour <=10):         # 'typo' by sleep techs
					hour = hour + 12
				minute = int(np.squeeze(ff['recording']['minute']))
				second = int(np.squeeze(ff['recording']['second']))
				millisecond = int(np.squeeze(ff['recording']['millisecond']))
				fs = int(np.squeeze(ff['recording']['samplingrate']))

				ff.close()

			assert(all(np.in1d(['CHEST', 'ABD', 'SPO2', 'PR', 'PULSEQUALITY'], channel_names))), 'Not all signals available!'
			logfile_study['all_signals_available'] = [1]

			data = pd.DataFrame()
			signals = []
			for signal in ['CHEST', 'ABD', 'SPO2', 'PR', 'PULSEQUALITY', 'PTAF', 'CFLOW', 'SNORE']:
				if signal not in channel_names: continue
				signals.append(signal)
				signal_channel = channel_names.index(signal)
				data[signal] =  s[signal_channel,:]



			# CHESTchannel = channel_names.index('CHEST')
			# ABDchannel = channel_names.index('ABD')
			# SPO2channel = channel_names.index('SPO2')
			# PRchannel = channel_names.index('PR')
			# PRqualitychannel = channel_names.index('PULSEQUALITY')


			recording_start = np.datetime64('{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}.{}'.format(year,month,day,hour,minute,second,millisecond))
			recording_start = pd.to_datetime(recording_start)

			# data = pd.DataFrame(columns=['DateTime','Epoch','CHEST','ABD','SPO2','PR','PRquality','EKG','Stage','Apnea'])

			# data['CHEST'] = s[CHESTchannel,:]
			# data['ABD'] = s[ABDchannel,:]
			# data['SPO2'] = s[SPO2channel,:]
			# data['PR'] = s[PRchannel,:]
			# data['PRquality'] = s[PRqualitychannel,:]

			del s

			data['Stage'] = sleep_stage
			data['Apnea'] = apnea

			# drop begin and end of recording with undefined sleep stage
			# for last batch of PSG airgo files, this is decommented as it's actually wrong because it shifts the timestart!
			# data = data.dropna(subset=['Stage'])

			data['DateTime'] = [recording_start + datetime.timedelta(seconds=sample/fs) for sample in range(data.shape[0])] #
			data['Epoch']   = [sample//(30*fs) for sample in range(data.shape[0])] #

			# save high resolution and EKG data:
			if 0:
				EKGchannel = channel_names.index('ECG-LA')
				data['EKG'] = s[EKGchannel,:]
				data.to_csv(os.path.join(saveDir,'PSG_'+study.SID+'.csv'), index = False)
				data[['DateTime','Epoch','EKG']].to_csv(os.path.join(saveDir,'PSG_'+study.SID+'_EKG.csv'), index = False)


			data_WDTIndex = data[['DateTime','Epoch','Stage','Apnea']+signals]
			del data
			data_WDTIndex = data_WDTIndex.set_index('DateTime')

			resampled1 = data_WDTIndex[signals].resample('0.1S').mean()
			resampled2 = data_WDTIndex[['Epoch','Stage','Apnea']].resample('0.1S').max()

			data10Hz = pd.concat([resampled1,resampled2],axis=1)

			if data10Hz[data10Hz.Epoch==0].shape[0] > data10Hz[data10Hz.Epoch==1].shape[0]:
				data10Hz = data10Hz.iloc[1:,:]
			maxEpoch = np.max(data10Hz.Epoch) # last epoch got truncated because of resampling, skip it.
			data10Hz = data10Hz.loc[data10Hz.Epoch<maxEpoch,:]

			data10Hz.to_csv(os.path.join(saveDir,'PSG_'+study.SID+'_10Hz.csv'), index = True)

			logfile_study['code_successful'] = [1]
			logfile = pd.concat([logfile, logfile_study])
			logfile.to_csv(logfile_path, index=False)


		except Exception as e:
			print('Error for this one.')
			print(e)
			continue











DoAlsoPlots = 0

print('DoAlsoPlots')
print(DoAlsoPlots)

if DoAlsoPlots:


	import pandas as pd
	import numpy as np

	import hdf5storage

	import plotly
	import plotly.graph_objs as go
	from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
	import plotly.io as pio
	from plotly import tools
	plotly.io.orca.config.executable  = 'C:/Users/wg984/AppData/Local/conda/conda/envs/plotly3/orca_app/orca.exe'


	import os
	import datetime
	import matplotlib.pyplot as plt
	from scipy.signal import correlate
	import time


	# select subject
	# subjectID = 1



	# time.sleep(60*60)

	for subjectID in range(128,340):

		try:

			print(subjectID)

			savedir = 'C:/Users/wg984/Wolfgang/AirGo_SleepStaging/AirGoFiles_TimeAlignedToPSG/'
			savedirForPlots = 'C:/Users/wg984/Dropbox (Partners HealthCare)/AirGo_PSG_TimeAlignment/Plots/'

			strsubjectID = str(subjectID).zfill(3)

			# load AirGo file
			AirGoDir = 'C:/Users/wg984/Dropbox (Partners HealthCare)/AirGoSleepLabData/ShareWithDavidKuller/Recordings_StudyID_4David/'
			AirGoFile = 'David_Air'+ strsubjectID +'.csv'
			AirGoData = pd.read_csv( os.path.join(AirGoDir,AirGoFile))

			AirGoData = AirGoData.drop(['date','time','DateNum'],axis=1)
			AirGoData = AirGoData[['DateTime','Band','accX','accY','accZ','CRCStatus']]
			AirGoData.DateTime = pd.to_datetime(AirGoData.DateTime, infer_datetime_format=1)

			# load PSG file
			PSGDir = saveDir = 'C:/Users/wg984/Dropbox (Partners HealthCare)/AirGoSleepLabData/ShareWithDavidKuller/TimeAlignedData/PSG_Files/'
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


			# compute CrossCorr and Lag:
			crosscorr = correlate(ABD_selection.values, AirGo_selection.values, mode='same')
			lag = np.argmax(crosscorr)


			AirGoOffset = len(ABD_selection.values)/2 - lag
			AirGoOffsetInSeconds = AirGoOffset/10
			AirGoOffsetInSeconds

			plt.figure()
			plt.plot(crosscorr)
			plt.savefig( os.path.join(savedirForPlots,'AirGo_PSG_' + strsubjectID + '_CrossCorrelation'))

			AirGoData.DateTime = AirGoData.DateTime - datetime.timedelta(seconds = AirGoOffsetInSeconds)

			# restrict AirGo Data to PSG start and End
			AirGoData = AirGoData[(AirGoData.DateTime >= PSGStartTime ) & (AirGoData.DateTime <= PSGEndTime)    ]

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

		except:
			print('error for this one')
			continue

















# import pandas as pd
# import numpy as np
# import os
# import hdf5storage as h5s
# import datetime

# # see GetSleeplabDataAirGoStudy.ipynb



# SleeplabListFile = 'C:/Users/wg984/Dropbox (Partners HealthCare)/AirGoSleepLabData/MasterList_Main_05.30.19.csv'
# SleeplabList = pd.read_csv(SleeplabListFile)

# saveDir = 'C:/Users/wg984/Wolfgang/AirGo_SleepStaging/SampleFile/'

# for index in np.arange(5,20):  # SleepLabList.index:

#     study = SleeplabList.loc[index]
#     print(study)
#     EdfFileName = study.Path.split('natus_data\\')[1]
#     # SignalFile = '//mad3/MGH-NEUR-OCDAC/Datasets_ConvertedData/sleeplab/natus_data/' + EdfFileName + '/Signal_' + EdfFileName + '.mat'
#     # LabelsFile = '//mad3/MGH-NEURO-CDAC/Datasets_ConvertedData/sleeplab/natus_data/' + EdfFileName + '/Labels_' + EdfFileName + '.mat'
#     # SignalFile = 'M:/Datasets_ConvertedData/sleeplab/natus_data/' + EdfFileName + '/Signal_' + EdfFileName + '.mat'
#     # LabelsFile = 'M:/Datasets_ConvertedData/sleeplab/natus_data/' + EdfFileName + '/Labels_' + EdfFileName + '.mat'

#     SignalFile = 'C:/Users/wg984/Wolfgang/AirGo_SleepStaging/MatFiles' + '/Signal_' + EdfFileName + '.mat'
#     LabelsFile = 'C:/Users/wg984/Wolfgang/AirGo_SleepStaging/MatFiles' + '/Labels_' + EdfFileName + '.mat'

#     ff = h5s.loadmat(SignalFile)
#     label = h5s.loadmat(LabelsFile)

#     channel_names = [ff['hdr'][0,i]['signal_labels'][0][0].upper().replace('EKG','ECG') for i in range(ff['hdr'].shape[1])]

#     CHESTchannel = channel_names.index('CHEST')
#     ABDchannel = channel_names.index('ABD')
#     SPO2channel = channel_names.index('SPO2')
#     EKGchannel = channel_names.index('ECG-LA')

#     s = ff['s']

#     # recording start
#     year = int(np.squeeze(ff['recording']['year']))
#     month = int(np.squeeze(ff['recording']['month']))
#     day = int(np.squeeze(ff['recording']['day']))
#     hour = int(np.squeeze(ff['recording']['hour']))
#     minute = int(np.squeeze(ff['recording']['minute']))
#     second = int(np.squeeze(ff['recording']['second']))
#     millisecond = int(np.squeeze(ff['recording']['millisecond']))

#     recording_start = np.datetime64('{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}.{}'.format(year,month,day,hour,minute,second,millisecond))
#     recording_start = pd.to_datetime(recording_start)

#     data = pd.DataFrame(columns=['DateTime','Epoch','CHEST','ABD','SPO2','EKG','Stage','Apnea'])

#     data['CHEST'] = s[CHESTchannel,:]
#     data['ABD'] = s[ABDchannel,:]
#     data['SPO2'] = s[SPO2channel,:]
#     data['EKG'] = s[EKGchannel,:]

#     del s

#     data['Stage'] = np.squeeze(label['stage'])
#     data['Apnea'] = np.squeeze(label['apnea'])

#     del label

#     # drop begin and end of recording with undefined sleep stage
#     data = data.dropna(subset=['Stage'])

#     fs = int(np.squeeze(ff['recording']['samplingrate']))
#     data['DateTime'] = [recording_start + datetime.timedelta(seconds=sample/fs) for sample in range(data.shape[0])] # 
#     data['Epoch']   = [sample//(30*fs) for sample in range(data.shape[0])] # 

#     data.to_csv(os.path.join(saveDir,study.SID+'.csv'), index = False)
#     data[['DateTime','Epoch','EKG']].to_csv(os.path.join(saveDir,study.SID+'_EKG.csv'), index = False)


#     data_WDTIndex = data[['DateTime','Epoch','CHEST','ABD','SPO2','Stage','Apnea']]
#     del data
#     data_WDTIndex = data_WDTIndex.set_index('DateTime')

#     resampled1 = data_WDTIndex[['CHEST','ABD','SPO2']].resample('0.1S').mean() 
#     resampled2 = data_WDTIndex[['Epoch','Stage','Apnea']].resample('0.1S').nearest()

#     data10Hz = pd.concat([resampled1,resampled2],axis=1)

#     if data10Hz[data10Hz.Epoch==0].shape[0] > data10Hz[data10Hz.Epoch==1].shape[0]:
#         data10Hz = data10Hz.iloc[1:,:]
#     maxEpoch = np.max(data10Hz.Epoch) # last epoch got truncated because of resampling, skip it.
#     data10Hz = data10Hz.loc[data10Hz.Epoch<maxEpoch,:]

#     data10Hz = data10Hz[['Epoch','CHEST','ABD','SPO2','Stage','Apnea']]
#     data10Hz.to_csv(os.path.join(saveDir,study.SID+'_10Hz.csv'), index = True)
    
