import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import io, sys
import time
import urllib.request
import urllib.parse
import socket

from lector import cargar_y_convertir_mapa, construir_grafo_navegacion
from main import ejecutar_navegacion, solicitar_multiples_paquetes
from mochila import resolver_mochila_dinamica, resolver_mochila_greedy
from greedy import definir_orden_prioridad
from genetico import aplicar_genetico
from backtracking import traducir_para_esp32

# Memoria para guardar las rutas antes de enviarlas al ESP32
rutas_pendientes_nav = []
rutas_pendientes_mochila = []
IP_ESP32_GLOBAL = "192.168.50.243"
# ---------------- CARGA INICIAL ----------------
ruta_mapa = 'mapas/tablero.json'
matriz, inicio, estaciones = cargar_y_convertir_mapa(ruta_mapa)
grafo = construir_grafo_navegacion(matriz)

# ---------------- UTILIDADES ----------------
def capturar_salida(func):
    """Ejecuta una función y captura todo lo que imprime en consola, devolviéndolo como string."""
    buffer = io.StringIO()
    viejo = sys.stdout 
    sys.stdout = buffer
    try:
        func()
    finally:
        sys.stdout = viejo
    return buffer.getvalue()


def ejecutar_comparacion_nav(paquete, peso, destino):
    """Ejecuta todos los algoritmos de navegación para un mismo paquete y muestra resultados comparativos."""
    comparaciones = [
        ('1 - Programación Dinámica', '1'),
        ('2 - Algoritmos Genéticos', '2'),
        ('3 - Greedy', '3'),
        ('4 - Backtracking', '4'),
        ('5 - Divide y Vencerás', '5'),
        ('6 - Las Vegas', '6'),
        ('7 - Monte Carlo', '7'),
    ]

    resultados = []
    print('=' * 50)
    print('COMPARACIÓN DE ALGORITMOS DE NAVEGACIÓN')
    print('=' * 50)
    print('Paquete:', paquete)
    print('Peso:', peso, 'kg')
    print('Destino:', destino)
    print()

    for nombre, id_alg in comparaciones:
        inicio_t = time.perf_counter()
        salida = ''
        pasos = None

        if id_alg == '2':
            paquete_dict = {'id': paquete, 'peso': peso, 'destino': destino}
            resultado = {}

            def ejecutar_genetico(): # Ejecutamos el genético y guardamos su resultado en un dict para luego mostrarlo
                resultado['ruta'], resultado['pasos'] = aplicar_genetico(matriz, inicio, [paquete_dict])

            salida = capturar_salida(ejecutar_genetico)
            pasos = resultado.get('pasos')
        else:
            resultado = {}

            def ejecutar_ruta(): # Ejecutamos la ruta de ida y vuelta para los algoritmos tradicionales y guardamos resultados en un dict
                ruta_ida = ejecutar_navegacion(nombre, grafo, matriz, inicio, destino, id_alg)
                ruta_vuelta = ejecutar_navegacion(nombre, grafo, matriz, destino, inicio, id_alg)
                resultado['ruta_ida'] = ruta_ida
                resultado['ruta_vuelta'] = ruta_vuelta
                resultado['pasos'] = 0
                if ruta_ida:
                    resultado['pasos'] += len(ruta_ida) - 1
                if ruta_vuelta:
                    resultado['pasos'] += len(ruta_vuelta) - 1

            salida = capturar_salida(ejecutar_ruta)
            pasos = resultado.get('pasos') # Obtenemos el conteo de pasos total (ida + vuelta) para la comparación

        tiempo = time.perf_counter() - inicio_t # Medimos el tiempo total de ejecución del algoritmo
        if pasos is None: # Si el algoritmo no encontró ruta, lo marcamos como inválido para la comparación
            pasos = 'Sin ruta'

        resultados.append({'algoritmo': nombre, 'pasos': pasos, 'tiempo': tiempo, 'salida': salida}) # Guardamos toda la información relevante para cada algoritmo en una lista de resultados

    validos = [r for r in resultados if isinstance(r['pasos'], int)]
    ganador = min(validos, key=lambda r: (r['pasos'], r['tiempo']), default=None)

    for r in resultados: # Imprimimos los resultados de cada algoritmo, incluyendo su salida detallada y destacando el ganador al final
        print(f"[{r['algoritmo']}]")
        print(f"Pasos: {r['pasos']}")
        print(f"Tiempo: {r['tiempo']:.6f} s")
        if r['salida'].strip():
            print(r['salida'].strip())
        print('-' * 50)

    if ganador:
        print(f"GANADOR: {ganador['algoritmo']} | Pasos: {ganador['pasos']} | Tiempo: {ganador['tiempo']:.6f} s")
    else: # Si ningún algoritmo encontró una ruta válida, lo indicamos claramente
        print('No fue posible determinar un ganador porque ninguno encontró ruta válida.')

