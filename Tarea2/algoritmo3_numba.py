# python algoritmo3_numba.py --N 2048
# por default es 1
'''
python algoritmo3_numba.py --N 2048 --hilos 1
python algoritmo3_numba.py --N 2048 --hilos 2
python algoritmo3_numba.py --N 2048 --hilos 4
python algoritmo3_numba.py --N 2048 --hilos 8
'''

from __future__ import annotations

import argparse
import time

import numpy as np
from numba import njit, prange, set_num_threads


@njit(parallel=True)
def multiplicar_paralelo(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    # Calcula C = A * B paralelizando las filas de C
    N = A.shape[0]
    C = np.zeros((N, N), dtype=np.float64)

    for i in prange(N):
        for k in range(N):
            a = A[i, k]
            for j in range(N):
                C[i, j] += a * B[k, j]

    return C


def inicializar_matriz(N: int, offset: float) -> np.ndarray:
    filas = np.arange(N, dtype=np.float64)[:, None]
    columnas = np.arange(N, dtype=np.float64)[None, :]
    return np.sin(0.1 * filas + 0.3 * columnas + offset)


def medir(A: np.ndarray, B: np.ndarray, hilos: int) -> float:
    set_num_threads(hilos)
    inicio = time.perf_counter()
    multiplicar_paralelo(A, B)
    return time.perf_counter() - inicio


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--N", type=int, default=2048)
    parser.add_argument("--hilos", type=int, default=1)
    args = parser.parse_args()

    A = inicializar_matriz(args.N, 1.0)
    B = inicializar_matriz(args.N, 2.0)
    set_num_threads(args.hilos)
    resultado_warmup = multiplicar_paralelo(A, B)
    checksum = float(np.sum(resultado_warmup))

    segundos = medir(A, B, args.hilos)
    print(
        f"N={args.N} hilos={args.hilos} tiempo={1000 * segundos:.2f} ms "
        f"checksum={checksum:.6f}"
    )


if __name__ == "__main__":
    main()