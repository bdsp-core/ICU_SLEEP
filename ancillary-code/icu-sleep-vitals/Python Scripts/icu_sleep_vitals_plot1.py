import os
import logging
import pytz
from datetime import datetime
from datetime import timedelta
from edw_functions import *
import path_config

import h5py
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt


font = {'family': 'sans-serif', 'weight': 'normal', 'size': 7}
matplotlib.rc('font', **font)

# #### data paths
path_vitals_edw = path_config.path_vitals_edw  # pulled from EDW.
path_vitals_hl7 = path_config.path_vitals_hl7
path_adt = path_config.path_adt

# the following two files are from RedCap, the portal our Clinical Research Coordinators use and enter data:
path_cohort = path_config.path_cohort
path_cam = path_config.path_cam  # CAM = Confusion Assessment Matrix ... to measure/assess delirium.

# read in LIST, ADT, and CAM data
cohort = pd.read_csv(path_cohort)
cohort.rename({'Study ID:': 'Study_id', 'MRN:': 'MRN', cohort.columns[7]: 'Enrollment'}, axis=1, inplace=True)
cohort = cohort.loc[cohort.Study_id != '98a', :]
cohort.Study_id = cohort.Study_id.astype(int)
# manual correction for 3 MRNs needed (they had a MRN change during their stay):
cohort.loc[cohort['Study_id'] == path_config.icu_sleep_vitals_plot_StudyID1, 'MRN'] = path_config.icu_sleep_vitals_plot_MRN1
cohort.loc[cohort['Study_id'] == path_config.icu_sleep_vitals_plot_StudyID2, 'MRN'] = path_config.icu_sleep_vitals_plot_MRN2
cohort.loc[cohort['Study_id'] == path_config.icu_sleep_vitals_plot_StudyID3, 'MRN'] = path_config.icu_sleep_vitals_plot_MRN3

cohort = cohort.dropna(how='all', axis=0, subset=['MRN'])
cohort['Enrollment'] = pd.to_datetime(cohort['Enrollment'], infer_datetime_format=1)

cam = pd.read_csv(path_cam)
cam.rename({'Study ID:': 'Study_id', 'MRN:': 'MRN', cam.columns[9]: 'Date'}, axis=1, inplace=True)
cam = cam.loc[cam.Study_id != '98a', :]
cam.Study_id = cam.Study_id.astype(int)

cam['Date'] = pd.to_datetime(cam['Date'], infer_datetime_format=1)

adt = pd.read_csv(path_adt)
adt['EffectiveDTS'] = pd.to_datetime(adt['EffectiveDTS'], infer_datetime_format=1)

print("The last three records of the cohort are:")
print()
print(cohort.tail(3))
print()
print("The top two records of the cam are:")
print()
print(cam.head(2))
print()
print("The top two records of the adt are:")
print()
print(adt.head(2))
print()

cohort['CAM_done'] = np.nan
cohort['Admission'] = np.nan
cohort['Discharge'] = np.nan
# cohort['EncounterID'] = np.nan

