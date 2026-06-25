import dash
from dash import html, dcc, callback, Input, Output, ALL, State, dash_table, register_page
import dash_bootstrap_components as dbc
import plotly.graph_objects as graph_objects
import pandas as pd

# Importar modulo para calculo de matricula proyectada
from pages.modulos.calculation_projection import calcular_proyeccion_completa, cargar_datos_consolidados, guardar_datos_reales, test_multiple_slider
from pages.modulos.slider_creation import crear_grupo_sliders 

register_page(
    __name__, 
    name="Proyección 8 Años",
    top_nav=True,
    path="/proyeccion",     
    )

UMBRAL_CRITICO = 600

# Menu Lateral
menu_lateral = dbc.Card([
    html.H5("Configuración", className="text-primary fw-bold mb-3"),
    html.Hr(),
    
    # Pestañas para los 20 slider separados en 10 para retencion y 10 para captacion
    dbc.Tabs([
        # Pestaña 1: Controles de Retención
        dbc.Tab(label="Retención", tab_id="tab-sliders-retencion", children=[
            html.Div([
            # Nuevos Slider retencion
                    html.Label(" Tasa de retencion (%):", className="fw-bold text-secondary me-1"),
                    html.Hr(),
                    # Crear slider con funcion crear_grupo_sliders para retencion
                    crear_grupo_sliders("Prebásica", "grupo-a", tipo_slider='retencion'),
                    crear_grupo_sliders("Primer Ciclo Básica", "grupo-b", tipo_slider='retencion'),
                    crear_grupo_sliders("Segundo Ciclo Básica", "grupo-c", tipo_slider='retencion'),
                ], className="pt-2")
             ]),


        dbc.Tab(label="Alumnos Nuevos", tab_id="tab-sliders-nuevos", children=[
            html.Div([
                    html.Label(" Nuevos Estudiantes:", className="fw-bold text-secondary me-1"),
                    html.Hr(),
                    # Crear slider con funcion crear_grupo_sliders para estudiantes nuevos
                    crear_grupo_sliders("Prebásica", "grupo-a", tipo_slider='nuevos'),
                    crear_grupo_sliders("Primer Ciclo Básica",  "grupo-b", tipo_slider='nuevos'),
                    crear_grupo_sliders("Segundo Ciclo Básica",  "grupo-c", tipo_slider='nuevos'),

                ], className="pt-2")
             ]),
      ], id="tabs-sliders-menu", active_tab="tab-sliders-retencion"),

    dbc.Button(
        [
            html.I(className="fas fa-file-excel me-2"), 
            "Exportar Proyección"
        ],
        id="btn-exportar-excel", 
        color="primary", 
        className="mt-2"),
    dcc.Download(id="descarga-excel"),
    
], body=True, className="shadow-sm border-0", 
    
)   

# Layaout Genral, Menu Lateral, 2 Tarjetas KPI, Gráfico y Tabla
layout = dbc.Container([
    dcc.Store(id="store-disparador-cambio", data=0),
    
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
            
            # Tabla para ingresar o cambiar datos
            dbc.Tabs([
                dbc.Tab(label="Datos Reales", tab_id="tab-ingreso", children=[
                    html.Div([
                        html.P("La siguiente tabla muestra el historial de matriculas. Puede editar cualquier celda o añadir el valor del año en curso para ajustar la proyección futura dinámicamente.", className="text-muted small"),
                        
            # Tabla interactiva
                dash_table.DataTable(
                                id="tabla-datos-reales",
                                columns=[
                                        {"name": "Año Académico", "id": "Año", "editable": True},
                                        {"name": "Matrícula Real Efectiva", "id": "Valor Real", "type": "numeric", "editable": True}
                                    ],
                                row_deletable=True,
                                style_cell={"textAlign": "center", "padding": "8px"},
                                style_header={"backgroundColor": "#f8f9fa", "fontWeight": "bold"},
                                style_table={"marginBottom": "1rem"} 
                                ),
                        html.Div([
                            dbc.Button("Añadir Nuevo Año Académico", id="btn-anadir-fila", color="secondary", size="sm", className="me-2"),
                            dbc.Button("Guardar Cambios en Sistema", id="btn-guardar-tabla", color="primary", size="sm")
                        ])
                    ], className="p-3")
                ]),
            ], id="tabs-gestion", active_tab="tab-ingreso", className="shadow-sm bg-white rounded"), # fin tabla configuracion

         # CORREGIDO: Sección de Pruebas sin márgenes disruptivos
            html.Div([
                html.H5("Consola de Verificación del DataFrame (Modo Test)", className="fw-bold text-secondary mt-4"),
                html.Pre(id="salida-dataframe", style={
                    "backgroundColor": "#212529", 
                    "color": "#00ff66", 
                    "padding": "15px", 
                    "borderRadius": "5px",
                    "fontFamily": "monospace",
                    "fontSize": "12px"
                })
            ], className="mt-3"),

        ], width=8) # Fin columna diagrama general
    ])
], fluid=True) # Fin Layaout para leer en aap.py


