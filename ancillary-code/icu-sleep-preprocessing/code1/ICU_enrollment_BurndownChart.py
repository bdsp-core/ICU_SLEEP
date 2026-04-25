import pandas as pd
import numpy as np
import matplotlib as plt
import datetime 
import plotly
import plotly.graph_objs as go
from plotly.offline import plot
from plotly import tools
import re

# read in exported redcap report, called consent date enrolled date, floor 1 date AM in redcap
consent = pd.read_csv('ICUSLEEP-ConsentDateEnrolledD_DATA_LABELS.csv')
consent.columns = consent.columns.str.strip()
consent.columns = ['Study ID:', 'Event Name', 'Repeat Instrument', 'Repeat Instance',
       'Consenting Date & Time', 'Evaluation Date and Time', 'First Day Enrolled in Study:']

# grab the dates of enrollment
enrollment_dates = pd.DataFrame(columns=['date'])
for study_id in np.unique(consent['Study ID:']):
    consent_id = consent.loc[consent['Study ID:'] == study_id,:]
    all_dates = consent_id['Consenting Date & Time'].dropna().values.tolist() + consent_id['Evaluation Date and Time'].dropna().values.tolist() + consent_id['First Day Enrolled in Study:'].dropna().values.tolist()
    if len(all_dates) == 0: continue
    date_id = pd.to_datetime(all_dates[0], infer_datetime_format=1) # .date()
    enrollment_dates.loc[study_id, 'date'] = date_id
    
enrollment_dates.drop('98a', inplace=True)

enrollment_dates = enrollment_dates.sort_values('date')
enrollment_dates['EnrollmentNo'] = np.arange(1,len(enrollment_dates)+1)
consent = enrollment_dates

# keep an approximate list of study ids that are probably not included in analysis (mostly patients who never got drug)
not_in_study = ['22','26', '30', '42', '44', '53', '56', '70', '89', '109', '118', '123', '162']

# end of study timeline
start = consent['date'].iloc[0]
June2022 = pd.Timestamp('2022-06-01 10:00:00')
End2021 = pd.Timestamp('2022-01-01 10:00:00')
trace_End2021 = go.Scatter(x=[start,End2021], y=[0,750], name = '750 until end of 2021', hoverinfo = 'x+y')
trace_June2022 = go.Scatter(x=[start,June2022], y=[0,750], name = '750 until June 2022', hoverinfo = 'x+y')

# get the enrollment timeseries
currentDate = datetime.datetime.now()
traceEnrollment = go.Scatter(x=pd.concat([consent['date'],pd.Series(currentDate)]), y=pd.concat([consent['EnrollmentNo'],pd.Series(consent['EnrollmentNo'].iloc[-1])]), name = 'enrollment', hoverinfo = 'x+y')

currentEnrollment = consent.iloc[-1,:].EnrollmentNo

FutureDate = np.array([currentDate + datetime.timedelta(days = 7*iWeeks) for iWeeks in range(52*4)])
FutureEnrollment4perWeek = np.array([currentEnrollment + 4*iWeeks for iWeeks in range(52*4)])
FutureEnrollment5perWeek = np.array([currentEnrollment + 5*iWeeks for iWeeks in range(52*4)])

trace_4perWeek = go.Scatter(x=FutureDate[FutureEnrollment4perWeek<=754], y=FutureEnrollment4perWeek[FutureEnrollment4perWeek<=754], name = '4 per week', hoverinfo = 'x+y',
                         line = dict(
            dash = 'dashdot',
            width = 2,
            color = 'red'
        ),
                           )
trace_5perWeek = go.Scatter(x=FutureDate[FutureEnrollment5perWeek<=755], y=FutureEnrollment5perWeek[FutureEnrollment5perWeek<=755], name = '5 per week', hoverinfo = 'x+y',
                           line = dict(
            dash = 'dashdot',
            width = 2,
            color = 'green'
        ),
             )

trace_750subjects = go.Scatter(x=[start, pd.Timestamp('2022-11-01 10:00:00')], y=[750, 750], line = dict(
            width = 2,
            color = 'rgb(122, 122, 122)'
        ), name = 'enrollment goal = 750', hoverinfo = 'x+y' )

### compute weekly enrollment rate for last week and last month:

EnrollmentsLastWeek = np.sum((consent['date'] >= pd.Timestamp(currentDate.date() - datetime.timedelta(hours = 7*24))).values)
EnrollmentsLastMonth = np.sum((consent['date'] >= pd.Timestamp(currentDate.date() - datetime.timedelta(hours = 4*7*24))).values)
EnrollmentsLast3Months = np.sum((consent['date'] >= pd.Timestamp(currentDate.date() - datetime.timedelta(hours = 3*4*7*24))).values)
EnrollmentRateLastWeek = EnrollmentsLastWeek
EnrollmentRateLastMonth = EnrollmentsLastMonth/4
EnrollmentRateLast3Months = EnrollmentsLast3Months/12

FutureEnrollmentAsAverageLast4Weeks = np.array([currentEnrollment + EnrollmentRateLastMonth*iWeeks for iWeeks in range(52*4)])
FutureEnrollmentAsAverageLast12Weeks = np.array([currentEnrollment + EnrollmentRateLast3Months*iWeeks for iWeeks in range(52*4)])

