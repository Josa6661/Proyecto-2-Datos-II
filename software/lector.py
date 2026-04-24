import json

def cargar_y_convertir_mapa(ruta_archivo):
    """
    Función que carga un archivo JSON y lo convierte en una matriz para representar el mapa.
    """
    
    # Leer el archivo como texto crudo (sin intentar entender el JSON todavía)
    with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
        texto_crudo = archivo.read()
    
    # Reemplaza las palabras sin comillas por palabras con comillas
    texto_arreglado = texto_crudo.replace(':Inicio', ':"Inicio"')
    texto_arreglado = texto_arreglado.replace(':Camino', ':"Camino"')
    texto_arreglado = texto_arreglado.replace(':Estacion', ':"Estacion"')
    
    # Convertir el texto arreglado a una lista de diccionarios Python
    datos = json.loads(texto_arreglado)
    
    # Averiguar el tamaño máximo del tablero para crear la matriz
    max_fila = max(item['fila'] for item in datos)
    max_col = max(item['columna'] for item in datos)
    
    # Crear la matriz llena de ceros (0 = Obstáculo)
    matriz = [[0 for _ in range(max_col)] for _ in range(max_fila)]
    
    inicio = None
    estaciones = []
    
    # Llenar la matriz con los datos
    for celda in datos:
        f = celda['fila'] - 1
        c = celda['columna'] - 1
        valor = celda['valor']
        
        if valor == "Camino":
            matriz[f][c] = 1
        elif valor == "Inicio":
            matriz[f][c] = 2
            inicio = (f, c)
        elif valor == "Estacion":
            matriz[f][c] = 3
            estaciones.append((f, c))
            
    print(f"Mapa de ({max_fila} filas x {max_col} columnas)")
    print(f"Coordenada de inicio: {inicio}")
    print(f"Total de estaciones: {len(estaciones)}")
    print(estaciones)
    
    return matriz, inicio, estaciones

def construir_grafo_navegacion(matriz):
    """
    Función que construye un grafo de navegación a partir de una matriz.
    """
    
    grafo = {}
    filas = len(matriz)
    columnas = len(matriz[0])
    movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for f in range(filas):
        for c in range(columnas):
            if matriz[f][c] != 0:
                vecinos = []
                for df, dc in movimientos:
                    nf = f + df
                    nc = c + dc
                    if 0 <= nf < filas and 0 <= nc < columnas and matriz[nf][nc] != 0:
                        vecinos.append(((nf, nc), 1))
                grafo[(f, c)] = vecinos
                
    return grafo

# Prueba
if __name__ == "__main__":
    ruta_archivo = "mapas/tablero.json"
    
    matriz_final, punto_inicio, lista_estaciones = cargar_y_convertir_mapa(ruta_archivo)
    grafo_mapa = construir_grafo_navegacion(matriz_final)
    
    print("\nPrimeras 5 filas de la matriz")
    for fila in matriz_final[:5]:
        print(fila)
        
    print("\nPrueba del Grafo en el Punto de Inicio", punto_inicio)
    print("Vecinos libres para caminar", grafo_mapa[punto_inicio])
        