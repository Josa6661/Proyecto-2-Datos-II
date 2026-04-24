import random

def monte_carlo_ruta(grafo, inicio, destino, iteraciones=3000):
    mejor_ruta = None
    mejor_longitud = float('inf')

    for _ in range(iteraciones):
        actual = inicio
        ruta = [actual]

        pasos = 0
        max_pasos = 1000

        while actual != destino and pasos < max_pasos:
            vecinos = [v for v, _ in grafo.get(actual, [])]

            if not vecinos:
                break

            siguiente = random.choice(vecinos)

            ruta.append(siguiente)
            actual = siguiente
            pasos += 1

        if actual == destino:
            if len(ruta) < mejor_longitud:
                mejor_ruta = ruta
                mejor_longitud = len(ruta)

    return mejor_ruta