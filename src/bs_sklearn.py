import numpy as np
from sklearn.linear_model import LinearRegression
from joblib import Parallel, delayed
import time

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

def bs_sklearn(X, y, N, k, B, p, seed):
    # Parámetros del experimento definidos en tarea01.pdf
    # N = 100000
    # k = 300
    # B = 48
    n_jobs = p # Modificar según el p deseado para los experimentos
    
    # print("Generando datos...")
    # X, y, beta_star = generar_datos(N, k)
    
    print(f"Iniciando bootstrapping con {B} resamples y p={n_jobs} procesos...")
    inicio = time.time()
    
    # Paralelismo de tareas con joblib
    # Se pasa una semilla distinta a cada tarea para asegurar resamples independientes
    betas_boot = Parallel(n_jobs=n_jobs)(
        delayed(fit_resample)(X, y, seed) for seed in range(B)
    )
    
    tiempo_total = time.time() - inicio
    print(f"Tiempo de ejecución: {tiempo_total:.4f} segundos")
    
    # Paso 3: Construir el intervalo de confianza descartando el 2,5% inferior y superior
    betas_boot = np.array(betas_boot) # Dimensión: (B, k+1)
    
    # Calcula los percentiles 2.5 y 97.5 para cada coeficiente
    ic_inferior = np.percentile(betas_boot, 2.5, axis=0)
    ic_superior = np.percentile(betas_boot, 97.5, axis=0)
    
    # Verificación opcional de un coeficiente
    # print(f"\nCoeficiente beta_0 (verdadero): {beta_star[0]:.4f}")
    out: list[tuple[int, int]] = []
    for j in range(k + 1):
        beta_j = [beta[j] for beta in betas_boot]
        beta_j.sort()
        len_beta_j = len(beta_j)
        inferior = round(len_beta_j * 0.025)
        superior = round(len_beta_j * 0.975)
        out.append((beta_j[inferior], beta_j[superior]))
        # print(beta_j[inferior], beta_j[superior])
    return out
    # print(f"Intervalo de confianza 95%: [{ic_inferior[0]:.4f}, {ic_superior[0]:.4f}]")
    # return [(ic_inferior[0], ic_superior[0])]

# if __name__ == "__main__":
#     main()