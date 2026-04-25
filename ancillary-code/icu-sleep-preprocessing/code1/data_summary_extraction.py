import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
from edw_functions import *
sys.path.append('/home/wolfgang/repos/sleep_research_io/')
from sleep_research_functions import *
import re
from datetime import datetime, timedelta
from apnea_detection_functions import self_similarity_indices
import pdb
from sleep_analysis_functions import *
from airgo_features import compute_airgo_features
import traceback
import multiprocessing
from multiprocessing import Pool

def init_statistics_to_extract_default():
    # dictionary for statistics to extract. format: key: name of biosignal/column, values: statistics
    # naming in summary spreadsheet is set up for naming key+value, except 'Index' is ignored, only key is used for those.
    statistics_to_extract = {
        'hr': ['mean', 'std', 'median', 'q25', 'q75', 'sda', 'asd'],
        'spo2': ['mean', 'std', 'median', 'q25', 'q75', 'sda', 'asd'],
        'spo2_airgo': ['mean', 'std', 'median', 'q25', 'q75', 'sda', 'asd'],
        'spo2_clean': ['mean', 'std', 'median', 'q25', 'q75', 'sda', 'asd'],
        'spo2_airgo_clean': ['mean', 'std', 'median', 'q25', 'q75', 'sda', 'asd'],
        'edw_bp_systolic': ['mean', 'std', 'median', 'q25', 'q75'],
        'edw_bp_diastolic': ['mean', 'std', 'median', 'q25', 'q75'],
        'edw_bp_map': ['mean', 'std', 'median', 'q25', 'q75'],
        'cpc_hfc_lfc_ratio': ['mean', 'std', 'median', 'q25', 'q75'],
        'cpc_hfc': ['mean', 'std', 'median', 'q25', 'q75', 'sum'],
        'cpc_lfc': ['mean', 'std', 'median', 'q25', 'q75', 'sum'],
        'hrv_nn': ['mean', 'std', 'median', 'q25', 'q75', 'sda', 'asd'],
        'hco3_arterial': ['mean', 'min', 'max'],
        'pco2_arterial': ['mean', 'min', 'max'],
        'po2_arterial': ['mean', 'min', 'max'],
        'ph_arterial': ['mean', 'min', 'max'],
        'oxygen_flow_rate': ['max'],
        'sofa_score': ['mean', 'min', 'max'],
        'cam_s': ['morning', 'evening'],
        # currently, we extract the data in a max 24 hour fashion, if at some point more than 24 hours need to e summaried, use min/max etc.
        'ahi_va_a3': ['index'],
        'ahi_va_a3_ss': ['index'],
        'ahi_vb_a3': ['index'],
        'ahi_vb_a3_ss': ['index'],
        'ahi_ro_a3': ['index'],
        'ahi_ro_a3_ss': ['index'],
        'ahi_rsr_a3': ['index'],
        'ahi_rsr_a3_ss': ['index'],
        'ahi_expert': ['index'],
        'ahi_va_a3_ss_aswti': ['index'],
        'ahi_vb_a3_ss_aswti': ['index'],
        'ahi_ro_a3_ss_aswti': ['index'],
        'ahi_rsr_a3_ss_aswti': ['index'],
        'hypoxic_burden_va_a3': ['index'],
        'hypoxic_burden_va_a3_ss': ['index'],
        'hypoxic_burden_vb_a3': ['index'],
        'hypoxic_burden_vb_a3_ss': ['index'],
        'hypoxic_burden_ro_a3': ['index'],
        'hypoxic_burden_ro_a3_ss': ['index'],
        'hypoxic_burden_rsr_a3': ['index'],
        'hypoxic_burden_rsr_a3_ss': ['index'],
        'hypoxic_burden_expert': ['index'],
        'hypoxic_burden_va_a3_ss_aswti': ['index'],
        'hypoxic_burden_vb_a3_ss_aswti': ['index'],
        'hypoxic_burden_ro_a3_ss_aswti': ['index'],
        'hypoxic_burden_rsr_a3_ss_aswti': ['index'],
        'hypoxia_index': ['LDI', 'SDI', 'TDI', 'pu90'],
        'hypoxia_index_ss': ['LDI', 'SDI', 'TDI', 'pu90'],
        'hypoxia_index_ss_aswti': ['LDI', 'SDI', 'TDI', 'pu90'],
        'self_similarity': ['sleep_index', 'sleep_q50', 'sleep_q75', 'apnea_index', 'apnea_q50', 'apnea_q75'],
        'opioids_sum': ['sum'],
        'benzos_sum': ['sum'],
        'antipsychotics_sum': ['sum'],
        'dex_studydrug': ['sum'],
        'airgo_available_h': ['index'],
        'ecg_available': ['index'],
        'airgo_ecg_available': ['index'],
        'spo2_available': ['index'],
        'spo2_airgo_available': ['index'],
        'sleep_hours_breathing': ['index'],
        'sleep_hours_breathing_aswti': ['index'],
        'sleep_hours_breathcomb1': ['index'],
        'sleep_hours_breathcomb1_aswti': ['index'],
        'stages_distribution_breathing': ['W', 'S', 'R', 'N1', 'N2', 'N3'],
        'sleep_index_breathing': ['sfi', 'sfi_w', 'arousali'],
        'sleep_hours_breathing_agrelaxed': ['index'],
        'stages_distribution_breathing_agrelaxed': ['W', 'S', 'R', 'N1', 'N2', 'N3'],
        'sleep_index_breathing_agrelaxed': ['sfi', 'sfi_w', 'arousali'],
        'sleep_hours_breathing_disrelaxed': ['index'],
        'stages_distribution_breathing_disrelaxed': ['W', 'S', 'R', 'N1', 'N2', 'N3'],
        'sleep_index_breathing_disrelaxed': ['sfi', 'sfi_w', 'arousali'],
        'sleep_hours_ecg_nn': ['index'],
        'sleep_hours_ecg_nn_aswti': ['index'],
        'stages_distribution_ecg_nn': ['W', 'S', 'R', 'N1', 'N2', 'N3'],
        'sleep_index_ecg_nn': ['sfi', 'sfi_w', 'arousali'],
        'sleep_hours_ecg_nn_agrelaxed': ['index'],
        'stages_distribution_ecg_nn_agrelaxed': ['W', 'S', 'R', 'N1', 'N2', 'N3'],
        'sleep_index_ecg_nn_agrelaxed': ['sfi', 'sfi_w', 'arousali'],
        'sleep_hours_ecg_nn_disrelaxed': ['index'],
        'stages_distribution_ecg_nn_disrelaxed': ['W', 'S', 'R', 'N1', 'N2', 'N3'],
        'sleep_index_ecg_nn_disrelaxed': ['sfi', 'sfi_w', 'arousali'],
        'sleep_hours_expert': ['index'],
        'stages_distribution_expert': ['W', 'S', 'R', 'N1', 'N2', 'N3'],
        'sleep_index_expert': ['sfi', 'sfi_w', 'arousali'],
        'ibi': ['mean', 'std', 'median', 'q25', 'q75', 'sda', 'asd'],
        'rr_10s_smooth': ['mean', 'std', 'median', 'q25', 'q75', 'sda', 'asd'],
        'instability_index_1min': ['mean', 'std', 'median', 'q25', 'q75', 'sda', 'asd'],
        'instability_index_30sec': ['mean', 'std', 'median', 'q25', 'q75', 'sda', 'asd'],
        'ventilation_10s_smooth': ['mean', 'std', 'median', 'q25', 'q75', 'sda', 'asd'],
        'ventilation_cvar_30sec': ['mean', 'std', 'median', 'q25', 'q75', 'sda', 'asd'],
        'inht_cycle_ratio_10sec': ['mean', 'std', 'median', 'q25', 'q75', 'sda', 'asd'],
        'hrv_ulf': ['mean', 'std', 'median', 'q25', 'q75', 'sda', 'asd'],
        'hrv_vlf': ['mean', 'std', 'median', 'q25', 'q75', 'sda', 'asd'],
        'hrv_lf': ['mean', 'std', 'median', 'q25', 'q75', 'sda', 'asd'],
        'hrv_hf': ['mean', 'std', 'median', 'q25', 'q75', 'sda', 'asd'],
        'hrv_lfhf': ['mean', 'std', 'median', 'q25', 'q75', 'sda', 'asd'],
        'hrv_nnmean': ['mean', 'std', 'median', 'q25', 'q75', 'sda', 'asd'],
        'hrv_nnmedian': ['mean', 'std', 'median', 'q25', 'q75', 'sda', 'asd'],
        'hrv_rmssd': ['mean', 'std', 'median', 'q25', 'q75', 'sda', 'asd'],
        'hrv_sd1': ['mean', 'std', 'median', 'q25', 'q75', 'sda', 'asd'],
        'hrv_sd2': ['mean', 'std', 'median', 'q25', 'q75', 'sda', 'asd'],
        'hrv_sd1sd2': ['mean', 'std', 'median', 'q25', 'q75', 'sda', 'asd'],
    }

    # add 'stagewise' for all variables as well:
    variables_stagewise = list(statistics_to_extract.keys())
    for key in variables_stagewise:
        if not np.any([x in key for x in ['hr', 'spo2', 'spo2_airgo', 'spo2_clean', 'spo2_airgo_clean',
                'hypoxia_index', 'edw_bp_systolic',
                'edw_bp_diastolic', 'edw_bp_map', 'cpc_hfc_lfc_ratio', 'cpc_hfc',
                'cpc_lfc', 'hrv_nn', 'oxygen_flow_rate',
                'ibi', 'rr_10s_smooth', 'instability_index_1min', 'instability_index_30sec',
                'ventilation_10s_smooth', 'ventilation_cvar_30sec', 'inht_cycle_ratio_10sec',
                'hrv_ulf', 'hrv_vlf', 'hrv_lf', 'hrv_hf', 'hrv_lfhf', 'hrv_nnmean', 'hrv_nnmedian',
                'hrv_rmssd', 'hrv_sd1', 'hrv_sd2', 'hrv_sd1sd2']]):
            continue

        statistics_to_extract[key + '_stagewise_agrelaxed'] = statistics_to_extract[key]
        statistics_to_extract[key + '_stagewise_disrelaxed'] = statistics_to_extract[key]

    return statistics_to_extract


