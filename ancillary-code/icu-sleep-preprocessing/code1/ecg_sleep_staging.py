import re
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import sys

sys.path.append('/home/wolfgang/repos/ICU-Sleep/code1')
from airgo_features import airgo_actigraphy_features

sys.path.append('/home/wolfgang/repos/sleep_research_io')
from sleep_research_functions import load_sleep_data, write_to_hdf5_file, read_in_routine

from tqdm import tqdm
from sleep_staging_functions import *
import traceback


def get_hrv_columns_to_add():

    hrv_cols_to_add = ['cpc_cntr_window',
     'cpc_hfc',
     'cpc_hfc_lfc_ratio',
     'cpc_lfc',
     'hrv_ac',
     'hrv_apen',
     'hrv_avgsqi',
     'hrv_btsdet',
     'hrv_dc',
     'hrv_fdflag',
     'hrv_hf',
     'hrv_iqr',
     'hrv_lf',
     'hrv_lfhf',
     'hrv_nn',
     'hrv_nnkurt',
     'hrv_nnmean',
     'hrv_nnmedian',
     'hrv_nnmode',
     'hrv_nnskew',
     'hrv_nnvariance',
     'hrv_pnn50',
     'hrv_rmssd',
     'hrv_rpeak',
     'hrv_sampen',
     'hrv_sd1',
     'hrv_sd1sd2',
     'hrv_sd2',
     'hrv_sdnn',
     'hrv_t_end',
     'hrv_t_start',
     'hrv_tdflag',
     'hrv_ttlpwr',
     'hrv_ulf',
     'hrv_vlf',
     'hrv_window_center']

    return hrv_cols_to_add


def main():


    # #### Sept 15. 
    # Do the following and combine into one 10Hz dataset:  
    # 1.) load NN data, apply sleep staging.  
    # 2.) load 10HZ HRV data.  
    # 3.) load 10Hz non-HRV data (most recent version).  

    # print('sleeeep')
    # import time
    # time.sleep(60*60*8)
    n_gpu = 4

    data_type = 'sleeplab'

    if data_type == 'icu':
        ### icu sleep data:

        dir_nn = '/media/mad3/Projects/ICU_SLEEP_STUDY/data/data_analysis/BMR_resampled_ECG_and_rpeaks'
        files_nn = os.listdir(dir_nn)
        dir_10hz_hrv = '/media/mad3/Projects/ICU_SLEEP_STUDY/Sleep_And_Breathing/icu_files_v2_hrv'
        files_10hz_hrv = os.listdir(dir_10hz_hrv)
        dir_10hz_research = '/media/mad3/Projects/ICU_SLEEP_STUDY/Sleep_And_Breathing/icu_files_step3_nohrv'
        files_10hz_research = os.listdir(dir_10hz_research)
        savedir = '/media/mad3/Projects/ICU_SLEEP_STUDY/Sleep_And_Breathing/icu_files_step_4'

    elif data_type == 'sleeplab':

        dir_nn = '/media/mad3/Projects/ICU_SLEEP_STUDY/Sleep_And_Breathing/ECG_and_rpeaks_sleeplab'
        files_nn = os.listdir(dir_nn)
        dir_10hz_hrv = '/media/mad3/Projects/ICU_SLEEP_STUDY/Sleep_And_Breathing/sleeplab_files_hrv'
        files_10hz_hrv = os.listdir(dir_10hz_hrv)
        dir_10hz_research = None
        files_10hz_research = None
        savedir =  '/media/mad3/Projects/ICU_SLEEP_STUDY/Sleep_And_Breathing/sleeplab_files_step4'



    if data_type == 'icu':

        if not os.path.exists(savedir):
            os.makedirs(savedir)

        new_fs = ecg_sleepstage_model_fs = 200

        print(f'# files_nn:            {len(files_nn)}')
        print(f'# files_10hz_hrv:      {len(files_10hz_hrv)}')
        print(f'# files_10hz_research: {len(files_10hz_research)}')
        print(f'# files SetDiff research and hrv: {len(set(files_10hz_research) - set(files_10hz_hrv))}')

        files_all_available = list(set(files_10hz_research).intersection(set(files_10hz_hrv)))
        files_all_available.sort()
        print(f'# files_all_available: {len(files_all_available)}')


        for file in tqdm(files_all_available):

            try:
                if os.path.exists(os.path.join(savedir, file)):
                    continue

                study_id = re.search('\d\d\d', file)[0]
                print(study_id)

                data_10hz, hdr, fs = read_in_routine(os.path.join(dir_10hz_research, file))
                data_nn, hdr_nn, fs_nn = read_in_routine(os.path.join(dir_nn, 'ECG_'+study_id+'.h5'))
                data_10hz_hrv, hdr_hrv, fs_hrv = read_in_routine(os.path.join(dir_10hz_hrv, file))

                data_10hz_hrv.rename({'nn': 'hrv_nn', 'r_peak': 'hrv_rpeak'}, axis=1, inplace=True)

                data_ecg_sleepstage = ecg_sleep_staging_routine_icusleep(data_nn, fs_nn, n_gpu=n_gpu)
                stage_pred_ecg_nn_10hz = data_ecg_sleepstage.stage_pred_ecg_nn.resample('100ms').max()

                data_10hz = data_10hz.join(stage_pred_ecg_nn_10hz, how='left')
                hrv_cols_to_add = get_hrv_columns_to_add()
                hrv_cols_available = [x for x in hrv_cols_to_add if x in data_10hz_hrv.columns]
                data_10hz = data_10hz.join(data_10hz_hrv[hrv_cols_available], how='left')
                data_10hz = data_10hz.loc[:,~data_10hz.columns.duplicated()]

                write_to_hdf5_file(data_10hz, os.path.join(savedir, file), hdr)

            except Exception as e:
                print(e)
                print(''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)))
                continue

    # for sleeplab, HRV data is the latest version, so code is a bit different:
    if data_type == 'sleeplab':

        if not os.path.exists(savedir):
            os.makedirs(savedir)

        new_fs = ecg_sleepstage_model_fs = 200

        print(f'# files_nn:            {len(files_nn)}')
        print(f'# files_10hz_hrv:      {len(files_10hz_hrv)}')

        files_all_available = files_10hz_hrv
        files_all_available.sort()
        print(f'# files_all_available: {len(files_all_available)}')

        for file in tqdm(files_all_available):

            try:
                if os.path.exists(os.path.join(savedir, file)):
                    continue

                study_id = re.search('\d\d\d', file)[0]
                print(study_id)

                data_nn, hdr_nn, fs_nn = read_in_routine(os.path.join(dir_nn, 'ECG_' + study_id + '.h5'))
                data_10hz, hdr, fs = read_in_routine(os.path.join(dir_10hz_hrv, file))

                data_10hz.rename({'nn': 'hrv_nn', 'r_peak': 'hrv_rpeak'}, axis=1, inplace=True)

                data_ecg_sleepstage = ecg_sleep_staging_routine_icusleep(data_nn, fs_nn, n_gpu=n_gpu)
                stage_pred_ecg_nn_10hz = data_ecg_sleepstage.stage_pred_ecg_nn.resample('100ms').max()

                data_10hz = data_10hz.join(stage_pred_ecg_nn_10hz, how='left')
                data_10hz = data_10hz.loc[:, ~data_10hz.columns.duplicated()]
                write_to_hdf5_file(data_10hz, os.path.join(savedir, file), hdr)

            except Exception as e:
                print(e)
                print(''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)))
                continue

if __name__ == '__main__':
    main()