# ---------------- VENTANA ----------------
root = tk.Tk()
root.title('Sistema Logístico TEC')
root.geometry('1100x820')
root.configure(bg='#0d1b2a')

style = ttk.Style()
style.theme_use('clam')
style.configure('TNotebook', background='#0d1b2a')
style.configure('TNotebook.Tab', padding=(12,8))

# ---------------- TITULO ----------------
header = tk.Label(root, text='SISTEMA LOGÍSTICO TEC', font=('Arial', 28, 'bold'), fg='white', bg='#0d1b2a')
header.pack(pady=10)

notebook = ttk.Notebook(root)
notebook.pack(fill='both', expand=True, padx=15, pady=(0,5))

# ==================================================
# TAB 1 NAVEGACION
# ==================================================
nav_tab = tk.Frame(notebook, bg='#1b263b')
notebook.add(nav_tab, text='Navegación')

form = tk.Frame(nav_tab, bg='#1b263b')
form.pack(pady=5)

# campos
labels = ['ID Paquete', 'Peso (kg)', 'Destino', 'Algoritmo']
for i, t in enumerate(labels):
    tk.Label(form, text=t+':', bg='#1b263b', fg='white', font=('Arial', 11, 'bold')).grid(row=i, column=0, sticky='e', padx=8, pady=6)

entry_id = tk.Entry(form, width=28)
entry_id.grid(row=0, column=1)

entry_peso = tk.Entry(form, width=28)
entry_peso.grid(row=1, column=1)

combo_dest = ttk.Combobox(form, width=25, state='readonly', values=estaciones)
combo_dest.grid(row=2, column=1)

combo_alg = ttk.Combobox(form, width=25, state='readonly', values=[
    '1 - Programación Dinámica',
    '2 - Algoritmos Genéticos',
    '3 - Greedy',
    '4 - Backtracking',
    '5 - Divide y Vencerás',
    '6 - Las Vegas',
    '7 - Monte Carlo'
])
combo_alg.grid(row=3, column=1)

out_nav = scrolledtext.ScrolledText(nav_tab, width=125, height=28, font=('Consolas', 10))
out_nav.pack(padx=12, pady=5)

