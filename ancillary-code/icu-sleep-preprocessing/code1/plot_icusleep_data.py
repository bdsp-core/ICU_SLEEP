import pandas as pd
import numpy as np
#matplotlib widget
import plotly # built with plotly version '4.4.1'
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
from plotly.subplots import make_subplots
import sys
import gc
import os
# from tqdm import tqdm



def covid_plot(data, trace_linewidth=1, labelfontsize=10, legend_position = [0.2, 1.15], legend_font_size=10):
    '''
    Plot designed for the 10Hz data, plots AirGo, Blood Pressure, Heart Rate, and SpO2.
    Input: sleep research-formatted data
    Output: fig (plotly figure instance)
    '''
    
    airgo_available = 'band' in data.columns
    BP_available = any(['ART1D' in data.columns, 'ART1S' in data.columns, 'NBPD' in data.columns, 'NBPS' in data.columns])
    HR_available = 'HR' in data.columns
    SPO2_available = 'SPO2%' in data.columns
    RR_available = 'resp' in data.columns

    num_traces = sum([airgo_available, BP_available, HR_available, SPO2_available, RR_available])

    fig = make_subplots(rows=num_traces, cols=1, shared_xaxes=True, shared_yaxes=False, specs=[[{"secondary_y": False}]] * num_traces )

    traces = []
    i_trace=1

    if airgo_available:
        trace_AirGo = go.Scatter(x=data.index, y=data.band, name = 'AirGo', hoverinfo = 'x+y', line = dict(color = 'dodgerblue', width = trace_linewidth), opacity = 0.8 )
        fig.add_trace(trace_AirGo, i_trace, 1)
        fig.update_yaxes(title_text="Circumference <br> Thorax (a.u.)", row=i_trace, col=1, range=[data['band'].quantile(0.01),data['band'].quantile(0.99)], title_font=dict(size=labelfontsize))
        i_trace+=1

    if RR_available:
        trace_RR = go.Scatter(x=data.index, y=data.resp, name = 'Resp.Rate', hoverinfo = 'x+y', line = dict(color = 'dodgerblue', width = trace_linewidth), opacity = 0.8)
        fig.add_trace(trace_RR, i_trace, 1)
        fig.update_yaxes(title_text="Resp. Rate", row=i_trace, col=1, range=[data.RESP.quantile(0.005),data.RESP.quantile(0.995)], title_font=dict(size=labelfontsize))

        i_trace+=1
        
    if SPO2_available:
        trace_SPO2 = go.Scatter(x=data.index, y=data['SPO2%'], name = 'SpO2%', hoverinfo = 'x+y', line = dict(color = 'navy', width = trace_linewidth), opacity = 0.8)
        fig.add_trace(trace_SPO2, i_trace, 1)
        fig.update_yaxes(title_text="SpO2 (%)", row=i_trace, col=1, range=[data['SPO2%'].quantile(0.01),data['SPO2%'].quantile(1)+0.5], title_font=dict(size=labelfontsize))
        i_trace+=1

    if HR_available:
        trace_HR = go.Scatter(x=data.index, y=data.HR, name = 'Heart Rate', hoverinfo = 'x+y', line = dict(color = 'crimson', width = trace_linewidth), opacity = 0.8)
        fig.add_trace(trace_HR, i_trace, 1)
        fig.update_yaxes(title_text="HR(bpm)", row=i_trace, col=1, range=[data['HR'].quantile(0.005),data['HR'].quantile(0.995)], title_font=dict(size=labelfontsize))
        i_trace+=1


    if 'ART1D' in data.columns:
        trace_ART1D = go.Scatter(x=data.index, y=data.ART1D, name = 'Art. BP diastolic', hoverinfo = 'x+y', line = dict(color = 'magenta', width = trace_linewidth), opacity = 0.8)
        fig.add_trace(trace_ART1D, i_trace, 1)
    if 'ART1S' in data.columns:
        trace_ART1S = go.Scatter(x=data.index, y=data.ART1S, name = 'Art. BP systolic', hoverinfo = 'x+y', line = dict(color = 'orange', width = trace_linewidth), opacity = 0.8)
        fig.add_trace(trace_ART1S, i_trace, 1)
    if 'NBPD' in data.columns:
        trace_NBPD = go.Scatter(x=data.index, y=data.NBPD, name = 'NonInv. BP diastolic', hoverinfo = 'x+y', line = dict(color = 'magenta', width = trace_linewidth, dash = 'dashdot'), opacity = 0.8 )
        fig.add_trace(trace_NBPD, i_trace, 1)
    if 'NBPS' in data.columns:
        trace_NBPS = go.Scatter(x=data.index, y=data.NBPS, name = 'NonInv. BP systolic', hoverinfo = 'x+y', line = dict(color = 'orange', width = trace_linewidth, dash = 'dashdot'), opacity = 0.8 )
        fig.add_trace(trace_NBPS, i_trace, 1)
    if BP_available: 
        fig.update_yaxes(title_text="BP (mmHg)", row=i_trace, col=1, title_font=dict(size=labelfontsize))
        i_trace+=1


    fig.update_layout(plot_bgcolor='rgb(237,237,237)')     # 'white'
    fig.update_layout(legend=dict(x=legend_position[0], y=legend_position[1], orientation = 'h'), font=dict(size=legend_font_size, color="black"))

    return fig


