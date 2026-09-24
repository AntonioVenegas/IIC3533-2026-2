from joblib import Parallel, delayed
import numpy as np
import matplotlib 
import threadpoolctl
import random
from gen_synth_data import gen_synthetic_data, uniform
from time import time

# X, y, real_beta = gen_synthetic_data()
# n = 100000
# k = 300
# B = 48

def bs_numpy_parallel(X: np.ndarray, y: np.ndarray, N: int = 100000, k: int = 300, B: int = 48):
    def bs_numpy(X: np.ndarray, y: np.ndarray):
        rows = uniform(N, (N, ))
        X_b = X[rows, :]
        y_b = y[rows]
        A = X_b.T @ X_b
        b = X_b.T @ y_b
        return np.linalg.solve(A, b)

    beta_hat = np.linalg.solve(X.transpose() @ X, X.transpose() @ y) # beta_hat sobre todo el dataset

    # bootstrap con joblib
    start = time()
    results = Parallel (n_jobs=4) (
        delayed(bs_numpy)(X, y) for _ in range(B)
    )
    print(time() - start)
    # calcular el intervalo de confianza con los vectores beta_hat_j
    out: list[tuple[int, int]] = []
    for j in range(k + 1):
        beta_j = [beta[j] for beta in results]
        beta_j.sort()
        len_beta_j = len(beta_j)
        inferior = round(len_beta_j * 0.025)
        superior = round(len_beta_j * 0.975)
        out.append((beta_j[inferior], beta_j[superior]))
        # print(beta_j[inferior], beta_j[superior])
    return out