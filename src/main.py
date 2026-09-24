
from gen_synth_data import gen_synthetic_data
from bs_auto import bs_auto
from bs_numpy import bs_numpy_parallel
from bs_sklearn import bs_sklearn
from intervals import compare_intervals, plot_comparison
import csv
from time import perf_counter

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

N = 100000
k = 300
B = 48
P_MAX = 8


def ejecutar_benchmark(X, y):
  metodos = {
    "auto": lambda p: bs_auto(X, y, p, B),
    "sklearn": lambda p: bs_sklearn(X, y, B, p),
    "numpy": lambda p: bs_numpy_parallel(X, y, B, p),
  }
  tiempos = []
  resultados = {}

  for p in range(1, P_MAX + 1):
    print(f"\nProcesos: p={p}")
    for nombre, metodo in metodos.items():
      inicio = perf_counter()
      resultados[nombre] = metodo(p)
      tiempo = perf_counter() - inicio
      tiempos.append((p, nombre, tiempo))
      print(f"Tiempo total {nombre}: {tiempo:.4f} segundos")

  return tiempos, resultados


def guardar_tiempos(tiempos, path="tiempos.csv"):
  with open(path, "w", newline="", encoding="utf-8") as archivo:
    escritor = csv.writer(archivo)
    escritor.writerow(["p", "metodo", "tiempo_segundos"])
    escritor.writerows(tiempos)
  print(f"Tabla de tiempos guardada en {path}")


def plot_tiempos(tiempos, path="tiempos_vs_procesos.png"):
  nombres = ["auto", "sklearn", "numpy"]
  fig, ax = plt.subplots(figsize=(8, 5))
  for nombre in nombres:
    datos = [(p, tiempo) for p, metodo, tiempo in tiempos if metodo == nombre]
    ax.plot(*zip(*datos), marker="o", label=nombre)
  ax.set_xlabel("Número de procesos (p)")
  ax.set_ylabel("Tiempo de ejecución (segundos)")
  ax.set_title("Tiempo de ejecución según el número de procesos")
  ax.set_xticks(range(1, P_MAX + 1))
  ax.grid(True, alpha=0.3)
  ax.legend(title="Versión")
  fig.tight_layout()
  fig.savefig(path, dpi=150)
  plt.close(fig)
  print(f"Gráfico de tiempos guardado en {path}")

if __name__ == "__main__":
  X, y, beta = gen_synthetic_data(N, k, B)

  tiempos, results = ejecutar_benchmark(X, y)
  guardar_tiempos(tiempos)
  plot_tiempos(tiempos)

  print()
  compare_intervals(results, beta)
  plot_comparison(results, beta)
