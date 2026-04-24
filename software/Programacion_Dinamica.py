from collections import deque
from lector import cargar_y_convertir_mapa, construir_grafo_navegacion

def bfs(inicio, objetivo, grafo):
    cola = deque([(inicio, [inicio])])
    visitados = set([inicio])

    while cola:
        nodo, camino = cola.popleft()

        if nodo == objetivo:
            return camino

        for vecino, _ in grafo.get(nodo, []):
            if vecino not in visitados:
                visitados.add(vecino)
                cola.append((vecino, camino + [vecino]))

    return None

def calcular_distancias(nodos, grafo):
    dist = {}
    caminos = {}

    for i in nodos:
        for j in nodos:
            if i != j:
                camino = bfs(i, j, grafo)
                
                if camino is not None:
                    dist[(i, j)] = len(camino)
                    caminos[(i, j)] = camino

    return dist, caminos

def tsp_dp_ruta(nodos, dist):
    n = len(nodos)
    memo = {}
    siguiente_nodo = {}

    def dp(pos, visitados):
        if visitados == (1 << n) - 1:
            return 0

        if (pos, visitados) in memo:
            return memo[(pos, visitados)]

        mejor = float('inf')
        mejor_sig = None

        for sig in range(n):
            if not (visitados & (1 << sig)):
                nodo_actual = nodos[pos]
                nodo_sig = nodos[sig]

                if (nodo_actual, nodo_sig) in dist:
                    costo = dist[(nodo_actual, nodo_sig)] + dp(
                        sig,
                        visitados | (1 << sig)
                    )

                    if costo < mejor:
                        mejor = costo
                        mejor_sig = sig

        memo[(pos, visitados)] = mejor
        siguiente_nodo[(pos, visitados)] = mejor_sig
        return mejor

    costo_total = dp(0, 1)

    # reconstruir ruta
    ruta = []
    visitados = 1
    pos = 0

    while True:
        sig = siguiente_nodo.get((pos, visitados))
        if sig is None:
            break

        ruta.append(nodos[sig])
        visitados |= (1 << sig)
        pos = sig

    return costo_total, ruta

def construir_ruta_completa(base, orden, caminos):
    ruta_total = []
    actual = base

    for destino in orden:
        tramo = caminos[(actual, destino)]

        if ruta_total:
            ruta_total += tramo[1:]
        else:
            ruta_total += tramo

        actual = destino

    # limpiar repeticiones consecutivas
    ruta_limpia = [ruta_total[0]]
    for nodo in ruta_total[1:]:
        if nodo != ruta_limpia[-1]:
            ruta_limpia.append(nodo)

    return ruta_limpia

def ruta_a_movimientos(ruta):
    movimientos = []

    for i in range(len(ruta) - 1):
        x1, y1 = ruta[i]
        x2, y2 = ruta[i+1]

        if x2 == x1 and y2 == y1 + 1:
            movimientos.append("DERECHA")
        elif x2 == x1 and y2 == y1 - 1:
            movimientos.append("IZQUIERDA")
        elif x2 == x1 + 1 and y2 == y1:
            movimientos.append("ABAJO")
        elif x2 == x1 - 1 and y2 == y1:
            movimientos.append("ARRIBA")

    return movimientos

def resolver_ruta_dinamica(matriz, inicio, destino):
    from lector import construir_grafo_navegacion
    
    grafo = construir_grafo_navegacion(matriz)

    # usar BFS directamente (porque es 1 destino)
    ruta = bfs(inicio, destino, grafo)

    return ruta

if __name__ == "__main__":
    mapa, base, estaciones = cargar_y_convertir_mapa("mapas/tablero.json")

    grafo = construir_grafo_navegacion(mapa)

    # FILTRAR estaciones
    estaciones_validas = []
    for est in estaciones:
        if bfs(base, est, grafo) is not None:
            estaciones_validas.append(est)

    # NODOS
    nodos = [base] + estaciones_validas
    
    # DISTANCIAS
    dist, caminos = calcular_distancias(nodos, grafo)    

    costo, orden = tsp_dp_ruta(nodos, dist)

    ruta_completa = construir_ruta_completa(base, orden, caminos)

    movimientos = ruta_a_movimientos(ruta_completa)
    
    print("Costo mínimo:", costo)
    print("Orden de estaciones:", orden)
    print("Ruta completa:", ruta_completa)
    print("Movimientos:", movimientos)