import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import io, sys
import time

from lector import cargar_y_convertir_mapa, construir_grafo_navegacion
from main import ejecutar_navegacion, solicitar_multiples_paquetes
from mochila import resolver_mochila_dinamica, resolver_mochila_greedy
from greedy import definir_orden_prioridad
from genetico import aplicar_genetico

# ---------------- CARGA INICIAL ----------------
ruta_mapa = 'mapas/tablero.json'
matriz, inicio, estaciones = cargar_y_convertir_mapa(ruta_mapa)
grafo = construir_grafo_navegacion(matriz)

# ---------------- UTILIDADES ----------------
def capturar_salida(func):
    buffer = io.StringIO()
    viejo = sys.stdout
    sys.stdout = buffer
    try:
        func()
    finally:
        sys.stdout = viejo
    return buffer.getvalue()


def ejecutar_comparacion_nav(paquete, peso, destino):
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

            def ejecutar_genetico():
                resultado['ruta'], resultado['pasos'] = aplicar_genetico(matriz, inicio, [paquete_dict])

            salida = capturar_salida(ejecutar_genetico)
            pasos = resultado.get('pasos')
        else:
            resultado = {}

            def ejecutar_ruta():
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
            pasos = resultado.get('pasos')

        tiempo = time.perf_counter() - inicio_t
        if pasos is None:
            pasos = 'Sin ruta'

        resultados.append({'algoritmo': nombre, 'pasos': pasos, 'tiempo': tiempo, 'salida': salida})

    validos = [r for r in resultados if isinstance(r['pasos'], int)]
    ganador = min(validos, key=lambda r: (r['pasos'], r['tiempo']), default=None)

    for r in resultados:
        print(f"[{r['algoritmo']}]")
        print(f"Pasos: {r['pasos']}")
        print(f"Tiempo: {r['tiempo']:.6f} s")
        if r['salida'].strip():
            print(r['salida'].strip())
        print('-' * 50)

    if ganador:
        print(f"GANADOR: {ganador['algoritmo']} | Pasos: {ganador['pasos']} | Tiempo: {ganador['tiempo']:.6f} s")
    else:
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
    try:
        paquete = entry_id.get().strip()
        peso = int(entry_peso.get())
        if not paquete:
            raise ValueError('Digite ID del paquete')
        if peso <= 0 or peso > 20:
            raise ValueError('Peso inválido')
        if not combo_dest.get() or not combo_alg.get():
            raise ValueError('Seleccione destino y algoritmo')

        texto = combo_dest.get().replace('(', '').replace(')', '').replace(',', '')
        a, b = texto.split()
        destino = (int(a), int(b))
        id_alg = combo_alg.get()[0]
        nombre = combo_alg.get()

        def proceso():
            print('='*50)
            print('ENVÍO INDIVIDUAL')
            print('='*50)
            print('Paquete:', paquete)
            print('Peso:', peso, 'kg')
            print('Destino:', destino)
            
            if id_alg == '2':
                paquete_dict = {'id': paquete, 'peso': peso, 'destino': destino, 'prioridad': 5}
                aplicar_genetico(matriz, inicio, [paquete_dict])
            else:
                print('\n>>> IDA')
                ruta1 = ejecutar_navegacion(nombre, grafo, matriz, inicio, destino, id_alg)
                print('\n>>> REGRESO')
                ruta2 = ejecutar_navegacion(nombre, grafo, matriz, destino, inicio, id_alg)
                pasos = 0
                if ruta1: pasos += len(ruta1)-1
                if ruta2: pasos += len(ruta2)-1
                print('\nRESUMEN')
                print('Total de pasos:', pasos)

        texto = capturar_salida(proceso)
        out_nav.delete('1.0', tk.END)
        out_nav.insert(tk.END, texto)
    except Exception as e:
        messagebox.showerror('Error', str(e))

def comparar_gui_nav():
    try:
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
    text='EJECUTAR RUTA',
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
    try:
        capacidad = 20
        limite = int(max_ent.get())
        if tipo == 'pd':
            gan, sel = resolver_mochila_dinamica(paquetes, capacidad, limite)
            nombre = 'Programación Dinámica'
        else:
            gan, sel = resolver_mochila_greedy(paquetes, capacidad, limite)
            nombre = 'Greedy'
        orden = definir_orden_prioridad([inicio] + [x['destino'] for x in sel])
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

        for paquete in sel:
            tabla_sel.insert('', tk.END, values=(
                paquete['id'],
                paquete['peso'],
                paquete['prioridad'],
                paquete['destino'],
            ))

        actual = inicio
        tramo = 1
        for dest in orden[1:]:
            out_mo.insert(tk.END, f'Tramo {tramo}: {actual} -> {dest}\n')
            txt = capturar_salida(lambda a=actual,d=dest: ejecutar_navegacion('Greedy', grafo, matriz, a, d, '3'))
            out_mo.insert(tk.END, txt + '\n')
            actual = dest
            tramo += 1
    except Exception as e:
        messagebox.showerror('Error', str(e))

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
