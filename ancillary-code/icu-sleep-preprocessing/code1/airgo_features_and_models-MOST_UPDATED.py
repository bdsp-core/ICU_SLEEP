
import pandas as pd
import numpy as np
import os
import sys

sys.path.append('/home/wolfgang/repos/ICU-Sleep/code1')
from apnea_detection_functions import apply_apnea_prediction_models
from airgo_features import compute_airgo_features
from sleep_staging_functions import apply_airgo_sleep_staging_models

sys.path.append('/home/wolfgang/repos/sleep_research_io')
from sleep_research_functions import *
from sleep_analysis_functions import *
import matplotlib.pyplot as plt

# ### Compute all airgo features (RR, MV, instability, complexity, actigraphy), apply apnea detection and sleep staging model. <br>  If other signals are available, like SpO2 (bedmaster, PSG), then models that use these signals will also be utilized.
# Currently models:
# Apnea Detection: Respiration Only (needs features computed), Respiration+SpO2.  
# Sleep Staging: Based on Respiration Only, Actigraphy Only.

# ### input: 
# <b> list of paths to files. </b>  
# files: either original airgo files, or merged with bedmaster or PSG data.


data_dir = './Data_Analysis/Airgo'
output_dir = './Data_Analysis/Airgo_Features'

data_dir = '/media/ssd2/icu_final_files'
output_dir = '/media/ssd2/icu_sleepstaging_TMP2'

data_dir = '/media/ssd2/Covid19_Respiration/Data_Analysis/Combined_Data'
output_dir = '/media/ssd2/Combined_Data2'

data_dir = '/media/ssd2/Covid19_Respiration/Data_Analysis/Combined_Data_3'
output_dir = '/media/ssd2/Combined_Data2'

data_dir = '/media/ssd2/Combined_Data3'
output_dir = '/media/ssd2/Combined_Data4'
overwrite = False

filepaths_input, filepaths_output = filepaths_routine(data_dir, output_dir)

fs_manual = 10
do_resample_and_interpolation = False       # recommended for raw airgo, resampling to 'perfect 10Hz'
do_compute_airgo_features = False           # all features. by default, complexity features are computed in this code which are the slowest but needed for apnea prediction.
do_apply_sleep_staging_models = False        # respiration-only, actigraphy-only.
do_apply_apnea_prediction_models = True    # respiration-only and respiration+spo2 models. if sleep_stage_available, sleep-only apnea versions get computed too.
do_compute_self_similarity = False          # depends on airgo available
do_compute_hypoxia_burden = True           # depends on apnea predictions and sleep stages (for hours of sleep)


### compute_hypoxia_burden params ###
apnea_name = 'apnea_pred_va_a3'                      # name of Apnea info column
hours_sleep = 'stage_pred_amendsumeffort'  # name of sleep stage column, or int/float for manual setting.

# start = int(sys.argv[1])
# end = int(sys.argv[2])

# filepath_input = filepaths_input[0]
# filepath_output = filepaths_output[0]


for filepath_input, filepath_output in list(zip(filepaths_input, filepaths_output)): # [start:end]:

    try:
    # if 1:
        
        if (os.path.exists(filepath_output)) & (not overwrite):
            print(f'{filepath_output} already exists. Continue.')
            continue

        print(filepath_input)

        data, hdr, fs = read_in_routine(filepath_input, fs_manual=fs_manual)


#         print('TMP!!!!')
#         index_airgo_start = data.band.dropna().index[0]
#         index_airgo_later = data.band.dropna().index[fs*3600]
#         data = data.loc[index_airgo_start : index_airgo_later]
        
        # skip missing airgo:
        if not 'band' in data.columns:
            print('No AirGo data at all.')
            continue
            
        # skip missing airgo:
        if not 'band' in data.columns:
            print('No AirGo data at all.')
            continue        
        
#         if data.acc_ai_10sec.dropna().mean() > 1:
#             print(file_tmp)
#             print('data.acc_ai_10sec.dropna().mean() > 1 --> V4.')
#             continue
            
#         if any(data.band_unscaled.dropna()>5000):
#             print(file_tmp)
#             print('unscaled airgo amplitude>5000 --> V4.')
#             continue
                        
        
        if do_resample_and_interpolation:
            data = airgo_resample_preprocess(data)

        if do_compute_airgo_features:
            data = compute_airgo_features(data, fs=fs, complexity_features=1)

        if do_apply_sleep_staging_models:
            
#             data.drop(['stage_pred_amendsumeffort'], axis=1, inplace=True)
#             data.drop(['stage_pred_activity1sec'], axis=1, inplace=True)
#             data.drop(['stage_pred_vcomb1'], axis=1, inplace=True)
            
            data = apply_airgo_sleep_staging_models(data, fs=fs)
        
        if do_apply_apnea_prediction_models:
            data = apply_apnea_prediction_models(data, fs=fs)
            
        # to be tested:
        if do_compute_self_similarity:
            data = self_similarity_airgo(data)
            
        if do_compute_hypoxia_burden:

            ### compute_hypoxia_burden params ###

            apnea_name = 'apnea_pred_ro_a3'  # name of Apnea info column
            hours_sleep = 'stage_pred_amendsumeffort'  # name of sleep stage column, or int/float for manual setting.
            hypoxia_name = 'hypoxic_area' + apnea_name.replace('apnea_pred', '')

            data, hypoxia_burden = compute_hypoxia_burden(data, fs, apnea_name = apnea_name, 
                hypoxia_name=hypoxia_name, hours_sleep = hours_sleep)

            apnea_name = 'apnea_pred_rsr_a3'  # name of Apnea info column
            hours_sleep = 'stage_pred_amendsumeffort'  # name of sleep stage column, or int/float for manual setting.
            hypoxia_name = 'hypoxic_area' + apnea_name.replace('apnea_pred', '')

            data, hypoxia_burden = compute_hypoxia_burden(data, fs, apnea_name = apnea_name, 
                hypoxia_name=hypoxia_name, hours_sleep = hours_sleep)

            apnea_name = 'apnea_pred_va_a3'  # name of Apnea info column
            hours_sleep = 'stage_pred_amendsumeffort'  # name of sleep stage column, or int/float for manual setting.
            hypoxia_name = 'hypoxic_area' + apnea_name.replace('apnea_pred', '')

            data, hypoxia_burden = compute_hypoxia_burden(data, fs, apnea_name = apnea_name, 
                hypoxia_name=hypoxia_name, hours_sleep = hours_sleep)


        save_data_routine(data, filepath_output, hdr=hdr, overwrite=overwrite)
        
    except Exception as e:
        print('Exception for ' + filepath_input)
        print(e)
        continue

