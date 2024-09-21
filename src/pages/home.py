from dash import html, register_page  #, callback # If you need callbacks, import it here.

register_page(
    __name__,
    name='HOME',
    top_nav=True,
    path='/'
)

image_path = 'assets/Original-Apaisado.png'

def layout():
    layout = html.Div([
        html.Img(src=image_path),
        html.P(
            [
                "Análisis de Datos, elija una opción del menu"
            ], className='home'
        )
    ])
    return layout