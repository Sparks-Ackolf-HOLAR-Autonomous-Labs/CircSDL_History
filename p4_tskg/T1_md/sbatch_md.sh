#!/bin/bash
#SBATCH --job-name=mt_p4t1_md
#SBATCH --partition=notchpeak-gpu-guest
#SBATCH --account=owner-gpu-guest
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --gres=gpu:1
#SBATCH --time=12:00:00
#SBATCH --requeue
#SBATCH --exclude=notch168,notch294,notch299,notch204
#SBATCH --output=logs/%x_%A_%a.out
# P4 T1 production MD; runs table in t1_design.json (ledger 126). Array index = run index.
cd "$SLURM_SUBMIT_DIR"; mkdir -p logs out
P=/uufs/chpc.utah.edu/sys/installdir/r8/mace/0.3.16_cu126/.venv/bin/python
nvidia-smi --query-gpu=name --format=csv,noheader
ARGS=$($P -c "import json;r=json.load(open('t1_design.json'))['md_runs'][$SLURM_ARRAY_TASK_ID];print(r['args'])")
ID=$($P -c "import json;print(json.load(open('t1_design.json'))['md_runs'][$SLURM_ARRAY_TASK_ID]['id'])")
$P md_events.py $ARGS --out out/$ID.json
