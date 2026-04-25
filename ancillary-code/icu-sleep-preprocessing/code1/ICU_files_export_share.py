import pandas as pd
import numpy as np
import os
import sys

# sys.path.append('/home/wolfgang/repos/AirGo_Apnea_Detection')

sys.path.append('/home/wolfgang/repos/ICU-Sleep/code1')
from apnea_detection_functions import apply_apnea_prediction_models
from airgo_features import compute_airgo_features
from sleep_staging_functions import apply_airgo_sleep_staging_models

sys.path.append('/home/wolfgang/repos/sleep_research_io')
from sleep_research_functions import *
from sleep_analysis_functions import *
from edw_functions import *

import matplotlib.pyplot as plt


def main():

    data_dir = '/media/mad3/Projects/ICU_SLEEP_STUDY/Sleep_And_Breathing/icu_files_v2'
    output_dir = '/media/mad3/Projects/ICU_SLEEP_STUDY/Sleep_And_Breathing/icu_files_share'
    overwrite = False

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    files = os.listdir(data_dir)
    files.sort()

    for file in files:

        try:

            study_id = file[-6:-3]
            input_file_path = os.path.join(data_dir, file)
            output_file_path = os.path.join(output_dir, file)

            if (os.path.exists(output_file_path)) & (not overwrite):
                continue

            print(file)


            data, hdr  = load_sleep_data(input_file_path, idx_to_datetime=True)


            signals_to_keep = ['IBI', 'acc_ai_10sec', 'accx', 'accy' 'accz', 'apnea_pred_ro_a3', 'apnea_prob_ro_a3',
                               'apnea_pred_rsr_a3', 'apnea_prob_rsr_a3', 'art1d', 'art1s', 'nbps', 'nbpd', 'band_unscaled', 'edw_bp_diastolic', 'edw_bp_systolic',
                               'edw_pulse', 'edw_pulse_oximetry', 'edw_respirations', 'edw_temperature', 'edw_urine_output', 'hr', 'spo2',
                               'instability_index_2min', 'instability_index_30sec', 'oxygen_device', 'oxygen_flow_rate',
                               'position_cluster', 'positioning_frequency', 'repositioned',
                               'rr_10s', 'rr_10s_smooth', 'self_similarity', 'stage_pred_activity10sec',
                               'stage_pred_amendsumeffort', 'stage_pred_comb_breath_activity_1',
                               'ventilation_10s', 'ventilation_10s_smooth']

            signals_to_keep = [x for x in signals_to_keep if x in data.columns]
            data = data[signals_to_keep]

            fs = hdr['fs']
            hdr['study_id'] = np.int32(hdr['study_id'])
            hdr['MRN'] = np.int32(0)
            hdr['fs'] = np.int32(hdr['fs'])
            hdr['start_datetime'] = np.array(
                [hdr['start_datetime'].year, hdr['start_datetime'].month, hdr['start_datetime'].day,
                 hdr['start_datetime'].hour, hdr['start_datetime'].minute, hdr['start_datetime'].second,
                 hdr['start_datetime'].microsecond])

            save_data_routine(data, output_file_path, hdr=hdr, overwrite=overwrite)

        except Exception as e:
            print(e)
            continue


if __name__ == '__main__':
    main()