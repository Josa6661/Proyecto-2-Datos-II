# Importamos deque para usar una cola eficiente en BFS
from collections import deque

# Importamos funciones para cargar el mapa y construir el grafo
from lector import cargar_y_convertir_mapa, construir_grafo_navegacion


# --- ALGORITMO DE BÚSQUEDA ---
def bfs(inicio, objetivo, grafo):
    # Cola para BFS: guarda tuplas (nodo_actual, camino_recorrido)
    cola = deque([(inicio, [inicio])])
    
    # Conjunto de nodos visitados para evitar ciclos
    visitados = set([inicio])

    # Mientras haya nodos por explorar
    while cola:
        # Sacamos el primer elemento de la cola (FIFO)
        nodo, camino = cola.popleft()

        # Si llegamos al objetivo, devolvemos el camino completo
        if nodo == objetivo:
            return camino

        # Recorremos los vecinos del nodo actual
        for vecino, _ in grafo.get(nodo, []):  # grafo.get evita error si no hay vecinos
            if vecino not in visitados:
                visitados.add(vecino)  # Marcamos como visitado
                
                # Agregamos a la cola el vecino con el camino actualizado
                cola.append((vecino, camino + [vecino]))

    # Si no se encuentra camino, devolvemos None
    return None


def calcular_distancias(nodos, grafo):
    """
    Calcula todas las distancias y caminos posibles entre cada par de puntos clave
    (Base y Estaciones). Esto crea una matriz de distancias simplificada.
    """
    
    dist = {}      # Diccionario para guardar distancias entre nodos
    caminos = {}   # Diccionario para guardar los caminos completos

    # Recorremos cada par de nodos
    for i in nodos:
        for j in nodos:
            if i != j:
                # Usamos BFS para encontrar el camino más corto
                camino = bfs(i, j, grafo)
                
                # Si existe un camino
                if camino is not None:
                    dist[(i, j)] = len(camino) # Guardamos la longitud del camino
                    caminos[(i, j)] = camino   # Guardamos el camino completo

    return dist, caminos


# --- OPTIMIZACIÓN DE RUTA (Traveling Salesman Problem) ---
def tsp_dp_ruta(nodos, dist):
    """
    Resuelve el problema del viajero usando Programación Dinámica.
    Busca el orden de visita que minimice el costo total.
    """
    
    n = len(nodos)  # Cantidad de nodos

    memo = {}             # Guarda resultados ya calculados (memorización)
    siguiente_nodo = {}   # Guarda decisiones para reconstruir la ruta

    def dp(pos, visitados): 
        # Caso base: si todos los nodos han sido visitados
        if visitados == (1 << n) - 1:
            return 0

        # Si ya se calculó este estado, lo retornamos
        if (pos, visitados) in memo:
            return memo[(pos, visitados)]

        mejor = float('inf')  # Inicializamos el mejor costo en infinito
        mejor_sig = None      # Mejor siguiente nodo

        # Probamos todos los posibles siguientes nodos
        for sig in range(n):
            # Verificamos si el nodo 'sig' no ha sido visitado
            if not (visitados & (1 << sig)):
                nodo_actual = nodos[pos]
                nodo_sig = nodos[sig]

                # Verificamos que exista camino entre los nodos
                if (nodo_actual, nodo_sig) in dist:
                    # Calculamos el costo total recursivamente
                    costo = dist[(nodo_actual, nodo_sig)] + dp(
                        sig,
                        visitados | (1 << sig)  # Marcamos nodo como visitado
                    )

                    # Si encontramos un mejor costo, lo guardamos
                    if costo < mejor:
                        mejor = costo
                        mejor_sig = sig

        # Guardamos el resultado en memo
        memo[(pos, visitados)] = mejor
        
        # Guardamos la decisión para reconstruir la ruta
        siguiente_nodo[(pos, visitados)] = mejor_sig
        
        return mejor

    # Iniciamos desde la base (posición 0) con solo ese nodo visitado
    costo_total = dp(0, 1)

    # --- reconstruir ruta ---
    ruta = []
    visitados = 1
    pos = 0

    # Reconstruimos la ruta usando las decisiones guardadas
    while True:
        sig = siguiente_nodo.get((pos, visitados))
        if sig is None:
            break

        ruta.append(nodos[sig])
        visitados |= (1 << sig)  # Marcamos como visitado
        pos = sig

    return costo_total, ruta


# --- ENSAMBLADO DE RUTA ---
def construir_ruta_completa(base, orden, caminos):
    # Lista donde se almacenará la ruta completa
    ruta_total = []
    
    # Comenzamos desde la base
    actual = base

    # Recorremos el orden óptimo de estaciones
    for destino in orden:
        # Obtenemos el camino entre el nodo actual y el destino
        tramo = caminos[(actual, destino)]

        # Evitamos duplicar el nodo donde se conectan los tramos
        if ruta_total:
            ruta_total += tramo[1:]
        else:
            ruta_total += tramo

        actual = destino

    # Limpiar repeticiones consecutivas
    ruta_limpia = [ruta_total[0]]
    for nodo in ruta_total[1:]:
        if nodo != ruta_limpia[-1]:
            ruta_limpia.append(nodo)

    return ruta_limpia


# --- CONVERSIÓN A COMANDOS ---
def ruta_a_movimientos(ruta):
    """
    Convierte una lista de coordenadas (x, y) en comandos de dirección 
    legibles para el robot.
    """
    
    movimientos = []

    # Recorremos la ruta comparando cada par de puntos consecutivos
    for i in range(len(ruta) - 1):
        x1, y1 = ruta[i]
        x2, y2 = ruta[i+1]

        # Determinamos la dirección según el cambio de coordenadas
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
    """
    Función de utilidad para encontrar un camino simple entre dos puntos
    sin pasar por múltiples estaciones.
    """
    
    # Importamos aquí por si se usa de forma independiente
    from lector import construir_grafo_navegacion
    
    # Construimos el grafo a partir de la matriz
    grafo = construir_grafo_navegacion(matriz)

    # Usamos BFS porque es el camino más corto en grafos sin peso
    ruta = bfs(inicio, destino, grafo)

    return ruta


# --- EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    
    # Cargamos el mapa desde el archivo JSON
    mapa, base, estaciones = cargar_y_convertir_mapa("mapas/tablero.json")

    # Construimos el grafo de navegación
    grafo = construir_grafo_navegacion(mapa)

    # FILTRAR estaciones accesibles (que sí tienen camino)
    estaciones_validas = []
    for est in estaciones:
        if bfs(base, est, grafo) is not None:
            estaciones_validas.append(est)

    # NODOS = base + estaciones válidas
    nodos = [base] + estaciones_validas
    
    # Calculamos distancias y caminos entre todos los nodos
    dist, caminos = calcular_distancias(nodos, grafo)    

    # Aplicamos programación dinámica (TSP)
    costo, orden = tsp_dp_ruta(nodos, dist)

    # Construimos la ruta completa real
    ruta_completa = construir_ruta_completa(base, orden, caminos)

    # Convertimos la ruta en movimientos
    movimientos = ruta_a_movimientos(ruta_completa)
    
    # Mostramos resultados
    print("Costo mínimo:", costo)
    print("Orden de estaciones:", orden)
    print("Ruta completa:", ruta_completa)
    print("Movimientos:", movimientos)