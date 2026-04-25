import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import sys
import h5py
# from biosppy.signals import ecg
sys.path.append('/home/wolfgang/repos/sleep_research_io')
from sleep_research_functions import load_sleep_data, write_to_hdf5_file, get_metadata
import pickle
import matlab.engine
import matlab
import scipy.signal
import datetime
import matplotlib.dates as mdates
import scipy
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
import mne
from mne.filter import filter_data, notch_filter, resample


def ecg_peak_finding_physionet(signal):

    eng = matlab.engine.start_matlab()  # matlab code is used for HRV and CPC computation.
    signal_matlab = matlab.double(list(signal))
    nn, sqi = eng.ECG_peak_finding_sqi(signal_matlab, fs, nargout=2)
    nn = np.array(nn)
    sqi = np.array(sqi)

    return nn, sqi


def ecg_peak_finding_routine(path_ecg_data, source=None):


    fs = 240  # by default, after resampling
    data = load_ecg_data(path_ecg_data)

    leads = [x for x in data.keys() if '_startdatetime' not in x]
    assert leads[0] == 'I'
    ecg_lead = leads[0]

    # create dataframe with ecg and datetime:
    t = data[f'{ecg_lead}_startdatetime']
    start_datetime = pd.to_datetime(f'{t[0]}-{t[1]}-{t[2]} {t[3]}:{t[4]}:{t[5]}.{t[6]}', infer_datetime_format=True)
    signal_ecg_lead = pd.DataFrame(data[ecg_lead], columns=['signal'])
    signal_ecg_lead = index_to_datetime_sleepdata_ecg(signal_ecg_lead, start_datetime, fs)

    # Amplitude scaling:
    if source is None:
        print(
            "No source info for ecg_hrv_cpc_routine given. Might be needed for unit conversion (e.g. source='bedmaster'.)")

    if source == 'bedmaster':
        if signal_ecg_lead.signal[
            (signal_ecg_lead.signal > signal_ecg_lead.signal.quantile(0.02)) & (
                    signal_ecg_lead.signal < signal_ecg_lead.signal.quantile(0.98))].std() > 2:
            signal_ecg_lead['signal'] = signal_ecg_lead['signal'] * 0.00243
        else:
            print(
                'Based on automatic standard deviation check, this signal seems to be in mV already. No conversion performed.')

    if 0:
        # only select subset of data for debug/developing:
        print('Attention, only subset of data selected. DEBUG/ DEVELOP MODE.')  # TMP TODO
        signal_ecg_lead = signal_ecg_lead.iloc[fs * 60 * 150:fs * 60 * 200, :]
        # signal_ecg_lead = signal_ecg_lead.loc['2019-07-30 09:45' : '2019-07-30 13:45',:]

    signal = signal_ecg_lead.values.flatten()
    # pd.Series(signal).to_csv('030_signal.csv')

    ##### ECG peak detection #####

    # using physionet Clifford et al toolbox:

    if 0:
        print(signal.shape)
        print(np.sum(~np.isfinite(signal)))
        plt.figure(figsize=(14, 10))
        plt.plot(signal)
        plt.savefig('debug.jpg', dppi=400)
        plt.show()
        plt.close()

    nn, sqi = ecg_peak_finding_physionet(signal)

    if np.all(pd.isna(nn)):
        print('nn is nan, i.e. no peaks were found in Matlab Toolbox. Bad siqnal quality.')
        nn = None

    # add R peaks and SQI to 240Hz ECG data:
    signal_ecg_lead['r_peak'] = np.int16(0)
    signal_ecg_lead.loc[signal_ecg_lead.iloc[np.round(nn[:,0]*fs).astype(int)-1].index, 'r_peak'] = 1
    signal_ecg_lead['sqi'] = np.nan
    signal_ecg_lead.loc[signal_ecg_lead.iloc[np.round(sqi[:, 0] * fs).astype(int) - 1].index, 'sqi'] = sqi[:, 1]
    signal_ecg_lead['sqi'] = signal_ecg_lead['sqi'].astype(np.float32)
    signal_ecg_lead['sqi'].fillna(method='ffill', limit = 2*fs, inplace=True)

    return signal_ecg_lead



