import numpy as np
import pandas as pd
import re
import datetime
import matplotlib.pyplot as plt
import os


def main():

    # filepath = 'C:/Users/wg984/Wolfgang/repos/ICU-Sleep/data/001_2018_06_06pm_airgo breath AirGo 78a5043e9810 2018-06-06 152600_Breath.csv'
    # savepath = 'C:/Users/wg984/Wolfgang/repos/ICU-Sleep/data/sample_research_breath4.csv'
    # savefolder = '//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/data_analysis/AirGo/airgo_research_single_files'
    # airgo_v4_to_research(filepath, savepath)

    ### get all v4 breath files:
    savefolder_single = '//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/data_analysis/AirGo/airgo_research_single_files'
    savefolder_merged = '//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/data_analysis/AirGo/airgo_research'

    savepaths = []

    ### get all v4 breath files:
    enrolled = '//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/enrolled_subjects/'
    enrolled_folders = os.listdir(enrolled)
    v4_files = []
    templist = list(enrolled_folders[i] for i in [22])
    for folder in templist: # enrolled_folders[18,23,28,29]:
        # try:
        if 1:
            print(folder)
            file_found = 0
            all_airgo_files_for_subject = []
            if '.db' in folder: continue
            if '.txt' in folder: continue
            files = os.listdir(os.path.join(enrolled, folder, 'airgo'))
            print(files)
            for file in files:
                if '_Breath.csv' in file:
                    file_found = 1
                    v4_file = os.path.join(enrolled, folder, 'airgo', file)
                    savepath = os.path.join(savefolder_single, file)
                    # do transform:
                    airgo_research = airgo_v4_to_research(v4_file, savepath)
                    all_airgo_files_for_subject.append(airgo_research)

            if file_found:
                airgo_research = pd.concat(all_airgo_files_for_subject)
                print(airgo_research.head)
                # plt.figure()
                # plt.plot(airgo_research['DateTime'], airgo_research['Band'])
                # # plt.show()
                # plt.savefig('airgo_'+re.split('_', folder)[0]+'.jpg')
                airgo_research.to_csv(os.path.join(savefolder_merged,'airgo_'+re.split('_', folder)[0]+'.csv'), index=False)

        # except Exception as e:
        #     file1 = open("airgo_v4_breath_errorlog.txt", "a")
        #     file1.write('\n')
        #     file1.write(folder)
        #     file1.write(str(e))
        #     file1.close()
        #     continue

    #             v4_files.append()
    #             savepaths.append()
    #
    # for v4_file, savepath in zip(v4_files, savepaths):
    #     airgo_v4_to_research(v4_file, savepath)


