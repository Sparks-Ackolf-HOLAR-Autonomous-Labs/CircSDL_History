#!/bin/bash
#SBATCH --job-name=mt_p4t1_o1
#SBATCH --partition=notchpeak-gpu-guest
#SBATCH --account=owner-gpu-guest
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --gres=gpu:1
#SBATCH --time=03:00:00
#SBATCH --requeue
#SBATCH --exclude=notch168,notch294,notch299,notch204
#SBATCH --output=logs/%x_%j.out
# P4 T1 question O1 (ledger 126).
cd "$SLURM_SUBMIT_DIR"; mkdir -p logs out
P=/uufs/chpc.utah.edu/sys/installdir/r8/mace/0.3.16_cu126/.venv/bin/python
nvidia-smi --query-gpu=name --format=csv,noheader
$P o1_binding.py --x 0.12 --rep 4 --samples 8 --seed 1 --out out/o1_x012_rep4.json
