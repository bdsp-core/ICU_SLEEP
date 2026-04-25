import pandas as pd
import numpy as np

import plotly
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
import plotly.io as pio
from plotly import tools
plotly.io.orca.config.executable  = 'C:/Users/wg984/AppData/Local/conda/conda/envs/plotly3/orca_app/orca.exe'
from plotly.subplots import make_subplots

import os
import datetime
import matplotlib.pyplot as plt
from scipy.signal import correlate
import time


# select subject
# subjectIDsel = 174
# do_crosscorrelation = 0
# do_manual_timeshift = 0
# minutes = 0
# seconds = 0
# remove_durationSec = 0
# remove_start_point = datetime.datetime(2019,5,1,2,41,0)


# later: shiftInSeconds = minutes*60+seconds, therefore both values need to be negative if you want to shift AirGo to the right. 
# looks like recording stop in PSG can still cause troubles, even though EDF+ reader takes those into account. 
# we want to 'shift' time data sometimes from a certain point, e.g. 20 seconds: remove 20 seconds in break of PSG and shift all data after that 20sec 'to the left'.

# time.sleep(60*60)

included_currently = ['001',
 '002',
 '003',
 '004',
 '005',
 '006',
 '007',
 '011',
 '012',
 '013',
 '014',
 '015',
 '016',
 '017',
 '018',
 '019',
 '020',
 '021',
 '022',
 '023',
 '024',
 '025',
 '026',
 '027',
 '028',
 '029',
 '030',
 '031',
 '032',
 '033',
 '034',
 '035',
 '036',
 '037',
 '038',
 '039',
 '040',
 '041',
 '042',
 '043',
 '044',
 '046',
 '047',
 '049',
 '050',
 '051',
 '052',
 '053',
 '054',
 '055',
 '058',
 '059',
 '060',
 '061',
 '062',
 '063',
 '064',
 '065',
 '068',
 '070',
 '071',
 '072',
 '073',
 '074',
 '075',
 '076',
 '077',
 '078',
 '079',
 '080',
 '081',
 '082',
 '083',
 '084',
 '085',
 '086',
 '087',
 '088',
 '089',
 '090',
 '091',
 '092',
 '093',
 '094',
 '095',
 '096',
 '097',
 '098',
 '099',
 '101',
 '102',
 '105',
 '106',
 '107',
 '108',
 '109',
 '110',
 '111',
 '112',
 '113',
 '114',
 '115',
 '116',
 '117',
 '118',
 '119',
 '120',
 '121',
 '122',
 '123',
 '124',
 '125',
 '126',
 '127',
 '128',
 '129',
 '130',
 '132',
 '133',
 '135',
 '136',
 '138',
 '139',
 '140',
 '141',
 '142',
 '143',
 '144',
 '145',
 '146',
 '147',
 '148',
 '149',
 '150',
 '151',
 '152',
 '154',
 '156',
 '157',
 '158',
 '159',
 '160',
 '161',
 '162',
 '163',
 '164',
 '165',
 '166',
 '167',
 '168',
 '169',
 '170',
 '171',
 '172',
 '173',
 '174',
 '175',
 '176',
 '177',
 '178',
 '179',
 '180',
 '181',
 '182',
 '183',
 '184',
 '185',
 '186',
 '187',
 '188',
 '189',
 '190',
 '191',
 '192',
 '193',
 '194',
 '195',
 '196',
 '197',
 '198',
 '199',
 '200',
 '201',
 '202',
 '203',
 '204',
 '205',
 '206',
 '207',
 '208',
 '209',
 '210',
 '211',
 '212',
 '213',
 '214',
 '215',
 '216',
 '217',
 '218',
 '219',
 '220',
 '221',
 '222',
 '223',
 '224',
 '225',
 '226',
 '227',
 '229',
 '230',
 '231',
 '232',
 '233',
 '234',
 '235',
 '237',
 '238',
 '239',
 '240',
 '241',
 '242',
 '243',
 '244',
 '245',
 '246',
 '247',
 '248',
 '249',
 '250',
 '251',
 '252',
 '253',
 '254',
 '255',
 '256',
 '257',
 '258',
 '259',
 '260',
 '261',
 '262',
 '263',
 '264',
 '265',
 '266',
 '267',
 '268',
 '269',
 '270',
 '271',
 '272',
 '273',
 '274',
 '275',
 '276',
 '277',
 '278',
 '280',
 '281',
 '282',
 '283',
 '284',
 '285',
 '286',
 '287',
 '288',
 '289',
 '290',
 '291',
 '292',
 '293',
 '294',
 '295',
 '296',
 '297',
 '298',
 '299',
 '300',
 '301',
 '302',
 '303',
 '304',
 '305',
 '306',
 '307',
 '308',
 '309',
 '310',
 '311',
 '312',
 '313',
 '316',
 '317',
 '318',
 '319',
 '322',
 '323',
 '324',
 '325',
 '326',
 '327',
 '328',
 '329',
 '331',
 '332',
 '333',
 '336',
 '337',
 '338',
 '340',
 '341',
 '342',
 '343',
 '344',
 '346',
 '348',
 '349',
 '350',
 '351',
 '352',
 '353',
 '358',
 '359',
 '360',
 '361',
 '362',
 '364',
 '366',
 '367',
 '368',
 '369',
 '370',
 '371',
 '372',
 '373',
 '374',
 '375',
 '376',
 '377',
 '378',
 '379',
 '381',
 '382',
 '383',
 '384',
 '385',
 '386',
 '401',
 '403',
 '407',
 '409',
 '411',
 '417',
 '419',
 '420',
 '422',
 '423',
 '427',
 '430',
 '433',
 '436',
 '439',
 '440',
 '441',
 '442',
 '443',
 '444',
 '446',
 '447',
 '448',
 '449',
 '452',
 '454',
 '456',
 '460',
 '461',
 '463',
 '464',
 '465']


