#!/bin/bash
# Variant 3: postprocess -> MVA labels -> 80/20 split. Runs in tmux.
#
# NOTE: run_postprocess.py has NO --mva flag (the vault doc's step 4 is wrong for this
# repo state). Correct call is just --postprocess --output_format parquet.
# Also: capture ${PIPESTATUS[0]} -- piping into tee masks the real exit code, which is
# how the first attempt reported exit=0 on three failures.
set -u
export X509_USER_PROXY=/afs/cern.ch/user/c/cgupta/private/x509up_u151861
cd /afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm
export MAMBA_ROOT_PREFIX=/eos/user/c/cgupta/EPR_task/b-hive/micromamba
MM=/eos/user/c/cgupta/EPR_task/b-hive/micromamba/micromamba
LOG=/tmp/cjet_study
D=/eos/user/c/cgupta/higgscharm/outputs/hww_2dcat_nocjet_kin/2022postEE
: > $LOG/chain.log

step() {  # $1=label $2=logfile ; rest = command
  local label=$1 lf=$2; shift 2
  echo "=== $(date '+%F %T') $label ===" >> $LOG/chain.log
  "$@" > "$lf" 2>&1
  local rc=$?
  echo "=== $(date '+%F %T') $label exit=$rc ===" >> $LOG/chain.log
  tail -4 "$lf" >> $LOG/chain.log
  return $rc
}

step "STEP1 postprocess" $LOG/v3_postprocess.log \
  $MM run -n b_hive python3 run_postprocess.py -w hww_2dcat_nocjet_kin \
  -y 2022postEE --postprocess --output_format parquet \
  || { echo "ABORT: postprocess failed" >> $LOG/chain.log; exit 1; }

step "STEP2 labels" $LOG/v3_labels.log \
  $MM run -n b_hive python3 /eos/home-c/cgupta/HToWW/b-hive/make_mva_labeled.py \
  --input-dir $D --groups-key process_groups \
  || { echo "ABORT: labels failed" >> $LOG/chain.log; exit 1; }

step "STEP3 split" $LOG/v3_split.log \
  $MM run -n b_hive python3 /eos/home-c/cgupta/HToWW/b-hive/split_train_test.py \
  --input-dir $D/mva_labeled \
  || { echo "ABORT: split failed" >> $LOG/chain.log; exit 1; }

echo "=== $(date '+%F %T') CHAIN_DONE ===" >> $LOG/chain.log
echo "train files: $(ls "$D/mva_labeled/train" 2>/dev/null | wc -l)  test files: $(ls "$D/mva_labeled/test" 2>/dev/null | wc -l)" >> $LOG/chain.log
