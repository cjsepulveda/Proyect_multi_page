import dash
import pathlib
from dash import html, dcc, callback, Input, Output, ALL, State, dash_table, register_page, no_update, exceptions
import dash_bootstrap_components as dbc
import plotly.graph_objects as graph_objects
import plotly.express as px
import pandas as pd
import copy

register_page(
    __name__, 
    name="data_corp",
    top_nav=True,
    path="/datos_corporacion",     
    )

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()
_df01_corp = None # cache en RAM

def load_data_corp():
    """Carga los datos de Excel solo una vez por proceso."""
    global _df01_corp
    # Si ya se cargaron los datos, no hacemos nada.
    if _df01_corp is not None:
        return

    workbook = DATA_PATH.joinpath('data_corp_demo.xlsx')
    _df01_corp = pd.read_excel(workbook, sheet_name='data_corp')

def obtener_datos_base():
    load_data_corp()
    return _df01_corp

# Diccionario de Unidades Educativas
unidades_edu = {
                'CORPORACIÓN': 'CORPORACIÓN',
                'BÁSICA 1':'BÁSICA 1',
                'BÁSICA 2':'BÁSICA 2',
                'BÁSICA SAN FELIPE':'BÁSICA SF',
                'MEDIA LOS ANDES':'MEDIA LOS ANDES',
                'MEDIA SAN FELIPE':'MEDIA SAN FELIPE'}

# Lista de diccionarios para 'options' usando una lista por comprensión
unidades_edu_options_dropdown = [{'label': k, 'value': v} for k, v in unidades_edu.items()]



