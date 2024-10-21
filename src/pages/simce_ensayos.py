import pathlib
from dash import dcc, html, Input, Output, callback, register_page
import pandas as pd
import plotly.graph_objs as go

register_page(
    __name__,
    name='Ensayos SIMCE',
    top_nav=True,
    path='/simce_ensayos'
)

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()
#df01 = pd.read_excel(DATA_PATH.joinpath('data_dia_2024.xlsx'), sheet_name='data_dia_mat')


# Inicio aplicacion Dash
# app = Dash(__name__)
# server=app.server

# Diagrama de la aplicación (Dos listas despegables y un gráfico)
def layout(): 
    layout = html.Div(
        children=[


# Marco para tres listas despegables NIVEL y PRUEBAS
html.Div(children=[

# Lista despegable de NIVELES
html.Div(
    children=[
        html.Div(children='NIVEL', className='menu-title'),
        dcc.Dropdown(
            id='level_simce', 
            options=[ 
                {"label": "1° MEDIO", "value": "1MEDIO"},
                {"label": "2° MEDIO", "value": "2MEDIO"},
                                
            ],
            value='1MEDIO',
            clearable=False,
            className='dropdown'
        ),
    ]),

# Lista despegable de ASIGNATURAS
html.Div(
    children=[
        html.Div(children='ASIGNATURA', className='menu-title'),
        dcc.Dropdown(
            id='subject_simce', 
            options=[ 
                {"label": "Lenguaje", "value": "len"},
                {"label": "Matemáticas", "value": "mat"},
                                
            ],
            value='len',
            clearable=False,
            className='dropdown'
        ),
    ]),

# Lista depegable para DESCRIPTORES
html.Div(
    children=[
        html.Div(children='Descriptor', className='menu-title'),
        dcc.Dropdown(
            id='test_simce', 
            options=[ 
                {"label": "Nivel de Logro", "value": "level_score"},
                {"label": "Habilidades", "value": "skill"},
                {"label": "Porcentaje Logro", "value": "average"},
                {"label": "Puntajes", "value": "score"},
                {"label": "Variaciones Puntajes", "value": "var_score"}
               ],
            value= 'level_score',
            clearable=False,
            className='dropdown',
           
        ),
    ]),


],
className="menu",
),

# Marco para el gráfico (dcc.Graph está incorporado en la función update_charts)
    html.Div(id='grafico_simce' , className="wrapper"),

    ])

    return layout

# callback para activar y desactivar opciones nivel y asignatura

@callback(
    Output('level_simce','disabled'),
    Output('subject_simce','disabled'),
    Input('test_simce','value')
    )

def active_level_subject(test_value):

    if test_value=='var_score':

        options_disabled_level = True
        options_disabled_subject = True
    
    else:

        options_disabled_level = False
        options_disabled_subject = False

    return options_disabled_level, options_disabled_subject

# callback para filtrar gráfico segun nivel, asignatura y descriptor
@callback(
        Output('grafico_simce', 'children'),
        [Input('level_simce', 'value'),
         Input('test_simce','value'),
         Input('subject_simce','value')]
        )

