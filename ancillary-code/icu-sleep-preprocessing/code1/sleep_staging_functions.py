import sys
import os
import numpy as np
import pandas as pd
import torch as th

sys.path.append('/home/wolfgang/repos/AirGoSleepPyT0-')
sys.path.append('/home/wolfgang/repos/AirGoSleepPyT0')

from segment_signal import *
from collections import Counter
from scipy import io as sio
th.cuda.empty_cache()
from utils import softmax
from braindecode.torch_ext.util import np_to_var, var_to_np

from tqdm import tqdm

from mymodel import ECGSleepNet, SleepNet_RNN
from tqdm import tqdm
import datetime
import scipy


def apply_airgo_sleep_staging_models_fold(data, fs=10, model_ids=None, input_signals=None, models_dir=None,
                                          n_gpu=1, output=0, fold_id=None, verbose=False):

    window_time = 270
    step_time = 30
    start_end_remove_window_num = 1
    n_jobs = -1
    to_remove_mean = False

    if models_dir is None:
        models_dir = './sleep_staging_models'
        if not os.path.exists(models_dir):
            models_dir = '/media/mad3/Projects/Wolfgang/AirGoSleepStaging/final_models'

    if model_ids is None:
        model_ids = ['amendsumeffort', 'activity10sec']
    if input_signals is None:
        input_signals = ['movavg_0_5s', 'acc_ai_10sec']

    lhl_data_collection = {}

    if (data.index[0].second != 0) | (data.index[0].microsecond != 0):
        # left pad data so that it starts with :00 second - allows comparisons with models with other input.
        left_pad_dt = pd.date_range(data.index[0].replace(second=0, microsecond=0), data.index[0], freq=str(1 / fs * 1000) + 'L',
                                    closed='left')
        df_left_pad = pd.DataFrame(index=left_pad_dt, columns=data.columns)
        data = pd.concat([df_left_pad, data], axis=0)

    for model_id, input_signal in list(zip(model_ids, input_signals)):
        if verbose:
            print(model_id)

        if input_signal not in data.columns:
            print(f'{input_signal} not in data. Skip sleep staging with model {model_id}.')
            continue

        if model_id == 'amendsumeffort':
            cnn_path = 'CNN_AirGoFilter_AmendSumEffort.pth'
            rnn_path = 'RNN_AirGoFilter_AmendSumEffort.pth'
            z_normalize_signal = False  # input signal is expected to be normalized (as of output of airgofeatures())

        elif model_id == 'activity10sec':
            cnn_path =  'CNN_best_model.pth'
            rnn_path = 'RNN_abest_model.pth'
            z_normalize_signal = False

        cnn_path = os.path.join(models_dir, cnn_path)
        cnn_model = th.load(cnn_path);
        cnn_model.eval();

        rnn_path = os.path.join(models_dir, rnn_path)
        lstm_model = th.load(rnn_path);
        lstm_model.eval();

        signal = data[input_signal].values
        signal = signal[np.newaxis, :]

        amplitude_thres = None
        amplitude_thres_low = None
        std_thres1=0
        std_thres2=0

        segs, seg_mask, seg_start_pos = segment_signal_only(signal, window_time, step_time, fs, 
                            start_end_remove_window_num=start_end_remove_window_num, 
                            amplitude_thres=amplitude_thres, amplitude_thres_low=amplitude_thres_low,
                        n_jobs=n_jobs, to_remove_mean=to_remove_mean, 
                        z_normalize_signal=z_normalize_signal)

        # REMOVE INF and NAN if still here...
        # segs.shape
        isgood = np.isfinite(segs).all(axis=2).flatten()
        segs = segs[isgood,:,:]
        seg_start_pos = seg_start_pos[isgood]

        if segs.shape[0] > 0:

            X = th.tensor(segs).float()

            yp_lstm, h_lstm, yp_cnn, h_cnn = cnn_and_lstm_predict(X, cnn_model, lstm_model, n_gpu=n_gpu)
            yp_lstm = np.argmax(yp_lstm, axis=1) + 1

            data[f'stage_pred_{model_id}'] = np.nan
            stage_iloc = seg_start_pos + int((window_time / 2 - step_time / 2) * fs)
            stage_loc = data.iloc[stage_iloc].index
            data.loc[stage_loc, f'stage_pred_{model_id}'] = yp_lstm
            data[f'stage_pred_{model_id}'].fillna(method='pad',
                                                  limit=30*fs-1, inplace=True)

            th.cuda.empty_cache()

        else:
            if verbose:
                print(f"""No valid data available, no sleep staging done 
                    for model_id: {model_id} and  input_signal {input_signal}.""")

    data['stage_pred_comb_breath_activity_1'] = data['stage_pred_amendsumeffort'].values
    if 'stage_pred_activity10sec' in data.columns:
        data.loc[data['stage_pred_activity10sec'] == 5, 'stage_pred_comb_breath_activity_1'] = 5

    return data


