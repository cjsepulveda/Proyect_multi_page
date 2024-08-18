from dash import html, register_page  #, callback # If you need callbacks, import it here.

register_page(
    __name__,
    name='HOME',
    top_nav=True,
    path='/'
)


def layout():
    layout = html.Div([
        html.P(
            [
                "Elija una opción desde el menu"
            ], className='home'
        )
    ])
    return layout