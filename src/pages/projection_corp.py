import dash
from dash import html, dcc, callback, Input, Output, State, dash_table, register_page
import dash_bootstrap_components as dbc
import plotly.graph_objects as graph_objects
import pandas as pd

# Importamos el motor matemático unificado
from pages.modulos.calculation_projection import calcular_proyeccion_completa, cargar_datos_consolidados, guardar_datos_reales

register_page(
    __name__, 
    name="Proyección 8 Años",
    top_nav=True,
    path="/proyeccion",     
    )

UMBRAL_CRITICO = 700

# (El objeto 'menu_lateral' se mantiene idéntico al bloque anterior)
menu_lateral = dbc.Card([
    html.H5("Factores Globales", className="text-primary fw-bold mb-3"),
    html.Hr(),
   
    # --- SLIDER 1 ---
    html.Div([
        html.Label("Tasa de Retención (%): ", className="fw-bold text-secondary me-1"),
        html.Span("85%", id="val-retencion", className="fw-bold text-primary") # 👈 Aquí se verá el valor
    ], className="d-flex justify-content-between mb-1"),
    dcc.Slider(
        id="sl-retencion", min=50, max=100, step=1, value=85, 
        marks={i: f"{i}%" for i in range(50, 101, 10)},
        updatemode="drag" # 👈 Clave para que responda de inmediato al arrastrar
    ),
    html.Br(),
    
    html.Label("Captación Nuevos Alumnos", className="fw-bold text-secondary"),
    dcc.Slider(id="sl-captacion", min=100, max=1000, step=50, value=80, marks={i: str(i) for i in range(100, 1001, 200)}),
    html.Br(),
    html.Label("Crecimiento Población (%)", className="fw-bold text-secondary"),
    dcc.Slider(id="sl-crecimiento", min=-5, max=10, step=0.5, value=0, marks={i: f"{i}%" for i in range(-5, 11, 3)}),
    html.Hr(),
    dbc.Button("Exportar Proyección a Excel", id="btn-exportar-excel", color="success", className="w-100 mt-2"),
    dcc.Download(id="descarga-excel")
], body=True, className="shadow-sm border-0 bg-light", style={"min-height": "80vh"})

layout = dbc.Container([
    dcc.Store(id="store-disparador-cambio", data=0),
    
    dbc.Row([
        dbc.Col(menu_lateral, width=3),
        
        dbc.Col([
            html.Div(id="contenedor-kpis", className="mb-4"),
            
            dbc.Card([
                dbc.CardHeader(html.H4("Modelo Predictivo de Matrículas Corporativas", className="m-0 text-dark")),
                dbc.CardBody(dcc.Graph(id="grafico-dinamico-completo"))
            ], className="shadow-sm mb-4"),
            
            dbc.Tabs([
                dbc.Tab(label=" Auditoría e Ingreso de Datos Reales", tab_id="tab-ingreso", children=[
                    html.Div([
                        html.P("La siguiente tabla muestra el historial consolidado extraído de Power Query (Excel). Puede editar cualquier celda o añadir el valor del año en curso para ajustar la proyección futura dinámicamente.", className="text-muted small"),
                        
                        # 📊 TABLA INTERACTIVA CONFIGURADA CON FILAS AÑADIBLES
dash_table.DataTable(
    id="tabla-datos-reales",
    columns=[
        {"name": "Año Académico", "id": "Año", "editable": True},
        {"name": "Matrícula Real Efectiva", "id": "Valor Real", "type": "numeric", "editable": True}
    ],
    row_deletable=True,
    style_cell={"textAlign": "center", "padding": "8px"},
    style_header={"backgroundColor": "#f8f9fa", "fontWeight": "bold"},
    # SE ELIMINÓ className="mb-3"
    # Se reemplaza por style_table para aplicar el margen inferior (equivalente a mb-3)
    style_table={"marginBottom": "1rem"} 
),
                        html.Div([
                            dbc.Button("Añadir Nuevo Año Académico", id="btn-anadir-fila", color="secondary", size="sm", className="me-2"),
                            dbc.Button("Guardar Cambios en Sistema", id="btn-guardar-tabla", color="primary", size="sm")
                        ])
                    ], className="p-3")
                ]),
            ], id="tabs-gestion", active_tab="tab-ingreso")
        ], width=9)
    ])
], fluid=True)


# 🔄 CALLBACK 1: Carga el Historial desde Excel y Gestiona las Ediciones del Usuario
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

# (Los callbacks 'actualizar_interfaz_proyeccion' y 'exportar_a_excel' se mantienen idénticos)



