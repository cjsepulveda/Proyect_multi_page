import pathlib
from dash import dcc, html, Input, Output, callback, register_page
from plotly.subplots import make_subplots
import pandas as pd
import plotly.graph_objs as go

register_page(
    __name__,
    name='DIA diagnóstico',
    top_nav=True,
    path='/diadiagnostico'
)

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()
#df01 = pd.read_excel(DATA_PATH.joinpath('data_dia_2024.xlsx'), sheet_name='data_dia_mat')


# Inicio aplicacion Dash


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
                id='leveldiag', 
                options=[ 
                    {"label": "2° BÁSICO", "value": "2BÁSICO"},
                    {"label": "3° BÁSICO", "value": "3BÁSICO"},
                    {"label": "4° BÁSICO", "value": "4BÁSICO"},
                    {"label": "5° BÁSICO", "value": "5BÁSICO"},
                    {"label": "6° BÁSICO", "value": "6BÁSICO"},
                    {"label": "7° BÁSICO", "value": "7BÁSICO"},
                    {"label": "8° BÁSICO", "value": "8BÁSICO"},
                    {"label": "1° MEDIO", "value": "1MEDIO"},
                    {"label": "2° MEDIO", "value": "2MEDIO"},


                                    
                ],
                value='2BÁSICO',
                clearable=False,
                className='dropdown'
            ),
        ]),

    # Lista despegable de ASIGNATURAS
    html.Div(
        children=[
            html.Div(children='ASIGNATURA', className='menu-title'),
            dcc.Dropdown(
                id='subjectdiag', 
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
                id='testdiag', 
                options=[ 
                    {"label": "Nivel de Logro", "value": "level_score"},
                    {"label": "Habilidades", "value": "skill"},
                    {"label": "Promedio de Habilidades", "value": "average"},
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
        html.Div(id='graficodiagnostico' , className="wrapper"),

        ])

    return layout
# callback para filtrar gráfico segun nivel, asignatura y descriptor
@callback(
        Output('graficodiagnostico', 'children'),
        [Input('leveldiag', 'value'),
         Input('testdiag','value'),
         Input('subjectdiag','value')]
        )

# función para trazar grafico segun nivel, asignatura y descriptor
def update_charts(nivel,test,asig):

    #if nivel=='2BÁSICO':
    n='Básico'
    
    #elif nivel =='3BÁSICO':
          #n='3° Básico'

    if asig == 'mat':
          df01 = pd.read_excel(DATA_PATH.joinpath('data_dia_2024.xlsx'), sheet_name='diag_update_mat')
          mask01=df01[(df01['NIVEL'] == nivel) & (df01['UNIDAD ACADÉMICA'] == 'BÁSICA 1')]
          mask02=df01[(df01['NIVEL'] == nivel) & (df01['UNIDAD ACADÉMICA'] == 'BÁSICA 2')]
          mask03=df01[(df01['NIVEL'] == nivel) & (df01['UNIDAD ACADÉMICA'] == 'BÁSICA SF')]
          mask04=df01[(df01['NIVEL'] == nivel) & (df01['UNIDAD ACADÉMICA'] == 'MEDIA LA')]
          mask05=df01[(df01['NIVEL'] == nivel) & (df01['UNIDAD ACADÉMICA'] == 'MEDIA SF')]

          a ='Matemáticas'
          count_skill = [0,1,2,3]
          name_skill =['Números','Álgebra','Geometría','Datos y Azar']
          colors_skill=['#00308F','#03C03C','#ffbf00','#c91b00']
          
          
          graph_y_axes_SKILL_ua1=[mask01['num'],mask01['alg'],mask01['geo'],mask01['dat']]
          graph_y_axes_SKILL_ua2=[mask02['num'],mask02['alg'],mask02['geo'],mask02['dat']]
          graph_y_axes_SKILL_ua3=[mask03['num'],mask03['alg'],mask03['geo'],mask03['dat']]
          graph_y_axes_SKILL_ua4=[mask04['num'],mask04['alg'],mask04['geo'],mask04['dat']]
          graph_y_axes_SKILL_ua5=[mask05['num'],mask05['alg'],mask05['geo'],mask05['dat']]

          count_ua_skill=[graph_y_axes_SKILL_ua1,graph_y_axes_SKILL_ua2,graph_y_axes_SKILL_ua3,graph_y_axes_SKILL_ua4,graph_y_axes_SKILL_ua5]

          graph_y_axes_average_ua1=mask01['prom_mat']
          graph_y_axes_average_ua2=mask02['prom_mat']
          graph_y_axes_average_ua3=mask03['prom_mat']
          graph_y_axes_average_ua4=mask04['prom_mat']
          graph_y_axes_average_ua5=mask05['prom_mat']

          count_ua_average=[graph_y_axes_average_ua1,graph_y_axes_average_ua2,graph_y_axes_average_ua3,graph_y_axes_average_ua4,graph_y_axes_average_ua5]

          color_avr='#007fd2'
          
          
    elif asig == 'len':
          df01 = pd.read_excel(DATA_PATH.joinpath('data_dia_2024.xlsx'), sheet_name='diag_update_len')
          mask01=df01[(df01['NIVEL'] == nivel) & (df01['UNIDAD ACADÉMICA'] == 'BÁSICA 1')]
          mask02=df01[(df01['NIVEL'] == nivel) & (df01['UNIDAD ACADÉMICA'] == 'BÁSICA 2')]
          mask03=df01[(df01['NIVEL'] == nivel) & (df01['UNIDAD ACADÉMICA'] == 'BÁSICA SF')]
          mask04=df01[(df01['NIVEL'] == nivel) & (df01['UNIDAD ACADÉMICA'] == 'MEDIA LA')]
          mask05=df01[(df01['NIVEL'] == nivel) & (df01['UNIDAD ACADÉMICA'] == 'MEDIA SF')]

          a ='Lenguaje'
          count_skill = [0,1,2]
          name_skill =['Localizar','Interpretar y relacionar','Reflexionar']
          colors_skill=['#00308F','#03C03C','#ffbf00']

          graph_y_axes_SKILL_ua1=[mask01['loc'],mask01['int'],mask01['ref']]
          graph_y_axes_SKILL_ua2=[mask02['loc'],mask02['int'],mask02['ref']]
          graph_y_axes_SKILL_ua3=[mask03['loc'],mask03['int'],mask03['ref']]
          graph_y_axes_SKILL_ua4=[mask04['loc'],mask04['int'],mask04['ref']]
          graph_y_axes_SKILL_ua5=[mask05['loc'],mask05['int'],mask05['ref']]

          count_ua_skill=[graph_y_axes_SKILL_ua1,graph_y_axes_SKILL_ua2,graph_y_axes_SKILL_ua3,graph_y_axes_SKILL_ua4,graph_y_axes_SKILL_ua5]

          graph_y_axes_average_ua1=mask01['prom_len']
          graph_y_axes_average_ua2=mask02['prom_len']
          graph_y_axes_average_ua3=mask03['prom_len']
          graph_y_axes_average_ua4=mask04['prom_len']
          graph_y_axes_average_ua5=mask05['prom_len']

          count_ua_average=[graph_y_axes_average_ua1,graph_y_axes_average_ua2,graph_y_axes_average_ua3,graph_y_axes_average_ua4,graph_y_axes_average_ua5]

          color_avr='#ffaf2b '
          print(df01)
    
    # Parámetros constantes para ambas asignaturas, petenecientes al descriptor NIVEL de LOGRO
    count_level=[0,1,2]

    if nivel=='1MEDIO' or nivel=='2MEDIO':
        count_ua =[3,4]
        count_col=[0,1]
        columnas = 2

    else:
        count_ua =[0,1,2]
        count_col=[0,1,2]
        columnas = 3

    

    name_level=['Nivel I','Nivel II','Nivel III']
    graph_y_axes_LEVEL_ua1=[mask01['NIVEL I'], mask01['NIVEL II'], mask01['NIVEL III']]
    graph_y_axes_LEVEL_ua2=[mask02['NIVEL I'], mask02['NIVEL II'], mask02['NIVEL III']]
    graph_y_axes_LEVEL_ua3=[mask03['NIVEL I'], mask03['NIVEL II'], mask03['NIVEL III']]
    graph_y_axes_LEVEL_ua4=[mask04['NIVEL I'], mask04['NIVEL II'], mask04['NIVEL III']]
    graph_y_axes_LEVEL_ua5=[mask05['NIVEL I'], mask05['NIVEL II'], mask05['NIVEL III']]

    count_ua_level=[graph_y_axes_LEVEL_ua1,graph_y_axes_LEVEL_ua2,graph_y_axes_LEVEL_ua3,graph_y_axes_LEVEL_ua4,graph_y_axes_LEVEL_ua5]

    colors_level=['#062c80','#0e6ac7','#4fb9fc']
    
    # Parámetros constantes para el gráfico, TITULO, y eje X con múltiples valores
    new_hovertemplate = 'Rendimiento: %{y:.0%}'+'<br>Nivel: %{x[0]}<br>'+'Etapa: %{x[1]}'
    graph_x_axes_ua1 = [mask01['NIVEL'], mask01['ETAPA']]
    graph_x_axes_ua2 = [mask02['NIVEL'], mask01['ETAPA']]
    graph_x_axes_ua3 = [mask03['NIVEL'], mask01['ETAPA']]
    graph_x_axes_ua4 = [mask04['NIVEL'], mask04['ETAPA']]
    graph_x_axes_ua5 = [mask05['NIVEL'], mask05['ETAPA']]

    x_axes_ua =[graph_x_axes_ua1,graph_x_axes_ua2,graph_x_axes_ua3,graph_x_axes_ua4,graph_x_axes_ua5]

    #print(mask01.iloc[:,1])
           
    trace01 = go.Figure()
    
    if test == 'level_score': # Gráfica para NIVEL de LOGRO
            trace01 = make_subplots(
                  rows=1, cols=columnas,
                  subplot_titles=("Básica 1", " Básica 2", "Básica SF"))
            trace01.update_annotations(font=dict(size=16, family="Arial", color="black"), font_weight="bold")

            for ua, col in zip(count_ua, count_col):
             for x in count_level:
                    trace01.add_bar( x=x_axes_ua[ua], y=count_ua_level[ua][x],
                                
                                legendgroup="group1", showlegend=True,
                                name=name_level[x],
                                texttemplate='%{y:.0%}',  # Format the labels as percentages with one decimal place
                                textposition='inside',
                                insidetextanchor='middle',  # Position of the labels
                                textfont=dict(size=15, family="Arial", color="white", weight= 700),
                                marker_color=colors_level[x],
                                hovertemplate = new_hovertemplate,
                                hoverlabel=dict(
                                                #bgcolor="white",
                                                #font_size=16,
                                                font_family="Inter",
                                                font_color="white"  # Sets the text color inside the box
                                                ),
                                row=1, col=col+1)
                
                
            trace01.update_layout(barmode="relative", template='simple_white')
            b ='Niveles de Logro'

    elif test == 'skill': # Gráfica para HABILIDADES
            
            trace01 = make_subplots(
                  rows=1, cols=3,
                  subplot_titles=("Básica 1", " Básica 2", "Básica SF"))
            
            trace01.update_annotations(font=dict(size=16, family="Arial", color="black"), font_weight="bold")


            for x in count_skill:
                trace01.add_bar( x=graph_x_axes_ua1, y=graph_y_axes_SKILL_ua1[x],
                            legendgroup="group1", showlegend=True, 
                            name=name_skill[x],
                            texttemplate='%{y:.0%}',  # Format the labels as percentages with one decimal place
                            textposition='outside',
                            insidetextanchor='middle',  # Position of the labels
                            textfont=dict(size=15, family="Arial", color="black", weight= 700),
                            marker_color=colors_skill[x],
                            hovertemplate = new_hovertemplate,
                            hoverlabel=dict(
                                                #bgcolor="white",
                                                #font_size=16,
                                                font_family="Inter",
                                                font_color="white"  , # Sets the text color inside the box
                                                ),
                            row=1, col=1)
                
                trace01.add_bar( x=graph_x_axes_ua2, y=graph_y_axes_SKILL_ua2[x], 
                            legendgroup="group1", showlegend=False,
                            name=name_skill[x], 
                            texttemplate='%{y:.0%}',  # Format the labels as percentages with one decimal place
                            textposition='outside',
                            insidetextanchor='middle',  # Position of the labels
                            textfont=dict(size=15, family="Arial", color="black", weight= 700),
                            marker_color=colors_skill[x],
                            hovertemplate = new_hovertemplate,
                            hoverlabel=dict(
                                                #bgcolor="white",
                                                #font_size=16,
                                                font_family="Inter",
                                                font_color="white"  , # Sets the text color inside the box
                                                ),
                            row=1, col=2)
                
                trace01.add_bar( x=graph_x_axes_ua3, y=graph_y_axes_SKILL_ua3[x], 
                            legendgroup="group1", showlegend=False,
                            name=name_skill[x], 
                            texttemplate='%{y:.0%}',  # Format the labels as percentages with one decimal place
                            textposition='outside',
                            insidetextanchor='middle',  # Position of the labels
                            textfont=dict(size=15, family="Arial", color="black", weight= 700),
                            marker_color=colors_skill[x],
                            hovertemplate = new_hovertemplate,
                            hoverlabel=dict(
                                                #bgcolor="white",
                                                #font_size=16,
                                                font_family="Inter",
                                                font_color="white"  , # Sets the text color inside the box
                                                ),
                            row=1, col=3)
                
                #trace01.update_layout(showlegend=False)
                        
            trace01.update_layout(barmode="group",  template='simple_white')
            b ='Habilidades'

    elif test == 'average': # Gráfica para PROMEDIO de HABILIDADES
            
            trace01 = make_subplots(
                  rows=1, cols=3,
                  subplot_titles=("Básica 1", " Básica 2", "Básica SF"))
            
            trace01.update_annotations(font=dict(size=16, family="Inter", color="black"), font_weight="bold")

            trace01.add_bar( x=graph_x_axes_ua1, y=graph_y_axes_average_ua1,
                            legendgroup="group1", showlegend=True,  
                            name='Promedio Habilidades', 
                            marker_color=color_avr,
                            texttemplate='%{y:.0%}',  # Format the labels as percentages with one decimal place
                            textposition='inside',
                            insidetextanchor='middle',  # Position of the labels
                            textfont=dict(size=15, family="Arial", color="white", weight= 700),
                            hovertemplate = new_hovertemplate,
                            hoverlabel=dict(
                                                #bgcolor="white",
                                                #font_size=16,
                                                font_family="Inter",
                                                font_color="white"  , # Sets the text color inside the box
                                                ),
                            row=1, col=1)
            
            trace01.add_bar( x=graph_x_axes_ua2, y=graph_y_axes_average_ua2, 
                            legendgroup="group1", showlegend=False,
                            name='Promedio Habilidades',
                            marker_color=color_avr,
                            texttemplate='%{y:.0%}',  # Format the labels as percentages with one decimal place
                            textposition='inside',
                            insidetextanchor='middle',  # Position of the labels
                            textfont=dict(size=15, family="Arial", color="white", weight= 700),
                            hovertemplate = new_hovertemplate,
                            hoverlabel=dict(
                                                #bgcolor="white",
                                                #font_size=16,
                                                font_family="Inter",
                                                font_color="white"  , # Sets the text color inside the box
                                                ),
                            row=1, col=2)
            
            trace01.add_bar( x=graph_x_axes_ua3, y=graph_y_axes_average_ua3,
                            legendgroup="group1", showlegend=False,
                            name='Promedio Habilidades',
                            marker_color=color_avr,
                            texttemplate='%{y:.0%}',  # Format the labels as percentages with one decimal place
                            textposition='inside',
                            insidetextanchor='middle',  # Position of the labels
                            textfont=dict(size=15, family="Arial", color="white", weight= 700),
                            hovertemplate = new_hovertemplate,
                            hoverlabel=dict(
                                                #bgcolor="white",
                                                #font_size=16,
                                                font_family="Inter",
                                                font_color="white"  , # Sets the text color inside the box
                                                ),
                            row=1, col=3)            

            trace01.update_layout(barmode="group",  template='simple_white')
            b ='Promedio Habilidades'
    
    trace01.update_layout(
    title_text=f"Rendimiento DIA Diagnóstico: {b} {a}",
    title_font_family='Consolas',
    title_font_weight=1000,
    # showlegend=False,
    legend_font_family='Consolas',
    activeselection_opacity=1,
    title_xref='paper',
    title_x= 0.0,
    title_font_size=20,
    legend_title_text='Descriptor',
    autosize=False,
    width=1200,
    height=380,
    margin=dict(l=0, r=0, b=50, t=80, pad=0),
       
        )
    trace01.update_yaxes(tickformat='.0%', tickfont_family='Consolas', tickfont_size=12, tickfont_weight=1000, range=[0, 1])
    trace01.update_xaxes(tickfont_family='Consolas', tickfont_size=12, tickfont_weight=1000)

    trace01.add_layout_image(                                 
                            source= "assets/Original-Apaisado.png",
                            x=1, y=1.10,
                            sizex=0.2, sizey=0.2,
                            xanchor="right", yanchor="bottom",                                
                            )

    
    
    
    new_trace01 = [dcc.Graph(figure=trace01, config={"displayModeBar": False}, className="card")]
   
    return new_trace01

# cargar en servidor
#if __name__ == '__main__':
    #app.run_server(debug=True)