import random

def monte_carlo_ruta(grafo, inicio, destino, iteraciones=3000):
    """
    Ejecuta múltiples simulaciones de caminos aleatorios y aproxima 
    la solución óptima guardando la ruta más corta encontrada
    """
    
    mejor_ruta = None
    mejor_longitud = float('inf')

    for _ in range(iteraciones): 
        actual = inicio
        ruta = [actual]

        pasos = 0
        max_pasos = 1000

        while actual != destino and pasos < max_pasos:
            vecinos = [v for v, _ in grafo.get(actual, [])] # Obtener solo los nodos vecinos sin considerar el peso

            if not vecinos: # Si no hay vecinos, es un callejón sin salida, así que abandonamos esta ruta
                break

            if len(ruta) > 1 and len(vecinos) > 1: # Evitar volver al nodo anterior a menos que sea la única opción
                opciones_avance = [n for n in vecinos if n != ruta[-2]]
                if opciones_avance: 
                    siguiente = random.choice(opciones_avance) # Elegir aleatoriamente entre las opciones que no son el nodo anterior
                else:
                    siguiente = random.choice(vecinos) # Si no hay opciones de avance, entonces sí podemos volver al nodo anterior
            else:
                siguiente = random.choice(vecinos) # Elegir aleatoriamente entre los vecinos

            ruta.append(siguiente)
            actual = siguiente
            pasos += 1

        if actual == destino: # Si llegamos al destino, evaluamos si esta ruta es la mejor encontrada
            if len(ruta) < mejor_longitud: # Si esta ruta es más corta que la mejor encontrada hasta ahora, la guardamos
                mejor_ruta = ruta 
                mejor_longitud = len(ruta) # Actualizamos la longitud de la mejor ruta encontrada

    return mejor_ruta