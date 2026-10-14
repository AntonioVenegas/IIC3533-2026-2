import numpy as np


def confidence_intervals(betas: np.ndarray) -> np.ndarray:
  """Intervalo 95% por coeficiente descartando el 2,5% inferior y superior.

  betas: matriz (B, k+1) con los beta_hat de cada resample.
  Retorna una matriz (k+1, 2) con columnas [inferior, superior].
  """
  betas_sorted = np.sort(betas, axis=0)
  B = betas_sorted.shape[0]
  inferior = round(B * 0.025)
  superior = min(round(B * 0.975), B - 1)
  return np.column_stack((betas_sorted[inferior], betas_sorted[superior]))


def coverage(intervals: np.ndarray, real_beta: np.ndarray) -> float:
  """Porcentaje de coeficientes reales que caen dentro de su intervalo."""
  inside = (intervals[:, 0] <= real_beta) & (real_beta <= intervals[:, 1])
  return 100 * inside.mean()


def compare_intervals(results: dict[str, np.ndarray], real_beta: np.ndarray):
  names = list(results)

  print(f"{'metodo':<10} {'cobertura':>10} {'ancho medio':>12}")
  for name in names:
    iv = results[name]
    width = (iv[:, 1] - iv[:, 0]).mean()
    print(f"{name:<10} {coverage(iv, real_beta):>9.2f}% {width:>12.5f}")

  print()
  print(f"{'par':<20} {'|dif inf|':>10} {'|dif sup|':>10} {'max |dif|':>10}")
  for i, a in enumerate(names):
    for b in names[i + 1:]:
      diff = np.abs(results[a] - results[b])
      print(f"{a + ' vs ' + b:<20} {diff[:, 0].mean():>10.5f} "
            f"{diff[:, 1].mean():>10.5f} {diff.max():>10.5f}")


def plot_comparison(results: dict[str, np.ndarray], real_beta: np.ndarray, path: str = "comparacion_intervalos.png"):
  import matplotlib
  matplotlib.use("Agg")
  import matplotlib.pyplot as plt

  names = list(results)
  metodo_rows = []
  for name in names:
    iv = results[name]
    width = (iv[:, 1] - iv[:, 0]).mean()
    metodo_rows.append([name, f"{coverage(iv, real_beta):.2f}%", f"{width:.5f}"])

  par_rows = []
  for i, a in enumerate(names):
    for b in names[i + 1:]:
      diff = np.abs(results[a] - results[b])
      par_rows.append([f"{a} vs {b}", f"{diff[:, 0].mean():.5f}",
                       f"{diff[:, 1].mean():.5f}", f"{diff.max():.5f}"])

  fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 4))
  tables = [
    (ax1, metodo_rows, ["método", "cobertura", "ancho medio"], "Cobertura por método"),
    (ax2, par_rows, ["par", "|dif inf|", "|dif sup|", "max |dif|"], "Diferencias entre intervalos"),
  ]
  for ax, rows, cols, title in tables:
    ax.axis("off")
    ax.set_title(title, fontweight="bold")
    table = ax.table(cellText=rows, colLabels=cols, loc="center", cellLoc="center")
    table.scale(1, 1.4)
    for (r, _), cell in table.get_celld().items():
      if r == 0:
        cell.set_text_props(fontweight="bold")
        cell.set_facecolor("#e6e6e6")

  fig.tight_layout()
  fig.savefig(path, dpi=150)
  print(f"Tabla guardada en {path}")
