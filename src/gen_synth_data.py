from typing import Any

import numpy as np

rng = np.random.default_rng(seed=0)  # Set the seed for next steps

def gen_synthetic_data(N: int = 100000, k: int = 300, B: int = 48) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
  beta_star = rng.normal(0, 1, k+1)
  X = np.zeros((N, k+1))
  X[:,1:] = rng.normal(0, 1, (N, k))
  X[:,0] = 1
  noise = rng.normal(0, 1, N)
  y = np.matmul(X, beta_star)
  y = y + noise

  return (X, y, beta_star)

def uniform(limit: int, size: tuple):
  return rng.choice(limit, size=size, replace=True) 