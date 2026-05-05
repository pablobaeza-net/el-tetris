import pygame
import sys
import os
from logica import LogicaTetris
from vista2 import VistaTetris       # Mantenemos "vista2" porque te funcionó perfecto
from persistance import PersistenciaTetris 

class JuegoTetris:
    def __init__(self):
        pygame.init()
        # Inicializar el mezclador de audio de Pygame
        pygame.mixer.init() 
        
        pygame.key.set_repeat(200, 50) 
        
        self.logica = LogicaTetris()
        self.vista = VistaTetris()
        self.persistencia = PersistenciaTetris()
        self.estado = "menu"
        self.drop_time = 0
        self.drop_speed = 800
        self.seleccion_menu = 0
        self.seleccion_gameover = 0
        self.nombre_jugador = ""
        self.input_activo = False

        # Lógica para cargar y reproducir la música de forma segura (usando os.path)
        try:
            # Detecta la carpeta donde está este main.py y busca "musi.mp3" ahí
            carpeta_juego = os.path.dirname(__file__)
            ruta_musica = os.path.join(carpeta_juego, "musi.mp3")
            
            pygame.mixer.music.load(ruta_musica) 
            pygame.mixer.music.set_volume(0.3)  # Volumen al 30%
            pygame.mixer.music.play(-1)         # Repetir infinitamente
        except Exception as e:
            print(f"⚠️ No se pudo cargar la música. Verifica el nombre del archivo. Error: {e}")
    
    def ejecutar(self):
        reloj = pygame.time.Clock()
        
        while True:
            eventos = pygame.event.get()
            for event in eventos:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            highscores = self.persistencia.top_10()
            
            if self.estado == "menu":
                self.manejar_menu(eventos, highscores)
            elif self.estado == "highscores":
                self.manejar_highscores(eventos)
            elif self.estado == "juego":
                self.actualizar_juego(eventos)
            elif self.estado == "gameover":
                self.manejar_gameover(eventos)
            
            reloj.tick(60)
    
    def manejar_menu(self, eventos, highscores):
        for event in eventos:
            if event.type == pygame.KEYDOWN:
                # Navegación con flechas
                if event.key == pygame.K_UP and self.seleccion_menu > 0:
                    self.seleccion_menu -= 1
                elif event.key == pygame.K_DOWN and self.seleccion_menu < 2:
                    self.seleccion_menu += 1
                
                # Seleccionar con Enter
                elif event.key == pygame.K_RETURN:
                    if self.seleccion_menu == 0: 
                        self.reiniciar() # Limpia el tablero al empezar
                        self.estado = "juego"
                    elif self.seleccion_menu == 1: 
                        self.estado = "highscores"
                    elif self.seleccion_menu == 2: 
                        pygame.quit()
                        sys.exit()

                # Atajos con teclas numéricas (1, 2, 3)
                elif event.key == pygame.K_1 or event.key == pygame.K_KP1:
                    self.reiniciar()
                    self.estado = "juego"
                elif event.key == pygame.K_2 or event.key == pygame.K_KP2:
                    self.estado = "highscores"
                elif event.key == pygame.K_3 or event.key == pygame.K_KP3:
                    pygame.quit()
                    sys.exit()
                    
        # Pasamos la selección a la vista para que el botón "brille"
        self.vista.dibujar_menu(highscores, self.seleccion_menu)
    
    def manejar_highscores(self, eventos):
        for event in eventos:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    self.estado = "menu"
        highscores = self.persistencia.top_10()
        self.vista.dibujar_highscores(highscores)
    
    def actualizar_juego(self, eventos):
        for event in eventos:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT: self.logica.mover(-1, 0)
                elif event.key == pygame.K_RIGHT: self.logica.mover(1, 0)
                elif event.key == pygame.K_DOWN: self.logica.bajar()
                elif event.key == pygame.K_UP: self.logica.rotar()
                elif event.key == pygame.K_SPACE: 
                    self.logica.hard_drop()
                    self.logica.puntos += 2
                elif event.key == pygame.K_ESCAPE:
                    self.estado = "menu"
        
        now = pygame.time.get_ticks()
        if now - self.drop_time > self.drop_speed:
            game_over = self.logica.bajar()
            self.drop_time = now
            if game_over:
                self.estado = "gameover"
                self.seleccion_gameover = 0 # Reset del selector
        
        self.vista.dibujar_tablero(
            self.logica.tablero, self.logica.pieza,
            self.logica.x, self.logica.y, self.logica.puntos
        )
    
    def manejar_gameover(self, eventos):
        if not self.input_activo:
            for event in eventos:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and self.seleccion_gameover > 0:
                        self.seleccion_gameover -= 1
                    elif event.key == pygame.K_DOWN and self.seleccion_gameover < 1:
                        self.seleccion_gameover += 1
                    elif event.key == pygame.K_RETURN:
                        if self.seleccion_gameover == 0:
                            self.input_activo = True
                        else:
                            self.estado = "menu"
                            
            self.vista.dibujar_gameover(self.logica.puntos, self.seleccion_gameover)
        else:
            self.manejar_input_nombre(eventos)
    
    def manejar_input_nombre(self, eventos):
        now = pygame.time.get_ticks()
        cursor = "_" if now % 1000 < 500 else ""
        nombre_display = self.nombre_jugador + cursor
        
        for event in eventos:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    self.nombre_jugador = self.nombre_jugador[:-1]
                elif event.key == pygame.K_RETURN and len(self.nombre_jugador) >= 1:
                    # Al presionar enter guarda y vuelve al menú principal
                    self.persistencia.guardar_puntaje(self.nombre_jugador.upper(), self.logica.puntos)
                    print(f"✅ Guardado: {self.nombre_jugador} - {self.logica.puntos}")
                    self.estado = "menu"
                    self.input_activo = False
                    self.nombre_jugador = ""
                else:
                    # Añade las letras al nombre si es alfanumérico y no excede 10 caracteres
                    if len(self.nombre_jugador) < 10 and event.unicode.isalnum():
                        self.nombre_jugador += event.unicode.upper()

        self.vista.dibujar_gameover_input(self.logica.puntos, nombre_display)
    
    def reiniciar(self):
        self.logica = LogicaTetris()
        self.drop_time = pygame.time.get_ticks()
        self.estado = "juego"

if __name__ == "__main__":
    juego = JuegoTetris()
    juego.ejecutar()