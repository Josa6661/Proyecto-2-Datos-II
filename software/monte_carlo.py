import random  # Se utiliza para seleccionar movimientos aleatorios

def monte_carlo_ruta(grafo, inicio, destino, iteraciones=3000):
    """
    Ejecuta múltiples simulaciones de caminos aleatorios y aproxima 
    la solución óptima guardando la ruta más corta encontrada
    """
    
    mejor_ruta = None  # Aquí se guardará la mejor ruta encontrada
    mejor_longitud = float('inf')  # Inicializamos con infinito para comparar longitudes

    # Repetimos el proceso muchas veces (simulación Monte Carlo)
    for _ in range(iteraciones): 
        actual = inicio  # Comenzamos desde el nodo inicial
        ruta = [actual]  # Guardamos la ruta recorrida

        pasos = 0  # Contador de pasos realizados en esta simulación
        max_pasos = 1000  # Límite para evitar bucles infinitos

        # Mientras no lleguemos al destino y no superemos el límite de pasos
        while actual != destino and pasos < max_pasos:
            
            # Obtener solo los nodos vecinos (ignorando el peso del grafo)
            vecinos = [v for v, _ in grafo.get(actual, [])]

            # Si no hay vecinos, estamos en un callejón sin salida
            if not vecinos:
                break  # Terminamos esta simulación

            # Si hay más de un nodo en la ruta y más de una opción de movimiento
            if len(ruta) > 1 and len(vecinos) > 1:
                
                # Evitamos regresar al nodo anterior (retroceder)
                opciones_avance = [n for n in vecinos if n != ruta[-2]]
                
                if opciones_avance:
                    # Elegimos aleatoriamente entre las opciones que avanzan
                    siguiente = random.choice(opciones_avance)
                else:
                    # Si no hay otra opción, permitimos retroceder
                    siguiente = random.choice(vecinos)
            else:
                # Si solo hay una opción o estamos al inicio, elegimos cualquier vecino
                siguiente = random.choice(vecinos)

            # Agregamos el siguiente nodo a la ruta
            ruta.append(siguiente)
            
            # Nos movemos al siguiente nodo
            actual = siguiente
            
            # Aumentamos el contador de pasos
            pasos += 1

        # Si llegamos al destino, evaluamos si esta es la mejor ruta
        if actual == destino:
            
            # Si esta ruta es más corta que la mejor encontrada
            if len(ruta) < mejor_longitud:
                mejor_ruta = ruta  # Guardamos la nueva mejor ruta
                mejor_longitud = len(ruta)  # Actualizamos la longitud mínima

    # Retornamos la mejor ruta encontrada (o None si no encontró ninguna)
    return mejor_ruta