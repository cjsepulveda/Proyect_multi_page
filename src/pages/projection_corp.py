import dash
from dash import html, dcc, callback, Input, Output, ALL, State, dash_table, register_page
import dash_bootstrap_components as dbc
import plotly.graph_objects as graph_objects
import pandas as pd
import copy

import pages.modulos.calculation_projection as proyecciones
# Importar funciones para calculo de matricula proyectada
from pages.modulos.calculation_projection import (
    calcular_proyeccion_completa, 
    #cargar_datos_consolidados, 
    guardar_escenario_simulacion,
    guardar_escenario_corporativo,
    listar_escenarios_por_unidad,
    listar_todos_escenarios_agrupados,
    cargar_datos_escenario,
    eliminar_archivo_escenario,
    proyeccion_corporativa,
    tasas_nuevos_alumnos,  
                 
)
from pages.modulos.slider_creation import crear_grupo_sliders 

register_page(
    __name__, 
    name="Proyección 8 Años",
    top_nav=True,
    path="/proyeccion",     
    )

UMBRAL_CRITICO = 600

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

# Lista de Columnas optimizadas para el menú lateral angosto en la tabla de datos
columnas_verticales = [
    {"name": "Año", "id": "Anio", "editable": False},
    {"name": "Matrícula", "id": "Matricula", "type": "numeric", "editable": True}
]

    
# Menu Lateral
menu_lateral = dbc.Card([

    # Lista despegable de UNIDAD EDUCATIVA
    html.Div(
        children=[
            html.H6('Unidad Educativa ', className="text-primary fw-bold mb-3"),
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
       
    # Contenedor para slider de unidades educativas, se oculta si se elije CORPORACION
    html.Div(
    id='contenedor-configuracion',
    children=[
        html.Br(),
        html.H6("Configuración", className="text-primary fw-bold mb-3"),
        html.Hr(),
        
        # Pestañas para los 20 slider separados en 10 para retencion y 10 para captacion
        dbc.Tabs([
            # Pestaña 1: Alumnos nuevos
            dbc.Tab(label="Alumnos Nuevos", tab_id="tab-sliders-retencion", label_style={'fontSize': '14px'},
                    children=[
                html.Div([
                # Slider alumnos nuevos
                        html.Label("Nuevos Estudiantes: ", className="fw-bold text-secondary me-1", style={"fontSize": "14px"}),
                        html.Hr(),
                        # Crear slider con funcion crear_grupo_sliders para retencion
                        html.Div(id='contenedor-captacion') # contenedor de slider segun unidad educativa elegida

                    ], className="pt-2")
                ]),

            # Pestaña 2: Retencion
            dbc.Tab(label="Retención", tab_id="tab-sliders-nuevos", label_style={'fontSize': '14px'},
                    children=[
                html.Div([
                # Slider retencion
                        html.Label(" Tasa de retencion (%):", className="fw-bold text-secondary me-1", style={"fontSize": "14px"}),
                        html.Hr(),
                        # Crear slider con funcion crear_grupo_sliders para retencion
                        html.Div(id='contenedor-retencion') # contenedor de slider segun unidad educativa elegida

                    ], className="pt-2")
                ]),
        ], id="tabs-sliders-menu", active_tab="tab-sliders-retencion"),
    ]

    ),

    # Dropdown múltiple para vista corporativa
    html.Div(
        id='contenedor-dropdown-corp',
        children=[
            html.Br(),
            html.H6("Escenarios por Unidad", className="text-primary fw-bold mb-2"),
            html.Hr(),
            dcc.Dropdown(
                id='dropdown-escenarios-corp',
                placeholder="Seleccionar escenarios...",
                multi=True,  # ← selección múltiple
                className="mb-3",
                style={
                        'width': '100%',          # Ancho del dropdown
                        'backgroundColor': '#f0f0f0', # Color de fondo
                        'color': '#333333',      # Color del texto
                        'fontSize': '14px'       # Tamaño de la fuente
                      }, 
            )
        ],
        style={'display': 'none'}  # ← oculto por defecto
    ),

   # Botones para gestion de escenarios"
    html.Br(),
    html.H6("Gestión de Escenarios Simulados", className="text-primary fw-bold mb-2"),
    html.Hr(),
    
    # Campo para escribir el nombre al guardar
    dcc.Input(id="input-nombre-escenario", 
              type="text", 
              placeholder="Ej: Proyeccion 01 BAS1", 
              className="form-control mb-2",
              style={"fontSize": "14px"},
              ),
              
    
    # Dropdown para seleccionar qué escenario cargar
    dcc.Dropdown(id="dropdown-escenarios-guardados", 
                 placeholder="Seleccionar escenario para cargar...",
                 style={
                        'width': '100%',          # Ancho del dropdown
                        'backgroundColor': '#f0f0f0', # Color de fondo
                        'color': '#333333',      # Color del texto
                        'fontSize': '14px'       # Tamaño de la fuente
                      }, 
                 className="mb-3"),
    
    # Botones de acción en una fila balanceada
    html.Div([
        dbc.Button("Guardar Escenario", id="btn-guardar-escenario", color="primary", size="sm", className="me-2"),
        dbc.Button("Cargar", id="btn-cargar-escenario", color="warning", size="sm", className="me-2"),
        dbc.Button("Eliminar", id="btn-eliminar-escenario", color="danger", size="sm")
    ], className="d-flex justify-content-start mb-3"),
    
    # Mensaje de confirmación oculto o alerta
    html.Div(id="mensaje-alerta-escenario", className="small text-muted mb-2"),

    # Boton exportar excel
    dbc.Button(
        [
            html.I(className="fas fa-file-excel me-2"), 
            "Exportar Proyección"
        ],
        id="btn-exportar-excel", 
        color="success",
        style={"fontSize": "14px"}, 
        className="mt-2"),
    dcc.Download(id="descarga-excel"),
    
    html.Br(),
    html.Br(),

    # Tabla para ver y modificar valores iniciales
    html.Label("Valores Iniciales Pre-kinder o 1° Medio:", style={'fontWeight': 'bold', "fontSize": "14px"}),
    # Tabla Vertical Interactiva
        dash_table.DataTable(
            id='tabla-matriculas-vertical',
            columns=columnas_verticales,
            editable=True,
            style_cell={
                'textAlign': 'center', 
                'padding': '6px',
                'fontSize': '13px',
                'fontFamily': 'sans-serif'
            },
            style_header={
                'backgroundColor': '#f4f4f4', 
                'fontWeight': 'bold',
                'border': '1px solid #d6d6d6'
            },
            style_data={
                'border': '1px solid #e0e0e0'
            }
        ),
    
    
], body=True, className="shadow-sm border-0", 
    
)

# Callback que convierte el diccionario plano de matriculas iniciales 
# en 10 filas verticales para la tabla
@callback(
    Output('tabla-matriculas-vertical', 'data'),
    Input('unidades_educativas', 'value')
)
def cargar_valores_verticales(unidad_seleccionada):
    # Obtener el diccionario de años de la unidad actual {'2027': 24, '2028': 22, ...}
    
    # Si es Corporación, retornar tabla vacía
    if unidad_seleccionada == 'CORPORACIÓN':
        return []
    
    valores_anios = proyecciones.matriculas_iniciales_default[unidad_seleccionada]
    
    # Transformar a formato de lista de filas verticales
    filas_tabla = []
    for anio, valor in valores_anios.items():
        filas_tabla.append({"Anio": anio, "Matricula": valor})
        
    return filas_tabla

# Callback para crear slider segun la unidad educativa elegida y buscar escenarios en el output
@callback(
    [
        Output('contenedor-retencion', 'children'), # Primer Output (retencion)
        Output('contenedor-captacion', 'children')  # Segundo Output (captacion)
    ],
    Output('dropdown-escenarios-guardados', 'options'), # 👈 Nuevo para cargar escenarios de slider
    Output('dropdown-escenarios-corp', 'options'),  
    Output('contenedor-dropdown-corp', 'style'),          # ← nuevo, escenarios agrupados
    Output('contenedor-configuracion', 'style'),  # ← nuevo, contender slider (visible/oculto)
    Input('unidades_educativas', 'value'),  # Origen: la unidad educativa seleccionada
)
def actualizar_sliders(unidad_educativa):
    
    if unidad_educativa == 'CORPORACIÓN':  # ← agregar este bloque primero
        opciones_dropdown = listar_escenarios_por_unidad(unidad_educativa)
        escenarios_agrupados = listar_todos_escenarios_agrupados()  # ← cargar escenarios
        return [], [], opciones_dropdown, escenarios_agrupados, {'display': 'block'}, {'display': 'none'}  # ← mostrar dropdown
    
    # Condicional que define por completo cada grupo independiente
    if unidad_educativa in ['BÁSICA 1', 'BÁSICA 2', 'BÁSICA SF']:
        tasas = tasas_nuevos_alumnos.get(unidad_educativa, {})  # ← obtener tasas de la unidad
        
        # Grupo completamente definido de 3 sliders
        sliders_retencion = [
            crear_grupo_sliders("Prebásica", "grupo-a", tipo_slider='retencion'),
            crear_grupo_sliders("Primer Ciclo Básica", "grupo-b", tipo_slider='retencion'),
            crear_grupo_sliders("Segundo Ciclo Básica", "grupo-c", tipo_slider='retencion'),
          ]
        
        sliders_captacion =[
            crear_grupo_sliders("Prebásica", "grupo-a", tipo_slider='nuevos',tasas_nivel=tasas),
            crear_grupo_sliders("Primer Ciclo Básica",  "grupo-b", tipo_slider='nuevos',tasas_nivel=tasas),
            crear_grupo_sliders("Segundo Ciclo Básica",  "grupo-c", tipo_slider='nuevos',tasas_nivel=tasas),
          ]
    else:
        
        tasas = tasas_nuevos_alumnos.get(unidad_educativa, {})  # ← obtener tasas de la unidad
        
        sliders_retencion = [
            crear_grupo_sliders("Enseñanza Media", "grupo-d", tipo_slider='retencion'),
          ]
        
        sliders_captacion =[
            crear_grupo_sliders("Enseñanza Media", "grupo-d", tipo_slider='nuevos',tasas_nivel=tasas),
          ]
        
    # Un solo punto de retorno para la variable que contiene el grupo seleccionado

    # 🚀 AGREGADO: Buscamos dinámicamente qué escenarios existen en disco para esta unidad educativa
    opciones_dropdown = listar_escenarios_por_unidad(unidad_educativa)
    
    # Retornamos los tres elementos en el orden exacto de los Outputs de arriba
    return sliders_retencion, sliders_captacion, opciones_dropdown, [], {'display': 'none'}, {'display': 'block'}

# Layaout General, Menu Lateral, 2 Tarjetas KPI, Gráfico y 2 Tablas con pestañas
layout = dbc.Container([
        
    # Layaout General, 1 fila, 2 columnas,
    dbc.Row([
        
        # Columna para menu lateral
        dbc.Col(menu_lateral, width=4), 
        
        # Columna para KPI, 2 pestañas con gráficos y 2 pestañas con tablas
        dbc.Col([                       
            # Tarjetas KPI
            html.Div(id="contenedor-kpis", className="mb-4"), # Tarjetas KPI
            
            # Diseño para gráfico unidad académica
            dbc.Card([
                dbc.CardHeader(html.Div([
                                        html.H6("Modelación Escenarios Matrículas: ", className="m-0 text-dark", style={"display": "inline"}),
                                        html.Span(id="variable-matricula", className="text-white fw-bold", style={"display": "inline", "marginLeft": "5px"})
                                        ], className="d-flex align-items-center")
                ),
                dbc.CardBody(
                    dcc.Loading(
                        id="loading-grafico",
                        type="circle",
                        children=dcc.Graph(config={"displayModeBar": False}, id="grafico-dinamico-completo")
                    )
                )
            ], className="shadow-sm mt-3"), # 'mt-3' separa la tarjeta de la barra de pestañas

            html.Br(),
            # Diseño de dos tabs para las tablas
            dbc.Tabs([
                
                 # Pestaña 1: Resumen de Matrícula Total por Año real y proyectado
                dbc.Tab(label="Tabla de Proyecciones", tab_id="tab-ingreso", children=[
                    html.Div([
                        html.P("La siguiente tabla muestra el desglose numérico detallado de la proyección según los valores actuales de los sliders.", className="text-muted small"),
                        
                        # Tabla de resultados dinámica (No editable)
                        dash_table.DataTable(
                            id="tabla-datos-reales", # Mantenemos el ID original para no romper dependencias
                            columns=[
                                {"name": "Año Académico", "id": "Año"},
                                {"name": "Matrícula Proyectada (Alumnos)", "id": "Valor", "type": "numeric"},
                                {"name": "Estado del Dato", "id": "Tipo"}
                            ],
                            style_cell={"textAlign": "center", "padding": "8px", "fontFamily": "Roboto mono"},
                            style_header={"backgroundColor": "#f8f9fa", "fontWeight": "bold"},
                            style_table={"marginBottom": "1rem"},
                            # Agregamos estilo condicional simple para diferenciar visualmente el dato Real de la Proyección
                            style_data_conditional=[
                                {
                                    'if': {'column_id': 'Tipo', 'filter_query': '{Tipo} eq "Proyección"'},
                                    'color': '#ffae00',
                                    'fontWeight': 'bold'
                                },
                                {
                                    'if': {'column_id': 'Tipo', 'filter_query': '{Tipo} eq "Real"'},
                                    'color': '#af0000',
                                    'fontWeight': 'bold'
                                }
                            ]
                        ),
                    ], className="p-3")
                ]),

                # Pestaña 2: Desagregado por Niveles Educativos
                dbc.Tab(label="Tabla desagregada po Niveles", tab_id="tab-matriz-desglose", children=[
                    html.Div([
                        html.P("Desagregado por nivel de enseñanza. Visualiza la transferencia secuencial de alumnos año tras año.", className="text-muted small"),
                        dash_table.DataTable(
                            id="tabla-matriz-desglose-cursos", # 🚀 ID único para la segunda tabla
                            style_cell={"textAlign": "center", "padding": "6px", "fontFamily": "Roboto mono", "fontSize": "12px"},
                            style_header={"backgroundColor": "#f8f9fa", "fontWeight": "bold"},
                            style_table={"marginBottom": "1rem", "overflowX": "auto"}, # overflowX permite scroll horizontal si hay muchos años
                            # Destacamos visualmente la fila de TOTAL UNIDAD para diferenciarla de los cursos individuales
                            style_data_conditional=[
                                {
                                    'if': {
                                        'filter_query': '{NIVEL} eq "TOTAL UNIDAD"' # 👈 Cambiado de row_index a filter_query
                                    },
                                    'backgroundColor': '#e8f4fd', # Azul muy suave corporativo
                                    'color': '#0056b3',
                                    'fontWeight': 'bold',
                                }
                            ]
                        ),
                    ], className="p-3")
                ]),



            ], id="tabs-gestion", active_tab="tab-ingreso", className="shadow-sm bg-white rounded"),
 # fin tabla configuracion

         ], width=8) # Fin columna diagrama general
    ])
], fluid=True) # Fin Layaout para leer en aap.py

# Callback para actualizar Gráfico y Generar Tarjetas KPI de Forma Simultánea
@callback(
    Output("grafico-dinamico-completo", "figure"),
    Output("contenedor-kpis", "children"), # Inyecta las tarjetas aquí
    Output("tabla-datos-reales", "data"), # 🚀 NUEVO OUTPUT AGREGADO AQUÍ
    Output("tabla-matriz-desglose-cursos", "data"),    # 🚀 NUEVO OUTPUT DATA
    Output("tabla-matriz-desglose-cursos", "columns"), # 🚀 NUEVO OUTPUT COLUMNS DINÁMICAS
    Output("variable-matricula", "children"), # nombre unidad educativa para el titulo de gráfico
        
    Input({"type": "slider-retencion", "id": ALL}, "value"), # Lista de 10 porcentajes para retención
    Input({"type": "slider-nuevos", "id": ALL}, "value"),    # Lista de 10 cantidades de alumnos
    Input('unidades_educativas', 'value'), # unidad educativa elegida para filtrar excel
    Input('tabla-matriculas-vertical', 'data'), # Reacciona si el usuario edita la matrícula inicial
    Input('dropdown-escenarios-corp', 'value'),  # ← nuevo, escenarios corporativos

)
def actualizar_interfaz_proyeccion(lista_retencion, lista_nuevos, unidad_edu, data_tabla_matriculas, escenarios_seleccionados):
    
    # ← Agregar este bloque al inicio
    if unidad_edu == 'CORPORACIÓN':
        titulo_grafico_unidad_educativa = unidad_edu

        # Construir diccionario de escenarios seleccionados
        escenarios_corp = {}
        if escenarios_seleccionados:
            for ruta in escenarios_seleccionados:
                datos = cargar_datos_escenario(ruta)
                if datos:
                    unidad = datos["unidad_educativa"]
                    escenarios_corp[unidad] = datos
    
        # Un solo df_corporacion con escenarios
        df_corporacion = proyecciones.proyeccion_corporativa(
        proyecciones.matriculas_iniciales_default,
        escenarios_corp=escenarios_corp
        )
        
        
        """Cálculo tarjetas KPI CORPORACIÓN"""
               
        # 1. Determinar nivel matrícula critica de unidad educativa, promedio años 2024, 2025 y 2026
        df_real_solo = df_corporacion[df_corporacion["Tipo"] == "Real"]      
        promedio = df_real_solo.loc[df_real_solo['PERIODO'].isin([2024, 2025, 2026]),'MATRICULA'].mean().round().astype(int)
        
        # 1.1 Matrícula año 2026
        valor_2026 = df_corporacion[df_corporacion["PERIODO"] == 2026]["MATRICULA"].values[0]

        # 2. Matricula Máxima
        fila_max = df_corporacion.loc[df_corporacion["MATRICULA"].idxmax()]
        max_valor = fila_max["MATRICULA"]
        max_anio = fila_max["PERIODO"]

        # 3. Estado de Alerta (¿Cae abajo de promedio en algún año proyectado?)
        df_proy_solo = df_corporacion[df_corporacion["Tipo"] == "Proyección"]
        quiebra_limite = (df_proy_solo["MATRICULA"] < valor_2026 * 0.95).any()
        
        # 4. Cálculo matricula año 2035 para mensaje de alerta específico
        valor_2035 = df_corporacion[df_corporacion["PERIODO"] == 2035]["MATRICULA"].values[0]
        
        # 5. Cálculo porcentaje matricula 20235 sobre matricula 2026

        porcentaje_matricula = valor_2035/valor_2026 - 1   

        if quiebra_limite:
            
            if valor_2035 < valor_2026 * 0.9:
                    kpi_alerta_texto = f"Baja Crítica {porcentaje_matricula:.1%}"
                    kpi_alerta_color = "danger"
            else:    
                    kpi_alerta_texto = f"Baja {porcentaje_matricula:.1%}"
                    kpi_alerta_color = "warning"
            
        else:
            
                 
            kpi_alerta_texto = f"Estable {'a la baja' if valor_2035 < valor_2026 * 1 else 
                                          
                                          'al alza' if valor_2035 < valor_2026 * 1.1 else 'alza sostenida'
                                          } {porcentaje_matricula:.1%}"
            kpi_alerta_color = "success"
            
            
        
        # DEFINIR TU VARIABLE O CONDICIÓN
        # Ejemplo: si el valor es mayor a 50000 es exitoso, si no, es una alerta.

        valor_condicion = valor_2035

        if valor_condicion > valor_2026 * 0.95:
            kpi_bg_1 = "bg-success"  # Fondo verde muy suave
        else:
            
            if valor_condicion < valor_2026 * 0.9:

                kpi_bg_1 = "bg-danger"   # Fondo rojo muy suave
            
            else:
                kpi_bg_1 = "bg-warning"   # Fondo rojo muy suave



        # CONSTRUCCIÓN VISUAL DE LAS TARJETAS KPI (Bootstrap)
        kpis_layout = dbc.Row([
            # 1. Primera Columna 
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    dbc.Row([ # Fila con dos columnas una texto y otra numérica
                        # Columna de texto
                        dbc.Col([
                                html.H6("Última Matrícula", className="text-muted card-subtitle small"),
                                html.Span(f"Año Académico: 2026", className="text-secondary small"),
                                
                        ],
                        width=8,
                        className="d-flex flex-column justify-content-center"
                        ), # Cierre columna Texto

                        # Columna Numérica
                        dbc.Col([
                                html.H6(f"{valor_2026:,}", className="text-white fw-bold my-1 fs-2"),
                        ],
                        width=4,
                        className="d-flex flex-column justify-content-center bg-primary text-white py-3 px-1 text-center rounded"
                        ), # Cierre columna numérica
                    ],
                    className="h-100 g-0" # Alinea verticalmente y quita márgenes (gutters)
                    ) # Cierre de la fila
                ]) # Cierre cuerpo tarjeta
            ],className="border-start border-primary border-2 shadow-sm h-100"), width=5), # Cierre borde tarjeta numero 1
            
            # 2. Segunda Columna 
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    dbc.Row([ # Filas con dos columnas, una de texto y otra numérica
                        # Columna de texto
                        dbc.Col([
                                html.H6("Estado matrícula al 2035", className="text-muted card-subtitle small"),
                                html.H6(kpi_alerta_texto, className=f"text-{kpi_alerta_color} fw-bold my-0 me-2"),
                            ],
                        width=8,
                        className="d-flex flex-column justify-content-center"
                        ), # Cierre columna Texto
                        # Columna numérica
                        dbc.Col([
                                html.Span(f"{valor_2035:,} ", className="text-white fw-bold fs-2"),
                        ],
                        width=4,
                        className= f"{kpi_bg_1} d-flex flex-column justify-content-center text-white py-3 px-1 text-center rounded"
                        ), # Cierre columna numérica
                    ],
                    className="h-100 g-0" # Alinea verticalmente y quita márgenes (gutters)
                    ) # Cierre de la fila
                ]) # Cierre cuerpo segunda tarjeta          
            ], className=f"border-start border-{kpi_alerta_color} border-2 shadow-sm h-100"), width=6), # Cierre borde segunda tarjeta
                    

        ], className="g-3", style={"marginTop": "5px"}) # Cierre fila con dos tarjetas


        # CALCULAR RANGO DINÁMICO SEGÚN LOS DATOS ACTUALES DE ESTA ESCUELA
        # Buscamos el valor máximo y mínimo dentro del DataFrame generado
        valor_maximo_corp = int(df_corporacion["MATRICULA"].max())
        valor_minimo_corp = int(df_corporacion["MATRICULA"].min())

        # Dejamos un 25% de holgura hacia arriba y hacia abajo para que la línea respire
        techo_eje_y_corp = int(valor_maximo_corp * 1.15)
        piso_eje_y_corp = max(0, int(valor_minimo_corp * 0.85))

        
        # Gráfico corporativo con valores default
        corp_graph = graph_objects.Figure()
        df_reales_corp = df_corporacion[df_corporacion["Tipo"] == "Real"]
        df_proy_corp = df_corporacion[df_corporacion["Tipo"] == "Proyección"]
        
        corp_graph.add_trace(graph_objects.Scatter(
            x=df_reales_corp["PERIODO"], y=df_reales_corp["MATRICULA"], name="Datos Reales",
            mode="lines+markers",
            marker=dict(color="#af0000", size=8),
            line=dict(color="#4B4B4B", width=2)
        ))
        
        punto_conexion_corp = df_reales_corp.tail(1)
        df_proy_conectado_corp = pd.concat([punto_conexion_corp, df_proy_corp])
        
        corp_graph.add_trace(graph_objects.Scatter(
            x=df_proy_conectado_corp["PERIODO"], y=df_proy_conectado_corp["MATRICULA"], name="Proyección",
            mode="lines+markers",
            marker=dict(color="#1d1d1d", size=8),
            line=dict(color="#ffae00", width=2)
        ))
        
        corp_graph.update_layout(
            hovermode="x unified", plot_bgcolor="white", height=260,
            margin=dict(l=40, r=30, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            font_family='Roboto mono',
        )
        corp_graph.update_xaxes(showgrid=True, gridcolor="#EAEAEA")
        corp_graph.update_yaxes(showgrid=True, 
                                gridcolor="#EAEAEA",
                                range=[piso_eje_y_corp, techo_eje_y_corp],
                                )

        # Preparar datos para la tabla
        df_tabla_corp = df_corporacion.rename(columns={
                                                "PERIODO": "Año",
                                                "MATRICULA": "Valor"
                                             })
        tabla_corp_data = df_tabla_corp.to_dict(orient="records")
        
        # Retornamos valores vacíos para los outputs que no aplican
        return corp_graph, kpis_layout, tabla_corp_data, [], [], titulo_grafico_unidad_educativa
         #      grafico  , kpi . tabla resumen , data desagregada , titulo gráfico



# CODIGO ORIGINAL
    else: 
        # PASO 1: Clonar el diccionario completo primero 
        # (usando tu variable 'matriculas_iniciales_deafault')
        diccionario_completo_actualizado = copy.deepcopy(proyecciones.matriculas_iniciales_default)

        titulo_grafico_unidad_educativa = unidad_edu

        # 1. Validación inicial por si la tabla viene vacía en el primer renderizado
        if not data_tabla_matriculas:
            # Si está vacía, puedes usar el diccionario default directamente para no romper el flujo
            valores_modificados = proyecciones.matriculas_iniciales_default.get(unidad_edu, {})
        else:
            # 2. Reconstruir el diccionario desde la tabla vertical
            valores_modificados = {}
            for fila in data_tabla_matriculas:
                anio = str(fila["Anio"])
                valor_matricula = int(fila["Matricula"]) if fila["Matricula"] is not None else 0
                valores_modificados[anio] = valor_matricula

        # Reemplazamos solo los datos de la unidad modificada dentro del diccionario completo
        diccionario_completo_actualizado[unidad_edu] = valores_modificados

        # Control de seguridad para que Dash no intente calcular con listas vacías
        if not lista_retencion or not lista_nuevos:
            raise dash.exceptions.PreventUpdate
        
        """Importante data frame para generar gráfico corporativo"""
        # Data Frame Corporativo
        df_corporacion = proyeccion_corporativa(
                diccionario_matriculas=diccionario_completo_actualizado,
                unidad_activa=unidad_edu,
                lista_retencion_activa=lista_retencion,
                lista_nuevos_activa=lista_nuevos,
                escenarios_corp=None
                )
        # Data frame para la unidad educativa seleccionada
        df, ultimo_anio_real_str, df_matriz_desglose = calcular_proyeccion_completa(lista_retencion, lista_nuevos, unidad_edu, diccionario_completo_actualizado)
        
       # CÁLCULO DE MÉTRICAS PARA TARJETAS KPI ---
       
       # 1. Determinar nivel matrícula critica de unidad educativa, promedio años 2024, 2025 y 2026
        df_real_solo = df[df["Tipo"] == "Real"]      
        promedio = df_real_solo.loc[df_real_solo['Año'].isin(['2024', '2025', '2026']),'Valor'].mean().round().astype(int)
        
        # 1.1 Matrícula año 2026
        valor_2026 = df[df["Año"] == "2026"]["Valor"].values[0]

        # 2. Matricula Máxima
        fila_max = df.loc[df["Valor"].idxmax()]
        max_valor = fila_max["Valor"]
        max_anio = fila_max["Año"]

        # 3. Estado de Alerta (¿Cae abajo de promedio en algún año proyectado?)
        df_proy_solo = df[df["Tipo"] == "Proyección"]
        quiebra_limite = (df_proy_solo["Valor"] < valor_2026 * 0.9).any()
        
        # 4. Cálculo matricula año 2035 para mensaje de alerta específico
        valor_2035 = df[df["Año"] == "2035"]["Valor"].values[0]
        
        # 5. Cálculo porcentaje matricula 20235 sobre matricula 2026

        porcentaje_matricula = valor_2035/valor_2026 - 1   

        if quiebra_limite:
            
            if valor_2035 < valor_2026 * 0.8:
                    kpi_alerta_texto = f"Baja Crítica {porcentaje_matricula:.1%}"
                    kpi_alerta_color = "danger"
            else:    
                    kpi_alerta_texto = f"Baja {porcentaje_matricula:.1%}"
                    kpi_alerta_color = "warning"
            
        else:
            
                 
            kpi_alerta_texto = f"Estable {'a la baja' if valor_2035 < valor_2026 * 1 else 
                                          
                                          'al alza' if valor_2035 < valor_2026 * 1.1 else 'alza sostenida'
                                          } {porcentaje_matricula:.1%}"
            kpi_alerta_color = "success"
            
            
        
    # DEFINIR TU VARIABLE O CONDICIÓN
    # Ejemplo: si el valor es mayor a 50000 es exitoso, si no, es una alerta.

        valor_condicion = valor_2035

        if valor_condicion > valor_2026 * 0.9:
            kpi_bg_1 = "bg-success"  # Fondo verde muy suave
        else:
            
            if valor_condicion < valor_2026 * 0.8:

                kpi_bg_1 = "bg-danger"   # Fondo rojo muy suave
            
            else:
                kpi_bg_1 = "bg-warning"   # Fondo rojo muy suave



    # CONSTRUCCIÓN VISUAL DE LAS TARJETAS KPI (Bootstrap)
        kpis_layout = dbc.Row([
            # 1. Primera Columna 
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    dbc.Row([ # Fila con dos columnas una texto y otra numérica
                        # Columna de texto
                        dbc.Col([
                                html.H6("Última Matrícula", className="text-muted card-subtitle small"),
                                html.Span(f"Año Académico: 2026", className="text-secondary small"),
                                
                        ],
                        width=8,
                        className="d-flex flex-column justify-content-center"
                        ), # Cierre columna Texto

                        # Columna Numérica
                        dbc.Col([
                                html.H6(f"{valor_2026:,}", className="text-white fw-bold my-1 fs-2"),
                        ],
                        width=4,
                        className="d-flex flex-column justify-content-center bg-primary text-white py-3 px-1 text-center rounded"
                        ), # Cierre columna numérica
                    ],
                    className="h-100 g-0" # Alinea verticalmente y quita márgenes (gutters)
                    ) # Cierre de la fila
                ]) # Cierre cuerpo tarjeta
            ],className="border-start border-primary border-2 shadow-sm h-100"), width=5), # Cierre borde tarjeta numero 1
            
            # 2. Segunda Columna 
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    dbc.Row([ # Filas con dos columnas, una de texto y otra numérica
                        # Columna de texto
                        dbc.Col([
                                html.H6("Estado matrícula al 2035", className="text-muted card-subtitle small"),
                                html.H6(kpi_alerta_texto, className=f"text-{kpi_alerta_color} fw-bold my-0 me-2"),
                            ],
                        width=8,
                        className="d-flex flex-column justify-content-center"
                        ), # Cierre columna Texto
                        # Columna numérica
                        dbc.Col([
                                html.Span(f"{valor_2035:,} ", className="text-white fw-bold fs-2"),
                        ],
                        width=4,
                        className= f"{kpi_bg_1} d-flex flex-column justify-content-center text-white py-3 px-1 text-center rounded"
                        ), # Cierre columna numérica
                    ],
                    className="h-100 g-0" # Alinea verticalmente y quita márgenes (gutters)
                    ) # Cierre de la fila
                ]) # Cierre cuerpo segunda tarjeta          
            ], className=f"border-start border-{kpi_alerta_color} border-2 shadow-sm h-100"), width=6), # Cierre borde segunda tarjeta
                    

        ], className="g-3", style={"marginTop": "5px"}) # Cierre fila con dos tarjetas
        
            
        # 1. 🚀 CALCULAR RANGO DINÁMICO SEGÚN LOS DATOS ACTUALES DE ESTA ESCUELA
        # Buscamos el valor máximo y mínimo dentro del DataFrame generado
        valor_maximo = int(df["Valor"].max())
        valor_minimo = int(df["Valor"].min())
        
        # Dejamos un 25% de holgura hacia arriba y hacia abajo para que la línea respire
        techo_eje_y = int(valor_maximo * 1.25)
        piso_eje_y = max(0, int(valor_minimo * 0.75)) # El 'max' evita que baje de 0 alumnos si hay valores muy chicos

        # Grafico para unidad educativa seleccionada
        unidad_edu_graph = graph_objects.Figure()
        
        df_reales = df[df["Tipo"] == "Real"]
        df_proy = df[df["Tipo"] == "Proyección"]
        
        unidad_edu_graph.add_trace(graph_objects.Scatter(
            x=df_reales["Año"], y=df_reales["Valor"], name="Datos Reales",
            mode="lines+markers", 
            marker=dict(color= "#af0000", size=8),
            line=dict(color="#4B4B4B", width=2)
        ))
        
        punto_conexion = df_reales.tail(1)
        df_proy_conectado = pd.concat([punto_conexion, df_proy])
        
        unidad_edu_graph.add_trace(graph_objects.Scatter(
            x=df_proy_conectado["Año"], y=df_proy_conectado["Valor"], name="Proyección",
            mode="lines+markers",
            marker=dict(color= "#1d1d1d", size=8), 
            line=dict(color="#ffae00", width=2)
        ))
        
        unidad_edu_graph.update_layout(
            hovermode="x unified", plot_bgcolor="white", height=260,
            margin=dict(l=40, r=30, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hoverlabel_font=dict(family='Roboto mono', weight='bold', size=14, color='black'),
            font_family='Roboto mono',
        )
        unidad_edu_graph.update_xaxes(showgrid=True, gridcolor="#EAEAEA")
        
        # CORRECCIÓN DEL EJE Y: Reemplazamos los números fijos por tus variables dinámicas
        unidad_edu_graph.update_yaxes(
                        showgrid=True, 
                        gridcolor="#EAEAEA",
                        range=[piso_eje_y, techo_eje_y]
                        )
        
        # Grafico para la CORPORACION completa
        #corp_graph = graph_objects.Figure()

        #df_reales_corp = df_corporacion[df_corporacion["Tipo"] == "Real"]
        #df_proy_corp = df_corporacion[df_corporacion["Tipo"] == "Proyección"]

        #corp_graph.add_trace(graph_objects.Scatter(
         #   x=df_reales_corp["PERIODO"], y=df_reales_corp["MATRICULA"], name="Datos Reales",
          #  mode="lines+markers", 
           # marker=dict(color= "#af0000", size=8),
            #line=dict(color="#4B4B4B", width=2)
        #))

        #punto_conexion_corp = df_reales_corp.tail(1)
        #df_proy_conectado_corp = pd.concat([punto_conexion_corp, df_proy_corp])

        #corp_graph.add_trace(graph_objects.Scatter(
         #   x=df_proy_conectado_corp["PERIODO"], y=df_proy_conectado_corp["MATRICULA"], name="Proyección",
          #  mode="lines+markers",
           # marker=dict(color= "#1d1d1d", size=8), 
            #line=dict(color="#ffae00", width=2)
        #))

        #corp_graph.update_layout(
         #   hovermode="x unified", plot_bgcolor="white", height=260,
          #  margin=dict(l=40, r=30, t=10, b=10),
           # legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            #hoverlabel_font=dict(family='Roboto mono', weight='bold', size=14, color='black'),
            #font_family='Roboto mono',
        #)

        #corp_graph.update_xaxes(showgrid=True, gridcolor="#EAEAEA")
        
        # CORRECCIÓN DEL EJE Y: Reemplazamos los números fijos por tus variables dinámicas
        #corp_graph.update_yaxes(
         #               showgrid=True, 
          #              gridcolor="#EAEAEA",
                        #range=[piso_eje_y_corp, techo_eje_y_corp]
           #             )

        # 1. Datos para tabla resumen por año
        tabla_consolidada_data = df.to_dict(orient="records") 

        
        # 2. Preparación para la Tabla 2 (Matricula por nivel y año)
        # Creamos las columnas dinámicamente basándonos en las columnas reales que trae el DataFrame
        columnas_matriz = [{"name": "Curso / Nivel", "id": "NIVEL"}] + [
            {"name": col, "id": col} for col in df_matriz_desglose.columns if col != "NIVEL"
        ]

        # Sólo datos, Lista de diccionarios, cada diccionario es un nivel con años y matrícula
        tabla_matriz_data = df_matriz_desglose.to_dict(orient="records") 

        # Retornamos los cinco elementos alineados con la cabecera
        return (
            unidad_edu_graph, # Gráfico unidad educativa
            kpis_layout, # Tarjetas con valores
            tabla_consolidada_data, # Tabla con el resumen por año de la matrícula
            tabla_matriz_data,  # Las filas con los datos desagregados por nivel y año
            columnas_matriz, # Los nombres de las columnas de cada año
            titulo_grafico_unidad_educativa, # título del gráfico
            )

# Callback para DESCARGAR el archivo Excel vinculando los componentes reales
@callback(
    Output("descarga-excel", "data"),
    Input("btn-exportar-excel", "n_clicks"),
    State({"type": "slider-retencion", "id": ALL}, "value"),
    State({"type": "slider-nuevos", "id": ALL}, "value"),
    State('unidades_educativas', 'value'),
    prevent_initial_call=True
)
def exportar_a_excel(n_clicks, lista_retencion, lista_nuevos, unidad_edu):
    if not n_clicks or not lista_retencion or not lista_nuevos:
        return dash.no_update
        
    # Ejecutamos el motor analítico con los mismos datos actuales de la pantalla
    df, _, _ = calcular_proyeccion_completa(
        lista_retencion, 
        lista_nuevos, 
        unidad_edu, 
        proyecciones.matriculas_iniciales_default
        )


    df_excel = df.rename(columns={"Año": "Año Académico", "Valor": "Matrícula (Alumnos)", "Tipo": "Estado del Dato"})
    
    return dcc.send_data_frame(df_excel.to_excel, filename="Reporte_Proyeccion_Matriculas.xlsx", sheet_name="Matrículas", index=False)

# Callback para GUARDAR escenario de una unidad educativa específica
@callback(
    Output("mensaje-alerta-escenario", "children"),
    # 🚀 CORRECCIÓN: Agregamos allow_duplicate=True para permitir que este callback actualice las opciones
    Output("dropdown-escenarios-guardados", "options", allow_duplicate=True), # Actualiza la lista desplegable al guardar
    Input("btn-guardar-escenario", "n_clicks"),
    State("unidades_educativas", "value"),
    State("input-nombre-escenario", "value"),
    State({"type": "slider-retencion", "id": ALL}, "value"),
    State({"type": "slider-nuevos", "id": ALL}, "value"),
    State('tabla-matriculas-vertical', 'data'),
    State('dropdown-escenarios-corp', 'value'),  # ← agregar
    prevent_initial_call=True # 👈 Esto es obligatorio si usas allow_duplicate
)
def ejecutar_guardado_escenario(
                        n_clicks, 
                        unidad_edu, 
                        nombre_escenario, 
                        lista_ret, 
                        lista_nuevos, 
                        data_tabla, 
                        escenarios_seleccionados
                        ):
    if not n_clicks:
        raise dash.exceptions.PreventUpdate
        
    if not nombre_escenario or str(nombre_escenario).strip() == "":
        opciones_actuales = listar_escenarios_por_unidad(unidad_edu)
        return "⚠️ Por favor, ingresa un nombre para el escenario.", opciones_actuales

    # Guardar escenario corporativo
    if unidad_edu == 'CORPORACIÓN':
        # Construir diccionario de receta
        escenarios_por_unidad = {}
        ue_corp = ['BÁSICA 1', 'BÁSICA 2', 'BÁSICA SF', 'MEDIA LOS ANDES', 'MEDIA SAN FELIPE']
        
        for unidad in ue_corp:
            escenarios_por_unidad[unidad] = "default"  # valor inicial
        
        if escenarios_seleccionados:
            for ruta in escenarios_seleccionados:
                datos = cargar_datos_escenario(ruta)
                if datos:
                    escenarios_por_unidad[datos["unidad_educativa"]] = ruta
        
        # Calcular df corporativo para guardar
        df_corp = proyecciones.proyeccion_corporativa(
            proyecciones.matriculas_iniciales_default,
            escenarios_corp={datos["unidad_educativa"]: cargar_datos_escenario(ruta) 
                           for ruta in (escenarios_seleccionados or []) 
                           if cargar_datos_escenario(ruta)}
        )
        
        exito, mensaje = guardar_escenario_corporativo(
            nombre_escenario.strip(), 
            escenarios_por_unidad, 
            df_corp
        )
        
    # Guardar escenario de unidad educativa
    else:
        df, _, _ = calcular_proyeccion_completa(
            lista_ret, lista_nuevos, unidad_edu,
            proyecciones.matriculas_iniciales_default
        )
        valores_tabla = {str(fila["Anio"]): fila["Matricula"] for fila in data_tabla}
        exito, mensaje = guardar_escenario_simulacion(
            unidad_edu, nombre_escenario.strip(), lista_ret, lista_nuevos, df, valores_tabla
        )

    nuevas_opciones = listar_escenarios_por_unidad(unidad_edu)
    return mensaje, nuevas_opciones

# Callback para CARGAR un escenario en los Sliders
@callback(
    Output({"type": "slider-retencion", "id": ALL}, "value"),
    Output({"type": "slider-nuevos", "id": ALL}, "value"),
    Output('tabla-matriculas-vertical', 'data', allow_duplicate=True),  # ← nuevo
    Output('dropdown-escenarios-corp', 'value', allow_duplicate=True),  # ← nuevo, corporativo
    Input("btn-cargar-escenario", "n_clicks"),
    State("dropdown-escenarios-guardados", "value"),
    State({"type": "slider-retencion", "id": ALL}, "value"),  # ← para mantener valores actuales
    State({"type": "slider-nuevos", "id": ALL}, "value"),     # ← para mantener valores actuales
    prevent_initial_call=True
)
def ejecutar_carga_en_sliders(n_clicks, ruta_archivo_escenario, sliders_ret_actuales, sliders_nuevos_actuales):
    if not n_clicks or not ruta_archivo_escenario:
        raise dash.exceptions.PreventUpdate
        
    datos_escenario = cargar_datos_escenario(ruta_archivo_escenario)
    
    if datos_escenario is None:
        raise dash.exceptions.PreventUpdate
    
    # Detectar tipo de escenario
    if datos_escenario.get("tipo") == "corporativo":
        # Cargar escenario corporativo — restaurar dropdown múltiple
        escenarios_por_unidad = datos_escenario.get("escenarios_por_unidad", {})
        # Extraer solo las rutas que no son "default"
        rutas_seleccionadas = [v for v in escenarios_por_unidad.values() if v != "default"]

        return sliders_ret_actuales, sliders_nuevos_actuales, dash.no_update, rutas_seleccionadas
    
    else:
        # Cargar escenario de unidad educativa — comportamiento original
        valores_retencion_guardados = datos_escenario.get("valores_retencion", [])
        valores_nuevos_guardados = datos_escenario.get("valores_nuevos", [])
        valores_tabla = datos_escenario.get("valores_tabla_inicial", {})
        filas_tabla = [{"Anio": anio, "Matricula": valor} for anio, valor in valores_tabla.items()]
        
        return valores_retencion_guardados, valores_nuevos_guardados, filas_tabla, dash.no_update

# Callback para ELIMINAR un escenario en los Sliders
@callback(
    Output("mensaje-alerta-escenario", "children", allow_duplicate=True),
    Output("dropdown-escenarios-guardados", "options", allow_duplicate=True),
    Output("dropdown-escenarios-guardados", "value"), # Resetea el selector visual a vacío
    Input("btn-eliminar-escenario", "n_clicks"),
    State("unidades_educativas", "value"),
    State("dropdown-escenarios-guardados", "value"),
    prevent_initial_call=True
)
def ejecutar_eliminacion_escenario(n_clicks, unidad_edu, ruta_archivo_escenario):
    if not n_clicks or not ruta_archivo_escenario:
        raise dash.exceptions.PreventUpdate
        
    # 1. Borramos el archivo del disco
    _, mensaje = eliminar_archivo_escenario(ruta_archivo_escenario)
    
    # 2. Listamos nuevamente los escenarios vigentes de esta escuela
    nuevas_opciones = listar_escenarios_por_unidad(unidad_edu)
    
    # 3. Retornamos el mensaje, las nuevas opciones y limpiamos la selección
    return mensaje, nuevas_opciones, None