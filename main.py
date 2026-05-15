import pygame
import random
import sys
import json
import os
from collections import deque

# ==========================================
# 1. CONFIGURACIÓN Y CONSTANTES
# ==========================================
SCREEN_WIDTH, SCREEN_HEIGHT = 400, 600
BLOCK_SIZE = 30
GRID_WIDTH, GRID_HEIGHT = 10, 20
UI_WIDTH = 250

COLORS = [
    (20, 20, 20), (0, 240, 240), (240, 240, 0), (160, 0, 240),
    (0, 240, 0), (240, 0, 0), (0, 0, 240), (240, 160, 0)
]

# Definición geométrica de las 7 piezas
SHAPES = [
    [[]],  # Indexación base 1
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]]   # L
]

# --- RUTA PARA ALMACENAMIENTO PERSISTENTE ---
CARPETA_DATOS = "datos_guardados"
if not os.path.exists(CARPETA_DATOS):
    os.makedirs(CARPETA_DATOS)

RUTA_JUGADORES = os.path.join(CARPETA_DATOS, "jugadores.json")
RUTA_SCORES = os.path.join(CARPETA_DATOS, "scores.json")

# ==========================================
# 2. MODELO DE DATOS
# ==========================================
class Tetrimino:
    def __init__(self, x, y, shape_idx):
        self.x = x
        self.y = y
        self.type = shape_idx
        self.shape = SHAPES[self.type]
        self.color = COLORS[self.type]

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

class Board:
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.intervalo_caida = 600  
        self.tiempo_acumulado_velocidad = 0  

    def is_valid_move(self, piece, adj_x, adj_y, new_shape=None):
        shape = new_shape or piece.shape
        for r, row in enumerate(shape):
            for c, val in enumerate(row):
                if val:
                    nx, ny = piece.x + c + adj_x, piece.y + r + adj_y
                    if nx < 0 or nx >= GRID_WIDTH or ny >= GRID_HEIGHT or (ny >= 0 and self.grid[ny][nx]):
                        return False
        return True

    def lock_piece(self, piece):
        for r, row in enumerate(piece.shape):
            for c, val in enumerate(row):
                if val and piece.y + r >= 0:
                    self.grid[piece.y + r][piece.x + c] = piece.type
        return self.clear_lines()

    def clear_lines(self):
        new_grid = [row for row in self.grid if any(v == 0 for v in row)]
        lines = GRID_HEIGHT - len(new_grid)
        for _ in range(lines): new_grid.insert(0, [0 for _ in range(GRID_WIDTH)])
        self.grid = new_grid
        return lines