for subjectID in included_currently: #  range(159, 343): #[subjectIDsel]: #range(163,164):

	try:
	# if 1:

		print(subjectID)

		# savedir = 'C:/Users/wg984/Wolfgang/AirGo_SleepStaging/AirGoFiles_TimeAlignedToPSG/'
		# savedirForPlots = 'C:/Users/wg984/Dropbox (Partners HealthCare)/AirGoSleepLabData/ShareWithDavidKuller/TimeAlignedDataNew/Plots/'
		# savedirForPlots = 'M:/Projects/AirGoSleepStaging/TimeAlignedDataNew/Plots/'
		savedirForPlots = 'C:/Users/wg984/Dropbox (Partners HealthCare)/AirGoSleepLabData/ShareWithDavidKuller/AirGo_PSG_TimeAligned/Plots/'

		strsubjectID = str(subjectID).zfill(3)
		
		# load AirGo file
		AirGoDir = 'C:/Users/wg984/Dropbox (Partners HealthCare)/AirGoSleepLabData/ShareWithDavidKuller/AirGo_PSG_TimeAligned/AirGo_Files/'
		# AirGoDir = 'M:/Projects/AirGoSleepStaging/TimeAlignedDataNew/AirGo_Files/'
		AirGoFile = 'AirGo_'+ strsubjectID +'.csv'
		AirGoData = pd.read_csv( os.path.join(AirGoDir,AirGoFile))

		AirGoData.DateTime = pd.to_datetime(AirGoData.DateTime, infer_datetime_format=1)

		# load PSG file
		PSGDir = 'C:/Users/wg984/Dropbox (Partners HealthCare)/AirGoSleepLabData/ShareWithDavidKuller/AirGo_PSG_TimeAligned/PSG_Files/'
		# PSGDir = 'M:/Projects/AirGoSleepStaging/TimeAlignedDataNew/PSG_Files/'
		PSGFile = 'PSG_Air' + strsubjectID + '_10Hz.csv'
		PSGData = pd.read_csv( os.path.join(PSGDir,PSGFile))
		PSGData.DateTime = pd.to_datetime(PSGData.DateTime, infer_datetime_format=1)

		PSGStartTime = PSGData.DateTime.iloc[0]
		PSGEndTime = PSGData.DateTime.iloc[-1]


		# fig = tools.make_subplots(rows=3, cols=1, shared_xaxes=True, shared_yaxes=False) # , subplot_titles=('HR', 'BP diastolic')

		fig = make_subplots(rows=3, cols=1, shared_xaxes=True, shared_yaxes=False, specs=[[{"secondary_y": True}], [{"secondary_y": False}], [{"secondary_y": False}]] )

		traces = []

		trace_ABD = go.Scattergl(x=PSGData.DateTime, y=PSGData.ABD, name = 'ABD', hoverinfo = 'x+y', line = dict(color = 'blue', width = 1), opacity = 0.8 )
		trace_CHEST = go.Scattergl(x=PSGData.DateTime, y=PSGData.CHEST, name = 'CHEST', hoverinfo = 'x+y', line = dict(color = 'green', width = 1), opacity = 0.8 )

		trace_AirGo = go.Scattergl(x=AirGoData.DateTime, y=AirGoData.Band, name = 'AirGo', hoverinfo = 'x+y', line = dict(color = 'orange', width = 1), opacity = 0.8 )

		trace_Apnea = go.Scatter(x=PSGData.DateTime, y=PSGData.Apnea, name = 'Apnea', hoverinfo = 'x+y', line = dict(color = 'DeepSkyBlue', width = 1), opacity = 0.8 )
		trace_Sleep = go.Scatter(x=PSGData.DateTime, y=PSGData.Stage, name = 'Stage', hoverinfo = 'x+y', line = dict(color = 'Crimson', width = 1), opacity = 0.8 )


		fig.add_trace(trace_Sleep, 1, 1)
		fig.add_trace(trace_Apnea, 1, 1, secondary_y=True)

		fig.add_trace(trace_AirGo, 2, 1)

		fig.add_trace(trace_ABD, 3, 1)
		fig.add_trace(trace_CHEST, 3, 1)

		fig['layout']['yaxis2'].update(tickvals=[1,2,3,4,5,6], ticktext =['OA', 'CA', 'MA', 'HY', '', 'RA' ], color = 'DeepSkyBlue')
		fig['layout']['yaxis1'].update(tickvals=[5,4,3,2,1], ticktext =['W','R','N1','N2','N3'], color = 'Crimson')
		fig['layout']['autosize'] = True

		plot(fig,  auto_open=False, filename = savedirForPlots+'AirGo_PSG_Annot_' + strsubjectID + '.html')

		# AirGoData.to_csv( os.path.join(savedir,'AirGo_'+strsubjectID+'.csv'), index=False)

	except:
		print('error for this one')
		continue