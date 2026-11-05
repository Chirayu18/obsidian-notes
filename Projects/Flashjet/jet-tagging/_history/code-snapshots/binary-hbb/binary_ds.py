"""LZ4Dataset variant that DROPS jets outside the binary task.

Why this exists
---------------
LZ4Dataset sets `truths = np.zeros(...)` and then only reassigns rows whose label
appears in `model_classes`.  With a binary {QCD, Hbb} mapping, the other EIGHT
signal classes (Hcc, Hgg, H4q, Hqql, Zqq, Wqq, Tbqq, Tbl) keep truth 0 and are
silently trained as QCD -- a background ~9x contaminated with other signals.

Gouskos & Maier train "8M signal + 8M background": a CLEAN two-class problem.
So rows that are neither the signal class nor QCD must be REMOVED, not relabelled.

This subclass overrides __iter__ minimally by filtering the raw array `s` right
after it is read, before any truth assignment, using the same trailing-column
layout LZ4Dataset itself uses: [..., process, label_0..label_N, weight].
"""
import numpy as np
import lz4.frame
import torch

from utils.torch.LZ4Dataset import LZ4Dataset


class BinaryFilteredLZ4Dataset(LZ4Dataset):
    """LZ4Dataset restricted to exactly the classes in `model_classes`."""

    def _keep_mask(self, s):
        """True for rows whose truth label is one of the model's classes."""
        labels = s[:, -(self.num_ele + 1):-1]
        keep = np.zeros(s.shape[0], dtype=bool)
        for _name, flavours in self.model_classes.items():
            for flav in flavours:
                idx = self.config_truths.index(flav)
                keep |= (labels[:, idx] == 1)
        return keep

    def __iter__(self):
        worker_info = torch.utils.data.get_worker_info()
        files_to_read = self.files
        if worker_info is not None:
            files_to_read = np.array_split(files_to_read, worker_info.num_workers)[worker_info.id]

        leftover_data = None
        for file in files_to_read:
            if self.verbose:
                print(f"Loading {file}")
            with lz4.frame.open(file, mode='r') as data:
                output_data = data.read()
            s = np.frombuffer(output_data, dtype=self.data_precision).copy()
            s = s[2:].reshape(-1, int(s[1]), order="C")

            # ---- the only change vs LZ4Dataset: drop out-of-task jets ----
            s = s[self._keep_mask(s)]
            if s.shape[0] == 0:
                continue

            if self.out_precision == 'float16':
                max_f16 = np.finfo(np.float16).max
                s = np.clip(s, -max_f16, max_f16).astype(np.float16)

            process = s[:, -(self.num_ele + 2)]
            if self.weighted_sampling:
                random_number = np.random.rand(s.shape[0])
                if not (self.process_weights is None):
                    for proc, proc_w in enumerate(self.process_weights):
                        random_number[process == proc] *= proc_w
                s = s[random_number < s[:, -1]]
                if s.shape[0] == 0:
                    continue

            s = np.random.permutation(s)
            truths = np.zeros(s.shape[0])
            labels = s[:, -(self.num_ele + 1):-1]
            for index, (name, flavours) in enumerate(self.model_classes.items()):
                for flav in flavours:
                    idx = self.config_truths.index(flav)
                    truths[labels[:, idx] == 1] = index
            weights = s[:, -1]
            process = s[:, -(self.num_ele + 2)]
            s = s[:, :-(self.num_ele + 2)]

            if leftover_data is not None:
                s = np.concatenate((leftover_data[0], s))
                truths = np.concatenate((leftover_data[1], truths))
                weights = np.concatenate((leftover_data[2], weights))
                process = np.concatenate((leftover_data[3], process))
                leftover_data = None

            num_samples = s.shape[0]
            for bs in range(0, num_samples, self.batch_size):
                be = min(bs + self.batch_size, num_samples)
                chunk = [s[bs:be], truths[bs:be], weights[bs:be], process[bs:be]]
                if (be - bs) == self.batch_size:
                    yield tuple(chunk)
                else:
                    leftover_data = chunk
            if (leftover_data is not None) and (self.data_type == "test"):
                yield tuple(leftover_data)
        return None
