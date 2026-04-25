#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import path_config

pd.options.display.max_columns = 999
pd.options.display.max_columns = 999

import pyodbc
conn1 = pyodbc.connect(driver=path_config.edw_vitals_lab_meds_driver1, TDS_version=path_config.edw_vitals_lab_meds_TDS_version1, host=path_config.edw_vitals_lab_meds_host1, user=path_config.edw_vitals_lab_meds_user1, pwd=path_config.edw_vitals_lab_meds_pwd1)
cursor1 = conn1.cursor()

conn2 = pyodbc.connect(driver=path_config.edw_vitals_lab_meds_driver2, TDS_version=path_config.edw_vitals_lab_meds_TDS_version2, host=path_config.edw_vitals_lab_meds_host2, user=path_config.edw_vitals_lab_meds_user2, pwd=path_config.edw_vitals_lab_meds_pwd2)
cursor2 = conn2.cursor()

print(pyodbc.version)

# all results will be saved as edw_{cohort_name}_{vitals, labs, meds}.csv
cohort_name = path_config.edw_vitals_lab_meds_cohort_name

df = pd.read_csv(path_config.path_cohort)
df.loc[df['Study ID:'] == path_config.edw_vitals_lab_meds_StudyID1, 'MRN:'] = path_config.edw_vitals_lab_meds_MRN1
df.loc[df['Study ID:'] == path_config.edw_vitals_lab_meds_StudyID2, 'MRN:'] = path_config.edw_vitals_lab_meds_MRN2
df.loc[df['Study ID:'] == path_config.edw_vitals_lab_meds_StudyID3, 'MRN:'] = path_config.edw_vitals_lab_meds_MRN3
df['mrn'] = df['MRN:']
mrn_s = ','.join(df['MRN:'].dropna().map(int).map(str).apply(lambda e: "'"+e.zfill(7)+"'").tolist())

mrn_s_list = df['mrn'].dropna().map(int).map(str).apply(lambda x: str(x).zfill(7)).tolist()

df.tail(3)

# len(df.mrn.unique())
df = df.dropna(how='all', axis=0, subset=['mrn'])
len(df['mrn'])

mrn_s;

query_demographics1 = """
SELECT t2.PatientIdentityID as MRN, t1.[PatientID], [PatientStatusCD], [PatientStatusDSC], [PatientNM], [BirthDTS],
                               [DeathDTS], [PatientRaceCD], [PatientRaceDSC], [EthnicGroupCD], [EthnicGroupDSC],
                               [LanguageCD], [LanguageDSC], [MaritalStatusCD], [MaritalStatusDSC], [SexCD],
                               [SexDSC], [AddressLine01TXT], [CityNM], [StateCD], [StateDSC],
                               [CountyCD], [CountyDSC], [CountryCD], [CountryDSC], [ZipCD]  
        FROM [Epic].[Patient].[Patient_MGH] t1  
        inner join epic.Patient.Race_MGH t11 on t1.PatientID=t11.PatientID    
        left join epic.Patient.Identity_MGH t2 on  (t1.PatientID=t2.PatientID  and t2.IdentityTypeID=67 )   
        where  t2.PatientIdentityID in ({}) 
      """.format(mrn_s)

df_demographics1 = pd.read_sql_query(query_demographics1, conn1)
df_demographics1.to_csv('edw_' + cohort_name + '_' + 'demographics.csv', index=False)
df_demographics1.head(3)

print(f'# of MRNs input: {len(df.mrn.unique())}')
print(f'# of MRNs found: {len(df_demographics1.MRN.unique())}')
print(f'MRNs not found: {set(mrn_s_list) - set(df_demographics1.MRN.values)}')

df_demographics1.sort_values(by='MRN')