def ecg_hrv_cpc_routine(path_ecg_data, path_vitals_data, fs_ecg=None, fs_hrv = 10, source=None):
    '''
    main function that carries out whole ecg hrv and cpc analysis. uses matlab toolboxes dor both, 
    MATLAB and python extension need to be installed.
    inputs: 
    path_ecg_data: ECG data with constant sampling frequency (assumed to be 240Hz here).
    path_vitals_data: this is the path to an .h5 file that contains the respiration data (here: 10Hz airgo data)
    outputs:
    hrv_10hz: HRV output, DataFrame.
    signal_ecg_lead: ECG signal used with detected peaks (binary sequence)
    cpc_df: Cardiopulmonary Coupling spectrogram, DataFrame

    '''
    eng = matlab.engine.start_matlab() # matlab code is used for HRV and CPC computation.

    # Amplitude scaling:
    if source is None:
        print(
            "No source info for ecg_hrv_cpc_routine given. Might be needed for unit conversion (e.g. source='bedmaster'.)")

    if source == 'bedmaster':

        data = load_ecg_data(path_ecg_data)
        leads = [x for x in data.keys() if '_startdatetime' not in x]
        assert leads[0] == 'I'
        ecg_lead = leads[0]

        fs_ecg = 240  # by default, after resampling

        # create dataframe with ecg and datetime:
        t = data[f'{ecg_lead}_startdatetime']
        start_datetime = pd.to_datetime(f'{t[0]}-{t[1]}-{t[2]} {t[3]}:{t[4]}:{t[5]}.{t[6]}', infer_datetime_format=True)
        signal_ecg_lead = pd.DataFrame(data[ecg_lead], columns=['signal'])
        signal_ecg_lead = index_to_datetime_sleepdata_ecg(signal_ecg_lead, start_datetime, fs_ecg)

        if signal_ecg_lead.signal[
            (signal_ecg_lead.signal > signal_ecg_lead.signal.quantile(0.02)) & (signal_ecg_lead.signal < signal_ecg_lead.signal.quantile(0.98))].std() > 2:
            signal_ecg_lead['signal'] = signal_ecg_lead['signal'] * 0.00243
        else:
            print(
                'Based on automatic standard deviation check, this signal seems to be in mV already. No conversion performed.')

    elif source == 'psg_sleeplab_edf':

        do_plots = 1
        notch_freq = 60
        bandpass_freq_ecg = [0, 48]
        n_jobs = 4

        edf = mne.io.read_raw_edf(path_ecg_data, stim_channel=None, preload=False, verbose=False);
        edf_channels = edf.info['ch_names']

        fs_ecg = int(edf.info['sfreq'])
        signal = edf.get_data(
            picks='ECG-LA').flatten()  # v1 and v2 signals are (somtimes? always?) empty/only noise.
        signal = signal * 1e3  # volt to millivolt for peak detection algo.

        # plt.figure()
        # plt.plot(signal)
        # plt.show()
        # import pdb; pdb.set_trace()


        signal = notch_filter(signal, fs_ecg, notch_freq, n_jobs=n_jobs, verbose='ERROR')
        signal = filter_data(signal, fs_ecg, bandpass_freq_ecg[0], bandpass_freq_ecg[1], n_jobs=n_jobs,
                                 verbose='ERROR')
        new_fs = 200
        signal = resample(signal, up=new_fs, down=fs_ecg, axis=0)
        fs_ecg = new_fs

        # plt.figure()
        # plt.plot(signal)
        # plt.show()
        # import pdb; pdb.set_trace()


        # edf contains correct timestamp but displays 'UTC' (standard edf). No conversion necessary, only remove UTC timezone.
        start_datetime = pd.Timestamp(edf.info['meas_date']).tz_localize(None)
        signal_ecg_lead = pd.DataFrame(signal, columns=['signal'])
        signal_ecg_lead = index_to_datetime_sleepdata_ecg(signal_ecg_lead, start_datetime, fs_ecg)


    if 0:
        # only select subset of data for debug/developing:
        print('Attention, only subset of data selected. DEBUG/ DEVELOP MODE.') # TMP TODO
        signal_ecg_lead = signal_ecg_lead.iloc[fs_ecg*60*150:fs_ecg*60*200,:]
        # signal_ecg_lead = signal_ecg_lead.loc['2019-07-30 09:45' : '2019-07-30 13:45',:]

    signal = signal_ecg_lead.values.flatten()

    
    ##### ECG peak detection and HRV analysis #####
    
    # using physionet Clifford et al toolbox:
    # names of output. Note: output is always the same, here only name of dataframe columns gets set:
    hrv_columns = ['hrv_t_start','hrv_t_end','hrv_NNmean','hrv_NNmedian','hrv_NNmode','hrv_NNvariance','hrv_NNskew','hrv_NNkurt',
     'hrv_iqr','hrv_SDNN','hrv_RMSSD','hrv_pnn50','hrv_btsdet','hrv_avgsqi','hrv_tdflag','hrv_ulf','hrv_vlf','hrv_lf','hrv_hf',
     'hrv_lfhf','hrv_ttlpwr','hrv_fdflag','hrv_ac','hrv_dc','hrv_SD1','hrv_SD2','hrv_SD1SD2','hrv_SampEn','hrv_ApEn']

    # print(signal.shape)
    # print(np.sum(~np.isfinite(signal)))
    # plt.figure(figsize=(14,10))
    # plt.plot(signal)
    # plt.savefig('debug.jpg', dppi=400)
    # plt.close()

    nn, hrv, sqi = hrv_physionet_toolbox_computation(eng, signal, fs_ecg, hrv_columns)

    if np.all(pd.isna(nn)):
        return None, None, None

    # add R peaks and SQI to 240Hz ECG data:
    signal_ecg_lead['r_peak'] = np.int16(0)
    signal_ecg_lead.loc[signal_ecg_lead.iloc[np.round(nn[:,0]*fs_ecg).astype(int)-1].index, 'r_peak'] = 1
    signal_ecg_lead['sqi'] = np.nan
    signal_ecg_lead.loc[signal_ecg_lead.iloc[np.round(sqi[:, 0] * fs_ecg).astype(int) - 1].index, 'sqi'] = sqi[:, 1]
    signal_ecg_lead['sqi'] = signal_ecg_lead['sqi'].astype(np.float32)
    signal_ecg_lead['sqi'].fillna(method='ffill', limit = 2*fs_ecg, inplace=True)


    # create a 10Hz HRV df:
    hrv_10hz = signal_ecg_lead[['signal']].resample(f"{1/fs_hrv}S").mean().copy()
    hrv_10hz['hrv_window_center'] = 0
    window_center = ((hrv.hrv_t_start + hrv.hrv_t_end)/2*fs_hrv).astype(int).values
    hrv_10hz.loc[hrv_10hz.index[window_center], 'hrv_window_center'] = 1


    for col in hrv_columns:
        hrv_10hz[col] = np.nan
    hrv_10hz.loc[hrv_10hz.hrv_window_center==1, hrv_columns] = hrv.values
    
    indices_tnn_hrv = np.round((nn[:,0]*fs_hrv).astype(int))
    hrv_10hz['r_peak'] = 0
    hrv_10hz['nn'] = np.nan
    hrv_10hz.loc[hrv_10hz.iloc[indices_tnn_hrv].index, 'r_peak'] = 1
    hrv_10hz.loc[hrv_10hz.r_peak==1, 'nn'] = nn[:,1]
    hrv_10hz['nn'] = hrv_10hz['nn'].interpolate(method='linear', limit=fs_hrv*3, limit_direction='both')

    to_interpolate = hrv_columns.copy()
    to_interpolate.remove('hrv_t_start')
    to_interpolate.remove('hrv_t_end')

    for col in hrv_10hz:
        if type(hrv_10hz[col].iloc[0]) == np.float64:
            hrv_10hz[col] = hrv_10hz[col].astype('float32')
    hrv_10hz['r_peak'] = hrv_10hz['r_peak'].astype(np.int16)
    hrv_10hz['hrv_window_center'] = hrv_10hz['hrv_window_center'].astype(np.int16)