def apply_airgo_sleep_staging_models(data, fs=10, model_ids=None, input_signals=None, models_dir=None,
                                     n_gpu=1, output=0, do_left_pad=False, verbose=False):
    """
    Sleep Staging Function.
    data: dataframe with input signals.
    fs: sampling frequency
    models_id: Choose the models that should be applied.
    input_signals: Choose input signals that shall be used.
    models_dir: path to directory containing the models.
    n_gpu: Number of GPUs to use. 0 means CPU.
    output: 0   for final prediction only.
            -1  for last hidden layer (both CNN and LSTM), softmax and final prediction.
    do_left_pad: Left pad the input data to nearest 'full minute', i.e. second == 0.
       This leads to epochs starting at seconds 00 and 30. Beneficial in cases where different input signals have
       different starting times. In this way, the overlapping time will all have equal epoch starting numbers.
       (e.g. True in ICU Sleep, but False in Sleeplab PSG).
    """

    window_time = 270
    step_time = 30
    start_end_remove_window_num = 1
    n_jobs = -1
    to_remove_mean = False

    if models_dir is None:
        models_dir = './sleep_staging_models'
        if not os.path.exists(models_dir):
            models_dir = '/media/mad3/Projects/Wolfgang/AirGoSleepStaging/final_models'

    if model_ids is None:
        model_ids = ['amendsumeffort', 'activity10sec']
    if input_signals is None:
        input_signals = ['movavg_0_5s', 'acc_ai_10sec']

    lhl_data_collection = {}

    if do_left_pad & ((data.index[0].second != 0) | (data.index[0].microsecond != 0)):
        # left pad data so that it starts with :00 second - allows comparisons with models with other input.
        left_pad_dt = pd.date_range(data.index[0].replace(second=0, microsecond=0), data.index[0], freq=str(1 / fs * 1000) + 'L',
                                    closed='left')
        df_left_pad = pd.DataFrame(index=left_pad_dt, columns=data.columns)
        data = pd.concat([df_left_pad, data], axis=0)

    for model_id, input_signal in list(zip(model_ids, input_signals)):
        if verbose:
            print(model_id)

        if input_signal not in data.columns:
            print(f'{input_signal} not in data. Skip sleep staging with model {model_id}.')
            continue

        if model_id == 'amendsumeffort':
            cnn_path = 'CNN_AirGoFilter_AmendSumEffort.pth'
            rnn_path = 'RNN_AirGoFilter_AmendSumEffort.pth'
            z_normalize_signal = False  # input signal is expected to be normalized (as of output of airgofeatures())

        elif model_id == 'activity10sec':
            cnn_path =  'CNN_ActivityIndex10sec.pth'
            rnn_path = 'RNN_ActivityIndex10sec.pth'
            z_normalize_signal = False

        cnn_path = os.path.join(models_dir, cnn_path)
        cnn_model = th.load(cnn_path);
        cnn_model.eval();

        rnn_path = os.path.join(models_dir, rnn_path)
        lstm_model = th.load(rnn_path);
        lstm_model.eval();

        signal = data[input_signal].values
        signal = signal[np.newaxis, :]

        amplitude_thres = None
        amplitude_thres_low = None
        std_thres1=0
        std_thres2=0

        segs, seg_mask, seg_start_pos = segment_signal_only(signal, window_time, step_time, fs, 
                            start_end_remove_window_num=start_end_remove_window_num, 
                            amplitude_thres=amplitude_thres, amplitude_thres_low=amplitude_thres_low,
                        n_jobs=n_jobs, to_remove_mean=to_remove_mean, 
                        z_normalize_signal=z_normalize_signal)

        # REMOVE INF and NAN if still here...
        isgood = np.isfinite(segs).all(axis=2).flatten()
        segs = segs[isgood,:,:]
        seg_start_pos = seg_start_pos[isgood]

        if segs.shape[0] > 0:

            X = th.tensor(segs).float()

            yprob_lstm, h_lstm, yp_cnn, h_cnn = cnn_and_lstm_predict(X, cnn_model, lstm_model, n_gpu=n_gpu)
            yp_lstm = np.argmax(yprob_lstm, axis=1) + 1

            th.cuda.empty_cache()

            data[f'stage_pred_{model_id}'] = np.nan
            stage_iloc = seg_start_pos + int((window_time/2-step_time/2)*fs)
            stage_loc = data.iloc[stage_iloc].index
            data.loc[stage_loc, f'stage_pred_{model_id}'] = yp_lstm
            data[f'stage_pred_{model_id}'].fillna(method='pad',
                                                  limit=30*fs-1, inplace=True)

            # create 'last hidden layer data format':
            if output == -1:
                lhl_data_collection[f'stage_pred_{model_id}'] = yp_lstm
                lhl_data_collection[f'yp_lstm_{model_id}'] = yprob_lstm
                lhl_data_collection[f'h_lstm_{model_id}'] = h_lstm
                lhl_data_collection[f'yp_cnn_{model_id}'] = yp_cnn
                lhl_data_collection[f'h_cnn_{model_id}'] = h_cnn
                lhl_data_collection[f'iloc_{model_id}'] = stage_iloc
                lhl_data_collection[f'loc_{model_id}'] = stage_loc
        else:
            if verbose:
                print(f"""No valid data available, no sleep staging done 
                    for model_id: {model_id} and  input_signal {input_signal}.""")

    if 'stage_pred_amendsumeffort' in data.columns:
        data['stage_pred_comb_breath_activity_1'] = data['stage_pred_amendsumeffort'].values
        if 'stage_pred_activity10sec' in data.columns:
            data.loc[data['stage_pred_activity10sec'] == 5, 'stage_pred_comb_breath_activity_1'] = 5

    if output == 0:
        return data
    elif output == -1:
        return data, stage_iloc, lhl_data_collection


