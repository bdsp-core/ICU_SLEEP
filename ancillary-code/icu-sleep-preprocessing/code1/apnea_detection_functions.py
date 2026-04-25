import pandas as pd
import numpy as np
import os
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import *
# from entropy import sample_entropy, katz_fd
import matplotlib.pyplot as plt
import sys
sys.path.append('/home/wolfgang/repos/sleep_research_io')
from sleep_research_functions import load_sleep_data, write_to_hdf5_file
from itertools import groupby
from scipy.integrate import simps



def apnea_model_init(model_ids_full = None, model_dir = None, verbose=False):

    if model_dir is None:
        # specify model and load it:
        model_dir = '/media/mad3/Projects/Wolfgang/AirGoSleepStaging/final_models_apnea_detection/'

    if model_ids_full is None:
        model_ids_full = ['Respiration+SpO2_robust_auto3', 'Respiration-Only_auto3']
            # 'Respiration+SpO2_robust_expert4', 'Respiration-Only_expert4', 'Respiration+SpO2_robust_auto4', 
            #                   'Respiration-Only_auto4', 


    # optimal hyperparamas, as evaluated in cross validation hyperparam search:
    models = {}
    model_ids = []

    optimal_thresholds = {
        'ro_a3': 0.55, # 0.6,
        'ro_a4': 0.65, # 0.7
        'ro_e4': 0.65, # 0.7
        'rs_a3': 0.55, # 0.55
        'rs_a4': 0.65, # 0.7
        'rs_e4': 0.65, # 0.7
        'rsr_a3': 0.5, # 0.55,
        'rsr_a4': 0.6, # 0.6
        'rsr_e4': 0.6 # 0.6
    }

    for model_id_full in model_ids_full:

        # Respiration Only
        if 'Respiration-Only' in model_id_full:
            spo2_feature = None
            model_id = model_id_full.replace('Respiration-Only','ro')

        # Respiration+SpO2 (robust)
        elif 'Respiration+SpO2_robust' in model_id_full:
            spo2_feature = 'spo2_drop_feature_30_70'
            model_id = model_id_full.replace('Respiration+SpO2_robust','rsr')

        # Respiration+SpO2
        elif 'Respiration+SpO2' in model_id_full:
            spo2_feature = 'spo2_drop_feature_0_40'
            model_id = model_id_full.replace('Respiration+SpO2','rs')

        model_id = model_id.replace('auto','a').replace('expert','e')

        pred_threshold = optimal_thresholds[model_id]

        with open(os.path.join(model_dir, f'model_{model_id_full}.p'), 'rb') as pickle_file:
            model = pickle.load(pickle_file)

        # model predictors:
        predictor_names = pd.read_csv(os.path.join(model_dir, 'features_selected.csv'))
        predictor_names = list(predictor_names.predictor_name)

        if spo2_feature is not None:
            predictor_names += [spo2_feature] 

        model_ids.append(model_id)
        models[f'model_{model_id}'] = model
        models[f'pred_threshold_{model_id}'] = pred_threshold
        models[f'predictor_names_{model_id}'] = predictor_names


    if verbose:
        print(f'Following Apnea Models loaded: {model_ids}')
    return models, model_ids


def apnea_prediction_versions(data):

    model_combination = ['apnea_pred_ro_a3','apnea_pred_rsr_a3']
    data['apnea_pred_va_a3'] = data['apnea_pred_ro_a3'].copy()

    if not 'apnea_pred_rsr_a3' in data.columns:
        return data

    data['apnea_pred_va_a3'] = data['apnea_pred_rsr_a3'].copy()

    if ('oxygen_flow' in data.columns) & (not 'oxygen_flow_rate' in data.columns):
        print("WARNING: columns 'oxygen_flor_rate expected, but only 'oxygen_flow' available. Might indicate old file format.")

    if all(np.isin(model_combination + ['oxygen_flow_rate'] , data.columns)):
        # use respiration+spo2, except when oxygen is supplied or no spo2 is available, then respiration only pred: 'va for version a...'

        data['oxygen_flow_pad'] = data.oxygen_flow_rate.astype('float32').interpolate(method='pad').dropna()
        data['apnea_pred_any_a3'] = data[model_combination].max(axis=1)
        data.loc[data.oxygen_flow_pad>0, 'apnea_pred_va_a3'] = data.loc[data.oxygen_flow_pad>0, 'apnea_pred_ro_a3']
        data.loc[pd.isna(data.spo2), 'apnea_pred_va_a3'] = data.loc[pd.isna(data.spo2), 'apnea_pred_ro_a3']

        # also compute the only-during-sleep versions:
        data = apnea_prediction_only_sleep(data, 'apnea_pred_any_a3')

        data.drop(['oxygen_flow_pad'], axis=1, inplace=True)

    data = apnea_prediction_only_sleep(data, 'apnea_pred_va_a3')

    return data