#     ##### load 10Hz vitals - only respiration data #####
    signals_to_load = ['movavg_0_5s']
    signals_contained_vitals, hdr_vitals = get_metadata(path_vitals_data)

    if 'movavg_0_5s' not in signals_contained_vitals:
        print('No AirGo signal available. No CPC performed.')
        hrv_10hz[to_interpolate] = hrv_10hz[to_interpolate].interpolate(method='linear', limit=fs_hrv * 15)
        return hrv_10hz, signal_ecg_lead, None

    data_vitals, hdr = load_sleep_data(path_vitals_data, load_all_signals=0, signals_to_load=signals_to_load, idx_to_datetime=1)
    
    
#     ##### CPC #####
    fs_cpc = 10
    
    # get respiration+nn df with fs_cpc sampling frequ.:
    breathing_start = data_vitals.movavg_0_5s.dropna().index[0]
    breathing_end = data_vitals.movavg_0_5s.dropna().index[-1]
    nn_start = hrv_10hz.nn.dropna().index[0]
    nn_end = hrv_10hz.nn.dropna().index[-1]
    cpc_start = max(breathing_start, nn_start)
    cpc_end = min(breathing_end, nn_end)
    breathing = data_vitals.loc[cpc_start : cpc_end, ['movavg_0_5s']]
    nn = hrv_10hz.loc[cpc_start : cpc_end, ['nn']]
    resp_nn = breathing.join(nn, how='outer')

    if resp_nn.shape[0] == 0:
        print('No overlap in ECG and respiration data. No CPC performend.')
        cpc_df = None
        cpc_lfhf = None
    else:
        resp_nn = resp_nn.resample(f'{1/fs_cpc}S').mean()
        resp_nn.rename({'movavg_0_5s':'resp'}, axis=1, inplace=True)
        resp_nn = resp_nn.interpolate(method='linear', limit=fs_cpc*5) # done.

        # signals get normalized (mainly so that we get equal variance in the the different signals) so their power in spectra are comparable.
        resp_nn.resp = clip_z_normalize(resp_nn.resp)
        resp_nn.nn = clip_z_normalize(resp_nn.nn)

        [cpc, phi, crossspectrum, coherence, spec_resp, spec_nn , t, f] = CPC_computation(eng, resp_nn.resp.values.copy(), resp_nn.nn.values.copy(),
                                                                                      fs_cpc, detrend = True, windowsize = 60*8.5, increment = 13)

        # compute cpc dataframe (columnnames frequency, index datetime) with LF, HF, HF/LF coupling features:
        cpc_df, cpc_lfhf = CPC_df_features(cpc, resp_nn, t, f, fs_cpc) # maybe rename cpc_df to cpc, i.e. overwrite

        to_interpolate += ['cpc_lfc', 'cpc_hfc', 'cpc_hfc_lfc_ratio']
    
        cpc_lfhf['cpc_cntr_window'] = np.int16(1)
        hrv_10hz = hrv_10hz.join(cpc_lfhf, how='outer').resample(f'{1/fs_hrv}S').mean()
        hrv_10hz.loc[pd.isna(hrv_10hz.cpc_cntr_window), 'cpc_cntr_window'] = 0
        hrv_10hz['cpc_cntr_window'] = hrv_10hz['cpc_cntr_window'].astype(np.int16)
        hrv_10hz['cpc_cntr_window'] = hrv_10hz['cpc_cntr_window'].astype(np.int16)

    for col in hrv_10hz:
        if type(hrv_10hz[col].iloc[0]) == np.float64:
            hrv_10hz[col] = hrv_10hz[col].astype('float32')
    hrv_10hz[to_interpolate] = hrv_10hz[to_interpolate].interpolate(method='linear', limit=fs_hrv*15)

    return hrv_10hz, signal_ecg_lead, cpc_df
    

