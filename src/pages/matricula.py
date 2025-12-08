import pathlib
from dash import dcc, html, Input, Output, callback, register_page
import pandas as pd
import plotly.express as px


register_page(
    __name__,
    name='Matrícula',
    top_nav=True,
    path='/matricula'
)

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()
df01 = pd.read_excel(DATA_PATH.joinpath('mat_2026.xlsx'), sheet_name='mat_2026')


# Listas de Unidades Educativas
nivel_options = {
                'BÁSICA 1':'BÁSICA 1',
                'BÁSICA 2':'BÁSICA 2',
                'BÁSICA SAN FELIPE':'BÁSICA SF',
                'MEDIA LOS ANDES':'MEDIA LOS ANDES',
                'MEDIA SAN FELIPE':'MEDIA SAN FELIPE'}

# Lista de pruebas PAES
type_options= ['LEN','MAT-01','HIST','CIEN HC/TP','CIEN PROF']

# Inicio aplicacion Dash
#app = Dash(__name__)
# server=app.server

# Diagrama de la aplicación (Una lista despegable y un gráfico)
def layout():    
    layout = html.Div(
        children=[


    # Marco para dos listas despegables UNIDAD EDUCATIVA
    html.Div(children=[

    # Lista despegable de UNIDAD EDUCATIVA
    html.Div(
        children=[
            html.Div(children='Unidad Educativa', className='menu-title'),
            dcc.Dropdown(
                id='unidades_educativas', 
                options=[ 
                    {"label": "CORPORACIÓN", "value": "Corporacion"},
                    {"label": "BÁSICA 1", "value": "BÁSICA 1"},
                    {"label": "BÁSICA 2", "value": "BÁSICA 2"},
                    {"label": "BÁSICA SAN FELIPE", "value": "BÁSICA SF"},
                    {"label": "MEDIA LOS ANDES", "value": "MEDIA LOS ANDES"},
                    {"label": "MEDIA SAN FELIPE", "value": "MEDIA SAN FELIPE"},
                                    
                ],
                value='MEDIA LOS ANDES',
                clearable=False,
                className='dropdown'
            ),
        ]),

    # Lista depegable para PRUEBAS PAES
    #html.Div(
    #    children=[
    #        html.Div(children='PRUEBAS', className='menu-title'),
    #        dcc.Dropdown(
    #            id='test_ensayos', 
    #            options=[ 
    #                {"label": "LENGUAJE", "value": "LEN"},
    #                {"label": "MATEMÁTICA", "value": "MAT-01"},
    #                {"label": "HISTORIA", "value": "HIST"},
    #                {"label": "MATEMÁTICA 2","value": "MAT-02"},
    #                {"label": "CIENCIAS HC/TP","value": "CIEN HC/TP"},
    #                {"label": "CIENCIAS PROFUNDIZACIÓN","value": "CIEN PROF"},
    #            ],
    #            value= 'LEN',
    #            clearable=False,
    #            className='dropdown',
            
    #        ),
    #    ]),


    ],
    className="menu",
    ),

    # Marco para el gráfico (dcc.Graph está incorporado en la función update_charts)
        html.Div(id='grafico_matricula' , className="wrapper"),

        ])

    return layout

# callback para filtrar gráfico segun unidad educativa
@callback(
        Output('grafico_matricula', 'children'),
        [Input('unidades_educativas', 'value'),
         ]
        )

