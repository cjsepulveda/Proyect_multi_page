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

              dbc.Tab(label="Matrícula",  tab_id="tab-graf-1", children=[
                            dbc.Card([
                                dbc.CardHeader(html.Div([
                                                        html.H6("Matrículas 2021 - 2026: ", className="m-0 text-dark", style={"display": "inline"}),
                                                        html.Span(id="titulo-grafico-matricula", className="text-white fw-bold", style={"display": "inline", "marginLeft": "5px"})
                                                        ], className="d-flex align-items-center"),
                                                        style={"backgroundColor":"#007bff"}  # Otro color de fondo
                                ),
                                dbc.CardBody(
                                    dcc.Loading(
                                        id="corp-loading-grafico",
                                        type="circle",
                                        children=dcc.Graph(config={"displayModeBar": False}, id="grafico-matricula-corp")
                                    )
                                )
                              ], className="shadow-sm mt-3")
                             ], # fin children Tab
                                 
                         ),
              dbc.Tab(label="Retención",  tab_id="tab-graf-2", children=[
                            dbc.Card([
                                dbc.CardHeader(html.Div([
                                                        html.H6("Retención 2021 - 2026: ", className="m-0 text-dark", style={"display": "inline"}),
                                                        html.Span(id="titulo-grafico-retencion", className="text-white fw-bold", style={"display": "inline", "marginLeft": "5px"})
                                                        ], className="d-flex align-items-center"),
                                                        style={"backgroundColor": "#00B321"}  # Color de fondo personalizado
                                ),
                                dbc.CardBody(
                                    dcc.Loading(
                                        id="corp-loading-grafico",
                                        type="circle",
                                        children=dcc.Graph(config={"displayModeBar": False}, id="grafico-retencion-corp")
                                    )
                                )
                            ], className="shadow-sm mt-3")
                            ],
                         ),
              dbc.Tab(label="Captación",  tab_id="tab-graf-3", children=[
                            dbc.Card([
                                dbc.CardHeader(html.Div([
                                                        html.H6("Captación 2021 - 2026: ", className="m-0 text-dark", style={"display": "inline"}),
                                                        html.Span(id="titulo-grafico-captacion", className="text-white fw-bold", style={"display": "inline", "marginLeft": "5px"})
                                                        ], className="d-flex align-items-center"),
                                                        style={"backgroundColor": "#FFA600"}  # Color de fondo tarjeta personalizado
                                ),
                                dbc.CardBody(
                                    dcc.Loading(
                                        id="corp-loading-grafico",
                                        type="circle",
                                        children=dcc.Graph(config={"displayModeBar": False}, id="grafico-captacion-corp")
                                    )
                                )
                            ], className="shadow-sm mt-3")
                            ],
                         ),
            
            
            
            ],active_tab="tab-graf-1"), # Cierre de pestañas
         
         ], # cierre listas en la columna
            width=8), # fin columna gráfico

     ]) # Cierre, fila de layaout

  ], fluid=True) # Fin Layaout, cierre dbc.Container