def ejecutar_gui_nav():
    """Ejecuta el algoritmo de navegación seleccionado para el paquete ingresado y muestra resultados en la interfaz."""
    try:
        paquete = entry_id.get().strip()
        peso = int(entry_peso.get())
        if not paquete: # Validamos que el ID del paquete no esté vacío
            raise ValueError('Digite ID del paquete')
        if peso <= 0 or peso > 20: # Validamos que el peso sea un número positivo y no exceda la capacidad máxima del robot
            raise ValueError('Peso inválido')
        if not combo_dest.get() or not combo_alg.get(): # Validamos que se haya seleccionado un destino y un algoritmo antes de proceder
            raise ValueError('Seleccione destino y algoritmo')

        texto = combo_dest.get().replace('(', '').replace(')', '').replace(',', '') # Procesamos el texto del destino para extraer las coordenadas en formato (fila, columna)
        a, b = texto.split()
        destino = (int(a), int(b))
        id_alg = combo_alg.get()[0]
        nombre = combo_alg.get()

        def proceso():
            """Proceso principal que ejecuta la navegación y prepara las rutas para su transmisión al robot, sin enviarlas directamente."""
            print('='*50)
            print('ENVÍO INDIVIDUAL')
            print('='*50)
            print('Paquete:', paquete)
            print('Peso:', peso, 'kg')
            print('Destino:', destino)
            
            global rutas_pendientes_nav 
            rutas_pendientes_nav = [] # Limpiar la memoria
            
            if id_alg == '2': # Si el algoritmo seleccionado es el genético, lo ejecutamos directamente con la función específica y guardamos su resultado
                paquete_dict = {'id': paquete, 'peso': peso, 'destino': destino, 'prioridad': 5}
                ruta_completa, pasos_totales = aplicar_genetico(matriz, inicio, [paquete_dict])
                
                if ruta_completa: # Si el genético encontró una ruta, la traducimos a comandos para el robot y la guardamos en memoria para su posterior transmisión
                    comando_robot = traducir_para_esp32(ruta_completa)
                    rutas_pendientes_nav.append(comando_robot)
                    print(f"\n[RUTA GENETICA CALCULADA]: {comando_robot.strip()}")
            else: # Para los algoritmos tradicionales, calculamos la ruta de ida y vuelta por separado, traducimos cada una a comandos para el robot y las guardamos en memoria sin enviarlas directamente
                print('\n>>> IDA')
                ruta1 = ejecutar_navegacion(nombre, grafo, matriz, inicio, destino, id_alg)
                
                if ruta1: # Si se encontró una ruta de ida válida, la traducimos a comandos para el robot y la guardamos en memoria para su posterior transmisión
                    comando_robot = traducir_para_esp32(ruta1)
                    rutas_pendientes_nav.append(comando_robot)
                    print(f"[RUTA IDA CALCULADA]: {comando_robot.strip()}")

                print('\n>>> REGRESO')
                ruta2 = ejecutar_navegacion(nombre, grafo, matriz, destino, inicio, id_alg)
                
                if ruta2: # Si se encontró una ruta de regreso válida, la traducimos a comandos para el robot y la guardamos en memoria para su posterior transmisión
                    comando_robot2 = traducir_para_esp32(ruta2)
                    rutas_pendientes_nav.append(comando_robot2)
                    print(f"[RUTA REGRESO CALCULADA]: {comando_robot2.strip()}")

                pasos = 0
                if ruta1: pasos += len(ruta1)-1
                if ruta2: pasos += len(ruta2)-1
                print('\nRESUMEN')
                print('Total de pasos:', pasos)

            print("\n" + "-"*50)
            print("[INFO] Rutas listas en memoria.")
            print("--> Presione 'TRANSMITIR AL ROBOT' para iniciar el movimiento fisico.")
            print("-" * 50)

        texto = capturar_salida(proceso)
        out_nav.delete('1.0', tk.END)
        out_nav.insert(tk.END, texto)
    except Exception as e: # Si ocurre cualquier error durante la validación o ejecución, mostramos un mensaje de error al usuario en lugar de imprimirlo en la consola
        messagebox.showerror('Error', str(e))
        
def transmitir_nav():
    global rutas_pendientes_nav, IP_ESP32_GLOBAL
    if not rutas_pendientes_nav:
        messagebox.showwarning("Aviso", "Primero debe ejecutar y calcular una ruta.")
        return
        
    out_nav.insert(tk.END, "\n" + "="*50 + "\nINICIANDO TRANSMISION WI-FI\n" + "="*50 + "\n")
    error_critico = False 
    
    # Recorrer cada ruta pendiente (ida y regreso) y enviarla al ESP32
    for i, comando_completo in enumerate(rutas_pendientes_nav):
        if i == 1:
            out_nav.insert(tk.END, f"\n[PAUSA] Llegada. Esperando 3s...\n")
            out_nav.see(tk.END); root.update()
            time.sleep(3)
            out_nav.insert(tk.END, f"[REGRESO] Iniciando Etapa 2...\n")
        else:
            out_nav.insert(tk.END, f"[IDA] Iniciando Etapa 1...\n")
        
        comandos_separados = comando_completo.strip().split(',')
        
        for cmd in comandos_separados:
            if not cmd: continue # Ignora comas vacias
            
            out_nav.insert(tk.END, f"  -> Ejecutando {cmd}... ")
            out_nav.see(tk.END); root.update()
            
            try:
                cmd_seguro = urllib.parse.quote(cmd)
                url = f"http://{IP_ESP32_GLOBAL}/ruta?cmd={cmd_seguro}"
                req = urllib.request.Request(url, headers={'Connection': 'close'})
                
                with urllib.request.urlopen(req, timeout=60) as respuesta:
                    resp_texto = respuesta.read().decode('utf-8').strip()
                    if "OK" in resp_texto:
                        out_nav.insert(tk.END, f"[LLEGÓ]\n")
                    else:
                        out_nav.insert(tk.END, f"[AVISO] {resp_texto}\n")
           
            except socket.timeout:
                out_nav.insert(tk.END, f"\n[ERROR] El carro no respondió a tiempo (Timeout).\n")
                error_critico = True
                break
            except Exception as e:
                out_nav.insert(tk.END, f"\n[ERROR RED] {e}\n")
                error_critico = True
                break
            
            out_nav.see(tk.END); root.update()
            time.sleep(0.5)
        
        if error_critico:
            out_nav.insert(tk.END, f"\n[ABORTADO] Conexión Perdida.\n")
            break 
        else:
            if i == 0:
                out_nav.insert(tk.END, f"\n[EXITO] Etapa 1 completada. ¡Paquete Entregado! Sonando alarma...\n")
            else:
                out_nav.insert(tk.END, f"\n[EXITO] Etapa 2 completada. ¡De vuelta en base! Sonando alarma...\n")
                
            out_nav.see(tk.END); root.update()
            
            try:
                url_beep = f"http://{IP_ESP32_GLOBAL}/beep"
                req_beep = urllib.request.Request(url_beep, headers={'Connection': 'close'})
                urllib.request.urlopen(req_beep, timeout=5)
                time.sleep(1)
            except Exception as e:
                out_nav.insert(tk.END, f"  [AVISO] Falla Wi-Fi al intentar pitar: {e}\n")
                
            root.update()
            
    # Solo imprimimos el exito total si terminamos sin levantar banderas
    if not error_critico:
        out_nav.insert(tk.END, f"\n[EXITO TOTAL] Viaje logistico completado al 100%.\n")
    rutas_pendientes_nav = [] # Limpiar memoria para el siguiente envío

