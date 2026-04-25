import hl7
import pymssql as p
import pandas as pd
import hive_config

# These are the connection settings for our Hive Database
host = hive_config.host1
database = hive_config.database1
username = hive_config.user
password = hive_config.password1

print("DB CONNECT ATTEMPT")

connection = p.connect(host=host,
                       user=username,
                       password=password,
                       database=database)

d = 1
o = 1
c1 = 1

dev = pd.DataFrame(columns=['msh3_sender_app', 'msh4_sender_fac', 'msh7_ts', 'msh9_msgType', 'msh10_controlID',
                            'msh11_procID', 'msh12_version', 'msh18_charset', 'msh21_msgProfID', 'pv1_3_ptLoc',
                            'obr2_PlacerOrdNum', 'obr3_FillerOrdNum', 'obr4_UnivID', 'obr7_obs_ts', 'obr10_collectorID', ])

obx = pd.DataFrame(columns=['msh3_sender_app', 'msh4_sender_fac', 'msh7_ts', 'obr2_PlacerOrdNum', 'obr3_FillerOrdNum',
                            'obr4_UnivID', 'obr7_obs_ts', 'obr10_collectorID', 'obx2_vType', 'obx3_id', 'obx3_dsc',
                            'obx4_subID', 'obx5_value', 'obx6_units', 'obx11_status', 'obx14_obs_ts', 'obx18_EqInstanceID'])

cursor = connection.cursor(as_dict=True)
cursor.execute('SELECT TOP 10000 * FROM [HL7Receiver-ORU].dbo.Hl7Message')

row = cursor.fetchone()

for row in cursor:
    h = hl7.parse(row['MessagePayload'])

    print(h.segments('MSH')[0][4])

    # get device information

    # try:
    #     dev_name = h.segments('OBR')[0][10][0]
    #     dev_orign = 0
    # except IndexError:
    #     dev_name = h.segments('PV1')[0][3][0]
    #     dev_orign = 1
    #     pass
    #
    # if dev_name in dev.values:
    #     if dev_orign == 0:
    #         ind = int(dev[dev['obr10_collectorID'] == h.segments('OBR')[0][10][0]].index[0])
    #     else:
    #         ind = int(dev[dev['pv1_3_ptLoc'] == h.segments('PV1')[0][3][0]].index[0])
    #     dev.at[ind, 'msh_count'] += 1
    # else:
    dev.at[d, 'msh3_sender_app'] = h.segments('MSH')[0][3][0]
    dev.at[d, 'msh4_sender_fac'] = h.segments('MSH')[0][4][0]
    dev.at[d, 'msh7_ts'] = hl7.parse_datetime(h.segments('MSH')[0][7][0])
    dev.at[d, 'msh9_msgType'] = h.segments('MSH')[0][9][0]
    dev.at[d, 'msh10_controlID'] = h.segments('MSH')[0][10][0]
    dev.at[d, 'msh11_procID'] = h.segments('MSH')[0][11][0]

    try:
        dev.at[d, 'msh12_version'] = h.segments('MSH')[0][12][0]
    except IndexError:
        pass
    try:
        dev.at[d, 'msh18_charset'] = h.segments('MSH')[0][18][0]
    except IndexError:
        pass
    try:
        dev.at[d, 'msh21_msgProfID'] = h.segments('MSH')[0][21][0]
    except IndexError:
        pass
    try:
        dev.at[d, 'pv1_3_ptLoc'] = h.segments('PV1')[0][3][0]
    except IndexError:
        pass

    dev.at[d, 'obr2_PlacerOrdNum'] = h.segments('OBR')[0][2][0]
    dev.at[d, 'obr3_FillerOrdNum'] = h.segments('OBR')[0][3][0]
    dev.at[d, 'obr4_UnivID'] = h.segments('OBR')[0][4][0]
    dev.at[d, 'obr7_obs_ts'] = hl7.parse_datetime(h.segments('OBR')[0][7][0])

    try:
        dev.at[d, 'obr10_collectorID'] = h.segments('OBR')[0][10][0]
    except IndexError:
        pass
    #    dev.at[d,'msh_count'] = 1
    d += 1
    print(d)

    # get OBX information
    obl = len(h.segments('OBX'))

    i = 0
    while i < obl:
        # if h.segments('OBX')[i][3][0][1][0] in obx.values:
        #     ind = int(obx[obx['obx3_dsc'] == h.segments('OBX')[i][3][0][1][0]].index[0])
        #     obx.at[ind, 'obx3_count'] += + 1
        # else:
        obx.at[o, 'msh3_sender_app'] = h.segments('MSH')[0][3][0]
        obx.at[o, 'msh4_sender_fac'] = h.segments('MSH')[0][4][0]
        obx.at[o, 'msh7_ts'] = hl7.parse_datetime(h.segments('MSH')[0][7][0])
        obx.at[o, 'obr2_PlacerOrdNum'] = h.segments('OBR')[0][2][0]
        obx.at[o, 'obr3_FillerOrdNum'] = h.segments('OBR')[0][3][0]
        obx.at[o, 'obr4_UnivID'] = h.segments('OBR')[0][4][0]
        obx.at[o, 'obr7_obs_ts'] = hl7.parse_datetime(h.segments('OBR')[0][7][0])
        try:
            obx.at[o, 'obr10_collectorID'] = h.segments('OBR')[0][10][0]
        except IndexError:
            pass
        obx.at[o, 'obx2_vType'] = h.segments('OBX')[i][2][0]
        obx.at[o, 'obx3_id'] = h.segments('OBX')[i][3][0][0][0]
        obx.at[o, 'obx3_dsc'] = h.segments('OBX')[i][3][0][1][0]
        obx.at[o, 'obx4_subID'] = h.segments('OBX')[i][4][0]
        obx.at[o, 'obx5_value'] = h.segments('OBX')[i][5][0]
        try:
            obx.at[o, 'obx6_units'] = h.segments('OBX')[i][6][0][0][0]
        except IndexError:
            pass
        try:
            obx.at[o, 'obx11_status'] = h.segments('OBX')[i][11][0][0][0]
        except IndexError:
            pass
        try:
            obx.at[o, 'obx14_obs_ts'] = hl7.parse_datetime(h.segments('OBX')[0][14][0])
        except IndexError:
            pass
        try:
            obx.at[o, 'obx18_EqInstanceID'] = h.segments('OBX')[i][18][0]
        except IndexError:
            pass
        o += 1
        i += 1

connection.close()

dev.to_csv('dev_all.csv', index=False)
obx.to_csv('obx_all.csv', index=False)

print(dev)
print(obx)
