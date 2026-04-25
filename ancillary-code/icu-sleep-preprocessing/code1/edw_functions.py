import pandas as pd
import numpy as np
import os


def get_vitals_single_mrn(filepath, mrn):

    data_vitals_all_mrns = get_vitals(filepath, load_raw=1)
    edw_vitals = data_vitals_all_mrns[data_vitals_all_mrns.MRN == mrn].copy()
    edw_vitals.drop(['MRN'], axis=1, inplace=True)
    edw_vitals.rename({'RecordedDTS': 'datetime'}, axis=1, inplace=True)
    edw_vitals.set_index('datetime', inplace=True)
    
    return edw_vitals


def get_edw_oxygen_single_mrn(filepath, mrn):
    
    data_oxygen_all_mrns = get_edw_oxygen(filepath, load_raw=1)
    edw_oxygen = data_oxygen_all_mrns[data_oxygen_all_mrns.MRN == mrn].copy()
    edw_oxygen.drop(['MRN'], axis=1, inplace=True)
    edw_oxygen.rename({'RecordedDTS': 'datetime'}, axis=1, inplace=True)
    edw_oxygen.set_index('datetime', inplace=True)
    
    return edw_oxygen


def save_edw_vitals_df_for_each_mrn(data_vitals_all_mrns, savedir, filename_start = ''):
    mrn_s = pd.unique(data_vitals_all_mrns.MRN)
    for mrn in mrn_s:
        data_mrn = data_vitals_all_mrns[data_vitals_all_mrns.MRN == mrn]
        data_mrn.to_csv(os.path.join(savedir, filename_start+str(mrn)+'.csv'))


def raw_vitals_load(filepath):
    '''
    filepath: raw vitals output from EDW.
    output: raw data with basic preprocessing done.
    '''
    vitals_raw = pd.read_csv(filepath)
    vitals_raw = vitals_raw.drop_duplicates(subset=['MRN', 'FlowsheetMeasureNM', 'RecordedDTS', 'MeasureTXT'])
    vitals_raw.dropna(subset=['MeasureTXT'], inplace=True)
    vitals_raw.RecordedDTS = pd.to_datetime(vitals_raw.RecordedDTS, infer_datetime_format=1)
    return vitals_raw


def get_vitals(vitals_raw, mrn_s=None, load_raw=False):
    '''
    in:
    vitals_raw = raw vitals output from EDW after loading it with raw_vitals_load() 
    or it can be a filepath, then load_raw must be True.
    mrn_s: list of MRNs. If None: all MRNs in vitals_raw,
    output:
    dictionary with MRNs as keys and patient-wise dataframes as values
    '''

    if load_raw:
    	vitals_raw = raw_vitals_load(vitals_raw)

    if any([type(mrn_s) == np.int64, type(mrn_s)==float, type(mrn_s)==int]):
        mrn_s = [mrn_s]
    if mrn_s is None: 
        mrn_s = pd.unique(vitals_raw.MRN)
    
    data_vitals_all_mrns = pd.DataFrame()
    
    for mrn_tmp in mrn_s:
        # for a MRN, get time-index based dataframe containing the vitals:
        vital_data_mrn = vitals_raw[vitals_raw.MRN == mrn_tmp]
        vital_data_df = vitals_df(vital_data_mrn)
        
        data_vitals_all_mrns = pd.concat([data_vitals_all_mrns, vital_data_df], axis=0, sort=True)
        
    return data_vitals_all_mrns


