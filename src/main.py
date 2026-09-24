
from gen_synth_data import gen_synthetic_data
from bs_auto import bs_auto
from bs_numpy import bs_numpy_parallel
from bs_sklearn import bs_sklearn

N = 100000
k = 300
B = 48

if __name__ == "__main__":
  X, y, beta = gen_synthetic_data(N, k, B)

  # coef_auto, coef_mean_auto = bs_auto(X, y, 4, B)
  # print("coefs auto: ")
  # print(coef_auto)

  print("\n")

  coef_sklearn = bs_sklearn(X, y, N, k, B, 4, 0)
  print("coefs sklearn: ")
  print(coef_sklearn)
  
  print("\n")

  # coef_numpy = bs_numpy_parallel(X, y, N, k, B)
  # print("coefs numpy: ")
  # print(coef_numpy)


