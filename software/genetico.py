import random
from lector import cargar_y_convertir_mapa
from greedy import dijkstra
from backtracking import traducir_ruta_a_instrucciones


"""
En este archivo se implementa el algoritmo genético para planificar el recorrido del robot.

El algoritmo genético optimiza el orden de visita de las estaciones.
Dijkstra calcula el camino real entre cada par de puntos.

Se utiliza un diccionario para almacenar los resultados de Dijkstra entre pares de puntos
 evitando cálculos repetidos y mejorando la eficiencia.
"""
diccionario_dijkstra = {}

def calcular_fitness(individuo, matriz, inicio):
    """
    Calcula la distancia total de una ruta.
    entre menor sea la distancia, mayor es el fitness.

    Entradas:
        - individuo: lista de tuplas (fila, col) que representa el orden de visita
        - matriz: mapa como lista de listas (0=obstáculo)
        - inicio: tupla (fila, col) de la base del robot

    Salidas:
        - distancia_total (el fitness): suma de las distancias entre puntos consecutivos
    """
    ruta = [inicio] + individuo + [inicio]
    distancia_total = 0

    for i in range(len(ruta) - 1):
        if (ruta[i], ruta[i+1]) in diccionario_dijkstra:
            dist, _ = diccionario_dijkstra[(ruta[i], ruta[i+1])]
        else:
            dist, _ = dijkstra(matriz, ruta[i], ruta[i+1])
            diccionario_dijkstra[(ruta[i], ruta[i+1])] = (dist, _)

        distancia_total += dist

    return distancia_total


def crear_poblacion(destinos, tamano):
    """
    crea una poblacion de individuos inicial (de rutas) aleatoria a partir de los destinos.
    Entradas:
        - destinos: lista de tuplas (fila, col) de las estaciones a visitar
        - tamano: número de individuos en la población
    Salidas:
        - poblacion: lista de individuos (rutas) aleatorias

    """
    def crear_individuo(destinos):
        """
        Crea un individuo aleatorio (una ruta) a partir de los destinos.
        """
        individuo = destinos[:]
        random.shuffle(individuo)
        return individuo
    
    poblacion = []
    for _ in range(tamano):
        poblacion.append(crear_individuo(destinos))
    return poblacion


def seleccionar_padre(poblacion, matriz, inicio):
    """
    toma una muestra aleatoria de la población y devuelve el individuo con mejor fitness (menor distancia total).
    Entradas:
        - poblacion: lista de individuos (rutas) a seleccionar
        - matriz: mapa como lista de listas (0=obstáculo)
        - inicio: tupla (fila, col) de la base del robot
    Salidas:
        - mejor: individuo con mejor fitness (menor distancia total) de la muestra
    """
    torneo = random.sample(poblacion, 3)
    mejor = torneo[0]

    for individuo in torneo:
        if calcular_fitness(individuo, matriz, inicio) < calcular_fitness(mejor, matriz, inicio):
            mejor = individuo

    return mejor


def cruzar(padre1, padre2):
    """
    toma dos padres y genera un hijo combinando partes de ambos.
    Se selecciona un segmento aleatorio del padre1 y se copia al hijo.
    """
    tamaño = len(padre1)
    a, b = sorted(random.sample(range(tamaño), 2))

    hijo = [None] * tamaño

    for i in range(a, b):
        hijo[i] = padre1[i]

    pos = 0
    for gen in padre2:
        if gen not in hijo:
            while hijo[pos] is not None:
                pos += 1
            hijo[pos] = gen

    return hijo


def mutar(individuo, probabilidad=0.1):
    """
    toma el individuo y con cierta probabilidad, le hace una variacion aleatoria (intercambio de dos destinos).
    """
    if random.random() < probabilidad:
        i, j = random.sample(range(len(individuo)), 2)
        individuo[i], individuo[j] = individuo[j], individuo[i]




def construir_camino_completo(inicio,orden, matriz_mapa):
    """
    Genera el camino completo del robot a travez de todas las estaciones en una sola lista

    Entradas:
    - inicio: tupla (fila, col) de la base del robot
    - orden: lista de tuplas (fila, col) en el orden de visita
    - matriz_mapa: matriz del mapa para calcular caminos entre puntos usando Dijkstra

    Salidas:
    - camino_total: lista que contiene todas las celdas del recorrido completo
    """
    camino_total = []
    orden = [inicio] + orden + [inicio]  
    posicion_actual = orden[0]

    for k in range(1, len(orden)):

        tramo = diccionario_dijkstra.get((posicion_actual, orden[k]))
        if tramo is None:
            tramo = dijkstra(matriz_mapa, posicion_actual, orden[k])
            diccionario_dijkstra[(posicion_actual, orden[k])] = tramo

        x, camino = tramo

        if not camino:
            print(f"Error: no hay camino entre {posicion_actual} y {orden[k]}, se omite.")
            continue

        if camino_total:
            camino_total += camino[1:]
        else:
            camino_total += camino

        posicion_actual = orden[k]

    return camino_total