query_vitals1 = """SELECT MRN,PatientID,PatientEncounterID,table2.InpatientDataID, table2.DepartmentID, FlowsheetDataID, FlowsheetMeasureID, FlowsheetMeasureNM, RecordedDTS, MeasureTXT
    FROM
    (SELECT  distinct t5.InpatientDataID,t4.FlowsheetDataID,t4.FlowsheetMeasureID,t4.RecordedDTS,t4.MeasureTXT,t6.FlowsheetMeasureNM
      FROM [Epic].[Clinical].[FlowsheetMeasure_MGH] t4
      INNER join Epic.Clinical.FlowsheetRecordLink_MGH t5 on t4.FlowsheetDataID=t5.FlowsheetDataID
      INNER join Epic.Clinical.FlowsheetGroup_MGH t6 on t4.FlowsheetMeasureID=t6.FlowsheetMeasureID
      WHERE  t4.FlowsheetMeasureID = '10' or t4.FlowsheetMeasureID = '11' or t4.FlowsheetMeasureID = '14' or t4.FlowsheetMeasureID = '5'
      or t4.FlowsheetMeasureID = '8' or t4.FlowsheetMeasureID = '9'  or t4.FlowsheetMeasureID = '61' or t4.FlowsheetMeasureID = '6' or t4.FlowsheetMeasureID = '61' or t4.FlowsheetMeasureID = '301260'
      or t4.FlowsheetMeasureID in ('3040600350', '3040900001', '3040900007', '3040900287', '160301', '160302', '160341', '160342', '160343', '160346', '160347', '160348', '160350', '160351', '3040101407', '3040950006', '304220020',
        '304220021','304220022', '304220023', '304220024', '304220025', '304220026', '304220028', '304220029', '304220030', '304220031', '401000', '401001', '301070', '2103010701', '7')
    ) table1
    inner join
    (SELECT  distinct t2.PatientID, t2.DepartmentID, InpatientDataID,PatientEncounterID,PatientIdentityID as MRN
     FROM [Epic].[Clinical].[InpatientDataStore_MGH] t1
     INNER join Epic.Encounter.ADT_MGH t2 on (t1.GenericPatientDatabaseCSNID=t2.PatientEncounterID)
     INNER join Epic.Patient.Identity_MGH t3 on (t2.PatientID=t3.PatientID and IdentityTypeID=67)
    ) table2
    on table1.InpatientDataID=table2.InpatientDataID
    where MRN in ({}) 
    """.format(mrn_s)

df_vitals1 = pd.read_sql_query(query_vitals1, conn1)

df_vitals1.head(3)

df_vitals1.to_csv('edw_' + cohort_name + '_' + 'vitals.csv', index=False)

print(f'# of MRNs input: {len(df.mrn.unique())}')
print(f'# of MRNs found: {len(df_vitals1.MRN.unique())}')
print(f'MRNs not found: {set(mrn_s_list) - set(df_vitals1.MRN.values)}')


# flowsheets is actually the vitals query but with additional items AFAIK.

query_flowsheets1 = """
SELECT MRN, PatientID, PatientEncounterID, table2.InpatientDataID, table2.DepartmentID, FlowsheetDataID, FlowsheetMeasureID, FlowsheetMeasureNM, RecordedDTS, MeasureTXT
    FROM 
    (SELECT  distinct t5.InpatientDataID,t4.FlowsheetDataID,t4.FlowsheetMeasureID,t4.RecordedDTS,t4.MeasureTXT,t6.FlowsheetMeasureNM
      FROM [Epic].[Clinical].[FlowsheetMeasure_MGH] t4 
      INNER join Epic.Clinical.FlowsheetRecordLink_MGH t5 on t4.FlowsheetDataID=t5.FlowsheetDataID
      INNER join Epic.Clinical.FlowsheetGroup_MGH t6 on t4.FlowsheetMeasureID=t6.FlowsheetMeasureID
      WHERE  t4.FlowsheetMeasureID in  ('3040600350', '3040900001', '3040900007', '3040900287', '160301', '160302', 
                                        '160341', '160342', '160343', '160346', '160347', '160348', '160350', '160351', 
                                        '3040101407', '3040950006', '304220020', '304220021', '304220022', '304220023', 
                                        '304220024', '304220025', '304220026', '304220028', '304220029', '304220030', 
                                        '304220031', '401000', '301070', '2103010701', '7', '3042300800', '29597',
                                        '1040129598', '301360', '8', '9', '301250', '301260', '10', '5', '6', '301640',
                                        '301550', '301570', '301620', '401001', '61', '11', '14')        
    ) table1
    inner join
    (SELECT  distinct t2.PatientID, t2.DepartmentID, InpatientDataID,PatientEncounterID,PatientIdentityID as MRN
    FROM [Epic].[Clinical].[InpatientDataStore_MGH] t1 
    INNER join Epic.Encounter.ADT_MGH t2 on (t1.GenericPatientDatabaseCSNID=t2.PatientEncounterID)
    INNER join Epic.Patient.Identity_MGH t3 on (t2.PatientID=t3.PatientID and IdentityTypeID=67)
    ) table2
    on table1.InpatientDataID=table2.InpatientDataID 
    where MRN in ({}) 
    """.format(mrn_s)


df_flowsheets1 = pd.read_sql_query(query_flowsheets1, conn1)
df_flowsheets1.to_csv('edw_' + cohort_name + '_' + 'flowsheets.csv', index=False)

