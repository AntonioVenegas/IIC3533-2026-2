import numpy as np
from sklearn.linear_model import LinearRegression
from joblib import Parallel, delayed
import time

from intervals import confidence_intervals

def generar_datos(N=100000, k=300, seed=42):
    """Genera los datos sintéticos según el ítem (a) de tarea01.pdf."""
    rng = np.random.default_rng(seed)
    
    # (I) Muestrear los k+1 coeficientes verdaderos
    beta_star = rng.standard_normal(k + 1)
    
    # (II) Generar matriz X con columna de unos al inicio
    X_raw = rng.standard_normal((N, k))
    ones_col = np.ones((N, 1))
    X = np.hstack((ones_col, X_raw))
    
    # (III) Calcular y = X * beta* + ruido
    ruido = rng.standard_normal(N)
    y = X @ beta_star + ruido
    
    return X, y, beta_star

def fit_resample(X, y, seed):
    """
    (I) Sortea N índices con reemplazo.
    (II) Toma las filas de X e y.
    (III) Calcula el estimador usando scikit-learn.
    """
    rng = np.random.default_rng(seed)
    N = X.shape[0]
    
    # Muestreo con reemplazo
    indices = rng.choice(N, size=N, replace=True)
    X_b = X[indices]
    y_b = y[indices]
    
    # fit_intercept=False porque X ya tiene la columna de unos
    modelo = LinearRegression(fit_intercept=False)
    modelo.fit(X_b, y_b)
    
    return modelo.coef_

def bs_sklearn(X, y, B, p, seed=0):
    print(f"Iniciando bootstrapping con {B} resamples y p={p} procesos...")
    inicio = time.time()

    # Paralelismo de tareas con joblib
    # Se pasa una semilla distinta a cada tarea para asegurar resamples independientes
    betas_boot = Parallel(n_jobs=p)(
        delayed(fit_resample)(X, y, seed + i) for i in range(B)
    )

    tiempo_total = time.time() - inicio
    print(f"Tiempo bs_sklearn: {tiempo_total:.4f} segundos")

    # Construir el intervalo de confianza descartando el 2,5% inferior y superior
    return confidence_intervals(np.array(betas_boot))