def signal_availability_check(data, statistic_name):

    signal_needed = {
        'hr': ['hr'],
        'spo2': ['spo2'],
        'spo2_airgo': ['spo2', 'band'],
        'spo2_clean': ['spo2_clean'],
        'spo2_airgo_clean': ['spo2_clean', 'band'],
        'edw_bp_systolic': ['edw_bp_systolic'],
        'edw_bp_diastolic': ['edw_bp_diastolic'],
        'edw_bp_map': ['edw_bp_map'],
        'cpc_hfc_lfc_ratio': ['cpc_hfc_lfc_ratio'],
        'cpc_hfc': ['cpc_hfc'],
        'cpc_lfc': ['cpc_lfc'],
        'hrv_nn': ['hrv_nn'],
        'hco3_arterial': ['hco3_arterial'],
        'pco2_arterial': ['pco2_arterial'],
        'po2_arterial': ['po2_arterial'],
        'ph_arterial': ['ph_arterial'],
        'oxygen_flow_rate': ['oxygen_flow_rate'],
        'sofa_score': ['sofa_score'],
        'cam_s': ['cam_s'],
        'ahi_va_a3': ['apnea_pred_va_a3'],
        'ahi_va_a3_ss': ['apnea_pred_va_a3_ss'],
        'ahi_vb_a3': ['apnea_pred_vb_a3'],
        'ahi_vb_a3_ss': ['apnea_pred_vb_a3_ss'],
        'ahi_ro_a3': ['apnea_pred_ro_a3'],
        'ahi_ro_a3_ss': ['apnea_pred_ro_a3_ss'],
        'ahi_rsr_a3': ['apnea_pred_rsr_a3'],
        'ahi_rsr_a3_ss': ['apnea_pred_rsr_a3_ss'],
        'ahi_expert': ['apnea_pred_expert'],
        'ahi_va_a3_ss_aswti': ['apnea_pred_va_a3_ss_aswti'],
        'ahi_vb_a3_ss_aswti': ['apnea_pred_vb_a3_ss_aswti'],
        'ahi_ro_a3_ss_aswti': ['apnea_pred_ro_a3_ss_aswti'],
        'ahi_rsr_a3_ss_aswti': ['apnea_pred_rsr_a3_ss_aswti'],
        'hypoxic_burden_va_a3': ['stage_pred_comb_breath_activity_1', 'hypoxic_area_va_a3'],
        'hypoxic_burden_va_a3_ss': ['stage_pred_comb_breath_activity_1', 'hypoxic_area_va_a3_ss'],
        'hypoxic_burden_vb_a3': ['stage_pred_comb_breath_activity_1', 'hypoxic_area_vb_a3'],
        'hypoxic_burden_vb_a3_ss': ['stage_pred_comb_breath_activity_1', 'hypoxic_area_vb_a3_ss'],
        'hypoxic_burden_ro_a3': ['stage_pred_comb_breath_activity_1', 'hypoxic_area_ro_a3'],
        'hypoxic_burden_ro_a3_ss': ['stage_pred_comb_breath_activity_1', 'hypoxic_area_ro_a3_ss'],
        'hypoxic_burden_rsr_a3': ['stage_pred_comb_breath_activity_1', 'hypoxic_area_rsr_a3'],
        'hypoxic_burden_rsr_a3_ss': ['stage_pred_comb_breath_activity_1', 'hypoxic_area_rsr_a3_ss'],
        'hypoxic_burden_expert': ['stage_pred_comb_breath_activity_1', 'hypoxic_area_expert'],
        'hypoxic_burden_va_a3_ss_aswti': ['stage_pred_comb_breath_activity_1_aswti', 'hypoxic_area_va_a3_ss_aswti'],
        'hypoxic_burden_vb_a3_ss_aswti': ['stage_pred_comb_breath_activity_1_aswti', 'hypoxic_area_vb_a3_ss_aswti'],
        'hypoxic_burden_ro_a3_ss_aswti': ['stage_pred_comb_breath_activity_1_aswti', 'hypoxic_area_ro_a3_ss_aswti'],
        'hypoxic_burden_rsr_a3_ss_aswti': ['stage_pred_comb_breath_activity_1_aswti', 'hypoxic_area_rsr_a3_ss_aswti'],
        'hypoxia_index': ['spo2_clean', 'stage_pred_comb_breath_activity_1'],
        'hypoxia_index_ss': ['spo2_clean', 'stage_pred_comb_breath_activity_1'],
        'hypoxia_index_ss_aswti': ['spo2_clean', 'stage_pred_comb_breath_activity_1_aswti'],
        'self_similarity': ['self_similarity'],
        'opioids_sum': ['opioids_sum'],
        'benzos_sum': ['benzos_sum'],
        'antipsychotics_sum': ['antipsychotics_sum'],
        'dex_studydrug': ['dex_studydrug'],
        'airgo_available_h': ['band'],
        'ecg_available': ['stage_pred_ecg_nn'],
        'airgo_ecg_available': ['band', 'stage_pred_ecg_nn'],
        'spo2_available': ['spo2'],
        'spo2_airgo_available': ['spo2', 'band'],
        'sleep_hours_breathing': ['stage_pred_amendsumeffort'],
        'sleep_hours_breathing_aswti': ['stage_pred_amendsumeffort'],
        'sleep_hours_breathcomb1': ['stage_pred_comb_breath_activity_1'],
        'sleep_hours_breathcomb1_aswti': ['stage_pred_comb_breath_activity_1'],
        'stages_distribution_breathing': ['stage_pred_amendsumeffort'],
        'sleep_index_breathing': ['stage_pred_amendsumeffort'],
        'sleep_hours_breathing_agrelaxed': ['ecg_nn_amendsumeffort_agreement_relaxed'],
        'stages_distribution_breathing_agrelaxed': ['ecg_nn_amendsumeffort_agreement_relaxed'],
        'sleep_index_breathing_agrelaxed': ['ecg_nn_amendsumeffort_agreement_relaxed'],
        'sleep_hours_breathing_disrelaxed': ['ecg_nn_amendsumeffort_agreement_relaxed'],
        'stages_distribution_breathing_disrelaxed': ['ecg_nn_amendsumeffort_agreement_relaxed'],
        'sleep_index_breathing_disrelaxed': ['ecg_nn_amendsumeffort_agreement_relaxed'],
        'sleep_hours_ecg_nn': ['stage_pred_ecg_nn'],
        'sleep_hours_ecg_nn_aswti': ['stage_pred_ecg_nn_aswti'],
        'stages_distribution_ecg_nn': ['stage_pred_ecg_nn'],
        'sleep_index_ecg_nn': ['stage_pred_ecg_nn'],
        'sleep_hours_expert': ['stage_pred_expert'],
        'stages_distribution_expert': ['stage_pred_expert'],
        'sleep_index_expert': ['stage_pred_expert'],
        'ibi': ['ibi'],
        'rr_10s_smooth': ['rr_10s_smooth'],
        'instability_index_1min': ['instability_index_1min'],
        'instability_index_30sec': ['instability_index_30sec'],
        'ventilation_10s_smooth': ['ventilation_10s_smooth'],
        'ventilation_cvar_30sec': ['ventilation_cvar_30sec'],
        'inht_cycle_ratio_10sec': ['inht_cycle_ratio_10sec'],
        'hrv_ulf': ['hrv_ulf'],
        'hrv_vlf': ['hrv_vlf'],
        'hrv_lf': ['hrv_lf'],
        'hrv_hf': ['hrv_hf'],
        'hrv_lfhf': ['hrv_lfhf'],
        'hrv_nnmean': ['hrv_nnmean'],
        'hrv_nnmedian': ['hrv_nnmedian'],
        'hrv_rmssd': ['hrv_rmssd'],
        'hrv_sd1': ['hrv_sd1'],
        'hrv_sd2': ['hrv_sd2'],
        'hrv_sd1sd2': ['hrv_sd1sd2'],
    }

    signal2_is_available = True
    # currently, do not check if stage is available here, as there are potentially many different stage versions
    # e.g. different staging models. this check is done where the stage_version is available
    if '_stagewise' in statistic_name:
        statistic_name = statistic_name.replace('_stagewise', '')
    if '_agrelaxed' in statistic_name:
        statistic_name = statistic_name.replace('_agrelaxed', '')
        signal2_is_available = 'ecg_nn_amendsumeffort_agreement_relaxed' in data.columns
    if '_disrelaxed' in statistic_name:
        statistic_name = statistic_name.replace('_disrelaxed', '')
        signal2_is_available = 'ecg_nn_amendsumeffort_agreement_relaxed' in data.columns

    signal_needed_for_statistic = signal_needed[statistic_name]
    signal_is_available = np.all(np.isin(signal_needed_for_statistic, data.columns))
    if not signal2_is_available:
        signal_is_available = False

    return signal_is_available


