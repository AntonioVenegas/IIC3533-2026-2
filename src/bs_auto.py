import numpy as np
from sklearn.ensemble import BaggingRegressor
from sklearn.linear_model import LinearRegression

def bs_auto(X: np.ndarray, y: np.ndarray, p: int = 1, B: int = 48):
  regr = BaggingRegressor(
    estimator=LinearRegression(),
    n_estimators= B,
    n_jobs=p
  ).fit(X, y)

  coefficients = np.array([
    estimator.coef_ for estimator in regr.estimators_ # type: ignore
  ], dtype=np.float64)

  # Optional: average coefficients across the fitted estimators
  mean_coefficients = coefficients.mean(axis=0)

  return coefficients, mean_coefficients