import dash
from dash import html
import dash_bootstrap_components as dbc


# Toggle the themes at [dbc.themes.LUX]
# The full list of available themes is:
# BOOTSTRAP, CERULEAN, COSMO, CYBORG, DARKLY, FLATLY, JOURNAL, LITERA, LUMEN,
# LUX, MATERIA, MINTY, PULSE, SANDSTONE, SIMPLEX, SKETCHY, SLATE, SOLAR,
# SPACELAB, SUPERHERO, UNITED, YETI, ZEPHYR.
# To see all themes in action visit:
# https://dash-bootstrap-components.opensource.faculty.ai/docs/themes/explorer/


# To use Font Awesome Icons
FA621 = "https://use.fontawesome.com/releases/v6.2.1/css/all.css"
APP_TITLE = "Rendimientos LMLA 2024"
image_path = 'assets/Original-Apaisado.png'

app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.CERULEAN,  # Dash Themes CSS
        FA621,  # Font Awesome Icons CSS
    ],
    title=APP_TITLE,
    use_pages=True,  
)

server = app.server

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Rendimiento", class_name='option_menu_side', href="/rendimientos")),
        dbc.NavItem(dbc.NavLink("PSU PAES PDT", class_name='option_menu_side',href="/psupdtpaes")),
        dbc.NavItem(dbc.NavLink("Ensayos PAES", class_name='option_menu_side', href="/ensayos_paes")),
        dbc.NavItem(dbc.NavLink("Ensayos SIMCE", class_name='option_menu_side', href="/simce_ensayos")),
        dbc.DropdownMenu(
            size="md",
            children=[
                #dbc.DropdownMenuItem("Etapa", header=True),
                dbc.DropdownMenuItem("Diagnóstico", href="/diadiagnostico"),
                dbc.DropdownMenuItem("Intermedio/Final", href="/diaintfin"),
            ],
            nav=True,
            in_navbar=True,
            label="DIA",
            ),
        ],
   
    brand="Liceo Particular Mixto Los Andes",
    brand_href="/",
    color="#b51808",
    dark=True,
   )
    
app.layout = html.Div(
                children=[
                    navbar,
                    dash.page_container
                ],
            )

if __name__ == '__main__':
    app.run_server(debug=True)