from joblib import Parallel, delayed
import numpy as np
import matplotlib 
import threadpoolctl
from data_generator import generate_dataset, normal, uniform
import random
from time import time

n = 100000
k = 300
B = 48 # resamples
X = generate_dataset(n, k)
real_beta = normal((k + 1, ))
noise = normal((n, )) # noise
y = (X @ real_beta) + noise

def bs_numpy(X, y):
    rows = uniform(n, (n, ))
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
for j in range(k + 1):
    beta_j = [beta[j] for beta in results]
    beta_j.sort()
    len_beta_j = len(beta_j)
    inferior = round(len_beta_j * 0.025)
    superior = round(len_beta_j * 0.975)
    # print(beta_j[inferior], beta_j[superior])