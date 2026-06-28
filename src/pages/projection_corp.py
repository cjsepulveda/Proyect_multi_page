import dash
from dash import html, dcc, callback, Input, Output, ALL, State, dash_table, register_page
import dash_bootstrap_components as dbc
import plotly.graph_objects as graph_objects
import pandas as pd

# Importar modulo para calculo de matricula proyectada
from pages.modulos.calculation_projection import (
    calcular_proyeccion_completa, 
    cargar_datos_consolidados, 
    guardar_datos_reales, 
    test_multiple_slider,
    guardar_escenario_simulacion,      
    listar_escenarios_por_unidad,      
    cargar_datos_escenario,
    eliminar_archivo_escenario,
    proyeccion_corporativa,
                 
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
                #'CORPORACIÓN': 'Corporacion',
                'BÁSICA 1':'BÁSICA 1',
                'BÁSICA 2':'BÁSICA 2',
                'BÁSICA SAN FELIPE':'BÁSICA SF',
                'MEDIA LOS ANDES':'MEDIA LOS ANDES',
                'MEDIA SAN FELIPE':'MEDIA SAN FELIPE'}

# Lista de diccionarios para 'options' usando una lista por comprensión
ue_options_dropdown = [{'label': k, 'value': v} for k, v in ue_options.items()]


# Menu Lateral
menu_lateral = dbc.Card([

    # Lista despegable de UNIDAD EDUCATIVA
    html.Div(
        children=[
            html.H5('Unidad Educativa', className="text-primary fw-bold mb-3"),
            dcc.Dropdown(
                id='unidades_educativas', 
                options=ue_options_dropdown,
                value='BÁSICA 1',
                clearable=False,
                className='dropdown'
            ),
        ]),
    html.Br(),
    html.H5("Configuración", className="text-primary fw-bold mb-3"),
    html.Hr(),
    
    # Pestañas para los 20 slider separados en 10 para retencion y 10 para captacion
    dbc.Tabs([
        # Pestaña 1: Controles de Retención
        dbc.Tab(label="Alumnos Nuevos", tab_id="tab-sliders-retencion", children=[
            html.Div([
            # Nuevos Slider retencion
                    html.Label("Nuevos Estudiantes: ", className="fw-bold text-secondary me-1"),
                    html.Hr(),
                    # Crear slider con funcion crear_grupo_sliders para retencion
                    html.Div(id='contenedor-captacion') # contenedor de slider segun unidad educativa elegida

                ], className="pt-2")
             ]),


        dbc.Tab(label="Retención", tab_id="tab-sliders-nuevos", children=[
            html.Div([
                    html.Label(" Tasa de retencion (%):", className="fw-bold text-secondary me-1"),
                    html.Hr(),
                    # Crear slider con funcion crear_grupo_sliders para retencion
                    html.Div(id='contenedor-retencion') # contenedor de slider segun unidad educativa elegida

                ], className="pt-2")
             ]),
      ], id="tabs-sliders-menu", active_tab="tab-sliders-retencion"),

    #Botones para gestion de escenarios"
    html.Br(),
    html.H5("Gestión de Escenarios Simulados", className="text-primary fw-bold mb-2"),
    html.Hr(),
    
    # Campo para escribir el nombre al guardar
    dcc.Input(id="input-nombre-escenario", type="text", placeholder="Ej: Proyeccion 01 BAS1", className="form-control mb-2"),
    
    # Dropdown para seleccionar qué escenario cargar
    dcc.Dropdown(id="dropdown-escenarios-guardados", placeholder="Seleccionar escenario para cargar...", className="mb-3"),
    
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
        className="mt-2"),
    dcc.Download(id="descarga-excel"),
    
], body=True, className="shadow-sm border-0", 
    
)

# Callback para crear slider segun la unidad educativa elegida y buscar escenarios en el output
# ! el output Output('dropdown-escenarios-guardados', 'options') esta duplicado en el callbac cargar datos
@callback(
    [
        Output('contenedor-retencion', 'children'), # Primer Output (retencion)
        Output('contenedor-captacion', 'children')  # Segundo Output (captacion)
    ],
    Output('dropdown-escenarios-guardados', 'options'), # 👈 NUEVO OUTPUT
    Input('unidades_educativas', 'value')           # Origen: la unidad educativa seleccionada
)