def get_date_start_end_from_range(dt_full_range):
    # get dt_d1 = DAY 1 (i.e. day with 8am start) and dt_end = end of full last day (i.e. day with 8am end)

    dt_d1 = dt_full_range[0]
    dt_end = dt_full_range[-1]

    if 8 < dt_d1.hour:
        dt_d1 = dt_d1.date()
    else:
        dt_d1 = dt_d1.date() - timedelta(days=1)

    if 8 <= dt_end.hour:
        dt_end = dt_end.date() + timedelta(days=1)
    else:
        dt_end = dt_end.date()

    num_days = (dt_end - dt_d1).days
    assert num_days <= 9  # based on ICU study protocol

    return dt_d1, dt_end


def get_timerange_dict_airgo_available(data, study_id=None):

    if int(study_id) == 126:
        airgo_signal_quality_smooth = data['airgo_signal_quality'].rolling('10min').median()
        dt_full_range = data.loc[airgo_signal_quality_smooth > 0].index

    # sensitive version, this seems to be fine for all subjects except 126 that has a small part good quality, then days nothing.
    else:
        dt_full_range = data.loc[data['airgo_signal_quality'] > 0].index
        # dt_full_range = data.loc[
        # 	(~pd.isna(data.band_unscaled)) & (data.band_unscaled < amplitude_thresh), 'band_unscaled'].index

    # get dt_d1 = DAY 1 (i.e. day with 8am start) and dt_end = end of full last day (i.e. day with 8am end)
    dt_d1, dt_end = get_date_start_end_from_range(dt_full_range)

    start_one_day_prior_to_airgo_available = True
    if start_one_day_prior_to_airgo_available:
        dt_d1 = dt_d1 - timedelta(days=1)

    timerange_dict = {}
    num_days = (dt_end - dt_d1).days

    for i_day in range(num_days):
        dt_i = dt_d1 + timedelta(days=i_day)
        timerange_dict['d' + str(i_day + 1)] = str(dt_i) + ' 08:00:00 - ' + str(dt_i) + ' 20:00:00'
        timerange_dict['n' + str(i_day + 1)] = str(dt_i) + ' 20:00:00 - ' + str(dt_i + timedelta(days=1)) + ' 08:00:00'
        timerange_dict['f' + str(i_day + 1)] = str(dt_i) + ' 08:00:00 - ' + str(dt_i + timedelta(days=1)) + ' 08:00:00'

    return timerange_dict


