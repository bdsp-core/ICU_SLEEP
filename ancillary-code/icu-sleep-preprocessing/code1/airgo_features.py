import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.signal import find_peaks
import datetime
from sklearn.cluster import KMeans
from scipy.stats import variation
from math import factorial, log
from numba import jit
import warnings

# try:
#     from entropy import sample_entropy, katz_fd
# except: 
#     print('Entropy package not installed. Use complexity_features=0 when computing airgo features.')

import multiprocessing
from multiprocessing import Pool


def main():

    airgo_research_dir = '//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/data_analysis/AirGo/airgo_research/'
    airgo_features_dir = '//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/data_analysis/AirGo/airgo_features/'
    airgo_features_dir_4Hz = '//mad3/MGH-NEURO-CDAC/Projects/ICU_SLEEP_STUDY/data/data_analysis/AirGo/airgo_features_4Hz/'

    # test = pd.read_csv(airgo_features_dir_4Hz+'airgo_001.csv')

    files = os.listdir(airgo_research_dir)[130:]
    # files = ['airgo_006.csv']

    for file in files:

        print(file)
        try:
            if not os.path.exists(os.path.join(airgo_features_dir,file)):
                filepath = os.path.join(airgo_research_dir, file)
                data = pd.read_csv(filepath)

                # just changed to structure of the code, if error its probably just names of variables or so:
                airgo_features = compute_airgo_features(data)
                data.columns = [columnname.lower() for columnname in data.columns]
                data.index.name = 'datetime'


                airgo_features4Hz = resample_to_4hz(airgo_features)

                airgo_features.to_csv(os.path.join(airgo_features_dir,file))
                airgo_features4Hz.to_csv(os.path.join(airgo_features_dir_4Hz,file))
        except Exception as e:
            print(e)
            continue


def compute_airgo_features(data, n_cores=None, fs=10, complexity_features=1, verbose=False):
    """ Compute airgo features in parallel and also in 24-hour chunks. """

    if n_cores is None:
        n_cores = multiprocessing.cpu_count() - 1

    data_processed = pd.DataFrame()
    part_hours = 12 # 8 hour blocks
    n_parts = int(np.ceil(data.shape[0] / fs / 3600 / part_hours))
    if verbose:
        print(f"Number of CPUs used for airgo feature compuatation: {n_cores}")
        print(f"Break down data into {n_parts} {part_hours}-hours parts.")
    for i_part in range(n_parts):
        if verbose:
            print(f"Part {i_part}")
        part_start = data.index[0] + datetime.timedelta(seconds=i_part * 3600 * part_hours)
        part_end = data.index[0] + datetime.timedelta(seconds=(i_part + 1) * 3600 * part_hours)
        part_start_processing = data.index[0] + datetime.timedelta(seconds=i_part * 3600 * part_hours) - datetime.timedelta(
            seconds=15 * 60)  # 15 minute overlap with previous day for processing
        part_end_processing = data.index[0] + datetime.timedelta(seconds=(i_part + 1) * 3600 * part_hours) + datetime.timedelta(
            seconds=15 * 60)  # 15 minute overlap to next day for processing

        data_day_tmp = data[part_start_processing:part_end_processing].copy()

        if n_cores > 1:
            assert fs == 10, 'fs != 10, change of parallel processing function is required.'
            data_split = np.array_split(data_day_tmp, n_cores)
            pool = Pool(n_cores)
            data_day_tmp = pd.concat(pool.map(compute_airgo_features_main, data_split))
            pool.close()
            pool.join()

        else:
            data_day_tmp = compute_airgo_features_main(data_day_tmp, fs=fs, complexity_features=complexity_features)

        data_day_tmp = data_day_tmp.loc[part_start: part_end] # remove overlap with other days.
        data_day_tmp = data_day_tmp.iloc[:-1, :] # last sample overlapping
        data_processed = pd.concat([data_processed, data_day_tmp], axis=0, sort=False) # collect all days again.

    return data_processed


