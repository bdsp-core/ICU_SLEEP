import pandas as pd

def preprocess_medication_data(df):
    

	# remove columns that are not used in the processing/analysis (currently):
	cols_remove = ['PatientLocationID', 'PatientLocationDSC', 'SiteCD', 'SiteDSC', 'SigTXT_Administered', 'PrescriptionQuantityNBR', 'CommentTxt']
	cols_remove = [x for x in cols_remove if x in df.columns]
	df.drop(cols_remove, axis = 1, inplace = True)

	df['MedicationDSC'] = df['MedicationDSC'].str.lower()
	df = df.drop_duplicates()

	df['MedicationTakenDTS'] = pd.to_datetime(df['MedicationTakenDTS'], infer_datetime_format=1)
	df['OrderStartDTS'] = pd.to_datetime(df['OrderStartDTS'], infer_datetime_format=1)
	df['OrderEndDTS'] = pd.to_datetime(df['OrderEndDTS'], infer_datetime_format=1)
	df = df.sort_values(by='MedicationTakenDTS')

	df.rename({'SigTXT_Order.1': 'SigTXT_Administered'}, axis=1, inplace=True)    
	df.rename({'SigTXT.1': 'SigTXT_Administered'}, axis=1, inplace=True)    
	df.rename({'SigTXT': 'SigTXT_Order'}, axis=1, inplace=True)    

	return df


