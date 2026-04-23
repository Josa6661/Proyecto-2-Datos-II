import heapq
from lector import cargar_y_convertir_mapa
from backtracking import  traducir_ruta_a_instrucciones

"""
En ese archivo se implementa el algoritmo greedy para planificar el recorrido del robot de entrega.

Se utilizó Nearest Neighbor para decidir el orden de visita.
Se utiliza Dijkstra para calcular caminos entre puntos.
"""
def dijkstra(matriz, origen, destino):
    """}
    Este es el algoritmo dijkstra (greedy) que se utiliza para encontrar el camino más corto entre dos puntos
    en el mapa

    entradas:
        - matriz: con el formato de 0=obstáculo, 1=camino, 2=inicio, 3=estación
        - origen: tupla (fila, columna) del punto de partida
        - destino: tupla (fila, columna) del punto de destino

    salidas:
        distancia: número de pasos del camino más corto (inf si no existe)
        camino: lista de tuplas en orden desde origen hasta destino
    """
    filas = len(matriz)
    cols = len(matriz[0])
    movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    dist = [[float("inf")] * cols for i in range(filas)]
    dist[origen[0]][origen[1]] = 0

    padre = {}
    padre[origen] = None

    # Cola de prioridad: (costo_acumulado, (fila, col))
    heap = [(0, origen)]

    while heap:
        costo_actual, actual = heapq.heappop(heap)

        # Si ya encontramos un camino más corto a este nodo, ignoramos
        if costo_actual > dist[actual[0]][actual[1]]:
            continue

        if actual == destino:
            # Reconstruir camino
            camino = []
            nodo = destino

            while nodo is not None:
                camino.append(nodo)
                nodo = padre[nodo]
            camino.reverse()
            return dist[destino[0]][destino[1]], camino

        for df, dc in movimientos:

            #se calculan los vecinos y se verifica que estén dentro del mapa y no sean obstáculos
            vecino_fila, vecino_columna = actual[0] + df, actual[1] + dc
            if 0 <= vecino_fila < filas and 0 <= vecino_columna < cols and matriz[vecino_fila][vecino_columna] != 0:
                nuevo_costo = costo_actual + 1

                if nuevo_costo < dist[vecino_fila][vecino_columna]:
                    dist[vecino_fila][vecino_columna] = nuevo_costo
                    padre[(vecino_fila, vecino_columna)] = actual
                    heapq.heappush(heap, (nuevo_costo, (vecino_fila, vecino_columna)))

    return float('inf'), []  # no hay camino



def precalcular_distancias(matriz, puntos):
    """
    Corre Dijkstra entre cada par de puntos y guarda
    la distancia y el camino real.

    Se guardan todas las distancias para que el algoritmo Greedy pueda determinar
    cual es el siguiente destino más cercano sin tener que recalcular caminos cada vez.
    
    Entradas:
        - matriz: mapa (0=obstáculo, 1=camino, 2=inicio, 3=estación)
        - puntos: lista de tuplas (fila, col) de los puntos de entrega y base

    salidas:
        - distancias[i][j]: pasos de puntos[i] a puntos[j]
        - caminos[i][j]: lista de celdas del camino de i a j
    """
    n = len(puntos)
    distancias = [[0] * n for _ in range(n)]
    caminos = [[[] for _ in range(n)] for _ in range(n)]

    for i in range(n):
        for j in range(n):
            if i != j:
                dist, camino = dijkstra(matriz, puntos[i], puntos[j])
                distancias[i][j] = dist
                caminos[i][j] = camino

    return distancias, caminos



def nearest_neighbor(distancias, num_destinos):
    """
    Algoritmo Greedy Nearest Neighbor para el orden de visita.

    Entradas:
        - distancias: matriz precomputada de distancias entre puntos
        - num_destinos: número de estaciones a visitar (sin contar la base)    
    
    Salidas:
        - orden: lista de índices en el orden de visita.
    """
    visitado = [False] * (num_destinos + 1)
    visitado[0] = True
    orden = [0]

    for _ in range(num_destinos):
        actual = orden[-1]
        mejor_dist = float('inf')
        mejor_siguiente = -1

        for j in range(1, num_destinos + 1):
            if not visitado[j] and distancias[actual][j] < mejor_dist:
                mejor_dist = distancias[actual][j]
                mejor_siguiente = j

        if mejor_siguiente == -1:
            # si no existe un camino al destino se omite en el orden de visita
            break

        visitado[mejor_siguiente] = True
        orden.append(mejor_siguiente)
    orden.append(0)  # retorno obligatorio a la base
    
    return orden