def compute_airgo_features_backup(data, n_cores=None, fs=10, complexity_features=1):

    if n_cores is None:
        n_cores = multiprocessing.cpu_count() - 1

    if n_cores > 1:
        assert fs == 10, 'fs != 10, change of parallel processing function is required.'
        data_split = np.array_split(data, n_cores)
        pool = Pool(n_cores)
        data = pd.concat(pool.map(compute_airgo_features_main, data_split))
        pool.close()
        pool.join()

    else:
        data = compute_airgo_features_main(data, fs=fs, complexity_features=complexity_features)

    return data


def resample_to_4hz(airgo_features):

    fs4_data = airgo_features.resample(datetime.timedelta(seconds=0.25)).mean()
    fs4_data.drop('peaks',axis=1)
    fs4_data.columns = [columnname.lower() for columnname in fs4_data.columns]
    fs4_data.index.name = 'datetime'

    return fs4_data



def acceleration_position(data):
    data['position_cluster'] = -1
#     cluster_names = ['right_lateral','left_lateral','suspine','prone']
    cluster_centers = np.array([
        [-0.10528739, -0.90177368,  0.07899741],
        [-0.14248938,  0.96973593, -0.06413331],
        [-0.16258391, -0.05833847, -0.9190312 ],
        [ 0.01891357,  0.09631911,  0.98882481]
    ])

    kmeans = KMeans(n_clusters=4, init=cluster_centers)
    kmeans.cluster_centers_ = cluster_centers
    index_valid = data[['accx_1sec','accy_1sec','accz_1sec']].dropna().index
    data.loc[index_valid, 'position_cluster'] = kmeans.predict(data[['accx_1sec','accy_1sec','accz_1sec']].dropna())
    
    return data


def airgo_acc_positioning_rulebased(data, fs=10, g=9.81):
    # first, set up array for airgo console position, if airgo was worn correctly or upside down
    accx_robust = pd.Series(data['accx'].values).rolling(5 * 60 * fs, center=True,
                                              min_periods=1).median()  # 5 min median for stability

    airgo_console_direction = np.zeros(data.shape[0], )
    airgo_console_direction[:] = np.nan
    first_valid_indeces = np.where(pd.notna(data['accx'].values))[0][:10 * fs]
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        airgo_console_direction[first_valid_indeces] = 1 # null hypothesis: correctly worn in the beginning.
        airgo_console_direction[accx_robust.values < -5] = 1 # 1 ... correctly
        airgo_console_direction[accx_robust.values > 5] = 2  # 2 ... upside-down
    airgo_console_direction = pd.Series(airgo_console_direction).fillna(method='ffill').rolling(10 * fs).median()
    airgo_console_direction[pd.isna(data.accx.values)] = np.nan
    # reverse X and Y values where airgo console is worn upside down:
    accx_corrected = data['accx'].values
    accy_corrected = data['accy'].values
    accx_corrected[airgo_console_direction == 2] = - accx_corrected[airgo_console_direction == 2]
    accy_corrected[airgo_console_direction == 2] = - accy_corrected[airgo_console_direction == 2]

    # apply the actual positioning logic based on the accelerometer data:
    acc_position = np.zeros(data.shape[0], )
    acc_position[:] = np.nan
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        acc_position[accx_corrected < -5/g] = 1 # 1 upright
        acc_position[pd.isna(acc_position) & (
                    data.accz < -5/g)] = 2  # 2 supine, pd.isna(data.acc_position)  basically works as 'else', i.e. only consider if it was not decided before.
        acc_position[pd.isna(acc_position) & (data.accz.values > 5/g)] = 3  # 3 prone
        acc_position[pd.isna(acc_position) & (accy_corrected < -5/g)] = 4  # 4 lateral right
        acc_position[pd.isna(acc_position) & (accy_corrected > 5/g)] = 5  # 5 lateral left
        acc_position[pd.isna(acc_position) & (pd.notna(accx_corrected))] = 6  # 6 ambiguous
    data['acc_position'] = acc_position
    data['airgo_console_direction'] = airgo_console_direction.values

    # data['airgo_console_direction'] = np.nan
    # first_valid_indeces = data['accx'].dropna().iloc[:10 * fs].index
    # data.loc[first_valid_indeces, 'airgo_console_direction'] = 1 # null hypothesis: correctly worn in the beginning.
    # data.loc[data.accx_robust < -5, 'airgo_console_direction'] = 1  # 1 ... correctly
    # data.loc[data.accx_robust > 5, 'airgo_console_direction'] = 2  # 2 ... upside-down
    # data.loc[pd.notna(data.accx), 'airgo_console_direction'] = data.loc[
    #     pd.notna(data.accx), 'airgo_console_direction'].fillna(method='ffill')
    # data.loc[pd.notna(data.accx), 'airgo_console_direction'] = data.loc[
    #     pd.notna(data.accx), 'airgo_console_direction'].rolling(10 * fs).median()
    # # reverse X and Y values where airgo console is worn upside down:
    # data['accx_corrected'] = data['accx']
    # data['accy_corrected'] = data['accy']
    # data.loc[data.airgo_console_direction == 2, 'accx_corrected'] = -1 * data.loc[
    #     data.airgo_console_direction == 2, 'accx'].values
    # data.loc[data.airgo_console_direction == 2, 'accy_corrected'] = -1 * data.loc[
    #     data.airgo_console_direction == 2, 'accy'].values

    # apply the actual positioning logic based on the accelerometer data:
    # data['acc_position'] = np.nan
    # data.loc[data.accx_corrected < -5, 'acc_position'] = 1  # 1 upright
    # data.loc[pd.isna(data.acc_position) & (
    #             data.accz < -5), 'acc_position'] = 2  # 2 supine, pd.isna(data.acc_position)  basically works as 'else', i.e. only consider if it was not decided before.
    # data.loc[pd.isna(data.acc_position) & (data.accz > 5), 'acc_position'] = 3  # 3 prone
    # data.loc[pd.isna(data.acc_position) & (data.accy_corrected < -5), 'acc_position'] = 4  # 4 lateral right
    # data.loc[pd.isna(data.acc_position) & (data.accy_corrected > 5), 'acc_position'] = 5  # 5 lateral left
    # data.loc[pd.isna(data.acc_position) & (pd.notna(data.accx_corrected)), 'acc_position'] = 6  # 6 ambiguous

    # data.drop(['accx_robust', 'airgo_console_direction', 'accx_corrected', 'accy_corrected'], axis=1, inplace=True)

    return data