def extract_cams(data_tmp):
    data_tmp = data_tmp.dropna()
    data_tmp = data_tmp[data_tmp != -1]
    num_cams = data_tmp.shape[0]

    assert num_cams <= 2, 'More than 2 CAM scores for a day?'
    if num_cams == 0:
        cam_morning = np.nan
        cam_evening = np.nan
    elif num_cams == 1:
        if data_tmp.index[0].hour < 14:
            cam_morning = data_tmp.iloc[0]
            cam_evening = np.nan
        else:
            cam_morning = np.nan
            cam_evening = data_tmp.iloc[0]
    else:
        cam_morning = data_tmp.iloc[0]
        cam_evening = data_tmp.iloc[1]

    return cam_morning, cam_evening


def compute_statistics(data, statistics, fs=10):
    '''
    this function computes summary statistics based on a univariate timeseries (no info from other columns is needed), therefore input here is a Pandas Series.
    Applies either default-type of statistics (such as mean, std., etc.)).
    '''

    statistics_result = []
    for i_statistic in statistics:

        if i_statistic in ['mean', 'std', 'median', 'min', 'max', 'sum']:
            i_result = data.apply(i_statistic)

        elif re.match('q\d\d', i_statistic) is not None:
            quantile = re.match('q\d\d', i_statistic)[0]
            quantile = np.float(quantile[1:])
            i_result = data.quantile(quantile / 100)

        elif i_statistic == 'asd':  # average of rolling standard deviation.
            i_result = data.rolling('5min', min_periods=1).std().mean()

        elif i_statistic == 'sda':  # standard deviation of rolling average
            i_result = data.rolling('5min', min_periods=1).mean().std()

        else:
            print(f'Unknown statistic: {i_statistic}. No computation done.')
            continue

        statistics_result.append(i_result)

    return statistics_result


