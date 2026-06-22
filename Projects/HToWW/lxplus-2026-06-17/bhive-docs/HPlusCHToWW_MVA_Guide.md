---
tags: [reference]
status: active
date: 2026-06-17
source: lxplus
---

# HPlusCHToWW MVA Training Guide (b-hive LAW Workflow)

This guide explains how to train an MVA for HPlusCHToWW analysis using the b-hive framework with parquet files.

---

## Prerequisites

You must be on the **ttcc branch** which has parquet support:
```bash
git checkout ttcc
```

---

## Files Created

| File | Purpose |
|------|---------|
| `config/HPlusCHToWW.yml` | Configuration with features and truths |
| `utils/models/simple_mlp_HToWW.py` | SimpleMLP model for binary classification |
| `utils/models/models.py` | Updated with model registration |

---

## Step 1: Prepare Your Parquet Files

Your parquet files must contain:

### Required Truth Columns
Add these columns to your parquet files before training:

```python
import pandas as pd

# Load your files
signal = pd.read_parquet("signal.parquet")
background = pd.read_parquet("background.parquet")

# Add truth labels
signal["isSignal"] = 1
signal["isBackground"] = 0

background["isSignal"] = 0
background["isBackground"] = 1

# Save
signal.to_parquet("signal_labeled.parquet")
background.to_parquet("background_labeled.parquet")
```

### Required Feature Columns
Your parquet files must contain these columns (from config):

**Global features (scalar per event):**
- `dilepton_mass`, `dilepton_pt`, `met_pt`
- `lepton1_pt`, `lepton2_pt`
- `mtl1`, `mtl2`, `mtll`
- `jet_multiplicity`, `cjet_multiplicity`, `bjet_multiplicity`
- `leadingjet_cvsl_pnet`, `leadingjet_cvsb_pnet`

**Jet features (array per event):**
- `jet_pt`, `jet_eta`, `jet_phi`
- `cjet_cand_cvsl_pnet`, `cjet_cand_cvsb_pnet`

**MET features:**
- `met_phi`

**Weight:**
- `weight_nominal` (or any weight column)

---

## Step 2: Create a Filelist

Create a text file listing your parquet files. The framework matches process names from the filename.

**filelists/HPlusCHToWW.txt:**
```
/path/to/HPlusCH_signal_labeled.parquet
/path/to/ttbar_background_labeled.parquet
/path/to/wjets_background_labeled.parquet
```

**Important:** The config `processes` list must match substrings in your filenames:
```yaml
processes:
- "HPlusCH"      # matches files containing "HPlusCH"
- "ttbar"        # matches files containing "ttbar"
- "wjets"        # matches files containing "wjets"
```

Or use `["default"]` to treat all files as one process.

---

## Step 3: Run the Training

### Setup Environment
```bash
cd /eos/home-c/cgupta/HToWW/b-hive
source setup.sh
law index --verbose  # First time only
```

### Build Dataset
```bash
law run DatasetConstructorTask \
    --config HPlusCHToWW \
    --filelist filelists/HPlusCHToWW.txt \
    --dataset-version v1 \
    --chunk-size 50000
```

### Train Model
```bash
law run TrainingTask \
    --config HPlusCHToWW \
    --model-name SimpleMLP_HToWW \
    --filelist filelists/HPlusCHToWW.txt \
    --dataset-version v1 \
    --training-version v1 \
    --epochs 50 \
    --batch-size 1024 \
    --learning-rate 1e-3
```

### Run Inference (Optional)
```bash
law run InferenceTask \
    --config HPlusCHToWW \
    --model-name SimpleMLP_HToWW \
    --dataset-version v1 \
    --training-version v1
```

### Plot ROC Curves (Optional)
```bash
law run ROCCurveTask \
    --config HPlusCHToWW \
    --model-name SimpleMLP_HToWW \
    --training-version v1
```

---

## Available Models

| Model | Description |
|-------|-------------|
| `SimpleMLP_HToWW` | Default MLP [128, 64, 32] hidden layers |
| `SimpleMLP_HToWW_Large` | Larger [256, 128, 64, 32] |
| `SimpleMLP_HToWW_Small` | Smaller [64, 32] |

---

## Configuration Reference

The config file `config/HPlusCHToWW.yml` defines:

```yaml
# Processor (must use LZ4TTCCProcessor for parquet)
processor: "LZ4TTCCProcessor"

# Features
global_features:    # Scalar variables per event
cpf_candidates:     # Jet-level arrays
npf_candidates:     # MET features
vtx_features:       # Lepton features (if needed)

# Candidate counts
n_cpf_candidates: 6   # Max jets to use
n_npf_candidates: 1   # MET is single value

# Truth labels
truths:
- "isSignal"
- "isBackground"

reference_flavour: "isSignal"

# Optional selections
selections:
  and:
    - "jet_multiplicity>1"
```

---

## Troubleshooting

### "File not found" errors
- Check that your filelist paths are absolute
- Verify parquet files exist and are readable

### "Column not found" errors
- Ensure all columns in `global_features`, `cpf_candidates`, etc. exist in your parquet
- Column names are case-sensitive

### Process matching issues
- The framework looks for process names as substrings in filenames
- Use `processes: ["default"]` to skip process matching

### Memory issues
- Reduce `--chunk-size` in DatasetConstructorTask
- Reduce `--batch-size` in TrainingTask

---

## Output Location

Trained models are saved to:
```
data/<config>/<dataset-version>/<training-version>/
├── model_*.pt           # Checkpoints per epoch
├── best_model.pt        # Best validation loss
├── training_metrics.npz # Loss/accuracy history
└── validation_metrics.npz
```

---

## Quick Reference

```bash
# Full pipeline
law run TrainingTask \
    --config HPlusCHToWW \
    --model-name SimpleMLP_HToWW \
    --filelist filelists/HPlusCHToWW.txt \
    --dataset-version v1 \
    --training-version v1 \
    --epochs 50
```

This will automatically run DatasetConstructorTask first if needed.