def airgo_breath_peak_detection(data, fs=10, prominence=1, rel_height=1.):
    # default prominence and rel_height values are based on unscaled/unnormalized airgo values. for normalized, values should be 0.01

    if 'movavg_0_5s_unscaled' not in data.columns:
        data['movavg_0_5s_unscaled'] = data['band_unscaled'].reset_index()['band_unscaled'].rolling(int(0.5*fs), center=True, min_periods=1).mean().values

    data['movavg_0_5s_unscaled_detrended'] = data['movavg_0_5s_unscaled'].values - data['movavg_0_5s_unscaled'].reset_index()['movavg_0_5s_unscaled'].rolling(120*fs, center=True, min_periods=1).mean().values
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        peaks, peak_prop = find_peaks(data.movavg_0_5s_unscaled_detrended.values, prominence=1, distance=int(fs*1.2), width=int(0.4*fs), rel_height=1, wlen=20*fs);
    # rel_height=1 makes width be measured at bottom of peak candidates.
    peaks_loc = data.index[peaks]
    tmp_array = np.zeros((data.shape[0],))
    tmp_array[peaks] = 1
    data['peaks'] = 0
    data['peaks'] = tmp_array
    tmp_array = np.zeros((data.shape[0],))
    tmp_array[peaks] = peak_prop['prominences']
    data['peak_prom'] = 0
    data['peak_prom'] = tmp_array

    # CRITERIA 1: peak prominence must exceed an adaptive threshold, based on moving standard deviation:
    data['movstd_1min_unscaled'] = pd.Series(data['movavg_0_5s_unscaled_detrended'].values).rolling(60*fs, center=True, min_periods=1).std().values
    data['movstd_30sec_unscaled'] = pd.Series(data['movavg_0_5s_unscaled_detrended'].values).rolling(30*fs, center=True, min_periods=1).std().values
    min_std_baseline = np.array([data['movstd_30sec_unscaled'].values, data['movstd_1min_unscaled'].values]) # parallel processing is faster with this univariate df column selecion!
    # min_std_baseline = data[['movstd_30sec_unscaled', 'movstd_1min_unscaled']].values
    min_std_baseline = np.min(min_std_baseline, axis=0)
    data['min_std_baseline'] = min_std_baseline
    peaks = data['peaks'].values
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        peaks[(data['peak_prom'].values < data['min_std_baseline'].values * 0.65) & (data['peak_prom'].values > 0)] = 0.5
    data['peaks'] = peaks

    # data = data.drop('min_std_baseline', axis=1) # do not activate in parallel processing
    # CRITERIA 2: further small and short breaths, compared to neighboring breaths, are removed.

    num_corrected_small_short = 0
    peaks = np.where(data['peaks'] == 1)[0]
    prom = data['peak_prom'].iloc[peaks].values
    peaks_array = data['peaks'].values

    for i in range(500):
        diff_between_peaks = np.concatenate([[4*fs],np.diff(peaks)]) # add 40 samples = 4 sec as standard peak to peak value in the beinning.
        ratio_time_between_peaks = np.concatenate([[1],np.divide(diff_between_peaks[1:], diff_between_peaks[:-1])])
        ratio_prom_pre = np.divide(prom[1:], prom[:-1])
        ratio_prom_pre = np.concatenate([[1], ratio_prom_pre])
        ratio_prom_post = np.divide(prom[:-1], prom[1:])
        ratio_prom_post = np.concatenate([ratio_prom_post, [1]])
        small_and_short_breath = (ratio_prom_pre < 0.55) & (ratio_time_between_peaks < 0.55) & (diff_between_peaks < fs*2)
        if sum(small_and_short_breath) == 0: break
        peaks_array[np.where(small_and_short_breath)[0]] = 0.6 # for parallel
        num_corrected_previous = num_corrected_small_short
        num_corrected_small_short = sum(peaks_array == 0.6)
        peaks = np.where(peaks_array == 1)[0]
        prom = data['peak_prom'].values[peaks]
        if num_corrected_small_short == num_corrected_previous: break

    data['peaks'] = peaks_array

    return data
            
    
