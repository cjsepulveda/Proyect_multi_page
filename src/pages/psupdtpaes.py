import pathlib
from dash import dcc, html, Input, Output, callback, register_page
import pandas as pd
import plotly.express as px

register_page(
    __name__,
    name='PSU PDT PAES',
    top_nav=True,
    path='/psupdtpaes'
)

PATH = pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath("data").resolve()
df01 = pd.read_csv(DATA_PATH.joinpath('psu_pdt_paes.csv'), sep=";", index_col=0)

df01['LENGUAJE'] = df01['LENGUAJE'].replace(',','.',regex=True)
df01['LENGUAJE'] = pd.to_numeric(df01['LENGUAJE'])

df01['MATEMÁTICA'] = df01['MATEMÁTICA'].replace(',','.',regex=True)
df01['MATEMÁTICA'] = pd.to_numeric(df01['MATEMÁTICA'])

df01['PROM. LEN-MAT'] = df01['PROM. LEN-MAT'].replace(',','.',regex=True)
df01['PROM. LEN-MAT'] = pd.to_numeric(df01['PROM. LEN-MAT'])

df01['HISTORIA'] = df01['HISTORIA'].replace(',','.',regex=True)
df01['HISTORIA'] = pd.to_numeric(df01['HISTORIA'])

df01['CIENCIAS'] = df01['CIENCIAS'].replace(',','.',regex=True)
df01['CIENCIAS'] = pd.to_numeric(df01['CIENCIAS'])

#print(df01.info())
#print(df01[['LENGUAJE','MATEMÁTICA','PROM. LEN-MAT','HISTORIA', 'CIENCIAS']].head())

#df03= df01[df01.columns[0]]
#print(df03.head())

# Inicio aplicacion Dash

# Diagrama de la aplicación
def layout(): 
    layout = html.Div(
        [
        html.Div(  children=[
            
            html.Div(children='Seleccione una o varias pruebas:', className="menu-title"),
            dcc.Checklist(
                id ='opt_test',
                options = ['LENGUAJE', 'MATEMÁTICA', 'PROM. LEN-MAT','HISTORIA','CIENCIAS'],
                inline=True,
                value = ['LENGUAJE'],
                className='checklist',
                inputStyle={"margin-left": "20px"}

            ),
        ],
        className='menu'),

            dcc.Graph(id='graph_test', config={"displayModeBar": False},  className="wrapper"),
        ]
    )
    return layout

@callback(
    Output('graph_test', 'figure'), 
    Input('opt_test', 'value'))

def display_time_series(select_area):
    
    my_string = ", ".join(str(element) for element in select_area)

    fig_test = px.line(df01, x='AÑO', y=select_area, color='AREA',
                  title= f'RENDIMIENTO ESTUDIANTES en {my_string}',
                  width=1000, height=390,
                  labels={'value':'','variable':'PRUEBA','AÑO':'Año'},
                  color_discrete_map={'HC':'blue','TP-COM':'green','TP-IND':'orange'},
                  template="simple_white",
                  
                  )
    
    fig_test.update_traces(
        mode="markers+lines", hovertemplate=None, line=dict( width=1.5))
    
    fig_test.update_yaxes(tickfont_weight='bold',title_font_weight='bold',tickfont_size=15)
    fig_test.update_xaxes(tickfont_weight='bold',title_font_weight='bold',tickfont_size=15)

    fig_test.update_layout(
                         
                         hoverlabel_font=dict(family='Consolas', weight='bold', size=15),
                         title_font_weight='bold',
                         font_family='Consolas',
                         title_font_size=20,
                         title_x=0.5,
                         hovermode="x",
                                                 
                         )


                     
    return fig_test
# cargar en servidor
#if __name__ == '__main__':
#   app.run_server(debug=True)
    