def nivel_unidad_educativa(unidad_edu):

    # Condicional que define por completo cada grupo independiente
    if unidad_edu in ['BÁSICA 1', 'BÁSICA 2', 'BÁSICA SF']:

        niveles = {
                     'PREKINDER': 'PREKINDER',
                     'KINDER':  'KINDER',
                     '1BÁSICO': '1BÁSICO',
                     '2BÁSICO': '2BÁSICO',
                     '3BÁSICO': '3BÁSICO',
                     '4BÁSICO': '4BÁSICO',
                     '5BÁSICO': '5BÁSICO',
                     '6BÁSICO': '6BÁSICO',
                     '7BÁSICO': '7BÁSICO',
                     '8BÁSICO': '8BÁSICO'
                     }
        
        # Lista de diccionarios para 'options' usando una lista por comprensión
        niveles_options_dropdown = [{'label': k, 'value': v} for k, v in niveles.items()]
    else:
        niveles = {
                     '1MEDIO': '1MEDIO',
                     '2MEDIO': '2MEDIO',
                     '3MEDIO': '3MEDIO',
                     '4MEDIO': '4MEDIO'}
        
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
                id='unidades_educativas_corp', 
                options=unidades_edu_options_dropdown,
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
    # Lista despegable para los niveles de la UNIDAD EDUCATIVA    
    html.Div(
            children=[
                html.H6(
                    [
                    html.I(className="fa-solid fa-users me-2"), 
                    'Niveles '
                    ],
                    className="text-primary fw-bold mb-3"
                ),
                dcc.Dropdown(
                    id='niveles_educativos',
                    
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
    Input('unidades_educativas_corp', 'value'),
)
def opciones_niveles(unidad_edu):

    lista_opciones_ue = nivel_unidad_educativa(unidad_edu)
    valor_inicial_ue = list(lista_opciones_ue[0].values())[0]
    return  lista_opciones_ue, valor_inicial_ue

layout = dbc.Container([

     # Layaout General, 1 fila, 2 columnas,
     dbc.Row([
    
     # Columna para menu lateral
        dbc.Col( menu_lateral, width=4), 

     # Columna para gráficos
        dbc.Col([

            dbc.Tabs([

              dbc.Tab(label="Gráfico 1", tab_id="tab-graf-1", children=[

                            dbc.Card([
                                dbc.CardHeader(html.Div([
                                                        html.H6("Matrículas 2021 - 2026: ", className="m-0 text-dark", style={"display": "inline"}),
                                                        html.Span(id="titulo-grafico-ue", className="text-white fw-bold", style={"display": "inline", "marginLeft": "5px"})
                                                        ], className="d-flex align-items-center")
                                ),
                                dbc.CardBody(
                                    dcc.Loading(
                                        id="corp-loading-grafico",
                                        type="circle",
                                        children=dcc.Graph(config={"displayModeBar": False}, id="grafico-matricula-corp")
                                    )
                                )
                            ], className="shadow-sm mt-3")




                ],
                        
                        
                        
                        ),
              dbc.Tab(label="Gráfico 2", children=[],
                        
                        
                        
                        
                        ),

            ],active_tab="tab-graf-1"),




            
        ],
            
            width=8), # fin columna gráfico

     ])

  ], fluid=True) # Fin Layaout para leer en aap.py

# callback para gráficos corporacion
@callback (
    Output('grafico-matricula-corp', 'figure'),
    Output('titulo-grafico-ue', 'children'),
    Input('unidades_educativas_corp', 'value'),
    Input('niveles_educativos', 'value'),

)
def graficos_corporativos(unidad_educativa, nivel_educativo):

    valor_unidad_educativa = unidad_educativa
    texto_unidad_educativa = next((k for k, v in unidades_edu.items() if v == valor_unidad_educativa), None)
    texto_nivel_educativo = nivel_educativo
    texto_final_grafico = texto_unidad_educativa + "-" + " " + texto_nivel_educativo

    

    df_corp_inicial = obtener_datos_base()
    df_corp_filtrado = df_corp_inicial.query("(UNIDAD_ACADEMICA == @unidad_educativa) and (NIVEL_MATRICULA == @nivel_educativo)").copy()
    df_corp_filtrado['TOTAL_ESTUDIANTES'] = (
        df_corp_filtrado['PROMOVIDO'] + 
        df_corp_filtrado['REPROBADO'] + 
        df_corp_filtrado['NUEVO']
    )

    # Creamos un diccionario inverso para obtener la etiqueta legible 
    # a partir del valor seleccionado en el dropdown
    inverse_dict = {v: k for k, v in unidades_edu.items()}

    # Extraer la etiqueta legible para el gráfico a partir del valor seleccionado en el dropdown
    label_graph = inverse_dict.get(unidad_educativa) 

    


    graph_matricula = px.line(df_corp_filtrado, x='PERIODO', y='TOTAL_ESTUDIANTES',
                               
                      #title=f'Matrícula 2021 - 2026 - {label_graph}',
                      #width=1280, 
                      height=260,
                      template="simple_white",
                      )
            
    graph_matricula.update_traces(
                          mode="markers+lines",
                          textposition='top center',
                          
                          hovertemplate=
                           '<b>Matriculados: </b>%{y}</b>',
                          marker=dict(color='#af0000', size=12),
                          line=dict(width=4, color='#4B4B4B'),
                    )
    
    graph_matricula.update_yaxes(tickfont_weight='normal', 
                         showgrid=True, 
                         tickfont_size=14,
                         showline=False, 
                         ticks="",
                         title_text="",
                         tickfont=dict(color='gray'))
    
    graph_matricula.update_xaxes(tickfont_weight='normal', 
                         tickfont_size=14, 
                         showgrid=True,
                         ticks="", 
                         showline=False,
                         title_text="",
                        tickfont=dict(color='gray'))
    
    graph_matricula.update_layout(
                         hoverlabel_font=dict(family='Roboto mono', weight='bold', size=14, color='black'),
                         font_family='Roboto mono',
                         title_font_weight='bold',
                         title_font_size=20,
                         title_xanchor='left',
                         margin=dict(l=40, r=30, t=10, b=10),
                         showlegend=False,
                         hovermode="x unified",
                         
                         )


    return graph_matricula, texto_final_grafico