def compute_breathing_instability_index(data, vname='2min', sec=120, fs=10):
    data[f'ventilation_cvar_{vname}'] = data[f'ventilation_10s_smooth'].reset_index(drop=True).rolling(sec*fs, center=True, min_periods=1).apply(lambda x: variation(x, nan_policy='omit'), raw=True).values
    data[f'IBI_cvar_{vname}'] = data['IBI'].reset_index()['IBI'].rolling(sec*fs, center=True, min_periods=1).apply(lambda x: variation(x, nan_policy='omit'), raw=True).values
    data[f'instability_index_{vname}'] = (data[f'ventilation_cvar_{vname}'].values + data[f'IBI_cvar_{vname}'].values)/2
    return data


def compute_breathing_instability_index_routine(data, fs=10):

    data['ventilation_10s']   = data['ventilation0'].reset_index(drop=True).rolling(10*fs, center=True, min_periods=1).sum().values*6
    data['ventilation_10s_smooth'] = data['ventilation_10s'].reset_index(drop=True).rolling(6*fs, center=True, min_periods=1).mean().values

    vname='30sec'
    sec=30
    data = compute_breathing_instability_index(data, vname=vname, sec=sec, fs=10)

    vname='1min'
    sec=60
    data = compute_breathing_instability_index(data, vname=vname, sec=sec, fs=10)

    vname='2min'
    sec=120
    data = compute_breathing_instability_index(data, vname=vname, sec=sec, fs=10)

    vname='5min'
    sec=300
    data = compute_breathing_instability_index(data, vname=vname, sec=sec, fs=10)
    
    return data


def clip_z_normalize(signal):

    signal_clipped = np.clip(signal.dropna(), np.percentile(signal.dropna(),1), np.percentile(signal.dropna(),99))
    mean = np.mean(signal_clipped.astype(np.float32))
    std = np.std(signal_clipped.astype(np.float32))
    signal = (signal - mean)/std

    return signal

 
