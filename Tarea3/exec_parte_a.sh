#!/usr/bin/env bash
# filepath: /home/Arbolichuu/gits/hpc/tareas/Tarea3/exec_parte_a.sh

BIN=${1:-"uv run python lu_serial.py"}
N=${2:-4096}

echo "b  tiempo_promedio(ms)  GFLOPS_promedio  checksum"
for b in 4096 2048 1024 512 256 128 64
do
  suma_t=0
  suma_g=0
  checksum=

  for r in 1 2 3
  do
    salida=$($BIN --N "$N" --b "$b")

    t=$(printf '%s\n' "$salida" | sed -nE 's/.*tiempo[=:][[:space:]]*([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?).*/\1/p')
    g=$(printf '%s\n' "$salida" | sed -nE 's/.*GFLOP\/s[=:][[:space:]]*([-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?).*/\1/p')
    checksum=$(printf '%s\n' "$salida" | sed -nE 's/.*checksum[=:][[:space:]]*([^ ,[:space:]]+).*/\1/p')

    echo "   b=$b corrida $r: $t ms, $g GFLOPS, checksum=$checksum"
    suma_t=$(awk -v a="$suma_t" -v x="$t" 'BEGIN { print a + x }')
    suma_g=$(awk -v a="$suma_g" -v x="$g" 'BEGIN { print a + x }')
  done

  awk -v b="$b" -v t="$suma_t" -v g="$suma_g" -v c="$checksum" \
    'BEGIN { printf "%d  %.2f  %.2f  %s\n", b, t/3, g/3, c }'
done