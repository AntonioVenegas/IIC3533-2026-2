#!/bin/bash
#SBATCH --qos=hpc-iic3533
#SBATCH --partition=hpc-iic3533
#SBATCH --account=default-account
#SBATCH --time=00:15:00
#SBATCH --output=out_%j.txt

PR=$1; PC=$2; N=$3; shift 3        
export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK
export OPENBLAS_NUM_THREADS=$SLURM_CPUS_PER_TASK
export MKL_NUM_THREADS=$SLURM_CPUS_PER_TASK

for b in "$@"; do
  mpirun -n $SLURM_NTASKS --map-by slot:PE=$SLURM_CPUS_PER_TASK \
         python lu_distributed.py --N $N --b $b --pr $PR --pc $PC
done