def apnea_prediction_only_sleep(data, model_id, stage_name = 'stage_pred_amendsumeffort'):
    # apnea prediction with SleepStage information (exclude wake preditions)

    if (stage_name in data.columns) & ('apnea_pred_' + model_id in data.columns):
        data['apnea_pred_' + model_id + '_ss'] = data['apnea_pred_' + model_id].copy()
        data.loc[data[stage_name]==5, 'apnea_pred_' + model_id + '_ss'] = 0

    return data


def apply_apnea_prediction_models(data, fs=10, verbose=True, verbose_results=False):


    if ('spo2%' in data.columns) & (not 'spo2' in data.columns):
        data.rename({'spo2%': 'spo2'}, axis=1, inplace=True)

    models, model_ids = apnea_model_init(verbose=verbose)

    # simple, non-general check if apnea features are computed already:
    if not all(['katz_fd_10s_smoothed' in data.columns, 'movstd_10s' in data.columns]):
        print('Features necessary for Apnea Detection not yet computed/not contained. Return data unchanged.')
        return data

    data = get_apnea_predictors(data)

    data_airgo_available = data[np.logical_not(pd.isna(data.band))]
    spo2_available = 'spo2' in data.columns
    if spo2_available:
        spo2_available = spo2_available & (data_airgo_available.spo2.dropna().shape[0]>0)

    for model_id in model_ids:

        model = models[f'model_{model_id}']
        pred_threshold = models[f'pred_threshold_{model_id}']
        predictor_names = models[f'predictor_names_{model_id}']

        if ('rsr' in model_id.lower()) and (not spo2_available):
            if verbose:
                print(f'{model_id} not applied, no SpO2 available.')
            continue

        data = run_prediction_routine(data, model, model_id, pred_threshold, predictor_names)
        
        data = apnea_prediction_only_sleep(data, model_id)


        if verbose_results:
            num_apneas = sum(data.loc[data['to_predict']==1, f'apnea_pred_{model_id}'].diff()==1)
            print(f'{model_id}, number of apneas: {num_apneas}')

    data = apnea_prediction_versions(data)

    # when done, drop the predictors (not features):
    predictor_names = pd.read_csv(os.path.join('/media/mad3/Projects/Wolfgang/AirGoSleepStaging/final_models_apnea_detection/features_selected.csv'))
    data.drop(predictor_names.predictor_name, axis=1, inplace=True)
    
    return data

def get_apnea_predictors(data, fs=10, window_length_sec=90, idx_of_interest_sec=60):
    ''' from features to predictors... 
    idx_of_interest_sec: point in time of window where we want to evaluate if event happens or not.
    '''

    if not 'to_predict_apnea' in data.columns:
        data['to_predict_apnea'] = 0
        index_to_predict_apnea = data.iloc[::fs].index
        data.loc[index_to_predict_apnea, 'to_predict_apnea'] = 1

    predictor_names = pd.read_csv('/media/mad3/Projects/Wolfgang/AirGoSleepStaging/final_models_apnea_detection/features_selected.csv')
    window_length = window_length_sec * fs
    idx_of_interest = idx_of_interest_sec * fs

    # let's create help array that collects all the feature data (needed for .loc operation)
    df_predictors = pd.DataFrame(index=range(data.shape[0]))

    if all(np.isin(predictor_names.predictor_name, data.columns)):
        data.drop(predictor_names.predictor_name, axis=1, inplace=True)

    for predictor in predictor_names.predictor_name:
        df_predictors[predictor] = np.nan
        df_predictors[predictor] = df_predictors[predictor].astype('float32')

    for idx_selection in range(60*fs,data.shape[0]-40*fs,fs):

        data_window = data.iloc[idx_selection-idx_of_interest : idx_selection+window_length-idx_of_interest+1]
        predictor_values_tmp = []

        for predictor in predictor_names.predictor_name:
            idx = int(predictor[-2:])
            feature = predictor[:-3]

            predictor_values_tmp.append(data_window[feature].iloc[idx])

        df_predictors.loc[idx_selection, predictor_names.predictor_name] = predictor_values_tmp

    df_predictors.index = data.index
    df_predictors[predictor] = df_predictors[predictor].astype('float32')
    data = pd.concat([data, df_predictors], axis=1)

    # SpO2 drop feature:
    if 'spo2' in data.columns:
        if data.spo2.dropna().shape[0] > 0:
            fs_resampled = 1
            data['spo2_drop_45s'] = np.nan
            data.loc[data.index[::fs], 'spo2_drop_45s']= data['spo2'][::fs].astype('float32').rolling(45*fs_resampled, min_periods=5).apply(lambda x:  x.max() - x[-1],raw=False)

            # i think the to_predict==1 is always overlapping with the ::fs approach for spo2, just to be sure though:
            # assert(sum(np.logical_not(pd.isna(data[data.to_predict_apnea==1]['spo2_drop_45s'])))>0)

            data.loc[data.to_predict_apnea==1, 'spo2_drop_feature_0_40'] = get_spo2_drop_feature(data.loc[data.to_predict_apnea==1, 'spo2_drop_45s'].values, fs_resampled, seconds_pre=0, seconds_post=40)
            data.loc[data.to_predict_apnea==1, 'spo2_drop_feature_30_70'] = get_spo2_drop_feature(data.loc[data.to_predict_apnea==1, 'spo2_drop_45s'].values, fs_resampled, seconds_pre=30, seconds_post=70)

    return data


