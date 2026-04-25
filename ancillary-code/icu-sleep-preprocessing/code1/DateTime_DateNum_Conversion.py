from datetime import datetime
from datetime import timedelta
import time 
from time import mktime
import pytz


def DateTime_to_DateNum(DateTimeList, localDateNum = 1):
	# input: list of timestamps / datetimes.

	localtime = pytz.timezone('US/Eastern')
	dateNumOffset = 719529 # 1.1.1970 in datenum
	
	LocalDateNumList = []

	for dateTime in DateTimeList:
		# convert to unix time:
		unixTime = dateTime.timestamp()
		#convert to DateNum:
		datenum =  unixTime /86400 + dateNumOffset

		# convert to 'local DateNum' (this is because the DateNum in the bedmaster files are converted directly from EST/EDT local time, not UTC. (matlab actually defines
		# DateNum implicitly on UTC))
		# i.e. in bedmaster files: from time zone EST (UTC -5) or EDT/DST (UTC -4)

		if localDateNum:
			dateTimeLocalized = localtime.localize(dateTime)
			# check if dateTime in DayLightSavingTime.
			if bool(dateTimeLocalized.dst()):
				LocalDateNumList.append(datenum - 4/24)		# DST
			else:
				LocalDateNumList.append(datenum - 5/24)		# EST

	return LocalDateNumList

					# # convert to unix time:
					# UnixList = 	[mktime(t.timetuple()) for t in DateTimeList]

					# #convert to DateNum:
					# DateNumList = [unixT /86400 + dateNumOffset for unixT in UnixList]


def DateNum_to_DateTime(DateNumList, localDateNum = 1):

    # !!! assumes DateNum is in 'local DateNum', i.e. transformed from EST/EDT.
	
	localtime = pytz.timezone('US/Eastern')
	dateNumOffset = 719529

	# to unix
	UnixList = [(datenum -  dateNumOffset) * 86400 for datenum in DateNumList]

    #     # to datetime 
	DateTimeList = [ datetime.fromtimestamp( unixT ) for unixT in UnixList ]

    # local time correction for local datenum:
	if localDateNum:
		DateTimeListCorrection = []
		for dateTime in DateTimeList:
			dateTimeLocalized = pytz.timezone('US/Eastern').localize(dateTime)
			# check if dateTime in DayLightSavingTime.
			if bool(dateTimeLocalized.dst()):
				DateTimeListCorrection.append(dateTimeLocalized + timedelta(hours = 4))		# DST
			else:
				DateTimeListCorrection.append(dateTimeLocalized + timedelta(hours = 5))     # EST
		DateTimeList = DateTimeListCorrection
     
    
	return DateTimeList