def actualizar_sliders(unidad_educativa):
    # Condicional que define por completo cada grupo independiente
    if unidad_educativa in ['BÁSICA 1', 'BÁSICA 2', 'BÁSICA SF']:
        # Grupo completamente definido de 3 sliders
        sliders_retencion = [
            crear_grupo_sliders("Prebásica", "grupo-a", tipo_slider='retencion'),
            crear_grupo_sliders("Primer Ciclo Básica", "grupo-b", tipo_slider='retencion'),
            crear_grupo_sliders("Segundo Ciclo Básica", "grupo-c", tipo_slider='retencion'),
          ]
        
        sliders_capatacion =[
            crear_grupo_sliders("Prebásica", "grupo-a", tipo_slider='nuevos'),
            crear_grupo_sliders("Primer Ciclo Básica",  "grupo-b", tipo_slider='nuevos'),
            crear_grupo_sliders("Segundo Ciclo Básica",  "grupo-c", tipo_slider='nuevos'),
          ]
    else:
        sliders_retencion = [
            crear_grupo_sliders("Enseñanza Media", "grupo-d", tipo_slider='retencion'),
          ]
        
        sliders_capatacion =[
            crear_grupo_sliders("Enseñanza Media", "grupo-d", tipo_slider='nuevos'),
          ]
        
    # Un solo punto de retorno para la variable que contiene el grupo seleccionado

    # 🚀 AGREGADO: Buscamos dinámicamente qué escenarios existen en disco para esta unidad educativa
    opciones_dropdown = listar_escenarios_por_unidad(unidad_educativa)
        
    # Retornamos los tres elementos en el orden exacto de los Outputs de arriba
    return sliders_retencion, sliders_capatacion, opciones_dropdown