# función para trazar grafico segun nivel, área y asignatura
def update_charts(unidad_edu):

    if unidad_edu == 'Corporacion':
        df_agrupado = df01.groupby('UNI_EDU').sum()
        df_agrupado_in = df_agrupado.reset_index()
        df_agrupado_new = df_agrupado_in.drop(['NIVEL','% META'], axis=1)

        # 2. Calcular los totales para las columnas numéricas
        total_SAE_2026 = df_agrupado_new['SAE_2026'].sum()
        total_MAT_2026 = df_agrupado_new['MAT_2026'].sum()

        # 3. Crear la fila de totales como una lista o diccionario
        fila_total = {'UNI_EDU': 'GENERAL', 'SAE_2026': total_SAE_2026, 'MAT_2026': total_MAT_2026}
                
        # 4. Convertir la fila a un DataFrame temporal (para concatenar)
        df_total = pd.DataFrame([fila_total]) # Importante: pasar la fila dentro de una lista

        # 5. Concatenar el DataFrame original con la fila de totales
        df_agrupado_total = pd.concat([df_agrupado_new, df_total], ignore_index=True)

        # Calcular el porcentaje de 'MAT_2026' respecto a 'SAE_2026'
        df_agrupado_total['% Meta'] = (df_agrupado_total['MAT_2026'] / df_agrupado_total['SAE_2026']) * 100

        select_nivel_subject = df_agrupado_total
        graph_x_axes = 'UNI_EDU'
        color_bar = 'UNI_EDU'
        # Create a new column to identify the last row
        # We will label the last row 'Last' and the rest 'Other'
        #df_agrupado_total['is_last'] = ['Other'] * len(df_agrupado_total)
        #df_agrupado_total.loc[df_agrupado_total.index[-1], 'is_last'] = 'Last'   
        # Define a specific color map: 'Last' will be red, 'Other' will be blue
        #color_map = {'Other': 'blue', 'Last': 'red'}



        print(df_agrupado_total)
    else:
        df_agrupado_ue = df01.query("UNI_EDU == @unidad_edu")
        
        #df_agrupado_ue_in = df_agrupado_ue.reset_index()
        df_agrupado_new_ue = df_agrupado_ue.drop(['UNI_EDU','% META'], axis=1)


        # 2. Calcular los totales para las columnas numéricas
        total_SAE_2026_ue = df_agrupado_new_ue['SAE_2026'].sum()
        total_MAT_2026_ue = df_agrupado_new_ue['MAT_2026'].sum()
        
        # 3. Crear la fila de totales como una lista o diccionario
        fila_total_ue = {'NIVEL': 'GENERAL', 'SAE_2026': total_SAE_2026_ue, 'MAT_2026': total_MAT_2026_ue}
                
        # 4. Convertir la fila a un DataFrame temporal (para concatenar)
        df_total_ue = pd.DataFrame([fila_total_ue]) # Importante: pasar la fila dentro de una lista

        # 5. Concatenar el DataFrame original con la fila de totales
        df_agrupado_total_ue = pd.concat([df_agrupado_new_ue, df_total_ue], ignore_index=True)
        
        # Calcular el porcentaje de 'MAT_2026' respecto a 'SAE_2026'
        df_agrupado_total_ue['% Meta'] = (df_agrupado_total_ue['MAT_2026'] / df_agrupado_total_ue['SAE_2026']) * 100

        select_nivel_subject = df_agrupado_total_ue
        graph_x_axes = 'NIVEL'
        color_bar = 'NIVEL'

        print(df_agrupado_total_ue)
    
    color_03='blue'

    trace01 = px.bar(select_nivel_subject, x=graph_x_axes, y=['MAT_2026'], 
                     title= f'Matrícula 2026 {unidad_edu} ',
                     width=1200, height=380,
                     labels={'value':'','variable':'Matrícula','NIVEL':'Niveles'},
                     #barmode='group',
                     color=color_bar,
                     color_discrete_map= {'GENERAL':color_03},
                     template="simple_white",
                     )
    
    trace01.add_layout_image(                                 
                            source= "assets/Original-Apaisado.png",
                            xref="paper", yref="paper",
                            x=1.12, y=1.15,
                            sizex=0.2, sizey=0.2,
                            xanchor="right", yanchor="bottom",                                
                            )

    trace01.update_traces(hovertemplate=
                          '<b>Matrícula:</b>: %{y:f}'+
                          '<br><b>Nivel:</b>: %{x}<br>',
                        )

    
    trace01.update_yaxes(tickfont_weight='bold',title_font_weight='bold',tickfont_size=15)
    trace01.update_xaxes(tickfont_weight='bold', title_font_weight='bold', tickfont_size=15)
    trace01.update_layout(
                         hoverlabel_font=dict(family='Consolas', weight='bold', size=15, color='white'),
                         font_family='Consolas',
                         title_font_weight='bold',
                         title_font_size=20,
                         title_x=0.5,
                         xaxis_type='category',
                         )
    new_trace01 = [dcc.Graph(figure=trace01, config={"displayModeBar": False}, className="card")]
   
    return new_trace01

# cargar en servidor
#if __name__ == '__main__':
 #   app.run_server(debug=True)