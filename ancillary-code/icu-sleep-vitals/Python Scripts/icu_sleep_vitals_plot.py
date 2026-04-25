#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import numpy as np
import os
import sys
import matplotlib
import matplotlib.pyplot as plt
import path_config

from datetime import timedelta
from edw_functions import *

# get_ipython().run_line_magic('load_ext', 'autoreload')
# get_ipython().run_line_magic('autoreload', '2')
# get_ipython().run_line_magic('matplotlib', 'widget')


pd.options.display.max_rows = 300
pd.options.display.max_columns = 300

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

print(cohort.tail(3))
print(cam.head(2))
print(adt.head(2))

# For each StudyID, we have some CAM dates - for those dates we know for sure the patient was in the hospital.
# Find the admission and discharge entries from ADT table that are closest to the first/last CAM dates.


def find_admission_and_discharge_entries(cohort):
    cohort['CAM_done'] = np.nan
    cohort['Admission'] = np.nan
    cohort['Discharge'] = np.nan

    for jloc, row in cohort.iterrows():
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
            cohort.loc[jloc, 'Admission'] = admission.iloc[-1]
        else:
            print(f'No Admission found for {row.Study_id}, {row.MRN}')
        # find discharge date
        discharge = adt_subject.loc[adt_subject.EffectiveDTS > date_pre_discharge].sort_values(by='EffectiveDTS')
        discharge = discharge.loc[discharge.ADTEventTypeDSC == 'Discharge', 'EffectiveDTS']
        if len(discharge) > 0:
            cohort.loc[jloc, 'Discharge'] = discharge.iloc[0]
        else:
            # possible, patient might still be in the hospital.
            print(f'No Discharge found for {row.Study_id}, {row.MRN}')
            cohort.loc[jloc, 'Discharge'] = pd.to_datetime('2099-01-01')

    # cohort = cohort[pd.notna(cohort.Admission)]
    # print(f'Number of Patients currently enrolled with at least 1 CAM-S assessment: {cohort.shape[0]}')

    #  print(cohort.head())


# #### read in EDW data

# just load raw vitals data to check what's in there.
def load_vitals_data_from_edw():
    vitals_raw = pd.read_csv(path_vitals_edw)
    vitals_raw.head(3)

    print(vitals_raw.FlowsheetMeasureNM.unique())
    vitals_raw[vitals_raw.FlowsheetMeasureNM == 'R ARTERIAL LINE BLOOD PRESSURE'].head()

    # load vitals and transform the data to sth. nicer to work with:
    data_vitals_edw = get_vitals(path_vitals_edw, load_raw=True)

    data_vitals_edw = data_vitals_edw.loc[np.isin(data_vitals_edw.MRN, cohort.MRN)]
    data_vitals_edw['Study_id'] = np.nan
    for study_id in cohort.Study_id.unique():
        mrn = cohort.loc[cohort.Study_id == study_id, 'MRN'].values[0].astype(int)
        data_vitals_edw.loc[data_vitals_edw.MRN == mrn, 'Study_id'] = study_id

    data_vitals_edw.head()

    vitals_cols = data_vitals_edw.columns[2:-1]
    data_vitals_edw[vitals_cols] = data_vitals_edw[vitals_cols].astype(float)

    print(vitals_cols)

# ### GET HL7 vitals here. TODO. For now, I create some artificial HL7 data.