def run_prediction_routine(data, model, model_id, pred_threshold, predictor_names):
    
    to_predict_tmp = ((data['to_predict_apnea']==1) & (np.all(np.isfinite(data[predictor_names]), axis=1))).astype('int')
    data[f'to_predict_{model_id}'] = to_predict_tmp
    X = data.loc[data[f'to_predict_{model_id}']==1, predictor_names]

    if X.shape[0] > 0:

        y_prob = model.predict_proba(X)[:, 1]
        y_pred = y_prob > pred_threshold
        y_pred = y_pred.astype('int')

        data[f'apnea_pred_{model_id}'] = np.nan
        data[f'apnea_prob_{model_id}'] = np.nan

        data.loc[to_predict_tmp == 1, f'apnea_pred_{model_id}'] = y_pred
        data.loc[to_predict_tmp == 1, f'apnea_prob_{model_id}'] = y_prob

        data.loc[(to_predict_tmp == 0) & (data.to_predict_apnea == 1), f'apnea_pred_{model_id}'] = 0
        data.loc[(to_predict_tmp == 0) & (data.to_predict_apnea == 1), f'apnea_prob_{model_id}'] = 0

        data.loc[data['to_predict_apnea'] == 1, f'apnea_pred_{model_id}'] = smooth(data.loc[data['to_predict_apnea'] == 1, f'apnea_pred_{model_id}'].values, zeros=3)
        data = bridge_small_prediction_gaps(data, model_id)
        data = break_up_long_apnea_predictions(data, model_id)

    return data


def bridge_small_prediction_gaps(data, model_id):

    start = data.loc[data.to_predict_apnea==1, f'apnea_pred_{model_id}'].diff() == 1
    end = data.loc[data.to_predict_apnea==1, f'apnea_pred_{model_id}'].diff() == -1
    if data.loc[data.to_predict_apnea==1, f'apnea_pred_{model_id}'].iloc[0] == 1:
        start.iloc[0] = True
    if data.loc[data.to_predict_apnea==1, f'apnea_pred_{model_id}'].iloc[-1] == 1:
        end.iloc[-1] = True
    start_idx = np.where(start)[0]
    end_idx = np.where(end)[0]
    
#     import pdb; pdb.set_trace()
    end_indices_close_to_next_start = np.where(start_idx[1:] - end_idx[:-1] < 10)[0]
    for idx_tmp in end_indices_close_to_next_start:
        loc_to_change = data.loc[data.to_predict_apnea==1].iloc[end_idx[idx_tmp]: start_idx[idx_tmp+1]].index
        data.loc[loc_to_change, f'apnea_pred_{model_id}'] = 1
            
    return data


def break_up_long_apnea_predictions(data, model_id):
    
    for i in range(10):

        start = data.loc[data.to_predict_apnea==1, f'apnea_pred_{model_id}'].diff() == 1
        end = data.loc[data.to_predict_apnea==1, f'apnea_pred_{model_id}'].diff() == -1
        if data.loc[data.to_predict_apnea==1, f'apnea_pred_{model_id}'].iloc[0] == 1:
            start.iloc[0] = True
        if data.loc[data.to_predict_apnea==1, f'apnea_pred_{model_id}'].iloc[-1] == 1:
            end.iloc[-1] = True
        start_idx = np.where(start)[0]
        end_idx = np.where(end)[0]

        long_apnea = np.where(end_idx - start_idx > 70)[0]

        if len(long_apnea) == 0:
            return data

        for idx_tmp in long_apnea:
            loc_to_change = data.loc[data.to_predict_apnea==1].iloc[start_idx[idx_tmp]+45:start_idx[idx_tmp]+48].index
            
            data.loc[loc_to_change, f'apnea_pred_{model_id}'] = 0

    return data