def extract_statistics_for_timerange(data_timerange, signal_name, statistics_dict, fs=10):
    """
    input
    data_timerange: data already filtered for wanted timerange.
    signal_name: indicator for which signal the statistics, as defined in statistics function, shall be extracted.
    output: statistics names and statistic values, as defined in statistics function for signal_name.
    """

    i_statistics = statistics_dict[signal_name]

    if signal_name == 'self_similarity':
        [sesi_sleep_index, sesi_sleep_q50, sesi_sleep_q75,
         sesi_apnea_index, sesi_apnea_q50, sesi_apnea_q75] = self_similarity_indices(data_timerange,
                                                           stage_variable='stage_pred_amendsumeffort',
                                                           apnea_variable='apnea_pred_vb_a3_ss')

        statistics_result = [sesi_sleep_index, sesi_sleep_q50, sesi_sleep_q75,
                             sesi_apnea_index, sesi_apnea_q50, sesi_apnea_q75]

    elif 'stages_distribution' in signal_name:

        assert statistics_dict[signal_name] == ['W', 'S', 'R', 'N1', 'N2',
                                                'N3'], 'Code currently requires this format/name'

        if signal_name in ['stages_distribution_breathing', 'stages_distribution_breathing_agrelaxed',
                           'stages_distribution_breathing_disrelaxed']:
            column_stage = 'stage_pred_amendsumeffort'
        elif signal_name in ['stages_distribution_ecg_nn', 'stages_distribution_ecg_nn_agrelaxed',
                             'stages_distribution_ecg_nn_disrelaxed']:
            column_stage = 'stage_pred_ecg_nn'
        elif signal_name == 'stages_distribution_expert':
            column_stage = 'stage_pred_expert'
        else:
            raise ValueError(f'Wrong signal_name: {signal_name}')

        if 'agrelaxed' in signal_name:
            data_timerange = data_timerange[data_timerange['ecg_nn_amendsumeffort_agreement_relaxed'] == 1]
        if 'disrelaxed' in signal_name:
            data_timerange = data_timerange[data_timerange['ecg_nn_amendsumeffort_agreement_relaxed'] == 0]

        signal_available_h = len(data_timerange[column_stage].dropna()) / fs / 3600 + 0.000001

        hours_sleep = sum(data_timerange[column_stage].dropna() < 5) / fs / 3600 + 0.000001  # (just add for numerical stability)
        perc_W = sum(data_timerange[column_stage].dropna() == 5) / fs / 3600 / signal_available_h
        perc_S = sum(data_timerange[column_stage].dropna() < 5) / fs / 3600 / signal_available_h
        perc_R = sum(data_timerange[column_stage].dropna() == 4) / fs / 3600 / hours_sleep
        perc_N1 = sum(data_timerange[column_stage].dropna() == 3) / fs / 3600 / hours_sleep
        perc_N2 = sum(data_timerange[column_stage].dropna() == 2) / fs / 3600 / hours_sleep
        perc_N3 = sum(data_timerange[column_stage].dropna() == 1) / fs / 3600 / hours_sleep

        statistics_result = [perc_W, perc_S, perc_R, perc_N1, perc_N2, perc_N3]

    elif 'sleep_index' in signal_name:
        assert statistics_dict[signal_name] == ['sfi', 'sfi_w',
                                                'arousali'], 'Code currently requires this format/name'

        if signal_name in ['sleep_index_breathing', 'sleep_index_breathing_agrelaxed',
                           'sleep_index_breathing_disrelaxed']:
            column_stage = 'stage_pred_amendsumeffort'
        elif signal_name in ['sleep_index_ecg_nn', 'sleep_index_ecg_nn_agrelaxed',
                             'sleep_index_ecg_nn_disrelaxed']:
            column_stage = 'stage_pred_ecg_nn'
        elif signal_name == 'sleep_index_expert':
            column_stage = 'stage_pred_expert'
        else:
            raise ValueError(f'Wrong signal_name: {signal_name}')

        if 'agrelaxed' in signal_name:
            stages = data_timerange[data_timerange['ecg_nn_amendsumeffort_agreement_relaxed'] == 1][column_stage].values
        elif 'disrelaxed' in signal_name:
            stages = data_timerange[data_timerange['ecg_nn_amendsumeffort_agreement_relaxed'] == 0][column_stage].values
        else:
            stages = data_timerange[column_stage].values
        hours_sleep = sum(
            data_timerange[column_stage].dropna() < 5) / fs / 3600 + 0.000001
        # sleep fragmentation index:
        w_or_n1 = np.isin(stages, [5, 3])
        deep_sleep = np.isin(stages, [1, 2, 4])
        fragmentation_shift = np.logical_and(w_or_n1[1:], deep_sleep[:-1])
        fragmentation_pos = np.where(fragmentation_shift)[0]
        sfi = np.round(len(fragmentation_pos) / hours_sleep, 1)

        # SFI_W, based only on transitions to W from N2, N3 or R
        stages_without_n1 = stages[np.isin(stages, [1, 2, 4, 5])]
        w = np.isin(stages_without_n1, [5])
        deep_sleep = np.isin(stages_without_n1, [1, 2, 4])
        fragmentation_shift = np.logical_and(w[1:], deep_sleep[:-1])
        fragmentation_pos = np.where(fragmentation_shift)[0]
        #     fragmentation_pos = smooth_fragmentation_index(fragmentation_pos, fs=10)
        sfi_w = np.round(len(fragmentation_pos) / hours_sleep, 1)

        # arousal index, based on transitions to W from sleep
        w = np.isin(stages, [5])
        sleep = np.isin(stages, [1, 2, 3, 4])
        fragmentation_shift = np.logical_and(w[1:], sleep[:-1])
        fragmentation_pos = np.where(fragmentation_shift)[0]
        #     fragmentation_pos = smooth_fragmentation_index(fragmentation_pos, fs=10)
        arousali = np.round(len(fragmentation_pos) / hours_sleep, 1)

        statistics_result = [sfi, sfi_w, arousali]


    elif 'ahi' in signal_name:

        apnea_version = signal_name.split('ahi_')[1]

        if 'to_predict_apnea' in data_timerange.columns:
            apnea_pred = data_timerange.loc[data_timerange['to_predict_apnea'] == 1, 'apnea_pred_' + apnea_version].dropna()
            if len(apnea_pred) == 0: return i_statistics, [np.nan]
            # very rarely, the first 2 indices are not representative/not real sampling rate, check next few:
            for i_valid_idx in range(10):
                if (apnea_pred.index[i_valid_idx+1] - apnea_pred.index[i_valid_idx]).total_seconds() < 10:
                    break
            assert (apnea_pred.index[i_valid_idx+1] - apnea_pred.index[i_valid_idx]).total_seconds() == 1
            fs_apnea = 1
        else:
            apnea_pred = data_timerange['apnea_pred_' + apnea_version].dropna()
            if len(apnea_pred) == 0: return i_statistics, [np.nan]
            # very rarely, the first 2 indices are not representative/not real sampling rate, check next few:
            for i_valid_idx in range(10):
                if (apnea_pred.index[i_valid_idx+1] - apnea_pred.index[i_valid_idx]).total_seconds() < 10:
                    break
            assert (apnea_pred.index[i_valid_idx+1] - apnea_pred.index[i_valid_idx]).total_seconds() == 0.1
            fs_apnea = 10

        num_apneas = sum(apnea_pred.diff() == 1)

        valid_apnea_pred_idx = apnea_pred.index

        if apnea_version == 'expert':
            hours_sleep = sum(data_timerange.loc[valid_apnea_pred_idx, 'stage_pred_expert'].dropna() < 5) / 3600 / fs_apnea
        if '_aswti' in apnea_version:
            hours_sleep = sum(data_timerange.loc[valid_apnea_pred_idx, 'stage_pred_comb_breath_activity_1_aswti'].dropna() < 5) / 3600 / fs_apnea
        elif '_ss' in apnea_version: # normalize by hours of sleep:
            hours_sleep = sum(data_timerange.loc[valid_apnea_pred_idx, 'stage_pred_comb_breath_activity_1'].dropna() < 5) / 3600 / fs_apnea

        else: # normalize by available valid data length:
            hours_sleep = len(valid_apnea_pred_idx) / 3600 / fs_apnea

        if hours_sleep == 0:
            AHI = np.nan
        else:
            hours_sleep + 1e5
            AHI = num_apneas / hours_sleep
        statistics_result = [AHI]

    elif 'hypoxic_burden' in signal_name:

        hypoxia_version = signal_name.split('hypoxic_burden_')[1]

        if 'aswti' in signal_name:
            hours_sleep = sum(data_timerange['stage_pred_comb_breath_activity_1_aswti'].dropna() < 5) / fs / 3600 + 0.000001
        else:
            hours_sleep = sum(data_timerange['stage_pred_comb_breath_activity_1'].dropna() < 5) / fs / 3600 + 0.000001

        areas = np.array(data_timerange[f'hypoxic_area_{hypoxia_version}'].dropna()) / 60  # in minutes
        areas = areas[areas > 0]
        areas_robust = areas[areas < np.std(areas) * 3]
        hypoxic_burden = np.sum(areas_robust) / hours_sleep
        hypoxic_burden = np.round(hypoxic_burden, 1)
        statistics_result = [hypoxic_burden]

    elif signal_name in ['airgo_available_h']:
        statistics_result = [len(data_timerange.band.dropna()) / fs / 3600]
    elif signal_name in ['ecg_available']:
        statistics_result = [len(data_timerange.stage_pred_ecg_nn.dropna()) / fs / 3600]
    elif signal_name in ['airgo_ecg_available']:
        statistics_result = [data_timerange.loc[(pd.notna(data_timerange.band) & (pd.notna(data_timerange.stage_pred_ecg_nn))), :].shape[0] / fs / 3600]
    elif signal_name in ['spo2_available']:
        statistics_result = [len(data_timerange.spo2.dropna()) / fs / 3600]
    elif signal_name in ['spo2_airgo_available']:
        statistics_result = [data_timerange.loc[(pd.notna(data_timerange.band) & (pd.notna(data_timerange.spo2))), :].shape[0] / fs / 3600]
    elif signal_name in ['sleep_hours_breathing']:
        statistics_result = [sum(data_timerange.stage_pred_amendsumeffort.dropna() < 5) / fs / 3600]
    elif signal_name in ['sleep_hours_breathing_aswti']:
        statistics_result = [sum(data_timerange.stage_pred_amendsumeffort_aswti.dropna() < 5) / fs / 3600]
    elif signal_name in ['sleep_hours_breathcomb1']:
        statistics_result = [sum(data_timerange.stage_pred_comb_breath_activity_1.dropna() < 5) / fs / 3600]
    elif signal_name in ['sleep_hours_breathcomb1_aswti']:
        statistics_result = [sum(data_timerange.stage_pred_comb_breath_activity_1_aswti.dropna() < 5) / fs / 3600]
    elif signal_name in ['sleep_hours_ecg_nn']:
        statistics_result = [sum(data_timerange.stage_pred_ecg_nn.dropna() < 5) / fs / 3600]
    elif signal_name in ['sleep_hours_ecg_nn_aswti']:
        statistics_result = [sum(data_timerange.stage_pred_ecg_nn_aswti.dropna() < 5) / fs / 3600]
    elif signal_name in ['sleep_hours_expert']:
        statistics_result = [sum(data_timerange.stage_pred_expert.dropna() < 5) / fs / 3600]
    elif signal_name in ['sleep_hours_breathing_agrelaxed']:
        statistics_result = [sum(data_timerange[data_timerange['ecg_nn_amendsumeffort_agreement_relaxed'] == 1].stage_pred_ecg_nn.dropna() < 5) / fs / 3600]
    elif signal_name in ['sleep_hours_ecg_nn_agrelaxed']:
        statistics_result = [sum(data_timerange[data_timerange['ecg_nn_amendsumeffort_agreement_relaxed'] == 1].stage_pred_ecg_nn.dropna() < 5) / fs / 3600]
    elif signal_name in ['sleep_hours_breathing_disrelaxed']:
        statistics_result = [sum(data_timerange[data_timerange['ecg_nn_amendsumeffort_agreement_relaxed'] == 0].stage_pred_ecg_nn.dropna() < 5) / fs / 3600]
    elif signal_name in ['sleep_hours_ecg_nn_disrelaxed']:
        statistics_result = [sum(data_timerange[data_timerange['ecg_nn_amendsumeffort_agreement_relaxed'] == 0].stage_pred_ecg_nn.dropna() < 5) / fs / 3600]

    elif 'hypoxia_index' in signal_name:

        # we need to be careful here with denominator as well. right sleep timerange.
        # we wanna use the same timespan as the apnea prediction/analysis, so it stays comparable.
        # in other use cases, we might choose just the timespan where spo2 is available. here, though, we use
        # timespan where there's airgo+spo2.

        # part used in apnea statistics:

        if 'aswti' in signal_name:
            stage_name = 'stage_pred_comb_breath_activity_1_aswti'
            data_timerange_selection = data_timerange.loc[(pd.notna(data_timerange[stage_name])) & \
                                                          (data_timerange[stage_name] < 5), :]

        elif 'ss' in signal_name:
            stage_name = 'stage_pred_comb_breath_activity_1'
            data_timerange_selection = data_timerange.loc[(pd.notna(data_timerange[stage_name])) & \
                                                          (data_timerange[stage_name] < 5), :]
        else:
            stage_name = 'stage_pred_comb_breath_activity_1_aswti'
            data_timerange_selection = data_timerange.loc[pd.notna(data_timerange[stage_name]), :]

        hours_sleep = data_timerange_selection.shape[0] / fs / 3600 + 0.000001

        data_timerange_selection = data_timerange_selection[['spo2_clean']].copy()

        if hours_sleep == 0:
            spo2_perc_below_90 = np.nan
            sdi = np.nan
            ldi = np.nan
            tdi = np.nan

        else:

            spo2_perc_below_90 = compute_spo2_perc_below_90(data_timerange_selection)
            data_timerange_selection, no_hypoxia_short, no_hypoxia_long = hypoxia_drops(data_timerange_selection, fs=fs)
            sdi = no_hypoxia_short / hours_sleep
            ldi = no_hypoxia_long / hours_sleep
            tdi = (no_hypoxia_short + no_hypoxia_long) / hours_sleep

            if 0:
                print(f'Fraction of SpO2 < 90: {spo2_perc_below_90}')
                print(f'Number of short desats: {no_hypoxia_short}')
                print(f'Number of long desats: {no_hypoxia_long}')
                print(f'Hypoxia SDI: {sdi}')
                print(f'Hypoxia LDI: {ldi}')
                print(f'Hypoxia TDI: {tdi}')
                print('')

        statistics_result = [ldi, sdi, tdi, spo2_perc_below_90]

    elif signal_name in ['cam_s']:
        cams_morning, cams_evening = extract_cams(data_timerange[signal_name])
        statistics_result = [cams_morning, cams_evening]

    elif signal_name in ['hrv_nn']:
        data_tmp = data_timerange.hrv_nn[data_timerange.hrv_rpeak == 1]
        statistics_result = compute_statistics(data_tmp, i_statistics)

    else:
        # default behavior: assume signal name is column name, remove NaNs and compute statistics:
        data_tmp = data_timerange[signal_name].dropna()
        if signal_name == 'sofa_score':
            data_tmp = data_tmp[data_tmp != -99]
        elif signal_name in ['hco3_arterial', 'po2_arterial', 'pco2_arterial', 'ph_arterial']:
            data_tmp = data_tmp[data_tmp != -1]

        if data_tmp.shape[0] == 0:
            if signal_name in ['oxygen_flow_rate']:
                statistics_result = [0] * len(i_statistics)
            else:
                statistics_result = [np.nan] * len(i_statistics)

        else:
            statistics_result = compute_statistics(data_tmp, i_statistics)

    return i_statistics, statistics_result

