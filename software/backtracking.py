from lector import construir_grafo_navegacion

def traducir_ruta_a_instrucciones(ruta_coordenadas):
    """
    Función que traduce una lista de coordenadas (ruta) a instrucciones de movimiento para el robot.
    """ 
    if not ruta_coordenadas or len(ruta_coordenadas) < 2:
        return "No hay ruta valida o ya estas en el destino"

    instrucciones = []
    direccion_actual = None
    contador_pasos = 0

    for i in range(1, len(ruta_coordenadas)): # Empiezaz desde el segundo punto para comparar con el anterior
        fila_anterior, col_anterior = ruta_coordenadas[i-1]
        fila_actual, col_actual = ruta_coordenadas[i]

        if fila_actual > fila_anterior:
            nueva_direccion = "abajo"
        elif fila_actual < fila_anterior:
            nueva_direccion = "arriba"
        elif col_actual > col_anterior:
            nueva_direccion = "derecha"
        elif col_actual < col_anterior:
            nueva_direccion = "izquierda"
        else:
            continue

        if nueva_direccion == direccion_actual:
            contador_pasos += 1
        else:
            if direccion_actual is not None:
                instrucciones.append(f"{contador_pasos} {direccion_actual}")
            direccion_actual = nueva_direccion
            contador_pasos = 1

    if direccion_actual is not None:
        instrucciones.append(f"{contador_pasos} {direccion_actual}")

    return ", ".join(instrucciones) + " (llega a estacion)"


def buscar_ruta_optima_backtracking(grafo, inicio, destino):
    """
    Función que utiliza backtracking para encontrar la ruta más corta entre dos puntos en un grafo.
    """
    mejor_ruta = [None]
    min_costo = [float('inf')]

    def dfs(actual, visitados, camino_actual, costo_actual):
        """
        Función recursiva que explora todas las rutas posibles desde el nodo actual hasta el destino.
        """
        # Si el costo actual ya supera el mejor encontrado, no seguimos explorando esta rama
        if costo_actual >= min_costo[0]:
            return

        if actual == destino: # Si llegamos al destino, verificamos si es la mejor ruta encontrada
            mejor_ruta[0] = list(camino_actual)
            min_costo[0] = costo_actual
            return

        # Desempaquetamos el vecino y su peso
        vecinos = grafo.get(actual, [])
        for siguiente, peso in vecinos:
            if siguiente not in visitados:
                visitados.add(siguiente)
                camino_actual.append(siguiente)
                
                dfs(siguiente, visitados, camino_actual, costo_actual + peso)
                
                camino_actual.pop() # removemos el nodo del camino actual
                visitados.remove(siguiente) # marcamos el nodo como no visitado para otras ramas

    dfs(inicio, {inicio}, [inicio], 0)
    return mejor_ruta[0]


def resolver_ruta_y_traducir(grafo, inicio, destino):
    """
    Función que resuelve la ruta óptima utilizando backtracking y traduce la ruta a instrucciones para el robot.
    """
    
    print(f"\nCALCULANDO RUTA OPTIMA CON BACKTRACKING HACIA {destino}...")
    ruta_coordenadas = buscar_ruta_optima_backtracking(grafo, inicio, destino)
    
    if ruta_coordenadas:
        print("Mejor ruta encontrada ", ruta_coordenadas)
        instrucciones_robot = traducir_ruta_a_instrucciones(ruta_coordenadas)
        print("Instrucciones para el hardware ", instrucciones_robot)
        return instrucciones_robot
    else:
        print("Error No se encontro ningun camino posible")
        return None


# Prueba local
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
        {"id": "P02", "destino": (4, 1)}, 
        {"id": "P03", "destino": (4, 9)}  
    ]
    
    print("PRUEBA DE BACKTRACKING EXHAUSTIVO CON GRAFOS")
    posicion_actual = (0, 0)
    
    for paquete in paquetes_viaje:
        destino = paquete["destino"]
        print(f"\n--- Calculando tramo hacia {paquete['id']} en {destino} ---")
        
        instrucciones = resolver_ruta_y_traducir(grafo_prueba, posicion_actual, destino)
        if instrucciones:
            posicion_actual = destino