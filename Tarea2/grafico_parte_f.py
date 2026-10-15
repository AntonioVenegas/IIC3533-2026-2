"""Parte f) Escalabilidad debil.

Lee el CSV de exec_parte_f.sh y genera grafico_parte_f.png (un panel por
algoritmo, en una fila) mas una tabla en consola.

Como el trabajo es W(N) = 2 N^3, al pasar de (p=1, N=1024) a (p=2, N=2048) y
(p=4, N=4096) el trabajo crece 8x por paso mientras p solo crece 2x. Por eso la
eficiencia debil se normaliza por trabajo por thread:

    E_debil(p, N) = [W(N) / (p T(p, N))] / [W(N0) / T(1, N0)]

es decir, el rendimiento (GFLOP/s) por thread relativo al caso p=1, N0=1024.
Ideal: E_debil = 1.

Uso: uv run python grafico_parte_f.py [resultados_parte_f.csv] [sufijo]
"""

import csv
import sys
from collections import defaultdict
from statistics import mean

import matplotlib.pyplot as plt

archivo = sys.argv[1] if len(sys.argv) > 1 else "resultados_parte_f.csv"
sufijo = sys.argv[2] if len(sys.argv) > 2 else ""

nombres = {
    "alg1": "Algoritmo 1: paralelismo de datos (C++/OpenMP)",
    "alg2": "Algoritmo 2: dividir y conquistar (C++/OpenMP tasks)",
    "alg3": "Algoritmo 3: Numba (Python)",
}
casos = [(1, 1024), (2, 2048), (4, 4096)]  # (p, N)
ps = [p for p, _ in casos]

# Promedio de las repeticiones: T[alg][(N, p)] en ms
corridas = defaultdict(lambda: defaultdict(list))
with open(archivo) as f:
    for fila in csv.DictReader(f):
        corridas[fila["algoritmo"]][(int(fila["N"]), int(fila["p"]))].append(float(fila["tiempo_ms"]))
T = {alg: {k: mean(v) for k, v in d.items()} for alg, d in corridas.items()}


def gflops_por_thread(alg, N, p):
    return 2 * N**3 / (T[alg][(N, p)] * 1e-3) / p / 1e9


def eficiencia_debil(alg, N, p):
    p0, N0 = casos[0]
    return gflops_por_thread(alg, N, p) / gflops_por_thread(alg, N0, p0)


plt.rcParams.update({"font.size": 12})
fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharey=True)

for ax, alg in zip(axes, sorted(T)):
    # Tabla en consola
    print(f"\n{nombres.get(alg, alg)}")
    print(f"{'p':>3} {'N':>6} {'T (ms)':>10} {'GFLOP/s/thr':>12} {'E debil':>8}")
    for p, N in casos:
        print(f"{p:>3} {N:>6} {T[alg][(N, p)]:>10.2f} {gflops_por_thread(alg, N, p):>12.3f} "
              f"{eficiencia_debil(alg, N, p):>8.3f}")

    e = [eficiencia_debil(alg, N, p) for p, N in casos]
    ax.axhline(1, color="#888888", linestyle="--", linewidth=1.5, label="Ideal")
    ax.plot(ps, e, marker="o", markersize=8, linewidth=2, color="#2a78d6",
            label="N crece con p")
    for (p, N), ei in zip(casos, e):
        ax.annotate(f"N={N}\n{ei:.2f}", (p, ei), textcoords="offset points",
                    xytext=(0, -14), ha="center", va="top", fontsize=10)

    titulo, _, detalle = nombres.get(alg, alg).partition(": ")
    ax.set_title(f"{titulo}\n{detalle}", fontsize=12)
    ax.set_xlabel("Número de threads p")
    ax.set_xticks(ps)
    ax.set_xlim(0.7, 4.3)
    ax.grid(True, color="#e0e0e0", linewidth=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)

axes[0].set_ylabel("Eficiencia débil (ref. p=1, N=1024)")
axes[0].set_ylim(0, max(1.2, axes[0].get_ylim()[1] * 1.1))
axes[0].legend(frameon=False, loc="lower left")
fig.suptitle("Escalabilidad débil", fontsize=14)
fig.tight_layout()
salida = f"grafico_parte_f{sufijo}.png"
fig.savefig(salida, dpi=200)
print(f"\nGráfico guardado en {salida}")

plt.show()
