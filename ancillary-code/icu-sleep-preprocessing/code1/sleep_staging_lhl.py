import pandas as pd
import numpy as np
import os
import sys
import re
sys.path.append('/home/wolfgang/repos/AirGo_Apnea_Detection')
from apnea_detection_functions import apply_apnea_prediction_models

sys.path.append('/home/wolfgang/repos/ICU-Sleep/code1')
from airgo_features import compute_airgo_features
from sleep_staging_functions import apply_airgo_sleep_staging_models, apply_ecg_sleep_staging_models, resample_ecg_data_for_sleep_staging

sys.path.append('/home/wolfgang/repos/sleep_research_io')
from sleep_research_functions import read_in_routine, save_data_routine, write_to_hdf5_file, write_to_hdf5_file_single_array
from sleep_analysis_functions import *
from edw_functions import *
import time
import matplotlib.pyplot as plt


def select_overlapping_dt_stages_hlh(lhl_data_collection_airgo, lhl_data_collection_hrv):
    """
    Input: the data collection dictionaries containing the output of the sleep staging models.
    We want to select the data from HRV and Breathing/AirGo based sleepstaging where (datetime) both are available.
    """

    lhl_data_collection_overlap = {}
    stage_versions_airgo = [x.split('stage_pred_')[-1] for x in lhl_data_collection_airgo.keys() if 'stage_pred' in x]
    locs_airgo = [set(lhl_data_collection_airgo[f'loc_{stage_version}']) for stage_version in stage_versions_airgo]
    stage_versions_hrv = [x.split('stage_pred_')[-1] for x in lhl_data_collection_hrv.keys() if 'stage_pred' in x]
    locs_hrv = [set(lhl_data_collection_hrv[f'loc_{stage_version}']) for stage_version in stage_versions_hrv]
    locs_all = locs_airgo + locs_hrv
    dt_stages_all = list(set.intersection(*locs_all))
    dt_stages_all.sort()
    if len(dt_stages_all) == 0:
        return lhl_data_collection_overlap

    for stage_version in stage_versions_airgo:
        dt_stage_version = [pd.Timestamp(x) for x in lhl_data_collection_airgo[f'loc_{stage_version}']]
        keys_stage_version = [x for x in lhl_data_collection_airgo.keys() if stage_version in x]
        assert type(dt_stage_version[0]) == type(dt_stages_all[0]), 'Different DateTime Types. Might break np.isin().'
        match_boolean = np.isin(dt_stage_version, dt_stages_all)
        for key in keys_stage_version:
            lhl_data_collection_overlap[key] = lhl_data_collection_airgo[key][match_boolean]
    for stage_version in stage_versions_hrv:
        dt_stage_version = [pd.Timestamp(x) for x in lhl_data_collection_hrv[f'loc_{stage_version}']]
        keys_stage_version = [x for x in lhl_data_collection_hrv.keys() if stage_version in x]
        assert type(dt_stage_version[0]) == type(dt_stages_all[0]), 'Different DateTime Types. Might break np.isin().'
        match_boolean = np.isin(dt_stage_version, dt_stages_all)
        for key in keys_stage_version:
            lhl_data_collection_overlap[key] = lhl_data_collection_hrv[key][match_boolean]

    return lhl_data_collection_overlap