def airgo_v4_to_research(filepath, savepath):
    AirGo_data = pd.read_csv(filepath)

    AirGo_data.columns = AirGo_data.columns.str.strip()
    print(AirGo_data.columns)
    # delete first entry because it has weird values, e.g. breathHigh = 0. also sampleTime+breathDuration is sometimes lower than sample time of second entry.
    AirGo_data.drop(0, 0, inplace=True)

    AirGo_breath = pd.DataFrame()

    sampleTime_beginning = AirGo_data['sampleTime']
    sampleTime_end = AirGo_data['sampleTime'] + AirGo_data['breathDuration']
    sampleTime_raw = pd.Series(np.zeros(2 * len(sampleTime_beginning)))
    sampleTime_raw.iloc[0::2] = sampleTime_beginning.values
    sampleTime_raw.iloc[1::2] = sampleTime_end.values

    girth = pd.Series(np.zeros(len(sampleTime_raw)))
    girth.iloc[0::2] = AirGo_data['breathLow'].values
    girth.iloc[1::2] = AirGo_data['breathHigh'].values

    accX = pd.Series(np.zeros(len(sampleTime_raw)))
    accX.iloc[0::2] = AirGo_data['accX'].values
    accX.iloc[1::2] = AirGo_data['accX'].values

    accY = pd.Series(np.zeros(len(sampleTime_raw)))
    accY.iloc[0::2] = AirGo_data['accY'].values
    accY.iloc[1::2] = AirGo_data['accY'].values

    accZ = pd.Series(np.zeros(len(sampleTime_raw)))
    accZ.iloc[0::2] = AirGo_data['accZ'].values
    accZ.iloc[1::2] = AirGo_data['accZ'].values

    # sample time in seconds:
    AirGo_breath['sampleTime'] = sampleTime_raw / 1000
    AirGo_breath['girth'] = girth
    AirGo_breath['accX'] = accX
    AirGo_breath['accY'] = accY
    AirGo_breath['accZ'] = accZ

    # create the DateTime array:

    AirGo_breath['sampleTime']

    try:
        starting_date = re.search("\d\d\d\d-\d\d-\d\d \d\d\d\d\d\d", filepath)
        starting_date = starting_date.group(0)
        starting_date = datetime.datetime.strptime(starting_date, '%Y-%m-%d %H%M%S')
    except:
        starting_date = re.search("\d\d\d\d-\d\d-\d\d \d\d_\d\d_\d\d", filepath)
        starting_date = starting_date.group(0)
        starting_date = datetime.datetime.strptime(starting_date, '%Y-%m-%d %H_%M_%S')



    DateTime = pd.Series(np.zeros(AirGo_breath.shape[0], ))
    DateTime.index = AirGo_breath.index

    for counter, sampleTime in enumerate(AirGo_breath['sampleTime']):
        DateTime.iloc[counter] = starting_date + datetime.timedelta(seconds=sampleTime)

    AirGo_breath['DateTime'] = DateTime

    AirGo_breath.columns = ['sampleTime', 'Band', 'accX', 'accY', 'accZ', 'DateTime']
    AirGo_breath = AirGo_breath[['DateTime', 'Band', 'accX', 'accY', 'accZ']]

    # drop duplicate:
    dup = AirGo_breath.duplicated(subset=['DateTime', 'Band'])
    AirGo_breath = AirGo_breath.mask(dup).dropna(axis=0, how='all')
    AirGo_breath = AirGo_breath.set_index('DateTime');

    AirGo_breath.index = AirGo_breath.index.round('100ms')
    AirGo_breath.reset_index(level=0, inplace=True)
    dup = AirGo_breath.duplicated(subset=['DateTime'])
    AirGo_breath.loc[dup,'DateTime'] = AirGo_breath.loc[dup,'DateTime'] + datetime.timedelta(seconds=0.1)

    AirGo_breath = AirGo_breath.set_index('DateTime')
    # resampling


    resampled = AirGo_breath.resample(datetime.timedelta(seconds=0.1)).interpolate(method='pchip', order=3,
                                                                                   limit_direction='forward', axis=0)
    resampled.reset_index(level=0, inplace=True)
    resampled = resampled[['DateTime', 'Band', 'accX', 'accY', 'accZ']]

    # detect all open belt areas
    OpenBeltIdx = np.where(resampled['Band'] > 60000)[0]

    LastIdxOpenBeltAtBeginOfRecording = np.where(np.diff(OpenBeltIdx) > 1)
    if LastIdxOpenBeltAtBeginOfRecording[0].shape[0] > 0:
        LastIdxOpenBeltAtBeginOfRecording = LastIdxOpenBeltAtBeginOfRecording[0][0]
        LastIdxOpenBeltAtBeginOfRecording = OpenBeltIdx[LastIdxOpenBeltAtBeginOfRecording]
        if any(resampled['Band'][:LastIdxOpenBeltAtBeginOfRecording] <60000): LastIdxOpenBeltAtBeginOfRecording = 0
    else: LastIdxOpenBeltAtBeginOfRecording = 0

    FirstIdxOpenBeltAtEndOfRecording = np.where(np.diff(OpenBeltIdx) > 1)
    if FirstIdxOpenBeltAtEndOfRecording[0].shape[0]>0:
        FirstIdxOpenBeltAtEndOfRecording = FirstIdxOpenBeltAtEndOfRecording[0][-1]
        FirstIdxOpenBeltAtEndOfRecording = OpenBeltIdx[FirstIdxOpenBeltAtEndOfRecording + 1]
        if any(resampled['Band'][FirstIdxOpenBeltAtEndOfRecording:] <60000): FirstIdxOpenBeltAtEndOfRecording = -1
    else: FirstIdxOpenBeltAtEndOfRecording = -1

    resampled = resampled.iloc[LastIdxOpenBeltAtBeginOfRecording + 1:FirstIdxOpenBeltAtEndOfRecording, :]

    resampled['CRCStatus'] = np.nan

    resampled.to_csv(savepath, index=False)

    # plt.figure()
    # plt.plot(AirGo_breath.index, AirGo_breath.Band)
    # plt.plot(resampled.DateTime, resampled.Band)
    # plt.title(filepath[15:])
    # plt.savefig(filepath.split('\\')[-1]+'.png')
    # plt.show()

    # AirGo_breath.reset_index(level=0, inplace=True)
    # plt.plot(AirGo_breath.DateTime[:1000], AirGo_breath.Band[:1000])
    # plt.plot(resampled.DateTime[:10000], resampled.Band[:10000])
    # plt.show()

    return resampled

if __name__ =='__main__':
    main()

