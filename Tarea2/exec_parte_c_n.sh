#!/usr/bin/env bash
# Parte c/e) Algoritmo 2 variando el tamano de bloque n.
# Para cada n mide T(p) con p en {1, 2, 4, 8} y guarda cada corrida en un CSV
# (N,n,p,rep,tiempo_ms,checksum). El checksum permite verificar que el resultado
# coincide con la referencia serial (172.331627 para N = 2048).
# Uso: ./exec_parte_c_n.sh [salida.csv] [repeticiones] [N]
# Luego: uv run python grafico_parte_c_n.py comp1.csv comp2.csv comp3.csv
OUT=${1:-resultados_parte_c_n.csv}
REPS=${2:-3}
N=${3:-2048}

g++ -O3 -march=native -fopenmp serial-parallel-recursive.cpp -o serial_parte_c || exit 1

echo "N,n,p,rep,tiempo_ms,checksum" > "$OUT"

for n in 128 256 512 1024
do
  for p in 1 2 4 8
  do
    for r in $(seq 1 $REPS)
    do
      salida=$(OMP_NUM_THREADS=$p ./serial_parte_c $N $n)
      t=$(echo "$salida" | sed -E 's/.*tiempo=([0-9.]+).*/\1/')
      c=$(echo "$salida" | sed -E 's/.*checksum=([-0-9.]+).*/\1/')
      echo "$N,$n,$p,$r,$t,$c" >> "$OUT"
      echo "n=$n p=$p corrida $r: $t ms (checksum=$c)"
    done
  done
done

echo "Resultados en $OUT"
