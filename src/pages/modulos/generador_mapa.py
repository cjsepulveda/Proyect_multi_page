import plotly.express as px
import json
from pyproj import Transformer
import pathlib

# Cargamos el GeoJSON y re-proyectamos las coordenadas UNA SOLA VEZ al importar el archivo,
# lo que optimiza la velocidad del dashboard drásticamente.
#path = pathlib.Path(__file__).parent
#data_path= path.joinpath("data").resolve()

data_geojson = pathlib.Path(__file__).resolve().parent.parent.joinpath("data").joinpath("comunas_aconcagua_santiago.geojson")

with open(data_geojson, 'r', encoding='utf-8') as archivo:
    geojson_chile = json.load(archivo)

# --- REPARACIÓN DE COORDENADAS (De Mercator a Latitud/Longitud) ---
# Transforma los números grandes de tu GeoJSON a coordenadas que Plotly entienda
transformer = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)
for feature in geojson_chile['features']:
    geom_type = feature['geometry']['type']
    coords = feature['geometry']['coordinates']
    if geom_type == "Polygon":
        feature['geometry']['coordinates'] = [[transformer.transform(x, y) for x, y in ring] for ring in coords]
    elif geom_type == "MultiPolygon":
        feature['geometry']['coordinates'] = [[[transformer.transform(x, y) for x, y in ring] for ring in polygon] for polygon in coords]


def actualizar_mapa_comunas(df_filtrado):
    """
    Recibe un DataFrame filtrado por el colegio seleccionado 
    y genera un nuevo mapa coroplético con los colores actualizados.
    """
    # Crear la figura MapLibre moderna con los nuevos datos
    fig = px.choropleth_map(
        df_filtrado,                       # El DataFrame que viene desde el callback
        geojson=geojson_chile,
        locations='Comuna',                 
        featureidkey='properties.Comuna',   
        color='Estudiantes',      # Columna que define la intensidad del color
        color_continuous_scale="Reds",  # Escala de colores (puedes cambiarla)
        map_style="carto-positron",     # Estilo moderno de MapLibre
        center={"lat": -32.75, "lon": -70.70}, 
        zoom=7.7,                           
        opacity=0.6,
        labels={'Estudiantes': 'N° Alumnos'}
    )

    fig.update_layout(
        margin={"r":0,"t":40,"l":0,"b":50},
        title_text="Concentración de Estudiantes por Comuna en el Valle del Aconcagua"
    )
    
    return fig
