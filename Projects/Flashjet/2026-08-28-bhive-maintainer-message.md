---
tags: [reference]
status: active
date: 2026-08-28
source: lxplus
---

# Draft message to b-hive maintainers

Re: [[2026-08-28-bhive-jetclass-part-setup]]. Mattermost channel is linked from the
b-hive README.

---

Hi — there's a silent data-loss bug affecting any filelist that uses XRootD paths,
including the one committed in the repo. On master (`448bb65`).

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

Switching to plain `/eos/...` paths fixes it (EOS is mounted on lxplus, so XRootD
isn't buying anything there), but the failure is quiet and easy to misread — I spent
a while chasing a phantom race condition before checking the generated names.

Possible fixes: derive the name from the real basename, e.g.
`os.path.splitext(os.path.basename(urlparse(f).path))[0]` plus a chunk index, and/or
raise on duplicate entries in `file_list` instead of silently merging them. The
shipped `shuffled_ParT_files.txt` probably wants regenerating either way.

Happy to open an MR if useful.
