def traducir_ruta_a_instrucciones(ruta_coordenadas): 
    if not ruta_coordenadas or len(ruta_coordenadas) < 2:
        return "No hay ruta valida o ya estas en el destino."

    instrucciones = []
    direccion_actual = None
    contador_pasos = 0

    for i in range(1, len(ruta_coordenadas)):
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


def buscar_ruta_backtracking(matriz, actual, destino, visitados=None):
    ### print(f" Casilla actual: {actual}") // para ver todo el proceso de busqueda
    
    if visitados is None:
        visitados = set()

    fila, col = actual
    filas_mapa = len(matriz)
    cols_mapa = len(matriz[0])

    # Condicion de exito si se llega al destino
    if actual == destino:
        return [actual]

    # Condiciones de fallo si se sale del mapa, choca con un 0, o ya pasamos por ahi
    if (fila < 0 or fila >= filas_mapa or 
        col < 0 or col >= cols_mapa or 
        matriz[fila][col] == 0 or 
        actual in visitados):
        return None

    # Marcar la celda actual como visitada
    visitados.add(actual)

    # Se da prioridad a moverse hacia la derecha y abajo
    movimientos = [
        (fila + 1, col), # Abajo
        (fila, col + 1), # Derecha
        (fila - 1, col), # Arriba
        (fila, col - 1)  # Izquierda
    ]
    
    for siguiente in movimientos:
        ruta = buscar_ruta_backtracking(matriz, siguiente, destino, visitados)
        if ruta:
            return [actual] + ruta

    # Si ningun camino sirvio, desmarcamos y retrocedemos
    visitados.remove(actual)
    return None


def resolver_ruta_y_traducir(matriz, inicio, destino):
    print(f"\nCALCULANDO RUTA CON BACKTRACKING HACIA {destino}...")
    ruta_coordenadas = buscar_ruta_backtracking(matriz, inicio, destino)
    
    if ruta_coordenadas:
        print("Ruta de coordenadas encontrada:", ruta_coordenadas)
        instrucciones_robot = traducir_ruta_a_instrucciones(ruta_coordenadas)
        print("Instrucciones para el hardware:", instrucciones_robot)
        return instrucciones_robot
    else:
        print("Error: No se encontro ningun camino posible esquivando los obstaculos.")
        return None


# Prueba
if __name__ == "__main__":
    
    mapa_prueba = [
        [2, 1, 1, 1, 1, 1, 1, 1, 1, 3], 
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
        [1, 3, 1, 1, 1, 1, 1, 1, 1, 3]  
    ]
    
    paquetes_viaje = [
        {"id": "P01", "destino": (0, 9)},
        {"id": "P02", "destino": (4, 1)}, 
        {"id": "P03", "destino": (4, 9)}  
    ]
    
    print("PRUEBA DE BACKTRACKING")
    
    posicion_actual = (0, 0)
    
    for paquete in paquetes_viaje:
        destino = paquete["destino"]
        print(f"\n--- Calculando tramo hacia {paquete['id']} en {destino} ---")
        
        instrucciones = resolver_ruta_y_traducir(mapa_prueba, posicion_actual, destino)
        
        if instrucciones:
            posicion_actual = destino
        else:
            print(f"Error: Estacion {destino} bloqueada.")