#!/bin/bash
# Event-regime timing sweep: flashjet (GPU) then FastJet (CPU) on the SAME saved
# events. Pinned to V100S so the numbers are comparable with the jet-regime plot
# already in the ML4Jets deck (that sweep ran on Tesla V100S-PCIE-32GB).
set -x
BH=/eos/home-c/cgupta/EPR_task/b-hive/micromamba/envs/b_hive/bin/python
FJ=/eos/home-c/cgupta/EPR_task/b-hive/micromamba/envs/fjbench/bin/python
export EVSCRATCH=/eos/home-c/cgupta/flashjet/bench_event/results
mkdir -p $EVSCRATCH
cd /eos/home-c/cgupta/flashjet/bench_event
nvidia-smi -L
$BH sweep_event_flashjet.py 3000 || exit 1
$FJ sweep_event_fastjet.py       || exit 1
echo DONE_ALL
