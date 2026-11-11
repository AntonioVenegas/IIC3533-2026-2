#!/bin/bash
# Parte (c): N = 2^13, configuracion 2 (grid 2x2, 4 procesos, T = 2 threads), variando b.
#
# Uso:
#   sbatch exec_parte_c.sh                     -> todos los b, 1 repeticion
#   sbatch exec_parte_c.sh 4096 2048           -> solo esos valores de b
#   REPS=3 sbatch exec_parte_c.sh 512 256 128  -> 3 repeticiones de cada b
#
#SBATCH --comment="Este job es parte de la parte c de la Tarea 3 del ramo 'computación de alto rendimiento'"
#SBATCH --qos=hpc-iic3533
#SBATCH --partition=hpc-iic3533
#SBATCH --account=default-account
#SBATCH --job-name=lu_parte_c
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=2
#SBATCH --time=00:15:00
#SBATCH --output=parte_c_%j.out
#SBATCH --mem=4G
 
# ---- Ambiente: venv creado con `uv venv --python /usr/bin/python3 ~/venvs/hpc` ----
VENV=~/venvs/hpc
source $VENV/bin/activate || { echo "No se pudo activar $VENV"; exit 1; }
PY=$VENV/bin/python
# Falla temprano si el python o las dependencias no estan en este nodo
$PY -c "import numpy, scipy, mpi4py" || { echo "Ambiente roto en $(hostname)"; exit 1; }
 
# Threads de BLAS = threads por proceso (T)
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export OPENBLAS_NUM_THREADS=$SLURM_CPUS_PER_TASK
export MKL_NUM_THREADS=$SLURM_CPUS_PER_TASK
 
N=8192
PR=2
PC=2
REPS=${REPS:-1}
BS=${@:-4096 2048 1024 512 256 128 64}
CSV=resultados_parte_c.csv
 
echo "Job $SLURM_JOB_ID en $(hostname) | N=$N grid=${PR}x${PC} T=$SLURM_CPUS_PER_TASK"
echo "b: $BS | repeticiones: $REPS | python: $(readlink -f $PY)"
 
for rep in $(seq 1 $REPS); do
  for b in $BS; do
    echo "=== b=$b rep=$rep  ($(date +%T)) ==="
    # Solo se verifica en la primera repeticion (la verificacion no entra en los tiempos)
    CHECK=""
    [ "$rep" -eq 1 ] && CHECK="--check"
    # --bind-to none: deja que los 2 threads de cada proceso usen CPUs distintas
    mpirun -n $SLURM_NTASKS --bind-to none \
      $PY lu_distributed.py --N $N --b $b --pr $PR --pc $PC \
                               --csv $CSV --rep $rep $CHECK
  done
done
 
echo "Fin: $(date +%T)"