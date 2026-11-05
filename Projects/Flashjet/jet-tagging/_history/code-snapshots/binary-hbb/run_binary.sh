#!/bin/bash
# BINARY Hbb-vs-QCD: baseline + PLuM, one seed each, sequentially in ONE job.
#
# Reproduces Gouskos & Maier on the TASK axis -- they train "in binary
# classification mode", 8M signal + 8M background. Our 10-class arms cannot see
# their claim directly because a binary tagger devotes all capacity to one
# boundary.
#
# Uses BinaryFilteredLZ4Dataset, which DROPS the other 8 signal classes. Merging
# them into QCD (what a plain 2-class dict does) would give a 9x-contaminated
# background and a meaningless rejection number.
#
# One job, not two: condor rewrites RequestCpus 4->8 for GPU jobs and only ~2
# slots in the pool are willing; two competing jobs is strictly worse than one.
cd /eos/user/c/cgupta/flashjet/b-hive
source setup.sh
export FLASHJET_SRC=/eos/home-c/cgupta/flashjet/FlastJetDemo/src
nvidia-smi
echo "law index: SKIPPED (exists; hangs for minutes rewriting .law on EOS)"

# guards
for f in utils/models/binary_hbb.py utils/torch/BinaryFilteredLZ4Dataset.py \
         config/jet_class_binary.yml config/jet_class_plum_binary.yml; do
  [ -f "$f" ] || { echo "FATAL: missing $f"; exit 1; }
done
grep -q "dataset: BinaryFilteredLZ4Dataset" config/jet_class_binary.yml || { echo "FATAL: baseline cfg missing dataset override"; exit 1; }
grep -q "dataset: BinaryFilteredLZ4Dataset" config/jet_class_plum_binary.yml || { echo "FATAL: plum cfg missing dataset override"; exit 1; }
grep -q "lund_tokens: true" config/jet_class_plum_binary.yml || { echo "FATAL: plum cfg lost lund_tokens"; exit 1; }
echo "guards OK"

ITERS=${ITERS:-200000}
COMMON="--dataset-version JetClass_train_100_mod \
 --TrainingTask-val-dataset-version JetClass_val_mod \
 --test-dataset-version JetClass_test_mod \
 --lr-scheduler batch_exp_decay --n-threads 4 --batch-size 512 \
 --learning-rate 0.001 --TrainingTask-loss-weighting True \
 --TrainingTask-use-iterations True --TrainingTask-total-iterations $ITERS \
 --TrainingTask-n-iters-per-save 20000 --epochs 0 --optimizer Ranger \
 --weight-decay 0 --eps 1e-5"

RC_TOT=0
echo "======== 1/2: BINARY baseline (Hbb vs QCD), $ITERS iters ========"
law run ROCCurveTask --config jet_class_binary \
  --training-version b_hive_binary_baseline_1 \
  --model-name ParticleTransformer_Paper_JetClass_HbbBinary $COMMON
RC=$?; echo "RC_baseline=$RC"; [ $RC -ne 0 ] && RC_TOT=$RC

echo "======== 2/2: BINARY PLuM (Hbb vs QCD), $ITERS iters ========"
law run ROCCurveTask --config jet_class_plum_binary \
  --training-version b_hive_binary_plum_1 \
  --model-name ParticleTransformer_PLuM_JetClass_HbbBinary $COMMON
RC=$?; echo "RC_plum=$RC"; [ $RC -ne 0 ] && RC_TOT=$RC

echo "RC_TOTAL=$RC_TOT"
exit $RC_TOT