def cpc_routine(data_vitals, fs_hrv = 10):

    eng = matlab.engine.start_matlab() # matlab code is used for HRV and CPC computation.

    #     ##### CPC #####
    fs_cpc = 10

    # get respiration+nn df with fs_cpc sampling frequ.:
    breathing_start = data_vitals.movavg_0_5s.dropna().index[0]
    breathing_end = data_vitals.movavg_0_5s.dropna().index[-1]
    nn_start = data_vitals.hrv_nn.dropna().index[0]
    nn_end = data_vitals.hrv_nn.dropna().index[-1]
    cpc_start = max(breathing_start, nn_start)
    cpc_end = min(breathing_end, nn_end)
    breathing = data_vitals.loc[cpc_start: cpc_end, ['movavg_0_5s']].copy()
    hrv_nn = data_vitals.loc[cpc_start: cpc_end, ['hrv_nn']]
    resp_nn = breathing.join(hrv_nn, how='outer')

    if resp_nn.shape[0] == 0:
        print('No overlap in ECG and respiration data. No CPC performend.')
        cpc_df = None
        cpc_lfhf = None
    else:
        resp_nn = resp_nn.resample(f'{1 / fs_cpc}S').mean()
        resp_nn.rename({'movavg_0_5s': 'resp'}, axis=1, inplace=True)
        resp_nn = resp_nn.interpolate(method='linear', limit=fs_cpc * 5)  # done.

        # signals get normalized (mainly so that we get equal variance in the the different signals) so their power in spectra are comparable.
        resp_nn.resp = clip_z_normalize(resp_nn.resp)
        resp_nn.hrv_nn = clip_z_normalize(resp_nn.hrv_nn)

        [cpc, phi, crossspectrum, coherence, spec_resp, spec_nn, t, f] = CPC_computation(eng,
                                                                                         resp_nn.resp.values.copy(),
                                                                                         resp_nn.hrv_nn.values.copy(),
                                                                                         fs_cpc, detrend=True,
                                                                                         windowsize=60 * 8.5,
                                                                                         increment=13)

        # compute cpc dataframe (columnnames frequency, index datetime) with LF, HF, HF/LF coupling features:
        cpc_df, cpc_lfhf = CPC_df_features(cpc, resp_nn, t, f, fs_cpc)  # maybe rename cpc_df to cpc, i.e. overwrite


        to_interpolate = ['cpc_lfc', 'cpc_hfc', 'cpc_hfc_lfc_ratio']
        cpc_lfhf['cpc_cntr_window'] = np.int16(1)
        for col_tmp in cpc_lfhf.columns:
            if col_tmp in data_vitals.columns:
                data_vitals.drop(col_tmp, axis=1, inplace=True)
        data_vitals = data_vitals.join(cpc_lfhf, how='outer').resample(f'{1 / fs_hrv}S').mean()
        data_vitals.loc[pd.isna(data_vitals.cpc_cntr_window), 'cpc_cntr_window'] = 0
        data_vitals['cpc_cntr_window'] = data_vitals['cpc_cntr_window'].astype(np.int16)
        data_vitals['cpc_cntr_window'] = data_vitals['cpc_cntr_window'].astype(np.int16)

    for col in data_vitals:
        if type(data_vitals[col].iloc[0]) == np.float64:
            data_vitals[col] = data_vitals[col].astype('float32')
    data_vitals[to_interpolate] = data_vitals[to_interpolate].interpolate(method='linear', limit=fs_hrv * 15)

    return data_vitals, cpc_df