def compute_airgo_features_main(data, fs=10, complexity_features=1):
    '''
    :param filepath: filepath to airgo research data file
    :return: airgo_features, dataframe containing original airgo data and additional features computed.
    '''

    verbose = False

    if 'band' not in data.columns:
        print("'compute_airgo_features(): band' not in data.columns, return data unchanged.")
        return data
    if data.band.dropna().shape[0] < fs*10:
        print("'compute_airgo_features(): 'band' contains less than 10 seconds of data. return data unchanged")
        return data

    if not type(data.index) == pd.core.indexes.datetimes.DatetimeIndex:
        data['datetime'] = pd.to_datetime(data['datetime'], infer_datetime_format=1)
        data.set_index('datetime', inplace=True)

    data['band_unscaled'] = data['band'].copy()
    data.band = clip_z_normalize(data.band)

    data['movavg_0_5s'] = data['band'].reset_index()['band'].rolling(int(0.5*fs), center=True, min_periods=1).mean().values
    data['movavg_1_2s'] = data['band'].reset_index()['band'].rolling(int(1.2*fs), center=True, min_periods=1).mean().values
    data['movavg_1min'] = data['band'].reset_index()['band'].rolling(int(60*fs), center=True, min_periods=1).mean().values

    data['deriv1'] = np.concatenate([[0], np.diff(data['movavg_0_5s'])])

    if verbose:
        print('ventilation')
    # ventilation
    data['ventilation0']      = np.maximum(np.zeros(data['deriv1'].shape), data['deriv1'].values)
    data['ventilation_3s']    = data['ventilation0'].rolling('3s').sum()*20
    data['ventilation_8s']    = data['ventilation0'].rolling('8s').sum()*60/8
    data['ventilation_10s']   = data['ventilation0'].rolling('10s').sum()*6
    data['ventilation_12s']    = data['ventilation0'].rolling('12s').sum()*60/12
    data['ventilation_15s']    = data['ventilation0'].rolling('15s').sum()*60/15
    data['ventilation_30s']    = data['ventilation0'].rolling('30s').sum()*60/30
    data['ventilation_60s']   = data['ventilation0'].rolling('60s').sum()
    data['ventilation_5min']    = data['ventilation0'].rolling('5min').sum()/5
    data['ventilation_10min']    = data['ventilation0'].rolling('10min').sum()/10
 
    data['ventilation_10s_smooth'] = data['ventilation_10s'].rolling('10s').mean()

    data['hypo_10_60']        = np.zeros(data['ventilation_60s'].shape)
    data.loc[data['ventilation_60s'].values != 0, 'hypo_10_60'] = np.divide(data['ventilation_10s'][data['ventilation_60s'].values != 0] , data['ventilation_60s'].values[data['ventilation_60s'].values != 0])

    data['movmedian_5min']   = data['band'].rolling('5min').median()
    data['movmedian_10min']  = data['band'].rolling('10min').median()
    if verbose:
        print('movstd')
    # start = time.time()
    data['movstd_8s'] = data['band'].rolling('8s').std()
    data['movstd_12s'] = data['band'].rolling('12s').std()
    data['movstd_15s'] = data['band'].rolling('15s').std()
    data['movstd_10s']    = data['band'].rolling('10s').std()
    data['movstd_30s']    = data['band'].rolling('30s').std()
    data['movstd_60s']    = data['band'].rolling('60s').std()
    data['movstd_5min']   = data['band'].rolling('5min').std()
    data['movstd_10min']  = data['band'].rolling('10min').std()

    if complexity_features:
        if verbose:
            print('katz')
        # regularities for smooted airgo signal:
        data['katz_fd_10s_smoothed'] = data.movavg_1_2s.rolling('10s', min_periods=2).apply(lambda x: katz_fd(x), raw=True)
        data['katz_fd_30s_smoothed'] = data.movavg_1_2s.rolling('30s', min_periods=2).apply(lambda x: katz_fd(x), raw=True)
        data['katz_fd_45s_smoothed'] = data.movavg_1_2s.rolling('45s', min_periods=2).apply(lambda x: katz_fd(x), raw=True)
        data['katz_fd_60s_smoothed'] = data.movavg_1_2s.rolling('60s', min_periods=2).apply(lambda x: katz_fd(x), raw=True)

        if verbose:
            print('sample entropy')
        data['sample_entropy_10s_smoothed'] = data.movavg_1_2s.rolling('10s', min_periods=10).apply(lambda x: sample_entropy(x), raw=True)
        data['sample_entropy_30s_smoothed'] = data.movavg_1_2s.rolling('30s', min_periods=10).apply(lambda x: sample_entropy(x), raw=True)

        # data['sample_entropy_45s_smoothed'] = data.movavg_1_2s.rolling('45s', min_periods=10).apply(lambda x: sample_entropy(x), raw=True)
        data['sample_entropy_60s_smoothed'] = data.movavg_1_2s.rolling('60s', min_periods=10).apply(lambda x: sample_entropy(x), raw=True)

    # # quantiles:
    # for quantile in [0.01, 0.25, 0.5, 0.75, 0.99]:
    #     data['movstd_10s_q'+str(int(quantile*100))] = data['movstd_10s'].rolling('60s').quantile(quantile)
    #     data['ventilation_10s_q'+str(int(quantile*100))] = data['ventilation_10s'].rolling('60s').quantile(quantile)
    #     data['katz_fd_10s_q'+str(int(quantile*100))] = data['katz_fd_10s'].rolling('60s').quantile(quantile)
    #     data['movstd_10s_q'+str(int(quantile*100))] = data['movstd_10s'].rolling('60s').quantile(quantile)  

    # if compute_rr:
    #     peaks = find_peaks(data.band.values, prominence=25, distance=5, width=3)[0]

    #     data['peaks'] = 0
    #     data['peaks'].iloc[peaks] = 1

    #     data['rr_10s'] = data['peaks'].rolling(window='10s').sum() * 6
    #     data['rr_60s'] = data['peaks'].rolling(window='60s').sum()
    if verbose:
        print('peak detection')
    data = airgo_breath_peak_detection(data)

    data['rr_10s'] = data['peaks'].rolling(window='10s', min_periods=1).sum() * 6
    data['rr_60s'] = data['peaks'].rolling(window='60s', min_periods=1).sum()
    data['rr_10s_smooth'] = data['rr_10s'].rolling('10s', min_periods=1).mean()

    data['movmedian_1min'] = data['band'].reset_index()['band'].rolling(60*fs, center=True, min_periods=1).quantile(0.5).values
    data['movmedian_30sec'] = data['band'].reset_index()['band'].rolling(30*fs, center=True, min_periods=1).quantile(0.5).values

    if verbose:
        print('IBI')
    peaks = data['peaks'].values
    bb_interval = np.diff(np.where(peaks == 1)[0])
    # BB_interval = np.diff(np.where(data.peaks == 1)[0])
    bb_interval = np.concatenate([bb_interval[:1],bb_interval])
    ibi = np.zeros(data.shape[0], )
    ibi[peaks == 1] = bb_interval/fs
    ibi[ibi > 25] = 25
    data['IBI'] = ibi
    data['IBI'].interpolate(method='linear', limit=20*fs, limit_area='inside', inplace=True)

    ibi_mean_5min = data['IBI'][data.peaks == 1].rolling('5min', min_periods=1).mean()
    ibi_std_5min = data['IBI'][data.peaks == 1].rolling('5min', min_periods=1).std()

    ibi_mean_5min_array = np.zeros(data.shape[0],)
    ibi_mean_5min_array[peaks == 1] = ibi_mean_5min
    ibi_std_5min_array = np.zeros(data.shape[0],)
    ibi_std_5min_array[peaks == 1] = ibi_std_5min
    data['IBI_mean_5min'] = ibi_mean_5min_array
    data['IBI_std_5min'] = ibi_std_5min_array

    data['ventilation_5min_deriv'] = data.ventilation_5min.diff().rolling('5min', min_periods=1).mean()
    # troughs, inhalation, exhalation time features:
    data['troughs'] = 0
    data['inht'] = np.nan
    data['exht'] = np.nan
    data['inht_exht_ratio'] = np.nan
    data['inht_cycle_ratio'] = np.nan
    # loc_peak = data[data.peaks == 1].index
    # trough_loc = [data.movavg_0_5s[loc_peak[iP]:loc_peak[iP+1]].idxmin() for iP in range(loc_peak.shape[0]-1)]
    # data.loc[trough_loc, 'troughs'] = 1

    movavg_0_5s = data['movavg_0_5s'].values
    peaks_idx = np.where(peaks == 1)[0]
    troughs_idx = [np.argmin(movavg_0_5s[peaks_idx[iP] : peaks_idx[iP+1]]) + peaks_idx[iP] for iP in range(len(peaks_idx)-1)]
    troughs = np.zeros(data.shape[0], )
    troughs[troughs_idx] = 1
    data['troughs'] = troughs

    troughs_idx = np.where(data.troughs == 1)[0]

    inht = np.zeros(data.shape[0], )
    exht = np.zeros(data.shape[0], )
    inht_exht_ratio = np.zeros(data.shape[0], )
    inht_cycle_ratio = np.zeros(data.shape[0], )
    inht[peaks_idx[1:]] = (peaks_idx[1:] - troughs_idx)/fs
    exht[peaks_idx[:-1]] = (troughs_idx - peaks_idx[:-1])/fs
    inht_exht_ratio[peaks_idx] = inht[peaks_idx] / (exht[peaks_idx] + 0.0001);
    inht_cycle_ratio[peaks_idx] = inht[peaks_idx] / (inht[peaks_idx] + exht[peaks_idx])

    data['inht'] = inht
    data['exht'] = inht
    data['inht_exht_ratio'] = inht_exht_ratio
    data['inht_cycle_ratio'] = inht_cycle_ratio

    data['inht_exht_ratio_10sec'] = pd.Series(data['inht_exht_ratio'].values).rolling(10*fs, center=True, min_periods=1).apply(lambda x: np.nanmean(x), raw=True).values
    data['inht_cycle_ratio_10sec'] = pd.Series(data['inht_cycle_ratio'].values).rolling(10*fs, center=True,min_periods=1).apply(lambda x: np.nanmean(x), raw=True).values

    # Tidal Volume per Breath features:
    if verbose:
        print('TV per breath')

    TVpB = np.zeros(data.shape[0], )
    TVpB[peaks_idx[1:]] = np.array([movavg_0_5s[peak_idx] - movavg_0_5s[trough_idx] for peak_idx, trough_idx in zip(peaks_idx[1:], troughs_idx)])

    # peaks_loc = data[data.peaks==1].index[1:]
    # troughs_loc = data[data.troughs==1].index
    # data['TVpB'] = np.nan
    # TVpB = np.array([data.movavg_0_5s[peak_loc] - data.movavg_0_5s[trough_loc] for peak_loc, trough_loc in zip(peaks_loc, troughs_loc)])
    # data.loc[peaks_loc, 'TVpB'] = TVpB

    TVpB_regularity = np.zeros(data.shape[0], )
    TVpB = TVpB[peaks_idx]
    TVpB_regularity[peaks_idx[:-1]] = 1 - np.array([min(TVpB[i], TVpB[i+1])/max(TVpB[i], TVpB[i+1]) for i in range(len(TVpB) - 1)])
    data['TVpB_regularity'] = TVpB_regularity

    # data['TVpB_regularity'] = np.nan
    # data.loc[peaks_loc[:-1], 'TVpB_regularity'] = 1 - np.array([min(TVpB[i],TVpB[i+1])/max(TVpB[i],TVpB[i+1]) for i in range(len(TVpB)-1)])
    data['TVpB_regularity_10sec'] = pd.Series(TVpB_regularity).rolling(10 * fs, center=True, min_periods=1).apply(lambda x: np.nanmean(x), raw=True).values

    if verbose:
        print('actigraphy features')
    data = airgo_actigraphy_features(data, fs=fs)

    if verbose:
        print('instability index')
    data = compute_breathing_instability_index_routine(data, fs=fs)

    # data.drop('ventilation0',axis=1)
    return data

