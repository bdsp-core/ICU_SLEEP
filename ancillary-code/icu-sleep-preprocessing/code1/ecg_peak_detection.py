import numpy as np
import pandas as pd
import os
import sys
import h5py
import traceback
sys.path.append('/home/wolfgang/repos/sleep_research_io')
from sleep_research_functions import load_sleep_data, write_to_hdf5_file, get_metadata, read_in_routine
from HRV_and_CPC_analysis_functions import ecg_hrv_cpc_routine, spectrum_plot_dt, cpc_and_signals_plot
from tqdm import tqdm
import matplotlib.pyplot as plt
from HRV_and_CPC_analysis_functions import load_ecg_data, ecg_peak_finding_routine

def main():

    do_plots = 1

    # directories with ECGs
    ecg_dir = '/media/mad3/Projects/ICU_SLEEP_STUDY/data/data_analysis/BMR_resampled_ECG'
    # save folders:
    ecg_r_peak_dir = '/media/mad3/Projects/ICU_SLEEP_STUDY/data/data_analysis/BMR_resampled_ECG_and_rpeaks2'
    if not os.path.exists(ecg_r_peak_dir):
        os.makedirs(ecg_r_peak_dir)

    # print quick summary of what files are available:
    ecg_files_available = os.listdir(ecg_dir)
    study_ids = [x.replace('ECG_', '').replace('.h5','') for x in ecg_files_available]
    study_ids.sort()

    files_done = os.listdir(ecg_r_peak_dir)
    study_ids_done = [x.replace('ECG_', '').replace('.h5','') for x in ecg_files_available]

    study_ids = list(set(study_ids) - set(study_ids_done))
    study_ids.sort()
    print(f'\nTo Do: {len(study_ids)}')
    study_ids = ['030']


    for study_id in tqdm(study_ids):

        try:

            # savepaths for this study_id:
            ecg_rpeak_path = os.path.join(ecg_r_peak_dir, 'ECG_' + str(study_id).zfill(3) + '.h5')

            # if os.path.exists(ecg_rpeak_path):
            #     print(f'{study_id} exists, continue.')
            #     continue

            print(study_id)

            path_ecg_data = os.path.join(ecg_dir, f'ECG_{study_id}.h5')
            signals_contained_ecg = get_metadata(path_ecg_data)
            print(signals_contained_ecg)

            if 0:
                print("DEBUGGING")
                fs = 240  # by default, after resampling
                data = load_ecg_data(path_ecg_data)

                leads = [x for x in data.keys() if '_startdatetime' not in x]
                assert leads[0] == 'I'
                ecg_lead = leads[0]
                signal_ecg_lead = pd.DataFrame(data[ecg_lead], columns=['signal'])
                signal_ecg_lead['signal'] = signal_ecg_lead['signal'] * 0.00243

                plt.figure(figsize=(10,6))
                plt.plot(signal_ecg_lead.signal)
                plt.show()

                plt.figure(figsize=(10,6))
                plt.plot(signal_ecg_lead.signal.iloc[:fs*3600])
                plt.savefig(str(study_id)+'_1.jpg')

                plt.figure(figsize=(10,6))
                plt.plot(signal_ecg_lead.signal.iloc[fs*3600:fs*7200])
                plt.savefig(str(study_id)+'_2.jpg')

                plt.figure(figsize=(10,6))
                plt.plot(signal_ecg_lead.signal.iloc[10000*fs:])
                plt.savefig(str(study_id)+'_3.jpg')

                plt.figure(figsize=(10,6))
                plt.plot(signal_ecg_lead.signal.iloc[fs*3500:fs*3600])
                plt.savefig(str(study_id)+'_4.jpg')

                plt.figure(figsize=(10,6))
                plt.plot(signal_ecg_lead.signal.iloc[10000*fs:10100*fs])
                plt.savefig(str(study_id)+'_5.jpg')

            signal_ecg_lead = ecg_peak_finding_routine(path_ecg_data, source='bedmaster')

            fig, ax = plt.subplots(2,1,figsize=(10, 5), sharex=True)
            ax[0].plot(signal_ecg_lead.signal)
            ax[0].scatter(signal_ecg_lead[signal_ecg_lead.r_peak == 1].index,
                          signal_ecg_lead[signal_ecg_lead.r_peak == 1].signal, c='red', s=6, zorder=5)
            ax[1].plot(signal_ecg_lead.sqi)
            plt.show()




            if not signal_ecg_lead is None:
                # save ECG and r peak detection:
                hdr = {}
                dt = signal_ecg_lead.index[0]
                hdr['start_datetime'] = np.array([dt.year, dt.month, dt.day,
                                                  dt.hour, dt.minute,
                                                  dt.second, dt.microsecond])
                hdr['study_id'] = int(study_id)
                hdr['fs'] = 240
                write_to_hdf5_file(signal_ecg_lead, ecg_rpeak_path, hdr = hdr, overwrite=True)

        except Exception as e:
            print(e)
            print(''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__)))
            continue


if __name__ == '__main__':
    main()