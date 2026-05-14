import pygame
import sys
import os
from logica import LogicaTetris
from vista2 import VistaTetris
from persistance import PersistenciaTetris 

class JuegoTetris:
    def __init__(self):
        pygame.init()
        # Ajuste de pantalla
        self.pantalla = pygame.display.set_mode((500, 800))
        pygame.display.set_caption("TETRIS")
        
        # Movimiento fluido
        pygame.key.set_repeat(150, 40) 
        
        self.logica = LogicaTetris()
        self.vista = VistaTetris(self.pantalla)
        self.persistencia = PersistenciaTetris()
        
        self.estado = "menu_modos"
        self.seleccion_menu = 0
        self.modo_juego = "entrenamiento"
        
        # Datos para el registro
        self.datos_jugador = {
            "alias": "",
            "nombre_real": "",
            "institucion": "",
            "edad": ""
        }
        self.campo_actual = 0 
        
        self.drop_time = 0
        self.drop_speed = 800

    def ejecutar(self):
        while True:
            eventos = pygame.event.get()
            for event in eventos:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            if self.estado == "menu_modos":
                self.manejar_menu_modos(eventos)
            elif self.estado == "registro":
                self.manejar_registro(eventos)
            elif self.estado == "jugando":
                self.actualizar_juego(eventos)
            elif self.estado == "gameover":
                self.manejar_gameover(eventos)

            pygame.time.Clock().tick(60)

    def manejar_menu_modos(self, eventos):
        for event in eventos:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.seleccion_menu = (self.seleccion_menu - 1) % 3
                elif event.key == pygame.K_DOWN:
                    self.seleccion_menu = (self.seleccion_menu + 1) % 3
                elif event.key == pygame.K_1: self.seleccion_menu = 0
                elif event.key == pygame.K_2: self.seleccion_menu = 1
                elif event.key == pygame.K_3: self.seleccion_menu = 2
                
                elif event.key == pygame.K_RETURN:
                    if self.seleccion_menu == 0:
                        self.modo_juego = "entrenamiento"
                        self.estado = "registro"
                    elif self.seleccion_menu == 1:
                        self.modo_juego = "competitivo"
                        self.estado = "registro"
                    elif self.seleccion_menu == 2:
                        pygame.quit()
                        sys.exit()
        
        self.vista.dibujar_menu_modos(self.seleccion_menu)

    def manejar_registro(self, eventos):
        campos = ["alias", "nombre_real", "institucion", "edad"]
        es_comp = (self.modo_juego == "competitivo")
        
        for event in eventos:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.estado = "menu_modos"
                elif event.key == pygame.K_UP:
                    self.campo_actual = (self.campo_actual - 1) % 4
                elif event.key == pygame.K_DOWN:
                    self.campo_actual = (self.campo_actual + 1) % 4
                elif event.key == pygame.K_BACKSPACE:
                    campo = campos[self.campo_actual]
                    self.datos_jugador[campo] = self.datos_jugador[campo][:-1]
                elif event.key == pygame.K_RETURN:
                    # Validar
                    alias_ok = self.datos_jugador["alias"].strip() != ""
                    if es_comp:
                        otros_ok = all(self.datos_jugador[c].strip() != "" for c in campos)
                        try:
                            edad = int(self.datos_jugador["edad"])
                            edad_ok = 5 <= edad <= 100
                        except: edad_ok = False
                        
                        if alias_ok and otros_ok and edad_ok:
                            self.reiniciar()
                            self.estado = "jugando"
                    else:
                        if alias_ok:
                            self.reiniciar()
                            self.estado = "jugando"
                else:
                    if len(self.datos_jugador[campos[self.campo_actual]]) < 15:
                        if event.unicode.isalnum() or event.unicode == " ":
                            self.datos_jugador[campos[self.campo_actual]] += event.unicode

        self.vista.dibujar_registro(self.datos_jugador, self.campo_actual, es_comp)

    def actualizar_juego(self, eventos):
        ahora = pygame.time.get_ticks()
        if ahora - self.drop_time > self.drop_speed:
            if self.logica.bajar():
                self.estado = "gameover"
            self.drop_time = ahora

        for event in eventos:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT: self.logica.mover(-1, 0)
                elif event.key == pygame.K_RIGHT: self.logica.mover(1, 0)
                elif event.key == pygame.K_DOWN:
                    if self.logica.bajar(): self.estado = "gameover"
                elif event.key == pygame.K_UP: self.logica.rotar()
                elif event.key == pygame.K_SPACE:
                    if self.logica.hard_drop(): self.estado = "gameover"
                elif event.key == pygame.K_c: self.logica.hacer_hold()
                elif event.key == pygame.K_ESCAPE: self.estado = "menu_modos"

        siguiente = getattr(self.logica, 'siguiente_pieza', None)
        hold = getattr(self.logica, 'pieza_hold', None)
        
        # ✅ CORRECCIÓN AQUÍ: Se usa el nombre real de tu función
        top = self.persistencia.cargar_top_puntajes()

        self.vista.dibujar_tablero(
            self.logica.tablero,
            self.logica.pieza,
            self.logica.x,
            self.logica.y,
            self.logica.puntos,
            siguiente,
            hold,
            top,
            self.modo_juego
        )

    def manejar_gameover(self, eventos):
        for event in eventos:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # ✅ CORRECCIÓN AQUÍ: Se guarda solo si es modo competitivo, usando tu función original
                    if self.modo_juego == "competitivo":
                        self.persistencia.guardar_datos_competitivo(self.datos_jugador, self.logica.puntos)
                    self.estado = "menu_modos"
        
        self.vista.dibujar_gameover(self.logica.puntos, self.modo_juego)

    def reiniciar(self):
        self.logica = LogicaTetris()
        self.drop_time = pygame.time.get_ticks()

if __name__ == "__main__":
    juego = JuegoTetris()
    juego.ejecutar()