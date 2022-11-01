import dash
from dash import dcc
from dash import html
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from datetime import datetime
import pyodbc
import json
from urllib.request import urlopen


server = 'LAPTOP-7S9B3U0H' 
database = 'Covid_19' 
username = 'sa' 
password = 'abc123'  
cnxn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()
# select 26 rows from SQL table to insert in dataframe.
query = "SELECT * FROM [Covid_19].[dbo].[casos_covid1M]"
df = pd.read_sql(query, cnxn)

with urlopen('https://gist.githubusercontent.com/john-guerra/43c7656821069d00dcbc/raw/be6a6e239cd5b5b803c6e7c2ec405b793a9064dd/Colombia.geo.json') as response:
    counties = json.load(response)
locs = df['Nombre departamento'].unique()
for loc in counties['features']:
    loc['id'] = loc['properties']['NOMBRE_DPT']

mes_options=[]
m=11
a=2021
sw=True
while(sw):
    if(m==2 and a==2022):
        sw=False
    if(m==13):
        m=1
        a+=1
    mes_options.append(datetime(a, m, 1))
    m+=1

external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css']


dash_app = dash.Dash(external_stylesheets=external_stylesheets)
app = dash_app.server

dash_app.layout = html.Div(style={'font-family':"Courier New, monospace"}, 
    children=[
        html.Div(
            html.H1('Casos de Covid 19 en colombia'), className = 'banner'
            ),

        html.Div(className="row", children=[
        html.Div(className="three columns", children=[
                dcc.Dropdown(
                    id='drop-fecha', placeholder="Seleccione una fecha",
                    options=[{
                    'label': str(i.strftime("%B"))+" "+str(i.year),
                    'value': i
                } for i in mes_options],
                )]
            )]),
    dcc.Graph(id='grafica-lineas', figure={}),

        html.Div(className="row", children=[
        html.Div(className="three columns", children=[
                dcc.Dropdown(
                    id='drop-recuperado', placeholder="Seleccione una fecha",
                    options=["Recuperado", "Fallecido"],clearable=False, value='Recuperado'
                )]
            )]),
    dcc.Graph(id='mapa', figure={}),

        html.Div([
    html.Div(className="three columns", children=[
                    dcc.Dropdown(
                        df['Nombre departamento'].unique(), id='drop-dep', placeholder="Seleccione departamento", clearable=False, value='CUNDINAMARCA'
                        )
                    ]
                ),

        html.Div(className = 'create_container2 five columns', children=[
                dcc.Graph(
                id='grafica-pie1', figure={})
        ]),
        html.Div(className = 'create_container2 five columns', children=[
            dcc.Dropdown(['Recuperado','Fallecido','Activo'], id='dropSex',placeholder="Seleccione el estado",value="Recuperado", clearable=False),
            dcc.Graph(
            id='grafica-pie2', figure={})
        ]),
        html.Div(className = 'create_container2 five columns', children=[
            dcc.Dropdown(df['Sexo'].unique(), id='dropSexo',placeholder="Seleccione el sexo",value="M", clearable=False),
            dcc.Graph(
            id='grafica-pie3', figure={})
        ])
    ], className = 'create_container2 twelve columns')
])


@dash_app.callback(
    dash.dependencies.Output('grafica-lineas', 'figure'),
    [dash.dependencies.Input('drop-fecha', 'value')])
def update_graph(Fecha):
    if(not Fecha):        
        df_plot = df.copy()
    else:
        por_a = df[df['fecha reporte web'].dt.year == int(Fecha[0:4])]
        df_plot=por_a[por_a['fecha reporte web'].dt.month==int(Fecha[5:7])]
    pv = pd.pivot_table(df_plot, index=['fecha reporte web'], columns=["Recuperado"], values=['ID de caso'], aggfunc='count')
    trace1 = go.Scatter(x=pv.index, y=pv[('ID de caso', 'Recuperado')], name='Recuperado')
    trace2 = go.Scatter(x=pv.index, y=pv[('ID de caso', 'Fallecido')], name='Fallecido')
    return {
        'data': [trace1, trace2],
        'layout':
        go.Layout(
            title='Estado de los pacientes {}'.format(Fecha[0:7] if Fecha else"Siempre"),
            )
    }


@dash_app.callback(
    dash.dependencies.Output('mapa', 'figure'),
    [dash.dependencies.Input('drop-recuperado', 'value')])
def update_graph(value):

    dff=df[df['Recuperado']==value]
    dff['Nombre departamento'] = dff['Nombre departamento'].replace({'GUAJIRA':'LA GUAJIRA', 'NORTE SANTANDER':'NORTE DE SANTANDER', 'VALLE':'VALLE DEL CAUCA'})
    group=dff.groupby(["Nombre departamento","Recuperado"])
    dff=group.size().reset_index(name='Cantidad')
    print(dff)
    trace1 = go.Choroplethmapbox(
                    geojson=counties,
                    locations=dff['Nombre departamento'],
                    z=dff['Cantidad'],
                    colorscale='Viridis',
                    colorbar_title=value)
    return {
        'data': [trace1],
        'layout':
        go.Layout(
            title='Pacientes '+value+'s por departamentos',mapbox_style="carto-positron", mapbox_zoom=4, 
            mapbox_center = {"lat": 4.570868, "lon": -74.2973328}, height=700)            
    }

@dash_app.callback(
    dash.dependencies.Output('grafica-pie1', component_property='figure'),
    [dash.dependencies.Input('drop-dep', component_property='value')])

def update_graph_pie(value):
    df_plot= df[df['Nombre departamento'] == value]
    df_plot['Estado']=df['Estado'].astype('category')
    df_plot['Estado']=df['Estado'].replace({'leve':'Leve'})
    pv = pd.pivot_table(df_plot, index=['Estado'], columns=["Nombre departamento"], values=['ID de caso'], aggfunc='count', fill_value=0)
    trace1 = go.Pie(labels =pv.index, values=pv[('ID de caso', value)], name='Depto')
    return{
        'data': [trace1],
        'layout':
        go.Layout(
            title='Estado de los pacientes de {} Siempre'.format(value)),
    }
@dash_app.callback(
    dash.dependencies.Output('grafica-pie2', component_property="figure"),
    dash.dependencies.Input('dropSex',component_property='value'), 
)
def generate_chart(a):
    df_plot=df[df['Recuperado']==a]
    df_m=df_plot[df_plot['Sexo']=='M']
    df_f=df_plot[df_plot['Sexo']=='F']
    trace=go.Box(y=df_m['Edad'],name="Hombres", boxmean=True)
    trace2=go.Box(y=df_f['Edad'],name="Mujeres",boxmean=True)
    return{
        'data': [trace,trace2],
        'layout':
        go.Layout(
            title='Edad de los pacientes {}'.format(a)),
    }

@dash_app.callback(
    dash.dependencies.Output('grafica-pie3', component_property="figure"),
    dash.dependencies.Input('dropSexo',component_property='value'),)
def generate_gr(a):
    df_plot=df[df['Sexo']==a]
    dfa=df_plot['Fecha de recuperación']-df_plot['Fecha de diagnóstico']
    n=[]
    for i  in dfa:
        try:

            if i:
                n.append(int(str(i)[:2]))
        except:
            pass
    f = go.Violin(y=n,name="Tiempo de recuperación")
    return{
        'data': [f],
        'layout':
        go.Layout(
            title='Tiempo de recuperación de los pacientes de sexo {}'.format(a)),
    }

if __name__ == '__main__':
    dash_app.run_server(debug=True)