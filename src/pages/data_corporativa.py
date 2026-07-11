import dash
from dash import html, dcc, callback, Input, Output, ALL, State, dash_table, register_page, no_update, exceptions
import dash_bootstrap_components as dbc
import plotly.graph_objects as graph_objects
import pandas as pd
import copy

register_page(
    __name__, 
    name="data_corp",
    top_nav=True,
    path="/datos_corporacion",     
    )

# Diccionario de Unidades Educativas
ue_options = {
                'CORPORACIÓN': 'CORPORACIÓN',  # ← agregar primero
                'BÁSICA 1':'BÁSICA 1',
                'BÁSICA 2':'BÁSICA 2',
                'BÁSICA SAN FELIPE':'BÁSICA SF',
                'MEDIA LOS ANDES':'MEDIA LOS ANDES',
                'MEDIA SAN FELIPE':'MEDIA SAN FELIPE'}

# Lista de diccionarios para 'options' usando una lista por comprensión
ue_options_dropdown = [{'label': k, 'value': v} for k, v in ue_options.items()]



def nivel_unidad_educativa(unidad_edu):

    # Condicional que define por completo cada grupo independiente
    if unidad_edu in ['BÁSICA 1', 'BÁSICA 2', 'BÁSICA SF']:

        niveles = {
                     'PRE-KINDER':'PRE-KINDER',
                     'KINDER': 'KINDER'}
        
        # Lista de diccionarios para 'options' usando una lista por comprensión
        niveles_options_dropdown = [{'label': k, 'value': v} for k, v in niveles.items()]
    else:
        niveles = {
                     '1MEDIO':'1MEDIO',
                     '2MEDIO': '2MEDIO'}
        
        # Lista de diccionarios para 'options' usando una lista por comprensión
        niveles_options_dropdown = [{'label': k, 'value': v} for k, v in niveles.items()]

    return  niveles_options_dropdown



menu_lateral = dbc.Card([

    # Lista despegable para UNIDAD EDUCATIVA
    html.Div(
        children=[
            html.H6(
                [
                 html.I(className="fa-solid fa-school me-2"), 
                'Unidad Educativa '
                ],
                className="text-primary fw-bold mb-3"
              ),
              dcc.Dropdown(
                id='unidades_educativas', 
                options=ue_options_dropdown,
                value='BÁSICA 1',
                clearable=False,
                style={
                        'width': '100%',          # Ancho del dropdown
                        'backgroundColor': '#f0f0f0', # Color de fondo
                        'color': '#333333',      # Color del texto
                        'fontSize': '14px'       # Tamaño de la fuente
                      },
                
            ),
        ]),

    html.Br(),
        
    html.Div(
            children=[
                html.H6(
                    [
                    html.I(className="fa-solid fa-school me-2"), 
                    'Niveles '
                    ],
                    className="text-primary fw-bold mb-3"
                ),
                dcc.Dropdown(
                    id='niveles_educativos', 
                    options = nivel_unidad_educativa("BÁSICA 1"),
                    value= "PRE-KINDER",
                    clearable=False,
                    style={
                            'width': '100%',          # Ancho del dropdown
                            'backgroundColor': '#f0f0f0', # Color de fondo
                            'color': '#333333',      # Color del texto
                            'fontSize': '14px'       # Tamaño de la fuente
                        },
                    
                ),
            ]),

   


     ], body=True, className="shadow-sm border-0", # fin menu lateral
    
 ) # fin dbc, Menu Lateral

@callback (
    Output('niveles_educativos', 'options'),
    Output('niveles_educativos', 'value'),
    Input('unidades_educativas', 'value')
)
def opciones_niveles(unidad_edu):

    lista_opciones = nivel_unidad_educativa(unidad_edu)
    
    valor_inicial = next(iter(lista_opciones[0].values()))

    return  lista_opciones, valor_inicial

layout = dbc.Container([

     # Layaout General, 1 fila, 2 columnas,
     dbc.Row([
    
     # Columna para menu lateral
        dbc.Col( menu_lateral, width=4), 

     # Columna para gráficos
        dbc.Col( width=8), 

     ])

  ], fluid=True) # Fin Layaout para leer en aap.py

