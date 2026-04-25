import numpy as np
import pandas as pd
import datetime
import os

# SEE JUPYTER NOTEBOOK

TimeAlignedOld = 'C:/Users/wg984/Dropbox (Partners HealthCare)/AirGoSleepLabData/ShareWithDavidKuller/TimeAlignedData/'
TimeAlignedNew = 'C:/Users/wg984/Dropbox (Partners HealthCare)/AirGoSleepLabData/ShareWithDavidKuller/TimeAlignedDataNew/'
TimeAlignedNew = 'M:/Projects/AirGoSleepStaging/TimeAlignedDataNew/'

SleepLabList = pd.read_csv('C:/Users/wg984/Dropbox (Partners HealthCare)/AirGoSleepLabData/MasterList_Main_1.23.20.csv')

for index in SleepLabList.index[165:166]: # :371]: # [370:372]:
    study = SleepLabList.loc[index]

    if (not isinstance(study.SID,float)) and (study.IncludedInStudy == True):
        # try:
        print(study.SID)
        # get offset:
        annotationfilePath = os.path.join(study.Path, 'annotations.csv')
        annotation = pd.read_csv(annotationfilePath)
        # import pdb
        # pdb.set_trace()
        epoch_first_sleepstage = annotation[annotation.event.str.contains('Sleep_stage')].iloc[0].epoch
        SecBeforeFirstSleepStage = (epoch_first_sleepstage-1)*30.
        
        # load airgo, apply change, save:
        airgo = pd.read_csv(os.path.join(TimeAlignedOld, 'AirGo_Files/AirGo_'+str(study.SID)[-3:]+'.csv'))
        airgo.DateTime = pd.to_datetime(airgo.DateTime, infer_datetime_format=1)
        airgo.DateTime += datetime.timedelta(seconds=SecBeforeFirstSleepStage)
        
        airgo.to_csv(os.path.join(TimeAlignedNew, 'AirGo_Files/AirGo_'+str(study.SID)[-3:]+'.csv'), index=False)
        airgo = airgo[['DateTime','accX','accY','accZ','Band','CRCStatus']]
        airgo.to_csv(os.path.join(TimeAlignedNew, 'AirGo_Files_FormatBB/AirGo_'+str(study.SID)[-3:]+'.csv'), index=False)
        
        print('successfully done.')

            # # load PSG, apply change, save:
            # psg = pd.read_csv(os.path.join(TimeAlignedOld, 'PSG_Files/PSG_'+str(study.SID)+'.csv'))
            # psg.DateTime = pd.to_datetime(psg.DateTime, infer_datetime_format=1)
            # psg.DateTime += datetime.timedelta(seconds=SecBeforeFirstSleepStage)
            # psg.to_csv(os.path.join(TimeAlignedNew, 'PSG_Files/PSG_'+str(study.SID)+'.csv'), index=False)

            # # load PSG, apply change, save:
            # psg = pd.read_csv(os.path.join(TimeAlignedOld, 'PSG_Files/PSG_'+str(study.SID)+'_10Hz.csv'))
            # psg.DateTime = pd.to_datetime(psg.DateTime, infer_datetime_format=1)
            # psg.DateTime += datetime.timedelta(seconds=SecBeforeFirstSleepStage)
            # psg.to_csv(os.path.join(TimeAlignedNew, 'PSG_Files/PSG_'+str(study.SID)+'_10Hz.csv'), index=False)

            # # load EKG, apply change, save:
            # psg = pd.read_csv(os.path.join(TimeAlignedOld, 'PSG_Files/PSG_'+str(study.SID)+'_EKG.csv'))
            # psg.DateTime = pd.to_datetime(psg.DateTime, infer_datetime_format=1)
            # psg.DateTime += datetime.timedelta(seconds=SecBeforeFirstSleepStage)
            # psg.to_csv(os.path.join(TimeAlignedNew, 'PSG_Files/PSG_'+str(study.SID)+'_EKG.csv'), index=False)

            
            # annotationfilePath = os.path.join(study.Path, 'annotations.csv')
            # annotation = pd.read_csv(annotationfilePath)
            # annotation.to_csv( os.path.join(TimeAlignedNew,'Annotations',study.SID+'_annotations.csv'), index = False)
            
            
        # except Exception as e:
        #     print('error for ' + str(study.SID))
        #     print(e)
        #     continue