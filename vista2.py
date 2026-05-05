import pygame

# Colores
NEGRO = (0, 0, 0)
BLANCO = (255, 255, 255)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AMARILLO = (255, 255, 0)
GRIS = (50, 50, 50)
AZUL = (0, 100, 200)
COLORES_PIEZAS = [
    (0, 255, 255), (255, 255, 0), (128, 0, 128),
    (0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 165, 0)
]

class VistaTetris:
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((500, 800))
        pygame.display.set_caption("TETRIS")
        self.reloj = pygame.time.Clock()
        self.bloque_size = 25
        
        # Fuentes (Aseguradas para coincidir con el resto del código)
        self.fuente_grande = pygame.font.Font(None, 72)
        self.fuente = pygame.font.Font(None, 48)
        self.fuente_med = pygame.font.Font(None, 36)
        self.fuente_peq = pygame.font.Font(None, 24)
    
    def dibujar_menu(self, highscores, seleccion=0):
        self.pantalla.fill(AZUL)
        
        # Título
        titulo = self.fuente_grande.render("TETRIS", True, BLANCO)
        self.pantalla.blit(titulo, ((500 - titulo.get_width()) // 2, 80))
        
        # TOP 3
        if highscores:
            top_txt = self.fuente_med.render("🏆 TOP 3", True, AMARILLO)
            self.pantalla.blit(top_txt, (200, 170))
            pygame.draw.rect(self.pantalla, GRIS, (120, 200, 260, 120))
            pygame.draw.rect(self.pantalla, BLANCO, (120, 200, 260, 120), 3)
            for i in range(min(3, len(highscores))):
                score = highscores[i]
                color_texto = AMARILLO if i == 0 else BLANCO
                linea = f"{i+1}. {score['nombre']:<8} {score['puntos']}"
                txt = self.fuente_peq.render(linea, True, color_texto)
                self.pantalla.blit(txt, (130, 220 + i * 35))
        
        # Opciones
        opciones = [
            ("1 ▶️ JUGAR", VERDE, 380),
            ("2 📊 HIGHSCORES", AMARILLO, 460),
            ("3 ❌ SALIR", ROJO, 540)
        ]
        
        for i, (texto, color_base, y) in enumerate(opciones):
            # 🆕 Si esta es la opción seleccionada, usamos su color original y borde más grueso
            # Si no, la ponemos gris para que se vea "apagada"
            color_fondo = color_base if i == seleccion else GRIS
            grosor_borde = 6 if i == seleccion else 2
            color_texto = BLANCO if i == seleccion else (200, 200, 200) # Texto un poco más opaco si no está seleccionado
            
            surf = self.fuente_med.render(texto, True, color_texto)
            rect = surf.get_rect(center=(250, y))
            
            pygame.draw.rect(self.pantalla, color_fondo, rect.inflate(140, 60))
            pygame.draw.rect(self.pantalla, BLANCO, rect.inflate(140, 60), grosor_borde)
            self.pantalla.blit(surf, rect)
        
        instruc = self.fuente_peq.render("↑↓ Seleccionar | ⏎ Enter | 1,2,3 Atajos", True, BLANCO)
        self.pantalla.blit(instruc, (80, 650))
        pygame.display.flip()
    
    def dibujar_highscores(self, highscores):
        self.pantalla.fill(NEGRO)
        titulo = self.fuente.render("🏆 HIGHSCORES", True, AMARILLO)
        self.pantalla.blit(titulo, (150, 100))
        
        pygame.draw.rect(self.pantalla, GRIS, (100, 200, 300, 400))
        pygame.draw.rect(self.pantalla, BLANCO, (100, 200, 300, 400), 3)
        
        headers = ["#", "NOMBRE", "PUNTOS"]
        for i, h in enumerate(headers):
            txt = self.fuente_peq.render(h, True, BLANCO)
            self.pantalla.blit(txt, (120 + i * 100, 220))
        
        y = 260
        for i, score in enumerate(highscores[:10]):
            color = AMARILLO if i == 0 else BLANCO
            linea = f"{i+1:2d}  {score['nombre']:<8} {score['puntos']:5d}"
            txt = self.fuente_peq.render(linea, True, color)
            self.pantalla.blit(txt, (110, y))
            y += 35
        
        volver = self.fuente_med.render("ESC 🏠 VOLVER", True, BLANCO)
        vrect = volver.get_rect(center=(250, 650))
        pygame.draw.rect(self.pantalla, VERDE, vrect.inflate(100, 50))
        pygame.draw.rect(self.pantalla, BLANCO, vrect.inflate(100, 50), 3)
        self.pantalla.blit(volver, vrect)
        pygame.display.flip()
    
    def dibujar_gameover(self, puntos, seleccion):
        overlay = pygame.Surface((500, 800))
        overlay.set_alpha(200)
        overlay.fill(ROJO)
        self.pantalla.blit(overlay, (0, 0))
        
        titulo = self.fuente_grande.render("GAME OVER", True, BLANCO)
        self.pantalla.blit(titulo, ((500 - titulo.get_width()) // 2, 200))
        
        puntos_txt = self.fuente.render(f"PUNTOS: {puntos}", True, AMARILLO)
        self.pantalla.blit(puntos_txt, (180, 320))
        
        opciones = ["1 ✍️ GUARDAR NOMBRE", "2 🏠 MENÚ PRINCIPAL"]
        for i, texto in enumerate(opciones):
            color = VERDE if i == seleccion else AZUL
            surf = self.fuente_med.render(texto, True, BLANCO)
            rect = surf.get_rect(center=(250, 450 + i * 90))
            pygame.draw.rect(self.pantalla, color, rect.inflate(180, 60))
            pygame.draw.rect(self.pantalla, BLANCO, rect.inflate(180, 60), 3)
            self.pantalla.blit(surf, rect)
        pygame.display.flip()
    
    def dibujar_gameover_input(self, puntos, nombre):
        overlay = pygame.Surface((500, 800))
        overlay.set_alpha(200)
        overlay.fill(ROJO)
        self.pantalla.blit(overlay, (0, 0))
        
        titulo = self.fuente_grande.render("¡NUEVO RECORD!", True, AMARILLO)
        self.pantalla.blit(titulo, ((500 - titulo.get_width()) // 2, 150))
        
        puntos_txt = self.fuente.render(f"{puntos} PUNTOS", True, BLANCO)
        self.pantalla.blit(puntos_txt, (180, 250))
        
        pygame.draw.rect(self.pantalla, NEGRO, (150, 350, 200, 80))
        pygame.draw.rect(self.pantalla, BLANCO, (150, 350, 200, 80), 4)
        
        nombre_txt = self.fuente_med.render(nombre, True, VERDE)
        self.pantalla.blit(nombre_txt, (170, 370))
        
        instruc = self.fuente_peq.render("TECLEA TU NOMBRE | ENTER", True, BLANCO)
        self.pantalla.blit(instruc, (130, 460))
        
        guardar_btn = self.fuente_med.render("💾 GUARDAR", True, BLANCO)
        grect = guardar_btn.get_rect(center=(250, 580))
        pygame.draw.rect(self.pantalla, VERDE, grect.inflate(120, 60))
        pygame.draw.rect(self.pantalla, BLANCO, grect.inflate(120, 60), 3)
        self.pantalla.blit(guardar_btn, grect)
        pygame.display.flip()
    
    def dibujar_tablero(self, tablero, pieza, x, y, puntos):
        self.pantalla.fill(NEGRO)
        
        # Tablero
        self.dibujar_matriz(tablero, 75, 75)
        self.dibujar_pieza(pieza, x, y, 75, 75)
        
        # Panel lateral
        pygame.draw.rect(self.pantalla, GRIS, (350, 75, 120, 500))
        pygame.draw.rect(self.pantalla, BLANCO, (350, 75, 120, 500), 3)
        
        p_txt = self.fuente_med.render(f"{puntos}", True, AMARILLO)
        self.pantalla.blit(p_txt, (370, 100))
        p_label = self.fuente_peq.render("PUNTOS", True, BLANCO)
        self.pantalla.blit(p_label, (365, 130))
        
        ctrls = ["← → MOVER", "↓ RÁPIDO", "↑ ROTAR", "SPACE DROP", "ESC PAUSA"]
        for i, ctrl in enumerate(ctrls):
            c_txt = self.fuente_peq.render(ctrl, True, BLANCO)
            self.pantalla.blit(c_txt, (360, 200 + i * 30))
        
        pygame.display.flip()
    
    def dibujar_matriz(self, matriz, pos_x, pos_y):
        for i in range(20):
            for j in range(10):
                if matriz[i][j]:
                    color = COLORES_PIEZAS[(i + j) % 7]
                    self.dibujar_bloque(color, j, i, pos_x, pos_y)
    
    def dibujar_pieza(self, pieza, px, py, pos_x, pos_y):
        for i, fila in enumerate(pieza['forma']):
            for j, celda in enumerate(fila):
                if celda:
                    color = COLORES_PIEZAS[i % 7]
                    self.dibujar_bloque(color, px + j, py + i, pos_x, pos_y)
    
    def dibujar_bloque(self, color, col, row, pos_x, pos_y):
        x = pos_x + col * self.bloque_size
        y = pos_y + row * self.bloque_size
        pygame.draw.rect(self.pantalla, color, (x, y, self.bloque_size, self.bloque_size))
        pygame.draw.rect(self.pantalla, BLANCO, (x, y, self.bloque_size, self.bloque_size), 1)