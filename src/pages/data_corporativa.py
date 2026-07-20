import dash
import pathlib
from dash import html, dcc, callback, Input, Output, ALL, State, dash_table, register_page, no_update, exceptions
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import copy

register_page(
    __name__, 
    name="data_corp",
    top_nav=True,
    path="/datos_corporacion",     
    )

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()
_df01_corp = _df02_cuota_mercado = _df03_cuota_mercado_basica = _df04_cuota_mercado_corp = None # cache en RAM


def load_data_corp():
    """Carga los datos de Excel solo una vez por proceso."""
    global _df01_corp, _df02_cuota_mercado, _df03_cuota_mercado_basica, _df04_cuota_mercado_corp
    # Si ya se cargaron los datos, no hacemos nada.
    if _df01_corp is not None:
        return

    workbook = DATA_PATH.joinpath('data_corp_demo.xlsx')
    _df01_corp = pd.read_excel(workbook, sheet_name='data_corp')
    _df02_cuota_mercado = pd.read_excel(workbook, sheet_name='data_mercado_media')
    _df03_cuota_mercado_basica = pd.read_excel(workbook, sheet_name='data_mercado_basica')
    _df04_cuota_mercado_corp = pd.read_excel(workbook, sheet_name='data_mercado_corp')


def obtener_datos_base():
    load_data_corp()
    return _df01_corp

def obtener_datos_mercado():
    load_data_corp()
    return _df02_cuota_mercado

def obtener_datos_mercado_basica():
    load_data_corp()
    return _df03_cuota_mercado_basica

def obtener_datos_mercado_corp():
    load_data_corp()
    return _df04_cuota_mercado_corp

# Diccionario de Unidades Educativas
unidades_edu = {
                'CORPORACIÓN': 'CORPORACION',
                'BÁSICA 1':'BÁSICA 1',
                'BÁSICA 2':'BÁSICA 2',
                'BÁSICA SAN FELIPE':'BÁSICA SF',
                'MEDIA LOS ANDES':'MEDIA LOS ANDES',
                'MEDIA SAN FELIPE':'MEDIA SAN FELIPE'}

# Lista de diccionarios para 'options' usando una lista por comprensión
unidades_edu_options_dropdown = [{'label': k, 'value': v} for k, v in unidades_edu.items()]

unidades_cuota_mercado = {
                           'CORPORACIÓN' : 'CORPORACION',
                           'PARV BÁSICA 1' :  'PARV BÁSICA 1',
                           'PARV BÁSICA 2' :  'PARV BÁSICA 2',
                           'PARV BÁSICA SAN FELIPE' :  'PARV BÁSICA SAN FELIPE',
                           'BÁSICA 1': 'BÁSICA 1',
                           'BÁSICA 2': 'BÁSICA 2',
                           'BÁSICA SAN FELIPE': 'BÁSICA SAN FELIPE',
                           'MEDIA LOS ANDES':'MEDIA LOS ANDES',
                           'MEDIA SAN FELIPE':'MEDIA SAN FELIPE',
                           
                           
                         }
unidades_cuota_mercado_dropdown = [{'label': k, 'value': v} for k, v in unidades_cuota_mercado.items()]

def nivel_unidad_educativa(unidad_edu):

    # Condicional que define por completo cada grupo independiente
    if unidad_edu in ['BÁSICA 1', 'BÁSICA 2', 'BÁSICA SF']:

        niveles = {
                     'GENERAL': 'GENERAL',
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
                     'GENERAL': 'GENERAL',
                     '1MEDIO': '1MEDIO',
                     '2MEDIO': '2MEDIO',
                     '3MEDIO': '3MEDIO',
                     '4MEDIO': '4MEDIO'}
        
        # Lista de diccionarios para 'options' usando una lista por comprensión
        niveles_options_dropdown = [{'label': k, 'value': v} for k, v in niveles.items()]

    return  niveles_options_dropdown



