import os
from pathlib import Path
import json
import pandas as pd

# 1. Obtiene la ruta de este archivo script (calculos_proyeccion.py)
ruta_actual = Path(__file__).resolve()

# 2. Sube un nivel a la carpeta 'pages' (.parent) y entra a 'data/archivo.xlsx'
data_corp_projection_path = ruta_actual.parent.parent / "data" / "data_corp_projection.xlsx"
json_data_web_path = ruta_actual.parent.parent / "data" / "data_web_user.json"

def cargar_datos_consolidados():
    """
    Une el Excel maestro de Power Query con las ediciones hechas en la web.
    El Excel manda, pero la web puede actualizar o agregar nuevos años.
    """
    # 1. Leer datos base desde tu archivo Excel
    if data_corp_projection_path.exists():
        # Asumimos que tu Excel tiene las columnas 'PERIODO' y 'MATRICULA'
        df_excel = pd.read_excel(data_corp_projection_path, sheet_name="data_mat_proj")
        # Convertimos a diccionario string-int para procesarlo igual: {'2024': 2400, '2025': 2520}
        datos_finales = dict(zip(df_excel['PERIODO'].astype(str), df_excel['MATRICULA'].astype(int)))
    else:
        # Respaldo por si el Excel no está en la carpeta
        datos_finales = {"2024": 664, "2025": 652, "2026": 635}

    # 2. Leer si hay datos nuevos ingresados desde la interfaz web
    if json_data_web_path.exists():
        with open(json_data_web_path, "r") as f:
            datos_web = json.load(f)
        # Combinar ambos: si un año está en la web, sobreescribe o añade al del Excel
        datos_finales.update(datos_web)
        
    return datos_finales

def guardar_datos_reales(datos_dict):
    """Guarda en JSON solo lo que el usuario edita en la interfaz web."""
    with open(json_data_web_path, "w") as f:
        json.dump(datos_dict, f, indent=4)

def calcular_proyeccion_completa(retencion, captacion, crecimiento):
    """Genera el DataFrame usando el Excel mapeado como historial base."""
    # 🚀 Aquí cargamos la unión de Excel + Cambios Web
    reales_dict = cargar_datos_consolidados() 
    
    anios = [str(a) for a in range(2024, 2036)]
    registros = []
    
    # Identificar cuál es el último año real disponible (venga de Excel o Web)
    ultimo_anio_real = max([int(k) for k in reales_dict.keys()])
    valor_actual = reales_dict[str(ultimo_anio_real)]
    
    for anio in anios:
        anio_int = int(anio)
        
        if anio_int <= ultimo_anio_real:
            # Si el año existe en nuestros registros combinados, es un dato histórico real
            val = reales_dict.get(anio, None)
            registros.append({"Año": anio, "Valor": val, "Tipo": "Real"})
        else:
            # Si es un año futuro, aplicamos el modelo predictivo matemático
            efecto_retencion = valor_actual * (retencion / 100)
            efecto_crecimiento = valor_actual * (crecimiento / 100)
            valor_actual = int(efecto_retencion + captacion + efecto_crecimiento)
            registros.append({"Año": anio, "Valor": valor_actual, "Tipo": "Proyección"})
            
    return pd.DataFrame(registros), str(ultimo_anio_real)
