import json
import os
from datetime import datetime

class PersistenciaTetris:
    def __init__(self, archivo="highscores.json"):
        # Esto asegura que el archivo se guarde siempre en la misma carpeta que el código
        directorio_actual = os.path.dirname(os.path.abspath(__file__))
        self.archivo = os.path.join(directorio_actual, archivo)
        
        self.highscores = self.cargar()
    
    def guardar_puntaje(self, nombre, puntos):
        """Guarda nuevo puntaje"""
        score = {
            'nombre': nombre,
            'puntos': puntos,
            'fecha': datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        self.highscores.append(score)
        # Ordena de mayor a menor y se queda solo con los 10 mejores
        self.highscores = sorted(self.highscores, key=lambda x: x['puntos'], reverse=True)[:10]
        self.guardar()
    
    def cargar(self):
        """Carga highscores"""
        if os.path.exists(self.archivo):
            try:
                with open(self.archivo, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ Error al leer el archivo: {e}")
                return []
        return []
    
    def guardar(self):
        """Guarda highscores físicamente en el disco"""
        try:
            with open(self.archivo, 'w') as f:
                json.dump(self.highscores, f, indent=2)
            print(f"✅ Récords guardados exitosamente en: {self.archivo}")
        except Exception as e:
            print(f"❌ Error al intentar guardar: {e}")
    
    def top_10(self):
        """Obtiene top 10"""
        return self.highscores[:10]
    
    def nuevo_record(self, puntos):
        """¿Es nuevo récord?"""
        if not self.highscores:
            return True
        return puntos > self.highscores[-1]['puntos']