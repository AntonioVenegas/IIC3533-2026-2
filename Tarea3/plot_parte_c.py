# Grafico de la parte (c): LU distribuida, N = 8192, grid 2x2, T = 2, variando b.
# Lee el CSV que escribe lu_distributed.py (una fila por proceso y corrida).
# Uso: python plot_parte_c.py [--csv resultados_parte_c.csv] [--parte-a resultados_parte_a.txt]
#
# - Tiempo de una corrida = el del proceso mas lento (max del total entre ranks).
# - Computo / comunicacion = promedio entre ranks y corridas.

import argparse
import csv
import re
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--csv", default="resultados_parte_c.csv")
parser.add_argument("--parte-a", default="resultados_parte_a.txt",
                    help="salida de exec_parte_a.sh, para marcar el mejor b de (a)")
args = parser.parse_args()

# ---- Lectura ----
with open(args.csv) as f:
    filas = list(csv.DictReader(f))
if not filas:
    raise SystemExit(f"{args.csv} esta vacio")

N = int(filas[0]["N"])
pr, pc, T = filas[0]["pr"], filas[0]["pc"], filas[0]["T"]
p = int(pr) * int(pc)

# El rank 0 escribe las p filas de cada corrida juntas, asi que cada bloque
# consecutivo de p filas es una corrida (aunque se repita "rep" entre jobs).
corridas = defaultdict(list)          # b -> lista de corridas (cada una: lista de filas)
for i in range(0, len(filas) - p + 1, p):
    bloque = filas[i:i + p]
    corridas[int(bloque[0]["b"])].append(bloque)

bs = sorted(corridas)
t_media, t_std, comp, comm, n_corr = [], [], [], [], []
for b in bs:
    t_corr = [max(float(r["total"]) for r in c) for c in corridas[b]]
    t_media.append(np.mean(t_corr))
    t_std.append(np.std(t_corr))
    comp.append(np.mean([float(r["computo"]) for c in corridas[b] for r in c]))
    comm.append(np.mean([float(r["comunicacion"]) for c in corridas[b] for r in c]))
    n_corr.append(len(t_corr))
t_media, t_std = np.array(t_media), np.array(t_std)
comp, comm = np.array(comp), np.array(comm)
gflops = (2 / 3) * N**3 / t_media / 1e9
b_mejor = bs[int(np.argmin(t_media))]

# Mejor b de la parte (a), leido de las lineas resumen "b  tiempo  GFLOPS  checksum"
b_a = None
try:
    with open(args.parte_a) as f:
        resumen = [l.split() for l in f if re.match(r"^\d+\s+[\d.]+\s", l)]
    b_a = int(min(resumen, key=lambda x: float(x[1]))[0])
except (OSError, ValueError):
    pass

# ---- Tabla para el informe ----
print(f"N = {N}, grid {pr}x{pc}, T = {T}")
print(f"{'b':>6}  {'corridas':>8}  {'tiempo [s]':>16}  {'GFLOP/s':>8}  "
      f"{'computo [s]':>11}  {'comunic. [s]':>12}  {'% comunic.':>10}")
for b, n, tm, ts, g, cp, cm in zip(bs, n_corr, t_media, t_std, gflops, comp, comm):
    marca = "  <- mejor" if b == b_mejor else ""
    print(f"{b:>6}  {n:>8}  {tm:>8.3f} ± {ts:<5.3f}  {g:>8.2f}  "
          f"{cp:>11.3f}  {cm:>12.3f}  {100 * cm / (cp + cm):>9.1f}%{marca}")
print(f"\nMejor b en (c): {b_mejor}" + (f"   |   mejor b en (a): {b_a}" if b_a else ""))

# ---- Grafico ----
AZUL, NARANJO = "#2a78d6", "#eb6834"
GRIS, TINTA = "#8a8984", "#52514e"
plt.rcParams.update({"font.size": 13, "axes.edgecolor": GRIS,
                     "xtick.color": TINTA, "ytick.color": TINTA})
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
x = np.arange(len(bs))  # posiciones equiespaciadas (b es potencia de 2)

# (1) Tiempo total de la factorizacion
ax1.errorbar(x, t_media, yerr=t_std, marker="o", markersize=8, linewidth=2,
             capsize=4, color=AZUL, label="Tiempo (proceso más lento)")
ax1.axvline(bs.index(b_mejor), color=TINTA, linestyle="--", linewidth=1.2,
            label=f"Mejor b en (c) = {b_mejor}")
if b_a in bs and b_a != b_mejor:
    ax1.axvline(bs.index(b_a), color=GRIS, linestyle=":", linewidth=1.5,
                label=f"Mejor b en (a) = {b_a}")
ax1.set_ylabel("Tiempo de factorización [s]")
ax1.set_title("Tiempo total")
ax1.set_ylim(bottom=0)
ax1.legend(frameon=False)

# (2) Computo vs comunicacion (promedio por proceso)
ax2.bar(x, comp, width=0.6, color=AZUL, edgecolor="white", linewidth=2,
        label="Cómputo")
ax2.bar(x, comm, width=0.6, bottom=comp, color=NARANJO, edgecolor="white",
        linewidth=2, label="Comunicación")
ax2.set_ylabel("Tiempo promedio por proceso [s]")
ax2.set_title("Cómputo vs comunicación")
ax2.legend(frameon=False)

for ax in (ax1, ax2):
    ax.set_xticks(x)
    ax.set_xticklabels([str(b) for b in bs])
    ax.set_xlabel("Tamaño de bloque b")
    ax.grid(True, axis="y", alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)

rango = (f"{min(n_corr)}" if min(n_corr) == max(n_corr)
         else f"{min(n_corr)}–{max(n_corr)}")
fig.suptitle(f"LU distribuida, N = {N}, grid {pr}×{pc}, T = {T} "
             f"(promedio de {rango} corridas, barras = desv. estándar)")
fig.tight_layout()
fig.savefig("parte_c.png", dpi=200)
fig.savefig("parte_c.pdf")
print("Guardado en parte_c.png y parte_c.pdf")