for jloc, row in cohort.iloc[:304].iterrows():
    cam_subject = cam[(cam.Study_id == row.Study_id) & (cam['CAM performed?'] == 'Yes')]
    adt_subject = adt[adt.MRN == row.MRN]

    cam_dates = list(cam_subject.Date.dropna())
    cam_dates.sort()
    if len(cam_dates) == 0:
        date_post_admission = row.Enrollment + timedelta(hours=24)
        date_pre_discharge = row.Enrollment
        cohort.loc[jloc, 'CAM_done'] = 0
    else:
        date_post_admission = cam_dates[0]
        date_pre_discharge = pd.Timestamp(cam_dates[-1].date())
        cohort.loc[jloc, 'CAM_done'] = 1

    # find admission date
    admission = adt_subject.loc[adt_subject.EffectiveDTS < date_post_admission].sort_values(by='EffectiveDTS')
    admission = admission.loc[admission.ADTEventTypeDSC == 'Admission', 'EffectiveDTS']
    #     if len(admission) == 0: # sometimes, no 'Admission' is in the ADT but only 'Transfer In'
    #         admission = adt_subject.loc[adt_subject.EffectiveDTS < date_post_admission].sort_values(by='EffectiveDTS')
    #         admission = admission.loc[admission.ADTEventTypeDSC == 'Transfer In', 'EffectiveDTS']

    if len(admission) > 0:
        admission = admission.iloc[-1]
        cohort.loc[jloc, 'Admission'] = admission
    else:
        print(f'No Admission found for {row.Study_id}, {row.MRN}')
        
    # find discharge date
    discharge = adt_subject.loc[adt_subject.EffectiveDTS > date_pre_discharge].sort_values(by='EffectiveDTS')
    discharge = discharge.loc[discharge.ADTEventTypeDSC == 'Discharge', 'EffectiveDTS']
    if len(discharge) > 0:
        discharge = discharge.iloc[0]
        cohort.loc[jloc, 'Discharge'] = discharge

    else:
        # possible, patient might still be in the hospital.
        print(f'No Discharge found for {row.Study_id}, {row.MRN}')
        cohort.loc[jloc, 'Discharge'] = pd.to_datetime('2099-01-01')
        
    # get EncounterID
    # import pdb; pdb.set_trace()
    try:
        adt_subject_encounter = adt_subject.loc[(adt_subject.EffectiveDTS >= admission) & (adt_subject.EffectiveDTS <= discharge), :]

        encounter_ids = ';'.join(
            pd.Series(adt_subject_encounter.PatientEncounterID.dropna().unique().astype(int)).map(str).apply(
                lambda e: "'" + e + "'").tolist())
        cohort.loc[jloc, 'EncounterID'] = encounter_ids

    except:
        print(f'EncounterID Error: {row.Study_id}')

# Read in EDW data

# Just load raw vitals data to check what's in there.
vitals_raw = pd.read_csv(path_vitals_edw)
print()
print("The top three records of the vitals are:")
print()
print(vitals_raw.head(3))
print()
print("The top five records of the vital R ARTERIAL LINE BLOOD PRESSURE are:")
print()
print(vitals_raw[vitals_raw.FlowsheetMeasureNM == 'R ARTERIAL LINE BLOOD PRESSURE'].head())

# Load vitals and transform the data to something nicer to work with:
data_vitals_edw = get_vitals(path_vitals_edw, load_raw=True)

data_vitals_edw = data_vitals_edw.loc[np.isin(data_vitals_edw.MRN, cohort.MRN)]
data_vitals_edw['Study_id'] = np.nan
for study_id in cohort.Study_id.unique():
    mrn = cohort.loc[cohort.Study_id == study_id, 'MRN'].values[0].astype(int)
    data_vitals_edw.loc[data_vitals_edw.MRN == mrn, 'Study_id'] = study_id

print()
print("The top five records of the edw are:")
print()
print(data_vitals_edw.head())

vitals_cols = data_vitals_edw.columns[2:-1]
data_vitals_edw[vitals_cols] = data_vitals_edw[vitals_cols].astype(float)

print()
print(vitals_cols)

def get_local_timestamps(time_array: np.ndarray) -> np.ndarray:
    # Check if time_array falls in a time change (if timestamp is not nan)
    if not (pd.isnull(time_array[0]) or pd.isnull(time_array[-1])):
        init_dt = datetime.utcfromtimestamp(time_array[0])
        end_dt = datetime.utcfromtimestamp(time_array[-1])
        offset_init = TIMEZONE.utcoffset(init_dt, is_dst=True).total_seconds()
        offset_end = TIMEZONE.utcoffset(end_dt, is_dst=True).total_seconds()
        offsets = np.array([offset_init, offset_end])
    else:
        offsets = np.array([np.nan, np.nan])

    # Convert unix to local and readable timestamps
    if offsets[0] == offsets[1]:
        local_timearray = pd.to_datetime(time_array + offsets[0], unit="s")
        local_timearray = np.array(local_timearray, dtype="datetime64[us]")
    else:
        local_timearray = np.empty(np.size(time_array), dtype="datetime64[us]")
        for idx, time_value in enumerate(time_array):
            if not pd.isnull(time_value):
                time_dt = datetime.fromtimestamp(time_value, TIMEZONE)
                local_timearray[idx] = pd.to_datetime(time_dt.strftime("%Y-%m-%d %H:%M:%S.%f"))
            else:
                local_timearray[idx] = np.datetime64("NaT")

    return local_timearray


print("The version of h5py installed on the system is:", h5py.__version__)
TIMEZONE = pytz.timezone("US/Eastern")
print("The current TIMEZONE is:", TIMEZONE)

