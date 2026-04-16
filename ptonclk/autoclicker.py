"""
╔══════════════════════════════════════════╗
║   AutoClicker ULTRA - Proyecto Escolar   ║
║   Hasta 1000+ clics por segundo          ║
╚══════════════════════════════════════════╝

REQUISITOS:
    pip install pynput

MEJORAS vs versión anterior:
    ✓ perf_counter() en lugar de sleep() → ultra preciso
    ✓ Busy-wait en modo turbo (>50 CPS)
    ✓ UI se actualiza en lote, no por cada clic
    ✓ Máximo subido a 1000 CPS
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener as KeyListener, Key

mouse = Controller()

# ─── Estado global ────────────────────────────────────────────────────────────
running    = False
click_count= 0
cps_real   = 0.0          # CPS medido en tiempo real

# ─── Loop de clic ULTRA PRECISO ───────────────────────────────────────────────
def auto_click():
    global running, click_count, cps_real

    try:
        cps = float(cps_var.get())
        cps = max(1, min(cps, 1000))
    except ValueError:
        cps = 10

    interval = 1.0 / cps          # segundos entre clics
    tipo     = click_type_var.get()
    boton    = Button.right if tipo == "Derecho" else Button.left

    # Contadores para medir CPS real
    t_start  = time.perf_counter()
    local_n  = 0

    while running:
        t_click = time.perf_counter()

        # ── Ejecutar clic ───────────────────────────────────────────────────
        if tipo == "Doble":
            mouse.click(Button.left, 2)
        else:
            mouse.click(boton, 1)

        click_count += 1
        local_n     += 1

        # ── Calcular CPS real cada 20 clics ────────────────────────────────
        if local_n % 20 == 0:
            elapsed  = time.perf_counter() - t_start
            cps_real = local_n / elapsed if elapsed > 0 else 0
            t_start  = time.perf_counter()
            local_n  = 0

        # ── Espera PRECISA ─────────────────────────────────────────────────
        # Para >50 CPS usamos busy-wait (más preciso que sleep)
        # Para ≤50 CPS combinamos sleep + busy-wait para no quemar CPU
        deadline = t_click + interval
        remaining = deadline - time.perf_counter()

        if cps <= 50 and remaining > 0.002:
            time.sleep(remaining - 0.001)   # dormir casi todo el tiempo
        # Busy-wait final para precisión de microsegundos
        while time.perf_counter() < deadline:
            pass


# ─── Actualizar UI cada 80ms (no por cada clic) ───────────────────────────────
def update_ui():
    if running:
        counter_var.set(f"{click_count:,}")
        cps_live_var.set(f"{cps_real:.0f} CPS")
        root.after(80, update_ui)   # volver a llamar en 80ms
    else:
        counter_var.set(f"{click_count:,}")
        cps_live_var.set("— CPS")


# ─── Iniciar / Detener ────────────────────────────────────────────────────────
def toggle():
    global running, click_count

    if not running:
        running      = True
        click_count  = 0
        btn_toggle.config(text="⏹  DETENER", bg="#e74c3c", activebackground="#c0392b")
        status_var.set("● ACTIVO")
        status_label.config(fg="#2ecc71")
        t = threading.Thread(target=auto_click, daemon=True)
        t.start()
        root.after(80, update_ui)   # arrancar el loop de UI
    else:
        running = False
        btn_toggle.config(text="▶  INICIAR", bg="#2ecc71", activebackground="#27ae60")
        status_var.set("○ INACTIVO")
        status_label.config(fg="#e74c3c")


# ─── Hotkey F6 ────────────────────────────────────────────────────────────────
def on_press(key):
    if key == Key.f6:
        root.after(0, toggle)


# ─── Validar entrada numérica ─────────────────────────────────────────────────
def validate_cps(value):
    if value in ("", "."): return True
    try:    float(value); return True
    except: return False


# ─────────────────────────────────────────────────────────────────────────────
#  INTERFAZ GRÁFICA
# ─────────────────────────────────────────────────────────────────────────────
root = tk.Tk()
root.title("AutoClicker ULTRA")
root.geometry("400x560")
root.resizable(False, False)
root.configure(bg="#0d0d0d")

# ── Variables ─────────────────────────────────────────────────────────────────
cps_var       = tk.StringVar(value="50")
click_type_var= tk.StringVar(value="Izquierdo")
status_var    = tk.StringVar(value="○ INACTIVO")
counter_var   = tk.StringVar(value="0")
cps_live_var  = tk.StringVar(value="— CPS")

# ── Título ────────────────────────────────────────────────────────────────────
tk.Label(root, text="⚡ AutoClicker ULTRA",
         font=("Consolas", 21, "bold"), bg="#0d0d0d", fg="#ff4444").pack(pady=(18, 2))

tk.Label(root, text="hasta 1000 clics/seg  |  F6 para activar",
         font=("Consolas", 9), bg="#0d0d0d", fg="#444466").pack()

ttk.Separator(root).pack(fill="x", padx=20, pady=10)

panel = tk.Frame(root, bg="#111122")
panel.pack(padx=18, fill="both", expand=True)

# ── Velocidad ─────────────────────────────────────────────────────────────────
tk.Label(panel, text="VELOCIDAD  (CPS — clics por segundo)",
         font=("Consolas", 9), bg="#111122", fg="#6666aa").pack(anchor="w", padx=14, pady=(14, 2))

cps_row = tk.Frame(panel, bg="#111122")
cps_row.pack(padx=10, fill="x")

vcmd = root.register(validate_cps)
tk.Entry(cps_row, textvariable=cps_var, width=6,
         font=("Consolas", 20, "bold"),
         bg="#0a0a1a", fg="#ff4444", insertbackground="#ff4444",
         relief="flat", justify="center",
         validate="key", validatecommand=(vcmd, "%P")
         ).pack(side="left", padx=(4, 10), ipady=6)

slider = tk.Scale(cps_row, from_=1, to=1000, orient="horizontal",
                  bg="#111122", fg="#6666aa", troughcolor="#0a0a1a",
                  highlightthickness=0, showvalue=False, length=220,
                  command=lambda v: cps_var.set(str(int(float(v)))))
slider.set(50)
slider.pack(side="left", fill="x", expand=True)

def sync_slider(*_):
    try: slider.set(float(cps_var.get()))
    except: pass
cps_var.trace_add("write", sync_slider)

# Presets rápidos
preset_row = tk.Frame(panel, bg="#111122")
preset_row.pack(fill="x", padx=10, pady=(4, 0))

PRESETS = [("Lento\n10", 10), ("Normal\n50", 50),
           ("Rápido\n200", 200), ("ULTRA\n1000", 1000)]

for label, val in PRESETS:
    tk.Button(preset_row, text=label,
              font=("Consolas", 8, "bold"),
              bg="#1a1a33", fg="#8888cc",
              activebackground="#ff4444", activeforeground="white",
              relief="flat", cursor="hand2", pady=4,
              command=lambda v=val: cps_var.set(str(v))
              ).pack(side="left", expand=True, fill="x", padx=2)

ttk.Separator(panel).pack(fill="x", padx=14, pady=10)

# ── Tipo de clic ──────────────────────────────────────────────────────────────
tk.Label(panel, text="TIPO DE CLIC",
         font=("Consolas", 9), bg="#111122", fg="#6666aa").pack(anchor="w", padx=14, pady=(0, 6))

type_row = tk.Frame(panel, bg="#111122")
type_row.pack(padx=10, fill="x")

btns_tipo = {}
for name in ("Izquierdo", "Derecho", "Doble"):
    b = tk.Button(type_row, text=name,
                  font=("Consolas", 10, "bold"),
                  bg="#0a0a1a", fg="white",
                  activebackground="#ff4444", activeforeground="white",
                  relief="flat", cursor="hand2", pady=7,
                  command=lambda n=name: set_type(n))
    b.pack(side="left", expand=True, fill="x", padx=2)
    btns_tipo[name] = b

def set_type(t):
    click_type_var.set(t)
    for n, b in btns_tipo.items():
        b.config(bg="#ff4444" if n == t else "#0a0a1a")

set_type("Izquierdo")

ttk.Separator(panel).pack(fill="x", padx=14, pady=10)

# ── Contador + CPS real ────────────────────────────────────────────────────────
tk.Label(panel, text="CLICS TOTALES",
         font=("Consolas", 9), bg="#111122", fg="#6666aa").pack()

tk.Label(panel, textvariable=counter_var,
         font=("Consolas", 38, "bold"), bg="#111122", fg="#ff4444").pack()

tk.Label(panel, textvariable=cps_live_var,
         font=("Consolas", 14), bg="#111122", fg="#ff8800").pack(pady=(0, 6))

# ── Estado ────────────────────────────────────────────────────────────────────
status_label = tk.Label(panel, textvariable=status_var,
                        font=("Consolas", 11, "bold"),
                        bg="#111122", fg="#e74c3c")
status_label.pack(pady=(0, 10))

# ── Botón principal ───────────────────────────────────────────────────────────
btn_toggle = tk.Button(root, text="▶  INICIAR",
                       font=("Consolas", 14, "bold"),
                       bg="#2ecc71", activebackground="#27ae60",
                       fg="white", activeforeground="white",
                       relief="flat", cursor="hand2",
                       pady=14, bd=0,
                       command=toggle)
btn_toggle.pack(fill="x", padx=18, pady=(6, 4))

tk.Label(root, text="F6 = activar/desactivar  |  presets arriba para velocidad rápida",
         font=("Consolas", 8), bg="#0d0d0d", fg="#333355").pack(pady=(0, 14))

# ─── Teclado ──────────────────────────────────────────────────────────────────
kl = KeyListener(on_press=on_press)
kl.daemon = True
kl.start()

def on_close():
    global running
    running = False
    kl.stop()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()