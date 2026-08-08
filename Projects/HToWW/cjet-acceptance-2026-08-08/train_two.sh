#!/bin/bash
# Two postEE-ONLY trainings for the c-jet acceptance study.
#
#   A (reference) = current 2dcat selection  -> hww_combine_fixed/2022postEE
#   B (test)      = variant 3 (no tag + kin) -> hww_2dcat_nocjet_kin/2022postEE
#
# Both use the SAME config (HPlusCHToWW_2dcats, 26 features incl. the 11 one-hots) and
# the same hyperparameters, and BOTH are restricted to 2022postEE. The stock filelists
# are 3-era; using them would confound the selection change with a training-statistics
# drop, which is exactly what this comparison must avoid.
set -u
export MAMBA_ROOT_PREFIX=/eos/user/c/cgupta/EPR_task/b-hive/micromamba
MM=/eos/user/c/cgupta/EPR_task/b-hive/micromamba/micromamba
BH=/eos/home-c/cgupta/HToWW/b-hive
LOG=/tmp/cjet_study
cd $BH

CONFIG=HPlusCHToWW_2dcats
MODEL=SimpleMLP_MultiClass
EPOCHS=30; BATCH=1024; LR=1e-3; WORKERS=4; CHUNK=300

run_one() {
  local tag=$1 trainfl=$2 testfl=$3
  local DV="hwwcom_2dcats_${tag}_train"
  local TV="hwwcom_2dcats_${tag}_test"
  local MV="hwwcom_multiclass_2dcats_${tag}"
  echo "=== $(date '+%F %T') [$tag] dataset(train) ===" >> $LOG/train.log
  $MM run -n b_hive law run DatasetConstructorTask --config $CONFIG --filelist "$trainfl" \
      --dataset-version "$DV" --coffea-worker $WORKERS --chunk-size $CHUNK \
      >> $LOG/train_$tag.log 2>&1
  echo "=== $(date '+%F %T') [$tag] dataset(train) exit=$? ===" >> $LOG/train.log

  echo "=== $(date '+%F %T') [$tag] dataset(test) ===" >> $LOG/train.log
  $MM run -n b_hive law run DatasetConstructorTask --config $CONFIG --filelist "$testfl" \
      --dataset-version "$TV" --coffea-worker $WORKERS --chunk-size $CHUNK \
      >> $LOG/train_$tag.log 2>&1
  echo "=== $(date '+%F %T') [$tag] dataset(test) exit=$? ===" >> $LOG/train.log

  echo "=== $(date '+%F %T') [$tag] TRAINING ===" >> $LOG/train.log
  $MM run -n b_hive law run TrainingTask --config $CONFIG --filelist "$trainfl" \
      --dataset-version "$DV" --training-version "$MV" --model-name $MODEL \
      --epochs $EPOCHS --batch-size $BATCH --learning-rate $LR --loss-weighting \
      >> $LOG/train_$tag.log 2>&1
  echo "=== $(date '+%F %T') [$tag] training exit=$? ===" >> $LOG/train.log

  echo "=== $(date '+%F %T') [$tag] INFERENCE ===" >> $LOG/train.log
  $MM run -n b_hive law run InferenceTask --config $CONFIG --filelist "$trainfl" \
      --dataset-version "$DV" --training-version "$MV" --model-name $MODEL \
      --epochs $EPOCHS --batch-size $BATCH --learning-rate $LR \
      --test-dataset-version "$TV" --test-filelist "$testfl" \
      >> $LOG/train_$tag.log 2>&1
  echo "=== $(date '+%F %T') [$tag] inference exit=$? ===" >> $LOG/train.log

  echo "=== $(date '+%F %T') [$tag] ROC ===" >> $LOG/train.log
  $MM run -n b_hive law run ROCCurveTask --config $CONFIG --filelist "$trainfl" \
      --dataset-version "$DV" --training-version "$MV" --model-name $MODEL \
      --epochs $EPOCHS --batch-size $BATCH --learning-rate $LR \
      --test-dataset-version "$TV" --test-filelist "$testfl" \
      >> $LOG/train_$tag.log 2>&1
  echo "=== $(date '+%F %T') [$tag] roc exit=$? ===" >> $LOG/train.log
  echo "=== $(date '+%F %T') [$tag] DONE_$tag ===" >> $LOG/train.log
}

REF=/eos/user/c/cgupta/higgscharm/outputs/hww_combine_fixed/2022postEE/mva_labeled
V3=/eos/user/c/cgupta/higgscharm/outputs/hww_2dcat_nocjet_kin/2022postEE/mva_labeled

run_one ref      "$REF/train/filelists/base.txt" "$REF/test/filelists/base.txt"
run_one nocjetkin "$V3/train/filelists/base.txt" "$V3/test/filelists/base.txt"

echo "=== $(date '+%F %T') ALL_TRAINING_DONE ===" >> $LOG/train.log