# Callback para cargar el Historial desde Excel y Gestiona las Ediciones del Usuario
@callback(
    Output("tabla-datos-reales", "data"),
    Output("store-disparador-cambio", "data"),
    Input("btn-guardar-tabla", "n_clicks"),
    Input("btn-anadir-fila", "n_clicks"),
    State("tabla-datos-reales", "data"),
    State("store-disparador-cambio", "data"),
    prevent_initial_call=False
)
def gestionar_tabla_auditoria(n_guardar, n_anadir, filas_tabla, contador_disparador):
    ctx = dash.callback_context
    
    # Determinar qué botón gatilló la acción
    disparador_id = ctx.triggered[0]["component_id"] if ctx.triggered else None
    
    # ACCIÓN A: El usuario añade una fila vacía para registrar un año nuevo (ej. a mitad de año)
    if disparador_id == "btn-anadir-fila":
        filas_tabla.append({"Año": "", "Valor Real": ""})
        return filas_tabla, contador_disparador
        
    # ACCIÓN B: El usuario presiona Guardar Cambios
    if disparador_id == "btn-guardar-tabla" and filas_tabla:
        nuevo_dict_web = {}
        for fila in filas_tabla:
            # Validamos que la fila tenga año y valor numérico antes de guardar en el JSON
            if fila["Año"] and fila["Valor Real"] is not None and str(fila["Valor Real"]).strip() != "":
                nuevo_dict_web[str(fila["Año"])] = int(fila["Valor Real"])
        
        guardar_datos_reales(nuevo_dict_web)
        contador_disparador += 1 # Notifica al gráfico que debe redibujarse
        
    # CARGA INICIAL: Lee los datos consolidados (Excel + JSON) para pintar la tabla completa
    dict_consolidado = cargar_datos_consolidados()
    # Ordenamos cronológicamente los años de menor a mayor
    anios_ordenados = sorted(list(dict_consolidado.keys()), key=int)
    
    tabla_data = [{"Año": anio, "Valor Real": dict_consolidado[anio]} for anio in anios_ordenados]
    
    return tabla_data, contador_disparador

# Callback para actualizar Gráfico y Generar Tarjetas KPI de Forma Simultánea
@callback(
    Output("grafico-dinamico-completo", "figure"),
    Output("contenedor-kpis", "children"), # Inyecta las tarjetas aquí
    Output("salida-dataframe", "children"), # salida slider en una tabla
    Input({"type": "slider-retencion", "id": ALL}, "value"), # Lista de 10 porcentajes para retención
    Input({"type": "slider-nuevos", "id": ALL}, "value"),    # Lista de 10 cantidades de alumnos
    Input("store-disparador-cambio", "data"),

)
def actualizar_interfaz_proyeccion(lista_retencion, lista_nuevos, _):
    
    # 1. Control de seguridad para que Dash no intente calcular con listas vacías
    if not lista_retencion or not lista_nuevos:
        raise dash.exceptions.PreventUpdate
    
    # Enviamos la lista completa a tu función del módulo especializado
    resultado_texto = test_multiple_slider(lista_retencion)
    
    df, ultimo_anio_real_str= calcular_proyeccion_completa(lista_retencion, lista_nuevos)
    
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
    magtricula_corp_graph.update_yaxes(showgrid=True, gridcolor="#EAEAEA",range=[200, 2000])
    
    

    return magtricula_corp_graph, kpis_layout, resultado_texto



# Callback para descargar el archivo Excel
@callback(
    Output("descarga-excel", "data"),
    Input("btn-exportar-excel", "n_clicks"),
    State("sl-retencion", "value"),
    State("sl-captacion", "value"),
    State("sl-crecimiento", "value"),
    prevent_initial_call=True
)
def exportar_a_excel(n_clicks, retencion, captacion, crecimiento):
    if n_clicks is None:
        return dash.no_update
    df, _ = calcular_proyeccion_completa(retencion, captacion, crecimiento)
    df_excel = df.rename(columns={"Valor": "Matrícula (Alumnos)", "Tipo": "Estado del Dato"})
    return dcc.send_data_frame(df_excel.to_excel, filename="Reporte_Proyeccion_Matriculas.xlsx", sheet_name="Matrículas", index=False)
