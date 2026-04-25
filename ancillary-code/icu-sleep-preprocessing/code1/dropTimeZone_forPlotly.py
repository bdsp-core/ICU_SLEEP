# drop time zone information. at this point, plotly does not support timezone specific plots, i.e. always transforms datetime to UTC. 
# therefore, for now, strip the information of local time zone. needs to be checked if data of a patient is during switch of timezone (daylight saving time).
import pandas as pd
import numpy as np
from datetime import datetime
from datetime import timedelta

def dropTimeZone(df_column):

	df_column.dt.tz_localize(None)

	return df_column

def AddNaNs(signalData, signalName):
	signalData = signalData.reset_index()
	IdxLargeTimeDif = np.where(signalData.datetime.diff() > timedelta(hours = 0.5))[0] - 1
	for idx in IdxLargeTimeDif:
		DataLargeTimeDif = signalData.iloc[idx,:]
		NaNData = pd.DataFrame([[None,DataLargeTimeDif.datetime + timedelta(seconds = 1)]], columns = [signalName,'datetime'])
		signalData = signalData.append(NaNData,ignore_index=False, sort = False)

	signalData.sort_values(by=['datetime'], inplace = True)
	signalData = signalData.set_index('datetime')
	return signalData