import random

def algoritmo_las_vegas(matriz, inicio, destino, max_intentos=1000):
    
    def obtener_vecinos(pos):
        f, c = pos
        vecinos = []
        # Movimientos: Arriba, Abajo, Izquierda, Derecha
        movimientos = [(f-1, c), (f+1, c), (f, c-1), (f, c+1)]
        
        for nf, nc in movimientos:
            if 0 <= nf < len(matriz) and 0 <= nc < len(matriz[0]):
                # Puede pasar por Caminos (1), Inicio (2) o Estaciones (3)
                if matriz[nf][nc] in [1, 2, 3]:
                    vecinos.append((nf, nc))
        return vecinos

    intento_actual = 0
    while intento_actual < max_intentos:
        ruta = [inicio]
        visitados = {inicio}
        actual = inicio
        
        pasos_en_este_intento = 0
        while actual != destino and pasos_en_este_intento < 500:
            vecinos = obtener_vecinos(actual)
            opciones = [v for v in vecinos if v not in visitados]
            
            if not opciones:
                break # Se quedó atrapado, reiniciar intento
            
            # Decisión probabilística: elige un camino al azar
            actual = random.choice(opciones)
            ruta.append(actual)
            visitados.add(actual)
            pasos_en_este_intento += 1
        
        if actual == destino:
            return ruta 
        
        intento_actual += 1
    
    return None 
if __name__ == "__main__":
    
    # 2=Inicio, 1=Camino, 3=Estación, 0=Obstáculo
    mapa_multientrega = [
        [2, 1, 1, 0, 0, 0],
        [0, 1, 1, 1, 1, 0],
        [0, 3, 1, 0, 1, 0], # Estación A en (2, 1)
        [0, 1, 0, 0, 1, 0],
        [0, 1, 1, 1, 3, 0], # Estación B en (4, 4)
        [0, 0, 0, 0, 0, 0]
    ]

    inicio_robot = (0, 0)
    
  
    paquetes_del_viaje = [
        {"id": "PAQ-01", "destino": (2, 1)},
        {"id": "PAQ-02", "destino": (4, 4)}
    ]

    print("=== INICIANDO PRUEBA DE ENTREGA (LAS VEGAS):")
    punto_actual = inicio_robot
    ruta_total_del_viaje = []

    for i, paquete in enumerate(paquetes_del_viaje):
        dest = paquete["destino"]
        print(f"\nCalculando tramo {i+1}: Desde {punto_actual} hasta {paquete['id']} en {dest}")
        
        ruta_tramo = algoritmo_las_vegas(mapa_multientrega, punto_actual, dest)
        
        if ruta_tramo:
            print(f"-> Ruta encontrada: {ruta_tramo}")
            # Guardamos la ruta (evitando repetir el punto donde termina uno y empieza el otro)
            if not ruta_total_del_viaje:
                ruta_total_del_viaje.extend(ruta_tramo)
            else:
                ruta_total_del_viaje.extend(ruta_tramo[1:])
            
            # Actualizamos la posición para el siguiente paquete
            punto_actual = dest
        else:
            print(f"-> ERROR: No se pudo encontrar ruta al paquete {paquete['id']}")
            break

    print("\n" + "="*50)
    print(f"RESUMEN DE LA RUTA TOTAL DEL VIAJE:")
    print(ruta_total_del_viaje)
    print(f"Total de celdas recorridas: {len(ruta_total_del_viaje)}")
    
    # Dibujar mapa final con la ruta marcada
    print("\nVisualización del recorrido (R = Ruta):")
    for f, fila in enumerate(mapa_multientrega):
        print(" ".join([" R " if (f, c) in ruta_total_del_viaje else " # " if v==0 else " . " for c, v in enumerate(fila)]))

