import sys
from lector import cargar_y_convertir_mapa, construir_grafo_navegacion
from backtracking import buscar_ruta_optima_backtracking, traducir_ruta_a_instrucciones
from divide_y_venceras import buscar_ruta_divide_y_venceras, suavizar_ruta
from las_vegas import algoritmo_las_vegas_grafo
from greedy import dijkstra, definir_orden_prioridad
from mochila import resolver_mochila_dinamica, resolver_mochila_greedy
from Programacion_Dinamica import resolver_ruta_dinamica
from monte_carlo import monte_carlo_ruta

def solicitar_un_paquete(estaciones_validas):
    """Configurar un solo paquete con validaciones estrictas"""
    print("\n" + "-"*40)
    print(" CONFIGURACIÓN DE PAQUETE ÚNICO")
    print("-" * 40)
    
    while True:
        id_paquete = input("\nID del paquete: ").strip()
        if id_paquete: 
            break
        print("Error: El ID no puede estar vacío.")
    
    while True:
        try:
            peso = int(input("Peso (Máximo 20kg): "))
            if 0 < peso <= 20: 
                break
            print("Error: El peso debe ser mayor a 0 y no puede exceder los 20kg.")
        except ValueError:
            print("Error: Ingrese un número entero.")
            
    print(f"\nEstaciones válidas en el mapa: {estaciones_validas}")
    while True:
        try:
            fila = int(input("Fila del destino: "))
            col = int(input("Columna del destino: "))
            destino = (fila, col)
            if destino in estaciones_validas:
                break
            print("Error: Esa coordenada no es una estación válida.")
        except ValueError:
            print("Error: Ingrese números enteros.")
            
    return {"id": id_paquete, "peso": peso, "destino": destino}


def solicitar_multiples_paquetes(estaciones_validas):
    """Configurar bodega con validación de peso, prioridad e IDs"""
    print("\n" + "-"*40)
    print(" CONFIGURACIÓN DE BODEGA")
    print("-" * 40)
    
    while True:
        try:
            max_entregas = int(input("Máximo de entregas permitidas por viaje: "))
            if max_entregas > 0: break
            print("Error: Debe ser un número mayor a 0.")
        except ValueError:
            print("Error: Ingrese un número entero.")

    paquetes = []
    while True:
        print(f"\n--- Paquete #{len(paquetes)+1} ---")
        print(f"Estaciones válidas: {estaciones_validas}")
        
        id_p = input("ID del paquete: ").strip()
        if not id_p:
            print("Error: El ID no puede estar vacío.")
            continue
            
        if any(p["id"] == id_p for p in paquetes):
            print("Error: Ya registraste un paquete con ese ID.")
            continue
        
        while True:
            try:
                peso = int(input("Peso (Máximo 20kg): "))
                if 0 < peso <= 20: break
                print("Error: Cada paquete debe pesar entre 1kg y 20kg.")
            except ValueError:
                print("Error: Ingrese un número entero.")
        
        while True:
            try:
                prioridad = int(input("Prioridad (1-10): "))
                if 1 <= prioridad <= 10: break
                print("Error: La prioridad debe ser un número del 1 al 10.")
            except ValueError:
                print("Error: Ingrese un número entero.")
        
        while True:
            try:
                f = int(input("Fila del destino: "))
                c = int(input("Columna del destino: "))
                dest = (f, c)
                if dest in estaciones_validas: break
                print("Error: Coordenada inválida. Revise la lista de estaciones.")
            except ValueError:
                print("Error: Ingrese números enteros.")
            
        paquetes.append({"id": id_p, "peso": peso, "prioridad": prioridad, "destino": dest})
        
        while True:
            respuesta = input("\n¿Agregar otro paquete? (s/n): ").lower()
            if respuesta in ['s', 'n']: break
            print("Error: Ingrese solo 's' o 'n'.")
            
        if respuesta == 'n':
            break
            
    return max_entregas, paquetes

