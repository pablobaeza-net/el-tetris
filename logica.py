import random
import copy

ANCHO_TAB = 10
ALTO_TAB = 20

PIEZAS = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[0, 1, 0], [1, 1, 1]],  # T
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[1, 0, 0], [1, 1, 1]],  # J
    [[0, 0, 1], [1, 1, 1]]   # L
]

class LogicaTetris:
    def __init__(self):
        self.tablero = [[0] * ANCHO_TAB for _ in range(ALTO_TAB)]
        self.pieza = self.nueva_pieza()
        self.x = 4  # 🆕 CENTRO mejorado
        self.y = 0
        self.puntos = 0
    
    def nueva_pieza(self):
        idx = random.randint(0, len(PIEZAS)-1)
        return {'forma': copy.deepcopy(PIEZAS[idx])}  # 🆕 Copia profunda
    
    def rotar(self):
        forma = self.pieza['forma']
        self.pieza['forma'] = [list(fila) for fila in zip(*forma[::-1])]
        # Verificar colisión después de rotar
        if self.colision():
            # Deshacer rotación si colisiona
            self.pieza['forma'] = forma
    
    def colision(self, dx=0, dy=0):
        forma = self.pieza['forma']
        for i, fila in enumerate(forma):
            for j, celda in enumerate(fila):
                if celda:
                    nx = self.x + j + dx
                    ny = self.y + i + dy
                    if nx < 0 or nx >= ANCHO_TAB or ny >= ALTO_TAB:
                        return True
                    if ny >= 0 and self.tablero[ny][nx]:
                        return True
        return False
    
    def fijar_pieza(self):
        for i, fila in enumerate(self.pieza['forma']):
            for j, celda in enumerate(fila):
                if celda:
                    y_tab = self.y + i
                    x_tab = self.x + j
                    if y_tab >= 0:  # 🆕 Evita índices negativos
                        self.tablero[y_tab][x_tab] = 1
        self.limpiar_lineas()
        self.pieza = self.nueva_pieza()
        self.x, self.y = 4, 0  # 🆕 Reset posición
        
        # Verificar Game Over
        return self.colision()
    
    def limpiar_lineas(self):
        lineas = 0
        nueva_tablero = [fila for fila in self.tablero if not all(fila)]
        lineas = ALTO_TAB - len(nueva_tablero)
        self.tablero = [[0] * ANCHO_TAB for _ in range(lineas)] + nueva_tablero
        self.puntos += lineas * 100
    
    def mover(self, dx, dy):
        if not self.colision(dx, dy):
            self.x += dx
            self.y += dy
            return True
        return False
    
    def bajar(self):
        if not self.colision(0, 1):
            self.y += 1
            return False
        return self.fijar_pieza()
    
    def hard_drop(self):
        while not self.colision(0, 1):
            self.y += 1
        return self.fijar_pieza()