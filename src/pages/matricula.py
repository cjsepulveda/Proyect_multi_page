import pathlib
from dash import dcc, html, Input, Output, callback, register_page
import pandas as pd
import plotly.express as px
import os
import datetime
from datetime import timedelta
from dash.dash_table import DataTable
import dash_bootstrap_components as dbc

register_page(
    __name__,
    name='Matrícula',
    top_nav=True,
    path='/matricula'
)

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()
df01 = pd.read_excel(DATA_PATH.joinpath('mat_2026.xlsx'), sheet_name='mat_2026')
df02 = pd.read_excel(DATA_PATH.joinpath('mat_2026.xlsx'), sheet_name='proyeccion_2026')
df03 = pd.read_excel(DATA_PATH.joinpath('mat_2026.xlsx'), sheet_name='genero')
df04 = pd.read_excel(DATA_PATH.joinpath('mat_2026.xlsx'), sheet_name='mat_time')

# Ruta de tu archivo
ruta_archivo = DATA_PATH.joinpath('mat_2026.xlsx')

# Obtener la hora de última modificación (timestamp Unix)
timestamp_mod = os.path.getmtime(ruta_archivo)

# Convertir a objeto datetime
fecha_mod = datetime.datetime.fromtimestamp(timestamp_mod)

# Ajustar Zona Horaria
fecha_menos_3h = fecha_mod + timedelta(hours=-4)

# Formatear como string legible (ej: '2025-12-11 10:30:00')
fecha_actualizada = fecha_mod.strftime('%Y-%m-%d %H:%M:%S')
fecha_actualizada_menos_tres = fecha_menos_3h.strftime('%Y-%m-%d %H:%M:%S')


# Diccionario de Unidades Educativas
ue_options = {
                'CORPORACIÓN': 'Corporacion',
                'BÁSICA 1':'BÁSICA 1',
                'BÁSICA 2':'BÁSICA 2',
                'BÁSICA SAN FELIPE':'BÁSICA SF',
                'MEDIA LOS ANDES':'MEDIA LOS ANDES',
                'MEDIA SAN FELIPE':'MEDIA SAN FELIPE'}

# Lista de diccionarios para 'options' usando una lista por comprensión
ue_options_dropdown = [{'label': k, 'value': v} for k, v in ue_options.items()]

# Inicio aplicacion Dash
#app = Dash(__name__)
# server=app.server

# Diagrama de la aplicación (Una lista despegable y un gráfico)
def layout():    
    
    layout = html.Div(
        children=[
    
    # Marco para lista despegable UNIDAD EDUCATIVA y Fecha Actualización
        html.Div(children=[
    
    # Fecha Actualización
    html.Div(
            children=[
            html.Div("Última actualización", style={'textAlign': 'center', 'color': 'white', 'fontSize': '14px'}),
            html.Div(f"Fecha: {fecha_actualizada_menos_tres}", style={'fontSize': '18px', 'fontWeight': 'bold', 'textAlign': 'center','color': 'white'})
        ],
    ),

    # Lista despegable de UNIDAD EDUCATIVA
    html.Div(
        children=[
            html.Div(children='Unidad Educativa', className='menu-title'),
            dcc.Dropdown(
                id='unidades_educativas', 
                options=ue_options_dropdown,
                
                #[ 
                 # {"label": "CORPORACIÓN", "value": "Corporacion"},
                 # {"label": "BÁSICA 1", "value": "BÁSICA 1"},
                 # {"label": "BÁSICA 2", "value": "BÁSICA 2"},
                 # {"label": "BÁSICA SAN FELIPE", "value": "BÁSICA SF"},
                 # {"label": "MEDIA LOS ANDES", "value": "MEDIA LOS ANDES"},
                 # {"label": "MEDIA SAN FELIPE", "value": "MEDIA SAN FELIPE"},
                                    
                #],
                value='Corporacion',
                clearable=False,
                className='dropdown'
            ),
        ]),

    ],
    className="menu",
    ),

    
    # Marco para el gráfico (dcc.Graph está incorporado en la función update_charts)

        html.Div(id='grafico_matricula' , className="grafico_and_card"),
        
        html.Div(id='grafico_evolucion' , className="grafico-evolucion"),

        html.Div(id='tabla_matricula' , className="wrapper"),



        ])

    return layout