query_labs1 = '''
SELECT  t4.ComponentID,t1.ProcedureDSC,t3.PatientIdentityID,
        t1.[PatientID],t1.[PatientEncounterID],t1.[OrderProcedureID],
        t1.[OrderingDTS],t1.[OrderDTS],t1.[OrderTimeDTS],t1.[StartDTS],
        t1.[EndDTS],t2.[ResultDateDTS],t1.[ResultDTS],[OrderTypeCD],
        t1.[OrderTypeDSC],t1.[OrderDisplayNM],t1.[ProcedureID],t1.[ProcedureDSC],
        t2.[ComponentID], t2.[ComponentCommentTXT],
        t4.ComponentNM,t4.ComponentCommonNM,t2.ResultTXT,t2.[ResultValueNBR],t4.LOINCTXT,
        t1.[LabStatusDSC],t1.[OrderStatusDSC],t2.[ReferenceRangeUnitCD],t2.[ResultStatusDSC],t2.[LabTechnicianID],
        t2.[DataTypeCD],t2.[DataTypeDSC],t2.[ComponentObservedDTS],t5.[SpecimenReceivedTimeDTS],t5.[SpecimenTakenTimeDTS],t5.[SpecimenCommentsTXT]
        FROM [Epic].[Orders].[Procedure_MGH] t1
        inner join Epic.Orders.Result_MGH t2 on t1.OrderProcedureID = t2.OrderProcedureID
        inner join Epic.Patient.Identity_MGH t3 on t3.PatientID=t1.PatientID and t3.IdentityTypeID = 67
        inner join epic.Reference.Component t4 on t2.ComponentID=t4.ComponentID
        inner join Epic.Orders.Procedure2_MGH t5 on t1.OrderProcedureID = t5.OrderProcedureID
        where t3.PatientIdentityID in ({})
        '''.format(mrn_s)


df_labs1 = pd.read_sql_query(query_labs1, conn1)

df_labs1.head(3)

df_labs1.to_csv('edw_' + cohort_name + '_' + 'labs.csv', index=False)

# query_meds1 = '''
# SELECT  t1.[OrderID],t2.PatientIdentityID as MRN,t1.[PatientEncounterID], t1.MedicationID, t1.MedicationDSC,
#             t1.OrderInstantDTS,t1.OrderStartDTS,t1.OrderEndDTS,t1.DoseUnitCD, t1.DoseUnitDSC, t1.MinimumDoseAMT,
#             t1.MaximumDoseAMT,t1.PatientLocationID, t1.PatientLocationDSC,t3.MedicationTakenDTS,t3.MARActionCD,
#             t3.MARActionDSC, t3.RouteDSC, t3.RouteCD,t3.[SiteCD],t3.[SiteDSC],t3.[InfusionRateNBR],t3.[InfusionRateUnitCD],
#             t3.[InfusionRateUnitDSC],t3.[DurationNBR],t3.[DurationUnitCD],t3.[DurationUnitDSC], t3.[]
#             t1.SigTXT,t1.PrescriptionQuantityNBR,MedicationDiscontinueReasonDSC,DiscreteFrequencyDSC,
#             DiscreteDoseAMT,DiscreteDispenseUnitDSC
#             FROM [Epic].[Orders].[Medication_MGH] t1
#             inner join Epic.Patient.Identity_MGH t2 on (t1.PatientID = t2.PatientID and t2.IdentityTypeID = 67)
#             left join Epic.Clinical.AdministeredMedication_MGH t3 on t1.OrderID=t3.OrderID
#             where t1.OrderStatusCD  in (5,2,9,10) and t2.PatientIdentityID in ({})
#             '''.format(mrn_s)

query_meds1 = '''
SELECT  t1.[OrderID],t2.PatientIdentityID as MRN,t1.[PatientEncounterID], t1.MedicationID, t1.MedicationDSC,
        t1.OrderInstantDTS,t1.OrderStartDTS,t1.OrderEndDTS,t1.DoseUnitCD, t1.DoseUnitDSC, t1.MinimumDoseAMT,
        t1.MaximumDoseAMT,t1.PatientLocationID, t1.PatientLocationDSC,t3.MedicationTakenDTS,t3.MARActionCD,
        t3.MARActionDSC, t3.RouteDSC, t3.RouteCD,t3.[SiteCD],t3.[SiteDSC],t3.[InfusionRateNBR],t3.[InfusionRateUnitCD],
        t3.[InfusionRateUnitDSC],t3.[DurationNBR],t3.[DurationUnitCD],t3.[DurationUnitDSC], t3.[ActionSourceDSC],
        t3.[CommentTxt], t3.[DefinedDailyDoseNBR], t3.[SigTXT],
        t1.SigTXT,t1.PrescriptionQuantityNBR,MedicationDiscontinueReasonDSC,DiscreteFrequencyDSC,
        DiscreteDoseAMT,DiscreteDispenseUnitDSC
        FROM [Epic].[Orders].[Medication_MGH] t1
        inner join Epic.Patient.Identity_MGH t2 on (t1.PatientID = t2.PatientID and t2.IdentityTypeID = 67)
        left join Epic.Clinical.AdministeredMedication_MGH t3 on t1.OrderID=t3.OrderID
        where t1.OrderStatusCD  in (5,2,9,10) and t2.PatientIdentityID in ({})
        '''.format(mrn_s)


