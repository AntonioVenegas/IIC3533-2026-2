# Graficos y tablas de la parte (d): LU distribuida, N = 8192, configuraciones 0 a 3
# (un nodo), con b = 512 (mejor en (a)) y b = 1024 (mejor en (c)).
# Lee el CSV que escribe lu_distributed.py (una fila por proceso y corrida).
# Uso: python plot_parte_d.py [--csv resultados_parte_d.csv]
#
# - Tiempo de una corrida = el del proceso mas lento (max del total entre ranks).
# - Speedup S = T(1x1, T=1) / T(config), con el mismo b.
# - Eficiencia E = S / (p * T), con p * T = CPUs totales usadas.
# - Computo / comunicacion = promedio entre ranks y corridas.

import argparse
import csv
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--csv", default="resultados_parte_d.csv")
args = parser.parse_args()

# ---- Lectura: agrupar filas por corrida ----
with open(args.csv) as f:
    filas = list(csv.DictReader(f))
if not filas:
    raise SystemExit(f"{args.csv} esta vacio")
N = int(filas[0]["N"])

# El rank 0 escribe las p filas de cada corrida juntas: se recorre en bloques de p.
corridas = defaultdict(list)      # (b, pr, pc, T) -> lista de corridas
i = 0
while i < len(filas):
    pr, pc = int(filas[i]["pr"]), int(filas[i]["pc"])
    bloque = filas[i:i + pr * pc]
    clave = (int(bloque[0]["b"]), pr, pc, int(bloque[0]["T"]))
    corridas[clave].append(bloque)
    i += pr * pc

CONFIG = {(1, 1): 0, (1, 2): 1, (2, 1): 1, (2, 2): 2, (2, 4): 3, (4, 2): 3}
bs = sorted({k[0] for k in corridas})
# Orden del eje x: CPUs totales, luego numero de procesos, luego forma del grid
combos = sorted({k[1:] for k in corridas},
                key=lambda c: (c[0] * c[1] * c[2], c[0] * c[1], c[0]))

res = {}   # (b, pr, pc, T) -> dict con metricas
for b in bs:
    t1 = np.mean([max(float(r["total"]) for r in c) for c in corridas[(b, 1, 1, 1)]])
    for pr, pc, T in combos:
        cs = corridas[(b, pr, pc, T)]
        t = np.array([max(float(r["total"]) for r in c) for c in cs])
        s = t1 / t
        cpus = pr * pc * T
        res[(b, pr, pc, T)] = dict(
            n=len(t), t=t.mean(), t_std=t.std(), S=s.mean(), S_std=s.std(),
            E=s.mean() / cpus, E_std=s.std() / cpus, cpus=cpus,
            comp=np.mean([float(r["computo"]) for c in cs for r in c]),
            comm=np.mean([float(r["comunicacion"]) for c in cs for r in c]))

# ---- Tablas (consola + markdown para el informe) ----
md = []
for b in bs:
    enc = (f"| Config | Grid | T | CPUs | Tiempo [s] | Speedup | Eficiencia "
           f"| Cómputo [s] | Comunic. [s] | % comunic. |")
    md += [f"\n### b = {b}  (N = {N}, promedio de 3 corridas)\n", enc,
           "|" + "---|" * 10]
    print(f"\n===== b = {b} =====")
    print(f"{'cfg':>3} {'grid':>5} {'T':>2} {'CPUs':>4} {'tiempo [s]':>15} "
          f"{'speedup':>13} {'efic.':>6} {'comp':>6} {'comm':>6} {'%comm':>6}")
    for pr, pc, T in combos:
        m = res[(b, pr, pc, T)]
        pct = 100 * m["comm"] / (m["comp"] + m["comm"])
        cfg = CONFIG[(pr, pc)]
        print(f"{cfg:>3} {pr}x{pc:<3} {T:>2} {m['cpus']:>4} "
              f"{m['t']:>7.2f} ± {m['t_std']:<5.2f} {m['S']:>5.2f} ± {m['S_std']:<5.2f}"
              f"{m['E']:>6.2f} {m['comp']:>6.2f} {m['comm']:>6.2f} {pct:>5.1f}%")
        md.append(f"| {cfg} | {pr}×{pc} | {T} | {m['cpus']} | "
                  f"{m['t']:.2f} ± {m['t_std']:.2f} | {m['S']:.2f} | {m['E']:.2f} | "
                  f"{m['comp']:.2f} | {m['comm']:.2f} | {pct:.0f}% |")

# Mejor combinacion por cantidad de CPUs (eleccion de T)
md += ["\n### Mejor combinación (p, T) para cada cantidad de CPUs\n",
       "| CPUs | b | Mejor grid y T | Tiempo [s] | Speedup | Eficiencia |", "|---|---|---|---|---|---|"]
print("\n===== Mejor (grid, T) para cada cantidad de CPUs =====")
for cpus in sorted({res[k]["cpus"] for k in res}):
    for b in bs:
        cand = [(res[(b, *c)]["t"], c) for c in combos if res[(b, *c)]["cpus"] == cpus]
        t, (pr, pc, T) = min(cand)
        m = res[(b, pr, pc, T)]
        print(f"CPUs={cpus} b={b}: {pr}x{pc} T={T}  t={t:.2f}s  S={m['S']:.2f}  E={m['E']:.2f}")
        md.append(f"| {cpus} | {b} | {pr}×{pc}, T={T} | {t:.2f} | {m['S']:.2f} | {m['E']:.2f} |")

