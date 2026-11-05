#!/bin/bash
#
# MVA training workflow — v11 (2D-CTAG variant)
# Features use the 11 one-hot cjet_cand_ctag2d_* categories INSTEAD OF the raw PNet
# cvsl/cvsb scores (config HPlusCHToWW_2dcats). Columns appended by
# scripts/append_ctag2d.py. Versions suffixed _2dcats so datasets/training output do
# NOT collide with the baseline v11. See Projects/HToWW/CTAG.md.
#
# 6-class: hplusc / higgsbkg / tt / st / diboson / vjets. Cross-era inputs, labeled via
# make_mva_labeled.py and split 80/20 by split_train_test.py. WG (W+gamma) excluded.
#
# Usage: ./train_v11_2dcats.sh [--epochs N] [--debug] ...

# ===================== CONFIGURATION =====================
CONFIG="HPlusCHToWW_2dcats"
MODEL="SimpleMLP_MultiClass"
TRAIN_FILELIST="/eos/home-c/cgupta/HToWW/b-hive/filelists/v11_train_allEras.txt"
TEST_FILELIST="/eos/home-c/cgupta/HToWW/b-hive/filelists/v11_test_allEras.txt"
DATASET_VERSION="hwwcom_v11_2dcats_train"
TEST_DATASET_VERSION="hwwcom_v11_2dcats_test"
TRAINING_VERSION="hwwcom_multiclass_v11_2dcats"
EPOCHS=30
BATCH_SIZE=1024
LEARNING_RATE=1e-3
COFFEA_WORKERS=4
CHUNK_SIZE=300
LOSS_WEIGHTING=true
DEBUG=false

# ===================== PARSE ARGS =====================
while [[ $# -gt 0 ]]; do
    case $1 in
        --config) CONFIG="$2"; shift 2;;
        --train-filelist) TRAIN_FILELIST="$2"; shift 2;;
        --test-filelist) TEST_FILELIST="$2"; shift 2;;
        --version) TRAINING_VERSION="$2"; shift 2;;
        --dataset-version) DATASET_VERSION="$2"; shift 2;;
        --model) MODEL="$2"; shift 2;;
        --epochs) EPOCHS="$2"; shift 2;;
        --batch-size) BATCH_SIZE="$2"; shift 2;;
        --lr) LEARNING_RATE="$2"; shift 2;;
        --workers) COFFEA_WORKERS="$2"; shift 2;;
        --no-loss-weighting) LOSS_WEIGHTING=false; shift;;
        --debug) DEBUG=true; shift;;
        -h|--help) echo "Usage: $0 [--epochs N] [--batch-size N] [--lr R] [--debug] ..."; exit 0;;
        *) echo "Unknown option: $1"; exit 1;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; cd "$SCRIPT_DIR"
echo "=============================================="
echo "v11 MVA training (6-class)"
echo "  config=$CONFIG model=$MODEL epochs=$EPOCHS"
echo "  train=$TRAIN_FILELIST"
echo "  test =$TEST_FILELIST"
echo "=============================================="
[ -f "$TRAIN_FILELIST" ] || { echo "ERROR: train filelist not found"; exit 1; }
[ -f "$TEST_FILELIST" ]  || { echo "ERROR: test filelist not found";  exit 1; }
DBG=""; [ "$DEBUG" = true ] && DBG="--debug"
LW="";  [ "$LOSS_WEIGHTING" = true ] && LW="--loss-weighting"

# ===================== STEP 1: DATASET CONSTRUCTION (train + held-out test) =====================
echo "### Step 1a: train dataset"
law run DatasetConstructorTask --config "$CONFIG" --filelist "$TRAIN_FILELIST" \
    --dataset-version "$DATASET_VERSION" --coffea-worker "$COFFEA_WORKERS" --chunk-size "$CHUNK_SIZE" $DBG \
    || { echo "ERROR: train dataset construction failed"; exit 1; }

echo "### Step 1b: test dataset"
law run DatasetConstructorTask --config "$CONFIG" --filelist "$TEST_FILELIST" \
    --dataset-version "$TEST_DATASET_VERSION" --coffea-worker "$COFFEA_WORKERS" --chunk-size "$CHUNK_SIZE" $DBG \
    || { echo "ERROR: test dataset construction failed"; exit 1; }

# ===================== STEP 2: TRAINING =====================
echo "### Step 2: training"
law run TrainingTask --config "$CONFIG" --filelist "$TRAIN_FILELIST" \
    --dataset-version "$DATASET_VERSION" --training-version "$TRAINING_VERSION" \
    --model-name "$MODEL" --epochs "$EPOCHS" --batch-size "$BATCH_SIZE" --learning-rate "$LEARNING_RATE" \
    $LW $DBG || { echo "ERROR: training failed"; exit 1; }

# ===================== STEP 3: INFERENCE (on held-out test) =====================
echo "### Step 3: inference"
law run InferenceTask --config "$CONFIG" --filelist "$TRAIN_FILELIST" \
    --dataset-version "$DATASET_VERSION" --training-version "$TRAINING_VERSION" \
    --model-name "$MODEL" --epochs "$EPOCHS" --batch-size "$BATCH_SIZE" --learning-rate "$LEARNING_RATE" \
    --test-dataset-version "$TEST_DATASET_VERSION" --test-filelist "$TEST_FILELIST" \
    $DBG || { echo "ERROR: inference failed"; exit 1; }

# ===================== STEP 4: ROC =====================
echo "### Step 4: ROC"
law run ROCCurveTask --config "$CONFIG" --filelist "$TRAIN_FILELIST" \
    --dataset-version "$DATASET_VERSION" --training-version "$TRAINING_VERSION" \
    --model-name "$MODEL" --epochs "$EPOCHS" --batch-size "$BATCH_SIZE" --learning-rate "$LEARNING_RATE" \
    --test-dataset-version "$TEST_DATASET_VERSION" --test-filelist "$TEST_FILELIST" \
    $DBG || { echo "ERROR: ROC failed"; exit 1; }

echo "=============================================="
echo "v11 training complete -> output/TrainingTask/$CONFIG/$TRAINING_VERSION/"
echo "=============================================="
