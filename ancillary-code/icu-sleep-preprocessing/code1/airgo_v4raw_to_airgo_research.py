import numpy as np
import pandas as pd
import re
import datetime
import matplotlib.pyplot as plt
import os

def main():

    savefolder_single = '//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/data_analysis/AirGo/airgo_research_single_files'
    savefolder_merged = '//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/data_analysis/AirGo/airgo_research'
    enrolled = '//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/enrolled_subjects/'
    enrolled_folders = os.listdir(enrolled)
    v4_files = []
    for folder in enrolled_folders[4:5]: # 170]:
        print(folder)
        file_found = 0
        all_airgo_files_for_subject = []
        if '.db' in folder: continue
        if '.txt' in folder: continue
        files = os.listdir(os.path.join(enrolled, folder, 'airgo'))
        #     print(files)
        for file in files:
            if '_Raw.csv' in file:
                file_found = 1
                v4_file = os.path.join(enrolled, folder, 'airgo', file)
                savepath = os.path.join(savefolder_single, file)
                # do transform:
                airgo_research = airgo_v4raw_to_research(v4_file, savepath)
                all_airgo_files_for_subject.append(airgo_research)

        if file_found:
            airgo_research = pd.concat(all_airgo_files_for_subject)
            print(airgo_research.head)
            plt.figure()
            plt.plot(airgo_research['DateTime'], airgo_research['Band'])
            # plt.show()
            plt.savefig('airgo_rawv4_'+re.split('_', folder)[0]+'.jpg')
            airgo_research.to_csv(os.path.join(savefolder_merged,'airgo_rawv4_'+re.split('_', folder)[0]+'.csv'))


def airgo_v4raw_to_research(filepath, savepath):

    AirGo_data = pd.read_csv(filepath)
    AirGo_data.columns = AirGo_data.columns.str.strip()
    starting_date = re.search("\d\d\d\d-\d\d-\d\d \d\d\d\d\d\d", filepath)
    starting_date = starting_date.group(0)
    starting_date = datetime.datetime.strptime(starting_date, '%Y-%m-%d %H%M%S')
    AirGo_data['DateTime'] = [starting_date + datetime.timedelta(seconds=x / 10) for x in
                              AirGo_data.sampleNumber.values]

    AirGo_data = AirGo_data[['DateTime', 'rawBeltValue', 'accX', 'accY', 'accZ']]
    AirGo_data.columns = ['DateTime', 'Band', 'accX', 'accY', 'accZ']

    # drop duplicate:
    dup = AirGo_data.duplicated(subset=['DateTime', 'Band'])
    AirGo_data = AirGo_data.mask(dup).dropna(axis=0, how='all')

    # detect all open belt areas
    OpenBeltIdx = np.where(AirGo_data['Band'] > 60000)[0]

    LastIdxOpenBeltAtBeginOfRecording = np.where(np.diff(OpenBeltIdx) > 1)
    if LastIdxOpenBeltAtBeginOfRecording[0].shape[0] > 0:
        LastIdxOpenBeltAtBeginOfRecording = LastIdxOpenBeltAtBeginOfRecording[0][0]
        LastIdxOpenBeltAtBeginOfRecording = OpenBeltIdx[LastIdxOpenBeltAtBeginOfRecording]
        if any(AirGo_data['Band'][:LastIdxOpenBeltAtBeginOfRecording] <60000): LastIdxOpenBeltAtBeginOfRecording = 0
    else: LastIdxOpenBeltAtBeginOfRecording = 0

    FirstIdxOpenBeltAtEndOfRecording = np.where(np.diff(OpenBeltIdx) > 1)
    if FirstIdxOpenBeltAtEndOfRecording[0].shape[0]>0:
        FirstIdxOpenBeltAtEndOfRecording = FirstIdxOpenBeltAtEndOfRecording[0][-1]
        FirstIdxOpenBeltAtEndOfRecording = OpenBeltIdx[FirstIdxOpenBeltAtEndOfRecording + 1]
        if any(AirGo_data['Band'][FirstIdxOpenBeltAtEndOfRecording:] <60000): FirstIdxOpenBeltAtEndOfRecording = -1
    else: FirstIdxOpenBeltAtEndOfRecording = -1

    AirGo_data = AirGo_data.iloc[LastIdxOpenBeltAtBeginOfRecording + 1:FirstIdxOpenBeltAtEndOfRecording, :]

    AirGo_data['CRCStatus'] = np.nan

    AirGo_data.to_csv(savepath, index=False)

    return AirGo_data

if __name__ == '__main__':
    main()