# 🔄 CALLBACK 2: Actualiza Gráfico AND Genera Tarjetas KPI de Forma Simultánea
@callback(
    Output("grafico-dinamico-completo", "figure"),
    Output("contenedor-kpis", "children"), # 👈 Inyecta las tarjetas aquí
    Input("sl-retencion", "value"),
    Input("sl-captacion", "value"),
    Input("sl-crecimiento", "value"),
    Input("store-disparador-cambio", "data")
)
def actualizar_interfaz_proyeccion(retencion, captacion, crecimiento, _):
    df, ultimo_anio_real = calcular_proyeccion_completa(retencion, captacion, crecimiento)
    
    # --- 🧮 CÁLCULO DE MÉTRICAS PARA TARJETAS KPI ---
    # 1. Pico Máximo
    fila_max = df.loc[df["Valor"].idxmax()]
    max_valor = fila_max["Valor"]
    max_anio = fila_max["Año"]
    
    # 2. Estado de Alerta (¿Cae abajo de 3500 en algún año proyectado?)
    df_proy_solo = df[df["Tipo"] == "Proyección"]
    quiebra_limite = (df_proy_solo["Valor"] < UMBRAL_CRITICO).any()
    
    if quiebra_limite:
        kpi_alerta_texto = "Riesgo Crítico"
        kpi_alerta_color = "danger"
        kpi_alerta_sub = f"Matrícula inferior a {UMBRAL_CRITICO}"
    else:
        kpi_alerta_texto = "Estable"
        kpi_alerta_color = "success"
        kpi_alerta_sub = "Estructura sobre el límite"
        
    # 3. Crecimiento Neto (Desde el último año real hasta el final del horizonte 2035)
    valor_inicial_proy = df[df["Año"] == ultimo_anio_real]["Valor"].values[0]
    valor_final_proy = df.iloc[-1]["Valor"]
    pct_crecimiento = ((valor_final_proy - valor_inicial_proy) / valor_inicial_proy) * 100
    
    # --- 🏗️ CONSTRUCCIÓN VISUAL DE LAS TARJETAS KPI (Bootstrap) ---
    kpis_layout = dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("Pico Máximo de Matrícula", className="text-muted card-subtitle small"),
                html.H3(f"{max_valor:,}", className="text-primary fw-bold my-1"),
                html.Span(f"Año Académico: {max_anio}", className="text-secondary small")
            ])
        ], className="border-start border-primary border-4 shadow-sm")),
        
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("Condición de Capacidad", className="text-muted card-subtitle small"),
                html.H3(kpi_alerta_texto, className=f"text-{kpi_alerta_color} fw-bold my-1"),
                html.Span(kpi_alerta_sub, className="text-secondary small")
            ])
        ], className=f"border-start border-{kpi_alerta_color} border-4 shadow-sm")),
        
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H6("Proyección Neta Total", className="text-muted card-subtitle small"),
                html.H3(f"{pct_crecimiento:+.1f}%", className=f"text-{'success' if pct_crecimiento >= 0 else 'danger'} fw-bold my-1"),
                html.Span(f"Periodo post-{ultimo_anio_real} a 2035", className="text-secondary small")
            ])
        ], className=f"border-start border-{'success' if pct_crecimiento >= 0 else 'danger'} border-4 shadow-sm"))
    ], className="g-3", style={"marginTop": "15px"})
    
    # --- 📈 DISEÑO DEL GRÁFICO ---
    fig = graph_objects.Figure()
    
    #fig.add_shape(
       # type="rect", x0=df["Año"].min(), x1=df["Año"].max(), y0=0, y1=UMBRAL_CRITICO,
        #fillcolor="rgba(230, 57, 70, 0.07)", #bordercolor="rgba(230, 57, 70, 0.2)",
        #borderwidth=1, 
        #line=dict(dash="dot",color="red"), layer="below"
    #)
    #fig.add_trace(graph_objects.Scatter(
     #   x=df["Año"], y=[UMBRAL_CRITICO] * len(df), name="Límite Institucional",
      #  mode="lines", line=dict(color="#e63946", width=1.5, dash="dashdot")
    #))
    
    df_reales = df[df["Tipo"] == "Real"]
    df_proy = df[df["Tipo"] == "Proyección"]
    
    fig.add_trace(graph_objects.Scatter(
        x=df_reales["Año"], y=df_reales["Valor"], name="Historial Real",
        mode="lines+markers", line=dict(color="#1d3557", width=4)
    ))
    
    punto_conexion = df_reales.tail(1)
    df_proy_conectado = pd.concat([punto_conexion, df_proy])
    
    fig.add_trace(graph_objects.Scatter(
        x=df_proy_conectado["Año"], y=df_proy_conectado["Valor"], name="Proyección Simulada",
        mode="lines+markers", line=dict(color="#f4a261", width=3, dash="dash")
    ))
    
    fig.update_layout(
        hovermode="x unified", plot_bgcolor="white", height=350,
        margin=dict(l=40, r=30, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    fig.update_xaxes(showgrid=True, gridcolor="#EAEAEA")
    fig.update_yaxes(showgrid=True, gridcolor="#EAEAEA",range=[0, 2000])
    
    print(df)

    return fig, kpis_layout



# 🔄 CALLBACK 3: Descarga de archivo Excel (Se mantiene idéntico)
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
