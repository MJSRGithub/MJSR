import pandas as pd
import numpy as np

import dash
dash.__version__
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output,State

import plotly.graph_objects as go

import os
print(os.getcwd())

df_ip_big=pd.read_csv('data/processed/COVID_final_set.csv',sep=';')
fig = go.Figure()
app = dash.Dash()
app.layout = html.Div([

    dcc.Markdown('''
    #  Task 2 of the Applied Data Science project on the COVID-19 data

    Here we will be able to select and control the following SIR parameters and be able to adjust the graph according to our requirements.
    It is a full walkthrough of the SIR model.
    '''),

    dcc.Markdown('''
    ## Multi-Select Country for visualization

    Please select the countries which you wish to view it.
    '''),

    dcc.Dropdown(
        id='country_drop_down',
        options=[ {'label': each,'value':each} for each in df_ip_big['country'].unique()],
        value=['US'], # which are pre-selected
        multi=True
    ),

    dcc.Markdown('''
        ## The SIR Parameters
        '''),

    dcc.Markdown('''
    ## Starting period(in Days)
    '''),
    dcc.Input(
            id="t_start", type="number", placeholder="number",
            value=7,min=0, max=1000,
            step=1,debounce=True
    ),

     dcc.Markdown('''
    ## Intro period(in Days)
    '''),
    dcc.Input(
            id="t_intr", type="number", placeholder="number",
            value=40,min=0, max=1000,
            step=1,debounce=True
    ),

     dcc.Markdown('''
    ## Hold period(in Days)
    '''),
    dcc.Input(
            id="t_halt", type="number", placeholder="number",
            value=43,min=0, max=1000,
            step=1,debounce=True
    ),

     dcc.Markdown('''
    ## Relaxing period(in Days)
    '''),
    dcc.Input(
            id="t_relx", type="number", placeholder="number",
            value=70,min=0, max=1000,
            step=1,debounce=True
    ),

     dcc.Markdown('''
    ## Max infection rate
    '''),
     dcc.Input(
             id="b_max", type="number", placeholder="number",
             value=0.35,min=0, max=100,
             debounce=True

    ),

     dcc.Markdown('''
    ## Min infection rate
    '''),
     dcc.Input(
             id="b_min", type="number", placeholder="number",
             value=0.13,min=0, max=100,
             debounce=True
    ),

     dcc.Markdown('''
    ## Recovering rate
    '''),
     dcc.Input(
             id="gamma", type="number", placeholder="number",
             value=0.09,min=0, max=100,
             debounce=True
    ),

    dcc.Graph(figure=fig, id='main_window_slope')
])

@app.callback(
    Output('main_window_slope', 'figure'),
    [Input('country_drop_down', 'value'),
    Input('t_start', component_property='value'),
    Input('t_intr',component_property= 'value'),
    Input('t_halt',component_property= 'value'),
    Input('t_relx',component_property= 'value'),
    Input('b_max',component_property= 'value'),
    Input('b_min', component_property='value'),
    Input('gamma', component_property='value')])

def update_figure(country_list,t_start,t_intr,t_halt,t_relx,bmax,bmin,gamma):

    traces =[]

    for each in country_list:

        df_plot=df_ip_big[df_ip_big['country']==each]
        df_plot=df_plot[['state','country','confirmed','confirmed_filtered','confirmed_DR','confirmed_filtered_DR','date']].groupby(['country','date']).agg(np.mean).reset_index()
        df_plot=df_plot['confirmed'][df_plot['confirmed']>35].reset_index(drop=True)


        ydata=df_plot
        xdata= np.arange(len(df_plot))

        traces.append(dict(
                                x=xdata,
                                y=ydata,
                                type='bar',
                                opacity=0.9,
                                visible=True,
                                name=each+'_Confirmed'
                          )
                     )

        pd_beta=np.concatenate((np.array(t_start*[bmax]),
                               np.linspace(bmax,bmin,t_intr),
                               np.array(t_halt*[bmin]),
                               np.linspace(bmin,bmax,t_relx),
                               ))

        I0=df_plot[0]
        N0=np.array(df_plot)[-1]/0.04
        S0=N0-I0
        R0=0


        SIR=np.array([S0,I0,R0])


        propagation_rates=pd.DataFrame(columns={'susceptible':S0,
                                            'infected':I0,
                                            'recoverd':R0})

        for each_beta in pd_beta:

            new_delta_vec=SIR_model(SIR,each_beta,gamma,N0)

            SIR=SIR+new_delta_vec

            propagation_rates=propagation_rates.append({'susceptible':SIR[0],
                                                        'infected':SIR[1],
                                                        'recovered':SIR[2]}, ignore_index=True)

        traces.append(dict(
                                x=propagation_rates.index,
                                y=propagation_rates.infected,
                                mode='markers+lines',
                                legend_title="Legend Title",
                                opacity=0.9,
                                visible=True,
                                name=each+'_Infected'

                          )
                     )

    return {
                        'data': traces,
                        'layout': dict (
                            width=1280,
                            height=720,
                            title= 'Scenario SIR simulations  (demonstration purposes only)',

                            xaxis={'title':'Time in days',
                                    #'tickangle':-45,
                                   # 'nticks':20,
                                    'tickfont':dict(size=14,color="#7f7f7f"),
                                  },
                            yaxis={'title':'Confirmed infected people (Source: John Hopkins,log-scale)',
                                   'type':"log",
                                    #'tickangle':-45,
                                   #'nticks':20,
                                    'tickfont':dict(size=14,color="#7f7f7f"),
                                  },

                    )
        }

if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False, port=8051)