def get_spo2_drop_feature(rolling_spo2_drop_array, fs, seconds_pre=0, seconds_post=40):
    '''
    rolling_spo2_drop_array: rolling spo2 drop (e.g. over 45 seconds) for each timepoint. (this is not supposed to be the feature for prediction because drop does not happen instantly. Plus: ICU sleep time alignment insecurity.)
    fs: sampling rate of rolling_spo2_drop_array
    seconds_pre: how many seconds before each timepoint are included to check for a drop (default: sleeplab: 0, icu-sleep: 30)
    seconds_post how many seconds after each timepoint are included to check for a drop (default: sleeplab: 40, icu-sleep: 70)

    return SPO2_drop_feature: max drop of SPO2% for a given timestamp (and it's pre and post environment).
    '''
    samples_pre = seconds_pre * fs
    samples_post = seconds_post * fs

    spo2_drop_feature = [np.nanmax(rolling_spo2_drop_array[x - samples_pre: x + samples_post]) for x in
                         range(samples_pre, len(rolling_spo2_drop_array) - samples_post)]
    spo2_drop_feature = np.concatenate(
        [np.zeros((samples_pre,)), np.array(spo2_drop_feature), np.zeros((samples_post,))])

    assert len(spo2_drop_feature) == len(
        rolling_spo2_drop_array), 'output array dimension does not match input array dimension?'

    return spo2_drop_feature


def self_similarity_indices(data, stage_variable = 'stage_pred', apnea_variable='apnea_pred_va_a3_ss'):
    
    self_similarity = data.self_similarity.values
    self_similarity_sleep = self_similarity[data[stage_variable]<5]
    self_similarity_apnea = self_similarity[data[apnea_variable]==1]
    hours_sleep = sum(data[stage_variable]<5)

    if self_similarity_sleep.shape[0] > 0:
        # self_similarity_sleep_index = simps(self_similarity_sleep, dx=1)/len(self_similarity_sleep)
        self_similarity_sleep_index = (sum(self_similarity_sleep) > 0.2) / hours_sleep
        self_similarity_sleep_q75 = np.quantile(self_similarity_sleep, 0.75)
        self_similarity_sleep_q50 = np.median(self_similarity_sleep)
    else:
        self_similarity_sleep_index = 0
        self_similarity_sleep_q75 = 0
        self_similarity_sleep_q50 = 0
        
    if self_similarity_apnea.shape[0] > 0:
        # self_similarity_apnea_index = simps(self_similarity_apnea, dx=1)/len(self_similarity_apnea)
        self_similarity_apnea_index = (sum(self_similarity_apnea) > 0.2) / sum(data[apnea_variable]==1)
        self_similarity_apnea_q75 = np.quantile(self_similarity_apnea, 0.75)
        self_similarity_apnea_q50 = np.median(self_similarity_apnea)
    else:
        self_similarity_apnea_index = 0
        self_similarity_apnea_q75 = 0
        self_similarity_apnea_q50 = 0        
        

    return [self_similarity_sleep_index, self_similarity_sleep_q50, self_similarity_sleep_q75,
            self_similarity_apnea_index, self_similarity_apnea_q50, self_similarity_apnea_q75]
























# def compute_feature_mean_movstd(signal_sel, quantile=0.5, mov_window_seconds=10, fs=10):

#     feature =  [signal_sel.movstd_10s.iloc[iPart-mov_window_seconds*fs : iPart].mean() for iPart in range(0,signal_sel.shape[0], fs)]
#     feature = pd.Series(feature).dropna()
#     feature = feature.loc[55:75]            # event-part of window

#     if len(feature)==0:
#         feature = np.nan
#     else:
#         feature = feature.quantile(quantile)

#     return feature

# def compute_feature_min_movstd(signal_sel, quantile=0.5, mov_window_seconds=10, fs=10):

#     feature =  [signal_sel.movstd_10s.iloc[iPart-mov_window_seconds*fs : iPart].min() for iPart in range(0,signal_sel.shape[0], fs)]
#     feature = pd.Series(feature).dropna()
#     feature_min = feature.loc[55:75]