# Function to remove artifacts from RR peaks
def adarri_artifact_removal(
    rpeaks: np.ndarray, ecg_lead: np.ndarray
) -> np.ndarray:
    adarri = np.log1p(np.abs(np.diff(np.diff(rpeaks))))
    artifact_pos = np.where(adarri >= 5)[0] + 2
    rpeak_q10, rpeak_q90 = np.percentile(ecg_lead[rpeaks], (10, 90))
    artifact_pos = (
        artifact_pos.tolist()
        + np.where(
            (ecg_lead[rpeaks] < rpeak_q10 - 300)
            | (ecg_lead[rpeaks] > rpeak_q90 + 300)
        )[0].tolist()
    )
    artifact_pos = np.sort(np.unique(artifact_pos))
    rpeaks_noart = rpeaks
    if len(artifact_pos) != 0:
        rpeaks_noart = np.delete(rpeaks, artifact_pos)

    return rpeaks_noart


def clip_z_normalize(signal):

    signal_clipped = np.clip(signal.dropna(), np.percentile(signal.dropna(),1), np.percentile(signal.dropna(),99))
    mean = np.mean(signal_clipped.astype(np.float32))
    std = np.std(signal_clipped.astype(np.float32))
    signal = (signal - mean)/std

    return signal


def cpc_and_signals_plot(cpc_df, hfc_lfc_ratio=None, resp=None, nn=None):
    
    num_subplots = 1
    if resp is not None: num_subplots+=1
    if nn is not None: num_subplots+=1
    if hfc_lfc_ratio is not None: num_subplots+=1

    loc_cpc = cpc_df.index
    f = np.array(cpc_df.columns).astype(float) # list(cpc_df.columns)
    loc_cpc_datenum = mdates.date2num(loc_cpc)
    fig, ax = plt.subplots(num_subplots, 1, figsize=(12,8), sharex=True)
    i = 0
    legend = []
    lines = []
    
    if resp is not None:
        l1, = ax[i].plot(resp)
        ax[i].set_ylim([np.nanquantile(resp, 0.005), np.nanquantile(resp, 0.995)])
        ax[i].set_ylabel('Amplitude (a.u.)')
        legend += ['Respiration']
        lines += [l1]
        i += 1
    if nn is not None:
        l2, = ax[i].plot(nn,'r')
        ax[i].set_ylim([np.nanquantile(nn, 0.005), np.nanquantile(nn, 0.995)])
        ax[i].set_ylabel('Duration (s)')
        legend += ['NN-Interval']
        lines += [l2]
        i += 1
    if hfc_lfc_ratio is not None:
        l3, = ax[i].plot(hfc_lfc_ratio, c='black', zorder=3)
        zero_line_x = [hfc_lfc_ratio.index[0], hfc_lfc_ratio.index[-1]]
        ax[i].plot(zero_line_x, [0, 0], ls = (0, (5, 7)), color='firebrick', alpha=0.5, zorder=2)
        ax[i].set_ylabel('Log. Ratio');  
        legend += ['HFC/LFC Log Ratio']
        lines += [l3]
        i += 1; 

    spectrum_plot_dt(cpc_df.transpose(), ax[i], loc_cpc_datenum, f, db=True, vmin=0.6, vmax=0.99); i += 1; 
    
    fig.legend(lines, legend, ncol=i-1, loc = 'upper center', bbox_to_anchor=[0.5, 0.93])

    plt.suptitle('Cardiopulmonary Coupling Analysis')

    return fig
        

