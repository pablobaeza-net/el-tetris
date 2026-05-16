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

SHAPES = [
    [[1, 1, 1, 1]], [[1, 1], [1, 1]], [[0, 1, 0], [1, 1, 1]],
    [[0, 1, 1], [1, 1, 0]], [[1, 1, 0], [0, 1, 1]],
    [[1, 0, 0], [1, 1, 1]], [[0, 0, 1], [1, 1, 1]]
]

# ==========================================
# 2. MODELO DE DATOS
# ==========================================
class Tetrimino:
    def __init__(self, x, y, shape_idx=None):
        self.x = x
        self.y = y
        self.type = shape_idx if shape_idx is not None else random.randint(1, len(SHAPES))
        self.shape = SHAPES[self.type - 1]
        self.color = COLORS[self.type]

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

class Board:
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]

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
# 3. MOTOR DEL JUEGO
# ==========================================
class TetrisGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH + UI_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tetris Pro - Persistent Edition")
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.SysFont("Consolas", 45, bold=True)
        self.font_ui = pygame.font.SysFont("Consolas", 22, bold=True)
        
        self.state = "MENU"
        self.player_nick = ""
        self.high_scores = self.load_scores()
        self.menu_options = ["JUGAR", "PUNTAJES", "SALIR"]
        self.selected_idx = 0
        self.reset_game()

    def load_scores(self):
        if os.path.exists("scores.json"):
            with open("scores.json", "r") as f:
                return json.load(f)
        return {}

    def save_score(self):
        # Si el nick ya existe, solo guarda si el nuevo score es mayor
        old_score = self.high_scores.get(self.player_nick, 0)
        if self.score > old_score:
            self.high_scores[self.player_nick] = self.score
            with open("scores.json", "w") as f:
                json.dump(self.high_scores, f)

    def reset_game(self):
        self.board = Board()
        self.queue = deque([Tetrimino(3, 0) for _ in range(4)])
        self.current_piece = self.queue.popleft()
        self.hold_piece = None
        self.can_hold = True
        self.score = 0
        self.game_over = False
        self.fall_time = 0

    def handle_hold(self):
        if not self.can_hold: return
        
        if self.hold_piece is None:
            self.hold_piece = Tetrimino(3, 0, self.current_piece.type)
            self.current_piece = self.queue.popleft()
            self.queue.append(Tetrimino(3, 0))
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
        self.draw_text_centered("TETRIS PRO", 100, self.font_title, (0, 255, 200))
        
        mouse_pos = pygame.mouse.get_pos()
        for i, opt in enumerate(self.menu_options):
            y = 250 + (i * 60)
            rect = pygame.Rect(0, 0, 200, 40)
            rect.center = ((SCREEN_WIDTH + UI_WIDTH) // 2, y)
            
            is_hover = rect.collidepoint(mouse_pos)
            if is_hover: self.selected_idx = i
            
            color = (0, 255, 100) if self.selected_idx == i else (150, 150, 150)
            self.draw_text_centered(opt, y, self.font_ui, color)
        pygame.display.flip()

    def draw_input_screen(self):
        self.screen.fill((15, 15, 25))
        self.draw_text_centered("INGRESA TU NICK:", 200, self.font_ui)
        self.draw_text_centered(self.player_nick + "_", 260, self.font_title, (255, 255, 0))
        self.draw_text_centered("Presiona ENTER para empezar", 400, self.font_ui, (100, 100, 100))
        pygame.display.flip()

    def draw_scores(self):
        self.screen.fill((10, 10, 20))
        self.draw_text_centered("TOP PUNTAJES", 60, self.font_title, (255, 215, 0))
        
        sorted_scores = sorted(self.high_scores.items(), key=lambda x: x[1], reverse=True)[:8]
        for i, (nick, score) in enumerate(sorted_scores):
            txt = f"{i+1}. {nick[:10]} - {score} pts"
            self.draw_text_centered(txt, 150 + (i * 45), self.font_ui)

        self.draw_text_centered("ESC para volver", 530, self.font_ui, (80, 80, 80))
        pygame.display.flip()

    def draw_game(self):
        self.screen.fill((15, 15, 20))
        # Tablero central
        for y, row in enumerate(self.board.grid):
            for x, val in enumerate(row):
                rect = (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE-1, BLOCK_SIZE-1)
                pygame.draw.rect(self.screen, COLORS[val] if val else (30, 30, 35), rect, 0 if val else 1)

        # Pieza actual
        for r, row in enumerate(self.current_piece.shape):
            for c, val in enumerate(row):
                if val:
                    pygame.draw.rect(self.screen, self.current_piece.color, 
                                     ((self.current_piece.x+c)*BLOCK_SIZE, (self.current_piece.y+r)*BLOCK_SIZE, BLOCK_SIZE-1, BLOCK_SIZE-1))
        
        # UI Lateral
        ux = SCREEN_WIDTH + 20
        pygame.draw.rect(self.screen, (40, 40, 50), (SCREEN_WIDTH, 0, UI_WIDTH, SCREEN_HEIGHT))
        
        self.screen.blit(self.font_ui.render(f"PLAYER: {self.player_nick}", True, (255, 255, 255)), (ux, 30))
        self.screen.blit(self.font_ui.render(f"SCORE: {self.score}", True, (0, 255, 100)), (ux, 80))
        
        # Preview HOLD
        self.screen.blit(self.font_ui.render("HOLD (C):", True, (150, 150, 150)), (ux, 150))
        if self.hold_piece:
            for r, row in enumerate(self.hold_piece.shape):
                for c, val in enumerate(row):
                    if val: pygame.draw.rect(self.screen, self.hold_piece.color, (ux + c*20, 190 + r*20, 18, 18))

        # Preview NEXT
        self.screen.blit(self.font_ui.render("SIGUIENTES:", True, (150, 150, 150)), (ux, 300))
        for i, p in enumerate(list(self.queue)[:3]):
            for r, row in enumerate(p.shape):
                for c, val in enumerate(row):
                    if val: pygame.draw.rect(self.screen, p.color, (ux + c*20, 340 + i*70 + r*20, 18, 18))

        if self.game_over:
            self.draw_text_centered("GAME OVER - M: MENU", SCREEN_HEIGHT//2, self.font_ui, (255, 50, 50))

        pygame.display.flip()

    def run(self):
        while True:
            if self.state == "MENU":
                self.draw_menu()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP: self.selected_idx = (self.selected_idx - 1) % 3
                        if event.key == pygame.K_DOWN: self.selected_idx = (self.selected_idx + 1) % 3
                        if event.key == pygame.K_RETURN:
                            if self.selected_idx == 0: self.state = "INPUT"
                            elif self.selected_idx == 1: self.state = "SCORES"
                            else: pygame.quit(); sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if self.selected_idx == 0: self.state = "INPUT"
                        elif self.selected_idx == 1: self.state = "SCORES"
                        else: pygame.quit(); sys.exit()

            elif self.state == "INPUT":
                self.draw_input_screen()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN and self.player_nick.strip():
                            self.reset_game(); self.state = "GAME"
                        elif event.key == pygame.K_BACKSPACE: self.player_nick = self.player_nick[:-1]
                        elif len(self.player_nick) < 10 and event.unicode.isalnum():
                            self.player_nick += event.unicode.upper()

            elif self.state == "SCORES":
                self.draw_scores()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: pygame.quit(); sys.exit()
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: self.state = "MENU"

            elif self.state == "GAME":
                self.fall_time += self.clock.get_rawtime()
                self.clock.tick()
                if not self.game_over:
                    if self.fall_time > 200:
                        if self.board.is_valid_move(self.current_piece, 0, 1): self.current_piece.y += 1
                        else:
                            lines = self.board.lock_piece(self.current_piece)
                            self.score += [10, 110, 310, 510, 1210][lines]
                            self.current_piece = self.queue.popleft()
                            self.queue.append(Tetrimino(3, 0))
                            self.can_hold = True
                            if not self.board.is_valid_move(self.current_piece, 0, 0): 
                                self.game_over = True
                                self.save_score()
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
