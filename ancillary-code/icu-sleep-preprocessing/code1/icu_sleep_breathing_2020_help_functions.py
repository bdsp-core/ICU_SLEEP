import pandas as pd
import numpy as np
import os
import sys
# sys.path.append('/home/wolfgang/repos/sleep_research_io')
# from sleep_research_functions import *


def inclusion_criteria(summary_days, summary_subjects=None):


    summary_days = summary_days.loc[summary_days.inclusion_subject == 1, :]
    summary_subjects = summary_subjects.loc[summary_subjects.inclusion_subject == 1, :]

    # summary_days = summary_days.loc[summary_days.airgo_available_h >= 2, :]
    # summary_days = summary_days.loc[summary_days.ecg_available >= 2, :]
#     summary_days = summary_days.loc[summary_days.sleep_hours_breathing >= 0.5, :]
#     summary_days = summary_days.loc[summary_days.sleep_hours_ecg_nn >= 0.5, :]
#     if summary_subjects is not None:
#         summary_subjects = summary_subjects.loc[np.isin(summary_subjects.study_id, summary_days.study_id.unique())]

    return summary_days, summary_subjects


def load_summary_data_with_inclusion_criteria(apply_inclusion_criteria=True, sleeplab_matched=False):
    
    dir_summaries = '/media/mad3/Projects/ICU_SLEEP_STUDY/Sleep_And_Breathing'
    if not os.path.exists(dir_summaries):
        dir_summaries = 'C:/Users/Wolfgang/Dropbox (Partners HealthCare)/SleepInICUandSleeplabPaper/Analysis'


    summary_subjects_icu = pd.read_csv(os.path.join(dir_summaries, 'summary_subjects_icu.csv'))
    summary_subjects_sleeplab = pd.read_csv(os.path.join(dir_summaries, 'summary_subjects_sleeplab.csv'))
    summary_days_icu = pd.read_csv(os.path.join(dir_summaries, 'summary_days_icu.csv'))
    if sleeplab_matched:
        summary_days_sleeplab = pd.read_csv(os.path.join(dir_summaries, 'summary_days_sleeplab_matched.csv'))
    else:
        summary_days_sleeplab = pd.read_csv(os.path.join(dir_summaries, 'summary_days_sleeplab.csv'))

        # filter/inclusion criteria:
    print(f'# of subjects ICU before inclusion criteria: {len(summary_days_icu.study_id.unique())}')
    print(f'# of 12-hour segments ICU before inclusion criteria: {summary_days_icu.shape[0]}')
    if apply_inclusion_criteria:
        summary_days_icu, summary_subjects_icu = inclusion_criteria(summary_days_icu, summary_subjects_icu)
        print(f'# of subjects ICU after inclusion criteria: {len(summary_days_icu.study_id.unique())}')
        print(f'# of 12-hour segments ICU after inclusion criteria: {summary_days_icu.shape[0]}')
    print(f"24-hour segments: {summary_days_icu.loc[summary_days_icu.day_cat == 'f', :].shape[0]}")
    print(f"12-hour segments: {summary_days_icu.loc[summary_days_icu.day_cat != 'f', :].shape[0]}")

    print('')
    print(f'# of subjects sleeplab before inclusion criteria: {len(summary_days_sleeplab.study_id.unique())}')
    print(f'# of 12-hour segments sleeplab before inclusion criteria: {summary_days_sleeplab.shape[0]}')
    if 0: # apply_inclusion_criteria:
        summary_days_sleeplab, summary_subjects_sleeplab = inclusion_criteria(summary_days_sleeplab, summary_subjects_sleeplab)
        print(f'# of subjects sleeplab after inclusion criteria: {len(summary_days_sleeplab.study_id.unique())}')
        print(f'# of 12-hour segments sleeplab after before inclusion criteria: {summary_days_sleeplab.shape[0]}')

    return [summary_subjects_icu, summary_subjects_sleeplab, summary_days_icu, summary_days_sleeplab]


