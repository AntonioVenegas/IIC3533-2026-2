#!/usr/bin/env bash
# Uso: ./exec_parte_b.sh [ejecutable] [N] [n]
BIN=${1:-./serial_parte_b}
N=${2:-2048}
n=${3:-256}

echo "p  tiempo(ms)  speedup  eficiencia"
for p in 1 2 4 8
do
  t=$(OMP_NUM_THREADS=$p $BIN $N $n | sed -E 's/.*tiempo=([0-9.]+).*/\1/')
  if [ $p -eq 1 ]; then T1=$t; fi
  awk -v p=$p -v t=$t -v t1=$T1 'BEGIN { s = t1/t; printf "%d  %.2f  %.2f  %.2f\n", p, t, s, s/p }'
done
