import random

class LogicaTetris:
    def __init__(self):
        self.ancho = 10
        self.alto = 20
        # Tablero numérico: 0 es vacío, 1-7 son colores
        self.tablero = [[0 for _ in range(self.ancho)] for _ in range(self.alto)]
        
        self.piezas = [
            [[1, 1, 1, 1]],         # I
            [[1, 1], [1, 1]],       # O
            [[0, 1, 0], [1, 1, 1]], # T
            [[0, 1, 1], [1, 1, 0]], # S
            [[1, 1, 0], [0, 1, 1]], # Z
            [[1, 0, 0], [1, 1, 1]], # J
            [[0, 0, 1], [1, 1, 1]]  # L
        ]
        
        self.puntos = 0
        self.siguiente_idx = random.randint(0, len(self.piezas)-1)
        self.siguiente_pieza = {'forma': self.piezas[self.siguiente_idx], 'color_idx': self.siguiente_idx}
        self.pieza_hold = None
        self.ya_cambio_hold = False
        
        self.nueva_pieza()

    def nueva_pieza(self):
        self.tipo_pieza = self.siguiente_idx
        self.pieza = {'forma': self.piezas[self.tipo_pieza], 'color_idx': self.tipo_pieza}
        
        self.siguiente_idx = random.randint(0, len(self.piezas)-1)
        self.siguiente_pieza = {'forma': self.piezas[self.siguiente_idx], 'color_idx': self.siguiente_idx}
        
        self.x = self.ancho // 2 - len(self.pieza['forma'][0]) // 2
        self.y = 0
        self.ya_cambio_hold = False

    def mover(self, dx, dy):
        if not self.colision(self.x + dx, self.y + dy, self.pieza['forma']):
            self.x += dx
            self.y += dy
            return True
        return False

    def rotar(self):
        pieza_rotada = list(zip(*self.pieza['forma'][::-1]))
        if not self.colision(self.x, self.y, pieza_rotada):
            self.pieza['forma'] = pieza_rotada

    def colision(self, nx, ny, forma):
        for r, fila in enumerate(forma):
            for c, valor in enumerate(fila):
                if valor:
                    if nx + c < 0 or nx + c >= self.ancho or ny + r >= self.alto:
                        return True
                    if ny + r >= 0 and self.tablero[ny + r][nx + c] != 0:
                        return True
        return False

    def fijar_pieza(self):
        for r, fila in enumerate(self.pieza['forma']):
            for c, valor in enumerate(fila):
                if valor:
                    self.tablero[self.y + r][self.x + c] = self.pieza['color_idx'] + 1
        self.limpiar_lineas()
        self.nueva_pieza()
        return self.colision(self.x, self.y, self.pieza['forma'])

    def limpiar_lineas(self):
        lineas_a_borrar = [i for i, fila in enumerate(self.tablero) if all(celda != 0 for celda in fila)]
        for i in lineas_a_borrar:
            del self.tablero[i]
            self.tablero.insert(0, [0 for _ in range(self.ancho)])
        
        puntos_base = [0, 100, 300, 500, 800]
        self.puntos += puntos_base[len(lineas_a_borrar)]

    def bajar(self):
        if not self.mover(0, 1):
            return self.fijar_pieza()
        return False

    def hard_drop(self):
        while self.mover(0, 1):
            pass
        return self.fijar_pieza()

    def hacer_hold(self):
        if self.ya_cambio_hold: return
        
        if self.pieza_hold is None:
            self.pieza_hold = {'forma': self.piezas[self.tipo_pieza], 'color_idx': self.tipo_pieza}
            self.nueva_pieza()
        else:
            temp_idx = self.tipo_pieza
            self.tipo_pieza = self.pieza_hold['color_idx']
            self.pieza = {'forma': self.piezas[self.tipo_pieza], 'color_idx': self.tipo_pieza}
            self.pieza_hold = {'forma': self.piezas[temp_idx], 'color_idx': temp_idx}
            
            self.x = self.ancho // 2 - len(self.pieza['forma'][0]) // 2
            self.y = 0
            
        self.ya_cambio_hold = True