# callback para gráficos corporacion
@callback (
    Output('grafico-matricula-corp', 'figure'),
    Output('titulo-grafico-matricula', 'children'),
    Output('grafico-retencion-corp', 'figure'),
    Output('titulo-grafico-retencion', 'children'),
    Output('grafico-captacion-corp', 'figure'),
    Output('titulo-grafico-captacion', 'children'),
    Input('unidades_educativas_corp', 'value'),
    Input('niveles_educativos', 'value'),

)
def graficos_corporativos(unidad_educativa, nivel_educativo):

    valor_unidad_educativa = unidad_educativa
    
    texto_unidad_educativa = next((k for k, v in unidades_edu.items() if v == valor_unidad_educativa), None)
    texto_nivel_educativo = nivel_educativo
    
    txt_final_graph_matricula = texto_unidad_educativa + "-" + " " + texto_nivel_educativo
    txt_final_graph_retencion = texto_unidad_educativa + "-" + " " + texto_nivel_educativo
    txt_final_graph_captacion = texto_unidad_educativa + "-" + " " + texto_nivel_educativo

    

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

    config_graficos_corp = [
        (df_corp_filtrado,"PERIODO","TOTAL_ESTUDIANTES","#ffffff","#5582ff",""),
        (df_corp_filtrado,"PERIODO","RETENCION","#ffffff","#22BB00",".0%"),
        (df_corp_filtrado,"PERIODO","NUEVO","#ffffff","#FFAE00",""),
        ]
    
    lista_graficos_corp = []
    
    for options in config_graficos_corp:
        
        data, data_col_x, data_col_y, color_marker, color_line, num_format = options
        grafico_corporativo = generar_graficos_corp (   data, 
                                                        data_col_x, 
                                                        data_col_y, 
                                                        color_marker, 
                                                        color_line, 
                                                        num_format)
        lista_graficos_corp.append(grafico_corporativo)

    return (lista_graficos_corp[0], 
            txt_final_graph_matricula, 
            lista_graficos_corp[1], 
            txt_final_graph_retencion,
            lista_graficos_corp[2],
            txt_final_graph_captacion
            )

def generar_graficos_corp(df_filtrado, data_x, data_y , marker_color, line_color, formato_num):

    if data_y =="TOTAL_ESTUDIANTES":
        color_border_marker = "#5582ff"
        color_fill = "rgba(85, 130, 255, 0.3)"
        hover_text ="Matrícula"
    
    elif data_y == "RETENCION":
        color_border_marker = "#22BB00"
        color_fill = "rgba(34, 187, 0, 0.3)"
        hover_text ="Retención"

    else:
        color_border_marker = "#FFAE00"
        color_fill = "rgba(255, 174, 0, 0.3)"
        hover_text = "Captación"

    # CALCULAR RANGO DINÁMICO SEGÚN LOS DATOS ACTUALES DE ESTA ESCUELA
        # Buscamos el valor máximo y mínimo dentro del DataFrame generado
    x_min = df_filtrado[data_x].min() - 0.5
    x_max = df_filtrado[data_x].max() + 0.5

    valor_maximo_corp = df_filtrado[data_y].max()
    valor_minimo_corp = df_filtrado[data_y].min()

        # Dejamos un 25% de holgura hacia arriba y hacia abajo para que la línea respire
    techo_eje_y_corp = (valor_maximo_corp * 1.5)
    piso_eje_y_corp = (valor_minimo_corp * 0.0)


    graph = px.line(df_filtrado, x= data_x, y= data_y,
                               
                      #title=f'Matrícula 2021 - 2026 - {label_graph}',
                      #width=1280, 
                      height=260,
                      template="simple_white",
                      )
            
    graph.update_traces(
                          mode="markers+lines",
                          textposition='top center',
                          hovertemplate=
                           f'<b> {hover_text}: </b>%{{y}}</b>',
                          marker=dict(color = marker_color, size = 12, 
                                        line=dict(width = 2,
                                                  color = color_border_marker)),
                          line=dict(width = 4, color = line_color),
                          fill = 'tozeroy',
                          fillcolor = color_fill,
                    )
    
    graph.update_yaxes(tickfont_weight='normal', 
                         showgrid=True, 
                         tickfont_size=14,
                         showline=False, 
                         ticks="",
                         title_text="",
                         tickformat= formato_num,
                         tickfont=dict(color='gray'),
                         range=[piso_eje_y_corp, techo_eje_y_corp])
    
    graph.update_xaxes(tickfont_weight='normal', 
                         tickfont_size=14, 
                         showgrid=True,
                         ticks="", 
                         showline=False,
                         title_text="",
                         tickfont=dict(color='gray'),
                         range=[x_min, x_max])
    
    graph.update_layout(
                         hoverlabel_font=dict(family='Roboto mono', weight='bold', size=14, color='black'),
                         font_family='Roboto mono',
                         title_font_weight='bold',
                         title_font_size=20,
                         title_xanchor='left',
                         margin=dict(l=40, r=30, t=10, b=10),
                         showlegend=False,
                         hovermode="x unified",
                         
                         )
    return graph