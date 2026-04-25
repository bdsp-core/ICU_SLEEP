import numpy as np
import pandas as pd
from datetime import datetime 
from DateTime_DateNum_Conversion import DateTime_to_DateNum
import re
import os

def str_subjectID(subjectID):
	#e.g. change '2' to '002'

	subjectID = str(subjectID)
	if len(subjectID) == 1:
		subjectID = '00'+subjectID
	elif len(subjectID) == 2:
		subjectID = '0'+subjectID
	return subjectID

def main():

	# AirgoRaw = pd.read_csv('//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/enrolled_subjects/036_Hasle_John/AirGo/AirGo_27fd43ceafd6_2019-02-04_18_19_49_raw.csv', skiprows = 10)
	# AirgoRaw.columns = ['date', 'time', 'accX', 'accY', 'accZ','band','CRCStatus']
	
	# TEMP: only select subset:
	# AirgoRaw = AirgoRaw.iloc[:200,:]
	AirGoRaw_ProcessTime_SleepLab()

	# subjectIDsToProcess = [49,71,75]
	# AirGoRaw_ProcessTime_ICUSleep(subjectIDsToProcess)

def AirGoRaw_ProcessTime_SleepLab():

	
	AirGoDir = 'C:/Users/wg984/Dropbox (Partners HealthCare)/AirGoSleepLabData/Recordings_StudyID/'

	savedir = 'C:/Users/wg984/Dropbox (Partners HealthCare)/AirGoSleepLabData/Recordings_StudyID_4Matlab/' #  'C:/Users/wg984/Dropbox (Partners HealthCare)/AirGoSleepLabData/Data_Analysis/' + room + '/'
	savedirDavid = 'C:/Users/wg984/Dropbox (Partners HealthCare)/AirGoSleepLabData/ShareWithDavidKuller/Recordings_StudyID_4David/'
	# AirGoDir = 'C:/Users/wg984/Dropbox (Partners HealthCare)/AirGoSleepLabData/CompressionCheck/209/209 Compressed/'
	# savedir = AirGoDir

	for AirGoFile in os.listdir(AirGoDir):

		if not os.path.exists(savedir + 'Mat_' + AirGoFile):
	# currently, code is set up so that it processes all airgo files for all specified rooms.
	# for room in rooms:

	# 	AirGoFiles = os.listdir(AirGoSleepLabDir + room + '/')
	
	# # temp:
	# for i in range(1,4):
	# 	if i == 1:
	# 		room = '203'
	# 		AirGoFile = 'AirGo_f718ba223cc5_2019-02-21_18_18_30_raw.csv'
	# 	elif i == 2:
	# 		room = '204'
	# 		AirGoFile = 'AirGo_5d0bb0cfd4e3_2019-02-21_18_31_57_raw.csv'
	# 	elif i == 3:
	# 		room = '205'
	# 		AirGoFile = 'AirGo_8f1a608e96cd_2019-02-21_18_18_08_raw.csv'


	# for AirGoFile in AirGoFiles:

			try:

				print(AirGoFile)
				# load AirGo data:
				AirgoRaw = pd.read_csv(AirGoDir + AirGoFile, skiprows = 1)
				AirgoRaw.columns = AirgoRaw.columns.str.strip()

				# print(AirgoRaw.head())
				# process AirGo Data:

				# drop OpenBelt At Begin And End Of Recording
				AirgoRaw = dropNonRecordingParts(AirgoRaw)

				AirgoRaw = drop_duplicates(AirgoRaw)
				AirgoRaw = AirGoRaw_ProcessTime(AirgoRaw)
				# print(AirgoRaw.head())


				AirgoRaw.DateTime = AirgoRaw.DateTime.apply(lambda x: str(x))
				# print(AirgoRaw.head())
				#re-order columns:
								# save AirGo data
				if not os.path.exists(savedirDavid):
					os.makedirs(savedirDavid)
				# AirgoRaw = AirgoRaw[['DateNum', 'DateTime', 'accX', 'accY', 'accZ', 'Band', 'CRCStatus']]
				AirgoRaw.to_csv(savedirDavid + 'David_' + AirGoFile , index  = False, header = True)
			

				AirgoRaw.drop('date', axis = 1, inplace = True)
				AirgoRaw.drop('time', axis = 1, inplace = True)

				# save AirGo data
				if not os.path.exists(savedir):
					os.makedirs(savedir)

				# AirgoRaw.to_csv(savedir + AirGoFile, index  = False, header = True)

				#re-order columns:

				AirGoMat = AirgoRaw[['DateNum','accX', 'accY', 'accZ', 'Band']]
				AirGoMat.to_csv(savedir + 'Mat_' + AirGoFile , index  = False, header = True)

			# except Exception as e:
			except:
				print(AirGoFile + ': unsolved irregularities in signal.')
				continue

