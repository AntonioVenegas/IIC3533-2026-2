#!/usr/bin/env bash
if [ "$#" -ne 0 ]; then
    echo "Usage: $0"
    echo "This will call ./serial_parte_b 2048 2048 while looping over different"
    echo "OPENMP_NUM_THREADS=p variable for each execution"
    exit 1
fi

for p in 1 2 4 8
do 
echo "p= $p"
OMP_NUM_THREADS=$p ./serial_parte_b 2048 2048
OMP_NUM_THREADS=$p ./serial_parte_b 2048 2048
OMP_NUM_THREADS=$p ./serial_parte_b 2048 2048
done
echo ""
