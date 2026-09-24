import numpy as np
from sklearn.ensemble import BaggingRegressor
from sklearn.linear_model import LinearRegression
from time import time

from intervals import confidence_intervals

def bs_auto(X: np.ndarray, y: np.ndarray, p: int = 1, B: int = 48, seed: int = 0) -> np.ndarray:
  start = time()
  regr = BaggingRegressor(
    # fit_intercept=False porque X ya tiene la columna de unos
    estimator=LinearRegression(fit_intercept=False),
    n_estimators=B,
    n_jobs=p,
    random_state=seed,
  ).fit(X, y)
  print(f"Tiempo bs_auto: {time() - start:.4f} segundos")

  coefficients = np.array([
    estimator.coef_ for estimator in regr.estimators_ # type: ignore
  ], dtype=np.float64)

  return confidence_intervals(coefficients)