menu_lateral = html.Div([

    dbc.Row([
        
        html.H6("Datos Corporación: ", className="mt-3 text-dark fw-bold", style={"display": "inline"}),

        dbc.Col(
    # Tarjeta para datos MATRICULA
            dbc.Card([
        dbc.CardHeader(html.Div([
                                    html.H6(
                                        [
                                         html.I(className="fa-solid fa-database me-2"), 
                                         'Data Matrícula'
                                         ],                                        
                                        className="m-0 text-dark", style={"display": "inline"}),
                                        html.Span(id="data", className="text-white fw-bold", style={"display": "inline", "marginLeft": "5px"})
                                    ], className="d-flex align-items-center"),
                                    style={"backgroundColor": "#757575"}  # Color de fondo personalizado
                                ),

        dbc.CardBody([
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
                        value='CORPORACION',
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
            # Lista despegable para los NIVELES de la UNIDAD EDUCATIVA    
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
    ])
    ], className="shadow-sm border-1", # fin tarjeta para data MATRICULA
        
    ), # fin dbc, data MATRICULA
          style={"marginTop": "16px"}),
        
     ]),

   
])

menu_lateral_mercado = html.Div([

    dbc.Row(
        dbc.Col(
        # Tarjeta para CUOTA MERCADO
            dbc.Card([
                dbc.CardHeader(html.Div([
                                    html.H6(
                                        [
                                         html.I(className="fa-solid fa-chart-pie me-2"), 
                                         'Cuota de Mercado'
                                         ],                                        
                                        className="m-0 text-dark", style={"display": "inline"}),
                                        html.Span(id="cuota", className="text-white fw-bold", style={"display": "inline", "marginLeft": "5px"})
                                     ], className="d-flex align-items-center"),
                                    style={"backgroundColor": "#757575"}  # Color de fondo personalizado
                                ),
                dbc.CardBody(
        # Lista despegable para CUOTAS DE MERCADO
                        html.Div(
                                children=[
                                    html.H6(
                                        [
                                        html.I(className="fa-solid fa-people-group me-2"), 
                                        'Niveles Unidades Educativas'
                                        ],
                                        className="text-primary fw-bold mb-3"
                                    ),
                                    dcc.Dropdown(
                                        id='unidades_cuota_mercado', 
                                        options=unidades_cuota_mercado_dropdown,
                                        value='CORPORACION',
                                        clearable=False,
                                        style={
                                                'width': '100%',          # Ancho del dropdown
                                                'backgroundColor': '#f0f0f0', # Color de fondo
                                                'color': '#333333',      # Color del texto
                                                'fontSize': '14px'       # Tamaño de la fuente
                                            },
                                        
                                    ),
                                ]),
                                            )
                            ], className="shadow-sm border-1", # fin tarjeta CUOTA MERCADO
                            
                            ), # fin dbc CUOTA MERCADO
         ),className="mt-3" # fin columna para CUOTA MERCADO
    )
])