def cnn_and_lstm_predict(X, cnn_model, lstm_model, n_gpu=1):

    with th.no_grad():

        batch_size = 128
        H = []
        yp_cnn = []
        for i_batch in range(int(np.ceil(X.shape[0]/batch_size))):
            X_batch = X[i_batch*batch_size : (i_batch+1)*batch_size, :, :]

            cnn_output, h_cnn = cnn_model(X_batch)
            cnn_output = var_to_np(cnn_output)
            yp_cnn.append(cnn_output)
            h_cnn = var_to_np(h_cnn)
            H.append(h_cnn)

        H = np.concatenate(H, axis=0)
        H = np.expand_dims(H, axis=0)
        H = np_to_var(H)
        yp_cnn = np.expand_dims(np.concatenate(yp_cnn, axis=0), axis=0)

        if n_gpu > 0:
            H = H.cuda()

        yp, h_lstm = lstm_model(H)
        yp = var_to_np(yp)
        h_lstm = np.squeeze(var_to_np(h_lstm))
        H = var_to_np(H)
        h_cnn = np.squeeze(H)

        yp = np.squeeze(yp)
        yp = softmax(yp)

        yp_cnn = softmax(np.squeeze(yp_cnn))

    th.cuda.empty_cache()
    
    del H, cnn_model, lstm_model

    return yp, h_lstm, yp_cnn, h_cnn