def ejecutar_navegacion(nombre, grafo, matriz, inicio, destino, id_t):
    """Ejecuta el algoritmo y muestra ruta/instrucciones"""
    ruta = None
    if id_t == "1": ruta = resolver_ruta_dinamica(matriz, inicio, destino)
    elif id_t == "2": print("[Módulo Algoritmos Genéticos Pendiente]")
    elif id_t == "3": _, ruta = dijkstra(matriz, inicio, destino)
    elif id_t == "4": ruta = buscar_ruta_optima_backtracking(grafo, inicio, destino)
    elif id_t == "5":
        ruta_c = buscar_ruta_divide_y_venceras(grafo, inicio, destino)
        ruta = suavizar_ruta(ruta_c)
    elif id_t == "6": ruta = algoritmo_las_vegas_grafo(grafo, inicio, destino)
    elif id_t == "7": ruta = monte_carlo_ruta(grafo, inicio, destino)

    if ruta:
        print(f"\nRuta ({nombre}): {ruta}")
        print(f"Instrucciones: {traducir_ruta_a_instrucciones(ruta)}")
    return ruta


def menu_navegacion(grafo, matriz, inicio, estaciones):
    pkg = solicitar_un_paquete(estaciones)
    dest = pkg["destino"]
    
    while True:
        print("\n" + "="*40)
        print(f" TÉCNICAS DE NAVEGACIÓN (Paquete: {pkg['id']})")
        print("="*40)
        print("1. Programacion dinamica")
        print("2. Algoritmos Genéticos")
        print("3. Greedy")
        print("4. Backtracking")
        print("5. Divide y Vencerás")
        print("6. Probabilistico: Las Vegas")
        print("7. Probabilistico: Monte Carlo")
        print("0. Volver")
        
        op = input("\nSeleccione técnica: ")
        nombres = ["", "Programacion dinamica", "Algoritmos Genéticos", "Greedy", 
                   "Backtracking", "Divide y Vencerás", "Probabilistico: Las Vegas", "Probabilistico: Monte Carlo"]
        
        if op == "0": break
        if "1" <= op <= "7":
            print(f"\n>>> IDA: BASE -> {dest}")
            ejecutar_navegacion(nombres[int(op)], grafo, matriz, inicio, dest, op)
            print(f"\n>>> VUELTA: {dest} -> BASE")
            ejecutar_navegacion(nombres[int(op)], grafo, matriz, dest, inicio, op)
            input("\nPresione Enter para continuar...")
        else:
            print("Opción inválida.")


def menu_mochila(grafo, matriz, inicio, estaciones):
    max_e, bodega = solicitar_multiples_paquetes(estaciones)
    
    while True:
        print("\n" + "="*40)
        print(" EVALUACIÓN DE MOCHILA")
        print("="*40)
        print("1. Programacion dinamica")
        print("2. Greedy")
        print("0. Volver")
        
        op = input("\nOpción: ")
        if op == "0": break
        
        if op == "1":
            ganancia, seleccionados = resolver_mochila_dinamica(bodega, 20, max_e)
            print("\n--- RESULTADO: Programacion dinamica ---")
        elif op == "2":
            ganancia, seleccionados = resolver_mochila_greedy(bodega, 20, max_e)
            print("\n--- RESULTADO: Greedy ---")
        else: 
            print("Opción inválida.")
            continue
            
        print(f"Paquetes: {[p['id'] for p in seleccionados]} | Prioridad total: {ganancia}")
        
        # Secuencia y Ejecución de Rutas (Aquí se calcula el camino físico real)
        orden = definir_orden_prioridad([inicio] + [p['destino'] for p in seleccionados])
        
        print("\n>>> EJECUTANDO RUTA DE LOGÍSTICA (Navegación tramo por tramo)")
        actual = inicio
        for i in range(1, len(orden)):
            destino_t = orden[i]
            print(f"\nTramo {i}: {actual} -> {destino_t}")
            ejecutar_navegacion("Greedy (Dijkstra)", grafo, matriz, actual, destino_t, "3") # Usa Greedy por defecto para mover el robot
            actual = destino_t
        input("\nPresione Enter para continuar...")


def main():
    ruta_mapa = "mapas/tablero.json"
    matriz, inicio, estaciones = cargar_y_convertir_mapa(ruta_mapa)
    grafo = construir_grafo_navegacion(matriz)
    
    while True:
        print("\n" + "*"*50)
        print(" SISTEMA LOGÍSTICO TEC")
        print("*"*50)
        print("1. Ejecutar las técnicas (1 Paquete)")
        print("2. Ejecutar la Mochila (Múltiples Paquetes)")
        print("0. Salir")
        
        op = input("\nSeleccione: ")
        if op == "1": menu_navegacion(grafo, matriz, inicio, estaciones)
        elif op == "2": menu_mochila(grafo, matriz, inicio, estaciones)
        elif op == "0": sys.exit()
        else: print("Opción inválida.")

if __name__ == "__main__":
    main()