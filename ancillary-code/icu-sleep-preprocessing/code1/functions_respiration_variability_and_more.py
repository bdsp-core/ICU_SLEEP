





# peak detection: probably you don't need it, but just here for completeness:
# parameters specific for airgo signal, although distance and width could be universal.
peaks, peak_prop = find_peaks(data.movavg_0_5s, prominence=1, distance=int(fs*1.2), width=int(0.4*fs), 
	rel_height=1)
# rel_height=1 makes width be measured at bottom of peak candidates.

data['peaks'] = 0
peaks_loc = data.iloc[peaks].index
data.loc[peaks_loc, 'peaks'] = 1
data['peak_prom']=0
data.loc[peaks_loc, 'peak_prom'] = peak_prop['prominences']


# Inter Breath Interval. This is for the regularity of the breath peak timings:
# pre-requisite: you already compute the peaks before data, 
# i.e. data.peaks is a boolean with 1 where a peak is detected.

data['IBI'] = np.nan
BB_interval = np.diff(np.where(data.peaks==1)[0])
BB_interval = np.concatenate([BB_interval[:1],BB_interval])
data.loc[data.peaks==1, 'IBI'] = BB_interval/fs
data.loc[data['IBI']>15, 'IBI']=15
data['IBI'].interpolate(method='linear', limit=20*fs, limit_area='inside', inplace=True)

data['IBI_mean_5min'] = np.nan
data.loc[data.peaks==1, 'IBI_mean_5min'] = data['IBI'][data.peaks==1].rolling('5min', min_periods=1).mean()
data['IBI_std_5min'] = np.nan
data.loc[data.peaks==1, 'IBI_std_5min'] = data['IBI'][data.peaks==1].rolling('5min', min_periods=1).std()

### ventilation:

# simple 'instantenious' ventilation just the derivative, but not negative:
data['ventilation0']      = np.maximum(np.zeros(data['deriv1'].shape), data['deriv1'].values)
# sum it up for 10 seconds and normalize to 'minute ventilation':
# i do this ugly reset index thing because there is no center=True option available for datetime index, yours does not have to have the reset_index part.
data['ventilation_10s']   = data['ventilation0'].reset_index(drop=True).rolling(10*fs, center=True, min_periods=1).sum().values*6
# smooth it:
data['ventilation_10s_smooth'] = data['ventilation_10s'].reset_index(drop=True).rolling(6*fs, center=True, min_periods=1).mean().values



from scipy.stats import variation

def compute_breathing_instability_index(data, vname='2min', sec=120, fs=10):

    data[f'ventilation_cvar_{vname}'] = data[f'ventilation_10s_smooth'].reset_index(drop=True).rolling(sec*fs, center=True, min_periods=1).apply(lambda x: variation(x, nan_policy='omit'), raw=False).values
    data[f'IBI_cvar_{vname}'] = data['IBI'].reset_index()['IBI'].rolling(sec*fs, center=True, min_periods=1).apply(lambda x: variation(x, nan_policy='omit'), raw=False).values
    data[f'instability_index_{vname}'] = (data[f'ventilation_cvar_{vname}'].values + data[f'IBI_cvar_{vname}'].values)/2
    return data


### NOTE: one thing i forgot to mention: i also like to combine the timing and ventilation
# regularity because, even if the peak detection is wrong in irregular breathing parts (possible), 
# then the ventilation part might still peak up real (ir)regularity, as it is independent of the peak detection.

# compute the 30 sec and 2 min breathing stability indices:
vname='30sec'
sec=30
data = compute_breathing_instability_index(data, vname=vname, sec=sec, fs=10)

vname='2min'
sec=120
data = compute_breathing_instability_index(data, vname=vname, sec=sec, fs=10)





###### SELF SIMILARITY PART #####

from main_central_apnea_app import compute_similarity

# This is for airgo, however, see the main_central_apnea_app part for the effort belts.


def self_similarity_airgo(data, fs=10, verbose=False):


    if data.band.dropna().shape[0] == 0:

        if verbose:
            print("No 'band' data available, no self similarity computed.")

        return datas

    if not 'peaks' in data.columns:
        data = airgo_breath_peak_detection(data, fs=fs, prominence=1, rel_height=1)

    data['troughs'] = 0
    loc_peak = data[data.peaks==1].index
    trough_loc = [data.movavg_0_5s[loc_peak[iP]:loc_peak[iP+1]].idxmin() for iP in range(loc_peak.shape[0]-1)]
    data.loc[trough_loc, 'troughs'] = 1

    trace = data.movavg_0_5s.values
    peaks = np.where(data.peaks==1)[0]
    troughs = np.where(data.troughs==1)[0]

    f_interp = interpolate.interp1d(peaks, trace[peaks], kind='cubic',fill_value="extrapolate")                                
    envelope_up = f_interp(range(len(trace)))

    f_interp = interpolate.interp1d(troughs, trace[troughs], kind='cubic',fill_value="extrapolate")                                
    envelope_lo = f_interp(range(len(trace)))
    
    similarity_array = compute_similarity(envelope_up, envelope_lo, fs)
    
    data['envelope_up'] = envelope_up
    data['envelope_lo'] = envelope_lo
    data['self_similarity'] = similarity_array
    
    return data
