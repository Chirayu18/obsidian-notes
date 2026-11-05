#!/bin/bash
# Append the 11 cjet_cand_ctag2d_* one-hots to variant 3's train/test parquets.
# The HPlusCHToWW_2dcats config REQUIRES these columns; the processor does not write
# them (they are a post-hoc step, append_onehot.py). Idempotent + atomic rename.
#
# Events with the -1 sentinel (no c-jet / PNet undefined) get cat=-1 -> all 11 one-hots
# zero, which is a sensible "no charm information" encoding.
set -u
export MAMBA_ROOT_PREFIX=/eos/user/c/cgupta/EPR_task/b-hive/micromamba
MM=/eos/user/c/cgupta/EPR_task/b-hive/micromamba/micromamba
D=/eos/user/c/cgupta/higgscharm/outputs/hww_2dcat_nocjet_kin/2022postEE/mva_labeled
LOG=/tmp/cjet_study
for sub in train test; do
  echo "=== $(date '+%F %T') one-hot $sub ===" >> $LOG/onehot.log
  $MM run -n b_hive python3 /eos/home-c/cgupta/HToWW/b-hive/scripts/append_onehot.py \
      --mva-dir "$D/$sub" >> $LOG/onehot.log 2>&1
  echo "=== $(date '+%F %T') $sub exit=$? ===" >> $LOG/onehot.log
done
echo "=== $(date '+%F %T') ONEHOT_DONE ===" >> $LOG/onehot.log