def segment_signal_only(signal, window_time, step_time, fs, 
                        notch_freq=None, bandpass_freq=None, start_end_remove_window_num=1, 
                        amplitude_thres=None, amplitude_thres_low=None, n_jobs=-1, 
                        to_remove_mean=False, z_normalize_signal=True,
                        std_thres1=0.00001, std_thres2=0.00001):

    # segmentation:

    window_size = int(round(window_time*fs))
    step_size = int(round(step_time*fs))

    # prepare segmentation:
    start_ids = np.arange(0, signal.shape[1]-window_size+1, step_size)
    if start_end_remove_window_num>0:
        start_ids = start_ids[start_end_remove_window_num:-start_end_remove_window_num]
    seg_masks = [seg_mask_explanation[0]]*len(start_ids)

    ### check for high amplitude (airgo not worn) before detrending signal:
    if amplitude_thres is not None:
    ## find large amplitude in signal
        signal_segs_temp = signal[:,[np.arange(x,x+window_size) for x in start_ids]].transpose(1,0,2)  # (#window, #ch, window_size+2padding)

        amplitude_large2d = np.any(np.abs(signal_segs_temp)>amplitude_thres, axis=2)
        amplitude_large1d = np.where(np.any(amplitude_large2d, axis=1))[0]
        for i in amplitude_large1d:
            seg_masks[i] = '%s'%(seg_mask_explanation[4])

    if amplitude_thres_low is not None:
        ## find low amplitude in signal
        signal_segs_temp = signal[:,[np.arange(x,x+window_size) for x in start_ids]].transpose(1,0,2)  # (#window, #ch, window_size+2padding)
        amplitude_low2d = np.any(np.abs(signal_segs_temp)<amplitude_thres_low, axis=2)
        amplitude_low1d = np.where(np.any(amplitude_low2d, axis=1))[0]
        for i in amplitude_low1d:
            seg_masks[i] = '%s'%(seg_mask_explanation[4])

    if z_normalize_signal:
        # normalize signal:
        signal = clip_z_normalize(pd.Series(signal[0,:]))
        signal = signal[np.newaxis, :]

    # create signal segments:
    signal_segs = signal[:,[np.arange(x,x+window_size) for x in start_ids]].transpose(1,0,2)  # (#window, #ch, window_size+2padding)
    signal_segs = signal_segs.astype(np.float32)
    ## find nan in signal segs

    nan2d = np.any(np.isnan(signal_segs), axis=2)
    nan1d = np.where(np.any(nan2d, axis=1))[0]
    for i in nan1d:
        seg_masks[i] = '%s'%(seg_mask_explanation[3])

    return signal_segs, seg_masks, start_ids




def ecg_peak_finding_physionet(signal):

    import matlab.engine
    import matlab
    from HRV_and_CPC_analysis_functions import hrv_physionet_toolbox_computation

    eng = matlab.engine.start_matlab()  # matlab code is used for HRV and CPC computation.
    signal_matlab = matlab.double(list(signal))
    nn, sqi = eng.ECG_peak_finding_sqi(signal_matlab, fs, nargout=2)
    nn = np.array(nn)
    sqi = np.array(sqi)

    return nn, sqi


