import pathlib
from dash import dcc, html, Input, Output, callback, register_page
import pandas as pd
import plotly.express as px

register_page(
    __name__,
    name='Rendimiento',
    top_nav=True,
    path='/rendimientos'
)

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()
df01 = pd.read_excel(DATA_PATH.joinpath('data_level_grade_02.xlsx'), sheet_name='DATA_JUN')

grades = df01["NIVEL"].sort_values().unique()
subjetsALL = df01["ASIGNATURA"].unique()

# Filtro para asiganturas segun nivel elegido
mask01 = df01[df01["NIVEL"]=="1MEDIO"]
mask02 = df01[df01["NIVEL"]=="2MEDIO"]
mask03 = df01[df01["NIVEL"]=="3MEDIO"]
mask04 = df01[df01["NIVEL"]=="4MEDIO"]

# Filtro para áreas
mask05 = df01[df01['AREA']=='PLAN COMÚN']
mask06 = df01[df01['AREA']=='CARRERAS']
mask07 = df01[df01['AREA']=='PROFUNDIZACIÓN HC']


# Listas de asignaturas según nivel
subjets1M = mask01["ASIGNATURA"].unique()
subjets2M = mask02["ASIGNATURA"].unique()
subjets3M = mask03["ASIGNATURA"].unique()
subjets4M = mask04["ASIGNATURA"].unique()

# Listas de asignaturas según área
subjets_plancomun = mask05["ASIGNATURA"].unique()
subjets_carreras = mask06['TIPO'].unique()
subjets_profundizacion = mask07['TIPO'].unique()

# Diccionario con listas de asignaturas plan comun segun nivel
all_options = {
    '1MEDIO': subjets1M,
    '2MEDIO': subjets2M,
    '3MEDIO': subjets3M,
    '4MEDIO': subjets4M
}

# Diccionario con listas de asignaturas por área para 3MEDIO y 4MEDIO
options_area = {
    'PLAN COMÚN':subjets_plancomun,
    'CARRERAS':subjets_carreras,
    'PROFUNDIZACIÓN HC': subjets_profundizacion
}

# Inicio aplicacion Dash

# Diagrama de la aplicación (Título, Tres listas despegables y un gráfico)
def layout():    
    layout = html.Div(
        children=[


    # Marco para tres listas despegables NIVEL, AREA, ASIGNATURA
    html.Div(children=[
    # Lista despegable de NIVELES, segun nivel
    html.Div(
        children=[
            html.Div(children='NIVEL', className='menu-title'),
            dcc.Dropdown(
                id='level', 
                options=[ 
                    {'label': nivel, 'value': nivel}
                    
                    for nivel in all_options.keys()
                    
                ],
                value='1MEDIO',
                clearable=False,
                className='dropdown'
            ),
        ]),

    # Lista depegable para Área (Plan Común, Carreras, Profundización HC)
    html.Div(
        children=[
            html.Div(children='ÁREA', className='menu-title'),
            dcc.Dropdown(
                id='area', 
                options=[ 
                {'label': area, 'value': area}
                    
                    for area in options_area.keys()
                    
                ],
                value= 'PLAN COMÚN',
                clearable=False,
                className='dropdown',
            
            ),
        ]),

    # Lista despegable de Asignaturas, segun nivel
    html.Div(
        children=[
            html.Div(children="ASIGNATURA", className="menu-title"),
            dcc.Dropdown(
                id='subject',
                clearable=False,
                className='dropdown',
                    ),
        
    ]),
    ],
    className="menu",
    ),

    # Marco para el gráfico (dcc.Graph está incorporado en la función update_charts)
        html.Div(id='grafico' , className="wrapper"),

        ]
    )
    return layout

# callback para cambiar lista despegable de asignaturas de 1MEDIO o 2MEDIO MEDIO segun nivel 
# o activar lista depegable "AREA" al elegir 3MEDIO o 4MEDIO
@callback(
    Output('subject', 'options'),
    Output('subject', 'value'),
    Output('area','disabled'),
    Output('area','value'),
    [Input('level', 'value'),
     Input('area','value')]
        
    )

# función para cambiar opciones de lista despegable asignaturas segun el nivel y valor inicial
def set_subject_options(selected_level, selected_area):

    if (selected_level=='2MEDIO' or selected_level=='1MEDIO') and (
        selected_area=='CARRERAS' or selected_area=='PROFUNDIZACIÓN HC'):

        value_area_ini ='PLAN COMÚN'
    
    else:

        value_area_ini = selected_area

    if selected_level == '1MEDIO' or selected_level == '2MEDIO': 
        
        options_disabled_area = True
        
        options_subjects = [{'label': i, 'value': i} 
                    for i in all_options[selected_level]]
    
        value_subject_ini = all_options[selected_level][0]

                  
        
    elif selected_level == '3MEDIO' or selected_level == '4MEDIO' :
        
        options_disabled_area = False

        options_subjects = [{'label': i, 'value': i} 
                    for i in options_area[selected_area]]
    
        value_subject_ini = options_area[selected_area][0]
       
        

    return options_subjects, value_subject_ini, options_disabled_area, value_area_ini

# callback para filtrar gráfico segun nivel y asignatura
@callback(
        Output('grafico', 'children'),
        [Input('level', 'value'),
        Input('subject','value'),
        Input('area','value')]
        )

# función para trazar grafico segun nivel, área y asignatura
def update_charts(nivel,asignatura,area_id):

    if  area_id == 'PLAN COMÚN':
        select_nivel_subject = df01.query("NIVEL == @nivel and ASIGNATURA == @asignatura")
        graph_x_axes = 'CURSO'
    
    elif area_id == 'CARRERAS' or area_id == 'PROFUNDIZACIÓN HC': 
        select_nivel_subject = df01.query("AREA == @area_id and TIPO == @asignatura")
        graph_x_axes = 'ASIGNATURA'

    trace01 = px.bar(select_nivel_subject, x=graph_x_axes, y=['MB','B','S','I','P'],
                     title= f'RENDIMIENTO ESTUDIANTES en {asignatura}',
                     width=1000, height=390,
                     labels={'value':'','variable':'Categorías','CURSO':'Cursos'},
                     barmode='group',
                     color_discrete_map={'MB':'blue','B':'green','S':'orange','I':'tomato','P':'darkred'},
                     template="simple_white",
                     range_y=[0,1],
                     )
    trace01.add_layout_image(                                 
                            source= "assets/Original-Apaisado.png",
                            xref="paper", yref="paper",
                            x=1.12, y=1.15,
                            sizex=0.2, sizey=0.2,
                            xanchor="right", yanchor="bottom",                                
                            )
    
    trace01.update_yaxes(tickformat=".1%", tickfont_weight='bold',title_font_weight='bold',tickfont_size=15)
    trace01.update_xaxes(tickfont_weight='bold', title_font_weight='bold')
    trace01.update_layout(
                         hoverlabel_font_color='white',
                         hoverlabel_font_family='Consolas',
                         uniformtext_minsize=5,
                         uniformtext_mode='show',
                         title_font_weight='bold',
                         font_family='Consolas',
                         title_font_size=20,
                         title_x=0.5
                         )
    
    new_trace01 = [dcc.Graph(figure=trace01, config={"displayModeBar": False}, className="card")]
   
    return new_trace01

# cargar en servidor
#if __name__ == '__main__':
 #   app.run_server(debug=True)