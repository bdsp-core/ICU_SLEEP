import sys
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt


sys.path.append('/home/wolfgang/repos/sleep_general')
from mgh_sleeplab import load_mgh_signal, annotations_preprocess, vectorize_respiratory_events, vectorize_sleep_stages

from sleep_analysis_functions import compute_spo2_clean, compute_hypoxia_burden, desaturation_detection, \
    hypoxaemic_burden_minutes
import datetime


def compute_hypoxia_statistics(data, apnea, sleep_stage, fs):
    data['apnea'] = apnea

    dt_start = pd.Timestamp('2000-01-01 00:00:00')
    dt_end = dt_start + datetime.timedelta(seconds=(data.shape[0] - 1) / fs)
    pseudo_dt_index = pd.date_range(start=dt_start, end=dt_end, periods=data.shape[0])
    data.index = pseudo_dt_index

    data = compute_spo2_clean(data, fs=fs)
    data['spo2'] = data['spo2_clean']

    data['apnea_binary'] = np.isin(data['apnea'], [1, 2, 3, 4]).astype(int)
    data['apnea_end'] = np.isin(data['apnea_binary'].diff(), [-1])

    sleep_stage = sleep_stage[np.logical_not(pd.isna(sleep_stage))]
    hours_sleep = sum(sleep_stage < 5) / fs / 3600

    data, hypoxia_burden = compute_hypoxia_burden(data, fs, hours_sleep=hours_sleep, apnea_name='apnea')

    T90burden, T90desaturation, T90nonspecific = hypoxaemic_burden_minutes(data['spo2'].values, fs)

    AHI = np.round(sum(data['apnea_end']) / hours_sleep, 1)

    return hypoxia_burden, AHI, hours_sleep, T90burden, T90desaturation, T90nonspecific


path_signal = "/media/mad3/Datasets_ConvertedData/sleeplab/grass_data/Cellucci_Lawrence_100816_2135.000/Signal_Cellucci_Lawrence_100816_2135.000.mat"
path_annotations = "/media/mad3/Datasets_ConvertedData/sleeplab/grass_data/Cellucci_Lawrence_100816_2135.000/annotations.csv"
print(path_signal)
print(path_annotations)

# read in raw data:
signal, params = load_mgh_signal(path_signal)
annotations = pd.read_csv(path_annotations)

fs = int(params['Fs'])
signal_len = signal.shape[0]

# get respiratory event and sleep stage array:
annotations = annotations_preprocess(annotations, fs)
resp = vectorize_respiratory_events(annotations, signal_len)
sleep_stage = vectorize_sleep_stages(annotations, signal_len)

hypoxia_burden, ahi, total_sleep_time, T90burden, T90desaturation, T90nonspecific = compute_hypoxia_statistics(signal, resp, sleep_stage, fs)

print(ahi)
print(hypoxia_burden)
print(total_sleep_time)
print(T90burden)
print(T90desaturation)
print(T90nonspecific)
