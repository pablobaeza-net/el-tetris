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

    def dibujar_registro(self, datos, campo_actual, es_competitivo=False):
        self.pantalla.fill(NEGRO)
        
        # TÍTULO ESPECIAL PARA COMPETITIVO
        if es_competitivo:
            titulo = self.fuente_titulos.render("🏆 MODO COMPETITIVO", True, AMARILLO)
            advertencia = self.fuente_med.render("⚠️ TODOS LOS CAMPOS OBLIGATORIOS ⚠️", True, ROJO)
        else:
            titulo = self.fuente_titulos.render("DATOS JUGADOR", True, AMARILLO)
            advertencia = self.fuente_med.render("Solo alias obligatorio", True, VERDE)
            
        self.pantalla.blit(titulo, ((500 - titulo.get_width()) // 2, 30))
        self.pantalla.blit(advertencia, ((500 - advertencia.get_width()) // 2, 80))
        
        campos_nombres = ["alias", "nombre_real", "institucion", "edad"]
        etiquetas = ["Alias:", "Nombre Real:", "Institución:", "Edad (5-100):"]
        
        y_base = 130
        for i, campo in enumerate(campos_nombres):
            # Resaltar campos vacíos en modo competitivo
            color_etiqueta = ROJO if es_competitivo and datos[campo].strip() == "" else BLANCO
            lbl = self.fuente_med.render(etiquetas[i], True, color_etiqueta)
            self.pantalla.blit(lbl, (50, y_base + (i * 100)))
            
            # Color de caja según estado
            if es_competitivo and datos[campo].strip() == "":
                color_caja = ROJO  # Campo vacío
            elif i == campo_actual:
                color_caja = VERDE  # Activo
            else:
                color_caja = GRIS  # Normal
                
            pygame.draw.rect(self.pantalla, color_caja, (50, y_base + 35 + (i * 100), 400, 40), 3)
            
            color_texto = BLANCO if i == campo_actual else (150, 150, 150)
            txt = self.fuente_med.render(datos[campo] + ("_" if i == campo_actual else ""), True, color_texto)
            self.pantalla.blit(txt, (60, y_base + 40 + (i * 100)))

        # MOSTRAR SI FALTA ALGO PARA JUGAR
        if es_competitivo:
            campos_validos = all(datos[campo].strip() != "" for campo in campos_nombres)
            try:
                edad = int(datos["edad"])
                edad_valida = 5 <= edad <= 100
            except:
                edad_valida = False
            
            if not campos_validos or not edad_valida:
                error_msg = self.fuente_med.render("❌ FALTAN DATOS VÁLIDOS", True, ROJO)
                self.pantalla.blit(error_msg, ((500 - error_msg.get_width()) // 2, 620))
            else:
                listo_msg = self.fuente_med.render("✅ ¡LISTO! Presiona ENTER", True, VERDE)
                self.pantalla.blit(listo_msg, ((500 - listo_msg.get_width()) // 2, 620))
        else:
            listo_msg = self.fuente_med.render("✅ Presiona ENTER para jugar", True, VERDE)
            self.pantalla.blit(listo_msg, ((500 - listo_msg.get_width()) // 2, 620))

        instruc = self.fuente_peq.render("↓↑ Moverse | ⏎ Enter para jugar | ESC Volver", True, BLANCO)
        self.pantalla.blit(instruc, ((500 - instruc.get_width()) // 2, 680))
        pygame.display.flip()

    def dibujar_tablero(self, tablero, pieza, x, y, puntos, siguiente_pieza, pieza_hold, top_puntajes, modo_juego):
        self.pantalla.fill(NEGRO)
        
        # MOSTRAR MODO EN TABLERO
        if modo_juego == "competitivo":
            modo_txt = self.fuente_peq.render("🏆 COMPETITIVO", True, AMARILLO)
        else:
            modo_txt = self.fuente_peq.render("🎯 ENTRENAMIENTO", True, VERDE)
        self.pantalla.blit(modo_txt, (10, 10))
        
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
        h_label = self.fuente_peq.render("HOLD (C)", True, VERDE)
        self.pantalla.blit(h_label, (panel_x + 15, 260))
        pygame.draw.rect(self.pantalla, NEGRO, (panel_x + 10, 285, 110, 80))
        pygame.draw.rect(self.pantalla, BLANCO, (panel_x + 10, 285, 110, 80), 2)
        if pieza_hold:
            self.dibujar_pieza_mini(pieza_hold, panel_x + 25, 300)
        
        # Controles
        ctrls = ["←→ MOVER", "↓ RÁPIDO", "↑ ROTAR", "SPC DROP", "C HOLD", "ESC SALIR"]
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

    def dibujar_gameover(self, puntos, modo_juego):
        self.pantalla.fill(ROJO)
        msg = self.fuente_grande.render("GAME OVER", True, BLANCO)
        self.pantalla.blit(msg, ((500 - msg.get_width()) // 2, 250))
        
        # MOSTRAR MODO Y PUNTOS
        if modo_juego == "competitivo":
            modo_txt = self.fuente_med.render("🏆 COMPETITIVO", True, AMARILLO)
        else:
            modo_txt = self.fuente_med.render("🎯 ENTRENAMIENTO", True, VERDE)
        self.pantalla.blit(modo_txt, ((500 - modo_txt.get_width()) // 2, 340))
        
        pts = self.fuente_med.render(f"PUNTOS: {puntos}", True, BLANCO)
        self.pantalla.blit(pts, ((500 - pts.get_width()) // 2, 390))
        
        info = self.fuente_peq.render("Presiona ENTER para volver al menú", True, BLANCO)
        self.pantalla.blit(info, ((500 - info.get_width()) // 2, 450))
        pygame.display.flip()