from joblib import Parallel, delayed
import numpy as np
from time import time

from intervals import confidence_intervals

def bs_numpy(X: np.ndarray, y: np.ndarray, seed: int):
    # rng propio por tarea: el rng global de gen_synth_data se reinicia con la
    # misma semilla en cada proceso de joblib y repetiría los resamples
    rng = np.random.default_rng(seed)
    N = X.shape[0]
    rows = rng.choice(N, size=N, replace=True)
    X_b = X[rows, :]
    y_b = y[rows]
    A = X_b.T @ X_b
    b = X_b.T @ y_b
    return np.linalg.solve(A, b)

def bs_numpy_parallel(X: np.ndarray, y: np.ndarray, B: int = 48, p: int = 4, seed: int = 0) -> np.ndarray:
    # bootstrap con joblib
    start = time()
    results = Parallel(n_jobs=p)(
        delayed(bs_numpy)(X, y, seed + i) for i in range(B)
    )
    print(f"Tiempo bs_numpy: {time() - start:.4f} segundos")

    # calcular el intervalo de confianza con los vectores beta_hat_j
    return confidence_intervals(np.array(results))
