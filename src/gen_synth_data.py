from typing import Any

import numpy as np

def gen_synthetic_data(seed: int = 0, N: int = 100000, k: int = 300, B: int = 48) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
  rng = np.random.default_rng(seed= seed)  # Set the seed for next steps
  beta_star = rng.normal(0, 1, k+1)
  X = np.zeros((N, k+1))
  X[:,1:] = rng.normal(0, 1, (N, k))
  noise = rng.normal(0, 1, N)
  y = np.matmul(X, beta_star)
  y = y + noise

  return (X, y, beta_star)