def save_stage_hlh_data(lhl_data_collection, study_id, output_h5_path):
    # stage_dt = list(stage_dt)
    stage_pred_versions = [x.split('stage_pred_')[-1] for x in lhl_data_collection.keys() if 'stage_pred' in x]

    for stage_pred_version in stage_pred_versions:

        keys_pred_version = [x for x in lhl_data_collection.keys() if stage_pred_version in x]
        if 'iloc_' + stage_pred_version in keys_pred_version: keys_pred_version.remove('iloc_' + stage_pred_version)

        for key in keys_pred_version:
            assert lhl_data_collection[key].shape[0] == lhl_data_collection['stage_pred_' + stage_pred_version].shape[0], \
                "Dimension mismatch in Last Hidden Layer Data"
        for key in keys_pred_version:
            if key == f'loc_{stage_pred_version}':
                stage_posix = np.array([pd.to_datetime(str(x)).value for x in lhl_data_collection[key]])
                write_to_hdf5_file_single_array(stage_posix, f'posix_{stage_pred_version}',
                                                output_h5_path, dtype='float64')
            else:
                write_to_hdf5_file_single_array(lhl_data_collection[key], key, output_h5_path, dtype='float32')

        study_id_array = np.array([int(study_id)] * lhl_data_collection['stage_pred_' + stage_pred_version].shape[0])
        write_to_hdf5_file_single_array(study_id_array, 'study_id_' + stage_pred_version, output_h5_path, dtype='int32')

