#!/bin/bash
# Jet-regime sweep RERUN on H100 NVL, for a like-for-like comparison with the
# event-regime sweep (which ran on H100 NVL). Writes to results_h100/ so the
# original V100S results in results_v100/ are NOT touched.
set -x
BH=/eos/home-c/cgupta/EPR_task/b-hive/micromamba/envs/b_hive/bin/python
FJ=/eos/home-c/cgupta/EPR_task/b-hive/micromamba/envs/fjbench/bin/python
export ATSCRATCH=/eos/home-c/cgupta/flashjet/bench_atlas/results_h100
mkdir -p $ATSCRATCH
cd /eos/home-c/cgupta/flashjet/bench_atlas
nvidia-smi -L
for TAG in atlastop-top atlastop-qcd; do
  $BH sweep_flashjet.py $TAG 20000   || exit 1
  $FJ sweep_fastjet.py  $TAG         || exit 1
done
echo DONE_ALL