def obtener_destinos_accesibles(inicio, destinos, matriz_mapa):
    """
    Verifica qué destinos son accesibles desde el inicio utilizando Dijkstra y devuelve una lista de destinos accesibles.

    Entradas:
    - inicio: tupla (fila, col) de la base del robot
    - destinos: lista de tuplas (fila, col) de las estaciones a visitar
    - matriz_mapa: matriz del mapa para calcular caminos entre puntos usando Dijkstra

    Salidas:
    - destinos_accesibles: lista de tuplas (fila, col) de estaciones que son accesibles desde el inicio
    """
    destinos_accesibles = []
    for destino in destinos:
        dist, _ = dijkstra(matriz_mapa, inicio, destino)
        diccionario_dijkstra[(inicio, destino)] = (dist, _)

        if dist == float('inf'):
            print(f"Advertencia: estación {destino} no es accesible desde {inicio}.")
        else:
            destinos_accesibles.append(destino)

    return destinos_accesibles

def aplicar_genetico(matriz_mapa, inicio, paquetes):
    """
    Planifica el recorrido usando:
        - Algoritmo genético para el orden óptimo de visita
        - Dijkstra para el camino real entre cada par de puntos

    Entradas:
        - matriz   : mapa como lista de listas (0=obstáculo)
        - inicio   : tupla (fila, col) de la base del robot
        - paquetes : lista de dicts {id, peso, destino, ...}

    Salidas:
        - camino_total  : lista de celdas del recorrido completo
        - cantidad_pasos: total de pasos
    """

    print("________________________________________________________")
    print("         RESULTADO — ALGORITMO GENÉTICO")
    print("________________________________________________________")

    if not paquetes:
        print("No hay paquetes.")
        return [], 0

    destinos = [p["destino"] for p in paquetes]

    if len(destinos) < 2:
        #si no hay elementos suficientes para aplicar el algoritmo genético, se construye el camino directo
        camino_total = construir_camino_completo(inicio, destinos, matriz_mapa)
        print("\nCamino total:")
        print(camino_total)

        print("\nInstrucciones totales:")
        print(traducir_ruta_a_instrucciones(camino_total))

        if len(camino_total) > 1:
            cantidad_pasos = len(camino_total) - 1 
            print(f"\nTotal de pasos: {cantidad_pasos}")
        else:
            cantidad_pasos = 0
            print(f"\nTotal de pasos: 0 (El robot no pudo moverse)")

        return camino_total, cantidad_pasos

    destinos_accesibles = obtener_destinos_accesibles(inicio, destinos, matriz_mapa)

    if not destinos_accesibles:
        print("Error: ninguna estación es accesible desde la base.")
        return [], 0

    else:

        n=len(destinos_accesibles)
        if n <= 3:
            generaciones = 5
            tam_poblacion = 5
        else:
            generaciones = 20
            tam_poblacion = 20

        destinos = destinos_accesibles

        poblacion = crear_poblacion(destinos, tam_poblacion)

        for _ in range(generaciones):
            nueva_poblacion = []

            for _ in range(tam_poblacion):
                padre1 = seleccionar_padre(poblacion, matriz_mapa, inicio)
                padre2 = seleccionar_padre(poblacion, matriz_mapa, inicio)

                hijo = cruzar(padre1, padre2)
                mutar(hijo)

                nueva_poblacion.append(hijo)
            poblacion = nueva_poblacion

        mejor = poblacion[0]

        for individuo in poblacion:
            if calcular_fitness(individuo, matriz_mapa, inicio) < calcular_fitness(mejor, matriz_mapa, inicio):
                mejor = individuo

        camino_total = construir_camino_completo(inicio, mejor, matriz_mapa)

    print("\nCamino total:")
    print(camino_total)

    print("\nInstrucciones totales:")
    print(traducir_ruta_a_instrucciones(camino_total))

    if len(camino_total) > 1:
        cantidad_pasos = len(camino_total) - 1 
        print(f"\nTotal de pasos: {cantidad_pasos}")
    else:
        cantidad_pasos = 0
        print(f"\nTotal de pasos: 0 (El robot no pudo moverse)")

    return camino_total, cantidad_pasos


if __name__ == "__main__":
    matriz, inicio, estaciones = cargar_y_convertir_mapa("mapas/tablero.json")
    paquetes_prueba = [
        {"id": "P02", "peso": 5, "destino": estaciones[1]},
        {"id": "P03", "peso": 2, "destino": estaciones[2]},
        {"id": "P04", "peso": 2, "destino": estaciones[3]},
        {"id": "P05", "peso": 3, "destino": estaciones[4]},
        {"id": "P06", "peso": 2, "destino": estaciones[5]},
        {"id": "P07", "peso": 2, "destino": estaciones[6]},
        {"id": "P08", "peso": 3, "destino": estaciones[7]}
    ]
    aplicar_genetico(matriz, inicio, paquetes_prueba)