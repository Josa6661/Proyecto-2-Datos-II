import heapq
from lector import cargar_y_convertir_mapa
from backtracking import  traducir_ruta_a_instrucciones
import math

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


def definir_orden_prioridad(puntos):
    """
    Calcula el orden de visita de las estaciones usando la heurística de la distancia entre cada estación
    (aplica nearest neightbor)

    Entradas:
        - puntos: lista de tuplas (fila, col) de la base y estaciones
    Salidas:
        - orden: lista de tuplas (fila, col) en el orden de visita
    """
    punto_actual = puntos[0]
    destinos = puntos[1:]
    orden = [punto_actual]  # empezamos en la base

    for i in range(len(destinos)):
        distancia_menor = float('inf')
        mejor_destino = None

        for j in range(len(destinos)):
            deltax = abs(punto_actual[0] - destinos[j][0])
            deltay = abs(punto_actual[1] - destinos[j][1])
            distancia_actual = math.sqrt((deltax ** 2) + (deltay ** 2))

            if distancia_actual < distancia_menor:
                mejor_destino = destinos[j]
                distancia_menor = distancia_actual

        orden.append(mejor_destino)
        destinos.remove(mejor_destino)
        punto_actual = mejor_destino

    orden.append(puntos[0])  # volvera la base al final
    return orden


    
def construir_ruta_completa(orden, matriz_mapa):
    """
    Genera el camino completo del robot a travez de todas las estaciones en una sola lista

    Entradas:
    - orden: lista de tuplas (fila, col) en el orden de visita
    - matriz_mapa: matriz del mapa para calcular caminos entre puntos usando Dijkstra

    Salidas:
    - camino_total: lista que contiene todas las celdas del recorrido completo
    """
    camino_total = []
    posicion_actual = orden[0]

    for k in range(1, len(orden)):
        x, camino = dijkstra(matriz_mapa, posicion_actual, orden[k])

        if not camino:
            print(f"Error: no hay camino entre {posicion_actual} y {orden[k]}, se omite.")
            continue
        print(f"Camino entre {posicion_actual} y {orden[k]}:\n {camino} (pasos: {x})")
        
        print("instrucciones:")
        print(traducir_ruta_a_instrucciones(camino)+"\n")

        if camino_total:
            camino_total += camino[1:]
        else:
            camino_total += camino

        posicion_actual = orden[k]

    return camino_total


def mostrar_resultado(camino_total):

    print(f"Total de pasos: {len(camino_total)}")
    print("\nCamino celda a celda total:")
    print(camino_total)
    print("\nInstrucciones para robot:")
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

    orden= definir_orden_prioridad(puntos)
    camino_total = construir_ruta_completa(orden, matriz_mapa)

    # Mostrar resultados en pantalla
    mostrar_resultado(camino_total)
    cantidad_pasos= len(camino_total)
    return camino_total, cantidad_pasos


#Prueba
if __name__ == "__main__":

    matriz, inicio, estaciones = cargar_y_convertir_mapa("mapas/tablero.json")
    paquetes_prueba = [
        {"id": "P01", "peso": 7, "destino": estaciones[0], "prioridad": 10},
        {"id": "P02", "peso": 5, "destino": estaciones[1], "prioridad": 8},
        {"id": "P03", "peso": 2, "destino": estaciones[2], "prioridad": 5},
    ]

    orden, camino = aplicar_greedy(matriz, inicio, paquetes_prueba)