def remove_non_valid_entries(df, verbose=False):
    

    if verbose: print(f'Remove entries with "Canceled Entry", "Missed", "Return to Cabinet", or ActionSourceDSC!=MAR')
    df = df[df.MARActionDSC != 'Canceled Entry']
    df = df[df.MARActionDSC != 'Missed']
    df = df[df.MARActionDSC != 'Return to Cabinet']
    df = df[df.ActionSourceDSC == 'MAR']  # only use meds entries from medication administration record. i think mainly meds used from 'Anesthesia' are removed.

    if verbose: print(f'Remove entries related to Anesthesia')
    df = df[df.MedicationDiscontinueReasonDSC != 'Anesthesia Stop']
  
    if verbose: print(f"Removing the following ear/eye drop meds: \n {pd.unique(df[df.DoseUnitDSC == 'drop'].MedicationDSC)}.")
    df = df[df.DoseUnitDSC != 'drop']

    if verbose: print(f"Removing the following spray meds: \n {pd.unique(df[df.DoseUnitDSC == 'spray'].MedicationDSC)}.")
    df = df[df.DoseUnitDSC != 'spray']

    if verbose: print(f"Removing the following millicurie-unit meds: \n {pd.unique(df[df.DoseUnitDSC == 'millicurie'].MedicationDSC)}.")
    df = df[df.DoseUnitDSC != 'millicurie']

    if verbose: print("change 'mg of codeine to just mg'")
    df.loc[df.DoseUnitDSC == 'mg of codeine', 'DoseUnitDSC'] = 'mg'
    if verbose: print("change mg of phosphate to just mg")
    df.loc[df.DoseUnitDSC == 'mg of phosphate', 'DoseUnitDSC'] = 'mg'

    if verbose: print('some manual change of composite drugs is done here:')
    # manual change of composite tablets:

    # 'BUTALBITAL-ACETAMINOPHEN-CAFFEINE 50 MG-325 MG-40 MG TABLET'
    tmp_multi = df[df.MedicationDSC == 'BUTALBITAL-ACETAMINOPHEN-CAFFEINE 50 MG-325 MG-40 MG TABLET'.lower()].copy()
    tmp_split1 = tmp_multi.copy()
    tmp_split1.loc[tmp_split1.MedicationDSC == 'BUTALBITAL-ACETAMINOPHEN-CAFFEINE 50 MG-325 MG-40 MG TABLET'.lower(), [
        'MedicationDSC', 'DoseUnitDSC', 'DiscreteDoseAMT']] = ['BUTALBITAL 50 MG tablet'.lower(), 'mg', '50']
    tmp_split2 = tmp_multi.copy()
    tmp_split2.loc[tmp_split2.MedicationDSC == 'BUTALBITAL-ACETAMINOPHEN-CAFFEINE 50 MG-325 MG-40 MG TABLET'.lower(), [
        'MedicationDSC', 'DoseUnitDSC', 'DiscreteDoseAMT']] = ['ACETAMINOPHEN 325 MG tablet'.lower(), 'mg', '325']
    tmp_split3 = tmp_multi.copy()
    tmp_split3.loc[tmp_split3.MedicationDSC == 'BUTALBITAL-ACETAMINOPHEN-CAFFEINE 50 MG-325 MG-40 MG TABLET'.lower(), [
        'MedicationDSC', 'DoseUnitDSC', 'DiscreteDoseAMT']] = ['CAFFEINE 40 MG tablet'.lower(), 'mg', '40']
    df = pd.concat([df, tmp_split1, tmp_split2, tmp_split3], axis=0)

    # 'HYDROCODONE 5 MG-ACETAMINOPHEN 325 MG TABLET'
    tmp_multi = df[df.MedicationDSC == 'HYDROCODONE 5 MG-ACETAMINOPHEN 325 MG TABLET'.lower()].copy()
    tmp_split1 = tmp_multi.copy()
    tmp_split1.loc[tmp_split1.MedicationDSC == 'HYDROCODONE 5 MG-ACETAMINOPHEN 325 MG TABLET'.lower(), [
        'MedicationDSC', 'DoseUnitDSC', 'DiscreteDoseAMT']] = ['HYDROCODONE 5 MG'.lower(), 'mg', '5']
    tmp_split2 = tmp_multi.copy()
    tmp_split2.loc[tmp_split2.MedicationDSC == 'HYDROCODONE 5 MG-ACETAMINOPHEN 325 MG TABLET'.lower(), [
        'MedicationDSC', 'DoseUnitDSC', 'DiscreteDoseAMT']] = ['ACETAMINOPHEN 325 MG tablet'.lower(), 'mg', '325']
    df = pd.concat([df, tmp_split1, tmp_split2], axis=0)

    # 'OXYCODONE-ACETAMINOPHEN 5 MG-325 MG TABLET'
    tmp_multi = df[df.MedicationDSC == 'OXYCODONE-ACETAMINOPHEN 5 MG-325 MG TABLET'.lower()].copy()
    tmp_split1 = tmp_multi.copy()
    tmp_split1.loc[tmp_split1.MedicationDSC == 'OXYCODONE-ACETAMINOPHEN 5 MG-325 MG TABLET'.lower(), [
        'MedicationDSC', 'DoseUnitDSC', 'DiscreteDoseAMT']] = ['OXYCODONE 5 MG'.lower(), 'mg', '5']
    tmp_split2 = tmp_multi.copy()
    tmp_split2.loc[tmp_split2.MedicationDSC == 'OXYCODONE-ACETAMINOPHEN 5 MG-325 MG TABLET'.lower(), [
        'MedicationDSC', 'DoseUnitDSC', 'DiscreteDoseAMT']] = ['ACETAMINOPHEN 325 MG tablet'.lower(), 'mg', '325']
    df = pd.concat([df, tmp_split1, tmp_split2], axis=0)

    if verbose: print('Some Gel or cream-type of meds are removed due to unclear dose.')
    df = df[df.MedicationDSC != 'HYDROCORTISONE 0.5 % TOPICAL CREAM'.lower()]
    df = df[df.MedicationDSC != 'MORPHINE INTRASITE GEL 0.1% CMPD BWH_MGH'.lower()]
    df = df[df.MedicationDSC != 'HYDROCORTISONE 1 % TOPICAL CREAM'.lower()]
    df = df[df.MedicationDSC != 'sodium chloride (pf) (ns) injection']

    if verbose: print('Some meds with non-common doses (mEq, Units, puff, mmoll) are removed, not needed currently.')
    df = df[df.DoseUnitDSC != 'mEq']
    df = df[df.DoseUnitDSC != 'Units']
    df = df[df.DoseUnitDSC != 'Units/kg/hr']
    df = df[df.DoseUnitDSC != 'puff']
    df = df[df.DoseUnitDSC != 'mmol']

    if verbose: print('Some more unclear MedicationDSCs are removed.')
    df = df[df.MedicationDSC != 'potassium, sodium phosphates 280 mg-160 mg-250 mg oral powder packet']
    df = df[df.MedicationDSC != 'insulin regular 100 unit/100 ml (1 unit/ml) in 0.9 % nacl iv solution']

    return df
    