def icu_sleep_plot(data, trace_linewidth=1, labelfontsize=10, legend_position = [0.2, 1.15], legend_font_size=10, fs=10, vertical_spacing=0.2):
    '''
    Plot designed for the 10Hz data, plots AirGo, Blood Pressure, Heart Rate, and SpO2.
    Input: sleep research-formatted data
    Output: fig (plotly figure instance)
    '''
    
    data.columns = [x.lower() for x in data.columns]
    # if 'movavg_0_5s' in data.columns:
    #     data.rename({'movavg_0_5s': 'band_smooth'}, axis=1, inplace=True)
    annotation_available = any(['stage' in data.columns, 'apnea' in data.columns])
    stage_pred_available = any(['stage_pred' in x for x in data.columns])
    apnea_pred_available = any(['apnea_pred_' + x in data.columns for x in ['ro_a3','ro_a4','ro_e4','rs_a3','rs_a4','rs_e4','rsr_a3','rsr_a4','rsr_e4', 'va_a3','va_a3_ss']])
    airgo_available = any(['band' in data.columns, 'band_smooth' in data.columns, 'movavg_0_5s' in data.columns, 'band_unscaled' in data.columns, 'movavg_0_5s_unscaled' in data.columns])
    # BP_available = any(['ART1D' in data.columns, 'ART1S' in data.columns, 'NBPD' in data.columns, 'NBPS' in data.columns])
    BP_available = any(['art1d' in data.columns, 'art1s' in data.columns, 'nbpd' in data.columns, 'nbps' in data.columns,
                        'edw_bp_diastolic' in data.columns, 'edw_bp_systolic' in data.columns])
    HR_available = any(['HR' in data.columns, 'hr' in data.columns, 'edw_pulse' in data.columns])
    nn_available = any(['nn_interval' in data.columns])
    SPO2_available = any(['SPO2%' in data.columns, 'spo2%' in data.columns, 'spo2' in data.columns, 'edw_pulse_oximetry' in data.columns])
    RR_available = any(['rr_10s' in data.columns, 'rr_10s_smooth' in data.columns, 'edw_respirations' in data.columns, 'resp' in data.columns, 'vent rate' in data.columns])
    ventilation_available = any(['ventilation_10s_smooth' in data.columns, 'ventilation_10s' in data.columns, 'ventilation_2min' in data.columns] )
    ventilation_std_available = any(['ventilation_std_2min' in data.columns, 'ventilation_cvar_2min' in data.columns] )

    ibi_available = any(['ibi' in data.columns, 'ibi_std_5min' in data.columns, 'ibi_std_2min' in data.columns, 'ibi_cvar_2min' in data.columns])
    inht_exht_available = any(['inht_cycle_ratio_10sec' in data.columns])
    airgo_actigraphy_available = any(['acc_ai_10sec' in data.columns, 'accy_1sec' in data.columns, 'position_cluster' in data.columns, 'positioned' in data.columns])
    oxygen_supplement_available = any(['oxygen_flow_rate' in data.columns, 'oxygen_device' in data.columns])
    self_similarity_available = any(['self_similarity' in data.columns])
    hypoxic_burden_available = any(['hypoxic_area_' + x in data.columns for x in ['ro_a3','ro_a4','ro_e4','rs_a3','rs_a4','rs_e4','rsr_a3','rsr_a4','rsr_e4', 'va_a3','va_a3_ss']])
    instability_index_available = any(['instability_index' in x for x in data.columns])
    quality_available = any(['airgo_signal_quality' in data.columns])
    sofa_available = any(['sofa_score' in data.columns, 'sofa_respiratory' in data.columns, 'sofa_cvs'])
    meds_available = any(['opioids_sum' in data.columns, 'benzos_sum' in data.columns, 'antipsychotics_sum'])

    num_traces = sum([annotation_available, stage_pred_available, apnea_pred_available, airgo_actigraphy_available, airgo_available, 
                      BP_available, HR_available, nn_available, SPO2_available, ibi_available, RR_available, 
                      ventilation_available, ventilation_std_available, inht_exht_available,
                     oxygen_supplement_available, hypoxic_burden_available, self_similarity_available, instability_index_available, quality_available,
                     sofa_available, meds_available])

    fig = make_subplots(rows=num_traces, cols=1, shared_xaxes=True, shared_yaxes=False, specs=[[{"secondary_y": False}]] * num_traces, vertical_spacing=0.01)

    traces = []
    i_trace=1

    if annotation_available:
        trace_Sleep = go.Scatter(x=data.index[::int(2*fs)], y=data.stage[::int(2*fs)], name = 'Stage', hoverinfo = 'x+y', line = dict(color = 'Crimson', width = 1), opacity = 0.8 )
        fig.add_trace(trace_Sleep, i_trace, 1)
        trace_Apnea = go.Scatter(x=data.index[::int(2*fs)], y=data.apnea[::int(2*fs)], name = 'Apnea', hoverinfo = 'x+y', line = dict(color = 'DeepSkyBlue', width = 1), opacity = 0.8)
        fig.add_trace(trace_Apnea, i_trace, 1)
        fig.update_yaxes(title_text="Stage, Apnea", row=i_trace, col=1, title_font=dict(size=labelfontsize), range=[-0.1,6.1], tickvals=[5,4,3,2,1], ticktext =['W','R','N1','N2','N3'], color = 'red')
        i_trace+=1

    if stage_pred_available:

        stage_pred_versions = [x for x in data.columns if 'stage_pred' in x]
        stage_pred_colors = {
        'stage_pred_amendsumeffort': 'navy',
        'stage_pred_activity10sec': 'gray',
        'stage_pred_comb_breath_activity_1': 'blue',
        'stage_pred_ecg_nn': 'red',
        }
        # opacities = [0.8, 0.4, 0.4]

        for iv, stage_pred_version in enumerate(stage_pred_versions):
            name = 'Stage ' + stage_pred_version.replace('stage_pred_','').replace('comb_breath_activity_1','').replace('amendsumeffort','Breathing-Only').replace('ecg_nn', 'ECG NN')
            trace_Sleep = go.Scatter(x=data.index[::int(2*fs)], y=data[stage_pred_version][::int(2*fs)], name = name, 
                hoverinfo = 'x+y', line = dict(color = stage_pred_colors[stage_pred_version], width = 1), opacity = 0.8)
            fig.add_trace(trace_Sleep, i_trace, 1)
        
        fig.update_yaxes(title_text="Sleep<br>Stage", row=i_trace, col=1, title_font=dict(size=labelfontsize), range=[-0.1,6.1], tickvals=[5,4,3,2,1], ticktext =['W','R','N1','N2','N3']) # , color = 'Crimson'
        i_trace+=1

    if apnea_pred_available:
        color_apnea_pred = ['teal', 'grey', 'seagreen']
        color_apnea_prob = ['orange', 'grey', 'palegreen']
        opacities = [0.8, 0.4, 0.4]
        i_pred = -1

        # add the apnea prediction and also probability if available:
        for model_id in ['va_a3', 'va_a3_ss', 'ro_a3','ro_a4','ro_e4','rs_a3','rs_a4','rs_e4','rsr_a3','rsr_a4','rsr_e4']:
            model_id = 'apnea_pred_' + model_id
            name = 'Apnea ' + model_id.replace('apnea_pred_','').replace('va_a3','').replace('ro_a3','Breathing-Only')

            if model_id in data.columns:
                i_pred += 1
                trace_Apnea = go.Scatter(x=data.index[np.logical_not(pd.isna(data[model_id]))][::2], y=data[model_id][np.logical_not(pd.isna(data[model_id]))][::2], 
                    name = name, hoverinfo = 'x+y', line = dict(color = color_apnea_pred[i_pred], width = 1), opacity = opacities[i_pred])
                fig.add_trace(trace_Apnea, i_trace, 1)
                
                if model_id.replace('pred','prob') in data.columns:
                    proba = model_id.replace('pred','prob')
                    trace = go.Scatter(x=data.index[np.logical_not(pd.isna(data[model_id]))][::2], y=data[proba][np.logical_not(pd.isna(data[model_id]))][::2], 
                        name = name.replace('Apnea', 'Apnea Probability'), hoverinfo = 'x+y', line = dict(color = color_apnea_prob[i_pred], width = 1), opacity = opacities[i_pred])
                    fig.add_trace(trace, i_trace, 1)

        fig.update_yaxes(title_text="Apnea<br>Prediction", row=i_trace, col=1, title_font=dict(size=labelfontsize), range=[-0.1,1.1])
        i_trace+=1

    if hypoxic_burden_available:

        color_hypoxia = ['forestgreen', 'lime', 'seagreen']

        i_hypoxia = -1
        for model_id in ['va_a3', 'va_a3_ss', 'ro_a3','ro_a4','ro_e4','rs_a3','rs_a4','rs_e4','rsr_a3','rsr_a4','rsr_e4']:
            model_id = 'hypoxic_area_' + model_id
            name = 'Hypoxic Burden' + model_id.replace('apnea_pred_','').replace('va_a3','').replace('ro_a3','Breathing-Only')

            if model_id in data.columns:
                i_hypoxia += 1
                trace = go.Scatter(x=data.index[::int(2*fs)], y=data[model_id][::int(2*fs)], name = 'Hypoxic Burden', hoverinfo = 'x+y', line = dict(color = color_hypoxia[i_hypoxia], width = 1), opacity = 0.8 )
                fig.add_trace(trace, i_trace, 1)
                fig.update_yaxes(title_text="Hypoxic<br>Burden", row=i_trace, col=1, title_font=dict(size=labelfontsize))
                i_trace+=1

    if self_similarity_available:
        trace = go.Scatter(x=data.index[::int(fs)], y=data.self_similarity[::int(fs)], name = 'Self Similarity', hoverinfo = 'x+y', line = dict(color = 'darkorange', width = 1), opacity = 0.8 )
        fig.add_trace(trace, i_trace, 1)
        fig.update_yaxes(title_text="Self-<br>Similarity", row=i_trace, col=1, title_font=dict(size=labelfontsize))
        
        if 'cpc_hfc_lfc_ratio' in data.columns:
            trace = go.Scatter(x=data.index[::int(fs*30)], y=data.cpc_hfc_lfc_ratio[::int(fs*30)], name = 'CPC LogRatio', hoverinfo = 'x+y', line = dict(color = 'black', width = 1), opacity = 0.8 )
            fig.add_trace(trace, i_trace, 1)         
        fig.update_yaxes(title_text="Self-Similarity, CPC", row=i_trace, col=1, title_font=dict(size=labelfontsize))


        i_trace+=1


    if airgo_available:
        airgo_colors = ['dodgerblue', 'blue']
        i_airgo = 0

        if 'band' in data.columns:
            trace_AirGo = go.Scatter(x=data.index[::int(fs/2)], y=data.band[::int(fs/2)], name = 'Airgo', hoverinfo = 'x+y', line = dict(color = airgo_colors[i_airgo], width = trace_linewidth), opacity = 0.5 )
            fig.add_trace(trace_AirGo, i_trace, 1)
            i_airgo += 1
            range_signal = [data['band'].quantile(0.01),data['band'].quantile(0.99)]
        if 'band_unscaled' in data.columns:
            trace_AirGo = go.Scatter(x=data.index[::int(fs/2)], y=data.band_unscaled[::int(fs/2)], name = 'Airgo', hoverinfo = 'x+y', line = dict(color = airgo_colors[i_airgo], width = trace_linewidth), opacity = 0.5 )
            fig.add_trace(trace_AirGo, i_trace, 1)
            i_airgo += 1
            range_signal = [data['band_unscaled'].quantile(0.01),data['band_unscaled'].quantile(0.99)]
        if 'band_smooth' in data.columns:
            trace_AirGo = go.Scatter(x=data.index[::int(fs/2)], y=data.band_smooth[::int(fs/2)], name = 'Airgo', hoverinfo = 'x+y', line = dict(color = airgo_colors[i_airgo], width = trace_linewidth), opacity = 0.8 )
            fig.add_trace(trace_AirGo, i_trace, 1)
            range_signal = [data['band_smooth'].quantile(0.01),data['band_smooth'].quantile(0.99)]
        if 'movavg_0_5s' in data.columns:
            trace_AirGo = go.Scatter(x=data.index[::int(fs/2)], y=data.movavg_0_5s[::int(fs/2)], name = 'Airgo', hoverinfo = 'x+y', line = dict(color = airgo_colors[i_airgo], width = trace_linewidth), opacity = 0.8 )
            fig.add_trace(trace_AirGo, i_trace, 1)
            range_signal = [data['movavg_0_5s'].quantile(0.01),data['movavg_0_5s'].quantile(0.99)]
        if 'movavg_0_5s_unscaled' in data.columns:
            trace_AirGo = go.Scatter(x=data.index[::int(fs/2)], y=data.movavg_0_5s_unscaled[::int(fs/2)], name = 'Airgo', hoverinfo = 'x+y', line = dict(color = airgo_colors[i_airgo], width = trace_linewidth), opacity = 0.8 )
            fig.add_trace(trace_AirGo, i_trace, 1)
            range_signal = [data['movavg_0_5s_unscaled'].quantile(0.01),data['movavg_0_5s_unscaled'].quantile(0.99)]
        if 'movmedian_1min' in data.columns:
            trace_AirGo = go.Scatter(x=data.index[::int(5*fs)], y=data['movmedian_1min'][::int(5*fs)], name = 'AirGo 1-min median', hoverinfo = 'x+y', line = dict(color = 'black', width = trace_linewidth), opacity = 0.8 )
            fig.add_trace(trace_AirGo, i_trace, 1)
        if 'movavg_1min' in data.columns:
            trace_AirGo = go.Scatter(x=data.index[::int(5*fs)], y=data['movavg_1min'][::int(5*fs)], name = 'AirGo 1-min mean', hoverinfo = 'x+y', line = dict(color = 'black', width = trace_linewidth), opacity = 0.8 )
            fig.add_trace(trace_AirGo, i_trace, 1)
            
        if 'peaks' in data.columns:
            peaks = data['peaks']
            trace_AirGo = go.Scatter(x=data.index[peaks==1], y=data.band_smooth[peaks==1], 
                        name = 'detected peak', hoverinfo = 'x+y', fillcolor='red', 
                                     mode='markers', opacity = 0.8,
                                     marker=dict(size=4, color='red')
                                    )
            fig.add_trace(trace_AirGo, i_trace, 1)
            
        fig.update_yaxes(title_text="Circumference<br>Thorax (a.u.)", row=i_trace, col=1, range=range_signal, title_font=dict(size=labelfontsize))
        i_trace+=1

    if quality_available:
        trace = go.Scatter(x=data.index[::int(5*fs)], y=data.airgo_signal_quality[::int(5*fs)], name = 'Airgo Quality', hoverinfo = 'x+y', line = dict(color = 'red', width = trace_linewidth), opacity = 0.8)
        fig.add_trace(trace, i_trace, 1)
        fig.update_yaxes(title_text="Signal<br>Quality", row=i_trace, col=1, range=[-0.1,2.1], title_font=dict(size=labelfontsize))
        i_trace+=1      

    if airgo_actigraphy_available:
        offset_position = 0
        if 'acc_ai_10sec' in data.columns:
            trace = go.Scatter(x=data.index[::2*fs], y=data.acc_ai_10sec[::2*fs], name = 'Actigraphy Activity', hoverinfo = 'x+y', line = dict(color = 'peru', width = trace_linewidth), opacity = 0.8 )
            fig.add_trace(trace, i_trace, 1)
            range_signal = [-0.01, data['acc_ai_10sec'].quantile(0.99)]
            offset_position = data['acc_ai_10sec'].quantile(0.99)+0.1
            
        if 'position_cluster' in data.columns:
            cluster_names = ['R.Lat.','L.Lat.','Suspine','Prone']
            cluster_colors = ['red','blue','green','black']
            
            change_pos = np.where(np.diff(data.position_cluster) != 0)[0]
            cluster_check = np.zeros((4,))
            
            for iPos in range(len(change_pos)-1):
                start_idx = change_pos[iPos]
                end_idx = change_pos[iPos+1]
                cluster_id = data.position_cluster.iloc[end_idx]
                if pd.isna(cluster_id): continue
                cluster_id = np.int32(cluster_id)
                if cluster_id == -1: continue
                name = 'Act. '+cluster_names[cluster_id]
                trace = go.Scatter(x=[data.index[start_idx],data.index[end_idx]], y=[offset_position]*2, hoverinfo = 'x+y', 
                                       line = dict(color = cluster_colors[cluster_id], width = trace_linewidth), opacity = 0.8,
                                       name = name, showlegend=bool(cluster_check[cluster_id]==0))

                fig.add_trace(trace, i_trace, 1)
                cluster_check[cluster_id] = 1

        if 'positioned' in data.columns:
            # offset_position = offset_position +0.1
            offset_position = 0.29
            # positioned = data.loc[np.logical_not(pd.isna(data.positioned)), 'positioned'].copy()
            # trace = go.Scatter(x=positioned.index, y=np.ones((len(positioned),))*offset_position, 
            #                    name = 'Positioning (EDW)', hoverinfo = 'x+text', 
            #                    hovertext = positioned, opacity = 0.8, # 'x+y'
            # fillcolor='red', mode='markers', marker=dict(size=8, color='red', symbol='triangle-up'))
            # fig.add_trace(trace, i_trace, 1)
            data_positioned = data.positioned.dropna()
            data_positioned = data_positioned[data_positioned!='nan']

            trace = go.Scatter(x=data_positioned.index, y=np.ones((len(data_positioned),))*offset_position, name = 'Positioning (EDW)',  mode='markers', hoverinfo = 'x+text', hovertext = data_positioned, opacity = 0.8, marker=dict(color='red', symbol='triangle-up', size=5)) # line = dict(color = 'orangered', width = trace_linewidth), opacity = 0.8
            fig.add_trace(trace, i_trace, 1)


                
        range_signal = [-0.01, offset_position+0.02]
        range_signal = [-0.01, 0.3]

        fig.update_yaxes(title_text="Actigraphy <br> Activity (g)", row=i_trace, col=1, range=range_signal, title_font=dict(size=labelfontsize))
        i_trace+=1
    

    if SPO2_available:
        spo2_name = [x for x in ['spo2','spo2%'] if x in data.columns]
        if len(spo2_name) > 0:
            spo2_name = spo2_name[0]
            trace_SPO2 = go.Scatter(x=data.index[::int(5*fs)], y=data[spo2_name][::int(5*fs)], name = 'SpO2%', hoverinfo = 'x+y', line = dict(color = 'navy', width = trace_linewidth), opacity = 0.8)
            fig.add_trace(trace_SPO2, i_trace, 1)

        if 'edw_pulse_oximetry' in data.columns:
            trace_SPO2 = go.Scatter(x=data.index[~pd.isna(data.edw_pulse_oximetry)], y=data.loc[~pd.isna(data.edw_pulse_oximetry),'edw_pulse_oximetry'], name = 'SpO2%  EDW', mode='markers', hoverinfo = 'x+y', \
                                    marker = dict(color = 'navy', size=5))
            fig.add_trace(trace_SPO2, i_trace, 1)
            if len(spo2_name) == 0: spo2_name = 'edw_pulse_oximetry'

        fig.update_yaxes(title_text="SpO2<br>(%)", row=i_trace, col=1, range=[data[spo2_name].quantile(0.01),data[spo2_name].quantile(1)+0.9], title_font=dict(size=labelfontsize))
        i_trace+=1


    if HR_available:
        hr_name = None
        if 'hr' in data.columns:
            hr_name = 'hr'
            trace_HR = go.Scatter(x=data.index[::int(5*fs)], y=data.hr[::int(5*fs)], name = 'Heart Rate', hoverinfo = 'x+y', line = dict(color = 'crimson', width = trace_linewidth), opacity = 0.8)
            fig.add_trace(trace_HR, i_trace, 1)
        if 'edw_pulse' in data.columns:
            trace_HR = go.Scatter(x=data.index[~pd.isna(data.edw_pulse)], y=data.loc[~pd.isna(data.edw_pulse),'edw_pulse'], name = 'HR EDW', mode='markers', hoverinfo = 'x+y', \
                                    marker = dict(color = 'crimson', size=5))
            fig.add_trace(trace_HR, i_trace, 1)
            if hr_name is None: hr_name = 'edw_pulse'

        fig.update_yaxes(title_text="HR<br>(bpm)", row=i_trace, col=1, range=[data[hr_name].quantile(0.01),data[hr_name].quantile(0.99)], title_font=dict(size=labelfontsize))
        i_trace+=1

    if nn_available:

        trace = go.Scatter(x=data.index[pd.notna(data.nn_interval)], y=data.nn_interval[pd.notna(data.nn_interval)], name = 'NN Interval', hoverinfo = 'x+y', line = dict(color = 'red', width = trace_linewidth), opacity = 0.8)
        fig.add_trace(trace, i_trace, 1)
        fig.update_yaxes(title_text="NN<br>(sec)", row=i_trace, col=1, range=[data.nn_interval.quantile(0.01),data.nn_interval.quantile(0.99)], title_font=dict(size=labelfontsize))
        i_trace+=1

    if instability_index_available:
        if 'instability_index_30sec' in data.columns:
            trace = go.Scatter(x=data.index[::int(10*fs)], y=data.instability_index_30sec[::int(10*fs)], name = 'Instability Index 30sec', hoverinfo = 'x+y', line = dict(color = 'darkseagreen', width = trace_linewidth), opacity = 0.4)
            fig.add_trace(trace, i_trace, 1)
        if 'instability_index_1min' in data.columns:
            trace = go.Scatter(x=data.index[::int(10*fs)], y=data.instability_index_1min[::int(10*fs)], name = 'Instability Index 1min', hoverinfo = 'x+y', line = dict(color = 'blue', width = trace_linewidth), opacity = 0.8)
            fig.add_trace(trace, i_trace, 1)
        if 'instability_index_2min' in data.columns:
            trace = go.Scatter(x=data.index[::int(10*fs)], y=data.instability_index_2min[::int(10*fs)], name = 'Instability Index 2min', hoverinfo = 'x+y', line = dict(color = 'forestgreen', width = trace_linewidth), opacity = 0.8)
            fig.add_trace(trace, i_trace, 1)
        if 'instability_index_5min' in data.columns:
            trace = go.Scatter(x=data.index[::int(10*fs)], y=data.instability_index_5min[::int(10*fs)], name = 'Instability Index 5min', hoverinfo = 'x+y', line = dict(color = 'lime', width = trace_linewidth), opacity = 0.8)
            fig.add_trace(trace, i_trace, 1)
        fig.update_yaxes(title_text="Instability<br>Index", row=i_trace, col=1, title_font=dict(size=labelfontsize), range=[0,0.8])

        i_trace+=1      


    if ventilation_available:
        if 'ventilation_10s_smooth' in data.columns:
            trace = go.Scatter(x=data.index[::int(10*fs)], y=data.ventilation_10s_smooth[::int(10*fs)], name = 'Minute Ventilation', hoverinfo = 'x+y', line = dict(color = 'purple', width = trace_linewidth), opacity = 0.8)
            fig.add_trace(trace, i_trace, 1)
            range_signal = [data['ventilation_10s_smooth'].quantile(0.01),data['ventilation_10s_smooth'].quantile(0.99)]
        if 'ventilation_2min' in data.columns:
            trace = go.Scatter(x=data.index[::int(10*fs)], y=data.ventilation_2min[::int(10*fs)], name = 'Minute Ventilation', hoverinfo = 'x+y', line = dict(color = 'magenta', width = trace_linewidth), opacity = 0.8)
            fig.add_trace(trace, i_trace, 1)
            range_signal = [data['ventilation_2min'].quantile(0.01),data['ventilation_2min'].quantile(0.99)]

        fig.update_yaxes(title_text="MV", row=i_trace, col=1, title_font=dict(size=labelfontsize), range=range_signal)
        i_trace+=1
        
    if ventilation_std_available:
        if 'ventilation_std_2min' in data.columns:
            trace = go.Scatter(x=data.index[::int(10*fs)], y=data.ventilation_std_2min[::int(10*fs)], name = 'Minute Ventilation Std', hoverinfo = 'x+y', line = dict(color = 'green', width = trace_linewidth), opacity = 0.8)
            fig.add_trace(trace, i_trace, 1)
            range_signal = [data['ventilation_std_2min'].quantile(0.01),data['ventilation_std_2min'].quantile(0.99)]
            fig.update_yaxes(title_text="Minute Ventilation Std", row=i_trace, col=1, title_font=dict(size=labelfontsize), range=range_signal)

        if 'ventilation_cvar_2min' in data.columns:
            trace = go.Scatter(x=data.index[::int(10*fs)], y=data.ventilation_cvar_2min[::int(10*fs)], name = 'Minute Ventilation Cvar', hoverinfo = 'x+y', line = dict(color = 'blue', width = trace_linewidth), opacity = 0.8)
            fig.add_trace(trace, i_trace, 1)
            range_signal = [data['ventilation_cvar_2min'].quantile(0.01),data['ventilation_cvar_2min'].quantile(0.99)]
            fig.update_yaxes(title_text="Minute Ventilation CVar", row=i_trace, col=1, title_font=dict(size=labelfontsize), range=range_signal)
            
    if RR_available:

        range_signal = [15,30]
        if 'rr_10s_smooth' in data.columns:
            trace_RR = go.Scatter(x=data.index[::int(10*fs)], y=data.rr_10s_smooth[::int(10*fs)], name = 'Resp.Rate', hoverinfo = 'x+y', line = dict(color = 'orangered', width = trace_linewidth), opacity = 0.8)
            range_signal = [np.min([range_signal[0], data['rr_10s_smooth'].quantile(0.01)]), np.max([data['rr_10s_smooth'].quantile(0.99), range_signal[1]])]
            fig.add_trace(trace_RR, i_trace, 1)

        if 'edw_respirations' in data.columns:
            data_edw_respirations = data.edw_respirations.dropna()
            trace_RR = go.Scatter(x=data_edw_respirations.index, y=data_edw_respirations.values, name = 'Resp.Rate EDW',  mode='markers', hoverinfo = 'x+y', marker=dict(color='black', size=5)) # line = dict(color = 'orangered', width = trace_linewidth), opacity = 0.8
            fig.add_trace(trace_RR, i_trace, 1)

        if 'resp' in data.columns: # bedmaster
            trace_RR = go.Scatter(x=data.index[::int(10*fs)], y=data.resp[::int(10*fs)], name = 'Resp.Rate (bedmaster)', hoverinfo = 'x+y', line = dict(color = 'yellowgreen', width = trace_linewidth), opacity = 0.8)
            range_signal = [np.min([range_signal[0], data['resp'].quantile(0.01)]), np.max([data['resp'].quantile(0.99), range_signal[1]])]
            fig.add_trace(trace_RR, i_trace, 1)        

        if 'vent rate' in data.columns: # bedmaster
            trace_RR = go.Scatter(x=data.index[::int(10*fs)], y=data['vent rate'][::int(10*fs)], name = 'Resp.Rate (bedmaster)', hoverinfo = 'x+y', line = dict(color = 'blue', width = trace_linewidth), opacity = 0.8)
            range_signal = [np.min([range_signal[0], data['vent rate'].quantile(0.01)]), np.max([data['vent rate'].quantile(0.99), range_signal[1]])]
            fig.add_trace(trace_RR, i_trace, 1)   

        fig.update_yaxes(title_text="RR", row=i_trace, col=1, title_font=dict(size=labelfontsize), range=range_signal)
        i_trace+=1


        
    if ibi_available:
        if 'ibi' in data.columns:
            trace = go.Scatter(x=data.index[::int(2*fs)], y=data.ibi[::int(2*fs)], name = 'Inter-Breath Interval', hoverinfo = 'x+y', line = dict(color = 'lightsalmon', width = trace_linewidth), opacity = 0.8)
            fig.add_trace(trace, i_trace, 1)
        if 'ibi_std_5min' in data.columns:
            trace = go.Scatter(x=data.index[np.logical_not(pd.isna(data['ibi_std_5min']))][::int(fs)], y=data.ibi_std_5min[np.logical_not(pd.isna(data['ibi_std_5min']))][::int(fs)], 
                               name = 'Inter-Breath Interval STD', hoverinfo = 'x+y', line = dict(color = 'orangered', width = trace_linewidth), opacity = 0.8)
            # trace = go.Scatter(x=data.index[::int(2*fs)], y=data.ibi_std_5min[::2*int(fs)], 
                               # name = 'Inter-Breath Interval STD', hoverinfo = 'x+y', line = dict(color = 'orangered', width = trace_linewidth), opacity = 0.8)
            fig.add_trace(trace, i_trace, 1) 
        if 'ibi_std_2min' in data.columns:
            trace = go.Scatter(x=data.index[np.logical_not(pd.isna(data['ibi_std_2min']))][::int(fs)], y=data.ibi_std_2min[np.logical_not(pd.isna(data['ibi_std_2min']))][::int(fs)], 
                               name = 'Inter-Breath Interval STD 2min', hoverinfo = 'x+y', line = dict(color = 'green', width = trace_linewidth), opacity = 0.8)
            # trace = go.Scatter(x=data.index[::int(2*fs)], y=data.ibi_std_5min[::2*int(fs)], 
                               # name = 'Inter-Breath Interval STD', hoverinfo = 'x+y', line = dict(color = 'orangered', width = trace_linewidth), opacity = 0.8)
            fig.add_trace(trace, i_trace, 1) 

        if 'ibi_cvar_2min' in data.columns:
            trace = go.Scatter(x=data.index[np.logical_not(pd.isna(data['ibi_cvar_2min']))][::int(fs)], y=data.ibi_cvar_2min[np.logical_not(pd.isna(data['ibi_cvar_2min']))][::int(fs)], 
                               name = 'Inter-Breath Interval CVar 2min', hoverinfo = 'x+y', line = dict(color = 'blue', width = trace_linewidth), opacity = 0.8)
            # trace = go.Scatter(x=data.index[::int(2*fs)], y=data.ibi_std_5min[::2*int(fs)], 
                               # name = 'Inter-Breath Interval STD', hoverinfo = 'x+y', line = dict(color = 'orangered', width = trace_linewidth), opacity = 0.8)
            fig.add_trace(trace, i_trace, 1) 

        fig.update_yaxes(title_text="IBI", row=i_trace, col=1, title_font=dict(size=labelfontsize))
        i_trace+=1
        
    if inht_exht_available:
        if 'inht_cycle_ratio_10sec' in data.columns:
            trace = go.Scatter(x=data.index[::10*int(fs)], y=data.inht_cycle_ratio_10sec[::10*int(fs)], name = 'Inhalation Time Ratio', hoverinfo = 'x+y', line = dict(color = 'green', width = trace_linewidth), opacity = 0.8)
            fig.add_trace(trace, i_trace, 1)
            fig.update_yaxes(title_text="Inhalation <br> Time (%)", row=i_trace, col=1, title_font=dict(size=labelfontsize))
            i_trace+=1       
                              
                              
    if 'art1d' in data.columns:
        trace_ART1D = go.Scatter(x=data.index[::int(10*fs)], y=data.art1d[::int(10*fs)], name = 'Art. BP diastolic', hoverinfo = 'x+y', line = dict(color = 'magenta', width = trace_linewidth), opacity = 0.8)
        fig.add_trace(trace_ART1D, i_trace, 1)
    if 'art1s' in data.columns:
        trace_ART1S = go.Scatter(x=data.index[::int(10*fs)], y=data.art1s[::int(10*fs)], name = 'Art. BP systolic', hoverinfo = 'x+y', line = dict(color = 'orange', width = trace_linewidth), opacity = 0.8)
        fig.add_trace(trace_ART1S, i_trace, 1)
    if 'nbpd' in data.columns:
        trace_NBPD = go.Scatter(x=data.index[::int(10*fs)], y=data.nbpd[::int(10*fs)], name = 'NonInv. BP diastolic', hoverinfo = 'x+y', line = dict(color = 'magenta', width = trace_linewidth, dash = 'dashdot'), opacity = 0.8 )
        fig.add_trace(trace_NBPD, i_trace, 1)
    if 'nbps' in data.columns:
        trace_NBPS = go.Scatter(x=data.index[::int(10*fs)], y=data.nbps[::int(10*fs)], name = 'NonInv. BP systolic', hoverinfo = 'x+y', line = dict(color = 'orange', width = trace_linewidth, dash = 'dashdot'), opacity = 0.8 )
        fig.add_trace(trace_NBPS, i_trace, 1)
    if 'edw_bp_diastolic' in data.columns:
        trace = go.Scatter(x=data.index[~pd.isna(data.edw_bp_diastolic)], y=data.loc[~pd.isna(data.edw_bp_diastolic),'edw_bp_diastolic'], name = 'NonInv. BP diastolic', mode='markers', hoverinfo = 'x+y', \
                                marker = dict(color = 'magenta', size=5))
        fig.add_trace(trace, i_trace, 1)
    if 'edw_bp_systolic' in data.columns:
        trace = go.Scatter(x=data.index[~pd.isna(data.edw_bp_diastolic)], y=data.loc[~pd.isna(data.edw_bp_systolic),'edw_bp_systolic'], name = 'NonInv. BP systolic', mode='markers', hoverinfo = 'x+y', \
                                marker = dict(color = 'orange', size=5))
        fig.add_trace(trace, i_trace, 1)
    if BP_available: 
        fig.update_yaxes(title_text="BP (mmHg)", row=i_trace, col=1, title_font=dict(size=labelfontsize))
        i_trace+=1

    if oxygen_supplement_available:
        oxygen_flow = data.oxygen_flow_rate.dropna() # data.loc[np.logical_not(pd.isna(data.oxygen_flow)), 'oxygen_flow'].copy()
        oxygen_device = data.oxygen_device.dropna() # data.loc[np.logical_not(pd.isna(data.oxygen_device)), 'oxygen_device'].copy()
        trace = go.Scatter(x=oxygen_flow.index, y=oxygen_flow, 
                           name = 'Oxygen Suppl.', hoverinfo = 'x+text', 
                           hovertext = oxygen_device, opacity = 0.8, # 'x+y'
        fillcolor='black', marker=dict(size=8, color='cornflowerblue')) # mode='markers'
        fig.add_trace(trace, i_trace, 1)
        fig.update_yaxes(title_text="Oxygen Suppl.", row=i_trace, col=1, title_font=dict(size=labelfontsize))
        i_trace+=1   


    if sofa_available:
        data.loc[data.sofa_score == -99, 'sofa_score'] = np.nan
        data.loc[data.sofa_respiratory == -99, 'sofa_respiratory'] = np.nan
        data.loc[data.sofa_cvs == -99, 'sofa_cvs'] = np.nan
        trace = go.Scatter(x=data.index[~pd.isna(data.sofa_score)], y=data.sofa_score[~pd.isna(data.sofa_score)], name = 'SOFA', hoverinfo = 'x+y', line = dict(color = 'magenta', width = trace_linewidth), opacity = 0.8)
        fig.add_trace(trace, i_trace, 1)
        trace = go.Scatter(x=data.index[~pd.isna(data.sofa_respiratory)], y=data.sofa_respiratory[~pd.isna(data.sofa_respiratory)], name = 'SOFA Respiratory', hoverinfo = 'x+y', line = dict(color = 'mediumturquoise', width = trace_linewidth), opacity = 0.8)
        fig.add_trace(trace, i_trace, 1)
        trace = go.Scatter(x=data.index[~pd.isna(data.sofa_cvs)], y=data.sofa_cvs[~pd.isna(data.sofa_cvs)], name = 'SOFA CVS', hoverinfo = 'x+y', line = dict(color = 'firebrick', width = trace_linewidth), opacity = 0.8)
        fig.add_trace(trace, i_trace, 1)
        fig.update_yaxes(title_text="SOFA", row=i_trace, col=1, title_font=dict(size=labelfontsize))
        i_trace+=1   

    if meds_available:

        valid_pts = valid_points_medications(data.opioids_sum)
        trace = go.Scatter(x=data.index[valid_pts], y=data.loc[data.iloc[valid_pts].index, 'opioids_sum'], \
            name = 'Opioids', mode='markers', hoverinfo = 'x+y+name', marker = dict(color = 'magenta', size=4, symbol='star'))
        fig.add_trace(trace, i_trace, 1)

        valid_pts = valid_points_medications(data.benzos_sum)
        trace = go.Scatter(x=data.index[valid_pts], y=data.loc[data.iloc[valid_pts].index, 'benzos_sum'], \
            name = 'Benzodiazepines', mode='markers', hoverinfo = 'x+y+name', marker = dict(color = 'green', size=4, symbol='star'))
        # trace = go.Scatter(x=data.index[(~pd.isna(data.benzos_sum)) & (data.benzos_sum>0)], y=data.loc[(~pd.isna(data.benzos_sum)) & (data.benzos_sum>0), 'benzos_sum'], \
            # name = 'Benzodiazepines', mode='markers', hoverinfo = 'x+y+name', marker = dict(color = 'green', size=5, symbol='star'))
        fig.add_trace(trace, i_trace, 1)

        valid_pts = valid_points_medications(data.antipsychotics_sum)
        trace = go.Scatter(x=data.index[valid_pts], y=data.loc[data.iloc[valid_pts].index, 'antipsychotics_sum'], \
            name = 'Antipsychotics', mode='markers', hoverinfo = 'x+y+name', marker = dict(color = 'dimgrey', size=4, symbol='star'))
        # trace = go.Scatter(x=data.index[(~pd.isna(data.antipsychotics_sum)) & (data.antipsychotics_sum>0)], y=data.loc[(~pd.isna(data.antipsychotics_sum)) & (data.antipsychotics_sum>0), 'antipsychotics_sum'], \
            # name = 'Antipsychotics', mode='markers', hoverinfo = 'x+y+name', marker = dict(color = 'dimgrey', size=5, symbol='star'))
        fig.add_trace(trace, i_trace, 1)

        fig.update_yaxes(title_text="Meds", row=i_trace, col=1, title_font=dict(size=labelfontsize))


    fig.update_layout(plot_bgcolor='rgb(237,237,237)')     # 'white'
    fig.update_layout(legend=dict(x=legend_position[0], y=legend_position[1], orientation = 'h'), font=dict(size=legend_font_size, color="black"))

    return fig

