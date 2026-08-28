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

Hi — hit a silent data-loss bug when using XRootD paths in a filelist, on master
(`448bb65`).

`utils/coffea_processors/base.py:129` builds the per-chunk output name from the input
path:

```python
filename = "_".join(events.metadata["filename"].split("/")[1:]).split(".")[0]
```

The trailing `.split(".")[0]` truncates at the first dot, so
`root://eoscms.cern.ch//eos/cms/store/.../HToBB_000.root` becomes just `_eoscms` —
identical for every file in the list. On 50 JetClass files: 1 unique output basename
with `root://` paths, 50 with plain `/eos/...` paths.

Two effects:
1. All files of a process write to the same `.npy` names and overwrite each other, so
   most of the input is silently dropped.
2. `file_list` then contains each path N times, and `merge_datasets`
   (`utils/dataset/merging.py:131-132`) does `np.load` then `os.remove` per entry —
   the duplicate entry raises `FileNotFoundError` on the already-deleted file. This is
   how it surfaces; it's not worker-count or storage related (fails with
   `--coffea-worker 1` and on local disk too).

Using local paths is a fine workaround, but the failure mode is quiet and easy to
misread, so it might be worth deriving the name from the actual basename (e.g.
`os.path.splitext(os.path.basename(urlparse(f).path))[0]` plus a chunk index), and/or
erroring on duplicate entries in `file_list` rather than merging them.

Happy to open an MR if useful.