def dropNonRecordingParts(AirgoRaw):
	'''
	we only want to remove those at the beginning and end of recording. therefore remove only
	part in beginning (until first time below 4050) and end (after last time <4050) of recording.
	'''	

	# detect all open belt areas
	amplitude_threshold = 4050
	OpenBeltIdx = np.where(AirgoRaw['Band'] > amplitude_threshold)[0]

	LastIdxOpenBeltAtBeginOfRecording = np.where(np.diff(OpenBeltIdx) > 1)
	if LastIdxOpenBeltAtBeginOfRecording[0].shape[0] > 0:
		LastIdxOpenBeltAtBeginOfRecording = LastIdxOpenBeltAtBeginOfRecording[0][0]
		LastIdxOpenBeltAtBeginOfRecording = OpenBeltIdx[LastIdxOpenBeltAtBeginOfRecording]
		if any(AirgoRaw['Band'][:LastIdxOpenBeltAtBeginOfRecording] <amplitude_threshold): LastIdxOpenBeltAtBeginOfRecording = 0
	else: LastIdxOpenBeltAtBeginOfRecording = 0

	FirstIdxOpenBeltAtEndOfRecording = np.where(np.diff(OpenBeltIdx) > 1)
	if FirstIdxOpenBeltAtEndOfRecording[0].shape[0]>0:
		FirstIdxOpenBeltAtEndOfRecording = FirstIdxOpenBeltAtEndOfRecording[0][-1]
		FirstIdxOpenBeltAtEndOfRecording = OpenBeltIdx[FirstIdxOpenBeltAtEndOfRecording + 1]
		if any(AirgoRaw['Band'][FirstIdxOpenBeltAtEndOfRecording:] <amplitude_threshold): FirstIdxOpenBeltAtEndOfRecording = -1
	else: FirstIdxOpenBeltAtEndOfRecording = -1

	AirgoRaw = AirgoRaw.iloc[LastIdxOpenBeltAtBeginOfRecording + 1:FirstIdxOpenBeltAtEndOfRecording, :]

	return AirgoRaw


def drop_duplicates(AirgoRaw):
	dup = AirgoRaw.duplicated(subset=['date','time','Band'])
	AirgoRaw = AirgoRaw.mask(dup).dropna(axis = 0, how='all')
	
	# also drop invalid entries:
	idx_crc = np.where(AirgoRaw.columns=='CRCStatus')[0][0]
	if not all(AirgoRaw.CRCStatus.isna()):
		AirgoRaw = AirgoRaw.mask(AirgoRaw.CRCStatus == 'Invalid').dropna(axis = 0, how='all')

		# if both neighboring entires are invalid, we'll add invalid flag for the middle entry too as this seems to be a missing
		# flag, visual manual check suggests this behavior.
		invalid = np.where(AirgoRaw.CRCStatus.iloc[:-2] == 'InvalidFlag')[0]

		if invalid.shape[0]>0:
			# check each neighbor of an invalid entry if it is between two invalid entries, if so, add to list invalid2.
			invalid2 = [x+1 for x in invalid if pd.isna(AirgoRaw.CRCStatus.iloc[x+1]) and AirgoRaw.CRCStatus.iloc[x+2]=='InvalidFlag']

			if len(invalid2)>0:
				AirgoRaw.iloc[invalid2, idx_crc] = 'InvalidFlag'
			#
			# for i_candidate in invalid_candidate:
			# 	if AirgoRaw.CRCStatus.iloc[i_candidate-1] == 'InvalidFlag' and AirgoRaw.CRCStatus.iloc[i_candidate +1] == 'InvalidFlag':
			# 		AirgoRaw.iloc[i_candidate,idx_crc] = 'InvalidFlag'

		AirgoRaw = AirgoRaw.mask(AirgoRaw.CRCStatus == 'InvalidFlag').dropna(axis=0, how='all')

	
	return AirgoRaw

