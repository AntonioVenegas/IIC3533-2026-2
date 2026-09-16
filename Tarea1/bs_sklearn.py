from joblib import Parallel, delayed
import numpy as np
import matplotlib 
import threadpoolctl
from sklearn.ensemble import BaggingRegressor 
from sklearn.linear_model import LinearRegression
from data_generator import generate_dataset, normal

n = 10000
k = 300
B = 48
X = generate_dataset(n, k)
beta = normal((k + 1, ))
N = normal((n, )) # noise
y = (X @ beta) + N

def bs_sklearn(X, y):
    pass


print(bs_sklearn(X, y))