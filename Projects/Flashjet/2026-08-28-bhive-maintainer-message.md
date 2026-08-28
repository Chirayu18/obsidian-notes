---
tags: [reference]
status: active
date: 2026-08-28
source: lxplus
---

# Draft message to b-hive maintainers

Re: [[2026-08-28-bhive-jetclass-part-setup]]. Mattermost channel is linked from the
b-hive README.

**Attachments** — the two filelists, identical apart from the 25-char prefix:
- [jetclass_val_BROKEN_xrootd.txt](bhive-bug-filelists/jetclass_val_BROKEN_xrootd.txt)
  — 50 files, `root://eoscms.cern.ch/` prefix → **1** output name (`_eoscms`), crashes
- [jetclass_val_FIXED_local.txt](bhive-bug-filelists/jetclass_val_FIXED_local.txt)
  — same 50 files, plain `/eos/...` → **50** output names, builds clean

Check without running b-hive:
```python
def mk(p): return "_".join(p.split("/")[1:]).split(".")[0]   # base.py:129
print(len({mk(l.strip()) for l in open("jetclass_val_BROKEN_xrootd.txt")}))  # 1
print(len({mk(l.strip()) for l in open("jetclass_val_FIXED_local.txt")}))    # 50
```

---

Hi — there's a silent data-loss bug affecting any filelist that uses XRootD paths,
including the one committed in the repo.

**Environment**
- `master`, commit `448bb6507d96c9a79861753bfc1639373c04b414` ("Merge branch
  'parquet_format' into 'master'", 2026-04-29)
- Fresh clone, **no changes to any Python file**. Only edit is a 12-line `processes:`
  block added to `config/jet_class.yml` — needed because `tasks/dataset.py:63` does
  `config["processes"]` (direct index) and `jet_class.yml` ships without that key.
- lxplus EL9; python 3.11.10, numpy 1.23.5, coffea 0.7.22, uproot 4.3.7,
  awkward 1.10.3, law 0.1.19
- config `jet_class`, processor `LZ4Processing`, data format ROOT

`utils/coffea_processors/base.py:129` builds the per-chunk output name from the input
path:

```python
filename = "_".join(events.metadata["filename"].split("/")[1:]).split(".")[0]
```

The trailing `.split(".")[0]` truncates at the first dot, which for
`root://eoscms.cern.ch//eos/cms/store/.../HToBB_000.root` lands inside the hostname.
Every file in the list therefore maps to the same name, `_eoscms`:

| filelist | files | unique output names |
|---|---|---|
| my JetClass list, `root://` paths | 50 | **1** |
| same list, plain `/eos/...` paths | 50 | **50** |
| **`filelists/shuffled_ParT_files.txt`** (in the repo) | 200 | **1** |

Two effects:

1. **Silent data loss** — all files write to the same `.npy` names and overwrite each
   other, so only a fraction of the input survives into the dataset. No warning.
2. **A crash, if you're lucky** — `file_list` then contains each path N times, and
   `merge_datasets` (`utils/dataset/merging.py:131-132`) does `np.load` then
   `os.remove` per entry, so the duplicate raises `FileNotFoundError` on the
   already-deleted file. Not worker-count or storage related: it fails with
   `--coffea-worker 1` and on local disk too.

**Reproducer**

```bash
ls /eos/cms/store/group/phys_btag/b_hive_HLT/jetclass/jetclass_val/*.root \
  | sed 's|^|root://eoscms.cern.ch/|' > filelists/jetclass_val.txt

rm -rf output/DatasetConstructorTask/jet_class/JetClass_val_mod   # must start clean

law run DatasetConstructorTask --config jet_class \
    --dataset-version JetClass_val_mod \
    --filelist filelists/jetclass_val.txt \
    --coffea-worker 12
```

```
FileNotFoundError: [Errno 2] No such file or directory:
  '.../JetClass_val_mod/HToWW2Q1L__eoscms_0_5000.npy'
```

The reported filename varies between runs. Dropping the `root://eoscms.cern.ch/`
prefix makes the identical command succeed (50 `.lz4`, 12 GB, exit 0).

Note a failed run deletes its own `.npy` inputs as the merge consumes them, so
re-running into an existing output dir fails earlier on a *different* file — clear
the directory between attempts or the symptom is misleading.

Switching to plain `/eos/...` paths fixes it (EOS is mounted on lxplus, so XRootD
isn't buying anything there), but the failure is quiet and easy to misread — I spent
a while chasing a phantom race condition before checking the generated names.

Possible fixes: derive the name from the real basename, e.g.
`os.path.splitext(os.path.basename(urlparse(f).path))[0]` plus a chunk index, and/or
raise on duplicate entries in `file_list` instead of silently merging them. The
shipped `shuffled_ParT_files.txt` probably wants regenerating either way.

Happy to open an MR if useful.
