import dash
from dash import dcc
from dash import html
import plotly.graph_objs as go
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

dash_app = dash.Dash()
app = dash_app.server

dash_app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Cantidad de Activos, Recuperados y fallecidos por departamento
    '''),
    html.Div(
        [
            dcc.Dropdown(
                id="Fecha",
                options=[{
                    'label': str(i.strftime("%B"))+" "+str(i.year),
                    'value': i
                } for i in mes_options],
                ),
        ],
        style={'width': '25%',
               'display': 'inline-block'}),
    dcc.Graph(
        id='grafica-estado',)
])
@dash_app.callback(
    dash.dependencies.Output('grafica-estado', 'figure'),
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

if __name__ == '__main__':
    dash_app.run_server(debug=True)