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

# CORREGIDO: Estructura sintáctica válida para las 7 piezas del juego
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
        self.font_sm = pygame.font.SysFont("Consolas", 16, bold=True)
        
        self.state = "MENU"
        self.player_nick = ""
        self.usuarios = self.load_users()
        self.high_scores = self.load_scores()
        self.menu_options = ["JUGAR", "PUNTAJES", "SALIR"]
        self.selected_idx = 0
        
        self.bag = []
        
        self.auth_order = ["Alias", "Nombre", "Apellido", "Institucion"]
        self.categories = ["Junior", "Senior", "Profesor"]
        self.scores_category_idx = 0
        self.limpiar_formulario()
        self.reset_game()

    def load_scores(self):
        if os.path.exists("scores.json"):
            with open("scores.json", "r", encoding="utf-8") as f:
                return json.load(f)
        return {"Junior": {}, "Senior": {}, "Profesor": {}}

    def load_users(self):
        if os.path.exists("jugadores.json"):
            with open("jugadores.json", "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def save_score(self):
        cat = self.usuarios.get(self.player_nick, {}).get("categoria", "Junior")
        if cat not in self.high_scores:
            self.high_scores[cat] = {}
            
        old_score = self.high_scores[cat].get(self.player_nick, 0)
        if self.score > old_score:
            self.high_scores[cat][self.player_nick] = self.score
            with open("scores.json", "w", encoding="utf-8") as f:
                json.dump(self.high_scores, f, indent=4)

    def save_users(self):
        with open("jugadores.json", "w", encoding="utf-8") as f:
            json.dump(self.usuarios, f, indent=4)

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

    def handle_hold(self):
        user_info = self.usuarios.get(self.player_nick, {})
        if user_info.get("categoria", "").upper() != "JUNIOR":
            return

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
        
        if self.auth_error:
            self.draw_text_centered(self.auth_error, 565, self.font_sm, (255, 50, 50))
            
        pygame.display.flip()

    def draw_scores(self):
        self.screen.fill((10, 10, 20))
        self.draw_text_centered("TOP PUNTAJES", 40, self.font_title, (255, 215, 0))
        
        cat_actual = self.categories[self.scores_category_idx]
        texto_selector = f"<  {cat_actual.upper()}  >"
        self.draw_text_centered(texto_selector, 105, self.font_ui, (0, 255, 200))
        self.draw_text_centered("Usa Flechas [Izquierda / Derecha] para cambiar", 135, self.font_sm, (120, 120, 120))
        
        cat_scores = self.high_scores.get(cat_actual, {})
        
        scores_filtrados = {}
        for nick, pto in cat_scores.items():
            if nick in self.usuarios and self.usuarios[nick].get("categoria") == cat_actual:
                scores_filtrados[nick] = pto

        sorted_scores = sorted(scores_filtrados.items(), key=lambda x: x[1], reverse=True)[:10]
        
        y_pos = 190
        for i in range(10):
            if i < len(sorted_scores):
                nick, score = sorted_scores[i]
                txt = f"{i+1:2d}. {nick[:12]:<12} - {score:,} pts"
                color_linea = (255, 255, 255) if i > 0 else (255, 215, 0)
            else:
                txt = f"{i+1:2d}. ----         - 0 pts"
                color_linea = (80, 80, 90)
                
            self.draw_text_centered(txt, y_pos, self.font_ui, color_linea)
            y_pos += 33

        self.draw_text_centered("ESC para volver al menú", 550, self.font_sm, (100, 100, 100))
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
                    if val:
                        pygame.draw.rect(self.screen, self.current_piece.color, 
                                         ((self.current_piece.x+c)*BLOCK_SIZE, (self.current_piece.y+r)*BLOCK_SIZE, BLOCK_SIZE-1, BLOCK_SIZE-1))
        
        ux = SCREEN_WIDTH + 20
        pygame.draw.rect(self.screen, (40, 40, 50), (SCREEN_WIDTH, 0, UI_WIDTH, SCREEN_HEIGHT))
        
        user_info = self.usuarios.get(self.player_nick, {})
        categoria_txt = user_info.get("categoria", "N/A").upper()
        nombre_real = user_info.get("nombre", "N/A")
        apellido_real = user_info.get("apellido", "N/A")

        self.screen.blit(self.font_ui.render(f"PLAYER: {self.player_nick}", True, (255, 255, 255)), (ux, 30))
        self.screen.blit(self.font_sm.render(f"RANK: {categoria_txt}", True, (255, 255, 0)), (ux, 65))
        self.screen.blit(self.font_ui.render(f"SCORE: {self.score}", True, (0, 255, 100)), (ux, 100))
        
        if categoria_txt == "JUNIOR":
            self.screen.blit(self.font_ui.render("HOLD (C):", True, (150, 150, 150)), (ux, 160))
            if self.hold_piece:
                for r, row in enumerate(self.hold_piece.shape):
                    for c, val in enumerate(row):
                        if val: pygame.draw.rect(self.screen, self.hold_piece.color, (ux + c*20, 200 + r*20, 18, 18))
            y_next_label = 310
            y_next_pieces = 350
        else:
            y_next_label = 160
            y_next_pieces = 200

        self.screen.blit(self.font_ui.render("SIGUIENTES:", True, (150, 150, 150)), (ux, y_next_label))
        for i, p in enumerate(list(self.queue)[:3]):
            for r, row in enumerate(p.shape):
                for c, val in enumerate(row):
                    if val: pygame.draw.rect(self.screen, p.color, (ux + c*20, y_next_pieces + i*70 + r*20, 18, 18))

        y_user_panel = SCREEN_HEIGHT - 45
        pygame.draw.line(self.screen, (100, 100, 100), (SCREEN_WIDTH + 15, y_user_panel), (SCREEN_WIDTH + UI_WIDTH - 15, y_user_panel), 1)
        
        nombre_completo_txt = f"USER: {nombre_real} {apellido_real}"
        self.screen.blit(self.font_sm.render(nombre_completo_txt, True, (200, 200, 200)), (ux, y_user_panel + 12))

        if self.game_over:
            self.draw_text_centered("GAME OVER - M: MENU", SCREEN_HEIGHT//2, self.font_ui, (255, 50, 50))

        pygame.display.flip()

    def process_registration(self):
        alias = self.auth_fields["Alias"].strip().upper()
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
        self.reset_game()
        self.state = "GAME"
        self.auth_error = ""

    def process_login(self):
        alias = self.login_alias.strip().upper()
        if not alias:
            self.auth_error = "Ingresa un alias para iniciar."
            return
            
        if alias in self.usuarios:
            self.player_nick = alias
            self.reset_game()
            self.state = "GAME"
            self.auth_error = ""
        else:
            self.auth_error = "El alias no esta registrado."

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
                                self.high_scores = self.load_scores()
                                self.scores_category_idx = 0
                                self.state = "SCORES"
                            else: pygame.quit(); sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.selected_idx == 0: 
                            self.limpiar_formulario()
                            self.state = "AUTH_MENU"
                        elif self.selected_idx == 1: 
                            self.high_scores = self.load_scores()
                            self.scores_category_idx = 0
                            self.state = "SCORES"
                        else: pygame.quit(); sys.exit()

            elif self.state == "AUTH_MENU":
                self.draw_auth_screen()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        m_pos = pygame.mouse.get_pos()
                        
                        for idx, f_name in enumerate(self.auth_order):
                            if self.rects_campos[f_name].collidepoint(m_pos):
                                self.active_field_idx = idx
                                self.is_login_active = False
                                
                        for idx, rcat in self.rects_categorias:
                            if rcat.collidepoint(m_pos):
                                self.selected_cat_idx = idx
                                
                        if self.box_login_rect.collidepoint(m_pos):
                            self.is_login_active = True
                            
                        if self.btn_registrar.collidepoint(m_pos):
                            self.process_registration()
                        elif self.btn_login.collidepoint(m_pos):
                            self.process_login()
                            
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.state = "MENU"
                        elif event.key == pygame.K_UP:
                            if self.is_login_active:
                                self.is_login_active = False
                                self.active_field_idx = len(self.auth_order) - 1
                            elif self.active_field_idx > 0:
                                self.active_field_idx -= 1
                        elif event.key == pygame.K_DOWN:
                            if not self.is_login_active:
                                if self.active_field_idx < len(self.auth_order) - 1:
                                    self.active_field_idx += 1
                                else:
                                    self.is_login_active = True
                        elif event.key == pygame.K_TAB:
                            if not self.is_login_active:
                                self.active_field_idx = (self.active_field_idx + 1) % len(self.auth_order)
                        elif event.key == pygame.K_BACKSPACE:
                            if self.is_login_active:
                                self.login_alias = self.login_alias[:-1]
                            else:
                                active_fn = self.auth_order[self.active_field_idx]
                                self.auth_fields[active_fn] = self.auth_fields[active_fn][:-1]
                        
                        elif event.key == pygame.K_RETURN:
                            if self.is_login_active: 
                                self.process_login()
                            else:
                                if self.active_field_idx < len(self.auth_order) - 1:
                                    self.active_field_idx += 1
                                else:
                                    self.process_registration()
                        else:
                            char = event.unicode
                            if char:
                                if self.is_login_active:
                                    if char.isalpha() and len(self.login_alias) < 10: 
                                        self.login_alias += char.upper()
                                else:
                                    active_fn = self.auth_order[self.active_field_idx]
                                    if active_fn == "Alias":
                                        if char.isalpha() and len(self.auth_fields[active_fn]) < 10:
                                            self.auth_fields[active_fn] += char.upper()
                                    elif active_fn in ["Nombre", "Apellido"]:
                                        if (char.isalpha() or char == " ") and len(self.auth_fields[active_fn]) < 15:
                                            self.auth_fields[active_fn] += char
                                    elif active_fn == "Institucion":
                                        if (char.isalnum() or char in " .-_") and len(self.auth_fields[active_fn]) < 20:
                                            self.auth_fields[active_fn] += char

            elif self.state == "SCORES":
                self.draw_scores()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE: 
                            self.state = "MENU"
                        elif event.key == pygame.K_LEFT:
                            self.scores_category_idx = (self.scores_category_idx - 1) % len(self.categories)
                        elif event.key == pygame.K_RIGHT:
                            self.scores_category_idx = (self.scores_category_idx + 1) % len(self.categories)

            elif self.state == "GAME":
                if not self.game_over:
                    self.fall_time += dt
                    self.board.tiempo_acumulado_velocidad += dt
                    if self.board.tiempo_acumulado_velocidad >= 30000:  
                        self.board.intervalo_caida = max(80, self.board.intervalo_caida - 35)  
                        self.board.tiempo_acumulado_velocidad = 0  
                    
                    if self.fall_time > self.board.intervalo_caida:
                        if self.board.is_valid_move(self.current_piece, 0, 1): 
                            self.current_piece.y += 1
                        else:
                            lines = self.board.lock_piece(self.current_piece)
                            score_map = [0, 100, 300, 500, 800]
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
                            if event.key == pygame.K_LEFT and self.board.is_valid_move(self.current_piece, -1, 0): self.current_piece.x -= 1
                            if event.key == pygame.K_RIGHT and self.board.is_valid_move(self.current_piece, 1, 0): self.current_piece.x += 1
                            if event.key == pygame.K_DOWN and self.board.is_valid_move(self.current_piece, 0, 1): self.current_piece.y += 1
                            if event.key == pygame.K_UP:
                                old = self.current_piece.shape; self.current_piece.rotate()
                                if not self.board.is_valid_move(self.current_piece, 0, 0): self.current_piece.shape = old
                            if event.key == pygame.K_SPACE:
                                drop = 0
                                while self.board.is_valid_move(self.current_piece, 0, 1):
                                    self.current_piece.y += 1
                                    drop += 1
                                self.score += (drop * 2)
                            if event.key == pygame.K_c: self.handle_hold()
                self.draw_game()

if __name__ == "__main__":
    game = TetrisGame()
    game.run()
