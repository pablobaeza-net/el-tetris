import pygame
import sys
from logica import LogicaTetris
from vista2 import VistaTetris
from persistance import PersistenciaTetris


class JuegoTetris:
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((500, 750))
        pygame.display.set_caption("Tetris Competitivo")
        
        # Música
        pygame.mixer.init()
        try:
            pygame.mixer.music.load("musi.mp3") 
            pygame.mixer.music.set_volume(0.4)
            pygame.mixer.music.play(-1)
        except:
            print("Archivo 'musi.mp3' no encontrado, iniciando en silencio.")

        self.logica = LogicaTetris()
        self.vista = VistaTetris(self.pantalla)
        self.persistencia = PersistenciaTetris()
        
        self.estado = "inicio_modo" 
        self.modo_juego = None
        self.seleccion_menu = 0
        self.datos_jugador = {"alias": "", "nombre_real": "", "institucion": "", "edad": ""}
        self.campos_lista = ["alias", "nombre_real", "institucion", "edad"]
        self.campo_activo = 0  
        self.drop_time = 0
        self.drop_speed = 500
        self.top_puntajes = []

    def reiniciar(self):
        self.logica = LogicaTetris()
        self.drop_time = pygame.time.get_ticks()
        
    def iniciar_partida(self):
        self.reiniciar()
        self.estado = "juego"

    def ejecutar(self):
        reloj = pygame.time.Clock()
        while True:
            eventos = pygame.event.get()
            for event in eventos:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            if self.estado == "inicio_modo":
                self.manejar_menu_modos(eventos)
            elif self.estado == "registro":
                self.manejar_registro(eventos)
            elif self.estado == "juego":
                self.actualizar_juego(eventos)
            elif self.estado == "gameover":
                self.manejar_gameover(eventos)
            
            reloj.tick(60)

    def manejar_menu_modos(self, eventos):
        for event in eventos:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and self.seleccion_menu > 0:
                    self.seleccion_menu -= 1
                elif event.key == pygame.K_DOWN and self.seleccion_menu < 2:
                    self.seleccion_menu += 1
                elif event.key == pygame.K_RETURN:
                    if self.seleccion_menu == 0:
                        self.modo_juego = "entrenamiento"
                        self.iniciar_partida()
                    elif self.seleccion_menu == 1:
                        self.modo_juego = "competitivo"
                        self.datos_jugador = {"alias": "", "nombre_real": "", "institucion": "", "edad": ""}
                        self.campo_activo = 0
                        self.estado = "registro"
                    elif self.seleccion_menu == 2:
                        pygame.quit()
                        sys.exit()
        
        # ¡ESTA ES LA LÍNEA QUE FALTABA! Por esto se veía todo negro.
        self.vista.dibujar_menu_modos(self.seleccion_menu)

    def manejar_registro(self, eventos):
        for event in eventos:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.estado = "inicio_modo"
                elif event.key == pygame.K_UP:
                    self.campo_activo = (self.campo_activo - 1) % 4
                elif event.key in [pygame.K_DOWN, pygame.K_TAB]:
                    self.campo_activo = (self.campo_activo + 1) % 4
                elif event.key == pygame.K_RETURN:
                    # Obligamos a que tenga al menos un alias para continuar
                    if self.datos_jugador["alias"].strip() != "":
                        self.iniciar_partida()
                elif event.key == pygame.K_BACKSPACE:
                    c = self.campos_lista[self.campo_activo]
                    self.datos_jugador[c] = self.datos_jugador[c][:-1]
                else:
                    c = self.campos_lista[self.campo_activo]
                    if len(self.datos_jugador[c]) < 20 and event.unicode.isprintable():
                        self.datos_jugador[c] += event.unicode
        self.vista.dibujar_registro(self.datos_jugador, self.campo_activo)

    def actualizar_juego(self, eventos):
        for event in eventos:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT: self.logica.mover(-1, 0)
                elif event.key == pygame.K_RIGHT: self.logica.mover(1, 0)
                elif event.key == pygame.K_DOWN: self.logica.bajar()
                elif event.key == pygame.K_UP: self.logica.rotar()
                elif event.key == pygame.K_SPACE: self.logica.hard_drop()
                elif event.key == pygame.K_h: self.logica.hacer_hold()
                elif event.key == pygame.K_ESCAPE: self.estado = "inicio_modo"
        
        now = pygame.time.get_ticks()
        if now - self.drop_time > self.drop_speed:
            if self.logica.bajar():
                if self.modo_juego == "competitivo":
                    self.persistencia.guardar_datos_competitivo(self.datos_jugador, self.logica.puntos)
                self.estado = "gameover"
            self.drop_time = now
        
        self.vista.dibujar_tablero(
            self.logica.tablero, 
            self.logica.pieza, 
            self.logica.x, 
            self.logica.y, 
            self.logica.puntos, 
            self.logica.siguiente_pieza, 
            self.logica.pieza_hold, 
            self.top_puntajes
        )

    def manejar_gameover(self, eventos):
        for event in eventos:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN: self.estado = "inicio_modo"
        self.vista.dibujar_gameover(self.logica.puntos)

if __name__ == "__main__":
    juego = JuegoTetris()
    juego.ejecutar()