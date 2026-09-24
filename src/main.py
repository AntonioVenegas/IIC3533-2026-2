
from gen_synth_data import gen_synthetic_data
from bs_auto import bs_auto
from bs_numpy import bs_numpy_parallel
from bs_sklearn import bs_sklearn
from intervals import compare_intervals, plot_comparison

N = 100000
k = 300
B = 48
p = 4

if __name__ == "__main__":
  X, y, beta = gen_synthetic_data(N, k, B)

  results = {
    "auto": bs_auto(X, y, p, B),
    "sklearn": bs_sklearn(X, y, B, p),
    "numpy": bs_numpy_parallel(X, y, B, p),
  }

  print()
  compare_intervals(results, beta)
  plot_comparison(results, beta)