data_directory = path_config.data_directory  # location of tensorized bedmaster files
print(os.listdir(data_directory))

# Select patient for which ML4C3-data (bedmaster vitals, EDW vitals) are plotted together with the EDW vitals we have pulled

# Map the EDW vital sign names to bedmaster equivalent.
bm_vitals_name_mapping = {'bp_art_diastolic': 'art1d',
                          'bp_art_systolic': 'art1s',
                          'bp_diastolic': 'nbpd',
                          'bp_systolic': 'nbps',
                          'pulse': 'hr',
                          'pulse_oximetry': 'spo2%',
                          'respirations': 'resp',
                          }

edw_vitals_names = ['bp_art_diastolic', 'bp_art_systolic', 'bp_diastolic', 'bp_systolic', 'pulse', 'pulse_oximetry',
                    'respirations']

bm_vitals_names = ['art1d', 'art1s', 'nbpd', 'nbps', 'hr', 'spo2%', 'resp']

'''
ROADMAP for bedmaster vitals:
1. Open bedmaster hd5 file.  
2. First Aim: Create a dataframe with datetime index and vital sign data as columns. init empty dataframe.  
3. Loop through each vital signal signal, load it, convert the unix-timestamps to local time and join it to the vitals-dataframe.  
4. All data for a patient is now loaded, proceed with plotting.  
'''


def load_selected_vs(data_bm_subject, encounter_id, vital_name_bm_tmp):
    """ for selected vital sign, load the data, convert time to date-time like and return dataframe with index datetime and one column for vitalsign data"""
    vitals_values_tmp = data_bm_subject['bedmaster'][encounter_id]['vitals'][vital_name_bm_tmp]['value'][:]
    vitals_dts_tmp = data_bm_subject['bedmaster'][encounter_id]['vitals'][vital_name_bm_tmp]['time'][:]
    assert vitals_values_tmp.shape[0] == vitals_dts_tmp.shape[
        0], 'Vital sign value array and timestamp arrays do not have same shape!'
    vitals_dts_tmp = get_local_timestamps(vitals_dts_tmp)  # unix -> datetime

    vitals_df_tmp = pd.DataFrame(columns=['datetime', vital_name_edw_tmp])
    vitals_df_tmp['datetime'] = vitals_dts_tmp
    vitals_df_tmp[vital_name_edw_tmp] = vitals_values_tmp
    vitals_df_tmp.set_index('datetime', inplace=True)
    return vitals_df_tmp


def add_selected_vs_to_df_encounter(bm_vitals_encounter_df, vitals_df_tmp):
    """join a single vital signs dataframe to encounter vitals dataframe that collects all vital signs"""
    bm_vitals_encounter_df = bm_vitals_encounter_df.join(vitals_df_tmp, how='outer')
    return bm_vitals_encounter_df


