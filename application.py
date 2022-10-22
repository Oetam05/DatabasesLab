import dash
from dash import dcc
from dash import html
import plotly.graph_objs as go
import pandas as pd

date_labels = ['fecha reporte web', 'Fecha de notificación', 'Fecha de inicio de síntomas', 'Fecha de muerte', 
          'Fecha de diagnóstico', 'Fecha de recuperación']
str_labels = {'Nombre departamento': 'category', 'Nombre municipio': 'category', 'Sexo': 'category', 
              'Tipo de contagio': 'category', 'Ubicación del caso': 'category', 'Estado': 'category', 
              'Nombre del país': 'category', 'Recuperado': 'category', 'Tipo de recuperación': 'category', 
              'Nombre del grupo étnico': 'category'}
file_name = "./DataSet/Casos_positivos_de_COVID-19_en_Colombia.csv"
df = pd.read_csv(file_name, low_memory=False, parse_dates=date_labels)
df = df.astype(str_labels)
df['Sexo'] = df['Sexo'].replace({'m':'M', 'f':'F'})
df['Sexo'].unique()
df['Sexo'] = df['Sexo'].astype('category')
df['Recuperado'] = df['Recuperado'].replace({'fallecido':'Fallecido'})
pv = pd.pivot_table(df, index=['Nombre departamento'], columns=["Recuperado"], values=['ID de caso'], aggfunc='count', fill_value=0)

trace1 = go.Bar(x=pv.index, y=pv[('ID de caso', 'Activo')], name='Activo')
trace2 = go.Bar(x=pv.index, y=pv[('ID de caso', 'Recuperado')], name='Recuperado')
trace3 = go.Bar(x=pv.index, y=pv[('ID de caso', 'Fallecido')], name='Fallecido')



dash_app = dash.Dash()
app = dash_app.server

dash_app.layout = html.Div(children=[
    html.H1(children='Hello Dash'),

    html.Div(children='''
        Cantidad de Activos, Recuperados y fallecidos por departamento
    '''),

    dcc.Graph(
        id='example-graph',
        figure={
           'data': [trace1, trace2, trace3],
            'layout':
            go.Layout(title='Por departamento', barmode='stack')
        }
    )
])

if __name__ == '__main__':
    dash_app.run_server(debug=True)