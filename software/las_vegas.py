import random
from lector import construir_grafo_navegacion
from backtracking import traducir_ruta_a_instrucciones

def algoritmo_las_vegas_grafo(grafo, inicio, destino, max_intentos=1000):
    """
    Implementar Las Vegas mediante caminata aleatoria con reinicios.
    Si el robot se encierra aborta el intento y vuelve a empezar desde el origen.
    """
    intento_actual = 0
    
    while intento_actual < max_intentos:
        ruta = [inicio]
        visitados = {inicio}
        actual = inicio
        pasos_en_este_intento = 0
        
        # Limite de pasos para evitar que se quede dando vueltas infinitas en espacios abiertos
        while actual != destino and pasos_en_este_intento < 500:
            # Consultar los vecinos seguros
            vecinos_con_peso = grafo.get(actual, [])
            nodos_siguientes = [v[0] for v in vecinos_con_peso]
            
            # Filtrar solo los nodos por los que no hemos pasado en este intento
            opciones = [v for v in nodos_siguientes if v not in visitados]
            
            if not opciones:
                # callejon sin salida asi que rompemos este ciclo para reiniciar
                break 
                
            
            actual = random.choice(opciones)
            ruta.append(actual)
            visitados.add(actual)
            pasos_en_este_intento += 1
            
        if actual == destino:
            return ruta 
            
        intento_actual += 1
        
    return None  # Si agotamos los intentos sin encontrar una ruta


def resolver_tramo_las_vegas(grafo, inicio, destino, etiqueta):
    """
    Gestionar la ejecucion del tramo probabilistico y su traduccion a instrucciones.
    """
    print(f"\n--- ANALIZANDO TRAMO {etiqueta} ---")
    print(f"Origen {inicio} -> Destino {destino}")
    
    ruta_aleatoria = algoritmo_las_vegas_grafo(grafo, inicio, destino)
    
    if ruta_aleatoria:
        instrucciones = traducir_ruta_a_instrucciones(ruta_aleatoria)
        print(f"Ruta generada por azar {ruta_aleatoria}")
        print(f"Instrucciones de Hardware {instrucciones}")
        return ruta_aleatoria
    else:
        print(f"Error Critico Agotados 1000 intentos para llegar a {destino}")
        return None


def ejecutar_viaje_completo_las_vegas(grafo, punto_inicio, lista_paquetes):
    """
    Gestionar la secuencia total de logistica desde la base hacia los paquetes y de vuelta.
    """
    print(" EJECUCION DE ALGORITMO LAS VEGAS")

    ubicacion_actual = punto_inicio
    
    for paquete in lista_paquetes:
        destino = paquete["destino"]
        id_pkg = paquete["id"]
        
        resultado = resolver_tramo_las_vegas(grafo, ubicacion_actual, destino, f"ENTREGA {id_pkg}")
        
        if resultado:
            ubicacion_actual = destino
        else:
            print(f" Fallo en entrega {id_pkg}")
            return

    print("\nFINALIZANDO ENTREGAS - RETORNANDO A LA BASE")

    resolver_tramo_las_vegas(grafo, ubicacion_actual, punto_inicio, "RETORNO A ORIGEN")

if __name__ == "__main__":
    mapa_simulado = [
        [2, 1, 1, 1, 1, 1, 1, 1, 1, 3], 
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1], 
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1], 
        [1, 3, 1, 1, 1, 1, 1, 1, 1, 3]  
    ]
    
    grafo = construir_grafo_navegacion(mapa_simulado)
    
    paquetes_viaje = [
        {"id": "P01", "destino": (0, 9)},
        {"id": "P02", "destino": (4, 1)}
    ]
    
    ejecutar_viaje_completo_las_vegas(grafo, (0, 0), paquetes_viaje)
