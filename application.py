from unicodedata import name
import dash
from dash import dcc
from dash import html
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
from datetime import datetime

date_labels = ['fecha reporte web', 'Fecha de notificación', 'Fecha de inicio de síntomas', 'Fecha de muerte', 
          'Fecha de diagnóstico', 'Fecha de recuperación']
str_labels = {'Nombre departamento': 'category', 'Nombre municipio': 'category', 'Sexo': 'category', 
              'Tipo de contagio': 'category', 'Ubicación del caso': 'category', 'Estado': 'category', 
              'Nombre del país': 'category', 'Recuperado': 'category', 'Tipo de recuperación': 'category', 
              'Nombre del grupo étnico': 'category'}
file_name = "./DataSet/Casos_positivos_de_COVID-19_en_Colombia.csv"
df = pd.read_csv(file_name, low_memory=False, parse_dates=date_labels,skiprows=[i for i in range(1,5900000)])#Se ommiten columnas para que no se demore en ejecutar
df = df.astype(str_labels)
df['Sexo'] = df['Sexo'].replace({'m':'M', 'f':'F'})
df['Sexo'].unique()
df['Sexo'] = df['Sexo'].astype('category')
df['Recuperado'] = df['Recuperado'].replace({'fallecido':'Fallecido'})
df['Nombre departamento'] = df['Nombre departamento'].replace({'Cundinamarca':'CUNDINAMARCA', 'STA MARTA D.E.':'MAGDALENA', 'CARTAGENA':'BOLIVAR', 'BOGOTA':'CUNDINAMARCA', 'BARRANQUILLA':'ATLANTICO'})

mes_options=[]
m=4
a=2020
sw=True
while(sw):
    if(m==4 and a==2022):
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
                    id='Fecha', placeholder="Seleccione una fecha",
                    options=[{
                    'label': str(i.strftime("%B"))+" "+str(i.year),
                    'value': i
                } for i in mes_options],
                )]
            )]),
    dcc.Graph(
        id='grafica-barras', figure={}),
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
            dcc.Graph(
            id='grafica-pie2', figure={})
        ])
    ], className = 'create_container2 twelve columns')
])
@dash_app.callback(
    dash.dependencies.Output('grafica-barras', 'figure'),
    [dash.dependencies.Input('Fecha', 'value')])
def update_graph(Fecha):
    if(not Fecha):        
        df_plot = df.copy()
    else:
        por_a = df[df['Fecha de diagnóstico'].dt.year == int(Fecha[0:4])]
        df_plot=por_a[por_a['Fecha de diagnóstico'].dt.month==int(Fecha[5:7])]
    pv = pd.pivot_table(df_plot, index=['Nombre departamento'], columns=["Recuperado"], values=['ID de caso'], aggfunc='count', fill_value=0)

    trace1 = go.Bar(x=pv.index, y=pv[('ID de caso', 'Activo')], name='Activo')
    trace2 = go.Bar(x=pv.index, y=pv[('ID de caso', 'Recuperado')], name='Recuperado')
    trace3 = go.Bar(x=pv.index, y=pv[('ID de caso', 'Fallecido')], name='Fallecido')
    return {
        'data': [trace1, trace2, trace3],
        'layout':
        go.Layout(
            title='Estado de los pacientes {}'.format(Fecha[0:7] if Fecha else"Siempre"),
            barmode='stack')
    }

@dash_app.callback(
    dash.dependencies.Output('grafica-pie1', component_property='figure'),
    [dash.dependencies.Input('drop-dep', component_property='value')])

def update_graph_pie(value):
    df_plot= df[df['Nombre departamento'] == value]
    pv = pd.pivot_table(df_plot, index=['Recuperado'], columns=["Nombre departamento"], values=['ID de caso'], aggfunc='count', fill_value=0)
    trace1 = go.Pie(labels =pv.index, values=pv[('ID de caso', value)], name='Depto')
    return{
        'data': [trace1],
        'layout':
        go.Layout(
            title='Estado de los pacientes de {} Siempre'.format(value)),
    }

if __name__ == '__main__':
    dash_app.run_server(debug=True)