import os
from pathlib import Path
import json
import pandas as pd

# 1. Obtiene la ruta de este archivo script (calculos_proyeccion.py)
ruta_actual = Path(__file__).resolve()

# 2. Sube un nivel a la carpeta 'pages' (.parent) y entra a 'data/archivo.xlsx'
data_corp_projection_path = ruta_actual.parent.parent / "data" / "data_corp_projection.xlsx"

# NOTA: Dejamos la ruta original aquí por trazabilidad, pero abajo generamos la ruta específica por unidad.
json_data_web_path = ruta_actual.parent.parent / "data" / "data_web_user.json"

def obtener_ruta_json_dinamica(uni_edu):
    """
    Toma la carpeta 'data' original del proyecto y construye una ruta
    de archivo única reemplazando espacios por guiones bajos.
    Ejemplo: .../data/datos_web_BÁSICA_1.json
    """
    nombre_limpio = str(uni_edu).replace(" ", "_")
    carpeta_data = data_corp_projection_path.parent
    return carpeta_data / f"datos_web_{nombre_limpio}.json"


def cargar_datos_consolidados(uni_edu):
    """
    Une el Excel maestro de Power Query con las ediciones hechas en la web.
    El Excel manda, pero la web puede actualizar o agregar nuevos años.
    """

    # Usamos la ruta dinámica construida a partir de la ubicación original
    ruta_json_especifica = obtener_ruta_json_dinamica(uni_edu)

    # 1. Leer datos base desde tu archivo Excel
    if data_corp_projection_path.exists():
        
        # filtrar el archivo excel según la unidad académica y luego eliminar la columna UNIDAD_ACADEMICA
                
        df_excel = pd.read_excel(data_corp_projection_path, sheet_name="data_mat_proj")
        df_excel_filtrado =  df_excel.query("UNIDAD_ACADEMICA == @uni_edu").copy()
        df_filtrado_final = df_excel_filtrado.drop(columns=['UNIDAD_ACADEMICA'])






        # Convertimos a diccionario string-int para procesarlo igual: {'2024': 2400, '2025': 2520}
        datos_finales = dict(zip(df_filtrado_final['PERIODO'].astype(str), df_filtrado_final['MATRICULA'].astype(int)))
    else:
        # Respaldo por si el Excel no está en la carpeta
        datos_finales = {"2024": 664, "2025": 652, "2026": 635}

    # 2. Leer si hay datos nuevos ingresados desde la interfaz web (Aislado por unidad)
    if ruta_json_especifica.exists():
        with open(ruta_json_especifica, "r") as f:
            datos_web = json.load(f)
        # Combinar ambos: el JSON de esta unidad sobreescribe o añade años al del Excel
        datos_finales.update(datos_web)
        
     
    return datos_finales

def guardar_datos_reales(uni_edu, datos_dict):
    """Guarda en un JSON exclusivo de la unidad lo que el usuario edita en la interfaz web."""
    ruta_json_especifica = obtener_ruta_json_dinamica(uni_edu)
    
    # Asegura que la carpeta contenedora exista por precaución
    ruta_json_especifica.parent.mkdir(parents=True, exist_ok=True)
    
    with open(ruta_json_especifica, "w") as f:
        json.dump(datos_dict, f, indent=4)

def calcular_proyeccion_completa(lista_retencion, lista_nuevos, unidad_educativa):
    """Genera el DataFrame usando el Excel mapeado como historial base."""
    # 🚀 Aquí cargamos la unión de Excel + Cambios Web
    reales_dict = cargar_datos_consolidados(unidad_educativa) 
    
    anios = [str(a) for a in range(2024, 2036)]
    registros = []
    
    # Identificar cuál es el último año real disponible (venga de Excel o Web)
    if reales_dict:
        ultimo_anio_real = max([int(k) for k in reales_dict.keys()])
    else:
        ultimo_anio_real = 2026
    # Identificar cuál es el último año real disponible (venga de Excel o Web)
    #ultimo_anio_real = max([int(k) for k in reales_dict.keys()])

    #valor_actual = reales_dict[str(ultimo_anio_real)]

    # 2. Generar la proyección (esto te devuelve un DataFrame con columnas PERIODO y MATRICULA)
     # 🌟 PASO CLAVE: Pasamos las dos listas al motor por niveles
    df_proj_corp = proyeccion_por_nivel(lista_retencion, lista_nuevos, unidad_educativa)
    
    
    #df_proj_corp = proyeccion_por_nivel(retencion, captacion)
    
    for anio in anios:
        anio_int = int(anio)
        
        if anio_int <= ultimo_anio_real:
            # Si el año existe en nuestros registros combinados, es un dato histórico real
            val = reales_dict.get(anio, None)
            registros.append({"Año": anio, "Valor": val, "Tipo": "Real"})
        else:
            # Si es un año futuro, aplicamos el modelo predictivo matemático
            

            # OPTIMIZACIÓN: Buscamos directamente el año en el DataFrame sin usar un ciclo 'for'
            fila_anio = df_proj_corp[df_proj_corp['PERIODO'] == anio]
            
            if not fila_anio.empty:
                # Extraemos el valor numérico de la matrícula de esa fila específica
                valor_actual = int(fila_anio['MATRICULA'].values[0])
                registros.append({"Año": anio, "Valor": valor_actual, "Tipo": "Proyección"})

           
            
    
    return pd.DataFrame(registros), str(ultimo_anio_real)

   
