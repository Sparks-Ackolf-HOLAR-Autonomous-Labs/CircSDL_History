#!/bin/bash
#SBATCH --job-name=mt_p4t1_bench
#SBATCH --partition=notchpeak-gpu-guest
#SBATCH --account=owner-gpu-guest
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --gres=gpu:1
#SBATCH --time=00:25:00
#SBATCH --exclude=notch168,notch294,notch299,notch204
#SBATCH --output=logs/%x_%j.out
# GPU timing for P4 T1 (no science output: MD length 2 ps, no events kept).
cd "$SLURM_SUBMIT_DIR"; mkdir -p logs bench
P=/uufs/chpc.utah.edu/sys/installdir/r8/mace/0.3.16_cu126/.venv/bin/python
nvidia-smi --query-gpu=name --format=csv,noheader
for rep in 4 5; do $P md_events.py --rep $rep --T 600 --eq-ps 0.4 --bench 400 --out bench/bench_rep$rep.json; done