def AirGoRaw_ProcessTime_ICUSleep(subjectIDsToProcess):

	Log = []

	for subjectID in subjectIDsToProcess:
		try:
			print('subjectID:{}'.format(subjectID))

			strsubjectID = str_subjectID(subjectID)
			# get AirGo File from enrolled patients directory:
			enrolledPDir = '//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/enrolled_subjects/'	
			try:
				patientFolder = enrolledSubjectFolderForSubjectID(strsubjectID)
			except:
				continue

			AirGoDir = enrolledPDir + patientFolder + '/AirGo/'

			##### todo:
			AirGoFiles = [x for x in os.listdir(AirGoDir) if strsubjectID in x]

			if len(AirGoFiles) == 0:
				print('No AirGo File.')
				Log.append('{}:No AirGoFile'.format(subjectID))
				continue

			elif len(AirGoFiles) == 1:
				AirgoRaw = pd.read_csv(os.path.join(enrolledPDir, patientFolder,'AirGo',AirGoFiles[0]),skiprows = 1)
			# check if there are more than 1 airgo files. check solution for breath version.
			elif len(AirGoFiles)>1:
				# NOTE: i do not want to order the files here because later i perform a check if data is monotonically increasing (data quality check as some airgo recordings had issues here.)
				# also i think this is multiple file occurence does not happen very often.
				print('more than 1 airgo file for this subject, get read in and concatenated in the following order (manual check if this is correct order:')
				print(AirGoFiles)
				Log.append('{}:more than 1 AirGoFile'.format(subjectID))
				AirgoRaw = []
				# load the actual AirGo File.
				for AirGoFile in AirGoFiles:
					AirgoRaw.append(pd.read_csv(os.path.join(enrolledPDir, patientFolder,'AirGo',AirGoFile),skiprows = 1))
			
			AirgoRaw = pd.concat(AirgoRaw,sort=False)
			AirgoRaw.columns = AirgoRaw.columns.str.strip()

			# drop OpenBelt At Begin And End Of Recording
			AirgoRaw = dropNonRecordingParts(AirgoRaw)
			AirgoRaw = drop_duplicates(AirgoRaw)

			AirgoRaw = AirGoRaw_ProcessTime(AirgoRaw)

			AirgoRaw.drop('date', axis = 1, inplace = True)
			AirgoRaw.drop('time', axis = 1, inplace = True)

			# AirgoRaw.to_csv('//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/data_analysis/036/AirGo/AirGoRawV1.csv', index  = False, header = True)
			
			AirgoRaw.DateTime = AirgoRaw.DateTime.apply(lambda x: str(x))

			#re-order columns:
			try:
				AirgoRaw = AirgoRaw[['DateNum', 'DateTime', 'accX', 'accY', 'accZ', 'Band', 'CRCStatus']]
			except:
				AirgoRaw = AirgoRaw[['DateNum', 'DateTime', 'accX', 'accY', 'accZ', 'band', 'CRCStatus']]
				AirgoRaw.columns = ['DateNum', 'DateTime', 'accX', 'accY', 'accZ', 'Band', 'CRCStatus']

			# AirGoDict = {'AirGoRaw':AirgoRaw.values,'AirGoRawVariables':['DateNum', 'DateTime', 'accX', 'accY', 'accZ', 'band', 'CRCStatus']}
			# hdf5storage.savemat('//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/data_analysis/036/AirGo/AirGoRawV1.mat', AirGoDict,  matlab_compatible=True)

			# V2, same format as bedmaster.
			# AirgoRaw.drop('DateTime', axis = 1).to_csv('//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/data_analysis/036/AirGo/AirGoRawV1_5.csv', index  = False, header = True)

			# AirGoDict = {'AirGoRaw':AirgoRaw.drop('DateTime', axis = 1).values,'AirGoRawVariables':['DateNum', 'accX', 'accY', 'accZ', 'band', 'CRCStatus']}
			# hdf5storage.savemat('//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/data_analysis/036/AirGo/AirGoRawV2.mat', AirGoDict,  matlab_compatible=True)

			saveDir = os.path.join('//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/data_analysis',strsubjectID,'AirGo')
			if not os.path.exists(saveDir):
				os.makedirs(saveDir)

			AirgoRaw.to_csv( os.path.join(saveDir,'AirGo10Hz.csv'), index  = False, header = True)

			pd.DataFrame(Log).to_csv('//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/data_analysis/DataProcessingLog/AirGoRaw_ProcessTime_'+str(subjectIDsToProcess)+'.csv')

			# V2csv alone.
			# AirgoRaw.DateTime.to_csv('//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/data_analysis/036/AirGo/AirGoRawV2.csv', index  = False, header = True)

		except:
			print("ERROR FOR THIS SUBJECT. CONTINUE WITH NEXT SUBJECT.")
			continue

