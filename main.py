import pygame
import random
import heapq  # Para la cola de prioridad en A*

# Inicializar Pygame
pygame.init()

# Dimensiones de la ventana y del tablero
ANCHO, ALTO = 300, 300
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("8 Puzzle Game")

# Colores
BLANCO = (255, 255, 255)

# Cargar y dividir la imagen en 9 partes
imagen = pygame.image.load("puzzle_image.jpg")
segmentos = []
ancho_segmento = ANCHO // 3
alto_segmento = ALTO // 3

for fila in range(3):
    fila_segmento = []
    for col in range(3):
        rect = pygame.Rect(col * ancho_segmento, fila * alto_segmento, ancho_segmento, alto_segmento)
        imagen_segmento = imagen.subsurface(rect)
        fila_segmento.append(imagen_segmento)
    segmentos.append(fila_segmento)

# Definir la matriz inicial del puzzle (3x3)
tablero = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 0]  # El "0" representa el espacio vacío
]

# Estado objetivo
objetivo = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 0]
]


# Función para dibujar el tablero en la pantalla usando imágenes
def dibujar_tablero(ventana, tablero):
    ventana.fill(BLANCO)
    for fila in range(3):
        for col in range(3):
            numero = tablero[fila][col]
            if numero != 0:  # No dibujar el espacio vacío
                imagen_segmento = segmentos[(numero - 1) // 3][(numero - 1) % 3]  # Coordenada original de la imagen
                ventana.blit(imagen_segmento, (col * ancho_segmento, fila * alto_segmento))
    pygame.display.update()


# Función para mover las fichas (controles invertidos)
def mover_ficha(tablero, movimiento):
    fila, col = buscar_espacio_vacio(tablero)
    if movimiento == "arriba" and fila > 0:
        tablero[fila][col], tablero[fila - 1][col] = tablero[fila - 1][col], tablero[fila][col]
    elif movimiento == "abajo" and fila < 2:
        tablero[fila][col], tablero[fila + 1][col] = tablero[fila + 1][col], tablero[fila][col]
    elif movimiento == "izquierda" and col > 0:
        tablero[fila][col], tablero[fila][col - 1] = tablero[fila][col - 1], tablero[fila][col]
    elif movimiento == "derecha" and col < 2:
        tablero[fila][col], tablero[fila][col + 1] = tablero[fila][col + 1], tablero[fila][col]


# Función para encontrar el espacio vacío
def buscar_espacio_vacio(tablero):
    for fila in range(3):
        for col in range(3):
            if tablero[fila][col] == 0:
                return fila, col


# Mezclar el tablero al inicio del juego
def mezclar_tablero(tablero):
    movimientos = ["arriba", "abajo", "izquierda", "derecha"]
    for _ in range(100):  # Hacer 100 movimientos aleatorios
        mover_ficha(tablero, random.choice(movimientos))


# Calcular la distancia de Manhattan como heurística
def heuristica(tablero, objetivo):
    distancia = 0
    for fila in range(3):
        for col in range(3):
            valor = tablero[fila][col]
            if valor != 0:
                fila_obj, col_obj = divmod(valor - 1, 3)
                distancia += abs(fila - fila_obj) + abs(col - col_obj)
    return distancia


# Implementación del Algoritmo A*
def a_star(tablero):
    def serializar(tablero):
        return tuple(tuple(fila) for fila in tablero)

    def deserializar(tablero_serializado):
        return [list(fila) for fila in tablero_serializado]

    movimientos = ["arriba", "abajo", "izquierda", "derecha"]
    fila_col_delta = {"arriba": (-1, 0), "abajo": (1, 0), "izquierda": (0, -1), "derecha": (0, 1)}

    inicial = serializar(tablero)
    objetivo_serializado = serializar(objetivo)

    frontera = [
        (heuristica(tablero, objetivo), 0, inicial, [])]  # (costo estimado, costo acumulado, tablero, movimientos)
    visitados = set()

    while frontera:
        _, costo_acumulado, estado_actual, secuencia_movimientos = heapq.heappop(frontera)

        if estado_actual in visitados:
            continue
        visitados.add(estado_actual)

        if estado_actual == objetivo_serializado:
            return secuencia_movimientos

        tablero_actual = deserializar(estado_actual)
        fila_vacia, col_vacia = buscar_espacio_vacio(tablero_actual)

        for movimiento in movimientos:
            df, dc = fila_col_delta[movimiento]
            nueva_fila, nueva_col = fila_vacia + df, col_vacia + dc

            if 0 <= nueva_fila < 3 and 0 <= nueva_col < 3:  # Movimiento válido
                nuevo_tablero = [fila[:] for fila in tablero_actual]  # Copiar el tablero
                nuevo_tablero[fila_vacia][col_vacia], nuevo_tablero[nueva_fila][nueva_col] = nuevo_tablero[nueva_fila][
                    nueva_col], nuevo_tablero[fila_vacia][col_vacia]
                nuevo_estado = serializar(nuevo_tablero)

                if nuevo_estado not in visitados:
                    nuevo_costo_acumulado = costo_acumulado + 1
                    nuevo_costo_estimado = nuevo_costo_acumulado + heuristica(nuevo_tablero, objetivo)
                    heapq.heappush(frontera, (
                    nuevo_costo_estimado, nuevo_costo_acumulado, nuevo_estado, secuencia_movimientos + [movimiento]))

    return None  # No se encontró solución


# Visualizar el proceso de solución paso a paso
def visualizar_solucion(tablero, movimientos):
    for movimiento in movimientos:
        mover_ficha(tablero, movimiento)
        dibujar_tablero(ventana, tablero)
        pygame.time.delay(500)  # Retraso de 500 ms para visualizar el movimiento


# Bucle principal del juego
mezclar_tablero(tablero)
jugando = True
solucion_encontrada = False

while jugando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            jugando = False
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE and not solucion_encontrada:
                movimientos_solucion = a_star(tablero)
                if movimientos_solucion:
                    visualizar_solucion(tablero, movimientos_solucion)
                solucion_encontrada = True

    dibujar_tablero(ventana, tablero)

pygame.quit()
