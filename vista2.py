import pygame

# Colores
NEGRO = (20, 20, 20)
BLANCO = (255, 255, 255)
GRIS = (50, 50, 50)
AMARILLO = (255, 200, 0)
AZUL = (0, 150, 255)
ROJO = (255, 50, 50)
VERDE = (0, 200, 100)

COLORES_PIEZAS = [
    (0, 255, 255),   # I - Cyan
    (255, 255, 0),   # O - Amarillo
    (128, 0, 128),   # T - Morado
    (0, 255, 0),     # S - Verde
    (255, 0, 0),     # Z - Rojo
    (0, 0, 255),     # J - Azul
    (255, 165, 0)    # L - Naranja
]

class VistaTetris:
    def __init__(self, pantalla):
        self.pantalla = pantalla
        pygame.font.init()
        self.fuente_grande = pygame.font.SysFont("Arial", 60, bold=True)
        self.fuente_titulos = pygame.font.SysFont("Arial", 45, bold=True)
        self.fuente_med = pygame.font.SysFont("Arial", 30, bold=True)
        self.fuente_peq = pygame.font.SysFont("Arial", 20)
        self.tam_bloque = 28

    def dibujar_menu_modos(self, seleccion=0):
        self.pantalla.fill(AZUL)
        titulo = self.fuente_grande.render("TETRIS", True, BLANCO)
        self.pantalla.blit(titulo, ((500 - titulo.get_width()) // 2, 120))
        
        subtitulo = self.fuente_med.render("SELECCIONA UN MODO", True, AMARILLO)
        self.pantalla.blit(subtitulo, ((500 - subtitulo.get_width()) // 2, 220))
        
        opciones = [
            ("1 ▶️ ENTRENAMIENTO", VERDE, 370),
            ("2 🏆 COMPETITIVO", AMARILLO, 470),
            ("3 ❌ SALIR", ROJO, 570)
        ]
        
        for i, (texto, color_base, y) in enumerate(opciones):
            color_fondo = color_base if i == seleccion else GRIS
            grosor_borde = 6 if i == seleccion else 2
            color_texto = BLANCO if i == seleccion else (200, 200, 200)
            
            surf = self.fuente_med.render(texto, True, color_texto)
            rect = surf.get_rect(center=(250, y))
            
            pygame.draw.rect(self.pantalla, color_fondo, rect.inflate(160, 60))
            pygame.draw.rect(self.pantalla, BLANCO, rect.inflate(160, 60), grosor_borde)
            self.pantalla.blit(surf, rect)
        
        instruc = self.fuente_peq.render("↑↓ Seleccionar | ⏎ Enter | 1-3 Atajos", True, BLANCO)
        self.pantalla.blit(instruc, ((500 - instruc.get_width()) // 2, 680))
        pygame.display.flip()

    def dibujar_registro(self, datos, campo_actual):
        self.pantalla.fill(NEGRO)
        
        titulo = self.fuente_titulos.render("DATOS JUGADOR", True, AMARILLO)
        self.pantalla.blit(titulo, ((500 - titulo.get_width()) // 2, 50))
        
        campos_nombres = ["alias", "nombre_real", "institucion", "edad"]
        etiquetas = ["Alias (Obligatorio):", "Nombre Real:", "Institución:", "Edad:"]
        
        y_base = 130
        for i, campo in enumerate(campos_nombres):
            lbl = self.fuente_med.render(etiquetas[i], True, BLANCO)
            self.pantalla.blit(lbl, (50, y_base + (i * 100)))
            
            color_caja = VERDE if i == campo_actual else GRIS
            pygame.draw.rect(self.pantalla, color_caja, (50, y_base + 35 + (i * 100), 400, 40), 2)
            
            txt = self.fuente_med.render(datos[campo] + ("_" if i == campo_actual else ""), True, BLANCO if i == campo_actual else (150, 150, 150))
            self.pantalla.blit(txt, (60, y_base + 40 + (i * 100)))

        instruc = self.fuente_peq.render("↓↑ Moverse | ⏎ Enter para avanzar/jugar | ESC Volver", True, BLANCO)
        self.pantalla.blit(instruc, ((500 - instruc.get_width()) // 2, 680))
        pygame.display.flip()

    def dibujar_tablero(self, tablero, pieza, x, y, puntos, siguiente_pieza, pieza_hold, top_puntajes):
        self.pantalla.fill(NEGRO)
        
        offset_x, offset_y = 50, 40 
        
        # Fondo del tablero
        pygame.draw.rect(self.pantalla, GRIS, (offset_x, offset_y, 10 * self.tam_bloque, 20 * self.tam_bloque), 2)
        
        # Dibujar matriz fija
        for i, fila in enumerate(tablero):
            for j, celda in enumerate(fila):
                if celda:
                    color = COLORES_PIEZAS[celda - 1]
                    px = offset_x + j * self.tam_bloque
                    py = offset_y + i * self.tam_bloque
                    pygame.draw.rect(self.pantalla, color, (px, py, self.tam_bloque, self.tam_bloque))
                    pygame.draw.rect(self.pantalla, BLANCO, (px, py, self.tam_bloque, self.tam_bloque), 1)
        
        # Dibujar pieza que cae
        color_pieza = COLORES_PIEZAS[pieza['color_idx']]
        for i, fila in enumerate(pieza['forma']):
            for j, celda in enumerate(fila):
                if celda:
                    px = offset_x + (x + j) * self.tam_bloque
                    py = offset_y + (y + i) * self.tam_bloque
                    if py >= offset_y:
                        pygame.draw.rect(self.pantalla, color_pieza, (px, py, self.tam_bloque, self.tam_bloque))
                        pygame.draw.rect(self.pantalla, BLANCO, (px, py, self.tam_bloque, self.tam_bloque), 1)

        # Panel lateral derecho
        panel_x = 350
        pygame.draw.rect(self.pantalla, GRIS, (panel_x, offset_y, 130, 560))
        pygame.draw.rect(self.pantalla, BLANCO, (panel_x, offset_y, 130, 560), 3)
        
        # Puntos
        p_txt = self.fuente_med.render(f"{puntos}", True, AMARILLO)
        self.pantalla.blit(p_txt, (panel_x + 20, 60))
        p_label = self.fuente_peq.render("PUNTOS", True, BLANCO)
        self.pantalla.blit(p_label, (panel_x + 15, 90))
        
        # Siguiente
        n_label = self.fuente_peq.render("SIGUIENTE", True, AMARILLO)
        self.pantalla.blit(n_label, (panel_x + 15, 140))
        pygame.draw.rect(self.pantalla, NEGRO, (panel_x + 10, 165, 110, 80))
        pygame.draw.rect(self.pantalla, BLANCO, (panel_x + 10, 165, 110, 80), 2)
        if siguiente_pieza:
            self.dibujar_pieza_mini(siguiente_pieza, panel_x + 25, 180)
            
        # Hold
        h_label = self.fuente_peq.render("HOLD (H)", True, VERDE)
        self.pantalla.blit(h_label, (panel_x + 15, 260))
        pygame.draw.rect(self.pantalla, NEGRO, (panel_x + 10, 285, 110, 80))
        pygame.draw.rect(self.pantalla, BLANCO, (panel_x + 10, 285, 110, 80), 2)
        if pieza_hold:
            self.dibujar_pieza_mini(pieza_hold, panel_x + 25, 300)
        
        # Controles
        ctrls = ["←→ MOVER", "↓ RÁPIDO", "↑ ROTAR", "SPC DROP", "H HOLD", "ESC SALIR"]
        for i, ctrl in enumerate(ctrls):
            c_txt = self.fuente_peq.render(ctrl, True, BLANCO)
            self.pantalla.blit(c_txt, (panel_x + 10, 410 + i * 25))

        pygame.display.flip()

    def dibujar_pieza_mini(self, pieza, pos_x, pos_y):
        bloque_mini = 18 
        color = COLORES_PIEZAS[pieza['color_idx']]
        for i, fila in enumerate(pieza['forma']):
            for j, celda in enumerate(fila):
                if celda:
                    x = pos_x + j * bloque_mini
                    y = pos_y + i * bloque_mini
                    pygame.draw.rect(self.pantalla, color, (x, y, bloque_mini, bloque_mini))
                    pygame.draw.rect(self.pantalla, BLANCO, (x, y, bloque_mini, bloque_mini), 1)

    def dibujar_gameover(self, puntos):
        self.pantalla.fill(ROJO)
        msg = self.fuente_grande.render("GAME OVER", True, BLANCO)
        self.pantalla.blit(msg, ((500 - msg.get_width()) // 2, 250))
        
        pts = self.fuente_med.render(f"PUNTOS: {puntos}", True, AMARILLO)
        self.pantalla.blit(pts, ((500 - pts.get_width()) // 2, 350))
        
        info = self.fuente_peq.render("Presiona ENTER para volver al menú", True, BLANCO)
        self.pantalla.blit(info, ((500 - info.get_width()) // 2, 450))
        pygame.display.flip()