def comparar_gui_nav():
    """Ejecuta la comparación de algoritmos de navegación para el paquete ingresado y muestra resultados en la interfaz."""
    try: # Validamos las entradas y luego ejecutamos la función de comparación que ya incluye la ejecución de todos los algoritmos y la impresión detallada de resultados en consola, capturando toda esa salida para mostrarla en el área de texto de la interfaz
        paquete = entry_id.get().strip()
        peso = int(entry_peso.get())
        if not paquete:
            raise ValueError('Digite ID del paquete')
        if peso <= 0 or peso > 20:
            raise ValueError('Peso inválido')
        if not combo_dest.get():
            raise ValueError('Seleccione destino')

        texto = combo_dest.get().replace('(', '').replace(')', '').replace(',', '')
        a, b = texto.split()
        destino = (int(a), int(b))

        texto = capturar_salida(lambda: ejecutar_comparacion_nav(paquete, peso, destino))
        out_nav.delete('1.0', tk.END)
        out_nav.insert(tk.END, texto)
    except Exception as e:
        messagebox.showerror('Error', str(e))

btns = tk.Frame(nav_tab, bg='#1b263b')
btns.pack(pady=2)

tk.Button(
    btns,
    text='CALCULAR RUTA',
    bg='#00b4d8',
    fg='white',
    font=('Arial', 11, 'bold'),
    width=20,
    height=2,
    bd=0,
    cursor='hand2',
    command=ejecutar_gui_nav
).grid(row=0, column=0, padx=8)

tk.Button(
    btns,
    text='TRANSMITIR AL ROBOT',
    bg='#198754',
    fg='white',
    font=('Arial', 11, 'bold'),
    width=20,
    height=2,
    bd=0,
    cursor='hand2',
    command=transmitir_nav
).grid(row=0, column=3, padx=8)

tk.Button(
    btns,
    text='COMPARAR TODO',
    bg='#6f42c1',
    fg='white',
    font=('Arial', 11, 'bold'),
    width=20,
    height=2,
    bd=0,
    cursor='hand2',
    command=comparar_gui_nav
).grid(row=0, column=1, padx=8)

tk.Button(
    btns,
    text='LIMPIAR',
    bg='#6c757d',
    fg='white',
    font=('Arial', 11, 'bold'),
    width=20,
    height=2,
    bd=0,
    cursor='hand2',
    command=lambda: out_nav.delete('1.0', tk.END)
).grid(row=0, column=2, padx=8)

# ==================================================
# TAB 2 MOCHILA
# ==================================================
mo_tab = tk.Frame(notebook, bg='#1b263b')
notebook.add(mo_tab, text='Mochila / Bodega')

left = tk.Frame(mo_tab, bg='#1b263b')
left.pack(side='left', fill='y', padx=12, pady=10)
right = tk.Frame(mo_tab, bg='#1b263b')
right.pack(side='right', fill='both', expand=True, padx=12, pady=10)

