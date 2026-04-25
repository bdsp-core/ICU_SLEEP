import numpy as np
import pandas as pd
from datetime import datetime
from DateTime_DateNum_Conversion import DateTime_to_DateNum
import re
import os
from AirGoRaw_ProcessTime import dropNonRecordingParts, drop_duplicates, AirGoRaw_ProcessTime, AirGo_toDateTime
import matplotlib.pyplot as plt

def main():

    Log = []

    savefolder = '//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/data_analysis/AirGo/airgo_research/'

    # subjectIDsToProcess = np.concatenate([np.arange(31,38), np.array([39]), np.arange(42, 190)])
    # subjectIDsToProcess = [89]
    # subjectIDsToProcess = [63, 89]
    # 108,
    subjectIDsToProcess =[114, 121, 155, 156,  165, 173, 175, 176, 177, 180, 181, 182, 183, 185, 186, 187, 188,
    189]

    subjectIDsToProcess = [187,188,189]

    for subjectID in subjectIDsToProcess:
        all_airgo_files_for_subject = []
        strsubjectID = str(subjectID).zfill(3)

        if os.path.exists(os.path.join(savefolder, 'airgo_'+strsubjectID+'.csv')):
            continue

        # if 1:
        try:
            print('subjectID:{}'.format(subjectID))
            
            # get AirGo File from enrolled patients directory:
            enrolledPDir = '//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/enrolled_subjects/'
            try:
                patientFolder = enrolledSubjectFolderForSubjectID(strsubjectID)
            except:
                continue

            AirGoDir = enrolledPDir + patientFolder + '/AirGo/'
            print(os.listdir(AirGoDir))
            AirGoFiles = [x for x in os.listdir(AirGoDir) if strsubjectID in x and '.csv' in x]

            if len(AirGoFiles) == 0:
                print('No AirGo File.')
                Log.append('{}:No AirGoFile'.format(subjectID))
                continue

            for AirGoFile in AirGoFiles:
                print(AirGoFile)
                airgo_research = airgo_rawv5_to_research(os.path.join(AirGoDir, AirGoFile))
                all_airgo_files_for_subject.append(airgo_research)

            airgo_research = pd.concat(all_airgo_files_for_subject)
            airgo_research = airgo_research.sort_values('DateTime')

            # plt.plot(airgo_research.DateTime, airgo_research.Band)
            # plt.show()

            airgo_research.to_csv( os.path.join(savefolder, 'airgo_'+strsubjectID+'.csv'), index = False)

        except Exception as e:
            print("error for this subject, continue with next.")
            print(e)
            print('\n')
            continue

    print(Log)

def airgo_rawv5_to_research(filepath):

    AirgoRaw = pd.read_csv(filepath, skiprows = 1)
    AirgoRaw.columns = AirgoRaw.columns.str.strip()

    # drop OpenBelt At Begin And End Of Recording
    AirgoRaw = dropNonRecordingParts(AirgoRaw)

    AirgoRaw = drop_duplicates(AirgoRaw)
    AirgoRaw = AirGoRaw_ProcessTime(AirgoRaw)

    AirgoRaw.DateTime = AirgoRaw.DateTime.apply(lambda x: str(x))

    AirgoRaw.drop('date', axis = 1, inplace = True)
    AirgoRaw.drop('time', axis = 1, inplace = True)
    AirgoRaw.drop('DateNum', axis=1, inplace=True)

    try:
        AirgoRaw = AirgoRaw[['DateTime', 'accX' , 'accY',  'accZ',  'Band', 'CRCStatus']]
    except:
        AirgoRaw = AirgoRaw[['DateTime', 'accX' , 'accY',  'accZ',  'band', 'CRCStatus']]
        AirgoRaw.columns = ['DateTime', 'accX' , 'accY',  'accZ',  'Band', 'CRCStatus']

    return AirgoRaw

def enrolledSubjectFolderForSubjectID(str_subject):

	enrolledPDir = '//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/enrolled_subjects/'
	patientDirs = os.listdir(enrolledPDir)
	regex=re.compile(".*"+str_subject+".*")
	patientFolder = [m.group(0) for l in patientDirs for m in [regex.search(l)] if m]

	if len(patientFolder) == 1:
		patientFolder = patientFolder[0]

	else: raise ValueError('not 1 patientfolder found.')

	return patientFolder

if __name__=='__main__':
    main()