def construir_camino_completo(orden, caminos):
    """
    Genera el camino completo del robot a travez de todas las estaciones en una sola lista

    Entradas:
    - orden: lista de índices en el orden de visita (incluye la base al inicio y al final)
    - caminos: matriz precomputada de caminos entre puntos

    Salidas:
    - camino_total: lista que contiene todas las celdas del recorrido completo
    """
    camino_total = []

    for k in range(len(orden) - 1):
        segmento = caminos[orden[k]][orden[k + 1]]

        if not segmento:
            print(f"Error: no hay camino entre índice {orden[k]} y {orden[k+1]}")
            return []

        if camino_total:
            camino_total += segmento[1:]
        else:
            camino_total += segmento

    return camino_total



def mostrar_resultado(puntos, orden, camino_total):

    print("\n orden de visita:")
    distancia_total = 0
    
    for k in range(len(orden) - 1):
        
        indice_origen = orden[k]
        indice_destino = orden[k + 1]

        nombre_origen = "BASE" if indice_origen == 0 else f"Estación {puntos[indice_origen]}"

        if indice_destino == 0:
            nombre_destino = "BASE"
        else:
            nombre_destino = f"Estación {puntos[indice_destino]}"

        print(f"  {nombre_origen}  -> {nombre_destino}")

    print(f"Total de celdas en el camino  : {len(camino_total)}")

    print("\nCAMINO CELDA A CELDA:")
    print(camino_total)

    print("\nINSTRUCCIONES PARA ROBOT:")
    print(traducir_ruta_a_instrucciones(camino_total))
    print("________________________________________________________")


def aplicar_greedy(matriz_mapa, inicio, paquetes):
    """
    Planifica el recorrido de entrega usando:
        - Dijkstra para calcular caminos reales entre puntos
        - Nearest Neighbor (Greedy) para decidir el orden de visita

    Entradas:
        - matriz: mapa como lista de listas (0=obstáculo)
        - inicio: tupla (fila, col) de la base del robot
        - paquetes: lista de dicts: {id, peso, destino, prioridad}

    Salidas:
        - orden_coordenadas: lista de coordenadas en el orden de visita
        - camino_total: lista de celdas del recorrido completo
    """


    print("________________________________________________________")
    print("          RESULTADO — ALGORITMO GREEDY")
    print("   (Nearest Neighbor + Dijkstra para caminos)")
    print("________________________________________________________")

    if not paquetes:
        print("No hay paquetes para entregar.")
        return [], []

    destinos = [p['destino'] for p in paquetes]
    puntos = [inicio] + destinos  # índice 0 siempre es la base

    # precomputar distancias y caminos reales con Dijkstra
    matriz_distancias, matriz_caminos = precalcular_distancias(matriz_mapa, puntos)

    # Verificar que todos los destinos sean accesibles
    inaccesibles = [puntos[i] for i in range(1, len(puntos)) if matriz_distancias[0][i] == float('inf')]
    if inaccesibles:
        print(f"Error: la estación {inaccesibles} no es accesible por lo que se omitirán las entregas a esta estación.")
    if len(inaccesibles) == len(destinos):
        print("Error: ninguna estación es accesible. No se pueden planificar entregas.")
        return [], []
        
    # decidir el orden con Nearest Neighbor
    orden_indices = nearest_neighbor(matriz_distancias, len(destinos))

    # construir el camino completo concatenando segmentos
    camino_total = construir_camino_completo(orden_indices, matriz_caminos)


    # Mostrar resultados en pantalla
    mostrar_resultado(puntos, orden_indices, camino_total)

    orden_coordenadas = [puntos[i] for i in orden_indices]
    return orden_coordenadas, camino_total



if __name__ == "__main__":

    matriz, inicio, estaciones = cargar_y_convertir_mapa("mapas/tablero.json")


    # Usamos estaciones reales del mapa
    paquetes_prueba = [
        {"id": "P01", "peso": 7,  "destino": estaciones[0], "prioridad": 10},
        {"id": "P02", "peso": 5,  "destino": estaciones[1], "prioridad": 8},
        {"id": "P03", "peso": 2,  "destino": estaciones[2], "prioridad": 5},
    ]

    orden, camino = aplicar_greedy(matriz, inicio, paquetes_prueba)