#     if len(feature)==0:
#         feature = np.nan
#     else:
#         feature = feature_min.quantile(quantile)
#         loc_feature = feature_min.idxmin()*10

#     return loc_feature, feature

# def compute_feature_max_movstd(signal_sel, minimum_pos, quantile=0.5, mov_window_seconds=10, fs=10):

#     movstd =  [signal_sel.movstd_10s.iloc[iPart-mov_window_seconds*fs : iPart].quantile(quantile) for iPart in range(0,signal_sel.shape[0], fs)]
#     min_pos = int(minimum_pos/fs)
#     max_loc = min_pos + np.nanargmax(movstd[min_pos:min_pos+60])
#     max_loc = max_loc*fs
#     max_value = np.nanmax(movstd[min_pos:min_pos+60])

#     return max_loc, max_value


# def compute_feature_hypo_10_60s(signal_sel, quantile1=0.5, quantile2=0.5, mov_window_seconds=10, fs=10):

#     feature =  [signal_sel.movstd_10s.iloc[iPart-mov_window_seconds*fs : iPart].quantile(quantile1) for iPart in range(0,signal_sel.shape[0], fs)]
#     feature = pd.Series(feature).dropna()
#     feature = feature.loc[55:75]

#     if len(feature)==0:
#         feature = np.nan
#     else:
#         feature = feature.quantile(quantile2)

#     return feature

# def compute_feature_median_movstd_10s(signal_sel, mov_window_seconds=10, fs=10):
#     feature = np.nanmedian(signal_sel.movstd_10s.iloc[550:750])
#     return feature

# def compute_feature_median_movstd_30s(signal_sel, mov_window_seconds=10, fs=10):
#     feature = np.nanmedian(signal_sel.movstd_30s.iloc[550:750])
#     return feature

# def compute_feature_median_movstd_60s(signal_sel, mov_window_seconds=10, fs=10):
#     feature = np.nanmedian(signal_sel.movstd_60s.iloc[550:750])
#     return feature
# def compute_feature_median_movstd_5min(signal_sel, mov_window_seconds=10, fs=10):
#     feature = np.nanmedian(signal_sel.movstd_5min.iloc[550:750])
#     return feature

# def compute_feature_median_movstd_10min(signal_sel, mov_window_seconds=10, fs=10):
#     feature = np.nanmedian(signal_sel.movstd_10min.iloc[550:750])
#     return feature

# def compute_feature_ventilation_60s(signal_sel, quantile=0.5, mov_window_seconds=10, fs=10):
#     feature = signal_sel.ventilation_60s.iloc[550:750].quantile(quantile)
#     return feature

# def compute_feature_ventilation_10s(signal_sel, quantile=0.5, mov_window_seconds=10, fs=10):
#     feature = signal_sel.ventilation_10s.iloc[550:750].quantile(quantile)
#     return feature

# def compute_feature_sample_entropy(signal_sel, quantile=0.5, mov_window_seconds=10, fs=10, begin_window=55, end_window=75):

#     mov_katz = [sample_entropy(signal_sel.Band.iloc[i:i+10*fs]) for i in range(begin_window*fs,end_window*fs,fs)]
#     feature = pd.Series(mov_katz).dropna()
#     feature = feature.quantile(quantile)
#     return feature

# def compute_feature_katz_fd(signal_sel, quantile=0.5, mov_window_seconds=10, fs=10, begin_window=55, end_window=75):

#     mov_katz = [katz_fd(signal_sel.Band.iloc[i:i+10*fs]) for i in range(begin_window*fs,end_window*fs,fs)]
#     feature = pd.Series(mov_katz).dropna()
#     feature = feature.quantile(quantile)
#     return feature



# def compute_feature_min_ventmax(signal_sel, mov_window_seconds=10, fs=10):

#     min_movmax =  [signal_sel.ventmax_10s.iloc[iPart-mov_window_seconds*fs : iPart].min() for iPart in range(0,signal_sel.shape[0], fs)]

#     min_movmax_loc = np.nanargmin(min_movmax[55:75])+55
#     min_movmax = np.nanmin(min_movmax[55:75]) #  look for minimum only from second 55 - 75, current design of window

#     return min_movmax_loc*fs, min_movmax


