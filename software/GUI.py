import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import io, sys

# IMPORTA TUS MODULOS DEL PROYECTO
from lector import cargar_y_convertir_mapa, construir_grafo_navegacion
from main import ejecutar_navegacion, solicitar_multiples_paquetes
from mochila import resolver_mochila_dinamica, resolver_mochila_greedy
from greedy import definir_orden_prioridad

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
    text='LIMPIAR',
    bg='#6c757d',
    fg='white',
    font=('Arial', 11, 'bold'),
    width=20,
    height=2,
    bd=0,
    cursor='hand2',
    command=lambda: out_nav.delete('1.0', tk.END)
).grid(row=0, column=1, padx=8)

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
campos = ['ID', 'Peso', 'Prioridad', 'Fila', 'Columna']
entries = {}
for i,c in enumerate(campos):
    tk.Label(left, text=c+':', bg='#1b263b', fg='white').grid(row=i, column=0, sticky='e', pady=4)
    ent = tk.Entry(left, width=18)
    ent.grid(row=i, column=1, pady=4)
    entries[c] = ent

paquetes = []
lista = tk.Listbox(left, width=34, height=12)
lista.grid(row=6, column=0, columnspan=2, pady=8)

max_ent = tk.Entry(left, width=18)
max_ent.grid(row=7, column=1)
tk.Label(left, text='Máx entregas:', bg='#1b263b', fg='white').grid(row=7, column=0)

out_mo = scrolledtext.ScrolledText(right, width=78, height=32, font=('Consolas',10))
out_mo.pack(fill='both', expand=True)

def agregar_paquete():
    try:
        p = {
            'id': entries['ID'].get(),
            'peso': int(entries['Peso'].get()),
            'prioridad': int(entries['Prioridad'].get()),
            'destino': (int(entries['Fila'].get()), int(entries['Columna'].get()))
        }
        paquetes.append(p)
        lista.insert(tk.END, f"{p['id']} | peso {p['peso']} | prio {p['prioridad']} | {p['destino']}")
        for e in entries.values(): e.delete(0, tk.END)
    except Exception:
        messagebox.showerror('Error', 'Datos inválidos')

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
btf.grid(row=8, column=0, columnspan=2, pady=8)

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
