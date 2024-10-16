import pathlib
from dash import dcc, html, Input, Output, callback, register_page
import pandas as pd
import plotly.express as px

register_page(
    __name__,
    name='Ensayos PAES',
    top_nav=True,
    path='/ensayos'
)

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()
df01 = pd.read_excel(DATA_PATH.joinpath('data_paes_2024_py.xlsx'), sheet_name='data')


# Listas de Niveles PAES
nivel_options = {
                '3° MEDIO':'3MEDIO',
                '4° MEDIO':'4MEDIO'}

# Lista de pruebas PAES
type_options= ['LEN','MAT-01','HIST','CIEN HC/TP','CIEN PROF']

# Inicio aplicacion Dash
#app = Dash(__name__)
# server=app.server

# Diagrama de la aplicación (Dos listas despegables y un gráfico)
def layout():    
    layout = html.Div(
        children=[


    # Marco para dos listas despegables NIVEL y PRUEBAS
    html.Div(children=[

    # Lista despegable de NIVELES
    html.Div(
        children=[
            html.Div(children='NIVEL', className='menu-title'),
            dcc.Dropdown(
                id='level_ensayos', 
                options=[ 
                    {"label": "3° MEDIO", "value": "3MEDIO"},
                    {"label": "4° MEDIO", "value": "4MEDIO"},
                                    
                ],
                value='3MEDIO',
                clearable=False,
                className='dropdown'
            ),
        ]),

    # Lista depegable para PRUEBAS PAES
    html.Div(
        children=[
            html.Div(children='PRUEBAS', className='menu-title'),
            dcc.Dropdown(
                id='test_ensayos', 
                options=[ 
                    {"label": "LENGUAJE", "value": "LEN"},
                    {"label": "MATEMÁTICA", "value": "MAT-01"},
                    {"label": "HISTORIA", "value": "HIST"},
                    {"label": "MATEMÁTICA 2","value": "MAT-02"},
                    {"label": "CIENCIAS HC/TP","value": "CIEN HC/TP"},
                    {"label": "CIENCIAS PROFUNDIZACIÓN","value": "CIEN PROF"},
                ],
                value= 'LEN',
                clearable=False,
                className='dropdown',
            
            ),
        ]),


    ],
    className="menu",
    ),

    # Marco para el gráfico (dcc.Graph está incorporado en la función update_charts)
        html.Div(id='grafico_ensayos' , className="wrapper"),

        ])

    return layout

# callback para filtrar gráfico segun nivel y asignatura
@callback(
        Output('grafico_ensayos', 'children'),
        [Input('level_ensayos', 'value'),
         Input('test_ensayos','value')]
        )

# función para trazar grafico segun nivel, área y asignatura
def update_charts(nivel,test):

    select_nivel_subject = df01.query("NIVEL == @nivel and TIPO == @test")
    graph_x_axes = 'CURSO'
    
    if test =='LEN':
        color_01='#664200'
        color_02='#ffc966'
        color_03='#ffa500'

    elif test =='MAT-01':
        color_01='#000033'
        color_02='#42a5f5'
        color_03='#000099'

    elif test=='HIST':
        color_01='#33691e'
        color_02='#8bc34a'
        color_03='#0b5010'

    else:
        color_01='#2e7d32'
        color_02='gold'
        color_03='#ffa500'


    trace01 = px.bar(select_nivel_subject, x=graph_x_axes, y=['ENSAYO-01','ENSAYO-02','ENSAYO-03'], 
                     title= f'PROMEDIOS {nivel} en {test}',
                     width=1000, height=380,
                     labels={'value':'','variable':'Ensayos','CURSO':'Cursos'},
                     barmode='group',
                     color_discrete_map={'ENSAYO-01':color_01,'ENSAYO-02':color_02,'ENSAYO-03':color_03},
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
                          '<b>Puntaje:</b>: %{y:.1f}'+
                          '<br><b>Curso:</b>: %{x}<br>',
                        )

    
    trace01.update_yaxes(tickfont_weight='bold',title_font_weight='bold',tickfont_size=15)
    trace01.update_xaxes(tickfont_weight='bold', title_font_weight='bold', tickfont_size=15)
    trace01.update_layout(
                         hoverlabel_font=dict(family='Consolas', weight='bold', size=15, color='white'),
                         font_family='Consolas',
                         title_font_weight='bold',
                         title_font_size=20,
                         title_x=0.5
                         )
    new_trace01 = [dcc.Graph(figure=trace01, config={"displayModeBar": False}, className="card")]
   
    return new_trace01

# cargar en servidor
#if __name__ == '__main__':
 #   app.run_server(debug=True)