#Programa Tablero
#Autor: Navarro Arellano Diego Emiliano
#Fecha: Abril 2025
#Grupo: 4CM2
import pygame
import sys
import random
import time


TAM = 4  # Tamaño del tablero (4x4)
NUM_ESTADOS = 16  # Número total de casillas/estados
MIN_SIMBOLOS = 3  # Mínimo número de símbolos en la cadena de movimientos
MAX_SIMBOLOS = 100  # Máximo número de símbolos en la cadena de movimientos
MAX_DFS = 4  # Límite de profundidad para DFS (controla el tiempo en cadenas largas)

# Dimensiones de la ventana:
# - Tablero: 400x400 (parte superior izquierda)
# - Diagramas (NFAs): se muestran en la parte inferior, divididos en dos áreas de 600x400
VENTANA_ANCHO = 1200
VENTANA_ALTO = 800

# Colores (usados para dibujar elementos en pantalla)
COLOR_BLANCO = (255, 255, 255)
COLOR_NEGRO = (0, 0, 0)
COLOR_ROJO = (255, 0, 0)
COLOR_AZUL_CLARO = (173, 216, 230)  # Color para el jugador 1 en el tablero
COLOR_VERDE_AMARGO = (0, 128, 0)  # Color para el jugador 2 en el tablero
COLOR_GRIS = (100, 100, 100)
COLOR_NODO = (220, 220, 250)  # Color de los nodos en el diagrama del NFA
COLOR_HIGHLIGHT = (0, 255, 0)  # Color para resaltar el nodo seleccionado en cada capa

# Parámetros iniciales del juego para cada jugador
J1_INICIAL = 1
J1_META = 16
J2_INICIAL = 4
J2_META = 13


# ========================================================
# CONSTRUCCIÓN DEL AUTÓMATA (NFA) A PARTIR DEL TABLERO
# ========================================================
def obtener_color(estado):
    """
    Retorna el color asociado a una casilla según su posición.
    Devuelve 'r' si la suma de fila y columna es impar, o 'b' si es par.
    """
    fila = (estado - 1) // TAM
    columna = (estado - 1) % TAM
    return 'r' if ((fila + columna) % 2 == 1) else 'b'


def construir_automata():
    """
    Construye el NFA (autómata) basado en el tablero 4x4.
    Cada estado (casilla) tiene transiciones en 8 direcciones (incluyendo diagonales)
    y se clasifican según el color ('r' o 'b') de la casilla destino.
    """
    automata = {}
    # Inicializar el autómata para cada estado con listas para 'r' y 'b'
    for estado in range(1, NUM_ESTADOS + 1):
        automata[estado] = {'r': [], 'b': []}

    # Lista de desplazamientos para las 8 direcciones (vertical, horizontal y diagonales)
    direcciones = [
        (-1, 0),  # Arriba
        (1, 0),  # Abajo
        (0, -1),  # Izquierda
        (0, 1),  # Derecha
        (-1, -1),  # Arriba-Izquierda
        (-1, 1),  # Arriba-Derecha
        (1, -1),  # Abajo-Izquierda
        (1, 1)  # Abajo-Derecha
    ]

    # Recorrer cada estado y calcular sus transiciones válidas
    for estado in range(1, NUM_ESTADOS + 1):
        fila_actual = (estado - 1) // TAM
        columna_actual = (estado - 1) % TAM
        for desplazamiento_fila, desplazamiento_columna in direcciones:
            fila_destino = fila_actual + desplazamiento_fila
            columna_destino = columna_actual + desplazamiento_columna
            # Verificar que el destino esté dentro del tablero
            if 0 <= fila_destino < TAM and 0 <= columna_destino < TAM:
                destino = fila_destino * TAM + columna_destino + 1
                color_destino = obtener_color(destino)
                automata[estado][color_destino].append(destino)
    return automata


