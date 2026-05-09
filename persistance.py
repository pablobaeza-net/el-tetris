import json
import os
from datetime import datetime

class PersistenciaTetris:
    def __init__(self):
        # Nombre de la carpeta donde se guardarán los archivos
        self.carpeta_destino = "datos_guardados"
        
        # Crear la carpeta si no existe en el directorio actual
        if not os.path.exists(self.carpeta_destino):
            os.makedirs(self.carpeta_destino)

    def guardar_datos_competitivo(self, datos_jugador, puntaje):
        # 1. Obtener el NOMBRE REAL para usarlo como nombre del archivo
        nombre_real = datos_jugador.get("nombre_real", "").strip()
        
        # Si el jugador dejó el nombre real en blanco, usamos un nombre por defecto para que no falle
        if not nombre_real:
            nombre_real = "SinNombre"
            
        # Crear la ruta del archivo: datos_guardados/NombreReal.json
        nombre_archivo = f"{nombre_real}.json"
        ruta_archivo = os.path.join(self.carpeta_destino, nombre_archivo)
        
        # 2. Obtener la fecha y hora actual
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 3. Estructura del JSON con las variables solicitadas
        datos_a_guardar = {
            "_alias": datos_jugador.get("alias", "").strip(),
            "_nombre_real": nombre_real,
            "_institucion": datos_jugador.get("institucion", "").strip(),
            "_edad": datos_jugador.get("edad", "").strip(),
            "_puntaje": puntaje,
            "_ultima_actualizacion": fecha_actual
        }
        
        # 4. Validar récords previos (si el archivo ya existe)
        if os.path.exists(ruta_archivo):
            try:
                with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
                    datos_existentes = json.load(archivo)
                    puntaje_historico = datos_existentes.get("_puntaje", 0)
                    # Si el puntaje actual es menor, conservamos el histórico
                    if puntaje < puntaje_historico:
                        datos_a_guardar["_puntaje"] = puntaje_historico
            except Exception:
                pass # Si hay error leyendo, simplemente sobrescribe
        
        # 5. Guardar el archivo .json
        try:
            with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
                json.dump(datos_a_guardar, archivo, indent=4, ensure_ascii=False)
            print(f"✅ Datos guardados correctamente en: {ruta_archivo}")
        except Exception as e:
            print(f"❌ Error al guardar los datos del jugador: {e}")

    def cargar_top_puntajes(self):
        top_jugadores = []
        if not os.path.exists(self.carpeta_destino):
            return top_jugadores
            
        for nombre_archivo in os.listdir(self.carpeta_destino):
            if nombre_archivo.endswith(".json"):
                ruta = os.path.join(self.carpeta_destino, nombre_archivo)
                try:
                    with open(ruta, 'r', encoding='utf-8') as archivo:
                        datos = json.load(archivo)
                        if "_alias" in datos and "_puntaje" in datos:
                            top_jugadores.append(datos)
                except Exception:
                    continue
                    
        top_jugadores.sort(key=lambda x: x.get("_puntaje", 0), reverse=True)
        return top_jugadores