def add_cam_to_day_night_parts(summary_days_subject):

    morning_cams = []

    for day_no in summary_days_subject.day_no.unique():
        summary_days_subject_day = summary_days_subject.loc[summary_days_subject.day_no == day_no]

        morning_cam = summary_days_subject_day.loc[summary_days_subject_day.day_cat == 'f', 'cam_s_morning'].values[0]
        evening_cam = summary_days_subject_day.loc[summary_days_subject_day.day_cat == 'f', 'cam_s_evening'].values[0]

        # same values for days:
        summary_days_subject.loc[(summary_days_subject.day_no == day_no) & (summary_days_subject.day_cat == 'd'), 'cam_s_morning'] = morning_cam
        summary_days_subject.loc[(summary_days_subject.day_no == day_no) & (summary_days_subject.day_cat == 'd'), 'cam_s_evening'] = evening_cam

        # same values for night for evening cams:
        summary_days_subject.loc[(summary_days_subject.day_no == day_no) & (summary_days_subject.day_cat == 'n'), 'cam_s_evening'] = evening_cam

        morning_cams.append(morning_cam)

    # cam_s morning for night parts become the cam s values after the night, i.e. we need to shift by 1 day:
    summary_days_subject.loc[(summary_days_subject.day_cat == 'n'), 'cam_s_morning'] = np.concatenate([morning_cams[1:], [np.nan]])

    return summary_days_subject


def add_statistics_to_tables(summary_subject, summary_days_part, signal_name, i_statistics, statistics_result, dt_key):

    for i_statistic, i_result in zip(i_statistics, statistics_result):
        tablecol_name = dt_key + '_' + signal_name + '_' + i_statistic
        tablecol_name = tablecol_name.replace('_index', '').replace('_sum_sum', '_sum')
        summary_subject[tablecol_name] = [i_result]

        tablecol_name = signal_name + '_' + i_statistic
        tablecol_name = tablecol_name.replace('_index', '').replace('_sum_sum', '_sum')
        summary_days_part[tablecol_name] = [i_result]

    return summary_subject, summary_days_part