# callback para filtrar gráfico segun unidad educativa
@callback(
        Output('grafico_matricula', 'children'),
        Output('tabla_matricula', 'children'),
        Output('grafico_evolucion', 'children'),
        [Input('unidades_educativas', 'value'),
         ]
        )

# función para trazar grafico de matricula
def update_charts(unidad_edu):

    if unidad_edu == 'Corporacion':
        
        df_time_agrupado_OLD_corp= df04.groupby('MATRICULA').sum().reset_index()
        df_time_agrupado_OLD_corp['MATRICULA'] = pd.to_datetime(df_time_agrupado_OLD_corp['MATRICULA'])
        df_time_agrupado_corp=df_time_agrupado_OLD_corp.drop(columns=['UE'])
        df_time_agrupado_corp['accumulated'] = df_time_agrupado_corp['ESTUDIANTES'].cumsum()
        df_time_agrupado = df_time_agrupado_corp

        #agrupar data frame genero por Femenino y Masculino
        df_genero_agrupado_corp = df03.groupby('Sexo').sum().reset_index()
        df_genero_agrupado_new_corp=df_genero_agrupado_corp.drop(['UNIDAD ACADÉMICA'],axis=1)
        
        df_genero_dict = df_genero_agrupado_new_corp.set_index('Sexo')['RECUENTO'].to_dict()
        masculino_count = df_genero_dict.get('F')
        femenino_count = df_genero_dict.get('M')
        
        #print(df_time_agrupado)
        #print(df_time_agrupado.dtypes)

        #Agrupar data frame para la nueva categoria Corporación, sumando las unidades educativas y eliminando columnas innecesarias
        df_agrupado_corp = df01.groupby('UNI_EDU').sum()
        df_agrupado_in = df_agrupado_corp.reset_index()
        df_agrupado_new = df_agrupado_in.drop(['NIVEL','% META'], axis=1)

        

        # Agregar al dataframe un fila nueva con los totales y calcular porcentaje
        # Calcular los totales para las columnas numéricas
        total_SAE_2026 = df_agrupado_new['SAE_2026'].sum()
        total_MAT_2026 = df_agrupado_new['MAT_2026'].sum()

        # Crear la fila de totales como una lista o diccionario
        fila_total = {'UNI_EDU': 'GENERAL', 'SAE_2026': total_SAE_2026, 'MAT_2026': total_MAT_2026}
                
        # Convertir la fila a un DataFrame temporal (para concatenar)
        df_total = pd.DataFrame([fila_total]) # Importante: pasar la fila dentro de una lista

        # Concatenar el DataFrame original con la fila de totales
        df_agrupado_total = pd.concat([df_agrupado_new, df_total], ignore_index=True)

        # Calcular el porcentaje de 'MAT_2026' respecto a 'SAE_2026'
        df_agrupado_total['% Meta'] = (df_agrupado_total['MAT_2026'] / df_agrupado_total['SAE_2026']) * 100

        select_nivel_subject = df_agrupado_total
        graph_x_axes = 'UNI_EDU'
        color_bar = 'UNI_EDU'
        etiqueta = 'Unidades Educativas'
        
    else:
        #datafreme de fechas, segun unidad educaticativa seleccionada en dropdown
        df_time_agrupado_OLD = df04.query("UE == @unidad_edu").copy() # dataframe como copia para evitar el error de SettingWithCopyWarning al modificar la columna 'MATRICULA' con pd.to_datetime
        df_time_agrupado_OLD['MATRICULA'] = pd.to_datetime(df_time_agrupado_OLD['MATRICULA'])
        df_time_agrupado_pre = df_time_agrupado_OLD.groupby('MATRICULA').sum().reset_index()
        df_time_agrupado_ue = df_time_agrupado_pre.drop(columns=['UE'])
        df_time_agrupado_ue['accumulated'] = df_time_agrupado_ue['ESTUDIANTES'].cumsum()
        df_time_agrupado = df_time_agrupado_ue

        #print(df_time_agrupado)|
        #print(df_time_agrupado.dtypes)

        #filtrado data frame de genero segun unidad educativa seleccionada en dropdown
        df_genero_agrupado_ue= df03.query("`UNIDAD ACADÉMICA` == @unidad_edu")
        df_genero_agrupado_new=df_genero_agrupado_ue.drop(['UNIDAD ACADÉMICA'],axis=1)
        
        df_genero_dict_ue = df_genero_agrupado_new.set_index('Sexo')['RECUENTO'].to_dict()
        masculino_count = df_genero_dict_ue.get('F')
        femenino_count = df_genero_dict_ue.get('M')

        # dataframe filtrado segun unidad educativa seleccionada en dropdown
        df_agrupado_ue = df01.query("UNI_EDU == @unidad_edu")
        df_agrupado_new_ue = df_agrupado_ue.drop(['UNI_EDU','% META'], axis=1)

        # Agregar al datafram un fila nueva con los totales y calcular porcentaje
        # Calcular los totales para las columnas numéricas
        total_SAE_2026_ue = df_agrupado_new_ue['SAE_2026'].sum()
        total_MAT_2026_ue = df_agrupado_new_ue['MAT_2026'].sum()
        
        # Crear la fila de totales como una lista o diccionario
        fila_total_ue = {'NIVEL': 'GENERAL', 'SAE_2026': total_SAE_2026_ue, 'MAT_2026': total_MAT_2026_ue}
                
        # Convertir la fila a un DataFrame temporal (para concatenar)
        df_total_ue = pd.DataFrame([fila_total_ue]) # Importante: pasar la fila dentro de una lista

        # Concatenar el DataFrame original con la fila de totales
        df_agrupado_total_ue = pd.concat([df_agrupado_new_ue, df_total_ue], ignore_index=True)
        
        # Calcular el porcentaje de 'MAT_2026' respecto a 'SAE_2026'
        df_agrupado_total_ue['% Meta'] = (df_agrupado_total_ue['MAT_2026'] / df_agrupado_total_ue['SAE_2026']) * 100

        select_nivel_subject = df_agrupado_total_ue
        graph_x_axes = 'NIVEL'
        color_bar = 'NIVEL'
        etiqueta = 'Niveles'
              
    
    color_03='blue'

    trace01 = px.bar(select_nivel_subject, x=graph_x_axes, y='MAT_2026', 
                     title= 'Matrícula 2026 Corporación Monte Aconcagua',
                     width=1020, height=380,
                     labels={graph_x_axes: '','MAT_2026':''},
                     #barmode='group',
                     color=color_bar,
                     color_discrete_map= {'GENERAL':color_03},
                     template="simple_white",
                     custom_data=['SAE_2026','% Meta'],
                     text_auto=True,
                     
            )
    
    trace01.add_layout_image(                                 
                            source= "assets/Original-Apaisado.png",
                            xref="paper", yref="paper",
                            x=1.0, y=1.15,
                            sizex=0.2, sizey=0.2,
                            xanchor="right", yanchor="bottom",                                
                            )

    trace01.update_traces(hovertemplate=
                          '<b>SAE 2026: </b>%{customdata[0]}</b><br>'+
                          '<b>Mat 2026: </b>%{y:f}<br>'+
                          '<b>% Meta  : </b>%{customdata[1]:.1f} %</b><br>',
                          textfont_size=16, textangle=0, textposition="outside", cliponaxis=False,
                          textfont=dict(weight="bold"),
                          width=0.5,
                          )

    
    trace01.update_yaxes(tickfont_weight='normal', showgrid=True, tickfont_size=15,showline=False, ticks="",
                         tickfont=dict(color='gray'))
    trace01.update_xaxes(tickfont_weight='bold', tickfont_size=12, showline=False, ticks="")
    trace01.update_layout(
                         hoverlabel_font=dict(family='Roboto mono', weight='bold', size=15, color='white'),
                         font_family='Roboto mono',
                         title_font_weight='bold',
                         title_font_size=20,
                         title_x=0.53,
                         title_xanchor='right',
                         xaxis_type='category',
                         showlegend=False,
                         
                         )
    
    # Gráfico de evolución matricula por fecha
    trace02 = px.line(df_time_agrupado, x='MATRICULA', y='accumulated', 
                      title='Evolución Matricula 2026 por fecha',
                      labels={'MATRICULA':'Fecha','accumulated':'Matriculados'},
                      width=1200, height=500,
                      template="simple_white",
                      markers=True,)
    
    trace02.update_traces(
                       marker=dict(color=' #e74040'),   # Change dot size
                       line=dict(width=2, color='gray')      # Change line thickness
                    )
    
    trace02.update_yaxes(tickfont_weight='normal', showgrid=True, tickfont_size=15,showline=False, ticks="",
                         title_text="",
                         tickfont=dict(color='gray'))
    
    trace02.update_xaxes(tickfont_weight='bold', tickfont_size=12, showgrid=True, showline=True,
                         title_text="",
                         tickfont=dict(color='gray'))
    
    trace02.update_layout(
                         hoverlabel_font=dict(family='Roboto mono', weight='bold', size=15, color='white'),
                         font_family='Roboto mono',
                         title_font_weight='bold',
                         title_font_size=20,
                         title_x=0.37,
                         title_xanchor='right',
                         #xaxis_type='category',
                         showlegend=False,
                         
                         )

    # Gráfico de matricula por unidad educativa o nivel, con tarjetas de genero
    new_trace01 = [dcc.Graph(figure=trace01, config={"displayModeBar": False}, className="graph_bar"),
                   html.Div(children=[
                            html.Div("Matrícula por género", style={'textAlign': 'left', 'color': 'gray', 'fontSize': '14px'}),

                            html.Div(children=[
                                     html.Div(
                                         html.I(className="fa-solid fa-child"), className="bloque-azul"),
                                     html.Div(f"{masculino_count}", className="bloque-gris"),
                                     
                            ],
                                className="contenedor-icono-texto"),
                             
                             html.Div(children=[
                                     html.Div(
                                         html.I(className="fa-solid fa-child-dress"), className="bloque-azul"),
                                     html.Div(f"{femenino_count}", className="bloque-gris"),
                                     
                            ],
                                className="contenedor-icono-texto"),
                            
                            ],
                       
                       className="card_contenedor")]
    
    # Tabla de proyección de matricula 2026, con columnas de variación porcentual y porcentaje alcanzado respecto a proyección
    # Redondear columnas específicas y formatear como porcentaje
   
    df02_REDONDEADO= df02.round({'% CRECIMIENTO': 3, '% ALCANZADO PROYECCIÓN':3})
    df02_REDONDEADO['% CRECIMIENTO'] = df02_REDONDEADO['% CRECIMIENTO'].map('{:.2%}'.format)
    df02_REDONDEADO['% ALCANZADO PROYECCIÓN'] = df02_REDONDEADO['% ALCANZADO PROYECCIÓN'].map('{:.2%}'.format)
    df02_nuevo = df02_REDONDEADO.rename(columns={'% CRECIMIENTO': 'VARIACION PORCENTUAL SAE 2026 Y MATRÍCULA 2025'})
    
    # Para columnas específicas (ej. ColumnaB):
    tabla_proyeccion = dbc.Table.from_dataframe(df02_nuevo, 
                                               striped=True, 
                                               bordered=True, 
                                               hover=True,
                                               color='dark',
                                               className="align-middle",
                                               style={'width': '90%',
                                                      'margin': 'auto', 
                                                      'text-align': 'center'
                                                      })
    # Gráfico de evolución matricula por fecha, para colocar debajo de la tabla de proyección
    newtrace02 = [dcc.Graph(figure=trace02, config={"displayModeBar": False}, className="graph_line")]
    

    return new_trace01, tabla_proyeccion, newtrace02

# cargar en servidor
# if __name__ == '__main__':
#   app.run_server(debug=True)