# Callback para cambiar opciones de niveles según unidad educativa elegida
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

     # Layaout General, 2 fila, cada fila con 2 columnas,
     dbc.Row([
    
     # Columna para menu lateral
        dbc.Col( menu_lateral, width=4), 

     # Columna para gráficos
        dbc.Col([
            # Tres Pestañas cada una con un gráfico, cada gráfico en una tarjeta
            dbc.Tabs([

              dbc.Tab(label="Matrícula",  tab_id="tab-graf-1", children=[
                            dbc.Card([
                                dbc.CardHeader(html.Div([
                                                        html.H6("Matrículas 2021-2026: ", className="m-0 text-dark", style={"display": "inline"}),
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
                              ], className="shadow-sm mt-3") # fin card
                             ], # fin children Tab
                                 
                         ),
              dbc.Tab(label="Retención",  tab_id="tab-graf-2", children=[
                            dbc.Card([
                                dbc.CardHeader(html.Div([
                                                        html.H6("Retención 2021-2026: ", className="m-0 text-dark", style={"display": "inline"}),
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
                                                        html.H6("Captación 2021-2026: ", className="m-0 text-dark", style={"display": "inline"}),
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

     ]), # Cierre, fila de layaout
     
     # Segunda fila para menu mercado y gráfico mercado
     dbc.Row([
         dbc.Col( menu_lateral_mercado, width=4), 
         
         dbc.Col([
            # Tarjeta para gráfico MERCADO
            dbc.Card([
                dbc.CardHeader(html.Div([
                                        html.H6(" Cuota de Mercado 2020-2025: ", className="m-0 text-dark", style={"display": "inline"}),
                                        html.Span(id="titulo-grafico-cuota-mercado", className="text-white fw-bold", style={"display": "inline", "marginLeft": "5px"})
                                        ], className="d-flex align-items-center"),
                                        style={"backgroundColor":"#BB0C00"}  # Otro color de fondo
                                ),
                dbc.CardBody(
                    dcc.Loading(
                        id="corp-loading-grafico",
                        type="circle",
                        children=dcc.Graph(config={"displayModeBar": False}, id="grafico-corp-mercado"),
                    )
                )
                ], className="shadow-sm mt-3"), # fin card

         ], 
            width=8), 
     ])
  ], fluid=True) # Fin Layaout, cierre dbc.Container

# Callback para opciones gráficos CORPORACION
@callback (
    Output('grafico-matricula-corp', 'figure'),
    Output('titulo-grafico-matricula', 'children'),
    Output('grafico-retencion-corp', 'figure'),
    Output('titulo-grafico-retencion', 'children'),
    Output('grafico-captacion-corp', 'figure'),
    Output('titulo-grafico-captacion', 'children'),
    Output('niveles_educativos', 'disabled'),
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

    if unidad_educativa == "CORPORACION":
        
        df_corp_inicial = obtener_datos_base()
        df_corp_drop = df_corp_inicial.drop(columns='UNIDAD_ACADEMICA')
        df_corp_drop["RETENCION"] = df_corp_drop["RETENCION"].replace(0, np.nan)
        df_corp_sum_mean = df_corp_drop.groupby('PERIODO').agg({
            'PROMOVIDO' : 'sum',
            'REPROBADO' : 'sum',
            'NUEVO'     : 'sum',
            'RETENCION' : 'mean'
                                }).reset_index()

        df_corp_sum_mean['TOTAL_ESTUDIANTES'] = (
            df_corp_sum_mean['PROMOVIDO'] + 
            df_corp_sum_mean['REPROBADO'] + 
            df_corp_sum_mean['NUEVO']
            )        
        df_corp_filtrado = df_corp_sum_mean

        disabled_level_grade = True

    else:

        if nivel_educativo == "GENERAL":

            df_corp_inicial = obtener_datos_base()
            df_corp_filter_ue = df_corp_inicial.query("UNIDAD_ACADEMICA == @unidad_educativa").copy()
            df_corp_ue_drop = df_corp_filter_ue.drop(columns='NIVEL_MATRICULA')
            df_corp_ue_drop["RETENCION"] = df_corp_ue_drop["RETENCION"].replace(0, np.nan)
            df_corp_sum_mean = df_corp_ue_drop.groupby('PERIODO').agg({
            'PROMOVIDO' : 'sum',
            'REPROBADO' : 'sum',
            'NUEVO'     : 'sum',
            'RETENCION' : 'mean'
                                }).reset_index()
            df_corp_sum_mean['TOTAL_ESTUDIANTES'] = (
            df_corp_sum_mean['PROMOVIDO'] + 
            df_corp_sum_mean['REPROBADO'] + 
            df_corp_sum_mean['NUEVO']
            )
            df_corp_filtrado = df_corp_sum_mean
     
            disabled_level_grade = False
        
        else: 

            df_corp_inicial = obtener_datos_base()
            df_corp_filtrado = df_corp_inicial.query("(UNIDAD_ACADEMICA == @unidad_educativa) and (NIVEL_MATRICULA == @nivel_educativo)").copy()
            df_corp_filtrado['TOTAL_ESTUDIANTES'] = (
                df_corp_filtrado['PROMOVIDO'] + 
                df_corp_filtrado['REPROBADO'] + 
                df_corp_filtrado['NUEVO']
                )
            
            disabled_level_grade = False
    
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
            txt_final_graph_captacion,
            disabled_level_grade 
            )

# Callback para opciones graficos MERCADO
@callback(
        Output('grafico-corp-mercado', 'figure'),
        Input('unidades_cuota_mercado','value'),
        )
def mercado_graficos(unidad_mercado):

    if unidad_mercado == "CORPORACION":
        
        df_corp_mercado = obtener_datos_mercado_corp()
        df_corp_filter_mercado = df_corp_mercado.copy()
    
    elif unidad_mercado in ["MEDIA LOS ANDES", "MEDIA SAN FELIPE"]:
        df_corp_mercado = obtener_datos_mercado()
        df_corp_filter_mercado = df_corp_mercado.query("UNIDAD_ACADEMICA == @unidad_mercado").copy()
    
    else:
        df_corp_mercado = obtener_datos_mercado_basica()
        df_corp_filter_mercado = df_corp_mercado.query("UNIDAD_ACADEMICA == @unidad_mercado").copy()
    
    grafico_mercado = generar_grafico_mercado(df_corp_filter_mercado, unidad_mercado)
    
    return grafico_mercado

# Funcion para crear graficos Matrícula, retencion y Captación
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
                      height=380,
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

# Funcion para crear grafico MERCADO
def generar_grafico_mercado(data_mercado_unidad, unidad_mercado_grafico):

    df_mercado = data_mercado_unidad
    
    if unidad_mercado_grafico == "CORPORACION":
        data_agrupado = ["MAT_CORPORACION", "SAN FELIPE", "LOS ANDES"]
        color_data_agrupado = ["#3067FD","#FFA21F","#3FBD3F" ]
        df_mercado["TOTAL"] = df_mercado[data_agrupado].sum(axis=1)

    elif unidad_mercado_grafico in ["MEDIA LOS ANDES", "MEDIA SAN FELIPE"]:
        
        data_agrupado = ["MAT_CORPORACION", "TP_PROVINCIA", "HC_PROVINCIA"]
        color_data_agrupado = ["#3067FD","#FFA21F","#3FBD3F" ]
        df_mercado["TOTAL"] = df_mercado[data_agrupado].sum(axis=1)

    else:

        data_agrupado = ["MAT_CORPORACION", "BASICAS_PROV"]
        color_data_agrupado = ["#3067FD","#FFA21F"]
        df_mercado["TOTAL"] = df_mercado[data_agrupado].sum(axis=1)

    
    
 
    graph_mercado = go.Figure()

    for mercado, color in zip(data_agrupado, color_data_agrupado):

        porcentaje_mercado = ((df_mercado[mercado]/df_mercado["TOTAL"])*100).round(1)

        graph_mercado.add_trace(
        go.Bar(
            x=df_mercado['PERIODO'], 
            y=df_mercado[mercado], 
            marker_color = color,
            name=mercado,
            text = porcentaje_mercado.astype(str) + "%",
            textposition= "inside",
            insidetextanchor= "middle",
            textfont=dict(
            size=16,                     
            color="white",
            weight = "bold"                                
            ),
            customdata=df_mercado[mercado],
            hovertemplate=f"<b>{mercado}</b>"
                           ": %{customdata:,}"
                           "<extra></extra>"
             )
         )
        
    if unidad_mercado_grafico in ['PARV BÁSICA 1','PARV BÁSICA 2','PARV BÁSICA SAN FELIPE']:
        graph_mercado.update_traces(name="PARV_PROVINCIA", selector=dict(name="BASICAS_PROV"))
    
    graph_mercado.update_layout(
                                    hoverlabel_font=dict(family='Roboto mono', weight='bold', size=14, color='black'),
                                    font_family='Roboto mono',
                                    template="simple_white",
                                    barmode='stack',
                                    barnorm='percent',  # Escala automáticamente las barras al 100%
                                    yaxis_ticksuffix='%',  # Añade el símbolo % al eje Y
                                    # legend_title_text='Categorías',
                                    margin=dict(l=40, r=30, t=10, b=10),
                                    hovermode="x unified" 
                                    )
        
    graph_mercado.update_xaxes(tickfont_weight='normal', 
                         tickfont_size=14, 
                         showgrid=False,
                         ticks="", 
                         showline=False,
                         title_text="",
                         tickfont=dict(color='gray'),
                         )
        
    graph_mercado.update_yaxes(tickfont_weight='normal', 
                         showgrid=False, 
                         tickfont_size=14,
                         showline=False, 
                         ticks="",
                         title_text="",
                         #tickformat= ".0%",
                         tickfont=dict(color='gray'),
                         )


    return graph_mercado