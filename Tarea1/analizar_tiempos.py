import csv
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


METODOS = ["auto", "sklearn", "numpy"]


def leer_tiempos(path="tiempos.csv"):
  tiempos = defaultdict(dict)
  with open(path, newline="", encoding="utf-8") as archivo:
    for fila in csv.DictReader(archivo):
      tiempos[fila["metodo"]][int(fila["p"])] = float(fila["tiempo_segundos"])
  return tiempos


def calcular_metricas(tiempos):
  metricas = []
  for metodo in METODOS:
    t_uno = tiempos[metodo][1]
    for p in sorted(tiempos[metodo]):
      tiempo = tiempos[metodo][p]
      speedup = t_uno / tiempo
      eficiencia = speedup / p
      metricas.append((p, metodo, tiempo, speedup, eficiencia))
  return metricas


def guardar_metricas(metricas, path="metricas_tiempos.csv"):
  with open(path, "w", newline="", encoding="utf-8") as archivo:
    escritor = csv.writer(archivo)
    escritor.writerow([
      "p", "metodo", "tiempo_segundos", "speedup", "eficiencia"
    ])
    escritor.writerows(metricas)
  print(f"Tabla de métricas guardada en {path}")


def calcular_overhead(tiempos):
  overhead = []
  for metodo in METODOS:
    t_uno = tiempos[metodo][1]
    for p in sorted(tiempos[metodo]):
      tiempo = tiempos[metodo][p]
      overhead.append((p, metodo, p * tiempo - t_uno))
  return overhead


def guardar_overhead(overhead, path="overhead_tiempos.csv"):
  with open(path, "w", newline="", encoding="utf-8") as archivo:
    escritor = csv.writer(archivo)
    escritor.writerow(["p", "metodo", "overhead_segundos"])
    escritor.writerows(overhead)
  print(f"Tabla de overhead guardada en {path}")


def plot_overhead(overhead, path="overhead_tiempos.png"):
  fig, ax = plt.subplots(figsize=(8, 5))
  colores = {"auto": "#1f77b4", "sklearn": "#ff7f0e", "numpy": "#2ca02c"}
  for metodo in METODOS:
    filas = [fila for fila in overhead if fila[1] == metodo]
    ax.plot(
      [fila[0] for fila in filas],
      [fila[2] for fila in filas],
      marker="o",
      color=colores[metodo],
      label=metodo,
    )
  ax.axhline(0, color="black", linestyle="--", label="ideal")
  ax.set_xlabel("Número de procesos (p)")
  ax.set_ylabel("Overhead $T_o(p)$ (segundos)")
  ax.set_title("Overhead según el número de procesos")
  ax.set_xticks(sorted({fila[0] for fila in overhead}))
  ax.grid(True, alpha=0.3)
  ax.legend()
  fig.tight_layout()
  fig.savefig(path, dpi=150)
  plt.close(fig)
  print(f"Gráfico de overhead guardado en {path}")


def plot_metricas(tiempos, metricas, path="metricas_tiempos.png"):
  p_valores = sorted({fila[0] for fila in metricas})
  metricas_por_metodo = {
    metodo: [fila for fila in metricas if fila[1] == metodo]
    for metodo in METODOS
  }

  fig, ejes = plt.subplots(1, 3, figsize=(16, 5))
  titulos = ["Tiempo T(p)", "Speedup S(p)", "Eficiencia E(p)"]
  indices = [2, 3, 4]
  colores = {"auto": "#1f77b4", "sklearn": "#ff7f0e", "numpy": "#2ca02c"}

  for eje, titulo, indice in zip(ejes, titulos, indices):
    for metodo in METODOS:
      filas = metricas_por_metodo[metodo]
      valores = [fila[indice] for fila in filas]
      eje.plot(
        p_valores,
        valores,
        marker="o",
        color=colores[metodo],
        label=metodo,
      )

    if indice == 2:
      for metodo in METODOS:
        t_uno = tiempos[metodo][1]
        eje.plot(
          p_valores,
          [t_uno / p for p in p_valores],
          linestyle="--",
          color=colores[metodo],
          alpha=0.7,
          label=f"ideal {metodo}",
        )
      eje.set_ylabel("Segundos")
    elif indice == 3:
      eje.plot(p_valores, p_valores, "k--", label="ideal")
      eje.set_ylabel("Speedup")
    else:
      eje.plot(p_valores, [1] * len(p_valores), "k--", label="ideal")
      eje.set_ylabel("Eficiencia")

    eje.set_xlabel("Número de procesos (p)")
    eje.set_title(titulo)
    eje.set_xticks(p_valores)
    eje.grid(True, alpha=0.3)

  ejes[0].legend(fontsize="small", ncol=2)
  fig.suptitle("Escalabilidad de las tres versiones", fontweight="bold")
  fig.tight_layout()
  fig.savefig(path, dpi=150)
  plt.close(fig)
  print(f"Gráfico de métricas guardado en {path}")


if __name__ == "__main__":
  tiempos = leer_tiempos()
  metricas = calcular_metricas(tiempos)
  overhead = calcular_overhead(tiempos)
  guardar_metricas(metricas)
  guardar_overhead(overhead)
  plot_metricas(tiempos, metricas)
  plot_overhead(overhead)

  for metodo in METODOS:
    t_uno = tiempos[metodo][1]
    print(f"T(1) {metodo}: {t_uno:.4f} segundos")