def vitals_df(data):
    '''
    input: 
    data: raw vitals containing the data for a single MRN.
    output:
    vital_data_df: dataframe structure with the containing vitals.
    '''
    mrn = pd.unique(data.MRN)
    assert(len(mrn)==1)
    mrn = mrn[0]
    
    vital_data_df = pd.DataFrame([])
    
    vitals_contained = pd.unique(data.FlowsheetMeasureNM)
    vitals_todo = ['PULSE OXIMETRY', 'TEMPERATURE', 'PULSE', 'RESPIRATIONS', 'URINE OUTPUT', 'BLOOD PRESSURE']
    
    for vital_tmp in vitals_todo:
        if not vital_tmp in vitals_contained: 
            continue
        
        vital_data = data[data.FlowsheetMeasureNM == vital_tmp].copy()
        vital_data.set_index('RecordedDTS', inplace=True)

        if vital_tmp == 'BLOOD PRESSURE':
            vital_data['bp_systolic'] = vital_data.MeasureTXT.apply(lambda x: x.split('/')[0])
            vital_data['bp_diastolic'] = vital_data.MeasureTXT.apply(lambda x: x.split('/')[1])
            vital_data = vital_data[['bp_systolic', 'bp_diastolic']]
        else:
            new_columns_name = vital_tmp.replace(' ','_').lower()
            vital_data.rename({'MeasureTXT':new_columns_name}, axis=1, inplace=True)
            vital_data = vital_data[new_columns_name]
            
        vital_data_df = vital_data_df.join(vital_data, how='outer')
        
    vital_data_df['MRN'] = mrn
    vital_data_df.reset_index(inplace=True)
        
    return vital_data_df



def get_edw_oxygen(vitals_raw, mrn_s=None, load_raw=False):
    '''
    similar to get_vitals but for the oxygen edw data.
    '''
    if load_raw:
        vitals_raw = pd.read_csv(vitals_raw)
        vitals_raw.drop(['PatientID','PatientEncounterID','InpatientDataID','DepartmentID','FlowsheetDataID','FlowsheetMeasureID'], axis=1, inplace=True)
        vitals_raw.drop_duplicates(inplace=True)
        vitals_raw.RecordedDTS = pd.to_datetime(vitals_raw.RecordedDTS, infer_datetime_format=1)

    if any([type(mrn_s) == np.int64, type(mrn_s)==float, type(mrn_s)==int]):
        mrn_s = [mrn_s]
    if mrn_s is None: 
        mrn_s = pd.unique(vitals_raw.MRN)
    
    event_ids = np.unique(vitals_raw.FlowsheetMeasureNM)

    df_mrn_s = []
    for mrn in mrn_s:

        df_mrn = vitals_raw[vitals_raw.MRN==mrn].copy()
        df_mrn.sort_index(inplace=True)
        dfs_event = []

        for event_id in event_ids:
            df_event = df_mrn[df_mrn.FlowsheetMeasureNM == event_id].copy()
            eventname = event_id.replace('R ','').replace(' ','_').lower()
            df_event.rename({'MeasureTXT':eventname}, axis=1, inplace=True)
            df_event.head(5)
            df_event.set_index('RecordedDTS', inplace=True)
            dfs_event.append(df_event[[eventname]])

        df_mrn = dfs_event[0].join(dfs_event[1:], how='outer').sort_index()
        df_mrn['MRN'] = mrn
        df_mrn_s.append(df_mrn.reset_index())

    df_mrn_s = pd.concat(df_mrn_s, sort=True)

    return df_mrn_s



#### LABS:
# i.e. just run data_labs_all_mrns = get_labs(filepath, mrn_s=None, load_raw=True)


def raw_labs_load(filepath):
    '''
    filepath: raw labs output from EDW.
    output: raw data with basic preprocessing done.
    '''
    labs_raw = pd.read_csv(filepath)
    labs_raw = labs_raw.drop_duplicates()
    
    # correct HCO3:
    hco3_unspecified = labs_raw[labs_raw['ComponentCommonNM'] == 'HCO3, UNSPECIFIED'].copy()
    for loc, row in hco3_unspecified.iterrows():
        hco3_unspecified.loc[loc, 'ComponentCommonNM'] = hco3_unspecified.loc[loc, 'ComponentCommonNM'].replace('UNSPECIFIED', hco3_unspecified.loc[loc, 'OrderDisplayNM'].split(' ')[0].upper())

    labs_raw.loc[labs_raw['ComponentCommonNM'] == 'HCO3, UNSPECIFIED', 'ComponentCommonNM'] = hco3_unspecified['ComponentCommonNM'].values
    
    labs_raw.rename({'PatientIdentityID': 'MRN'}, axis=1, inplace=True)
    
    return labs_raw