plot_average = '12weeks'
if plot_average == '12weeks':
    trace_asAverage = go.Scatter(x=FutureDate[FutureEnrollmentAsAverageLast12Weeks<=755], y=FutureEnrollmentAsAverageLast12Weeks[FutureEnrollmentAsAverageLast12Weeks<=755], name = '%.1f per week (average last 12 weeks)'%EnrollmentRateLast3Months, hoverinfo = 'x+y',
                               line = dict(
                width = 2,
                color = 'orange'
            ),
                 )
elif plot_average == '4weeks':
    trace_asAverage = go.Scatter(x=FutureDate[FutureEnrollmentAsAverageLast4Weeks<=755], y=FutureEnrollmentAsAverageLast4Weeks[FutureEnrollmentAsAverageLast4Weeks<=755], name = '%.1f per week (average last 4 weeks)'%EnrollmentRateLastMonth, hoverinfo = 'x+y',
                               line = dict(
                width = 2,
                color = 'orange'
            ),
                 )


# actual figure

fig = go.FigureWidget()

fig.add_trace(traceEnrollment);
fig.add_trace(trace_750subjects);
fig.add_trace(trace_4perWeek);
fig.add_trace(trace_5perWeek);
fig.add_trace(trace_asAverage);

weeks_average = {re.search('\d+', plot_average)[0]}

layout = go.Layout(
    showlegend=True,
    images = [dict(
        source= "https://upload.wikimedia.org/wikipedia/commons/d/d5/Emojione_1F525.svg",
        xref= "paper",
        yref= "paper",
        x= 0.61,
        y= 1.12,
        sizex= 0.1,
        sizey= 0.1,
        xanchor= "left",
        yanchor= "top"
      )],
    
    annotations=[
        
                dict(
            x=pd.Timestamp(currentDate + datetime.timedelta(hours = 24*10)),
            y=currentEnrollment+310,
            xref='x',
            yref='y',
            text= 'Enrollments last 7 days= \t '+ str(EnrollmentRateLastWeek),
            showarrow=False,
#             arrowhead=7,
            ax=500,
            ay=500
        ),
        
                dict(
            x=pd.Timestamp(currentDate + datetime.timedelta(hours = 24*10)),
            y=currentEnrollment+280,
            xref='x',
            yref='y',
            text= 'Weekly enrollment rate for last 4 weeks= \t' + str(EnrollmentRateLastMonth),
            showarrow=False,
#             arrowhead=7,
#             ax=500,
            ay=40
        ),
        
                dict(
            x=pd.Timestamp(currentDate + datetime.timedelta(hours = 24*10)),
            y=currentEnrollment+250,
            xref='x',
            yref='y',
            text= 'Weekly enrollment rate for last 12 weeks= \t %.1f'%EnrollmentRateLast3Months,
            showarrow=False,
#             arrowhead=7,
#             ax=500,
            ay=40
        ),
        
        
        dict(
            x=pd.Timestamp(currentDate),
            y=currentEnrollment,
            xref='x',
            yref='y',
            text= str(currentDate.date()) +' - ' + str(currentEnrollment) +' subjects enrolled',
            showarrow=True,
            arrowhead=7,
            ax=80,
            ay=40
        ),
                dict(
            x=FutureDate[FutureEnrollment5perWeek<=755][-1],
            y=750,
            xref='x',
            yref='y',
            text=str(FutureDate[FutureEnrollment5perWeek<=755][-1]).split(' ')[0],
            showarrow=True,
            arrowhead=7,
            ax=60,
            ay=-35
        ),
        
                dict(
            x=FutureDate[FutureEnrollment4perWeek<=754][-1],
            y=750,
            xref='x',
            yref='y',
            text=str(FutureDate[FutureEnrollment4perWeek<=754][-1]).split(' ')[0],
            showarrow=True,
            arrowhead=7,
            ax=60,
            ay=-35
        ),
        
                 dict(
            x=FutureDate[FutureEnrollmentAsAverageLast12Weeks<=754][-1],
            y=750,
            xref='x',
            yref='y',
            text=str(FutureDate[FutureEnrollmentAsAverageLast12Weeks<=754][-1]).split(' ')[0],
            showarrow=True,
            arrowhead=7,
            ax=60,
            ay=-10
        ),

#                  dict(
#             x=FutureDate[FutureEnrollmentAsAverageLast4Weeks<=754][-1],
#             y=750,
#             xref='x',
#             yref='y',
#             text=str(FutureDate[FutureEnrollmentAsAverageLast4Weeks<=754][-1]).split(' ')[0],
#             showarrow=True,
#             arrowhead=7,
#             ax=60,
#             ay=-10
#         ),
                         dict(
            x= 0.2, #consent.date.iloc[0],
            y=1.07,
            showarrow=False,
            xref='paper',
            yref='paper',
            text='# currently enrolled subjects with study ID: ' + str(currentEnrollment),

        ),
                                 dict(
            x= 0.2, #consent.date.iloc[0],
            y=1.05,
            showarrow=False,
            xref='paper',
            yref='paper',
            text='# subjects who will/might not be included in study: ' + str(len(not_in_study)),

        ),
                                 dict(
            x= 0.2, #consent.date.iloc[0],
            y=1.03,
            showarrow=False,
            xref='paper',
            yref='paper',
            text=f"Projected enrollment date for #750 based on last-12-week enrollment rate: " + str(FutureDate[FutureEnrollmentAsAverageLast12Weeks<=754][-1]).split(' ')[0],

        )
        
    ],
     title=('ICU-Sleep enrollment'),
)

fig.layout = layout
plot(fig,filename = 'ICU_enrollment_burndownchart.html', auto_open=True)