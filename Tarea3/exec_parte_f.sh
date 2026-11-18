#!/bin/bash
# Parte (f): N = 2^13, configuracion 2 (un nodo), con los b de N/2 y N/16.
#
#   Config  grid          T
#     2     2x2           1, 2
#
# Se pide un nodo con 8 CPUs para todas las configuraciones, asi todas corren
# con el mismo recurso reservado y p*T <= 8 nunca hace oversubscription.
#
# Uso (todo junto puede pasar los 15 min, se recomienda separar en jobs):
#   sbatch exec_parte_f.sh 2               -> configuracion 2
#   CHECK=0 sbatch exec_parte_f.sh 2         -> sin verificacion
#
#SBATCH --comment="Este job es parte de la parte f de la Tarea 3 del ramo 'computación de alto rendimiento'"
#SBATCH --qos=hpc-iic3533
#SBATCH --partition=hpc-iic3533
#SBATCH --account=default-account
#SBATCH --job-name=lu_parte_f
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --ntasks-per-node=4
#SBATCH --cpus-per-task=2
#SBATCH --time=00:15:00
#SBATCH --output=parte_f_%j.out
#SBATCH --mem=4G

# ---- Verifica que mpi exista en el nodo ---
command -v mpirun || { echo "mpirun not found on $(hostname)"; exit 1; }

# ---- Ambiente: venv creado con `uv venv --python /usr/bin/python3 ~/venvs/hpc` ----
VENV=~/venvs/hpc
source $VENV/bin/activate || { echo "No se pudo activar $VENV"; exit 1; }
PY=$VENV/bin/python
$PY -c "import numpy, scipy, mpi4py" || { echo "Ambiente roto en $(hostname)"; exit 1; }

N=8192
REPS=${REPS:-3}
BS=${BS:-"512 4096"}          # b de (N/2) = 512, de (N/16) = 1024
CHECK_ON=${CHECK:-1}
CONFIGS=${@:-2}
CSV=resultados_parte_f.csv

# Lista de corridas "pr pc T" por configuracion
runs_config() {
  case $1 in
    0) echo "1 1 1;1 1 2;1 1 4;1 1 8" ;;
    1) echo "1 2 1;1 2 2;1 2 4;2 1 1;2 1 2;2 1 4" ;;
    2) echo "2 2 1;2 2 2" ;;
    3) echo "2 4 1;4 2 1" ;;
    *) echo "Configuracion desconocida: $1" >&2 ;;
  esac
}

echo "Job $SLURM_JOB_ID en $(hostname) | N=$N | CPUs reservadas: $SLURM_NTASKS"
echo "configs: $CONFIGS | b: $BS | repeticiones: $REPS | python: $(readlink -f $PY)"

for rep in $(seq 1 $REPS); do
  for cfg in $CONFIGS; do
    IFS=';' read -ra RUNS <<< "$(runs_config $cfg)"
    for run in "${RUNS[@]}"; do
      read -r PR PC T <<< "$run"
      P=$((PR * PC))
      # Threads de BLAS = T (no SLURM_CPUS_PER_TASK, porque T cambia dentro del job)
      export OMP_NUM_THREADS=$T OPENBLAS_NUM_THREADS=$T MKL_NUM_THREADS=$T
      for b in $BS; do
        echo "=== config=$cfg grid=${PR}x${PC} T=$T b=$b rep=$rep  ($(date +%T)) ==="
        # Solo se verifica en la primera repeticion (la verificacion no entra en los tiempos)
        EXTRA=""
        [ "$rep" -eq 1 ] && [ "$CHECK_ON" = "1" ] && EXTRA="--check"
        # --bind-to none: cada proceso puede usar varias CPUs para sus T threads
        mpirun -n $P --bind-to none \
          $PY lu_distributed.py --N $N --b $b --pr $PR --pc $PC \
                                --csv $CSV --rep $rep $EXTRA
      done
    done
  done
done

echo "Fin: $(date +%T)"
