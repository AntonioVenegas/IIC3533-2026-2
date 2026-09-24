import numpy as np
from sklearn.ensemble import BaggingRegressor
from sklearn.linear_model import LinearRegression

def bs_auto(X: np.ndarray, y: np.ndarray, p: int = 1):
  regr = BaggingRegressor(
    estimator=LinearRegression(),
    n_jobs=p
  ).fit(X, y)

  print(regr.get_params())