def airgo_actigraphy_features(data, fs=10):

    # accelerometer features:
    g = 9.81
    if any([data.accx.dropna().shape[0]==0, data.accy.dropna().shape[0]==0, data.accz.dropna().shape[0]==0]):
        print('No valid acceleration data. Do not compute airgo actigraphy features.')
        
        return data

    for acc in ['accx','accy', 'accz']:
        data[acc] /=g
        data[acc+'_1sec'] = data[acc].reset_index()[acc].rolling(fs, center=True, min_periods=1).mean().values
        data[acc+'_var_1sec'] = data[acc].reset_index()[acc].rolling(fs, center=True, min_periods=1).var().values
        data[acc+'_var_10sec'] = data[acc].reset_index()[acc].rolling(10*fs, center=True, min_periods=1).var().values

    data['acc_ai_1sec'] = np.sqrt(np.maximum([0],np.mean([data['accx_var_1sec'], data['accy_var_1sec'], data['accz_var_1sec']], axis=0)))
    data['acc_ai_10sec'] = np.sqrt(np.maximum([0],np.mean([data['accx_var_10sec'], data['accy_var_10sec'], data['accz_var_10sec']], axis=0)))
    data['acc_enmo'] = np.maximum([0],np.sqrt(data.accx**2+data.accy**2+data.accz**2)-0.98)
    data['acc_enmo_1sec'] = data['acc_enmo'].reset_index()['acc_enmo'].rolling(fs, center=True, min_periods=1).mean().values
    data['acc_enmo_10sec'] = data['acc_enmo'].reset_index()['acc_enmo'].rolling(10*fs, center=True, min_periods=1).mean().values
    # get position cluster (assumption: device is worn on the chest; 4 clusters)
    # data = acceleration_position(data)
    data = airgo_acc_positioning_rulebased(data, fs=fs, g=g)
    # for acc in ['accx', 'accy', 'accz']:
    #     data.drop(acc+'_var_1sec', axis=1, inplace=True)
    #     data.drop(acc+'_var_10sec', axis=1, inplace=True)
    return data



