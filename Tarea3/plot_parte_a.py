# Grafico de la parte (a): tiempo y GFLOP/s de lu_serial.py en funcion de b.
# Lee la salida de exec_parte_a.sh (las lineas "b=... corrida ...: ... s, ... GFLOPS").
# Uso: python plot_parte_a.py [--archivo resultados_parte_a.txt] [--N 4096]

import argparse
import re
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--archivo", default="resultados_parte_a.txt")
parser.add_argument("--N", type=int, default=4096)
args = parser.parse_args()

patron = re.compile(r"b=(\d+) corrida \d+: ([-+\d.eE]+) s, ([-+\d.eE]+) GFLOPS")
tiempos = defaultdict(list)
gflops = defaultdict(list)
with open(args.archivo) as f:
    for linea in f:
        m = patron.search(linea)
        if m:
            b = int(m.group(1))
            tiempos[b].append(float(m.group(2)))
            gflops[b].append(float(m.group(3)))

if not tiempos:
    raise SystemExit(f"No se encontraron corridas en {args.archivo}")

bs = sorted(tiempos)
t_media = np.array([np.mean(tiempos[b]) for b in bs])
t_std = np.array([np.std(tiempos[b]) for b in bs])
g_media = np.array([np.mean(gflops[b]) for b in bs])
g_std = np.array([np.std(gflops[b]) for b in bs])
b_mejor = bs[int(np.argmin(t_media))]

# Tabla para el informe
print(f"N = {args.N}, 1 thread, {len(tiempos[bs[0]])} corridas por b")
print(f"{'b':>6}  {'tiempo [s]':>16}  {'GFLOP/s':>14}")
for b, tm, ts, gm, gs in zip(bs, t_media, t_std, g_media, g_std):
    marca = "  <- mejor" if b == b_mejor else ""
    print(f"{b:>6}  {tm:>8.3f} ± {ts:<5.3f}  {gm:>7.2f} ± {gs:<5.2f}{marca}")
print(f"\nb con menor tiempo: {b_mejor}")

# Grafico
plt.rcParams.update({"font.size": 13})
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8))

ax1.errorbar(bs, t_media, yerr=t_std, marker="o", capsize=4, color="tab:blue")
ax1.set_ylabel("Tiempo de factorización [s]")
ax1.set_title("Tiempo")

ax2.errorbar(bs, g_media, yerr=g_std, marker="s", capsize=4, color="tab:orange")
ax2.set_ylabel("Rendimiento [GFLOP/s]")
ax2.set_title("Rendimiento")

for ax in (ax1, ax2):
    ax.set_xscale("log", base=2)
    ax.set_xticks(bs)
    ax.set_xticklabels([str(b) for b in bs])
    ax.set_xlabel("Tamaño de bloque b")
    ax.axvline(b_mejor, color="gray", linestyle="--", linewidth=1,
               label=f"mejor b = {b_mejor}")
    ax.grid(True, alpha=0.3)
    ax.legend()

fig.suptitle(f"LU serial por bloques, N = {args.N}, 1 thread (promedio ± desv. estándar)")
fig.tight_layout()
fig.savefig("parte_a.png", dpi=200)
fig.savefig("parte_a.pdf")
print("Guardado en parte_a.png y parte_a.pdf")