with open("tabla_parte_d.md", "w") as f:
    f.write("\n".join(md) + "\n")

# ---- Graficos ----
AZUL, NARANJO = "#2a78d6", "#eb6834"
GRIS, TINTA = "#8a8984", "#52514e"
COLOR_B = {bs[0]: AZUL, bs[-1]: NARANJO}
plt.rcParams.update({"font.size": 13, "axes.edgecolor": GRIS,
                     "xtick.color": TINTA, "ytick.color": TINTA})

etiquetas = [f"{pr}×{pc}\nT={T}" for pr, pc, T in combos]
x = np.arange(len(combos))
ancho = 0.38
cpus_combo = [pr * pc * T for pr, pc, T in combos]
# Separadores verticales entre grupos de igual cantidad de CPUs
cortes = [j - 0.5 for j in range(1, len(combos)) if cpus_combo[j] != cpus_combo[j - 1]]


def decorar(ax, ylabel):
    ax.set_xticks(x)
    ax.set_xticklabels(etiquetas, fontsize=11)
    ax.set_ylabel(ylabel)
    ax.set_xlim(-0.6, len(combos) - 0.4)
    ax.grid(True, axis="y", alpha=0.3)
    ax.spines[["top", "right"]].set_visible(False)
    for c in cortes:
        ax.axvline(c, color=GRIS, linewidth=0.8, alpha=0.6)


def rotular_cpus(ax, y):
    # Nombre de cada grupo de CPUs sobre el grafico
    inicio = -0.5
    for fin in cortes + [len(combos) - 0.5]:
        j = int(inicio + 0.5)
        ax.text((inicio + fin) / 2, y, f"{cpus_combo[j]} CPU" + ("s" if cpus_combo[j] > 1 else ""),
                ha="center", va="bottom", fontsize=11, color=TINTA,
                transform=ax.get_xaxis_transform())
        inicio = fin


# Figura 1: speedup y eficiencia
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 9.5), sharex=True)
for k, b in enumerate(bs):
    off = (k - 0.5) * ancho
    S = [res[(b, *c)]["S"] for c in combos]
    Ss = [res[(b, *c)]["S_std"] for c in combos]
    E = [res[(b, *c)]["E"] for c in combos]
    Es = [res[(b, *c)]["E_std"] for c in combos]
    ax1.bar(x + off, S, ancho, yerr=Ss, capsize=3, color=COLOR_B[b],
            edgecolor="white", linewidth=2, label=f"b = {b}", error_kw={"ecolor": TINTA})
    ax2.bar(x + off, E, ancho, yerr=Es, capsize=3, color=COLOR_B[b],
            edgecolor="white", linewidth=2, label=f"b = {b}", error_kw={"ecolor": TINTA})
# Speedup ideal = CPUs totales
ax1.hlines(cpus_combo, x - 0.45, x + 0.45, colors=TINTA, linestyles="--",
           linewidth=1.5, label="Ideal (= CPUs)")
ax1.set_title("Speedup  S = T(1×1, T=1) / T(p, T)", pad=26)
ax2.axhline(1, color=TINTA, linestyle="--", linewidth=1.5, label="Ideal")
ax2.set_title("Eficiencia  E = S / (p·T)")
ax2.set_ylim(0, 1.1)
decorar(ax1, "Speedup")
decorar(ax2, "Eficiencia")
ax1.set_ylim(0, 9)
rotular_cpus(ax1, 1.0)
ax1.legend(frameon=False, loc="upper left", ncol=3)
ax2.set_xlabel("Grid de procesos (pr × pc) y threads por proceso T")
fig.suptitle(f"LU distribuida en un nodo, N = {N}: configuraciones 0–3 "
             f"(promedio de 3 corridas, barras = desv. estándar)")
fig.tight_layout()
fig.savefig("parte_d_speedup.png", dpi=200)
fig.savefig("parte_d_speedup.pdf")

# Figura 2: computo vs comunicacion (promedio por proceso) y tiempo total
fig, axs = plt.subplots(1, len(bs), figsize=(16, 5.8), sharey=True)
for ax, b in zip(np.atleast_1d(axs), bs):
    comp = np.array([res[(b, *c)]["comp"] for c in combos])
    comm = np.array([res[(b, *c)]["comm"] for c in combos])
    tot = np.array([res[(b, *c)]["t"] for c in combos])
    ax.bar(x, comp, 0.65, color=AZUL, edgecolor="white", linewidth=2, label="Cómputo")
    ax.bar(x, comm, 0.65, bottom=comp, color=NARANJO, edgecolor="white",
           linewidth=2, label="Comunicación")
    ax.plot(x, tot, "o", color=TINTA, markersize=8, label="Tiempo total (proceso más lento)")
    ax.set_title(f"b = {b}", pad=26)
    decorar(ax, "Tiempo [s]" if b == bs[0] else "")
    ax.set_xticklabels(etiquetas, fontsize=10)
    rotular_cpus(ax, 1.0)
    ax.set_xlabel("Grid (pr × pc) y T")
np.atleast_1d(axs)[0].legend(frameon=False, loc="upper right")
fig.suptitle(f"Cómputo vs comunicación por proceso (promedio entre procesos y corridas), N = {N}",
             y=0.995)
fig.tight_layout()
fig.savefig("parte_d_tiempos.png", dpi=200)
fig.savefig("parte_d_tiempos.pdf")
print("\nGuardado: parte_d_speedup.{png,pdf}, parte_d_tiempos.{png,pdf}, tabla_parte_d.md")