def get_labs(labs_raw, mrn_s=None, load_raw=False):
    '''
    in:
    labs_raw = raw labs output from EDW after loading it with raw_labs_load() 
    or it can be a filepath, then load_raw must be True.
    mrn_s: list of MRNs. If None: all MRNs in labs_raw,
    output:
    dictionary with MRNs as keys and patient-wise dataframes as values
    '''

    if load_raw:
        labs_raw = raw_labs_load(labs_raw)

    if any([type(mrn_s) == np.int64, type(mrn_s)==float, type(mrn_s)==int]):
        mrn_s = [mrn_s]
    if mrn_s is None: 
        mrn_s = pd.unique(labs_raw.MRN)
    
    data_labs_all_mrns = pd.DataFrame()
    
    for mrn_tmp in mrn_s:
        # for a MRN, get time-index based dataframe containing the labs:
        labs_data_mrn = labs_raw[labs_raw.MRN == mrn_tmp]
        labs_data_df = labs_df(labs_data_mrn)
        
        data_labs_all_mrns = pd.concat([data_labs_all_mrns, labs_data_df], axis=0, sort=True)
        
    if 'index' in data_labs_all_mrns.columns:
        data_labs_all_mrns.drop(['index'], axis=1, inplace=True)

    int_labs = ['hco3_arterial', 'hco3_venous', 'pco2_arterial', 'pco2_venous', 'po2_arterial', 'po2_venous']
    for lab_tmp in int_labs:
        data_labs_all_mrns.loc[pd.isna(data_labs_all_mrns[lab_tmp]), lab_tmp] = -1
        data_labs_all_mrns.loc[:, lab_tmp] = data_labs_all_mrns[lab_tmp].round().astype(np.int32)
        
    return data_labs_all_mrns



def labs_df(data):
    '''
    input: 
    data: raw labs containing the data for a single MRN.
    output:
    lab_data_df: dataframe structure with the containing labs.
    '''
    mrn = pd.unique(data.MRN)
    assert(len(mrn)==1)
    mrn = mrn[0]
    
    labs_data_df = pd.DataFrame([])
    
    labs_contained = pd.unique(data.ComponentCommonNM)
    labs_todo = ['PO2, ARTERIAL', 'PO2, VENOUS',
                   'PCO2, ARTERIAL', 'PCO2, VENOUS',
                   'HCO3, ARTERIAL', 'HCO3, VENOUS',
                   'PH, ARTERIAL', 'PH, VENOUS' ]
    
    for lab_tmp in labs_todo:
        if not lab_tmp in labs_contained: 
            continue
        
        labs_data = data[data.ComponentCommonNM == lab_tmp].copy()
        labs_data.rename({'SpecimenTakenTimeDTS' : 'datetime'}, inplace=True, axis=1)
        labs_data.set_index('datetime', inplace=True)

        new_columns_name = lab_tmp.replace(', ','_').lower()
        labs_data.rename({'ResultValueNBR':new_columns_name}, axis=1, inplace=True)
        labs_data = labs_data[new_columns_name]

        labs_data_df = labs_data_df.join(labs_data, how='outer')
        
    labs_data_df['MRN'] = mrn
    labs_data_df.reset_index(inplace=True)
        
    return labs_data_df


def get_labs_single_mrn(filepath, mrn):

    data_labs_all_mrns = get_labs(filepath, load_raw=1)
    edw_labs = data_labs_all_mrns[data_labs_all_mrns.MRN == mrn].copy()
    edw_labs.drop(['MRN'], axis=1, inplace=True)
    edw_labs.rename({'RecordedDTS': 'datetime'}, axis=1, inplace=True)
    edw_labs.set_index('datetime', inplace=True)
    
    return edw_labs

