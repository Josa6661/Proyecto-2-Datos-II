def validar_datos(entregas, capacidad_maxima, max_entregas):
    # Revisar que no haya pesos o capacidades negativas
    if capacidad_maxima <= 0 or max_entregas <= 0:
        print("Error El peso y la cantidad maxima de entregas deben ser mayores a 0")
        return False
        
    for paquete in entregas:
        if paquete["peso"] <= 0 or paquete["prioridad"] <= 0:
            print(f"Error El paquete {paquete['id']} tiene valores invalidos")
            return False
            
    return True

def resolver_mochila_dinamica(entregas, capacidad_maxima=20, max_entregas=2):
    if not validar_datos(entregas, capacidad_maxima, max_entregas):
        return 0, []

    n = len(entregas)
    
    # Matriz 3D: dp[i][w][c] = prioridad maxima usando los primeros i paquetes, con capacidad w y max c entregas
    dp = [[[0 for _ in range(max_entregas + 1)] for _ in range(capacidad_maxima + 1)] for _ in range(n + 1)]

    # Evaluar si vale mas la pena llevar o dejar cada paquete
    for i in range(1, n + 1):
        peso = entregas[i-1]["peso"]
        prioridad = entregas[i-1]["prioridad"]

        for w in range(capacidad_maxima + 1):
            for c in range(1, max_entregas + 1):
                if peso <= w:
                    # Compara dejarlo vs llevarlo (restando su peso y restando 1 al espacio de cajas)
                    dp[i][w][c] = max(dp[i-1][w][c], dp[i-1][w - peso][c - 1] + prioridad)
                else:
                    # Si no cabe por peso, se deja
                    dp[i][w][c] = dp[i-1][w][c]

    # Leer el cubo de reversa para sacar los paquetes elegidos
    paquetes_elegidos = []
    w = capacidad_maxima
    c = max_entregas
    
    for i in range(n, 0, -1): 
        if dp[i][w][c] != dp[i-1][w][c]:
            paquetes_elegidos.append(entregas[i-1])
            w -= entregas[i-1]["peso"]
            c -= 1 

    return dp[n][capacidad_maxima][max_entregas], paquetes_elegidos


def resolver_mochila_greedy(entregas, capacidad_maxima=20, max_entregas=2):
    if not validar_datos(entregas, capacidad_maxima, max_entregas):
        return 0, []

    # Ordenar la lista buscando los que den mas puntos por cada kilo
    entregas_ordenadas = sorted(
        entregas,
        key=lambda x: x["prioridad"] / x["peso"],
        reverse=True
    )

    peso_actual = 0
    prioridad_total = 0
    paquetes_elegidos = []

    # Llenar la mochila hasta que ya no quepa por peso o por limite de entregas
    for paquete in entregas_ordenadas:
        if peso_actual + paquete["peso"] <= capacidad_maxima and len(paquetes_elegidos) < max_entregas:
            paquetes_elegidos.append(paquete)
            peso_actual += paquete["peso"]
            prioridad_total += paquete["prioridad"]

    return prioridad_total, paquetes_elegidos


# Prueba
if __name__ == "__main__":
    lista_paquetes = [
        {"id": "P01", "peso": 11, "destino": (1, 6), "prioridad": 2},
        {"id": "P02",  "peso": 10, "destino": (8, 7), "prioridad": 10},
        {"id": "P03",  "peso": 10, "destino": (4, 10), "prioridad": 5},
        {"id": "P04", "peso": 4,  "destino": (19, 2), "prioridad": 1},
        {"id": "P05", "peso": 5,  "destino": (13, 7), "prioridad": 4},
        {"id": "P06",  "peso": 2,  "destino": (3, 3), "prioridad": 1}
    ]
    
    # limite de entregas por viaje
    limite_entregas = 2
    
    print(f"EVALUACION DE CARGA (Maximo {limite_entregas} paquetes)")
    
    total_dinamica, elegidos_dinamica = resolver_mochila_dinamica(lista_paquetes, 20, limite_entregas)
    print("RESULTADOS PROGRAMACION DINAMICA")
    print(f"Prioridad Maxima {total_dinamica}")
    print("Paquetes", [p["id"] for p in elegidos_dinamica])
    
    total_greedy, elegidos_greedy = resolver_mochila_greedy(lista_paquetes, 20, limite_entregas)
    print("RESULTADOS GREEDY")
    print(f"Prioridad Maxima {total_greedy}")
    print("Paquetes", [p["id"] for p in elegidos_greedy])