def spectrum_plot_dt(var, ax, t, f, db=True, vmin=0.05, vmax=0.99, colormap="jet"):
    '''datetime version'''
    if db:
        var = 20*np.log10(var+1e-5)
    vmin = np.nanquantile(var, vmin)
    vmax = np.nanquantile(var, vmax)
    im = ax.imshow(var, origin = 'lower', aspect = 'auto' , cmap = colormap, interpolation="none", vmin=vmin, vmax=vmax, extent=(t[0], t[-1], f[0], f[-1])) # ,vmin=q01, vmax=q09
#     fig.colorbar(im, ax=ax)
    ax.xaxis_date()
    date_format = mdates.DateFormatter('%H:%M:%S')
    ax.xaxis.set_major_formatter(date_format)

    ax.set_yticks([0.01, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9])
    ax.set_ylabel('Hz')
    ax.set_ylim([0, 0.7])

def spectrum_plot(var, ax, t, f, db=True, vmin=0.05, vmax=0.99, colormap="jet"):
    '''not datetime version'''
    if db:
        var = 20*np.log10(var+1e-5)
    vmin = np.nanquantile(var, vmin)
    vmax = np.nanquantile(var, vmax)
    im = ax.imshow(var, origin = 'lower', aspect = 'auto' , cmap = colormap, interpolation="hanning", vmin=vmin, vmax=vmax, extent=(t[0], t[-1], f[0], f[-1])) # ,vmin=q01, vmax=q09
#     fig.colorbar(im, ax=ax)
    ax.set_yticks([0.01, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9])
    ax.set_ylabel('Hz')
    ax.set_ylim([0, 0.7])
    
       
    
def load_ecg_data(filepath, load_all_signals=True, verbose=False):
    
    ff = h5py.File(filepath, 'r')

    if load_all_signals:
        signals_to_load = list(ff.keys())
    if verbose:
        print(f'signals to load: {signals_to_load}')

    data = {}
    for signal_to_load_tmp in signals_to_load:  
        data[signal_to_load_tmp] = ff[signal_to_load_tmp][:]

        if type(data[signal_to_load_tmp][0]) == np.float16:
            data[signal_to_load_tmp] = data[signal_to_load_tmp].astype('float32') 
            
    return data


def index_to_datetime_sleepdata_ecg(data, start_datetime, fs):
    '''
    for starting datetime and samplingrate create datetime-index for dataframe.
    '''
    data.index = pd.date_range(start_datetime, periods=data.shape[0], freq=str(np.round(1/fs*1e9))+'N')
    return data


