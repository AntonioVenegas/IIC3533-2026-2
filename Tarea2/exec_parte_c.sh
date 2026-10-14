#!/usr/bin/env bash
# Uso: ./exec_parte_c.sh [ejecutable] [N] [n]
# g++ -O3 -march=native -fopenmp serial-parallel-recursive.cpp -o serial_parte_c
BIN=${1:-./serial_parte_c}
N=${2:-2048}
n=${3:-256}

echo "p  tiempo_promedio(ms)"
for p in 1 2 4 8
do
  suma=0
  for r in 1 2 3
  do
    t=$(OMP_NUM_THREADS=$p $BIN $N $n | sed -E 's/.*tiempo=([0-9.]+).*/\1/')
    echo "   p=$p corrida $r: $t ms"
    suma=$(awk -v a=$suma -v b=$t 'BEGIN { print a + b }')
  done
  awk -v p=$p -v s=$suma 'BEGIN { printf "%d  %.2f\n", p, s/3 }'
done