def load_vitals_data_from_hl7(vitals_cols, data_vitals_edw):
    data_vitals_hl7 = pd.read_csv(path_vitals_hl7)

    random_error = (np.random.random(data_vitals_hl7[vitals_cols].shape) - 1) * 5

    data_vitals_hl7[vitals_cols] = data_vitals_hl7[vitals_cols].astype(float)
    data_vitals_hl7[vitals_cols] += random_error

    # ##### we actually don't need Urine output, at least I don't think that is contained in HL7

    vitals_cols = list(vitals_cols)
    if 'urine_output' in vitals_cols:
        vitals_cols.remove('urine_output')

    # #### tmp, select sample patient

    mrn_sel = cohort.MRN.iloc[0].astype(int)
    study_id = cohort.loc[cohort.MRN == mrn_sel, 'Study_id'].values[0]
    print(f'Selection MRN: {mrn_sel}, StudyID: {study_id}')

    cohort.loc[cohort.MRN == mrn_sel]

    cam_dates = cam[cam.Study_id == study_id].Date.values
    admission = cohort.loc[cohort.MRN == mrn_sel, 'Admission'].values[0]
    discharge = cohort.loc[cohort.MRN == mrn_sel, 'Discharge'].values[0]
    data_vitals_edw_subject = data_vitals_edw.loc[data_vitals_edw.MRN == mrn_sel]
    data_vitals_edw_subject = data_vitals_edw_subject.loc[(data_vitals_edw_subject.RecordedDTS > admission) &
                                                          (data_vitals_edw_subject.RecordedDTS < discharge)]
    data_vitals_edw_subject.sort_values(by='RecordedDTS', inplace=True)

    data_vitals_hl7_subject = data_vitals_hl7.loc[data_vitals_hl7.MRN == mrn_sel]
    data_vitals_hl7_subject = data_vitals_hl7_subject.loc[(data_vitals_hl7_subject.RecordedDTS > admission) &
                                                          (data_vitals_hl7_subject.RecordedDTS < discharge)]
    data_vitals_hl7_subject.sort_values(by='RecordedDTS', inplace=True)

    markersize = 4
    linewidth = 1

    fig, ax = plt.subplots(len(vitals_cols), 1, figsize=(8, 8), sharex='True')

    for i_ax, vital_name in enumerate(vitals_cols):
        # i_ax = 0
        # vital_name = 'bp_systolic'
        color_edw = 'blue'
        color_hl7 = 'green'

        if vital_name == 'pulse':  # pulse means heart rate.
            color_edw = 'black'
            color_hl7 = 'red'
        elif vital_name == 'pulse_oximetry':  # oxygen saturation
            color_edw = 'black'
            color_hl7 = 'royalblue'
        elif vital_name == 'respirations':  # oxygen saturation
            color_edw = 'black'
            color_hl7 = 'limegreen'
        elif vital_name == 'temperature':
            color_edw = 'black'
            color_hl7 = 'orange'

        vital_data_hl7 = data_vitals_hl7_subject[['RecordedDTS', vital_name]].dropna(how='any')
        vital_data_edw = data_vitals_edw_subject[['RecordedDTS', vital_name]].dropna(how='any')
        ax[i_ax].plot(vital_data_edw['RecordedDTS'], vital_data_edw[vital_name], linewidth=linewidth, c=color_edw,
                      marker='o', markersize=markersize)
        ax[i_ax].plot(vital_data_hl7['RecordedDTS'], vital_data_hl7[vital_name], linewidth=linewidth, c=color_hl7,
                      marker='o', markersize=markersize)
        ax[i_ax].set_title('  ' + vital_name, loc='left', pad=-10, y=1.01, color='black', x=0)

        if i_ax == 0:  # also plot CAM dates in first plot:
            ax[0].scatter(cam_dates, vital_data_edw[vital_name].max() * np.ones(len(cam_dates), ), c='red', s=16)
            ax[i_ax].legend(['EDW', 'HL7', 'CAM-S'])

        else:
            ax[i_ax].legend(['EDW', 'HL7'])

    plt.subplots_adjust(hspace=0, bottom=0.05, top=0.98)
    # plt.tight_layout()
    plt.savefig(f'vitals_edw_hl7_{mrn_sel}.png', dpi=600)
    plt.savefig(f'vitals_edw_hl7_{mrn_sel}.pdf')

    vital_name = 'temperature'

    print(vital_data_hl7.shape)
    # vital_data_edw

    np.corrcoef(vital_data_hl7[vital_name].values, vital_data_edw[vital_name].values)[0, 1]


if __name__ == "__main__":
    find_admission_and_discharge_entries(cohort)
    load_vitals_data_from_edw()
    load_vitals_data_from_hl7()