def apply_ecg_sleep_staging_models(data, fs=200, model_ids=None, input_signals=None, n_gpu=1,
                                   models_dir=None, output=0, do_left_pad=False, verbose=False):
    """
    Sleep Staging Function.
    data: dataframe with input signals.
    fs: sampling frequency
    models_id: Choose the models that should be applied.
    input_signals: Choose input signals that shall be used.
    models_dir: path to directory containing the models.
    n_gpu: Number of GPUs to use. 0 means CPU.
    output: 0   for final prediction only.
            -1  for last hidden layer (both CNN and LSTM), softmax and final prediction.
    do_left_pad: Left pad the input data to nearest 'full minute', i.e. second == 0.
       This leads to epochs starting at seconds 00 and 30. Beneficial in cases where different input signals have
       different starting times. In this way, the overlapping time will all have equal epoch starting numbers.
       (e.g. True in ICU Sleep, but False in Sleeplab PSG).
    """

    verbose = False
    window_time = 270
    step_time = 30
    start_end_remove_window_num = 1
    n_jobs = -1
    to_remove_mean = False
    if models_dir is None:
        models_dir = './sleep_staging_models'
        if not os.path.exists(models_dir):
            models_dir = '/media/mad3/Projects/Wolfgang/AirGoSleepStaging/final_models'

    if model_ids is None:
        model_ids = ['ecg_nn']
    if input_signals is None:
        input_signals = ['r_peak']

    if do_left_pad & ((data.index[0].second != 0) | (data.index[0].microsecond != 0)):
        # left pad data so that it starts with :00 second - allows comparisons with models with other input.
        left_pad_dt = pd.date_range(data.index[0].replace(second=0, microsecond=0), data.index[0], freq=str(1 / fs * 1000) + 'L', closed='left')
        df_left_pad = pd.DataFrame(index=left_pad_dt, columns=data.columns)
        data = pd.concat([df_left_pad, data], axis=0)

    lhl_data_collection = {}
    for model_id, input_signal in list(zip(model_ids, input_signals)):
        if verbose:
            print(model_id)

        if input_signal not in data.columns:
            print(f'{input_signal} not in data. Skip sleep staging with model {model_id}.')
            continue

        if model_id == 'ecg_nn':
            cnn_path = 'CNN_ECG_NN.pth'
            rnn_path = 'LSTM_ECG_NN.pth'
            z_normalize_signal = False 

        
        signal = data[input_signal].values
        signal = signal[np.newaxis, :]

        # Load models:
        cnn_path = os.path.join(models_dir, cnn_path)
        cnn_model = ECGSleepNet()
        cnn_model.load_state_dict(th.load(cnn_path));
        if n_gpu>0:
            cnn_model = cnn_model.cuda()
        cnn_model.eval();

        rnn_path = os.path.join(models_dir, rnn_path)
        lstm_model = SleepNet_RNN(1280, 5, 20, 2, dropout=0, bidirectional=True)
        lstm_model.load_state_dict(th.load(rnn_path))
        if n_gpu>0:
            lstm_model = lstm_model.cuda()
        lstm_model.eval()

        # Signal segmentation for CNN
        amplitude_thres = None
        amplitude_thres_low = None
        std_thres1 = 0
        std_thres2 = 0
        
        signal_segs, seg_masks, seg_start_pos = segment_signal_only(signal, window_time, step_time, fs, 
                        notch_freq=None, bandpass_freq=None, start_end_remove_window_num=1, 
                        amplitude_thres=None, amplitude_thres_low=None, n_jobs=-1,
                        to_remove_mean=False, z_normalize_signal=False,
                        std_thres1=0.00001, std_thres2=0.00001)


        # REMOVE INF and NAN if still here...
        isgood = np.isfinite(signal_segs).all(axis=2).flatten()
        signal_segs = signal_segs[isgood,:,:]
        seg_start_pos = seg_start_pos[isgood]

        if signal_segs.shape[0] > 0:
            X = signal_segs
            X = th.tensor(X).float()
            if n_gpu>0:
                X = X.cuda()

            yprob_lstm, h_lstm, yp_cnn, h_cnn = cnn_and_lstm_predict(X, cnn_model, lstm_model, n_gpu=n_gpu) # [0]
            yp_lstm = np.argmax(yprob_lstm, axis=1) + 1

            data[f'stage_pred_{model_id}'] = np.nan
            stage_iloc = seg_start_pos + int((window_time/2-step_time/2)*fs)
            stage_loc = data.iloc[stage_iloc].index
            data.loc[stage_loc, f'stage_pred_{model_id}'] = yp_lstm
            data[f'stage_pred_{model_id}'].fillna(method='pad',
                                                  limit=30*fs-1, inplace=True)

            # create 'last hidden layer data format':
            if output == -1:
                lhl_data_collection[f'stage_pred_{model_id}'] = yp_lstm
                lhl_data_collection[f'yp_lstm_{model_id}'] = yprob_lstm
                lhl_data_collection[f'h_lstm_{model_id}'] = h_lstm
                lhl_data_collection[f'yp_cnn_{model_id}'] = yp_cnn
                lhl_data_collection[f'h_cnn_{model_id}'] = h_cnn
                lhl_data_collection[f'iloc_{model_id}'] = stage_iloc
                lhl_data_collection[f'loc_{model_id}'] = stage_loc

        else:
            if verbose:
                print(f"""No valid data available, no sleep staging done 
                    for model_id: {model_id} and  input_signal {input_signal}.""")

#     if 'stage_pred_amendsumeffort' in data.columns:
#         data['stage_pred_comb_breath_activity_1'] = data['stage_pred_amendsumeffort'].values
#         if 'stage_pred_activity10sec' in data.columns:
#             data.loc[data['stage_pred_activity10sec'] == 5, 'stage_pred_comb_breath_activity_1'] = 5
    if output == 0:
        return data, stage_iloc, yp_lstm
    elif output == -1:
        return data, stage_iloc, lhl_data_collection


