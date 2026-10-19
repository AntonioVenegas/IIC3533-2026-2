"""Parte c/e) Algoritmo 2: efecto del tamano de bloque n en T(p), S(p) y E(p).

Lee un CSV de exec_parte_c_n.sh por computador y genera grafico_parte_c_n.png,
una grilla de 3 x 4: filas = T(p), S(p), E(p); columnas = tamano de bloque n.
Cada panel tiene una curva por computador y la curva ideal.

El speedup usa como T(1) el tiempo con p = 1 del mismo n, para aislar cuanto
escala cada configuracion del arbol (no la calidad serial de la hoja).

Uso: uv run python grafico_parte_c_n.py comp1.csv comp2.csv comp3.csv
"""

import csv
import sys
from collections import defaultdict
from statistics import mean

import matplotlib.pyplot as plt

archivos = sys.argv[1:] or [
    "output/parte_c_n_comp1.csv",
    "output/parte_c_n_comp2.csv",
    "output/parte_c_n_comp3.csv",
]
nombres = [f"Computador {i + 1}" for i in range(len(archivos))]
colores = ["#2a78d6", "#eb6834", "#1baf7a"]
marcadores = ["o", "s", "^"]
CHECKSUM_REF = 172.331627  # referencia serial para N = 2048

# Promedio de las repeticiones: T[computador][(n, p)] en ms
T = {}
for nombre, archivo in zip(nombres, archivos):
    corridas = defaultdict(list)
    with open(archivo) as f:
        for fila in csv.DictReader(f):
            corridas[(int(fila["n"]), int(fila["p"]))].append(float(fila["tiempo_ms"]))
            if int(fila["N"]) == 2048 and abs(float(fila["checksum"]) - CHECKSUM_REF) > 1e-4:
                print(f"AVISO {nombre}: n={fila['n']} p={fila['p']} checksum={fila['checksum']}")
    T[nombre] = {k: mean(v) for k, v in corridas.items()}

ns = sorted({n for t in T.values() for n, _ in t})
ps = sorted({p for t in T.values() for _, p in t})


def speedup(nombre, n, p):
    return T[nombre][(n, 1)] / T[nombre][(n, p)]


# Tabla en consola
for nombre in nombres:
    print(f"\n{nombre}")
    print(f"{'n':>6} {'p':>3} {'T(p) ms':>10} {'S(p)':>6} {'E(p)':>6}")
    for n in ns:
        for p in ps:
            s = speedup(nombre, n, p)
            print(f"{n:>6} {p:>3} {T[nombre][(n, p)]:>10.2f} {s:>6.2f} {s / p:>6.2f}")

plt.rcParams.update({"font.size": 12})
fig, axes = plt.subplots(3, len(ns), figsize=(4.2 * len(ns), 11), sharex=True, sharey="row")

for col, n in enumerate(ns):
    ax_t, ax_s, ax_e = axes[:, col]
    for nombre, color, m in zip(nombres, colores, marcadores):
        tiempos = [T[nombre][(n, p)] / 1000 for p in ps]
        s = [speedup(nombre, n, p) for p in ps]
        estilo = dict(marker=m, markersize=7, linewidth=2, color=color, label=nombre)
        ax_t.plot(ps, tiempos, **estilo)
        ax_s.plot(ps, s, **estilo)
        ax_e.plot(ps, [si / p for si, p in zip(s, ps)], **estilo)

    # Curvas ideales: T(1)/p (con el T(1) promedio de los computadores), S = p, E = 1
    t1_prom = mean(T[nombre][(n, 1)] for nombre in nombres) / 1000
    ideal = dict(color="gray", linestyle="--", linewidth=1.5, label="Ideal")
    ax_t.plot(ps, [t1_prom / p for p in ps], **ideal)
    ax_s.plot(ps, ps, **ideal)
    ax_e.plot(ps, [1] * len(ps), **ideal)

    ax_t.set_title(f"n = {n}  ({(2048 // n) ** 2} bloques de C)")
    ax_e.set_xlabel("Número de threads p")

for ax in axes.flat:
    ax.set_xscale("log", base=2)
    ax.set_xticks(ps)
    ax.set_xticklabels([str(p) for p in ps])
    ax.grid(True, color="#e0e0e0", linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

axes[0, 0].set_ylabel("Tiempo T(p) (s)")
axes[1, 0].set_ylabel("Speedup S(p)")
axes[2, 0].set_ylabel("Eficiencia E(p)")
axes[0, 0].set_ylim(bottom=0)
axes[1, 0].set_ylim(bottom=0)
axes[2, 0].set_ylim(0, 1.2)

handles, labels = axes[0, 0].get_legend_handles_labels()
fig.legend(handles, labels, loc="lower center", ncol=len(labels), frameon=False)
fig.suptitle("Algoritmo 2 (dividir y conquistar): efecto del tamaño de bloque n (N = 2048)")
fig.tight_layout(rect=(0, 0.04, 1, 0.97))
fig.savefig("grafico_parte_c_n.png", dpi=200)
plt.show()