def remove_bad_oximetry(data, fs=None):
    data.PR[data.PRquality < 70] = np.nan
    data.SPO2[data.PRquality < 70] = np.nan
    # to be included another rule if pysiologcially not meaningful large drop happens:

    large_std1 = data.SPO2.rolling(20).std() > 10
    large_std2 = data.SPO2.iloc[-1::-1].rolling(20).std() > 10
    large_std2 = large_std2.iloc[-1::-1]
    data.SPO2.loc[large_std1] = np.nan
    data.SPO2.loc[large_std2] = np.nan

    large_std1 = data.PR.rolling(20).std() > 10
    large_std2 = data.PR.iloc[-1::-1].rolling(20).std() > 10
    large_std2 = large_std2.iloc[-1::-1]
    data.PR.loc[large_std1] = np.nan
    data.PR.loc[large_std2] = np.nan

    if fs is not None:
        data['SPO2'].interpolate(method='linear', limit=int(6 * fs), inplace=True, limit_area='inside')
        data['PR'].interpolate(method='linear', limit=int(6 * fs), inplace=True, limit_area='inside')
    return data



def train_model(X_train, y_train, classifier='random_forest', l1_ratio=0.5, regularization_c=1):

    scaler = StandardScaler()
    scaler.fit(X_train)
    X_train = scaler.transform(X_train)

    # FIT MODEL and return:
    if classifier=='random_forest':
        classifier = RandomForestClassifier(random_state=0, max_features=None, min_samples_leaf = 2, n_jobs=-1)
        classifier.fit(X_train, y_train)
    elif classifier=='logistic_regression':
        classifier = LogisticRegression(random_state=0, fit_intercept=False, class_weight = 'balanced', max_iter=1000, penalty='elasticnet', l1_ratio=l1_ratio, solver='saga', C=regularization_c)
        classifier.fit(X_train, y_train)

    return scaler, classifier


def evaluate_model(X_test, y_test, classifier, scaler=None, threshold=0.5):

    if scaler is not None:
        X_test = scaler.transform(X_test)

    y_test_binary = y_test.copy()
    y_test_binary[np.in1d(y_test_binary, [1,2,3,4])] = 1
    y_test_binary[y_test_binary==6] = 0
    y_test_binary[y_test_binary==-1] = 0

    # y_test_pred = classifier.predict(X_test)
    y_test_prob = classifier.predict_proba(X_test)
    y_test_pred = y_test_prob[:, 1] > threshold
    y_test_pred = y_test_pred.astype('int')

    cm = confusion_matrix(y_test_binary, y_test_pred)
    cm_norm = confusion_matrix(y_test_binary, y_test_pred, normalize='true')
    accuracy = accuracy_score(y_test_binary, y_test_pred)
    fpr, tpr, thresholds = roc_curve(y_test_binary, y_test_prob[:,1], pos_label=1)

    custom_cfm = []
    for iC in range(5):
        acc_binarized = accuracy_score(y_test_binary[y_test==iC]>0, y_test_pred[y_test==iC])
        custom_cfm.append(acc_binarized)

    results = {}
    results['confusion_matrix'] = cm
    results['custom_cfm'] = custom_cfm
    results['confusion_matrix_norm'] = cm_norm
    results['accuracy'] = accuracy
    results['f1_score'] = f1_score(y_test_binary, y_test_pred)
    results['auc'] = auc(fpr, tpr)
    results['roc_curve'] = [fpr, tpr, thresholds]

    return results


def print_results(results):
        print('Confusion Matrix:')
        print(results['confusion_matrix'])
        print('AUC'.rjust(12) +': \t %.3f'%results['auc'])
        print('F1 score'.rjust(12) + ': \t %.3f' %results['f1_score'])
        classes = ['no event','obstructive','central','mixed','hypopnea']
#         classes = [x.rjust(12) for x in classes]
        print('Accuracies per class:')
        for accuracy_class, classname in list(zip(results['custom_cfm'], classes)):
            print(classname.rjust(12) + '\t %.3f'%accuracy_class)




def update_AHI_results(AHI_results, study_id, AHI_true, AHI_pred):
    AHI_results_tmp = pd.DataFrame()
    AHI_results_tmp['study_id'] = [study_id]
    AHI_results_tmp['AHI_true'] = [AHI_true]
    AHI_results_tmp['AHI_pred'] = [AHI_pred]
    AHI_results = AHI_results.append(AHI_results_tmp, ignore_index=True)
    return AHI_results

def get_data(data_path, columns, get_hdr=False):
    # load in 10 Hz data:
    [data, hdr] = load_sleep_data(data_path, idx_to_datetime=1)
    data = data[columns]
    data = data[data.Stage > -1]
    data['to_predict'] = 0
    data.loc[~data.isna().any(axis=1), 'to_predict'] = 1
    if get_hdr: return data, hdr
    else: return data