# entradas
# Mostrar estaciones disponibles
tk.Label(left, text='Estaciones:', bg='#1b263b', fg='white', font=('Arial', 9, 'bold')).grid(row=0, column=0, columnspan=2, sticky='w', pady=(4, 2))
stations_label = tk.Label(left, text=str(estaciones), bg='#1b263b', fg='#00d4ff', font=('Arial', 8), wraplength=250, justify='left')
stations_label.grid(row=1, column=0, columnspan=2, sticky='w', pady=(0, 8))

campos = ['ID', 'Peso', 'Prioridad', 'Fila', 'Columna']
entries = {}
for i,c in enumerate(campos):
    tk.Label(left, text=c+':', bg='#1b263b', fg='white').grid(row=i+2, column=0, sticky='e', pady=4)
    ent = tk.Entry(left, width=18)
    ent.grid(row=i+2, column=1, pady=4)
    entries[c] = ent

paquetes = []
lista = tk.Listbox(left, width=34, height=12)
lista.grid(row=7, column=0, columnspan=2, pady=8)

max_ent = tk.Entry(left, width=18)
max_ent.grid(row=8, column=1)
tk.Label(left, text='Máx entregas:', bg='#1b263b', fg='white').grid(row=8, column=0)

out_mo = scrolledtext.ScrolledText(right, width=78, height=32, font=('Consolas',10))

resumen_mo = tk.Frame(right, bg='#1b263b')
resumen_mo.pack(fill='x', pady=(0, 8))

resumen_vars = {
    'cantidad': tk.StringVar(value='0'),
    'peso': tk.StringVar(value='0'),
    'prioridad': tk.StringVar(value='0'),
    'promedio': tk.StringVar(value='0.00'),
}

for i, (texto, clave) in enumerate([ 
    ('Seleccionados', 'cantidad'),
    ('Peso total', 'peso'),
    ('Prioridad total', 'prioridad'),
    ('Promedio prioridad', 'promedio'),
]):
    bloque = tk.Frame(resumen_mo, bg='#243b55', padx=10, pady=8)
    bloque.grid(row=0, column=i, padx=5, sticky='ew')
    tk.Label(bloque, text=texto, bg='#243b55', fg='white', font=('Arial', 9, 'bold')).pack()
    tk.Label(bloque, textvariable=resumen_vars[clave], bg='#243b55', fg='#00d4ff', font=('Arial', 12, 'bold')).pack()

tabla_sel = ttk.Treeview(right, columns=('id', 'peso', 'prioridad', 'destino'), show='headings', height=7)
for col, texto, ancho in [
    ('id', 'ID', 90),
    ('peso', 'Peso', 80),
    ('prioridad', 'Prioridad', 90),
    ('destino', 'Destino', 140),
]:
    tabla_sel.heading(col, text=texto)
    tabla_sel.column(col, width=ancho, anchor='center')
tabla_sel.pack(fill='x', pady=(0, 8))

out_mo.pack(fill='both', expand=True)


def limpiar_mochila():
    """Limpia todas las entradas, listas y resultados relacionados con la sección de mochila para permitir un nuevo inicio."""
    paquetes.clear()
    lista.delete(0, tk.END)
    out_mo.delete('1.0', tk.END)
    tabla_sel.delete(*tabla_sel.get_children())
    for e in entries.values():
        e.delete(0, tk.END)
    max_ent.delete(0, tk.END)
    resumen_vars['cantidad'].set('0')
    resumen_vars['peso'].set('0')
    resumen_vars['prioridad'].set('0')
    resumen_vars['promedio'].set('0.00')

def agregar_paquete():
    """Agrega un paquete a la lista de paquetes a entregar, validando sus datos y actualizando la interfaz."""
    try:
        id_p = entries['ID'].get().strip()
        peso = int(entries['Peso'].get())
        prioridad = int(entries['Prioridad'].get())
        fila = int(entries['Fila'].get())
        columna = int(entries['Columna'].get())
        destino = (fila, columna)
        
        # Validaciones
        if not id_p:
            raise ValueError('El ID no puede estar vacio')
        if any(pkg['id'] == id_p for pkg in paquetes):
            raise ValueError('Ya existe un paquete con ese ID')
        if peso <= 0 or peso > 20:
            raise ValueError('Peso debe ser entre 1 y 20 kg')
        if prioridad < 1 or prioridad > 10:
            raise ValueError('Prioridad debe ser entre 1 y 10')
        if destino not in estaciones:
            raise ValueError('Destino no es una estacion valida')
        
        p = {
            'id': id_p,
            'peso': peso,
            'prioridad': prioridad,
            'destino': destino
        }
        paquetes.append(p)
        lista.insert(tk.END, f"{p['id']} | peso {p['peso']} | prio {p['prioridad']} | {p['destino']}")
        for e in entries.values(): e.delete(0, tk.END)
    except ValueError as ve:
        messagebox.showerror('Error', str(ve))
    except Exception:
        messagebox.showerror('Error', 'Datos invalidos')