def proyeccion_por_nivel(lista_retencion, lista_nuevos, unidad_educativa):

    """
    Motor analítico por niveles de enseñanza básica de Chile.
    lista_retencion: 10 porcentajes desde Pre-Kinder hasta 8° Básico.
    lista_nuevos: 10 cantidades de alumnos nuevos desde Pre-Kinder hasta 8° Básico.
    """


    df_nivel = pd.read_excel(data_corp_projection_path, sheet_name="data_proj")

    # Filtra donde el valor de la columna 'Nombre' sea exactamente 'Juan'

    df_nivel_filtrado = df_nivel.query("UNIDAD_ACADEMICA == @unidad_educativa").copy()

    #df_nivel_filtrado = df_nivel[df_nivel['UNIDAD_ACADEMICA'] == 'BÁSICA 1']
    
    # SOLUCIÓN: Convertimos absolutamente todas las columnas a texto (str)
    # Esto transforma el número 2026 en texto '2026' de inmediato
    df_nivel_filtrado.columns = df_nivel_filtrado.columns.astype(str)

    # Inicializar columnas futuras
    for year in range(2027, 2036):
        df_nivel_filtrado[str(year)] = 0.0

    # 1. Convertimos el porcentaje de retención a decimal (ej: de 85 a 0.85)
    # Si tus sliders ya envían decimales (ej: 0.85), usa directamente: tasa_ret = retención
    #tasa_ret = retención / 100 if retención > 1 else retención
    
    # 2. Cantidad fija de alumnos nuevos que entran por nivel cada año
    # Usamos la variable 'captacion' como el valor fijo de nuevos ingresos
    #nuevos_estudiantes_por_nivel = captacion 


    for periodo in range(2027, 2036):
        j = df_nivel_filtrado.columns.get_loc(str(periodo)) # Columna actual
        j_anterior = df_nivel_filtrado.columns.get_loc(str(periodo - 1)) # Columna año anterior(ej: 2026)

          # 🔄 CICLO POR NIVEL EDUCATIVO (Filas: 0 a 9)
        for nivel in range (len(df_nivel_filtrado)):
            
            # 🌟 EXTRAER VALORES DEL SLIDER CORRESPONDIENTES A ESTA FILA (NIVEL) SPECÍFICA
            # Convertimos el porcentaje del slider actual a decimal (ej: 95 -> 0.95)
            tasa_ret_nivel = lista_retencion[nivel] / 100 if lista_retencion[nivel] > 1 else lista_retencion[nivel]
            alumnos_nuevos_nivel = lista_nuevos[nivel]
            


            if nivel == 0:
                # Pre-Kinder (Primer nivel, no viene de un nivel anterior). 
                # Se mantiene tu regla base pero sumando sus alumnos nuevos correspondientes del slider
                 # SOLUCIÓN: Buscamos la posición numérica de la columna '2026'
                j_2026 = df_nivel_filtrado.columns.get_loc('2026')

                df_nivel_filtrado.iloc[nivel, j] = df_nivel_filtrado.iloc[nivel, j_2026] + alumnos_nuevos_nivel

            else:
                
                # Cohorte: Los que estaban el año pasado en el nivel anterior (nivel - 1) 
                # se multiplican por la tasa de retención del nivel actual
                alumnos_que_pasan = df_nivel_filtrado.iloc[nivel - 1, j_anterior] * tasa_ret_nivel

                # Sumamos los estudiantes nuevos destinados específicamente a este nivel
                total_calculado = alumnos_que_pasan + alumnos_nuevos_nivel

                 # Calculamos el flujo con decimales primero
                #alumnos_que_pasan = df_nivel.iloc[nivel - 1, j_anterior] * tasa_ret
                #total_calculado = alumnos_que_pasan + nuevos_estudiantes_por_nivel
                
                # APLICACIÓN DEL ROUND: Redondeamos a 0 decimales el total antes de asignarlo
                df_nivel_filtrado.iloc[nivel, j] = int(round(total_calculado, 0))
    
    # --- AGREGA ESTAS LÍNEAS AQUÍ (FUERA DE LOS CICLOS FOR) ---
    # Convertimos las columnas proyectadas a tipo entero antes de retornar
    columnas_proyeccion = [str(y) for y in range(2027, 2036)]
    df_nivel_filtrado[columnas_proyeccion] = df_nivel_filtrado[columnas_proyeccion].astype(int)

     # =====================================================================
    # NUEVO: AGREGAR FILA DE TOTALES ANTES DE SALIR DE LA FUNCIÓN
    # =====================================================================
    # 1. Sumamos verticalmente solo las columnas numéricas de los años
    totales_años = df_nivel_filtrado.sum(numeric_only=True)
    
    # 2. Creamos la estructura de la fila final combinando texto y sumas
    fila_total = {
        'UNIDAD_ACADEMICA': df_nivel_filtrado['UNIDAD_ACADEMICA'].iloc[0], # Copia "BÁSICA 1"
        'NIVEL': 'TOTAL UNIDAD'                                   # Nombre de la fila
    }
    
    # Rellenamos el diccionario con los resultados de las sumas anuales
    for col, suma in totales_años.items():
        fila_total[col] = suma

    # 3. Insertamos la fila de totales al final del DataFrame original
    df_total_fila = pd.DataFrame([fila_total])
    df_nivel_filtrado = pd.concat([df_nivel_filtrado, df_total_fila], ignore_index=True)

    # 4. Homogeneizamos todo el bloque de años (incluyendo el TOTAL) a números enteros
    columnas_años = [str(y) for y in range(2026, 2036)]
    df_nivel_filtrado[columnas_años] = df_nivel_filtrado[columnas_años].astype(int)

    df_totales_proyectados =df_nivel_filtrado.iloc[[-1]] # última fila

    # 1. Seleccionamos solo las columnas que no son de texto (las de los años)
    df_totales_proyectados = df_totales_proyectados.drop(columns=['UNIDAD_ACADEMICA', 'NIVEL'])

