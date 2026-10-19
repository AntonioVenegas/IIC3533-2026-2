#!/usr/bin/env bash
# Parte c/e) Algoritmo 2 variando el tamano de bloque n.
# Para cada n mide el serial de referencia (serial.cpp con el mismo n) y T(p) del
# Algoritmo 2 con p en {1, 2, 4, 8}, en la misma corrida para que el T(1) serial y
# los T(p) se midan en las mismas condiciones de la maquina.
# Guarda cada corrida en un CSV (programa,N,n,p,rep,tiempo_ms,checksum); el serial
# queda con p = 1. El checksum permite verificar el resultado (172.331627 para N = 2048).
# Uso: ./exec_parte_c_n.sh [salida.csv] [repeticiones] [N]
# Luego: uv run python grafico_parte_c_n.py comp1.csv comp2.csv comp3.csv
OUT=${1:-resultados_parte_c_n.csv}
REPS=${2:-3}
N=${3:-2048}

g++ -O3 -march=native -fopenmp serial.cpp -o serial || exit 1
g++ -O3 -march=native -fopenmp serial-parallel-recursive.cpp -o serial_parte_c || exit 1

echo "programa,N,n,p,rep,tiempo_ms,checksum" > "$OUT"

# Ejecuta "$@", extrae tiempo y checksum y agrega la fila al CSV
medir() {
  local programa=$1 n=$2 p=$3 r=$4
  shift 4
  local salida t c
  salida=$("$@")
  t=$(echo "$salida" | sed -E 's/.*tiempo=([0-9.]+).*/\1/')
  c=$(echo "$salida" | sed -E 's/.*checksum=([-0-9.]+).*/\1/')
  echo "$programa,$N,$n,$p,$r,$t,$c" >> "$OUT"
  echo "$programa n=$n p=$p corrida $r: $t ms (checksum=$c)"
}

for n in 128 256 512 1024
do
  for r in $(seq 1 $REPS)
  do
    medir serial $n 1 $r ./serial $N $n
    for p in 1 2 4 8
    do
      medir paralelo $n $p $r env OMP_NUM_THREADS=$p ./serial_parte_c $N $n
    done
  done
done

echo "Resultados en $OUT"
