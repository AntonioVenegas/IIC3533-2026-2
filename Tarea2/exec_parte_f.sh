#!/usr/bin/env bash
# Parte f) Escalabilidad debil.
# Mide T(p, N) en (p=1, N=1024), (p=2, N=2048) y (p=4, N=4096) con los tres algoritmos
# (lo que usa la eficiencia debil) y guarda cada corrida en un CSV (algoritmo,N,p,rep,tiempo_ms).
# Uso: ./exec_parte_f.sh [salida.csv] [repeticiones] [n_bloque_alg2]
# Luego: uv run python grafico_parte_f.py salida.csv
OUT=${1:-resultados_parte_f.csv}
REPS=${2:-3}
n=${3:-256}

g++ -O3 -march=native -fopenmp serial-parallel-data.cpp -o serial_parte_b || exit 1
g++ -O3 -march=native -fopenmp serial-parallel-recursive.cpp -o serial_parte_c || exit 1

echo "algoritmo,N,p,rep,tiempo_ms" > "$OUT"

for caso in "1 1024" "2 2048" "4 4096"
do
  read p N <<< "$caso"
  for r in $(seq 1 $REPS)
  do
    # Algoritmo 1: problema base (n = N, sin subdivision)
    t=$(OMP_NUM_THREADS=$p ./serial_parte_b $N $N | sed -E 's/.*tiempo=([0-9.]+).*/\1/')
    echo "alg1,$N,$p,$r,$t" >> "$OUT"
    echo "Alg1   N=$N p=$p corrida $r: $t ms"

    # Algoritmo 2: dividir y conquistar con hojas de n x n
    t=$(OMP_NUM_THREADS=$p ./serial_parte_c $N $n | sed -E 's/.*tiempo=([0-9.]+).*/\1/')
    echo "alg2,$N,$p,$r,$t" >> "$OUT"
    echo "Alg2   N=$N p=$p corrida $r: $t ms"

    # Algoritmo 3: Numba (el script ya excluye el warm-up JIT)
    t=$(uv run python algoritmo3_numba.py --N $N --hilos $p | sed -E 's/.*tiempo=([0-9.]+).*/\1/')
    echo "alg3,$N,$p,$r,$t" >> "$OUT"
    echo "Numba  N=$N p=$p corrida $r: $t ms"
  done
done

echo "Resultados en $OUT"