# ========================================================
# DIBUJO DEL TABLERO (PARTE SUPERIOR IZQUIERDA DE LA VENTANA)
# ========================================================
def dibujar_tablero(pantalla, posicion_jugador1, posicion_jugador2):
    """
    Dibuja el tablero 4x4 y posiciona a los jugadores en el área asignada (0-400 px).
    """
    area_tablero = pygame.Rect(0, 0, 400, 400)
    pygame.draw.rect(pantalla, COLOR_BLANCO, area_tablero)

    # Calcular el tamaño de cada casilla
    tam_casilla = 400 // TAM

    # Dibujar líneas verticales y horizontales para formar el tablero
    for i in range(TAM + 1):
        pygame.draw.line(pantalla, COLOR_NEGRO, (i * tam_casilla, 0), (i * tam_casilla, 400))
        pygame.draw.line(pantalla, COLOR_NEGRO, (0, i * tam_casilla), (400, i * tam_casilla))

    # Dibujar cada casilla con su número y color
    for numero in range(1, NUM_ESTADOS + 1):
        fila = (numero - 1) // TAM
        columna = (numero - 1) % TAM
        color_casilla = COLOR_ROJO if obtener_color(numero) == 'r' else COLOR_NEGRO
        rect_casilla = pygame.Rect(columna * tam_casilla, fila * tam_casilla, tam_casilla, tam_casilla)
        pygame.draw.rect(pantalla, color_casilla, rect_casilla)
        fuente = pygame.font.Font(None, 30)
        # Se elige el color del texto en contraste con el color de la casilla
        texto = fuente.render(str(numero), True, COLOR_BLANCO if color_casilla == COLOR_NEGRO else COLOR_NEGRO)
        rect_texto = texto.get_rect(center=rect_casilla.center)
        pantalla.blit(texto, rect_texto)

    # Dibujar la posición del jugador 1
    fila_jugador1 = (posicion_jugador1 - 1) // TAM
    columna_jugador1 = (posicion_jugador1 - 1) % TAM
    rect_jugador1 = pygame.Rect(columna_jugador1 * tam_casilla, fila_jugador1 * tam_casilla, tam_casilla, tam_casilla)
    pygame.draw.rect(pantalla, COLOR_AZUL_CLARO, rect_jugador1)

    # Dibujar la posición del jugador 2, si es diferente a la del jugador 1
    if posicion_jugador2 != posicion_jugador1:
        fila_jugador2 = (posicion_jugador2 - 1) // TAM
        columna_jugador2 = (posicion_jugador2 - 1) % TAM
        rect_jugador2 = pygame.Rect(columna_jugador2 * tam_casilla, fila_jugador2 * tam_casilla, tam_casilla,
                                    tam_casilla)
        pygame.draw.rect(pantalla, COLOR_VERDE_AMARGO, rect_jugador2)

    # Escribir etiquetas "J1" y "J2" en sus respectivas posiciones
    fuente = pygame.font.Font(None, 30)
    if posicion_jugador1 != posicion_jugador2:
        texto_j1 = fuente.render("J1", True, COLOR_BLANCO)
        rect_texto_j1 = texto_j1.get_rect(center=(columna_jugador1 * tam_casilla + tam_casilla // 2,
                                                  fila_jugador1 * tam_casilla + tam_casilla // 2))
        pantalla.blit(texto_j1, rect_texto_j1)
        texto_j2 = fuente.render("J2", True, COLOR_BLANCO)
        rect_texto_j2 = texto_j2.get_rect(center=(columna_jugador2 * tam_casilla + tam_casilla // 2,
                                                  fila_jugador2 * tam_casilla + tam_casilla // 2))
        pantalla.blit(texto_j2, rect_texto_j2)


# ========================================================
# CÁLCULO DE LA DISTANCIA MANHATTAN (FILTRA MOVIMIENTOS)
# ========================================================
def distancia_manhattan(estado_actual, meta):
    """
    Calcula la distancia Manhattan entre dos casillas dadas (estado_actual y meta).
    """
    fila_estado = (estado_actual - 1) // TAM
    columna_estado = (estado_actual - 1) % TAM
    fila_meta = (meta - 1) // TAM
    columna_meta = (meta - 1) % TAM
    return abs(fila_estado - fila_meta) + abs(columna_estado - columna_meta)


# ========================================================
# OBTENCIÓN DE LA CADENA DE MOVIMIENTOS
# ========================================================
def obtener_cadena_movimientos(modo_ejecucion):
    """
    Solicita o genera una cadena de movimientos (compuesta de 'r' y 'b') según el modo de ejecución.
    En modo automático se genera una cadena aleatoria; en modo manual se permite la entrada del usuario.
    """
    if modo_ejecucion == 'automatico':
        cantidad_simbolos = random.randint(MIN_SIMBOLOS, MAX_SIMBOLOS)
        cadena_movimientos = ''.join(random.choice(['r', 'b']) for _ in range(cantidad_simbolos))
        print("Cadena generada (automático):", cadena_movimientos)
        return cadena_movimientos
    else:
        texto_ingresado = input(
            f"Ingrese cadena (r/b) entre {MIN_SIMBOLOS} y {MAX_SIMBOLOS}, o Enter para aleatoria: ").strip()
        if not texto_ingresado:
            cantidad_simbolos = random.randint(MIN_SIMBOLOS, MAX_SIMBOLOS)
            cadena_movimientos = ''.join(random.choice(['r', 'b']) for _ in range(cantidad_simbolos))
            print("Cadena generada (manual vacía):", cadena_movimientos)
            return cadena_movimientos
        else:
            if len(texto_ingresado) < MIN_SIMBOLOS or len(texto_ingresado) > MAX_SIMBOLOS:
                print("Longitud inválida, se genera aleatoria.")
                cantidad_simbolos = random.randint(MIN_SIMBOLOS, MAX_SIMBOLOS)
                cadena_movimientos = ''.join(random.choice(['r', 'b']) for _ in range(cantidad_simbolos))
                print("Cadena generada:", cadena_movimientos)
                return cadena_movimientos
            # Verificar que cada símbolo sea válido
            for simbolo in texto_ingresado:
                if simbolo not in ['r', 'b']:
                    print("Caracter inválido, se genera aleatoria.")
                    cantidad_simbolos = random.randint(MIN_SIMBOLOS, MAX_SIMBOLOS)
                    cadena_movimientos = ''.join(random.choice(['r', 'b']) for _ in range(cantidad_simbolos))
                    print("Cadena generada:", cadena_movimientos)
                    return cadena_movimientos
            print("Cadena ingresada (manual):", texto_ingresado)
            return texto_ingresado


# ========================================================
# DFS PARA GENERAR CAMINOS (CON LÍMITE DE PROFUNDIDAD)
# ========================================================
def dfs_caminos(automata, estado_actual, cadena, indice, camino, caminos_completos, caminos_ganadores, meta):
    """
    Función recursiva que explora todas las rutas posibles a partir de 'estado_actual'
    siguiendo la cadena de movimientos. Se almacenan tanto todos los caminos como
    aquellos que alcanzan la meta.
    """
    camino.append(estado_actual)
    # Caso base: fin de la cadena o se alcanzó el límite de profundidad
    if indice == len(cadena) or indice >= MAX_DFS:
        caminos_completos.append(list(camino))
        if estado_actual == meta:
            caminos_ganadores.append(list(camino))
        camino.pop()
        return

    simbolo = cadena[indice]
    destinos = automata[estado_actual][simbolo]
    if destinos:
        # Explorar cada destino posible para el símbolo actual
        for destino in destinos:
            dfs_caminos(automata, destino, cadena, indice + 1, camino, caminos_completos, caminos_ganadores, meta)
    else:
        caminos_completos.append(list(camino))
        if estado_actual == meta:
            caminos_ganadores.append(list(camino))
    camino.pop()


def generar_caminos_jugador(automata, estado_inicial, meta, cadena):
    """
    Genera y retorna dos listas:
      - caminos_completos: todas las rutas posibles siguiendo la cadena.
      - caminos_ganadores: rutas que logran alcanzar la meta.
    """
    caminos_completos = []
    caminos_ganadores = []
    dfs_caminos(automata, estado_inicial, cadena, 0, [], caminos_completos, caminos_ganadores, meta)
    return caminos_completos, caminos_ganadores


def guardar_caminos(caminos, nombre_archivo):
    """
    Guarda la lista de caminos en un archivo de texto, cada línea representa un camino.
    """
    with open(nombre_archivo, "w") as archivo:
        for camino in caminos:
            archivo.write(" ".join(map(str, camino)) + "\n")
    print(f"Archivo '{nombre_archivo}' generado.")


# ========================================================
# CONSTRUCCIÓN DE CAPAS DEL NFA (PARA DIAGRAMA DINÁMICO)
# ========================================================
def construir_capas(automata, estado_inicial, prefijo_cadena):
    """
    A partir del estado_inicial y un prefijo de la cadena de movimientos,
    construye una lista de capas (cada capa es un conjunto de estados alcanzables).
    La capa 0 corresponde al estado_inicial; cada capa i incluye los estados
    alcanzados tras consumir los primeros i símbolos del prefijo.
    """
    capas = []
    capa_actual = {estado_inicial}
    capas.append(capa_actual)
    for simbolo in prefijo_cadena:
        siguiente_capa = set()
        for estado in capa_actual:
            for destino in automata[estado][simbolo]:
                siguiente_capa.add(destino)
        capas.append(siguiente_capa)
        capa_actual = siguiente_capa
    return capas


# ========================================================
# DIBUJAR DIAGRAMA DEL NFA EN CAPAS
# ========================================================
def dibujar_nfa_en_capas(pantalla, automata, capas, nodos_destacados, offset_x, offset_y, ancho_area, alto_area, titulo,
                         prefijo_cadena):
    """
    Dibuja el diagrama del NFA hasta la última capa en el área definida.
    Se resaltan los nodos que se encuentran en el diccionario 'nodos_destacados'
    (clave = número de capa, valor = nodo seleccionado en esa capa).
    """
    # Dibujar fondo del área
    area = pygame.Rect(offset_x, offset_y, ancho_area, alto_area)
    pygame.draw.rect(pantalla, (245, 245, 245), area)

    # Dibujar título en la parte superior del área
    fuente_titulo = pygame.font.Font(None, 28)
    texto_titulo = fuente_titulo.render(titulo, True, COLOR_NEGRO)
    pantalla.blit(texto_titulo, (offset_x + 20, offset_y + 10))

    # Calcular separación horizontal entre capas
    cantidad_capas = len(capas)
    distancia_x = (ancho_area - 100) / (cantidad_capas - 1) if cantidad_capas > 1 else 0
    x_inicial = offset_x + 50
    alto_disponible = alto_area - 50

    # Almacenar las posiciones de los nodos para luego dibujar las conexiones
    posiciones = {}
    for indice_capa, capa in enumerate(capas):
        x = x_inicial + indice_capa * distancia_x
        capa_ordenada = sorted(capa)
        cantidad_nodos = len(capa_ordenada)
        if cantidad_nodos == 0:
            continue
        distancia_y = alto_disponible // (cantidad_nodos + 1)
        for indice_nodo, estado in enumerate(capa_ordenada, start=1):
            y = offset_y + 50 + indice_nodo * distancia_y
            posiciones[(estado, indice_capa)] = (x, y)
            # Determinar el color del nodo: se resalta si fue elegido en esta capa
            color_nodo = COLOR_HIGHLIGHT if nodos_destacados.get(indice_capa, None) == estado else COLOR_NODO
            pygame.draw.circle(pantalla, color_nodo, (x, y), 15)
            pygame.draw.circle(pantalla, COLOR_NEGRO, (x, y), 15, 2)
            fuente_nodo = pygame.font.Font(None, 20)
            texto_nodo = fuente_nodo.render(str(estado), True, COLOR_NEGRO)
            rect_texto_nodo = texto_nodo.get_rect(center=(x, y))
            pantalla.blit(texto_nodo, rect_texto_nodo)

    # Dibujar las aristas entre nodos de capas consecutivas
    for indice_capa in range(cantidad_capas - 1):
        simbolo = prefijo_cadena[indice_capa] if indice_capa < len(prefijo_cadena) else ''
        for estado in capas[indice_capa]:
            # Explorar conexiones (sin importar el color) hacia la siguiente capa
            for destino in automata[estado]['r'] + automata[estado]['b']:
                if destino in capas[indice_capa + 1]:
                    if (estado, indice_capa) in posiciones and (destino, indice_capa + 1) in posiciones:
                        x1, y1 = posiciones[(estado, indice_capa)]
                        x2, y2 = posiciones[(destino, indice_capa + 1)]
                        pygame.draw.line(pantalla, COLOR_NEGRO, (x1, y1), (x2, y2), 2)
                        # Colocar el símbolo en el punto medio de la arista
                        mx, my = (x1 + x2) // 2, (y1 + y2) // 2
                        fuente_simbolo = pygame.font.Font(None, 18)
                        texto_simbolo = fuente_simbolo.render(simbolo, True, COLOR_NEGRO)
                        pantalla.blit(texto_simbolo, (mx, my))


# ========================================================
# SIMULACIÓN DEL JUEGO POR TURNOS
# ========================================================
def simular_juego_turn_based(automata, cadena_movimientos, pantalla, jugador_inicia):
    """
    Simula el juego por turnos. Ambos jugadores procesan la misma cadena de movimientos.
    Se actualizan y muestran en pantalla los diagramas del NFA en capas para cada jugador,
    resaltando el nodo seleccionado en cada capa. Al finalizar se guardan los diagramas en PNG.
    """
    # Posiciones iniciales de los jugadores
    posicion_jugador1 = J1_INICIAL
    posicion_jugador2 = J2_INICIAL

    # Diccionarios para almacenar el nodo seleccionado en cada capa para cada jugador
    nodos_destacados_j1 = {}  # clave: capa, valor: nodo
    nodos_destacados_j2 = {}

    print("\nInicia el juego.")
    print("El jugador que inicia es:", jugador_inicia)
    reloj = pygame.time.Clock()

    # Dibujo inicial de los diagramas del NFA con cadena vacía (capa 0)
    capas_jugador1 = construir_capas(automata, J1_INICIAL, "")
    capas_jugador2 = construir_capas(automata, J2_INICIAL, "")
    pantalla.fill(COLOR_BLANCO)
    dibujar_tablero(pantalla, posicion_jugador1, posicion_jugador2)
    dibujar_nfa_en_capas(pantalla, automata, capas_jugador1, nodos_destacados_j1, 0, 400, 600, 400, "NFA Jugador 1", "")
    dibujar_nfa_en_capas(pantalla, automata, capas_jugador2, nodos_destacados_j2, 600, 400, 600, 400, "NFA Jugador 2",
                         "")
    pygame.display.flip()
    pygame.time.delay(1500)

    turno_actual = jugador_inicia  # 'J1' o 'J2'

    # Procesar cada símbolo de la cadena de movimientos
    for indice, simbolo in enumerate(cadena_movimientos):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Función interna para elegir un destino que no empeore la distancia a la meta
        def elegir_destino(opciones_destino, meta):
            if not opciones_destino:
                return None
            distancia_optima = min(distancia_manhattan(x, meta) for x in opciones_destino)
            opciones_validas = [x for x in opciones_destino if distancia_manhattan(x, meta) <= distancia_optima + 1]
            return random.choice(opciones_validas) if opciones_validas else random.choice(opciones_destino)

        # Procesamiento para el Jugador 1
        destinos_jugador1 = [dest for dest in automata[posicion_jugador1][simbolo] if dest != posicion_jugador2]
        if destinos_jugador1:
            destino_elegido_j1 = elegir_destino(destinos_jugador1, J1_META)
            posicion_jugador1 = destino_elegido_j1
            print(f"[J1] -> {posicion_jugador1} con '{simbolo}'")
            nodos_destacados_j1[indice + 1] = destino_elegido_j1  # Registrar el nodo seleccionado en esta capa
        else:
            print(f"[J1] no puede moverse con '{simbolo}', cediendo turno a J2")

        # Procesamiento para el Jugador 2
        destinos_jugador2 = [dest for dest in automata[posicion_jugador2][simbolo] if dest != posicion_jugador1]
        if destinos_jugador2:
            destino_elegido_j2 = elegir_destino(destinos_jugador2, J2_META)
            posicion_jugador2 = destino_elegido_j2
            print(f"[J2] -> {posicion_jugador2} con '{simbolo}'")
            nodos_destacados_j2[indice + 1] = destino_elegido_j2
        else:
            print(f"[J2] no puede moverse con '{simbolo}', cediendo turno a J1")

        # Construir diagramas actualizados con el prefijo actual de la cadena
        prefijo_actual = cadena_movimientos[:indice + 1]
        capas_jugador1 = construir_capas(automata, J1_INICIAL, prefijo_actual)
        capas_jugador2 = construir_capas(automata, J2_INICIAL, prefijo_actual)

        pantalla.fill(COLOR_BLANCO)
        dibujar_tablero(pantalla, posicion_jugador1, posicion_jugador2)
        dibujar_nfa_en_capas(pantalla, automata, capas_jugador1, nodos_destacados_j1, 0, 400, 600, 400, "NFA Jugador 1",
                             prefijo_actual)
        dibujar_nfa_en_capas(pantalla, automata, capas_jugador2, nodos_destacados_j2, 600, 400, 600, 400,
                             "NFA Jugador 2", prefijo_actual)
        pygame.display.flip()
        pygame.time.delay(1500)
        reloj.tick(60)

    print("\nCadena terminada.")
    print(f"Posiciones finales: J1={posicion_jugador1}, J2={posicion_jugador2}")
    if posicion_jugador1 == J1_META:
        print("¡J1 alcanzó su meta!")
    if posicion_jugador2 == J2_META:
        print("¡J2 alcanzó su meta!")

    # Guardar los diagramas finales del NFA en archivos PNG
    area_nfa_jugador1 = pantalla.subsurface(pygame.Rect(0, 400, 600, 400))
    area_nfa_jugador2 = pantalla.subsurface(pygame.Rect(600, 400, 600, 400))
    pygame.image.save(area_nfa_jugador1, "NFA_jugador1.png")
    pygame.image.save(area_nfa_jugador2, "NFA_jugador2.png")

    pygame.time.delay(5000)
    pygame.quit()
    return (posicion_jugador1 == J1_META, posicion_jugador2 == J2_META)


def main():
    """
    Función principal que inicializa el juego, solicita el modo de ejecución,
    obtiene la cadena de movimientos, genera las rutas para cada jugador,
    y finalmente inicia la simulación del juego.
    """
    random.seed(time.time())
    automata = construir_automata()

    # Seleccionar modo de ejecución
    print("\nSeleccione modo de ejecución:")
    print(" 1) Automático")
    print(" 2) Manual")
    opcion = input("Opción (1/2): ").strip()
    modo_ejecucion = "automatico" if opcion == "1" else "manual"

    # Obtener la cadena de movimientos según el modo seleccionado
    cadena_movimientos = obtener_cadena_movimientos(modo_ejecucion)


    # Elegir aleatoriamente quién inicia y mostrarlo en consola
    jugador_inicia = random.choice(['J1', 'J2'])
    print("El jugador que inicia es:", jugador_inicia)

    pygame.init()
    pantalla = pygame.display.set_mode((VENTANA_ANCHO, VENTANA_ALTO))
    pygame.display.set_caption("Simulación Ajedrez 4x4 - NFA (Dinámica)")
    print("\n--- Iniciando Simulación ---\n")
    fin_jugador1, fin_jugador2 = simular_juego_turn_based(automata, cadena_movimientos, pantalla, jugador_inicia)

    # Generar caminos (completos y ganadores) para cada jugador antes de la simulación.
    caminos_completos_jugador1, caminos_ganadores_jugador1 = generar_caminos_jugador(automata, J1_INICIAL, J1_META,
                                                                                     cadena_movimientos)
    caminos_completos_jugador2, caminos_ganadores_jugador2 = generar_caminos_jugador(automata, J2_INICIAL, J2_META,
                                                                                     cadena_movimientos)
    guardar_caminos(caminos_completos_jugador1, "movimientos_completos_jugador1.txt")
    guardar_caminos(caminos_ganadores_jugador1, "movimientos_ganadores_jugador1.txt")
    guardar_caminos(caminos_completos_jugador2, "movimientos_completos_jugador2.txt")
    guardar_caminos(caminos_ganadores_jugador2, "movimientos_ganadores_jugador2.txt")

    print("\n--- Programa Finalizado ---")
    if fin_jugador1:
        print("Jugador 1 alcanzó su meta durante la simulación.")
    if fin_jugador2:
        print("Jugador 2 alcanzó su meta durante la simulación.")
    sys.exit()




if __name__ == "__main__":
    main()