df_meds1 = pd.read_sql_query(query_meds1, conn1)
# df_meds1.rename({'SigTXT': 'SigTXT_Order', 'SigTXT.1': 'SigTXT_Administered'}, axis=1, inplace=True)

df_meds1.head()

df_meds1.to_csv('edw_' + cohort_name + '_' + 'meds.csv', index=False)

# query_meds2 = '''
# SELECT  *
#             FROM [Epic].[Orders].[Medication_MGH] t1
#             inner join Epic.Patient.Identity_MGH t2 on (t1.PatientID = t2.PatientID and t2.IdentityTypeID = 67)
#             left join Epic.Clinical.AdministeredMedication_MGH t3 on t1.OrderID=t3.OrderID
#             where t1.OrderStatusCD  in (5,2,9,10) and t2.PatientIdentityID in ({})
#             '''.format(mrn_s)
# df_meds2=pd.read_sql_query(query_meds2,conn1)
# df_meds2.to_csv('meds_v2_full_extraction.csv')


# --------------------------------------------------------
# --- ADT SQL
# --- PatientID is also referred to as Z-iD, it is the MGB information system's unique ID assigned to a patient, MRN - used in MGH could be different from BWH MRN.
# --- PatientEncounterID is also called the CSN, it is an unique assigned to each Admission visit (however, it doesn't represent an unique visit/stay anymore because departments/specialty have implemented consults as "Admission")

# --- Within data query selection is made within  - this can be changed to MRN, PatientEncounterID or PatientID (Z-number)
# --- t1.PatientEncounterID in 
# ---            (SELECT distinct [PatientEncounterID] 
# ---            FROM [Epic].[Encounter].[ADT_MGH] 
# ---            where (EffectiveDTS>= '2016-04-01' and EffectiveDTS<='2016-04-03'  ) )

# --- PatientIdentityID is the commonly referred to MRN, it is only unique to MGH
# --- bench time 2 minutes for time range of 1 month
# --- 589778 records, 
query_adt1 = """
SELECT [EventID], [ADTEventTypeDSC], [ADTEventSubtypeDSC], [DepartmentID], [DepartmentDSC], [RoomID], [BedID], [EffectiveDTS],
       ADT.[PatientID], PID.PatientIdentityID as MRN, ADT.[PatientEncounterDateRealNBR], ADT.[PatientEncounterID],
       [PatientClassCD], [PatientClassDSC], [PatientServiceCD], [PatientServiceDSC], ADT.[AccommodationCD], Acc.AccommodationDSC,
       [AccommodationReasonDSC], [PatientSummaryTypeCD], [PatientSummaryTypeDSC], [FromBaseClassCD], [FromBaseClassDSC], [ToBaseClassCD],
       [ToBaseClassDSC], iso.IsolationDSC as IsolationStatus, iso.IsolationAddedDTS as IsolationStartDTS, iso.IsolationRemovedDTS as IsolationEndDTS
  FROM [Epic].[Encounter].[ADT_mgh] ADT
  left join (select distinct AccommodationCD, AccommodationDSC
                From Epic.Encounter.PatientEncounterHospital_mgh) Acc On ADT.AccommodationCD = Acc.AccommodationCD
    join [Epic].[Patient].[Identity_MGH] PID ON PID.PatientID = ADT.PatientID and PID.IdentityTypeID = 67
    Left JOIN [Epic].[Encounter].[HospitalIsolation_MGH] iso
            on iso.PatientEncounterID = ADT.PatientEncounterID
  Where ADT.ADTEventSubtypeCD != 2 AND  PID.PatientIdentityID in ({}) 
      """.format(mrn_s)


df_adt1 = pd.read_sql_query(query_adt1, conn1)

df_adt1.to_csv('edw_' + cohort_name + '_' + 'adt.csv', index=False)

print(df_adt1.MRN.unique().shape)
