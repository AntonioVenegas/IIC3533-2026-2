import numpy as np

rng = np.random.default_rng(42)

def normal(size: tuple):
    return rng.normal(0, 1, size)

def uniform(limit: int, size: tuple):
    return rng.choice(limit, size=size, replace=True)

def generate_dataset(N: int, k: int):
    X = normal((N, k + 1))
    X[:, 0] = 1
    return X