def resolver(tipo):
    """Ejecuta el algoritmo de mochila seleccionado (dinámico o greedy) con los paquetes ingresados, muestra resultados en la interfaz y prepara las rutas para su transmisión al robot sin enviarlas directamente."""
    global rutas_pendientes_mochila
    try:
        capacidad = 20
        limite = int(max_ent.get())
        if tipo == 'pd': # Si el tipo es programación dinámica, ejecutamos esa función específica y guardamos su resultado
            gan, sel = resolver_mochila_dinamica(paquetes, capacidad, limite)
            nombre = 'Programación Dinámica'
        else: # Si el tipo es greedy, ejecutamos esa función específica y guardamos su resultado
            gan, sel = resolver_mochila_greedy(paquetes, capacidad, limite)
            nombre = 'Greedy'
            
        orden = definir_orden_prioridad([inicio] + [x['destino'] for x in sel]) # Definimos el orden de entrega basado en la prioridad de los paquetes seleccionados, incluyendo la base como punto de partida
        
        out_mo.delete('1.0', tk.END)
        out_mo.insert(tk.END, f'Resultado {nombre}\n')
        out_mo.insert(tk.END, '='*45 + '\n')
        out_mo.insert(tk.END, f"Paquetes elegidos: {[x['id'] for x in sel]}\n")
        out_mo.insert(tk.END, f"Prioridad total: {gan}\n")
        out_mo.insert(tk.END, f"Orden de entrega: {orden}\n\n")

        tabla_sel.delete(*tabla_sel.get_children())
        peso_total = sum(x['peso'] for x in sel)
        prioridad_total = sum(x['prioridad'] for x in sel)
        promedio_prioridad = (prioridad_total / len(sel)) if sel else 0

        resumen_vars['cantidad'].set(str(len(sel)))
        resumen_vars['peso'].set(str(peso_total))
        resumen_vars['prioridad'].set(str(prioridad_total))
        resumen_vars['promedio'].set(f'{promedio_prioridad:.2f}')

        for paquete in sel: # Mostramos en la tabla los paquetes seleccionados para entrega, con su ID, peso, prioridad y destino, para que el usuario tenga un resumen visual de lo que se va a entregar antes de transmitir las rutas al robot
            tabla_sel.insert('', tk.END, values=(
                paquete['id'], paquete['peso'], paquete['prioridad'], paquete['destino']
            ))

        actual = inicio
        tramo = 1
        rutas_pendientes_mochila = [] # Limpiamos la memoria de envíos

        for dest in orden[1:]: # Recorremos el orden de entrega definido y para cada destino calculamos la ruta desde la posición actual del robot, traducimos esa ruta a comandos para el robot y guardamos esa información en memoria para su posterior transmisión, sin enviarla directamente en este paso
            out_mo.insert(tk.END, f'Tramo {tramo}: {actual} -> {dest}\n')
            
            ruta_tramo = []
            def aux_ejecutar():
                """Función auxiliar para ejecutar la navegación y capturar su salida, guardando la ruta calculada en una variable no local para luego traducirla a comandos para el robot."""
                nonlocal ruta_tramo
                ruta_tramo = ejecutar_navegacion('Greedy', grafo, matriz, actual, dest, '3')
                
            txt = capturar_salida(aux_ejecutar)
            out_mo.insert(tk.END, txt + '\n')

            if not ruta_tramo: # Si no se encontró ruta para este tramo, levantamos una alerta en la interfaz y saltamos al siguiente destino sin intentar enviar nada al robot para este tramo, ya que sería inútil e incluso podría causar errores si el robot intenta ejecutar comandos sin una ruta válida
                out_mo.insert(tk.END, f"[ALERTA] Destino inalcanzable. Se omite el paquete hacia {dest}.\n\n")
                continue 
            
            comando_robot = traducir_para_esp32(ruta_tramo).strip()
            
            # Guardamos la info del tramo en la memoria en vez de enviarla
            rutas_pendientes_mochila.append({
                'tramo': tramo,
                'origen': actual,
                'destino': dest,
                'comando': comando_robot
            })
            
            out_mo.insert(tk.END, f"✓ Ruta calculada: {comando_robot}\n\n")
            actual = dest
            tramo += 1
            
        out_mo.insert(tk.END, "-"*45 + "\n[INFO] Rutas listas en memoria.\n--> Presione 'TRANSMITIR AL ROBOT' para iniciar.\n")
        root.update()
            
    except Exception as e:
        messagebox.showerror('Error', str(e))
        