def main():

    data_source = 'sleeplab'
    # data_source = 'icu_sleep'
    print(f'data source selected: {data_source}')
    time.sleep(5)


    if data_source == 'icu_sleep':
        dir_airgo = f'/scr/wolfgang/Sleep_And_Breathing/icu_files_step6' # was originally step_5_2
        dir_hrv = '/media/mad3/Projects/ICU_SLEEP_STUDY/Other_unsorted/data_analysis/BMR_resampled_ECG_and_rpeaks'
        savedir_10hz = f'/scr/wolfgang/Sleep_And_Breathing/icu_files_step7'
        output_dir_lhl = f'/scr/wolfgang/Sleep_And_Breathing/icu_files_sleep_staging_lhl'
        # TMP
        # savedir_10hz = f'/scr/wolfgang/Sleep_And_Breathing/TMP_icu_files'
        # output_dir_lhl = f'/scr/wolfgang/Sleep_And_Breathing/TMP_icu_files_sleep_staging_lhl'

        do_left_pad = True
        models_dir_airgo = './sleep_staging_models'
        models_dir_ecg = './sleep_staging_models'

    if data_source == 'sleeplab':
        dir_airgo = f'/scr/wolfgang/Sleep_And_Breathing/sleeplab_files_step6'
        dir_hrv = '/media/mad3/Projects/ICU_SLEEP_STUDY/Sleep_And_Breathing/ECG_and_rpeaks_sleeplab'
        savedir_10hz = None # no need to save those files, just hidden layer for sleeplab needed
        output_dir_lhl = f'/scr/wolfgang/Sleep_And_Breathing/sleeplab_files_sleep_staging_lhl'
        do_left_pad = False

        # TMP
        # savedir_10hz = f'/scr/wolfgang/Sleep_And_Breathing/TMP_icu_files'
        # output_dir_lhl = f'/scr/wolfgang/Sleep_And_Breathing/TMP_icu_files_sleep_staging_lhl'

        folds = pd.read_csv('airgo_ss_test_folds.csv')
        folds.fileID = [x.replace('Feature_Air', 'psg_airgo_10hz_').replace('.mat', '.h5') for x in folds.fileID]
        folds['study_id'] = [re.search('\d\d\d', x)[0] for x in folds.fileID]
        models_dir_ecg = './sleep_staging_models' # airgo per fold further down.

    overwrite = False
    n_gpu = 4

    for dir_tmp in [savedir_10hz, output_dir_lhl]:
        if dir_tmp is not None:
            if not os.path.exists(dir_tmp):
                os.makedirs(dir_tmp)

    files_airgo = os.listdir(dir_airgo)
    files_airgo.sort()

    files_hrv = os.listdir(dir_hrv)

    for file in files_airgo: # [: len(files_airgo) // 2]
        study_id = file[-6:-3]

        # ### TMP
        # if not study_id in ['126']: # 122
        #     continue
        # print(study_id)
        # ### END TMP

        if data_source == 'sleeplab':
            # have to select fold for sleeplab:
            fold_id = folds.loc[folds.study_id == study_id, 'fold_id'].values[0]
            models_dir_airgo = f'./sleep_staging_models/fold_{fold_id}'

        input_file_path_airgo = os.path.join(dir_airgo, file)
        input_file_path_hrv = os.path.join(dir_hrv, 'ECG_' + study_id + '.h5')
        output_file_path_full = os.path.join(output_dir_lhl, 'staging_lhl_full.h5')
        output_file_path_overlap = os.path.join(output_dir_lhl, 'staging_lhl_overlap.h5')

        print(file)

        # AIRGO BASED SLEEP STAGING:
        data_10hz, hdr_10hz, fs_10hz = read_in_routine(input_file_path_airgo, check_airgo_scaling=False)
        airgo_cols = ['acc_ai_10sec', 'movavg_0_5s']
        airgo_cols = [x for x in airgo_cols if x in data_10hz.columns]
        data_airgo = data_10hz[airgo_cols].copy()
        if data_source == 'sleeplab': # only use data from epoch 0 onwards.
            start_psg = data_10hz.loc[data_10hz.epoch == 0].index[0]
            data_airgo = data_airgo.loc[start_psg:]

        data_airgo, stage_iloc_airgo, lhl_data_collection_airgo = \
            apply_airgo_sleep_staging_models(data_airgo, fs=fs_10hz, n_gpu=n_gpu, output=-1, do_left_pad=do_left_pad,
                                             models_dir=models_dir_airgo)
        stage_dt_airgo = data_airgo.index[stage_iloc_airgo]


        # ECG BASED SLEEP STAGING:
        data_hrv, hdr_hrv, fs_hrv = read_in_routine(input_file_path_hrv)
        if data_source == 'sleeplab':
            data_hrv = data_hrv.loc[start_psg:]

        ecg_sleepstage_model_fs = 200
        if fs_hrv != ecg_sleepstage_model_fs:
            data_hrv = resample_ecg_data_for_sleep_staging(data_hrv, fs_hrv, ecg_sleepstage_model_fs=ecg_sleepstage_model_fs)
        data_hrv, stage_iloc_hrv, lhl_data_collection_hrv = \
                apply_ecg_sleep_staging_models(data_hrv, ecg_sleepstage_model_fs, n_gpu=n_gpu, output=-1, do_left_pad=do_left_pad,
                                                   models_dir=models_dir_ecg)
        if data_source == 'icu_sleep':
            data_hrv.stage_pred_ecg_nn.fillna(method='ffill', limit=ecg_sleepstage_model_fs*60*5, inplace=True) # pad for five minutes, bridge gaps for bad quality signal for max this time.

        stage_dt_hrv = data_hrv.index[stage_iloc_hrv]

        # join sleep staging results to 10 data, and save with updated sleep stage info.
        # remove cols
        ecg_stage_col = ['stage_pred_ecg_nn']
        data_airgo.drop(airgo_cols, axis=1, inplace=True)
        cols_to_drop = list(data_airgo.columns) + ecg_stage_col
        data_10hz.drop(cols_to_drop, axis=1, inplace=True)
        data_10hz = data_10hz.join(data_airgo, how='outer') # outer to get left-padding from sleep stage
        data_10hz = data_10hz.join(data_hrv[ecg_stage_col], how='left') # left to only use ecg data within what is covered by the data.

        if savedir_10hz is not None:
            write_to_hdf5_file(data_10hz, os.path.join(savedir_10hz, file), hdr_10hz)

        # save full info:
        save_stage_hlh_data(lhl_data_collection_airgo, study_id, output_file_path_full)
        save_stage_hlh_data(lhl_data_collection_hrv, study_id, output_file_path_full)

        # only select data where we have exact overlap for ecg and airgo based predictions.
        lhl_data_collection_overlap = select_overlapping_dt_stages_hlh(lhl_data_collection_airgo, lhl_data_collection_hrv)
        if not bool(lhl_data_collection_overlap):
            print(f'No Overlap for {study_id}. Continue')
            continue

        save_stage_hlh_data(lhl_data_collection_overlap, study_id, output_file_path_overlap)

        # blub = 1

        # nothing = 1



if __name__ == '__main__':
    main()