def bm_edw_plot_routine():
    cam_dates = cam[cam.Study_id == study_id].Date.values
    admission = cohort.loc[cohort.MRN == mrn_sel, 'Admission'].values[0]
    discharge = cohort.loc[cohort.MRN == mrn_sel, 'Discharge'].values[0]
    data_vitals_edw_subject = data_vitals_edw.loc[data_vitals_edw.MRN == mrn_sel]
    data_vitals_edw_subject = data_vitals_edw_subject.loc[(data_vitals_edw_subject.RecordedDTS > admission) &
                                                          (data_vitals_edw_subject.RecordedDTS < discharge)]
    data_vitals_edw_subject.sort_values(by='RecordedDTS', inplace=True)

    data_vitals_bm_subject = bm_vitals_subject_df.loc[(bm_vitals_subject_df.index > admission) &
                                                      (bm_vitals_subject_df.index < discharge)]
    data_vitals_bm_subject.sort_index(inplace=True)

    markersize = 2
    linewidth = 1

    fig, ax = plt.subplots(len(vitals_cols), 1, figsize=(12, 8), sharex=True)

    for i_ax, vital_name in enumerate(vitals_cols):

        #     i_ax = 0
        #     vital_name = 'bp_systolic'
        color_edw = 'blue'
        color_bm = 'green'

        if vital_name == 'pulse':  # pulse means heart rate.
            color_edw = 'black'
            color_bm = 'red'
        elif vital_name == 'pulse_oximetry':  # oxygen saturation
            color_edw = 'black'
            color_bm = 'royalblue'
        elif vital_name == 'respirations':  # oxygen saturation
            color_edw = 'black'
            color_bm = 'limegreen'
        elif vital_name == 'temperature':
            color_edw = 'black'
            color_bm = 'orange'

        if vital_name in data_vitals_edw_subject.columns:
            vital_data_edw = data_vitals_edw_subject[['RecordedDTS', vital_name]].dropna(how='any')
            ax[i_ax].plot(vital_data_edw['RecordedDTS'], vital_data_edw[vital_name], linewidth=0, c=color_edw,
                          marker='o',
                          markersize=markersize, zorder=2)

        if vital_name in data_vitals_bm_subject.columns:
            ax[i_ax].plot(data_vitals_bm_subject.index, data_vitals_bm_subject[vital_name], linewidth=linewidth,
                          c=color_bm, zorder=1)

        ax[i_ax].set_title('  ' + vital_name, loc='left', pad=-10, y=1.01, color='black', x=0)

        if i_ax == 0:  # also plot CAM dates in first plot:
            y_loc_cam = np.nanmax([vital_data_edw[vital_name].dropna().max(), 90])
            ax[0].scatter(cam_dates, y_loc_cam * np.ones(len(cam_dates), ), c='red', s=16, zorder=3)
            ax[i_ax].legend(['EDW', 'BM', 'CAM-S'], frameon=False, fontsize=6, loc=3)

        else:
            ax[i_ax].legend(['EDW', 'BM'], frameon=False, fontsize=6, loc=3)

    plt.subplots_adjust(hspace=0, bottom=0.05, top=0.98)

    return fig


# Note this code so far has only been tested with one encounter, multiple encounters for one patient need to be checked if it works as expected.

mrn_sel = path_config.icu_sleep_vitals_plot_MRN  # select your MRN of interest (loop over all MRNs)
print(mrn_sel)

print()
print("This is how the cohort looks now: ")
print(cohort)

cohort.MRN = mrn_sel
print()
print("The MRN to be selected from the cohort is:")
print(cohort.MRN)
print()

# subject level:
study_id = cohort.loc[cohort.MRN == mrn_sel, 'Study_id'].values[0]
print(cohort.loc[cohort.MRN == mrn_sel])
print()
print(f'Selection MRN: {mrn_sel}, StudyID: {study_id}')

bmfile = f'{mrn_sel}.hd5'
print()
print(bmfile)
print()
data_bm_subject = h5py.File(os.path.join(data_directory, bmfile), "r")
print(data_bm_subject.keys())
print('Encounters in bedmaster file:')
print(data_bm_subject['bedmaster'].keys())
print()
bm_vitals_subject_df = pd.DataFrame(columns = edw_vitals_names) # init empty dataframe for bedmaster vitals
print(bm_vitals_subject_df)
print()
print(cohort.columns.values.tolist())
print()
encounter_ids = cohort.loc[cohort.MRN == mrn_sel, 'EncounterID'].values[0]
encounter_ids = encounter_ids.split(';')
print(encounter_ids)
print()

# encounter level:
for encounter_id in encounter_ids:
    encounter_id = encounter_id.replace("'", "")
    bm_vitals_encounter_df = pd.DataFrame()

    for vital_name_edw_tmp in edw_vitals_names:
        vital_name_bm_tmp = bm_vitals_name_mapping[vital_name_edw_tmp]

        if not encounter_id in data_bm_subject['bedmaster'].keys():
            continue
            
        if not data_bm_subject['bedmaster'][encounter_id]['vitals'].keys():
            continue

        vitals_df_tmp = load_selected_vs(data_bm_subject, encounter_id, vital_name_bm_tmp)
        bm_vitals_encounter_df = add_selected_vs_to_df_encounter(bm_vitals_encounter_df, vitals_df_tmp)

    # concat all different encounters:
    bm_vitals_subject_df = pd.concat([bm_vitals_subject_df, bm_vitals_encounter_df], axis=0)
    print(bm_vitals_subject_df)
    print()

# PLOT:
fig = bm_edw_plot_routine()

fig.savefig(f'vitals_edw_bm_{mrn_sel}.png', dpi=600)
fig.savefig(f'vitals_edw_bm_{mrn_sel}.pdf')

data_bm_subject.close()  # close hd5 file