def transmitir_mochila():
    """Recorre las rutas pendientes de la mochila calculadas previamente, las envía al ESP32 para que el robot las ejecute, maneja posibles errores de conexión o ejecución y muestra el progreso detallado en la interfaz."""
    global IP_ESP32_GLOBAL, rutas_pendientes_mochila
    if not rutas_pendientes_mochila: # Si no hay rutas pendientes en memoria, levantamos una alerta para que el usuario sepa que primero debe resolver la ruta de la mochila antes de intentar transmitirla, ya que no tendría sentido intentar enviar algo sin haber calculado las rutas primero
        messagebox.showwarning("Aviso", "Primero debe resolver la ruta de la mochila.")
        return

    out_mo.insert(tk.END, "\n" + "="*50 + "\nINICIANDO TRANSMISION WI-FI (MOCHILA)\n" + "="*50 + "\n")
    error_critico = False

    for tramo_data in rutas_pendientes_mochila: # Recorremos cada tramo guardado en memoria para la mochila, extraemos su información (número de tramo, origen, destino y comandos para el robot) y luego intentamos enviar esos comandos al ESP32, manejando posibles errores de conexión o ejecución y mostrando el progreso detallado en la interfaz para que el usuario pueda seguir lo que está ocurriendo con cada tramo de la entrega
        tramo = tramo_data['tramo']
        origen = tramo_data['origen']
        destino = tramo_data['destino']
        comando_robot = tramo_data['comando']

        out_mo.insert(tk.END, f"\n[TRAMO {tramo}] Viajando de {origen} -> {destino}\n")
        
        comandos_separados = comando_robot.split(',')
        for cmd in comandos_separados: # Recorremos cada comando separado por comas para enviarlo individualmente al ESP32, lo que nos permite manejar mejor la comunicación y detectar exactamente en qué paso ocurre cualquier posible error, además de mostrar un progreso más detallado en la interfaz para cada comando enviado
            if not cmd: continue

            out_mo.insert(tk.END, f"  -> Ejecutando {cmd}... ")
            out_mo.see(tk.END); root.update()

            try: # Enviamos el comando al ESP32 utilizando una solicitud HTTP, asegurándonos de codificar correctamente el comando para la URL y manejando la respuesta del ESP32 para determinar si el robot llegó correctamente o si hubo algún aviso o error que debamos mostrar en la interfaz
                cmd_seguro = urllib.parse.quote(cmd)
                url = f"http://{IP_ESP32_GLOBAL}/ruta?cmd={cmd_seguro}"
                req = urllib.request.Request(url, headers={'Connection': 'close'})
                
                with urllib.request.urlopen(req, timeout=60) as respuesta: # Establecemos un timeout razonable para la respuesta del ESP32, ya que el robot podría tardar en ejecutar el comando y responder, pero si excede ese tiempo es probable que haya un problema de conexión o que el robot esté atascado, por lo que levantamos una alerta en la interfaz para que el usuario pueda tomar acción
                    resp_texto = respuesta.read().decode('utf-8').strip()
                    if "OK" in resp_texto:
                        out_mo.insert(tk.END, "[LLEGÓ]\n")
                    else: # Si la respuesta no contiene "OK", asumimos que el comando fue recibido pero hubo algún tipo de aviso o mensaje que el ESP32 nos está enviando, por lo que lo mostramos en la interfaz para que el usuario esté informado de cualquier situación que pueda requerir su atención
                        out_mo.insert(tk.END, f"[AVISO] {resp_texto}\n")
                        
            except socket.timeout:
                out_mo.insert(tk.END, f"\n[ERROR] Timeout. Posible atasco.\n")
                error_critico = True
                break
            except Exception as e:
                out_mo.insert(tk.END, f"\n[ERROR RED] {e}\n")
                error_critico = True
                break

            out_mo.see(tk.END); root.update()
            time.sleep(0.5)

        if error_critico: # Si se levantó una bandera de error crítico durante el envío de comandos para este tramo, asumimos que la situación es grave (como una conexión perdida o un robot atascado) y decidimos abortar toda la operación para evitar seguir enviando comandos que probablemente no serán ejecutados correctamente, además de informar al usuario con un mensaje claro en la interfaz sobre lo que ocurrió y por qué se detuvo el proceso
            out_mo.insert(tk.END, "\n[ABORTADO] Falla en este tramo. Deteniendo toda la operación.\n")
            break
        else: #
            out_mo.insert(tk.END, f"[EXITO] Robot llegó al punto de entrega {destino}.\n")

            try: # Si el robot llegó correctamente, intentamos enviar una solicitud para que el ESP32 active la alarma de pitido, lo que sirve como confirmación audible de que el paquete fue entregado, pero si ocurre algún error al intentar hacer esto (como un problema de red) simplemente mostramos un aviso en la interfaz sin marcarlo como un error crítico, ya que el paquete ya fue entregado y el pitido es solo una confirmación adicional que no afecta la entrega en sí
                url_beep = f"http://{IP_ESP32_GLOBAL}/beep"
                req_beep = urllib.request.Request(url_beep, headers={'Connection': 'close'})
                urllib.request.urlopen(req_beep, timeout=5)
                time.sleep(1)
            except Exception as e:
                out_mo.insert(tk.END, f"  [AVISO] El carro llegó, pero falló la red al pitar: {e}\n")

    if not error_critico: # Si terminamos de procesar todas las rutas pendientes sin levantar ninguna bandera de error crítico, asumimos que toda la operación fue un éxito total y lo informamos claramente en la interfaz para que el usuario sepa que todos los paquetes fueron entregados correctamente sin ningún problema grave durante el proceso
        out_mo.insert(tk.END, f"\n[EXITO TOTAL] Todos los paquetes entregados correctamente.\n")
    
    rutas_pendientes_mochila = [] # Limpiamos después de terminar