def sample_entropy(x, order=2, metric='chebyshev'):
    """Sample Entropy.

    Parameters
    ----------
    x : list or np.array
        One-dimensional time series of shape (n_times).
    order : int
        Embedding dimension. Default is 2.
    metric : str
        Name of the distance metric function used with
        :py:class:`sklearn.neighbors.KDTree`. Default is
        `Chebyshev <https://en.wikipedia.org/wiki/Chebyshev_distance>`_.

    Returns
    -------
    se : float
        Sample Entropy.
    """
    x = np.asarray(x, dtype=np.float64)
    if metric == 'chebyshev' and x.size < 5000:
        return _numba_sampen(x, mm=order, r=0.2)
    else:
        phi = _app_samp_entropy(x, order=order, metric=metric,
                                approximate=False)
        return -np.log(np.divide(phi[1], phi[0]))



@jit('f8(f8[:], i4, f8)', nopython=True)
def _numba_sampen(x, mm=2, r=0.2):
    """
    Fast evaluation of the sample entropy using Numba.
    """
    n = x.size
    n1 = n - 1
    mm += 1
    mm_dbld = 2 * mm

    # Define threshold
    r *= x.std()

    # initialize the lists
    run = [0] * n
    run1 = run[:]
    r1 = [0] * (n * mm_dbld)
    a = [0] * mm
    b = a[:]
    p = a[:]

    for i in range(n1):
        nj = n1 - i

        for jj in range(nj):
            j = jj + i + 1
            if abs(x[j] - x[i]) < r:
                run[jj] = run1[jj] + 1
                m1 = mm if mm < run[jj] else run[jj]
                for m in range(m1):
                    a[m] += 1
                    if j < n1:
                        b[m] += 1
            else:
                run[jj] = 0
        for j in range(mm_dbld):
            run1[j] = run[j]
            r1[i + n * j] = run[j]
        if nj > mm_dbld - 1:
            for j in range(mm_dbld, nj):
                run1[j] = run[j]

    m = mm - 1

    while m > 0:
        b[m] = b[m - 1]
        m -= 1

    b[0] = n * n1 / 2
    a = np.array([float(aa) for aa in a])
    b = np.array([float(bb) for bb in b])
    p = np.true_divide(a, b)
    return -log(p[-1])


def katz_fd(x):
    """Katz Fractal Dimension.

    Parameters
    ----------
    x : list or np.array
        One dimensional time series.

    Returns
    -------
    kfd : float
        Katz fractal dimension.
    """
    x = np.array(x)
    dists = np.abs(np.ediff1d(x))
    ll = dists.sum()
    ln = np.log10(np.divide(ll, dists.mean()))
    aux_d = x - x[0]
    d = np.max(np.abs(aux_d[1:]))
    return np.divide(ln, np.add(ln, np.log10(np.divide(d, ll))))



if __name__=='__main__':
    main()