# 2. Pivoteamos para que queden solo las dos columnas deseadas
    df_totales_proyectados = df_totales_proyectados.melt(var_name='PERIODO', value_name='MATRICULA')
    df_totales_proyectados = df_totales_proyectados[df_totales_proyectados['PERIODO'] != '2026']

    return df_totales_proyectados

def test_multiple_slider(retencion_por_nivel):
    """
    Recibe una lista de 10 valores de los sliders 
    y multiplica una columna de un DataFrame de ejemplo.
    """
    # Creamos un DataFrame de prueba con una columna base de unos
    df_original = pd.DataFrame({"Valores_Base": [10, 20, 30, 40, 50, 60, 70, 80,90, 100]})
    
    # Supongamos que multiplicas la fila i del DF por el valor del slider i
    # (Aquí va tu lógica real de multiplicación)
    df_original["Resultado"] = df_original["Valores_Base"] * retencion_por_nivel/100
    df_original=df_original.round(0).astype(int)
    
    # Retornamos el resultado formateado como texto para el ejemplo
    return df_original.to_string()
# =====================================================================
# BLOQUE DE PRUEBA EXCLUSIVO PARA LA ÚLTIMA FUNCIÓN
# =====================================================================
if __name__ == "__main__":
    print("--- INICIANDO PRUEBA AISLADA: proyeccion_por_nivel ---")
    print(f"Ruta detectada para el Excel: {data_corp_projection_path}\n")
    
    # 1. Valores simulados para los argumentos (Sliders)
    mi_retencion = 95
    mi_captacion = 12
    
    try:
        # 2. Invocamos ÚNICAMENTE la última función
        df_resultado = proyeccion_por_nivel(mi_retencion, mi_captacion)
        df_previo = calcular_proyeccion_completa(mi_retencion,mi_captacion)
        
        # 3. Verificamos que se hayan agregado correctamente las 9 columnas
        print("¡Éxito! El archivo se leyó correctamente.")
        print("\nLista completa de columnas generadas en el DataFrame:")
        print(list(df_resultado.columns))
        
        pd.set_option('display.max_columns', None)       # Muestra todas las columnas
        pd.set_option('display.expand_frame_repr', False) # Evita saltos de línea feos
        
        print("\n=== DATAFRAME COMPLETO (11 FILAS Y TODAS LAS COLUMNAS) ===")
        print(df_resultado) # Imprime las 11 filas completas sin recortar nada
        print(df_previo)
        
    except FileNotFoundError:
        print("❌ ERROR: No se encontró el archivo Excel.")
        print(f"Verifica que exista un archivo llamado 'data_corp_projection.xlsx' dentro de la carpeta: {data_corp_projection_path.parent}")
    except Exception as e:
        print(f"❌ Ocurrió un error inesperado: {e}")