# ==========================================
# 3. MOTOR PRINCIPAL DEL JUEGO
# ==========================================
class TetrisGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH + UI_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris Pro - Persistent Edition")
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.SysFont("Consolas", 45, bold=True)
        self.font_ui = pygame.font.SysFont("Consolas", 22, bold=True)
        self.font_sm = pygame.font.SysFont("Consolas", 14, bold=True)
        
        self.state = "MENU"
        self.player_nick = ""
        self.usuarios = self.load_users()
        self.high_scores = self.load_scores()
        
        self.menu_options = ["JUGAR", "PRACTICA", "SALIR"]
        self.selected_idx = 0
        self.modo_practica_activo = False 
        
        self.bag = []
        self.auth_order = ["Alias", "Nombre", "Apellido", "Institucion"]
        self.categories = ["Junior", "Senior", "Profesor"]
        
        # Temporizadores internos para el movimiento continuo fluido manual
        self.tiempo_mov_lateral = 0
        self.tiempo_mov_abajo = 0
        
        self.limpiar_formulario()
        self.reset_game()

    def load_scores(self):
        if os.path.exists(RUTA_SCORES):
            with open(RUTA_SCORES, "r", encoding="utf-8") as f: return json.load(f)
        return {"Junior": {}, "Senior": {}, "Profesor": {}}

    def load_users(self):
        if os.path.exists(RUTA_JUGADORES):
            with open(RUTA_JUGADORES, "r", encoding="utf-8") as f: return json.load(f)
        return {}

    def save_score(self):
        if self.modo_practica_activo: return
        cat = self.usuarios.get(self.player_nick, {}).get("categoria", "Junior")
        if cat not in self.high_scores: self.high_scores[cat] = {}
        old_score = self.high_scores[cat].get(self.player_nick, 0)
        if self.score > old_score:
            self.high_scores[cat][self.player_nick] = self.score
            with open(RUTA_SCORES, "w", encoding="utf-8") as f: json.dump(self.high_scores, f, indent=4)

    def save_users(self):
        if self.modo_practica_activo: return
        with open(RUTA_JUGADORES, "w", encoding="utf-8") as f: json.dump(self.usuarios, f, indent=4)

    def limpiar_formulario(self):
        self.auth_fields = {"Alias": "", "Nombre": "", "Apellido": "", "Institucion": ""}
        self.active_field_idx = 0
        self.selected_cat_idx = 0
        self.login_alias = ""
        self.is_login_active = False
        self.auth_error = ""

    def get_random_piece_idx(self):
        if not self.bag:
            self.bag = list(range(1, len(SHAPES)))
            random.shuffle(self.bag)
        return self.bag.pop()

    def reset_game(self):
        self.board = Board()
        self.bag = []
        self.queue = deque([Tetrimino(3, 0, self.get_random_piece_idx()) for _ in range(4)])
        self.current_piece = self.queue.popleft()
        self.hold_piece = None
        self.can_hold = True
        self.score = 0
        self.game_over = False
        self.fall_time = 0
        self.tiempo_mov_lateral = 0
        self.tiempo_mov_abajo = 0

    def handle_hold(self):
        if not self.modo_practica_activo:
            user_info = self.usuarios.get(self.player_nick, {})
            if user_info.get("categoria", "").upper() != "JUNIOR": return
            
        if not self.can_hold: return
        if self.hold_piece is None:
            self.hold_piece = Tetrimino(3, 0, self.current_piece.type)
            self.current_piece = self.queue.popleft()
            self.queue.append(Tetrimino(3, 0, self.get_random_piece_idx()))
        else:
            temp_type = self.current_piece.type
            self.current_piece = Tetrimino(3, 0, self.hold_piece.type)
            self.hold_piece = Tetrimino(3, 0, temp_type)
        self.can_hold = False

    def draw_text_centered(self, text, y, font, color=(255, 255, 255)):
        surf = font.render(text, True, color)
        rect = surf.get_rect(center=((SCREEN_WIDTH + UI_WIDTH) // 2, y))
        self.screen.blit(surf, rect)

    def draw_menu(self):
        self.screen.fill((10, 10, 15))
        self.draw_text_centered("TETRIS", 100, self.font_title, (0, 255, 200))
        
        mouse_pos = pygame.mouse.get_pos()
        for i, opt in enumerate(self.menu_options):
            y = 250 + (i * 60)
            rect = pygame.Rect(0, 0, 200, 40)
            rect.center = ((SCREEN_WIDTH + UI_WIDTH) // 2, y)
            if rect.collidepoint(mouse_pos): self.selected_idx = i
            
            color = (0, 255, 100) if self.selected_idx == i else (150, 150, 150)
            self.draw_text_centered(opt, y, self.font_ui, color)
        pygame.display.flip()

    def draw_auth_screen(self):
        self.screen.fill((15, 15, 25))
        mid_x = (SCREEN_WIDTH + UI_WIDTH) // 2
        self.draw_text_centered("REGISTRO DE NUEVO JUGADOR", 40, self.font_ui, (0, 255, 200))
        
        y_offset = 90
        self.rects_campos = {}
        for i, f_name in enumerate(self.auth_order):
            lbl = self.font_sm.render(f"{f_name}:", True, (180, 180, 180))
            self.screen.blit(lbl, (mid_x - 220, y_offset + 5))
            
            box_rect = pygame.Rect(mid_x - 80, y_offset, 280, 30)
            self.rects_campos[f_name] = box_rect
            
            is_active = (self.active_field_idx == i and not self.is_login_active)
            b_color = (0, 255, 100) if is_active else (80, 80, 80)
            pygame.draw.rect(self.screen, b_color, box_rect, 2)
            
            val_txt = self.font_sm.render(self.auth_fields[f_name], True, (255, 255, 255))
            self.screen.blit(val_txt, (mid_x - 73, y_offset + 5))
            y_offset += 45
            
        lbl_cat = self.font_sm.render("Categoría:", True, (180, 180, 180))
        self.screen.blit(lbl_cat, (mid_x - 220, y_offset + 5))
        
        self.rects_categorias = []
        for i, cat in enumerate(self.categories):
            cat_rect = pygame.Rect(mid_x - 80 + (i * 95), y_offset, 85, 30)
            self.rects_categorias.append((i, cat_rect))
            bg_color = (0, 120, 200) if self.selected_cat_idx == i else (40, 40, 50)
            pygame.draw.rect(self.screen, bg_color, cat_rect)
            pygame.draw.rect(self.screen, (100, 100, 100), cat_rect, 1)
            
            cat_txt = self.font_sm.render(cat, True, (255, 255, 255))
            c_rect = cat_txt.get_rect(center=cat_rect.center)
            self.screen.blit(cat_txt, c_rect)
            
        y_offset += 50
        self.btn_registrar = pygame.Rect(mid_x - 150, y_offset, 300, 35)
        pygame.draw.rect(self.screen, (0, 120, 240), self.btn_registrar)
        self.draw_text_centered("REGISTRAR Y EMPEZAR", y_offset + 17, self.font_sm, (255, 255, 255))
        
        y_offset += 65
        pygame.draw.line(self.screen, (60, 60, 70), (40, y_offset), (SCREEN_WIDTH + UI_WIDTH - 40, y_offset), 2)
        y_offset += 25
        self.draw_text_centered("INICIAR SESIÓN", y_offset, self.font_ui, (0, 255, 200))
        
        y_offset += 40
        lbl_log = self.font_sm.render("Tu Alias:", True, (180, 180, 180))
        self.screen.blit(lbl_log, (mid_x - 220, y_offset + 5))
        
        self.box_login_rect = pygame.Rect(mid_x - 80, y_offset, 280, 30)
        b_color_log = (0, 255, 100) if self.is_login_active else (80, 80, 80)
        pygame.draw.rect(self.screen, b_color_log, self.box_login_rect, 2)
        
        log_txt = self.font_sm.render(self.login_alias, True, (255, 255, 255))
        self.screen.blit(log_txt, (mid_x - 73, y_offset + 5))
        
        y_offset += 50
        self.btn_login = pygame.Rect(mid_x - 150, y_offset, 300, 35)
        pygame.draw.rect(self.screen, (0, 150, 70), self.btn_login)
        self.draw_text_centered("INICIAR Y JUGAR", y_offset + 17, self.font_sm, (255, 255, 255))
        
        if self.auth_error: self.draw_text_centered(self.auth_error, 565, self.font_sm, (255, 50, 50))
        pygame.display.flip()

    def draw_game(self):
        self.screen.fill((15, 15, 20))
        for y, row in enumerate(self.board.grid):
            for x, val in enumerate(row):
                rect = (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE-1, BLOCK_SIZE-1)
                pygame.draw.rect(self.screen, COLORS[val] if val else (30, 30, 35), rect, 0 if val else 1)

        if not self.game_over:
            for r, row in enumerate(self.current_piece.shape):
                for c, val in enumerate(row):
                    if val: pygame.draw.rect(self.screen, self.current_piece.color, ((self.current_piece.x+c)*BLOCK_SIZE, (self.current_piece.y+r)*BLOCK_SIZE, BLOCK_SIZE-1, BLOCK_SIZE-1))
        
        ux = SCREEN_WIDTH + 20
        pygame.draw.rect(self.screen, (40, 40, 50), (SCREEN_WIDTH, 0, UI_WIDTH, SCREEN_HEIGHT))
        
        if self.modo_practica_activo:
            nick_display = "INVITADO"
            categoria_txt = "PRACTICA"
            nombre_real, apellido_real = "MODO", "PRACTICA"
            ver_hold = True 
        else:
            user_info = self.usuarios.get(self.player_nick, {})
            nick_display = self.player_nick
            categoria_txt = user_info.get("categoria", "N/A").upper()
            nombre_real = user_info.get("nombre", "N/A")
            apellido_real = user_info.get("apellido", "N/A")
            ver_hold = (categoria_txt == "JUNIOR")
        
        self.screen.blit(self.font_ui.render(f"PLAYER: {nick_display}", True, (255, 255, 255)), (ux, 30))
        self.screen.blit(self.font_sm.render(f"RANK: {categoria_txt}", True, (255, 255, 0)), (ux, 65))
        self.screen.blit(self.font_ui.render(f"SCORE: {self.score}", True, (0, 255, 100)), (ux, 100))
        
        if ver_hold:
            self.screen.blit(self.font_ui.render("HOLD (C):", True, (150, 150, 150)), (ux, 160))
            if self.hold_piece:
                for r, row in enumerate(self.hold_piece.shape):
                    for c, val in enumerate(row):
                        if val: pygame.draw.rect(self.screen, self.hold_piece.color, (ux + c*20, 200 + r*20, 18, 18))
            y_next_label, y_next_pieces = 310, 350
        else:
            y_next_label, y_next_pieces = 160, 200

        self.screen.blit(self.font_ui.render("SIGUIENTES:", True, (150, 150, 150)), (ux, y_next_label))
        for i, p in enumerate(list(self.queue)[:3]):
            for r, row in enumerate(p.shape):
                for c, val in enumerate(row):
                    if val: pygame.draw.rect(self.screen, p.color, (ux + c*20, y_next_pieces + i*70 + r*20, 18, 18))

        y_user_panel = SCREEN_HEIGHT - 45
        pygame.draw.line(self.screen, (100, 100, 100), (SCREEN_WIDTH + 15, y_user_panel), (SCREEN_WIDTH + UI_WIDTH - 15, y_user_panel), 1)
        nombre_completo_txt = f"USER: {nombre_real} {apellido_real}"
        self.screen.blit(self.font_sm.render(nombre_completo_txt, True, (200, 200, 200)), (ux, y_user_panel + 12))

        if self.game_over: self.draw_text_centered("GAME OVER - M: MENU", SCREEN_HEIGHT//2, self.font_ui, (255, 50, 50))
        pygame.display.flip()

    def process_registration(self):
        alias = self.auth_fields["Alias"].strip()
        nombre = self.auth_fields["Nombre"].strip()
        apellido = self.auth_fields["Apellido"].strip()
        inst = self.auth_fields["Institucion"].strip()
        cat = self.categories[self.selected_cat_idx]
        
        if not all([alias, nombre, apellido, inst]):
            self.auth_error = "Todos los campos son obligatorios."
            return
        if alias in self.usuarios:
            self.auth_error = "El alias ya existe. Usa Inicio de Sesion."
            return
            
        self.usuarios[alias] = {"nombre": nombre, "apellido": apellido, "institucion": inst, "categoria": cat}
        self.save_users()
        self.player_nick = alias
        self.modo_practica_activo = False
        self.reset_game()
        self.state = "GAME"
        self.auth_error = ""

    def process_login(self):
        alias = self.login_alias.strip()
        if not alias:
            self.auth_error = "Ingresa un alias para iniciar."
            return
        if alias in self.usuarios:
            self.player_nick = alias
            self.modo_practica_activo = False
            self.reset_game()
            self.state = "GAME"
            self.auth_error = ""
        else:
            self.auth_error = "El alias no esta registrado."

    def manejar_entradas_juego(self, dt):
        """Maneja el movimiento fluido continuo consultando el estado del teclado."""
        keys = pygame.key.get_pressed()
        self.tiempo_mov_lateral += dt
        self.tiempo_mov_abajo += dt

        # Movimiento hacia la izquierda continuo (cada 50 ms tras pulsación inicial)
        if keys[pygame.K_LEFT]:
            if self.tiempo_mov_lateral > 50:
                if self.board.is_valid_move(self.current_piece, -1, 0): self.current_piece.x -= 1
                self.tiempo_mov_lateral = 0
        # Movimiento hacia la derecha continuo
        elif keys[pygame.K_RIGHT]:
            if self.tiempo_mov_lateral > 50:
                if self.board.is_valid_move(self.current_piece, 1, 0): self.current_piece.x += 1
                self.tiempo_mov_lateral = 0
        else:
            # Si no se presionan flechas laterales, permite un toque instantáneo al hacer clic de nuevo
            self.tiempo_mov_lateral = 60

        # Caída suave manual acelerada continua (cada 30 ms)
        if keys[pygame.K_DOWN]:
            if self.tiempo_mov_abajo > 30:
                if self.board.is_valid_move(self.current_piece, 0, 1): self.current_piece.y += 1
                self.tiempo_mov_abajo = 0
        else:
            self.tiempo_mov_abajo = 40

    def run(self):
        while True:
            dt = self.clock.get_rawtime()
            self.clock.tick()
            
            if self.state == "MENU":
                self.draw_menu()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP: self.selected_idx = (self.selected_idx - 1) % 3
                        if event.key == pygame.K_DOWN: self.selected_idx = (self.selected_idx + 1) % 3
                        if event.key == pygame.K_RETURN:
                            if self.selected_idx == 0: 
                                self.limpiar_formulario()
                                self.state = "AUTH_MENU"
                            elif self.selected_idx == 1:
                                self.modo_practica_activo = True
                                self.reset_game()
                                self.state = "GAME"
                            else: 
                                pygame.quit(); sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.selected_idx == 0: self.limpiar_formulario(); self.state = "AUTH_MENU"
                        elif self.selected_idx == 1:
                            self.modo_practica_activo = True
                            self.reset_game()
                            self.state = "GAME"
                        else: pygame.quit(); sys.exit()

            elif self.state == "AUTH_MENU":
                self.draw_auth_screen()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        m_pos = pygame.mouse.get_pos()
                        for idx, f_name in enumerate(self.auth_order):
                            if self.rects_campos[f_name].collidepoint(m_pos): self.active_field_idx = idx; self.is_login_active = False
                        for idx, rcat in self.rects_categorias:
                            if rcat.collidepoint(m_pos): self.selected_cat_idx = idx
                        if self.box_login_rect.collidepoint(m_pos): self.is_login_active = True
                        if self.btn_registrar.collidepoint(m_pos): self.process_registration()
                        if self.btn_login.collidepoint(m_pos): self.process_login()
                            
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE: self.state = "MENU"
                        elif event.key == pygame.K_UP:
                            if self.is_login_active: self.is_login_active = False; self.active_field_idx = len(self.auth_order) - 1
                            elif self.active_field_idx > 0: self.active_field_idx -= 1
                        elif event.key == pygame.K_DOWN:
                            if not self.is_login_active:
                                if self.active_field_idx < len(self.auth_order) - 1: self.active_field_idx += 1
                                else: self.is_login_active = True
                        elif event.key == pygame.K_TAB:
                            if not self.is_login_active: self.active_field_idx = (self.active_field_idx + 1) % len(self.auth_order)
                        elif event.key == pygame.K_BACKSPACE:
                            if self.is_login_active: self.login_alias = self.login_alias[:-1]
                            else: self.auth_fields[self.auth_order[self.active_field_idx]] = self.auth_fields[self.auth_order[self.active_field_idx]][:-1]
                        elif event.key == pygame.K_RETURN:
                            if self.is_login_active: self.process_login()
                            else:
                                if self.active_field_idx < len(self.auth_order) - 1: self.active_field_idx += 1
                                else: self.process_registration()
                        else:
                            char = event.unicode
                            if char:
                                if self.is_login_active:
                                    if char != " " and len(self.login_alias) < 25: self.login_alias += char
                                else:
                                    active_fn = self.auth_order[self.active_field_idx]
                                    if active_fn == "Alias" and char != " " and len(self.auth_fields[active_fn]) < 25: self.auth_fields[active_fn] += char
                                    elif active_fn in ["Nombre", "Apellido"] and (char.isalpha() or char == " ") and len(self.auth_fields[active_fn]) < 25: self.auth_fields[active_fn] += char
                                    elif active_fn == "Institucion" and (char.isalpha() or char == " ") and len(self.auth_fields[active_fn]) < 25: self.auth_fields[active_fn] += char

            elif self.state == "GAME":
                if not self.game_over:
                    # Aplicar la función de escaneo continuo de las flechas (Laterales y Abajo)
                    self.manejar_entradas_juego(dt)
                    
                    self.fall_time += dt
                    self.board.tiempo_acumulado_velocidad += dt
                    if self.board.tiempo_acumulado_velocidad >= 30000:  
                        self.board.intervalo_caida = max(80, self.board.intervalo_caida - 35)  
                        self.board.tiempo_acumulado_velocidad = 0  
                    
                    if self.fall_time > self.board.intervalo_caida:
                        if self.board.is_valid_move(self.current_piece, 0, 1): self.current_piece.y += 1
                        else:
                            lines = self.board.lock_piece(self.current_piece)
                            score_map = {0: 0, 1: 100, 2: 300, 3: 500, 4: 800}
                            self.score += score_map[lines] if lines < len(score_map) else 1210
                            
                            nueva_pieza_temp = self.queue.popleft()
                            if not self.board.is_valid_move(nueva_pieza_temp, 0, 0): 
                                self.game_over = True
                                self.save_score() 
                            else: 
                                self.current_piece = nueva_pieza_temp
                                self.queue.append(Tetrimino(3, 0, self.get_random_piece_idx()))
                                self.can_hold = True
                        self.fall_time = 0

                for event in pygame.event.get():
                    if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if self.game_over and event.key == pygame.K_m: self.state = "MENU"
                        if not self.game_over:
                            # MODIFICADO: Rotación confinada ESTRICTAMENTE al evento discreto KEYDOWN (no se puede mantener presionada)
                            if event.key == pygame.K_UP:
                                old = self.current_piece.shape; self.current_piece.rotate()
                                if not self.board.is_valid_move(self.current_piece, 0, 0): self.current_piece.shape = old
                            # Caída instantánea dura (Espacio) e intercambio (C) se mantienen por pulsaciones individuales
                            if event.key == pygame.K_SPACE:
                                drop = 0
                                while self.board.is_valid_move(self.current_piece, 0, 1): self.current_piece.y += 1; drop += 1
                                self.score += (drop * 2)
                            if event.key == pygame.K_c: self.handle_hold()
                self.draw_game()

if __name__ == "__main__":
    game = TetrisGame()
    game.run()