def valid_points_medications(series):

        valid_pts = np.where(~pd.isna(series) & series > 0)[0]
        continuous_pts = valid_pts[np.where(np.diff(valid_pts) <= 10)[0]]
        # since meds frequency is 1 second but 60 seconds is enough for infusion, let's only keep each 60th point:
        # continuous_pts = list(set(continuous_pts) - set(continuous_pts[::60])) # deactivated becuase now med interval is 1minute.
        valid_pts = list(set(valid_pts) - set(continuous_pts))
        valid_pts.sort()

        return valid_pts


    
def main():

	start_file_no = 1
	end_file_no = 'none'

	print(f'start_file_no: {start_file_no}')
	print(f'end_file_no: {end_file_no}')

	files_directory = 'M:/Projects/ICU_SLEEP_STUDY/data/data_analysis/biosignals_10Hz_data_daynight/'
	savedir_plots = 'M:/Projects/ICU_SLEEP_STUDY/data/data_analysis/biosignals_10Hz_plots/'

	all_files = os.listdir(files_directory)
	all_files.sort()
	all_files = all_files[start_file_no:] # end_file_no

	for filename in tqdm(all_files):

		filepath = os.path.join(files_directory, filename)

		# CHECK IF FILE ALREADY EXISTS, CONTINUE IF SO.
		signals_contained_tmp, hdr = get_metadata(filepath)
		if 'day_night_id' in hdr: 
		    title = f'StudyID '+str(hdr['study_id']).zfill(3)+', '+hdr['day_night_id'].split('_')[1].replace('n', 'Night ').replace('d','Day')
		    save_path = os.path.join(savedir_plots, 'FILEFORMAT_day_night_partitions/'+hdr['day_night_id'])
		else: 
		    title = f'StudyID '+str(hdr['study_id']).zfill(3)+', Full Data'
		    save_path = os.path.join(savedir_plots, 'FILEFORMAT_full/'+str(hdr['study_id']).zfill(3))
		if os.path.exists(save_path.replace('FILEFORMAT','PNG') +'.png'):
			continue
		# END OF CHECK.

		try:
			gc.collect()

			# filepath = 'M:/Projects/ICU_SLEEP_STUDY/data/data_analysis/biosignals_10Hz_data/icusleep_001.h5'

			data, hdr = load_sleep_data(filepath, idx_to_datetime=1)


			if 'day_night_id' in hdr: 
			    title = f'StudyID '+str(hdr['study_id']).zfill(3)+', '+hdr['day_night_id'].split('_')[1].replace('n', 'Night ').replace('d','Day')
			    save_path = os.path.join(savedir_plots, 'FILEFORMAT_day_night_partitions/'+hdr['day_night_id'])
			else: 
			    title = f'StudyID '+str(hdr['study_id']).zfill(3)+', Full Data'
			    save_path = os.path.join(savedir_plots, 'FILEFORMAT_full/'+str(hdr['study_id']).zfill(3))

			# PLOT (html version)
			fig = icu_sleep_plot(data, trace_linewidth=1, labelfontsize=12, legend_position = [0.2, 1.05], legend_font_size=12)
			fig.update_layout(title=title)
			plot(fig, filename=save_path.replace('FILEFORMAT','HTML')+'.html', auto_open=False)
			del fig

			# PLOT (pdf/png version)
			fig = icu_sleep_plot(data, trace_linewidth=0.5, labelfontsize=8, legend_position = [0.18, 1.15], legend_font_size=8)
			fig.update_layout(title=title)
			fig.write_image(save_path.replace('FILEFORMAT','PDF')+'.pdf', scale=3)
			fig.write_image(save_path.replace('FILEFORMAT','PNG')+'.png', scale=5)
			del fig

		except Exception as e:
			print(filename)
			print('error for this one!')
			print(e)


if __name__ =='__main__':
	main()