# botones izquierda
btf = tk.Frame(left, bg='#1b263b')
btf.grid(row=9, column=0, columnspan=2, pady=8)

tk.Button(
    btf,
    text='AGREGAR',
    width=18,
    height=2,
    bg='#198754',
    fg='white',
    font=('Arial', 10, 'bold'),
    bd=0,
    cursor='hand2',
    command=agregar_paquete
).grid(row=0,column=0,padx=4,pady=4)

tk.Button(
    btf,
    text='RESOLVER PD',
    width=18,
    height=2,
    bg='#0d6efd',
    fg='white',
    font=('Arial', 10, 'bold'),
    bd=0,
    cursor='hand2',
    command=lambda: resolver('pd')
).grid(row=1,column=0,padx=4,pady=4)

tk.Button(
    btf,
    text='RESOLVER GREEDY',
    width=18,
    height=2,
    bg='#fd7e14',
    fg='white',
    font=('Arial', 10, 'bold'),
    bd=0,
    cursor='hand2',
    command=lambda: resolver('gr')
).grid(row=2,column=0,padx=4,pady=4)

tk.Button(
    btf,
    text='TRANSMITIR AL ROBOT',
    width=18,
    height=2,
    bg='#6f42c1',
    fg='white',
    font=('Arial', 10, 'bold'),
    bd=0,
    cursor='hand2',
    command=transmitir_mochila
).grid(row=4, column=0, padx=4, pady=4)

tk.Button(
    btf,
    text='LIMPIAR CARGA',
    width=18,
    height=2,
    bg='#6c757d',
    fg='white',
    font=('Arial', 10, 'bold'),
    bd=0,
    cursor='hand2',
    command=limpiar_mochila
).grid(row=3,column=0,padx=4,pady=4)

# salir
bottom = tk.Frame(root, bg='#0d1b2a')
bottom.pack(side='bottom', pady=15)

btn_salir = tk.Button(
    bottom,
    text='SALIR',
    command=root.destroy,
    font=('Arial', 14, 'bold'),
    bg='#e63946',
    fg='white',
    activebackground='#b00020',
    activeforeground='white',
    width=20,
    height=2,
    bd=0,
    cursor='hand2'
)

btn_salir.pack()

root.mainloop()
