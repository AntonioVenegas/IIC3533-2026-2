import argparse
import numpy as np
from mpi4py import MPI
from scipy.linalg import lu_factor, solve_triangular
 
 
def matrix_entries(rows, cols, N):
    """Entradas A[rows, cols] de la matriz del problema (indices globales)."""
    I = np.asarray(rows, dtype=np.float64)[:, None]
    J = np.asarray(cols, dtype=np.float64)[None, :]
    A = np.sin(1e-3 * I * J + 0.3 * I + 0.7 * J)
    A[np.asarray(rows)[:, None] == np.asarray(cols)[None, :]] = N
    return A
 
 
def global_indices(blocks, b):
    """Indices globales (fila o columna) de una lista de bloques, en orden."""
    return (np.asarray(blocks)[:, None] * b + np.arange(b)[None, :]).ravel()

def distributed_check(A_loc, my_I, my_J, b, N, comm):
    """Compara A x con L (U x) para un vector aleatorio x, sin juntar la matriz.
 
    Cada proceso usa solo sus bloques: calcula su aporte a A x, U x y L y, y los
    aportes se suman entre todos con Allreduce (solo se comunican vectores de largo N).
    """
    grow = global_indices(my_I, b)        # filas globales de mi arreglo local
    gcol = global_indices(my_J, b)        # columnas globales de mi arreglo local
 
    x = np.random.default_rng(0).standard_normal(N)   # misma semilla: mismo x en todos
 
    # Se recorre por franjas de b filas para no crear copias grandes de la matriz
    def local_matvec(vec, which):
        part = np.zeros(N)
        v = vec[gcol]
        for s in range(0, len(grow), b):
            rows = grow[s:s + b]
            F = A_loc[s:s + b]                       # factores L\U guardados
            if which == "A":
                M = matrix_entries(rows, gcol, N)    # A original, regenerada
            elif which == "U":
                M = np.where(rows[:, None] <= gcol[None, :], F, 0.0)
            else:                                    # "L": parte estricta + unos en la diagonal
                M = np.where(rows[:, None] > gcol[None, :], F, 0.0)
                M[rows[:, None] == gcol[None, :]] = 1.0
            part[rows] = M @ v
        total = np.empty(N)
        comm.Allreduce(part, total, op=MPI.SUM)      # suma los aportes de todos los procesos
        return total
 
    Ax = local_matvec(x, "A")
    y = local_matvec(x, "U")       # y = U x
    z = local_matvec(y, "L")       # z = L y = L U x
    return np.linalg.norm(Ax - z) / np.linalg.norm(Ax)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--N", type=int, default=4096)
    parser.add_argument("--b", type=int, default=256)
    parser.add_argument("--pr", type=int, default=1)
    parser.add_argument("--pc", type=int, default=1)
    parser.add_argument("--check", action="store_true",
                        help="calcula ||A - LU|| / ||A|| (solo para N chico)")
    args = parser.parse_args()
    N, b, pr, pc = args.N, args.b, args.pr, args.pc
 
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
 
    if pr * pc != size:
        raise SystemExit(f"pr*pc = {pr*pc} no coincide con el numero de procesos {size}")
    if N % b != 0:
        raise SystemExit("Se asume que b divide a N")
 
    myrow, mycol = rank // pc, rank % pc
    row_comm = comm.Split(myrow, mycol)   # rango dentro de row_comm = mycol
    col_comm = comm.Split(mycol, myrow)   # rango dentro de col_comm = myrow
 
    nb = N // b                            # numero de bloques por lado
 
    # ---- Inicializacion: cada proceso genera SOLO sus bloques ----
    my_I = np.arange(myrow, nb, pr)        # filas de bloques globales que tengo
    my_J = np.arange(mycol, nb, pc)        # columnas de bloques globales que tengo
    A_loc = matrix_entries(global_indices(my_I, b), global_indices(my_J, b), N)
 
    t_comp = 0.0
    t_comm = 0.0
    comm.Barrier()
    t_start = MPI.Wtime()
 
    for k in range(nb):                    # k = indice de BLOQUE
        t0 = MPI.Wtime()
        r, c = k % pr, k % pc              # dueno de A_kk
 
        # Donde empieza la "esquina" (bloques con indice global > k) en mi arreglo local
        i0 = np.searchsorted(my_I, k, side="right") * b
        j0 = np.searchsorted(my_J, k, side="right") * b
        n_rows = A_loc.shape[0] - i0       # filas de la submatriz restante
        n_cols = A_loc.shape[1] - j0       # columnas de la submatriz restante
 
        # Posicion local de la fila/columna de bloques k (solo valida si me corresponde)
        lr = (k // pr) * b
        lc = (k // pc) * b
 
        # ---- 1. Bloque diagonal ----
        if myrow == r and mycol == c:
            lu, piv = lu_factor(A_loc[lr:lr + b, lc:lc + b], check_finite=False)
            assert np.all(piv == np.arange(b)), "lu_factor hizo pivoteo"
            A_loc[lr:lr + b, lc:lc + b] = lu
            diag = np.ascontiguousarray(lu)
        else:
            diag = np.empty((b, b))
        t_comp += MPI.Wtime() - t0
 
        t0 = MPI.Wtime()
        if myrow == r:                     # solo la fila r necesita A_kk (panel U)
            row_comm.Bcast(diag, root=c)
        if mycol == c:                     # solo la columna c necesita A_kk (panel L)
            col_comm.Bcast(diag, root=r)
        t_comm += MPI.Wtime() - t0
 
        # ---- 2a. Panel de U (procesos de la fila r) ----
        t0 = MPI.Wtime()
        if myrow == r:
            U = solve_triangular(diag, A_loc[lr:lr + b, j0:], lower=True,
                                 unit_diagonal=True, check_finite=False)
            A_loc[lr:lr + b, j0:] = U
            U_panel = np.ascontiguousarray(U)
        else:
            U_panel = np.empty((b, n_cols))
 
        # ---- 2b. Panel de L (procesos de la columna c) ----
        if mycol == c:
            L = solve_triangular(diag, A_loc[i0:, lc:lc + b].T, trans="T",
                                 lower=False, check_finite=False).T
            A_loc[i0:, lc:lc + b] = L
            L_panel = np.ascontiguousarray(L)
        else:
            L_panel = np.empty((n_rows, b))
        t_comp += MPI.Wtime() - t0
 
        # ---- Envio de paneles ----
        t0 = MPI.Wtime()
        col_comm.Bcast(U_panel, root=r)    # en cada columna, la fila r difunde sus U_kj
        row_comm.Bcast(L_panel, root=c)    # en cada fila, la columna c difunde sus L_ik
        t_comm += MPI.Wtime() - t0
 
        # ---- 3. Actualizacion: una sola multiplicacion ----
        t0 = MPI.Wtime()
        if n_rows > 0 and n_cols > 0:
            A_loc[i0:, j0:] -= L_panel @ U_panel
        t_comp += MPI.Wtime() - t0
 
    t_total = MPI.Wtime() - t_start

    # ---- Reporte de tiempos por proceso ----
    times = comm.gather((rank, myrow, mycol, t_comp, t_comm, t_total), root=0)
    if rank == 0:
        print(f"N={N} b={b} grid={pr}x{pc}")
        print("rank (fila,col)  computo[s]  comunic.[s]  total[s]")
        for rk, mr, mc, tc, tm, tt in times:
            print(f"{rk:4d} ({mr},{mc})      {tc:9.4f}  {tm:10.4f}  {tt:8.4f}")
 
    # ---- Verificacion distribuida (opcional, fuera de la medicion de tiempos) ----
    if args.check:
        res = distributed_check(A_loc, my_I, my_J, b, N, comm)
        if rank == 0:
            print(f"||Ax - L(Ux)|| / ||Ax|| = {res:.3e}")

if __name__ == "__main__":
    main()