def predict_data(model, to_predict_matrix):
    y_pred = model.predict(to_predict_matrix)
    y_prob = model.predict_proba(to_predict_matrix)
    return y_pred, y_prob

def remove_predictions_wake(data):
    data.loc[(data['apnea_prediction']==1) & (data['Stage']==5), 'apnea_prediction'] = 0
    data.loc[(data['apnea_probability']==1) & (data['Stage']==5), 'apnea_probability'] = 0
    return data


def computeAHI(labels, predictions, show=False):
    ### COMPUTE AHI ###

    # make labels binary:
    labels = np.in1d(labels, [1,2,3,4]) # apneas and hypopneas

    events = ['No event', 'event']
    AHIevs = np.zeros([1, 2], dtype=int)

    # compute true AHI
    trues = np.array(labels == 1, dtype=int)
    trues = np.concatenate([[0], np.diff(trues)])
    beg = np.argwhere(trues > 0)[:, 0]
    tAHI = len(beg)
    # compute predicted AHI
    preds = np.array(predictions == 1, dtype=int)
    preds = np.concatenate([[0], np.diff(preds)])
    beg = np.argwhere(preds > 0)[:, 0]
    pAHI = len(beg)
    # print the AHI's
    if show:
        print('%ss: %d/%d (t/p)' % (events[1], tAHI, pAHI))
    # add each event count to matrix
    AHIevs[0, 0] = tAHI
    AHIevs[0, 1] = pAHI
    # return matrix with AHI's
    return AHIevs



def do_plot(data, save_path=None):
    data.loc[data.SPO2 < 85, 'SPO2'] = 85

    # replace all zeros by nan's
    y = data.Apnea.values.astype('float')
    y[(y == 0)] = float('nan')

    yp = data.apnea_prediction_smooth.values.astype('float')
    yp[yp == 0] = float('nan')

    yproba = data.apnea_probability.values.astype('float')
    # yproba = np.array([int(x*10)-4 for x in yproba if not np.isnan(x)]).astype('float')
    yproba[~np.isnan(yproba)] = yproba[~np.isnan(yproba)] * 10 - 4
    yproba[~np.isnan(yproba)] = yproba[~np.isnan(yproba)].astype('int').astype('float')
    yproba[yproba <= 0] = float('nan')  # prbability to [nan,1,2,3,4,5,6] from [0,0.5,0.6,0.7,0.8,0.9,1]

    band_wake = np.empty(data.Band.values.shape)
    band_wake[:] = np.nan
    band_sleep = np.empty(data.Band.values.shape)
    band_sleep[:] = np.nan
    band_wake[data.Stage == 5] = data.Band.values[data.Stage == 5]
    band_sleep[data.Stage < 5] = data.Band.values[data.Stage < 5]

    # apnea_prediction_smooth = apnea_prediction_smooth.astype('float')
    # apnea_prediction_smooth[apnea_prediction_smooth==0] = float('nan')

    assert (len(yp) == len(y)), 'Length of annotation and prediction arrays differ!'

    # use seg_start_pos to convert to the nonoverlapping signal
    # yp_smooth = apnea_prediction_smooth     # shape = (N, 4100)

    # define the ids each row
    nrow = 20
    row_ids = np.array_split(np.arange(len(data)), nrow)
    row_ids.reverse()

    fig = plt.figure(figsize=(24, 40))
    ax = fig.add_subplot(111)
    row_height = 25
    label_color = [None, 'b', 'g', 'cyan', 'm', 'k', 'r']
    confidence_color = [None, 'b', 'b', 'g', 'g', 'red', 'red']

    for ri in range(nrow):
        # plot signal
        #     ax.plot(data.hypo_10_60.values[row_ids[ri]] * 4+ri*row_height+5, c='g', lw=0.3)
        #     ax.plot(data.movavg_10s.values[row_ids[ri]] * 5+ri*row_height+5, c='g', lw=0.3)

        #     ax.plot(data.movstd_10s.values[row_ids[ri]] * 5+ri*row_height+3, c='g', lw=0.3)
        #     ax.plot(movstd_peaks[row_ids[ri]] * 5+ri*row_height+3, c='r', lw=0.3, marker='o', ms=4)

        #     ax.plot(data.Band.values[row_ids[ri]] * 2+ri*row_height, c='k', lw=0.3)
        ax.plot(band_sleep[row_ids[ri]] * 2 + ri * row_height, c='k', lw=0.3)
        ax.plot(band_wake[row_ids[ri]] * 2 + ri * row_height, c='r', lw=0.3)
        ax.plot(data.SPO2.values[row_ids[ri]] - np.nanmean(
            np.nanmean(data.SPO2.values[row_ids[ri]].astype('float32'))) - 5 + ri * row_height, c='darkblue', lw=0.3)
    #     ax.plot(data.prediction_proba.values[row_ids[ri]]-np.nanmean( np.nanmean(data.prediction_proba.values[row_ids[ri]].astype('float32'))) - 5 +ri*row_height, c='darkblue', lw=0.3)

    for yi in range(3):
        if yi == 0:
            y2 = y  # plot actual label
        elif yi == 1:
            y2 = yp  # plot raw model output
        elif yi == 2:
            y2 = yproba


        # run over each plot row
        for ri in range(nrow):
            # plot tech annonation
            ax.axhline(ri * row_height - 10 - yi, c=[0.5, 0.5, 0.5], ls='--', lw=0.2)  # gridline
            loc = 0

            # group all labels and plot them
            for i, j in groupby(y2[row_ids[ri]]):
                len_j = len(list(j))
                if not np.isnan(i) and label_color[int(i)] is not None:
                    # i is the value of the label
                    # list(j) is the list of labels with same value
                    if yi in [0, 1]:
                        ax.plot([loc, loc + len_j], [ri * row_height - 10 - yi] * 2, c=label_color[int(i)],
                                lw=1)  # [ri*row_height-3*(2**yi)]*2
                    else:
                        ax.plot([loc, loc + len_j], [ri * row_height - 10 - yi] * 2, c=confidence_color[int(i)],
                                lw=1)  # [ri*row_height-3*(2**yi)]*2

                loc += len_j

    # plot layout setup
    ax.set_xlim([0, max([len(x) for x in row_ids])])
    ax.axis('off')
    plt.tight_layout()
    # plt.title(test_info[si])
    # save the figure
    if save_path is not None:
        plt.savefig(save_path)

