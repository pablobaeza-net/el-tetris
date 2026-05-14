import random
import copy

ANCHO_TAB = 10
ALTO_TAB = 20

PIEZAS = [
    {'forma': [[1, 1, 1, 1]], 'color_idx': 0},  # I
    {'forma': [[1, 1], [1, 1]], 'color_idx': 1},  # O
    {'forma': [[0, 1, 0], [1, 1, 1]], 'color_idx': 2},  # T
    {'forma': [[0, 1, 1], [1, 1, 0]], 'color_idx': 3},  # S
    {'forma': [[1, 1, 0], [0, 1, 1]], 'color_idx': 4},  # Z
    {'forma': [[1, 0, 0], [1, 1, 1]], 'color_idx': 5},  # J
    {'forma': [[0, 0, 1], [1, 1, 1]], 'color_idx': 6}   # L
]

class LogicaTetris:
    def __init__(self):
        self.tablero = [[0] * ANCHO_TAB for _ in range(ALTO_TAB)]
        self.puntos = 0
        self.siguiente_pieza = copy.deepcopy(random.choice(PIEZAS))
        self.pieza_hold = None
        self.ya_cambio_hold = False
        self.nueva_pieza_en_juego()

    def nueva_pieza_en_juego(self):
        self.pieza = self.siguiente_pieza
        
        # 🆕 Lógica para que la siguiente pieza NO sea igual a la actual
        nueva_sig = copy.deepcopy(random.choice(PIEZAS))
        while nueva_sig['color_idx'] == self.pieza['color_idx']:
            nueva_sig = copy.deepcopy(random.choice(PIEZAS))
            
        self.siguiente_pieza = nueva_sig
        
        self.x = 3
        self.y = 0
        self.ya_cambio_hold = False
        return self.colision()

    def hacer_hold(self):
        if self.ya_cambio_hold:
            return
        if self.pieza_hold is None:
            self.pieza_hold = copy.deepcopy(PIEZAS[self.pieza['color_idx']])
            self.nueva_pieza_en_juego()
        else:
            aux = copy.deepcopy(PIEZAS[self.pieza['color_idx']])
            self.pieza = copy.deepcopy(self.pieza_hold)
            self.pieza_hold = aux
            self.x = 3
            self.y = 0
        self.ya_cambio_hold = True

    def rotar(self):
        forma_original = self.pieza['forma']
        self.pieza['forma'] = [list(fila) for fila in zip(*self.pieza['forma'][::-1])]
        if self.colision():
            self.pieza['forma'] = forma_original

    def colision(self, dx=0, dy=0):
        for i, fila in enumerate(self.pieza['forma']):
            for j, celda in enumerate(fila):
                if celda:
                    nx, ny = self.x + j + dx, self.y + i + dy
                    if nx < 0 or nx >= ANCHO_TAB or ny >= ALTO_TAB:
                        return True
                    if ny >= 0 and self.tablero[ny][nx]:
                        return True
        return False

    def bajar(self):
        if not self.colision(dy=1):
            self.y += 1
            return False
        else:
            return self.fijar_pieza()

    def fijar_pieza(self):
        for i, fila in enumerate(self.pieza['forma']):
            for j, celda in enumerate(fila):
                if celda:
                    if self.y + i < 0: return True
                    self.tablero[self.y + i][self.x + j] = self.pieza['color_idx'] + 1
                    
        # ✅ AQUÍ RECUPERAMOS TUS PUNTOS POR COLOCAR LA FICHA
        self.puntos += 10
        
        self.limpiar_lineas()
        return self.nueva_pieza_en_juego()

    def limpiar_lineas(self):
        nuevas = [f for f in self.tablero if not all(f)]
        lineas = ALTO_TAB - len(nuevas)
        self.tablero = [[0] * ANCHO_TAB for _ in range(lineas)] + nuevas
        
        # ✅ PUNTOS POR ELIMINAR LÍNEAS
        self.puntos += lineas * 100

    def mover(self, dx, dy):
        if not self.colision(dx, dy):
            self.x += dx
            self.y += dy

    def hard_drop(self):
        while not self.colision(dy=1):
            self.y += 1
        return self.fijar_pieza()