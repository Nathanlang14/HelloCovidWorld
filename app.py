import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

import flask
import pandas as pd
import datetime as dt
import plotly.graph_objects as go
import os

server = flask.Flask('app')
server.secret_key = os.environ.get('secret_key', 'secret')

app = dash.Dash('app', server=server)

df = pd.read_csv('covid_2020_daily.csv')
final_day = df[df.date == '12/31/2020']
df.date = pd.to_datetime(df.date, infer_datetime_format=True)
us_total = df.groupby(['date'], as_index = False).sum()


options=[{'label': i, 'value': i} for i in df['state'].unique()]
options.insert(0,{'label':'All States', 'value':'All States'})


app.layout = html.Div(
    children=[
        html.Div([html.H1('US COVID-19 Data')]),
        html.Div([
            html.H2('Positive and Total Cases by State'),
            dcc.Dropdown(
                id='my-dropdown',
                options=options,
                value='All States'
            ),
            dcc.Graph(id='my-graph')
        ], className="barchart"),

        html.Div([
            html.H2('Map of Total Cases by State'),
            dcc.Graph(id='my-map')
        ], className="map"),

        html.Div([
            dcc.Slider(
                id='my-slider',
                min=0,
                max=353,
                step=1,
                value=150,
                marks={0: 'Jan', 19: 'Feb',
                       48: 'Mar',
                       79: 'Apr',
                       109: 'May',
                       140: 'Jun',
                       170: 'July',
                       201: 'Aug',
                       232: 'Sept',
                       262: 'Oct',
                       293: 'Nov',
                       323: 'Dec'
                       }
            ),
            html.Div(id='slider-output')
        ])
])


@app.callback(Output('my-graph', 'figure'),
              [Input('my-dropdown', 'value')])
def update_graph(selected_dropdown_value):
    if selected_dropdown_value == 'All States':
        dff = us_total
    else:
        dff = df[df['state'] == selected_dropdown_value]

    fig = go.Figure(data=[
        go.Bar(name='Total Tests', x=dff.date, y=dff.totalTestResults),
        go.Bar(name='Positive Tests', x=dff.date, y=dff.positive)

    ])

    fig.update_layout(
        barmode='overlay'
    )

    return fig

@app.callback(Output('my-map', 'figure'),
              [Input('my-slider', 'value')])
def update_map(selected_date):
    df_day = df[df.date == (df.date.min() + dt.timedelta(days=selected_date))]

    daily_map = go.Figure(data=go.Choropleth(
        locations=df_day['state'],
        z=df_day['totalTestResults'],
        locationmode='USA-states',
        colorscale='Reds',
        colorbar_title="Total Tests",
    ))

    daily_map.update_layout(
        title_text='2020 US Covid Testing Total by State',
        geo_scope='usa',
        height=700,
        width=1100
    )
    return daily_map


if __name__ == '__main__':
    app.run_server()