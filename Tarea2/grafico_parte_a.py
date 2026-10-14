import matplotlib.pyplot as plt

n = [2048, 1024, 512, 256, 128, 64, 32]
tiempos = {
    "Computador 1": [5425.50, 5398.57, 3093.14, 3336.35, 4313.99, 3245.57, 3342.32],
    "Computador 2": [6639.22, 5823.21, 4472.22, 3710.70, 4285.88, 4962.99, 5911.91],
    "Computador 3": [2807.91, 2589.23, 2400.75, 2372.43, 2123.01, 2796.28, 2991.96],
}
colores = ["#2a78d6", "#eb6834", "#1baf7a"]
marcadores = ["o", "s", "^"]

plt.rcParams.update({"font.size": 12})
fig, ax = plt.subplots(figsize=(8, 5))

for (nombre, t), color, m in zip(tiempos.items(), colores, marcadores):
    ax.plot(n, t, marker=m, markersize=8, linewidth=2, color=color, label=nombre)

ax.set_xscale("log", base=2)
ax.set_xticks(n)
ax.set_xticklabels([str(v) for v in n])
ax.invert_xaxis()  # de n = N (sin subdivision) a hojas mas pequenas
ax.set_ylim(bottom=0)

ax.set_title("Tiempo serial vs tamaño de bloque (N = 2048)")
ax.set_xlabel("Tamaño de bloque n")
ax.set_ylabel("Tiempo (ms)")
ax.grid(True, color="#e0e0e0", linewidth=0.8)
ax.set_axisbelow(True)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
ax.legend(frameon=False)

fig.tight_layout()
fig.savefig("grafico_parte_a.png", dpi=200)
plt.show()