def extract_summary_tables_for_subject(data, timerange, statistics_to_extract, study_id='000', clinical_table=None, fs=10):
    if statistics_to_extract == 'default':
        statistics_dict = init_statistics_to_extract_default()
    else:
        raise ValueError("Only default-statistics option implemented.")

    if timerange == 'all':
        timerange_dict = get_timerange_dict_airgo_available(data, study_id=study_id)
    elif timerange == 'sleeplab': # only extract the night of sleeplab study.
        timerange_dict = get_timerange_dict_airgo_available(data, study_id=study_id)
        dt_full_range = data.loc[data['airgo_signal_quality'] > 0].index
        dt_d1, dt_end = get_date_start_end_from_range(dt_full_range)
        timerange_dict = {}
        timerange_dict['n1'] = str(dt_d1) + ' 20:00:00 - ' + str(dt_d1 + timedelta(days=1)) + ' 08:00:00'
    else:
        raise ValueError(f"Timerange choice {timerange} not recognised. Only 'all' and 'sleeplab' implemented.")

    if clinical_table is None:
        merge_with_clinical_table = False
    else:
        merge_with_clinical_table = True

    summary_subject = pd.DataFrame()
    summary_days_subject = pd.DataFrame()

    summary_subject['study_id'] = [study_id]

    for dt_key in timerange_dict.keys():
        #         print(dt_key)
        summary_days_part = pd.DataFrame()
        summary_days_part['study_id'] = [study_id]
        summary_days_part['day_cat'] = [dt_key[0]]
        summary_days_part['day_no'] = [dt_key[1]]

        i_timerange = timerange_dict[dt_key]
        summary_days_part['timerange'] = [i_timerange]
        summary_subject[dt_key + '_' + 'timerange'] = [i_timerange]

        data_timerange = data.loc[i_timerange.split(' - ')[0]: i_timerange.split(' - ')[1]]

        for signal_name in statistics_dict:

            if (signal_name == 'cam_s') & (dt_key[0] != 'f'):
                continue  # only add cam s for full day.

            signal_is_available = signal_availability_check(data_timerange, signal_name)
            # if signal needed is not available, just return None.
            if signal_is_available:

                # sleep stage-wise feature extraction.
                # loop over all sleep stages and gather results before moving on.
                if '_stagewise' in signal_name:
                    i_statistics = []
                    statistics_result = []

                    for stage_version in ['stage_pred_ecg_nn', 'stage_pred_amendsumeffort']:
                        if stage_version not in data.columns:
                            continue

                        for i_stage, stage in enumerate(['N3', 'N2', 'N1', 'R', 'W', 'N2N3', 'S']):
                            stage_no = i_stage + 1
                            if stage in ['N3', 'N2', 'N1', 'R', 'W']: # 'real' stage:
                                data_stage = data_timerange[data_timerange[stage_version] == stage_no]
                            elif stage == 'N2N3':
                                data_stage = data_timerange[np.isin(data_timerange[stage_version], [1, 2])]
                            elif stage == 'S':
                                data_stage = data_timerange[np.isin(data_timerange[stage_version], [1, 2, 3, 4])]

                            signal_name_extract = signal_name.replace('_stagewise', '')

                            if '_agrelaxed' in signal_name:
                                data_stage = data_stage[data_stage['ecg_nn_amendsumeffort_agreement_relaxed'] == 1]
                                signal_name_extract = signal_name_extract.replace('_agrelaxed', '')
                            elif '_disrelaxed' in signal_name:
                                data_stage = data_stage[data_stage['ecg_nn_amendsumeffort_agreement_relaxed'] == 0]
                                signal_name_extract = signal_name_extract.replace('_disrelaxed', '')

                            if data_stage.shape[0] < fs * 60 * 5:
                                i_statistics_stage = statistics_dict[signal_name_extract]
                                statistics_result_stage = [np.nan] * len(i_statistics_stage)

                            else:
                                i_statistics_stage, statistics_result_stage = extract_statistics_for_timerange(data_stage,
                                                                                                   signal_name_extract,
                                                                                                   statistics_dict,
                                                                                                   fs=fs)
                                # i_statistics <-- add sleep stage name here. make a list and add this list to the table.

                            i_statistics += [stage_version.replace('stage_pred_', '') + f'_{stage}_' + x for x in i_statistics_stage]
                            statistics_result += statistics_result_stage

                else:
                    i_statistics, statistics_result = extract_statistics_for_timerange(data_timerange, signal_name,
                                                                                       statistics_dict, fs=fs)
            else:
                i_statistics = statistics_dict[signal_name]
                statistics_result = [np.nan] * len(i_statistics)

            summary_subject, summary_days_part = add_statistics_to_tables(summary_subject, summary_days_part, signal_name, i_statistics, statistics_result, dt_key)


        if merge_with_clinical_table:
            table_subject = clinical_table[clinical_table.study_id == int(study_id)].reset_index(drop=True)
            summary_days_part = table_subject.join(summary_days_part.drop('study_id', axis=1), how='outer')
            assert summary_days_part.shape[0] == 1

        summary_days_subject = pd.concat([summary_days_subject, summary_days_part], axis=0, sort=False)

    if np.all([x in data.columns for x in ['cam_s_morning', 'cam_s_evening']]):
        summary_days_subject = add_cam_to_day_night_parts(summary_days_subject)

    if merge_with_clinical_table:
        table_subject = clinical_table[clinical_table.study_id == int(study_id)].reset_index(drop=True)
        summary_subject = table_subject.join(summary_subject.drop('study_id', axis=1), how='outer')
        assert summary_subject.shape[0] == 1

    return summary_subject, summary_days_subject


def compute_apnea_pred_with_ss(data, stage_version='stage_pred_comb_breath_activity_1', add_on='_ss'):
    apnea_versions = ['apnea_pred_ro_a3', 'apnea_pred_rsr_a3', 'apnea_pred_any_a3',
                      'apnea_pred_va_a3', 'apnea_pred_vb_a3']

    for apnea_ver in apnea_versions:
        if not apnea_ver in data.columns:
            data[apnea_ver] = np.nan
            data[apnea_ver + add_on] = np.nan

        data[apnea_ver + add_on] = data[apnea_ver].copy()
        data.loc[data[stage_version] == 5, apnea_ver + add_on] = 0

    return data


