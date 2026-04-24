from collections import deque
from lector import construir_grafo_navegacion
from backtracking import traducir_ruta_a_instrucciones

def suavizar_ruta(ruta_original):
    """
    Recibe una ruta con posibles ciclos y retornar una ruta limpia y directa.
    """
    if not ruta_original:
        return []
        
    ruta_limpia = []
    indice = 0
    
    while indice < len(ruta_original):
        actual = ruta_original[indice]
        ruta_limpia.append(actual)
        
        ultimo_indice = len(ruta_original) - 1
        
        # Buscar desde el final hacia atras para encontrar el bucle mas grande posible
        while ultimo_indice > indice:
            if ruta_original[ultimo_indice] == actual:
                # Omitir el tramo ciclico adelantando el indice principal
                indice = ultimo_indice
                break
            ultimo_indice -= 1
            
        indice += 1
        
    return ruta_limpia


def buscar_ruta_corta_bfs(grafo, inicio, destino):
    """
    Ejecuta busqueda en anchura (BFS) para resolver tramos cortos.
    """
    cola = deque([(inicio, [inicio])])
    visitados = {inicio}
    
    while cola:
        actual, camino = cola.popleft()
        
        if actual == destino:
            return camino
            
        # Extraer el vecino y el peso de la tupla proporcionada por el grafo
        for vecino, peso in grafo.get(actual, []):
            if vecino not in visitados:
                visitados.add(vecino)
                cola.append((vecino, camino + [vecino]))
    return []


def encontrar_punto_control_seguro(grafo, inicio, destino):
    """
    Calcula el punto medio geometrico entre dos coordenadas.
    Retorna el nodo transitable mas cercano en caso de colision con un obstaculo.
    """
    mitad_fila = (inicio[0] + destino[0]) // 2
    mitad_columna = (inicio[1] + destino[1]) // 2
    
    # Retornar la coordenada directamente si la mitad exacta es transitable
    if (mitad_fila, mitad_columna) in grafo:
        return (mitad_fila, mitad_columna)
        
    mejor_nodo = None
    distancia_minima = float('inf')
    
    # Evaluar nodos mediante distancia Manhattan para encontrar la alternativa optima
    for nodo in grafo.keys():
        distancia = abs(nodo[0] - mitad_fila) + abs(nodo[1] - mitad_columna)
        if distancia < distancia_minima:
            distancia_minima = distancia
            mejor_nodo = nodo
            
    return mejor_nodo


def buscar_ruta_divide_y_venceras(grafo, inicio, destino, profundidad=0):
    """
    Aplica particionamiento espacial para dividir la ruta principal en sub-rutas.
    Resuelve recursivamente hasta alcanzar el caso base.
    """
    if inicio == destino:
        return [inicio]
        
    distancia_manhattan = abs(inicio[0] - destino[0]) + abs(inicio[1] - destino[1])
    
    # Prevenir sobrecarga de recursion en casos de rutas muy cortas o profundidades excesivas
    if distancia_manhattan <= 2 or profundidad > 4:
        return buscar_ruta_corta_bfs(grafo, inicio, destino)
        
    punto_control = encontrar_punto_control_seguro(grafo, inicio, destino)
    
    # Evitar particiones triviales que no aportan valor y pueden generar ciclos innecesarios
    if punto_control == inicio or punto_control == destino:
        return buscar_ruta_corta_bfs(grafo, inicio, destino)
        
    # Resolver sub-problemas de manera recursiva
    mitad_izquierda = buscar_ruta_divide_y_venceras(grafo, inicio, punto_control, profundidad + 1)
    mitad_derecha = buscar_ruta_divide_y_venceras(grafo, punto_control, destino, profundidad + 1)
    
    # Unir las sub-rutas omitiendo la duplicacion del nodo central
    if mitad_izquierda and mitad_derecha:
        return mitad_izquierda + mitad_derecha[1:]
        
    # En caso de que alguna de las mitades no sea resoluble, intentar resolver la ruta completa sin dividir
    return buscar_ruta_corta_bfs(grafo, inicio, destino)


def resolver_ruta_divide(grafo, inicio, destino):
    """
    Función principal para resolver la ruta utilizando el enfoque de divide y vencerás.
    Incluye pasos de suavizado para eliminar ciclos y generar instrucciones de navegación claras.
    """
    print(f"\n--- CALCULANDO RUTA DIVIDE Y VENCERAS HACIA {destino} ---")
    
    ruta_cruda = buscar_ruta_divide_y_venceras(grafo, inicio, destino)
    print("Ruta original con posibles vueltas: ", ruta_cruda)
    
    ruta_final = suavizar_ruta(ruta_cruda)
    print("Ruta pasada por el suavizador: ", ruta_final)
    
    if ruta_final:
        instrucciones = traducir_ruta_a_instrucciones(ruta_final)
        print("Instrucciones de navegacion: ", instrucciones)
        return instrucciones
        
    print("Error: Mapa bloqueado o ruta inaccesible.")
    return None


# Bloque de prueba unitaria
if __name__ == "__main__":
    mapa_prueba = [
        [2, 1, 1, 1, 1, 1, 1, 1, 1, 3], 
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
        [1, 3, 1, 1, 1, 1, 1, 1, 1, 3]  
    ]
    
    grafo_prueba = construir_grafo_navegacion(mapa_prueba)
    
    paquetes_viaje = [
        {"id": "P01", "destino": (0, 9)},
        {"id": "P02", "destino": (4, 1)}
    ]
    
    posicion_actual = (0, 0)
    
    for paquete in paquetes_viaje:
        instrucciones = resolver_ruta_divide(grafo_prueba, posicion_actual, paquete["destino"])
        if instrucciones:
            posicion_actual = paquete["destino"]