# Layaout Genral, Menu Lateral, 2 Tarjetas KPI, Gráfico y Tabla
layout = dbc.Container([
    # COMENTADO: Ya no se utiliza el store para auditar cambios de la tabla
    #dcc.Store(id="store-disparador-cambio", data=0),
    
    # Layaout General, 1 fila, 2 columnas,
    dbc.Row([
        
        # Columna para menu lateral
        dbc.Col(menu_lateral, width=4), 
        
        # Columna para KPI, Gráfico y tabla
        dbc.Col([                       
            # Tarjetas KPI
            html.Div(id="contenedor-kpis", className="mb-4"), # Tarjetas KPI
            
            # Gráfico en formato tarjeta
            dbc.Card([                                        
                dbc.CardHeader(html.H6("Modelación Escenarios Matrículas Corporativas", className="m-0 text-dark")),
                dbc.CardBody(dcc.Graph(config={"displayModeBar": False}, id="grafico-dinamico-completo"))
            ], className="shadow-sm mb-4"),
            
            # Gráfico en formato tarjeta, CORPORACION
            dbc.Card([                                        
                dbc.CardHeader(html.H6("Modelación Escenarios Matrículas Corporativas", className="m-0 text-dark")),
                dbc.CardBody(dcc.Graph(config={"displayModeBar": False}, id="grafico-corp"))
            ], className="shadow-sm mb-4"),


            # Tabla para mostrar el resultado de la proyección
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
                        html.P("Desglose detallado por nivel de enseñanza. Visualiza la transferencia secuencial de alumnos año tras año.", className="text-muted small"),
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
    Output("grafico-corp", "figure"), # 🚀 Grafico CORPORACION
    Input({"type": "slider-retencion", "id": ALL}, "value"), # Lista de 10 porcentajes para retención
    Input({"type": "slider-nuevos", "id": ALL}, "value"),    # Lista de 10 cantidades de alumnos
    Input('unidades_educativas', 'value'), # unidad educativa elegida para filtrar excel
    #Input("store-disparador-cambio", "data"),

)
def actualizar_interfaz_proyeccion(lista_retencion, lista_nuevos, unidad_edu):
    
    # 1. Control de seguridad para que Dash no intente calcular con listas vacías
    if not lista_retencion or not lista_nuevos:
        raise dash.exceptions.PreventUpdate
    
    # obtener el dataframe para el gráfico y enviar
    
    df_corporacion = proyeccion_corporativa()
    df, ultimo_anio_real_str, df_matriz_desglose= calcular_proyeccion_completa(lista_retencion, lista_nuevos, unidad_edu)
    
    # CÁLCULO DE MÉTRICAS PARA TARJETAS KPI ---
    # 1. Matricula Máxima
    fila_max = df.loc[df["Valor"].idxmax()]
    max_valor = fila_max["Valor"]
    max_anio = fila_max["Año"]
    
    # 2. Estado de Alerta (¿Cae abajo de 500 en algún año proyectado?)
    df_proy_solo = df[df["Tipo"] == "Proyección"]
    quiebra_limite = (df_proy_solo["Valor"] < UMBRAL_CRITICO).any()

    # Cálculo matricula año 2035 para mensaje de alerta específico
    valor_2035 = df[df["Año"] == "2035"]["Valor"].values[0]
    
    if quiebra_limite:
        kpi_alerta_texto = f"Riesgo Crítico {'' if valor_2035 < UMBRAL_CRITICO * 0.8 else ''}"
        kpi_alerta_color = "danger"
        
    else:
        kpi_alerta_texto = f"Estable {'' if valor_2035 < UMBRAL_CRITICO * 1.2 else ''}"
        kpi_alerta_color = "success"
        
        
    
# 1. DEFINIR TU VARIABLE O CONDICIÓN
# Ejemplo: si el valor es mayor a 50000 es exitoso, si no, es una alerta.

    valor_condicion = valor_2035

    if valor_condicion > UMBRAL_CRITICO:
        kpi_bg_1 = "bg-success"  # Fondo verde muy suave
    else:
        kpi_bg_1 = "bg-danger"   # Fondo rojo muy suave



# CONSTRUCCIÓN VISUAL DE LAS TARJETAS KPI (Bootstrap)
    kpis_layout = dbc.Row([
        # 1. Primera Columna 
        dbc.Col(dbc.Card([
            dbc.CardBody([
                dbc.Row([ # Fila con dos columnas una texto y otra numérica
                    # Columna de texto
                    dbc.Col([
                            html.H6("Máxima Matrícula", className="text-muted card-subtitle small"),
                            html.Span(f"Año Académico: {max_anio}", className="text-secondary small"),
                    ],
                    width=8,
                    className="d-flex flex-column justify-content-center"
                    ), # Cierre columna Texto

                    # Columna Numérica
                    dbc.Col([
                            html.H6(f"{max_valor:,}", className="text-white fw-bold my-1 fs-2"),
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
        ], className=f"border-start border-{kpi_alerta_color} border-2 shadow-sm h-100"), width=5), # Cierre borde segunda tarjeta
                 

    ], className="g-3", style={"marginTop": "5px"}) # Cierre fila con dos tarjetas
    
        
    # 1. 🚀 CALCULAR RANGO DINÁMICO SEGÚN LOS DATOS ACTUALES DE ESTA ESCUELA
    # Buscamos el valor máximo y mínimo dentro del DataFrame generado
    valor_maximo = int(df["Valor"].max())
    valor_minimo = int(df["Valor"].min())
    
    # Dejamos un 15% de holgura hacia arriba y hacia abajo para que la línea respire
    techo_eje_y = int(valor_maximo * 1.15)
    piso_eje_y = max(0, int(valor_minimo * 0.85)) # El 'max' evita que baje de 0 alumnos si hay valores muy chicos



    # DISEÑO DEL GRÁFICO ---
    magtricula_corp_graph = graph_objects.Figure()
    
    df_reales = df[df["Tipo"] == "Real"]
    df_proy = df[df["Tipo"] == "Proyección"]
    
    magtricula_corp_graph.add_trace(graph_objects.Scatter(
        x=df_reales["Año"], y=df_reales["Valor"], name="Datos Reales",
        mode="lines+markers", 
        marker=dict(color= "#af0000", size=8),
        line=dict(color="#4B4B4B", width=2)
    ))
    
    punto_conexion = df_reales.tail(1)
    df_proy_conectado = pd.concat([punto_conexion, df_proy])
    
    magtricula_corp_graph.add_trace(graph_objects.Scatter(
        x=df_proy_conectado["Año"], y=df_proy_conectado["Valor"], name="Proyección",
        mode="lines+markers",
        marker=dict(color= "#1d1d1d", size=8), 
        line=dict(color="#ffae00", width=2)
    ))
    
    magtricula_corp_graph.update_layout(
        hovermode="x unified", plot_bgcolor="white", height=260,
        margin=dict(l=40, r=30, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hoverlabel_font=dict(family='Roboto mono', weight='bold', size=14, color='black'),
        font_family='Roboto mono',
    )
    magtricula_corp_graph.update_xaxes(showgrid=True, gridcolor="#EAEAEA")
    
     # 3. CORRECCIÓN DEL EJE Y: Reemplazamos los números fijos por tus variables dinámicas
    magtricula_corp_graph.update_yaxes(
                    showgrid=True, 
                    gridcolor="#EAEAEA",
                    range=[piso_eje_y, techo_eje_y]
                    )
    
    # GRAFICO TOTAL CORPORACION
    corp_graph = graph_objects.Figure()
    corp_graph.add_trace(graph_objects.Scatter(
        x=df_corporacion["PERIODO"], y=df_corporacion["MATRICULA"], name="Datos Reales",
        mode="lines+markers", 
        marker=dict(color= "#af0000", size=8),
        line=dict(color="#4B4B4B", width=2)
    ))


    # 1. Preparación de datos para la Tabla 1 (Consolidada)
    tabla_consolidada_data = df.to_dict(orient="records") 

    
    # 2. Preparación dinámica para la Tabla 2 (Matriz por Niveles)
    # Creamos las columnas dinámicamente basándonos en las columnas reales que trae el DataFrame
    columnas_matriz = [{"name": "Curso / Nivel", "id": "NIVEL"}] + [
        {"name": col, "id": col} for col in df_matriz_desglose.columns if col != "NIVEL"
    ]

    # Sólo datos, Lista de diccionarios, cada diccionario es un nivel con años y matrícula
    tabla_matriz_data = df_matriz_desglose.to_dict(orient="records") 

     # Retornamos los cinco elementos alineados con la cabecera
    return (
        magtricula_corp_graph, 
        kpis_layout, 
        tabla_consolidada_data, 
        tabla_matriz_data,  # Inyecta las filas desglosadas
        columnas_matriz, # Inyecta los nombres de las columnas de años
        corp_graph     # GRAFICO TOTAL CORPORACION
    )



# CORREGIDO: Callback para descargar el archivo Excel vinculando los componentes reales
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
    df, _, _ = calcular_proyeccion_completa(lista_retencion, lista_nuevos, unidad_edu)
    df_excel = df.rename(columns={"Año": "Año Académico", "Valor": "Matrícula (Alumnos)", "Tipo": "Estado del Dato"})
    
    return dcc.send_data_frame(df_excel.to_excel, filename="Reporte_Proyeccion_Matriculas.xlsx", sheet_name="Matrículas", index=False)

# Callback para guardar escenario de una unidad educativa específica
@callback(
    Output("mensaje-alerta-escenario", "children"),
    # 🚀 CORRECCIÓN: Agregamos allow_duplicate=True para permitir que este callback actualice las opciones
    Output("dropdown-escenarios-guardados", "options", allow_duplicate=True), # Actualiza la lista desplegable al guardar
    Input("btn-guardar-escenario", "n_clicks"),
    State("unidades_educativas", "value"),
    State("input-nombre-escenario", "value"),
    State({"type": "slider-retencion", "id": ALL}, "value"),
    State({"type": "slider-nuevos", "id": ALL}, "value"),
    prevent_initial_call=True # 👈 Esto es obligatorio si usas allow_duplicate
)
def ejecutar_guardado_escenario(n_clicks, unidad_edu, nombre_escenario, lista_ret, lista_nuevos):
    if not n_clicks:
        raise dash.exceptions.PreventUpdate
        
    if not nombre_escenario or str(nombre_escenario).strip() == "":
        opciones_actuales = listar_escenarios_por_unidad(unidad_edu)
        return "⚠️ Por favor, ingresa un nombre para el escenario antes de guardar.", opciones_actuales

    # Ejecutamos el motor analítico para obtener el DataFrame que queremos respaldar
    df, _, _= calcular_proyeccion_completa(lista_ret, lista_nuevos, unidad_edu)
    
    # Llamamos a tu función del módulo especializado
    exito, mensaje = guardar_escenario_simulacion(unidad_edu, nombre_escenario.strip(), lista_ret, lista_nuevos, df)
    
    # Recargamos las opciones del dropdown para que aparezca el nuevo escenario de inmediato
    nuevas_opciones = listar_escenarios_por_unidad(unidad_edu)
    
    return mensaje, nuevas_opciones

# Callback para CARGAR un escenario en los Sliders
@callback(
    Output({"type": "slider-retencion", "id": ALL}, "value"),
    Output({"type": "slider-nuevos", "id": ALL}, "value"),
    Input("btn-cargar-escenario", "n_clicks"),
    State("dropdown-escenarios-guardados", "value"),
    prevent_initial_call=True
)
def ejecutar_carga_en_sliders(n_clicks, ruta_archivo_escenario):
    if not n_clicks or not ruta_archivo_escenario:
        raise dash.exceptions.PreventUpdate
        
    # Leemos el archivo JSON seleccionado
    datos_escenario = cargar_datos_escenario(ruta_archivo_escenario)
    
    if datos_escenario is None:
        raise dash.exceptions.PreventUpdate
        
    # Extraemos las listas de valores guardadas
    valores_retencion_guardados = datos_escenario.get("valores_retencion", [])
    valores_nuevos_guardados = datos_escenario.get("valores_nuevos", [])
    
    # Retornamos los arreglos directos. Dash se encargará de posicionarlos en orden en los sliders
    return valores_retencion_guardados, valores_nuevos_guardados

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