def main():

    data_type = 'icu'

    save = False

    if data_type == 'icu':

        dir_input = f'/scr/wolfgang/Sleep_And_Breathing/icu_files_step8' # compute ahi versions etc # for Sleep and Breathing
        # dir_input = f'/media/mad3/Projects/ICU_SLEEP_STUDY/Sleep_And_Breathing/icu_files_step3_nohrv' # for Undiagnosed Apnea
        # dir_save = f'/media/mad3/Projects/ICU_SLEEP_STUDY/Sleep_And_Breathing/icu_files_step4_nohrv'

        # clinical table, where data gets added:
        # table_path = '/media/mad3/Projects/ICU_SLEEP_STUDY/Undiagnosed_Apnea/summary_subjects_icu.csv'
        table_path = '/media/mad3/Projects/ICU_SLEEP_STUDY/Sleep_And_Breathing/summary_subjects_icu.csv'

        # table_path = '/media/mad3/Projects/Wolfgang/backup/summary_subjects_1.csv'
        table = pd.read_csv(table_path)
        table.rename({'Study ID': 'study_id'}, inplace=True, axis=1)
        # remove dummy biosignals columns:
        table = table[table.columns[:22]]
        files = os.listdir(dir_input)
        timerange = 'all'

    elif data_type == 'sleeplab':

        dir_input = f'/scr/wolfgang/Sleep_And_Breathing/sleeplab_files_step6'
        # dir_save = f'/media/mad3/Projects/ICU_SLEEP_STUDY/Sleep_And_Breathing/sleeplab_files_step5'

        files = os.listdir(dir_input)

        study_ids = [x.replace('psg_airgo_10hz_', '').replace('.h5', '') for x in files]
        study_ids.sort()
        table = pd.DataFrame()
        table['study_id'] = study_ids
        timerange = 'sleeplab'

    if save:
        if not os.path.exists(dir_save):
            os.makedirs(dir_save)

    files.sort()
    print(len(files))

    summary_subjects = pd.DataFrame()
    summary_days = pd.DataFrame()

    # summary_subjects = pd.read_csv('summary_subjects.csv')
    # summary_days = pd.read_csv('summary_days.csv')
    #
    # remove_study_ids = [92] + list(range(135, 190)) # remove last subject.
    # for remove_id in remove_study_ids:
    #     summary_subjects = summary_subjects.loc[summary_subjects.study_id != remove_id, :]
    #     summary_days = summary_days.loc[summary_days.study_id != remove_id, :]

    print(table.study_id.unique().shape)
    overwrite = True

    # vers = int(sys.argv[1])
    vers = 2

    if vers == 1:
        files = files[:55]
        suffix = '_1'
    elif vers == 2:
        files = files[55:]
        suffix = '_2'
    elif vers == 3:
        files = files[90:]
        suffix = '_3'
    elif vers == 'tmp':
        files = ['icusleep_079.h5']
        suffix = '_tmp'
    else:
        suffix = ''


    # files = ['icusleep_121.h5']

    for file in files:

        try:
        # if 1:
            filepath = os.path.join(dir_input, file)
            study_id = re.search('\d\d\d', file)[0]

            if (data_type=='icu') & True:
                if not int(study_id) in table.study_id.values:
                    continue
            if 0:
                if int(study_id) in summary_subjects.study_id.values:
                    continue

            print(study_id)

            d = get_metadata(filepath)
            data, hdr, fs = read_in_routine(filepath)

            # compute airgo quality and remove airgo derivates with bad quality, if not yet done.
            if 'airgo_signal_quality' not in data.columns:
                data, hdr = airgo_signal_quality_routine(data, hdr, fs)

            # some preprocessing dependent on icu or sleeplab:
            if data_type == 'icu':
                data['edw_bp_map'] = (data.edw_bp_systolic + 2 * data.edw_bp_diastolic) / 3

            elif data_type == 'sleeplab':
                data['apnea_pred_expert'] = np.isin(data.apnea.values, [1,2,3,4]).astype(int)
                data.rename({'pr': 'hr'}, axis=1, inplace=True)
                data.rename({'stage': 'stage_pred_expert'}, axis=1, inplace=True)

            do_aswti_sleepstage = True
            if do_aswti_sleepstage:
                data = sleep_stage_aswti(data, 'stage_pred_comb_breath_activity_1', min_sleep=30, fs=fs)
                data = sleep_stage_aswti(data, 'stage_pred_amendsumeffort', min_sleep=30, fs=fs)
                data = sleep_stage_aswti(data, 'stage_pred_ecg_nn', min_sleep=30, fs=fs)
                data = sleep_stage_aswti(data, 'stage_pred_expert', min_sleep=30, fs=fs)

            do_compute_self_similarity = True
            if do_compute_self_similarity & ('self_similarity' not in data.columns):
                data = self_similarity_airgo(data)

            do_compute_spo2_clean = True
            if do_compute_spo2_clean:
                data = compute_spo2_clean(data, fs=fs)

            if not 'spo2_airgo' in data.columns: # spo2 when airgo is available
                if np.all([x in data.columns for x in ['band', 'spo2']]):
                    data['spo2_airgo'] = data['spo2'].values
                    data.loc[pd.isna(data.band), 'spo2_airgo'] = np.nan

            if not 'spo2_airgo_clean' in data.columns: # spo2 when airgo is available
                if np.all([x in data.columns for x in ['band', 'spo2_clean']]):
                    data['spo2_airgo_clean'] = data['spo2_clean'].values
                    data.loc[pd.isna(data.band), 'spo2_airgo_clean'] = np.nan

            if 'self_similarity' in data.columns:
                data.loc[
                    (data.airgo_signal_quality == 0) | (pd.isna(data.airgo_signal_quality)), 'self_similarity'] = np.nan

            # APNEA PRED VB:
            apnea_column = 'apnea_pred_vb_a3'
            # if (apnea_column == 'apnea_pred_vb_a3') & (apnea_column not in data.columns):
            if 1:
                # 'vb': 'va' but take RSR if opioids are given. if RSR not available, NaN.
                if all([x in data.columns for x in ['opioids_sum', 'apnea_pred_va_a3']]):
                    opioids_sum_1h = (data['opioids_sum'].rolling('1h').max() > 0).values
                    data['apnea_pred_vb_a3'] = data['apnea_pred_va_a3'].values
                    data.loc[opioids_sum_1h, 'apnea_pred_vb_a3'] = data.loc[opioids_sum_1h, 'apnea_pred_rsr_a3'].values

            apnea_columns = ['apnea_pred_any_a3', 'apnea_pred_ro_a3', 'apnea_pred_rsr_a3', \
                             'apnea_pred_va_a3', 'apnea_pred_vb_a3']
            apnea_columns = apnea_columns + [x + '_ss' for x in apnea_columns]
            data = compute_apnea_pred_with_ss(data, stage_version='stage_pred_comb_breath_activity_1')
            apnea_columns = apnea_columns + [x + '_aswti' for x in apnea_columns if 'ss' in x]
            data = compute_apnea_pred_with_ss(data, stage_version='stage_pred_comb_breath_activity_1_aswti', add_on='_ss_aswti')

            # HYPOXIC BURDEN COMPUTATION:
            apnea_columns = apnea_columns + ['apnea_pred_expert']
            for apnea_name in apnea_columns:
                if not apnea_name in data.columns:
                    continue
                hypoxia_name = 'hypoxic_area' + apnea_name.replace('apnea_pred', '')
                if 'aswti' in apnea_name:
                    hours_sleep = 'stage_pred_comb_breath_activity_1_aswti'  # name of sleep stage column, or int/float for manual setting.
                else:
                    hours_sleep = 'stage_pred_comb_breath_activity_1'
                if hypoxia_name not in data.columns:
                    data, hypoxia_burden = compute_hypoxia_burden(data, fs, apnea_name=apnea_name,
                                                              hypoxia_name=hypoxia_name, hours_sleep=hours_sleep)

            # RR CORRECTION (remove artifacts):
            if 'ibi' in data.columns:
                data.loc[data.ibi > 12, 'ibi'] = np.nan # IBI of >12 means <5 breaths per minute.

            if 'rr_10s_smooth' in data.columns:
                data.loc[data.rr_10s_smooth < 5, 'rr_10s_smooth'] = np.nan
                data.loc[data.rr_10s_smooth > 60, 'rr_10s_smooth'] = np.nan

            if data.band.dropna().shape[0] == 0:
                print(f'No valid AirGo data any more, skip {file}')
                continue

            statistics_to_extract = 'default'

            if data_type == 'icu':
                clinical_table = table
            elif data_type == 'sleeplab':
                clinical_table = None
            summary_subject, summary_days_subject = extract_summary_tables_for_subject(data, timerange,
                                                                                       statistics_to_extract,
                                                                                       study_id=study_id,
                                                                                       clinical_table=clinical_table,
                                                                                       fs = fs)

            summary_subjects = pd.concat([summary_subjects, summary_subject], axis=0, sort=False)
            summary_days = pd.concat([summary_days, summary_days_subject], axis=0, sort=False)

            summary_subjects.to_csv('summary_subjects_' + data_type + suffix + '.csv', index=False)
            summary_days.to_csv('summary_days_' + data_type + suffix + '.csv', index=False)

            if save:
                filepath_save = os.path.join(dir_save, file)
                cols_to_drop = ['apnea_binary', 'apnea_end']
                for col_to_drop in cols_to_drop:
                    data.drop(col_to_drop, axis=1, inplace=True)

                write_to_hdf5_file(data, filepath_save, hdr=hdr, overwrite=True)

        except Exception as e:
            print(file)
            print(e)
            print(''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)))
            continue

    summary_subjects.to_csv('summary_subjects_' + data_type + suffix + '.csv', index=False)
    summary_days.to_csv('summary_days_' + data_type + suffix + '.csv', index=False)


if __name__ == '__main__':
    main()