def smooth(y, win=10, zeros=3):
    ## apply smoothning for windows of length <win>
    seg_ids = np.arange(0, y.shape[0] - win + 1, 1)
    label_segs = y[[np.arange(x, x + win) for x in seg_ids]]
    # run over all windows
    for s, seg in enumerate(label_segs):
        lab, cn = np.unique(seg, return_counts=True)
        # make all 0's of <zeros>/<window> is no-event
        if lab[0] == 0 and cn[0] >= zeros:
            label_segs[s] = 0
        # otherwise take the most occuring value
        else:
            label_segs[s] = lab[np.argmax(cn, axis=0)]

    # save the smooth labels
    ys = label_segs[:, 0]
    y_smooth = np.array(ys)
    # determine shift
    shift = zeros - 1
    half_win = int(win / 2)

    # binarize for shift correction
    ys[ys > 0] = 1
    y_diff = np.concatenate([[0], np.diff(ys)])
    beg = np.argwhere(y_diff > 0)[:, 0]
    end = np.argwhere(y_diff < 0)[:, 0]
    # verify label size matches
    if beg.shape[0] != 0:
        if end.shape[0] == 0:
            end = np.array([y_diff.shape[0]])
        if beg[0] > end[0]:
            beg = np.concatenate([[0], beg])
        if beg[-1] > end[-1]:
            end = np.concatenate([end, [len(y_diff) - shift - half_win]])

    # Make sure only one label is assigned and shift all events by <zeros-1>, back to orignal
    for x in range(beg.shape[0]):
        # determine segment start & end
        s = beg[x]
        e = end[x]

        if s<e:
            # determine including labels
            lab, cn = np.unique(y_smooth[s:e], return_counts=True)
            try:
                # assign most occuring one to the whole segment + correction for the sliding window
                ce = e + half_win  # correction
                y_smooth[s:ce] = lab[np.argmax(cn, axis=0)]
                # and apply shift
                y_smooth[s + shift:ce + shift] = y_smooth[s:ce]
                y_smooth[s:s + shift] = 0
            except:
                try:
                    # print('Tried to fill the event till the end')
                    # assign most occuring one to the whole segment + correction for the sliding window
                    ce = -1  # correction
                    y_smooth[s:ce] = lab[np.argmax(cn, axis=0)]
                    # and apply shift
                    y_smooth[s + shift:ce] = int(y_smooth[s])
                    y_smooth[s:s + shift] = 0

                except:
                    print('But id didn\'t work, somthing went wrong with beginning (%s) and end (%s)' % (s, e))

    # correct array for the edges
    y_smooth = np.concatenate([y_smooth, y[:win - 1]])
    return (y_smooth)