def hrv_physionet_toolbox_computation(eng, signal, fs, hrv_columns):

    # pd.Series(signal).to_csv('signal_ecg.csv', index=False)
    signal_matlab = matlab.double(list(signal))
    nn, hrv, sqi = eng.HRV_Analysis_ICUSleepProject2(signal_matlab, fs, nargout=3)

    nn = np.array(nn)
    hrv = np.array(hrv)
    sqi = np.array(sqi)

    if np.all(pd.isna(nn)):
        print('nn is nan, i.e. no peaks were found in Matlab Toolbox. Bad siqnal quality.')
        return nn, hrv, sqi

    hrv = pd.DataFrame(data=hrv, columns=hrv_columns)
    
    return nn, hrv, sqi



def CPC_computation(eng, respiration_signal, nn_signal, fs, detrend = True, windowsize = 60*8.5, increment = 13, do_plots=False):
    '''
    COMPUTE CPC as described in Thomas et. al
        windowsize and increment in seconds, 13sec is 2.5% of 8.5min window
    '''

    if detrend:        
        respiration_signal[np.logical_not(pd.isna(respiration_signal))] = scipy.signal.detrend(respiration_signal[np.logical_not(pd.isna(respiration_signal))])
        nn_signal[np.logical_not(pd.isna(nn_signal))] = scipy.signal.detrend(nn_signal[np.logical_not(pd.isna(nn_signal))])

    respiration_signal = matlab.double(list(respiration_signal))
    nn_signal = matlab.double(list(nn_signal))
    
    C, phi, S12, S1, S2, t, f = eng.MultiTaperFreqDomainAnalysis_includingCPC(respiration_signal, nn_signal, windowsize, increment, fs, nargout=7)
    C = np.transpose(np.array(C))
    phi = np.transpose(np.array(phi))
    S12 = np.transpose(np.array(S12))
    S1 = np.transpose(np.array(S1)).real
    S2 = np.transpose(np.array(S2)).real # usually output is real except when there are nans, then 0-valued imaginary part needs to be removed
    t = np.array(t).flatten()
    f = np.array(f).flatten()
    CS = (np.conj(S12)*S12).real
    
    CPC = np.multiply(C, CS)

    if do_plots:
                
        num_subplots = 5
        fig, ax = plt.subplots(num_subplots, 1, figsize=(10,8), sharex=True)
        i = 0
        spectrum_plot(S1, ax[i], t, f, db=True, vmin=0.05, vmax=0.99); i += 1; 
        spectrum_plot(S2, ax[i], t, f, db=True, vmax=0.99); i += 1; 
        spectrum_plot(C, ax[i], t, f, db=False, vmin=0.05, vmax=0.99); i += 1; 
        spectrum_plot(CS, ax[i], t, f, db=True, vmax=0.99); i += 1; 
        spectrum_plot(CPC, ax[i], t, f, db=True, vmin=0.6, vmax=0.99); i += 1; 
        plt.suptitle('Resp., NN, Coherence, Cross Spectrum, CPC')
        plt.savefig('tmp_cpc_plot.svg')
        plt.savefig('tmp_cpc_plot.png', dpi=300)

    return [CPC, phi, CS, C, S1, S2, t, f]



def CPC_df_features(cpc, resp_nn, t, f, fs_cpc):
    
    idx_cpc = (t*fs_cpc).astype(int)
    loc_cpc = resp_nn.index[idx_cpc]
    cpc_df = pd.DataFrame(data=np.transpose(cpc), columns=f)
    cpc_df.index = loc_cpc

    frequency_div_idx = np.where(f>0.1)[0][0]
    frequency_hf_idx = np.where(f>0.4)[0][0]

    cpc_lfhf = pd.DataFrame()
    cpc_lfhf['cpc_lfc'] = cpc_df.iloc[:, :frequency_div_idx].sum(axis=1)
    cpc_lfhf['cpc_hfc'] = cpc_df.iloc[:, frequency_div_idx:frequency_hf_idx].sum(axis=1)
    cpc_lfhf['cpc_hfc_lfc_ratio'] = np.log(cpc_lfhf['cpc_hfc']/cpc_lfhf['cpc_lfc'])

    return cpc_df, cpc_lfhf
