import pandas as pd
import numpy as np
import h5py
import os
import sys
sys.path.append('C:/Users/wg984/Wolfgang/repos/sleep_research_io')
sys.path.append('/home/wolfgang/repos/sleep_research_io')
from sleep_research_functions import index_to_datetime_sleepdata, load_sleep_data, write_to_hdf5_file, read_in_routine, load_bm_data_aligned, merge_bm_and_airgo, airgo_resample_preprocess, bm_resample_interpolate
sys.path.append('C:/Users/wg984/Wolfgang/repos/Bedmaster-ICU-tools/code')
sys.path.append('/home/wolfgang/repos/Bedmaster-ICU-tools/code')
from research_bm_tools import BMR_load, get_metadata
from resample_BMR import remove_non_monotonic_data
from edw_functions import get_vitals, save_edw_vitals_df_for_each_mrn, get_edw_oxygen, get_vitals_single_mrn, get_edw_oxygen_single_mrn
from datetime import datetime, timedelta

# ## input
# ### bedmaster:
# output from bedmaster_data_vitals_for_MRNs (maybe different in future), i.e. bedmaster .h5 file, default-name: MRN_{mrn}.h5
# ### airgo:
# either raw airgo file [.csv] or a file with additional columns/signals (features, model outputs) [.csv or .h5 sleep_research_format]

# ### in general:
# usually, patients are either identified via study_id or via mrn. read-in procedure shall be stable for these variants, i.e. what is needed is a dictionary that maps bedmaster file to airgo file / vice versa. this dictionary might need to be created in different ways for different projects, but from there onwards read in/processing should be standardized.


### covid-19 respiration data:

study_table = '/media/ssd2/Covid19_Respiration/Database Skeleton.xlsx'
study_table = pd.read_excel(study_table)
study_table.StudyID = study_table.StudyID.apply(lambda x: str(x).zfill(3))

mapping_df = pd.DataFrame()
mapping_df['study_id'] = study_table['StudyID']
mapping_df['mrn'] = study_table['MRN']
mapping_df['bm_file'] = mapping_df['mrn'].apply(lambda x: 'MRN_'+ str(x) + '.h5')
mapping_df['airgo_file'] = mapping_df['study_id'].apply(lambda x: 'airgo_'+ str(x) + '.csv')

bm_files_dir = '/media/mad3/Projects/covid_data/h5_files'
airgo_files_dir = '/media/ssd2/Covid19_Respiration/Data_Analysis/Airgo_Features'
output_dir = '/media/ssd2/Covid19_Respiration/Data_Analysis/Combined_Data'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    
mapping_df['bm_file_path'] = mapping_df['bm_file'].apply(lambda x: os.path.join(bm_files_dir, x))
mapping_df['airgo_file_path'] = mapping_df['airgo_file'].apply(lambda x: os.path.join(airgo_files_dir, x))

# EDW data: for EDW, we use the raw output from EDW queries, MRN selection happs within loading function.
data_dir = '/media/mad3/Projects/covid_data/EDW'
cohort_name = 'airgo_covid_2020_06_30'
vitals_file_path = os.path.join(data_dir, f'edw_{cohort_name}_vitals.csv')
oxygen_supplement_file_path = os.path.join(data_dir, f'edw_{cohort_name}_oxygen_supplement.csv')
mapping_df['edw_vitals_file_path'] = vitals_file_path
mapping_df['edw_oxygen_supplement_file_path'] = oxygen_supplement_file_path

mapping_df['output_file_path'] = mapping_df['study_id'].apply(lambda x: os.path.join(output_dir, f'cov_resp_{x}.h5'))


# PARAMS AND SETTINGS:
do_resample_and_interpolation = False # IF only airgo exists, does it need to be resampled to 'perfect 10Hz'?


for irow, row in mapping_df.iloc[11:].iterrows():
    
    try:
        
        airgo_path_tmp = row.airgo_file_path
        bm_path_tmp = row.bm_file_path
        output_path_tmp = row.output_file_path
        
        if os.path.exists(output_path_tmp):
            continue
            
        print(row.study_id)
        airgo_exists = os.path.exists(airgo_path_tmp)
        print(f'airgo_exists: {airgo_exists}')
        bm_exists = os.path.exists(bm_path_tmp)
        print(f'bm_exists: {bm_exists}')
        
        
        bm_exists = os.path.exists(bm_path_tmp)
        
        if airgo_exists:
            data_airgo, hdr_airgo, fs_airgo = read_in_routine(airgo_path_tmp)

        if bm_exists:
            # this load the bedmaster data that is saved in 'dataframe vitals' format, 
            # i.e. signals are already aligned and concatenated and posix is separate column. gets convertd to datetime
            data_bm = load_bm_data_aligned(bm_path_tmp)

        if airgo_exists & bm_exists:
            
#             print('tmp!!!!')
#             data_airgo = data_airgo.iloc[5000:5000+fs_airgo*60*120]
#             data_bm = data_bm.loc[data_airgo.index[0] : data_airgo.index[-1]]
            
            data_combined = merge_bm_and_airgo(data_bm, data_airgo)

        elif airgo_exists:
            if do_resample_and_interpolation:
                data_airgo = airgo_resample_preprocess(data_airgo)
            data_combined = data_airgo

        elif bm_exists:
            data_combined = bm_resample_interpolate(data_bm)

            
        ### ADD EDW:
        
        # vitals:
        edw_vitals = get_vitals_single_mrn(row.edw_vitals_file_path, row.mrn)
        edw_vitals.columns = ['edw_' + x for x in edw_vitals.columns]
        edw_vitals = edw_vitals.loc[data_combined.index[0] - timedelta(hours=1.5):data_combined.index[-1] + timedelta(hours=1.5)]
        edw_vitals = edw_vitals.asfreq('0.1S')
        data_combined = data_combined.join(edw_vitals, how='outer')
        
        # oxygen:
        edw_oxygen = get_edw_oxygen_single_mrn(row.edw_oxygen_supplement_file_path, row.mrn)
        edw_oxygen = edw_oxygen.loc[data_combined.index[0] - timedelta(hours=1.5):data_combined.index[-1] + timedelta(hours=1.5)]
        edw_oxygen = edw_oxygen.asfreq('0.1S')
        data_combined.join(edw_oxygen, how='outer')
        
        
        hdr = {}
        dt = data_combined.index[0]
        hdr['start_datetime'] = np.array([dt.year, dt.month, dt.day,
                 dt.hour, dt.minute,
                 dt.second, dt.microsecond])
        hdr['MRN'] = row.mrn
        hdr['study_id'] = int(row.study_id)
        hdr['fs'] = 10

        write_to_hdf5_file(data_combined, output_path_tmp, hdr=hdr)
        
    except Exception as e:
        print(f'Exception for {row.study_id}:')
        print(e)
        continue
    