def enrolledSubjectFolderForSubjectID(str_subject):

	enrolledPDir = '//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/enrolled_subjects/'	
	patientDirs = os.listdir(enrolledPDir)
	regex=re.compile(".*"+str_subject+".*")
	patientFolder = [m.group(0) for l in patientDirs for m in [regex.search(l)] if m]

	if len(patientFolder) == 1:
		patientFolder = patientFolder[0]

	else: raise ValueError('not 1 patientfolder found.')

	return patientFolder


def AirGoRaw_ProcessTime(AirgoRaw):
	# very-safe way to convert airgo device time to datetime/datenum. process each entry. is quite slow but could handle breaks or anything like that if it happens.
	# fast would be to just convert first datetime and then automatically append '10Hz datetime rate'.

	# input: pd DataFrame of raw AirGo recording, i.e. with following columns:
	# AirgoRaw.columns = ['date', 'time', 'accX', 'accY', 'accZ','band','CRCStatus']

	# output: DataFrame, appended with columns 'DateTime' and 'DateNum'

	AirgoRaw['DateTime'] = AirGo_toDateTime(AirgoRaw.date, AirgoRaw.time)
	# print('DateTime done')

	AirgoRaw['DateNum'] = DateTime_to_DateNum(AirgoRaw['DateTime'].tolist())
	# print('DateNum done')

	# check if time is monotonically increases. it's possible that it is not because of time drifts. if AirGo gets reconnect to iPad, time resets.

	diff = AirgoRaw['DateNum'].diff()
	TimeIrregularity = diff.where(diff<0).dropna()

	i_loop = 0
	while TimeIrregularity.shape[0] >= 1:
		max_loops = 100
		i_loop += 1
		for time_irregularity_idx in TimeIrregularity.index:
			# if a neighbor of the time_irregularity has been removed, remove the time irregularity too:
			if any([time_irregularity_idx-1 not in AirgoRaw.index, time_irregularity_idx+1 not in AirgoRaw.index]):
				# print('drop neighbor)')
				AirgoRaw.drop(time_irregularity_idx, axis=0, inplace=True)
			diff = AirgoRaw['DateNum'].diff()
			TimeIrregularity = diff.where(diff < 0).dropna()

		if i_loop > max_loops:
			break
	# remove the data before the time irregularities, if still some left
	if TimeIrregularity.shape[0] >= 1:
		for time_irregularity_idx in TimeIrregularity.index:
			idx_to_drop = AirgoRaw.loc[:time_irregularity_idx][(AirgoRaw.loc[:time_irregularity_idx, 'DateNum'] > AirgoRaw.loc[time_irregularity_idx, 'DateNum'])]
			idx_to_drop = idx_to_drop.index
			AirgoRaw.drop(idx_to_drop, axis=0, inplace=True)
		diff = AirgoRaw['DateNum'].diff()
		TimeIrregularity = diff.where(diff < 0).dropna()

	if TimeIrregularity.shape[0] >= 1:
		print('TimeIrregularity.shape[0]')
		print(TimeIrregularity.shape[0])
		print('do not process this one for now.')
		import pdb; pdb.set_trace()
		return []
	# while TimeIrregularity.shape[0] >= 1:
	#
	# 	TimeIrrSel = TimeIrregularity.index[0]
	#
	# 	if TimeIrrSel/AirgoRaw.shape[0] > 0.99:
	# 		# often, when putting off the belt, button gets pressed and if iPad is close, it connects and resets time. therefore, if the index is at the very end of the signal
	# 		# (i.e. afeter 99% of recording time, just dismiss the rest of the data
	# 		print('One time irregularity in AirGo, at the end of the recording. Dismiss the end of the recording.')
	# 		AirgoRaw = AirgoRaw.iloc[:TimeIrrSel,:]
	# 	elif TimeIrrSel/AirgoRaw.shape[0] < 0.01:
	# 		print('One time irregularity in AirGo, at the beginning of the recording. Dismiss the beginning of the recording.')
	# 		AirgoRaw = AirgoRaw.iloc[TimeIrrSel+1:,:]
	# 	else:
	# 		print(TimeIrregularity.index)
	# 		print(AirgoRaw.shape[0])
	# 		raise ValueError('Time irregularity in AirGo Data. Not at the end or beginning of the recording. Not implemented yet.')
	#
	# 	diff = AirgoRaw['DateNum'].diff()
	# 	TimeIrregularity = diff.where(diff<0).dropna()

	# if TimeIrregularity.shape[0] == 1:
	# 	if TimeIrregularity.index/AirgoRaw.shape[0] > 0.99:
	# 		# often, when putting off the belt, button gets pressed and if iPad is close, it connects and resets time. therefore, if the index is at the very end of the signal
	# 		# (i.e. afeter 99% of recording time, just dismiss the rest of the data
	# 		print('One time irregularity in AirGo, at the end of the recording. Dismiss the end of the recording.')
	# 		AirgoRaw = AirgoRaw.iloc[:TimeIrregularity.index[0],:]
	# 	elif TimeIrregularity.index/AirgoRaw.shape[0] < 0.01:
	# 		print('One time irregularity in AirGo, at the beginning of the recording. Dismiss the beginning of the recording.')
	# 		AirgoRaw = AirgoRaw.iloc[TimeIrregularity.index[0]+1:,:]
	# 	else:
	# 		print(TimeIrregularity.index)
	# 		print(AirgoRaw.shape[0])
	# 		raise('Time irregularity in AirGo Data. Not at the end of the recording. Not implemented yet.')
	# elif TimeIrregularity.shape[0] > 1:

	# 	raise('More than one time irregularities in AirGo Data. Not implemented yet.')


	return AirgoRaw

def AirGo_toDateTime(date, time):
	# inputs: two columns of dataframe (series), with the date and time respectively, for each timepoint.
	# output: new column with python datetime format.
	# DateTime = pd.Series(np.zeros([len(date),]))

	# for entry in range(len(date)):
	# 	if entry % 500 == 0:
	# 		print(entry)
	# 	DateTime.iloc[entry] = datetime.strptime(date.iloc[entry]+' '+time.iloc[entry],'%Y-%m-%d %H:%M:%S.%f')
	# return DateTime

	date = date.apply(lambda x: x+' ')
	DateTime = pd.to_datetime(date+time, infer_datetime_format = 1)

	return DateTime

if __name__ == '__main__':
	main()
