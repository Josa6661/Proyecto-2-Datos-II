from lector import cargar_y_convertir_mapa
from mochila import resolver_mochila_dinamica

def configurar_y_solicitar_entregas(lista_estaciones_validas):
    
    print("SISTEMA DE GESTION DEL ROBOT")

    while True:
        max_entregas_str = input("Ingrese el maximo de entregas permitidas por viaje: ")
        try:
            max_entregas = int(max_entregas_str)
            break
        except ValueError:
            print("Error Solo se permiten numeros enteros")

    if max_entregas <= 0:
        print("Ajustando maximo de entregas a 1 por defecto")
        max_entregas = 1

    paquetes_ingresados = []
    ingresando_datos = True

    print("\nREGISTRO DE PAQUETES")
    print("Estaciones validas en el mapa:", lista_estaciones_validas)

    while ingresando_datos:
        print("\n--- Nuevo Paquete ---")
        id_paquete = input("ID de la entrega: ").strip()

        if id_paquete == "":
            print("Error El ID no puede estar vacio")
            continue

        id_repetido = False
        for paquete in paquetes_ingresados:
            if paquete["id"] == id_paquete:
                id_repetido = True
                break

        if id_repetido:
            print("Error Ya existe una entrega con ese ID")
            continue

        try:
            peso = int(input("Peso en kilos: "))
        except ValueError:
            print("Error Solo se permiten numeros enteros")
            continue

        if peso <= 0:
            print("Error El peso debe ser mayor a cero")
            continue

        while True:
            try:
                prioridad = int(input("Prioridad (escala del 1 al 10, 1=min, 10=max): "))
                if prioridad < 1 or prioridad > 10:
                    print("Error La prioridad debe estar entre 1 y 10")
                    continue
                break
            except ValueError:
                print("Error Solo se permiten numeros enteros")

        try:
            fila = int(input("Fila del destino: "))
            col = int(input("Columna del destino: "))
        except ValueError:
            print("Error Solo se permiten numeros enteros")
            continue

        destino_usuario = (fila, col)

        if destino_usuario not in lista_estaciones_validas:
            print("Error Esa coordenada no es una estacion valida en el mapa")
            continue

        nuevo_paquete = {
            "id": id_paquete,
            "peso": peso,
            "destino": destino_usuario,
            "prioridad": prioridad
        }

        paquetes_ingresados.append(nuevo_paquete)
        print(f"Paquete {id_paquete} registrado con exito")

        while True:
            respuesta = input("Desea ingresar otro paquete? (s/n): ")
            if respuesta.lower() == 's' or respuesta.lower() == 'n':
                break
            print("Error Responda solo con s o n")

        if respuesta.lower() != 's':
            ingresando_datos = False

    return max_entregas, paquetes_ingresados

def ejecutar_sistema():
    ruta_mapa = "mapas/tablero.json"
    matriz, inicio, estaciones_validas = cargar_y_convertir_mapa(ruta_mapa)
    
    limite_entregas, paquetes_pendientes = configurar_y_solicitar_entregas(estaciones_validas)
    
    print("\nRESUMEN DE ENTREGAS")
    print(f"Total de paquetes registrados: {len(paquetes_pendientes)}")
    peso_total = sum(p["peso"] for p in paquetes_pendientes)
    print(f"Peso total: {peso_total} kilos")
    print(f"Maximo de entregas permitidas: {limite_entregas}")
    
    numero_viaje = 1
    
    print("\nPROCESANDO RUTA CON PROGRAMACION DINAMICA...")
    
    while len(paquetes_pendientes) > 0:
        print(f"\n--- PLANIFICANDO VIAJE #{numero_viaje} ---")
    
        ganancia, paquetes_para_el_viaje = resolver_mochila_dinamica(paquetes_pendientes, 20, limite_entregas)
        
        if len(paquetes_para_el_viaje) == 0:
            print("Alerta: Los paquetes restantes son demasiado pesados para la capacidad del robot (20kg).")
            print("Paquetes varados:", [p['id'] for p in paquetes_pendientes])
            break
        
        print(f"El robot cargara {len(paquetes_para_el_viaje)} paquetes en este recorrido")
        print("Paquetes seleccionados:")
        for p in paquetes_para_el_viaje:
            print(f"- {p['id']} hacia destino {p['destino']} (Prioridad: {p['prioridad']}, Peso: {p['peso']}kg)")
        
        ids_seleccionados = [p['id'] for p in paquetes_para_el_viaje]
        paquetes_pendientes = [p for p in paquetes_pendientes if p['id'] not in ids_seleccionados]
        
        numero_viaje += 1
        
    print("\nLa logistica de carga ha finalizado")
        
if __name__ == "__main__":
    ejecutar_sistema()