def ecg_peak_detection_sqi_plot():
    
    sel = data.iloc[start_idx : start_idx + duration*fs]
    fig, ax = plt.subplots(2,1,figsize=(13,8), sharex=True)
    
    ax[0].plot(sel.signal)
    ax[0].scatter(sel.loc[sel['r_peak']==1].index, sel.signal[sel['r_peak']==1], zorder=10, c='r')    
    ax[1].plot(sel.sqi)
    
    plt.title(str(study_id))
    plt.tight_layout()
#     plt.savefig(str(study_id) + '_ecg_sqi.pdf', dpi=500)
#     plt.savefig(str(study_id) + '_ecg_sqi.jpg', dpi=500)
    return fig


def compute_nn_based_on_r_peak(data, new_fs):
    
    nn_interval = np.diff(np.where(data.r_peak==1)[0])/new_fs
    nn_interval[nn_interval>2.5] = np.nan
    nn_interval = np.concatenate([[np.nan], nn_interval])
    data.loc[data.r_peak==1, 'nn_interval'] = nn_interval
    
    return data


def resample_ecg_data_for_sleep_staging(data, fs, ecg_sleepstage_model_fs=200):
    
    r_peaks_prior_resampling = data.r_peak.sum()
    data_resampled = data.resample('5ms').agg({'sqi': 'mean', 'r_peak':'max'})
    data_resampled['signal'] = 0
    signal_resampled = scipy.signal.resample_poly(data.signal.values, ecg_sleepstage_model_fs, fs)
    assert np.abs(len(signal_resampled) - len(data_resampled)) < fs, 'Sth. with resampling did not work.'
    data_resampled.loc[:data_resampled.iloc[[len(signal_resampled)-1]].index[0], 'signal'] = signal_resampled

    if r_peaks_prior_resampling != data_resampled.r_peak.sum():
        print(f'r_peaks prior resampling: {r_peaks_prior_resampling}')
        print(f'r_peaks post resampling: {data_resampled.r_peak.sum()}')
        raise ValueError('This works so far for bedmaster 240 to sleeplab 200 Hz conversion')
        
    return data_resampled


def ecg_sleep_staging_routine_icusleep(data, fs, ecg_sleepstage_model_fs=200, n_gpu=1, do_left_pad=False, output=0):
    '''
    resample, sleep staging, nn computation based on binary r peak sequence.
    '''
    
    if fs != ecg_sleepstage_model_fs:
        data = resample_ecg_data_for_sleep_staging(data, fs, ecg_sleepstage_model_fs)

    if output == 0:
        data, stage_iloc, yp = apply_ecg_sleep_staging_models(data, fs=ecg_sleepstage_model_fs, model_ids=['ecg_nn'],
                                                              input_signals=['r_peak'], n_gpu=n_gpu, output=output,
                                                              do_left_pad=do_left_pad, verbose=True)
        if not 'nn_interval' in data:
            data = compute_nn_based_on_r_peak(data, ecg_sleepstage_model_fs)
        data.loc[pd.isna(data.sqi), 'stage_pred_ecg_nn'] = np.nan
        data.stage_pred_ecg_nn.fillna(method='ffill', limit=ecg_sleepstage_model_fs*60*5, inplace=True) # pad for five minutes, bridge gaps for bad quality signal for max this time.
        return data

    if output == -1:
        data, stage_iloc, lhl_data_collection = apply_ecg_sleep_staging_models(data, fs=ecg_sleepstage_model_fs, model_ids=['ecg_nn'], input_signals=['r_peak'],
                                                                               n_gpu=n_gpu, output=output,
                                                                               do_left_pad=do_left_pad, verbose=True)
        if not 'nn_interval' in data:
            data = compute_nn_based_on_r_peak(data, ecg_sleepstage_model_fs)
        data.loc[pd.isna(data.sqi), 'stage_pred_ecg_nn'] = np.nan
        data.stage_pred_ecg_nn.fillna(method='ffill', limit=ecg_sleepstage_model_fs*60*5, inplace=True) # pad for five minutes, bridge gaps for bad quality signal for max this time.
        return data, stage_iloc, lhl_data_collection