# función para trazar grafico segun nivel, asignatura y descriptor
def update_charts(nivel,test,asig):

    if nivel=='1MEDIO':
          n='1° Medio'
    
    elif nivel =='2MEDIO':
          n='2° Medio'

    if asig == 'mat':
          df01 = pd.read_excel(DATA_PATH.joinpath('data_ensayo_simce_2024.xlsx'), sheet_name='data_simce_mat')
          mask01=df01[df01['NIVEL'] == nivel]
          a ='Matemáticas'
          count_skill = [0,1,2,3]
          name_skill =['Números','Álgebra','Geometría','Datos y Azar']
          colors_skill=['#00308F','#03C03C','#ffbf00','#c91b00']
          graph_y_axes_SKILL=[mask01['num'],mask01['alg'],mask01['geo'],mask01['dat']]
          graph_y_axes_average=mask01['prom_mat']
          graph_y_axes_score=mask01['punt_mat']
          color_avr='#007fd2'
          color_score='#FFD966'

    elif asig == 'len':
          df01 = pd.read_excel(DATA_PATH.joinpath('data_ensayo_simce_2024.xlsx'), sheet_name='data_simce_len')
          mask01=df01[df01['NIVEL'] == nivel]
          a ='Lenguaje'
          count_skill = [0,1,2]
          name_skill =['Localizar','Interpretar y relacionar','Reflexionar']
          colors_skill=['#00308F','#03C03C','#ffbf00']
          graph_y_axes_SKILL=[mask01['loc'],mask01['int'],mask01['ref']]
          graph_y_axes_average=mask01['prom_len']
          graph_y_axes_score=mask01['punt_len']
          color_avr='#ffaf2b'
          color_score='#0147EB'

    
    # Parámetros constantes para ambas asignaturas, petenecientes al descriptor NIVEL de LOGRO
    count_level=[0,1,2]
    name_level=['INSUFICIENTE','ELEMENTAL','ADECUADO']
    graph_y_axes_LEVEL=[mask01['INSUFICIENTE'], mask01['ELEMENTAL'], mask01['ADECUADO']]
    colors_level=['#062c80','#0e6ac7','#4fb9fc']
    
    # Parámetros constantes para el gráfico, leyenda barras, y eje X con múltiples valores

    if test =='score':
         new_hovertemplate = 'Rendimiento: %{y:.1f}'+'<br>Curso: %{x[0]}<br>'+'Etapa: %{x[1]}'
         graph_x_axes = [mask01['CURSO'],mask01['Etapa']]
    
    else:
        new_hovertemplate = 'Rendimiento: %{y:.0%}'+'<br>Curso: %{x[0]}<br>'+'Etapa: %{x[1]}'
        graph_x_axes = [mask01['CURSO'],mask01['Etapa']]

    #print(mask01.iloc[:,1])
           
    trace01 = go.Figure()
    
    if test == 'level_score': # Gráfica para NIVEL de LOGRO
            
            for x in count_level:
                trace01.add_bar( x=graph_x_axes, y=graph_y_axes_LEVEL[x], 
                                name=name_level[x],
                                marker_color=colors_level[x],
                                hovertemplate = new_hovertemplate)
               
            trace01.update_layout(barmode="relative", template='simple_white')
            b ='Niveles de Logro'

    elif test == 'skill': # Gráfica para HABILIDADES
            
            for x in count_skill:
                trace01.add_bar( x=graph_x_axes, y=graph_y_axes_SKILL[x], 
                            name=name_skill[x], 
                            marker_color=colors_skill[x],
                            hovertemplate = new_hovertemplate)
                        
            trace01.update_layout(barmode="group",  template='simple_white')
            b ='Habilidades'

    elif test == 'average': # Gráfica para PROMEDIO de HABILIDADES
                        
            trace01.add_bar( x=graph_x_axes, y=graph_y_axes_average, 
                            name='Promedio Habilidades', 
                            marker_color=color_avr,
                            hovertemplate = new_hovertemplate)
                        
            trace01.update_layout(barmode="group",  template='simple_white')
            b ='Porcentaje Logro'
    
    elif test =='score': #Gráfica para PUNTAJES SIMCE

            trace01.add_bar( x=graph_x_axes, y=graph_y_axes_score, 
                            name='PUNTAJES SIMCE', 
                            marker_color=color_score,
                            hovertemplate = new_hovertemplate)
                        
            trace01.update_layout(barmode="group",  template='simple_white')
            b='Puntajes'

    elif test =='var_score': #Gráfica VARIACIONES PUNTAJES SIMCE
            df02 = pd.read_excel(DATA_PATH.joinpath('data_ensayo_simce_2024.xlsx'), sheet_name='var')
            graph_x_axes = [df02['NIVEL'],df02['ASIGNATURA']]
            graph_y_axes_score_var=df02['VALOR']

            trace01.add_bar( x=graph_x_axes, y=graph_y_axes_score_var, 
                            name='VARIACIONES PUNTAJES SIMCE', 
                            marker_color='Green',
                            hovertemplate = new_hovertemplate)
                        
            trace01.update_layout(barmode="group", template='simple_white')
            b='Variaciones'
            a ='Lenguaje y Mateáticas'
            n ='1° y 2° Medio'
    
    # actualizaciones LAYOUT gráfico

    trace01.update_layout(
    title_text=f"ENSAYOS SIMCE: {b}, {a} {n}",
    title_font_family='Consolas',
    title_font_weight=1000,
    legend_font_family='Consolas',
    activeselection_opacity=1,
    title_xref='paper',
    title_x= 0.0,
    title_font_size=25,
    legend_title_text='Descriptor',
    autosize=True,
    bargap=0.5,
    legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.0,
                xanchor="right",
                x=0.7),
    width=1000,
    height=400,
    margin=dict(l=0, r=0, b=50, t=80, pad=0),
       
        )
    # opciones fuente, tamaño para ejes
    trace01.update_xaxes(
            tickfont_family='Consolas', 
            tickfont_size=15, 
            tickfont_weight=1000,
            )
    trace01.update_yaxes(
             tickfont_family='Consolas', 
             tickfont_size=15, 
             tickfont_weight=1000
             )
        
    if test == 'score': #opcion grafico con escala numérica para puntajes simce

        trace01.update_yaxes(
             tickformat='.0f', 
             )
                
    elif test == 'var_score': # opción gráfico para variacion puntajes SIMCE

        trace01.update_yaxes(
            tickformat='.0%', 
            zeroline=True,
            zerolinecolor='black'
            )
        
      
    else: # opción graficos con escalas en porcentaje
        trace01.update_yaxes(
             tickformat='.0%', 
             )
        
    new_trace01 = [dcc.Graph(figure=trace01, config={"displayModeBar": False}, className="card")]
   
    return new_trace01

# cargar en servidor
# if __name__ == '__main__':
#   app.run_server(debug=True)