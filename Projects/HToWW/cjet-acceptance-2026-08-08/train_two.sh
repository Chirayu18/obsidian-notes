#!/bin/bash
# Two postEE-ONLY trainings for the c-jet acceptance study.
#
#   A (reference) = current 2dcat selection  -> hww_combine_fixed/2022postEE
#   B (test)      = variant 3 (no tag + kin) -> hww_2dcat_nocjet_kin/2022postEE
#
# Same config (HPlusCHToWW_2dcats, 26 features incl. the 11 one-hots), same
# hyperparameters, both restricted to 2022postEE -- the stock filelists are 3-era and
# would confound the selection change with a training-statistics drop.
#
# TWO TRAPS, both of which make the chain "succeed" in seconds:
#  1. `law` lives INSIDE the b_hive env, so setup.sh must be sourced *within*
#     `micromamba run -n b_hive`, not before it. Sourcing it outside gives
#     "law: command not found" and LAW_CONFIG_FILE stays unset.
#  2. Without that env, every task dies with "task family 'X' not found in index"
#     and law still exits 0 -- so we grep for it explicitly.
set -u
export MAMBA_ROOT_PREFIX=/eos/user/c/cgupta/EPR_task/b-hive/micromamba
MM=/eos/user/c/cgupta/EPR_task/b-hive/micromamba/micromamba
BH=/eos/home-c/cgupta/HToWW/b-hive
LOG=/tmp/cjet_study

CONFIG=HPlusCHToWW_2dcats
MODEL=SimpleMLP_MultiClass
EPOCHS=30; BATCH=1024; LR=1e-3; WORKERS=4; CHUNK=300

law_run() {  # $1=label $2=tag, rest = law args
  local label=$1 tag=$2; shift 2
  echo "=== $(date '+%F %T') [$tag] $label ===" >> $LOG/train.log
  $MM run -n b_hive bash -c "cd $BH && source setup.sh >/dev/null 2>&1 && law run $*" \
      >> $LOG/train_$tag.log 2>&1
  local rc=$?
  if tail -40 $LOG/train_$tag.log | grep -q "not found in index"; then
    echo "=== $(date '+%F %T') [$tag] $label FAILED: task not in index ===" >> $LOG/train.log
    return 1
  fi
  echo "=== $(date '+%F %T') [$tag] $label exit=$rc ===" >> $LOG/train.log
  return $rc
}

run_one() {
  local tag=$1 trainfl=$2 testfl=$3
  local DV="hwwcom_2dcats_${tag}_train"
  local TV="hwwcom_2dcats_${tag}_test"
  local MV="hwwcom_multiclass_2dcats_${tag}"
  local COMMON="--config $CONFIG --filelist '$trainfl' --dataset-version $DV --training-version $MV --model-name $MODEL --epochs $EPOCHS --batch-size $BATCH --learning-rate $LR"

  law_run "dataset(train)" $tag "DatasetConstructorTask --config $CONFIG --filelist '$trainfl' --dataset-version $DV --coffea-worker $WORKERS --chunk-size $CHUNK" || return 1
  law_run "dataset(test)"  $tag "DatasetConstructorTask --config $CONFIG --filelist '$testfl' --dataset-version $TV --coffea-worker $WORKERS --chunk-size $CHUNK" || return 1
  law_run "TRAINING"  $tag "TrainingTask $COMMON --loss-weighting" || return 1
  law_run "INFERENCE" $tag "InferenceTask $COMMON --test-dataset-version $TV --test-filelist '$testfl'" || return 1
  law_run "ROC"       $tag "ROCCurveTask $COMMON --test-dataset-version $TV --test-filelist '$testfl'" || return 1
  echo "=== $(date '+%F %T') [$tag] DONE_$tag ===" >> $LOG/train.log
}

REF=/eos/user/c/cgupta/higgscharm/outputs/hww_combine_fixed/2022postEE/mva_labeled
V3=/eos/user/c/cgupta/higgscharm/outputs/hww_2dcat_nocjet_kin/2022postEE/mva_labeled

run_one ref       "$REF/train/filelists/base.txt" "$REF/test/filelists/base.txt" \
  || echo "=== ref chain aborted ===" >> $LOG/train.log
run_one nocjetkin "$V3/train/filelists/base.txt"  "$V3/test/filelists/base.txt" \
  || echo "=== nocjetkin chain aborted ===" >> $LOG/train.log

echo "=== $(date '+%F %T') ALL_TRAINING_DONE ===" >> $LOG/train.log
