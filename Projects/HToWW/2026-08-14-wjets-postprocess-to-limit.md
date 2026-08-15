---
tags: [reference]
status: active
date: 2026-08-14
source: lxplus
---

# HANDOFF — W+jets jet-binned: postprocess → inference → datacard → limit (2026-08-14)

Continues [[2026-08-13-wjets-session-handoff]] (now superseded) and
[[2026-08-13-wjets-jetbinned-replacement]]. Task A1.1 of
[[2026-08-12-master-task-list]].

---

## 0. WHERE WE ARE — RESULT

The 2026-08-13 session left the reprocessing done but **nothing downstream run**.
This session ran the whole pipeline forward:
**postprocess ✅ → inference ✅ → datacard ✅ → limit ✅**.

> ### 🎯 **Expected limit 1160 → 1034 (−126, −10.9%)**
> ### V+jets `n_eff` in SR_hplusc: **279.8 → 1169.6 (×4.18)**, rel. stat. err **5.98% → 2.92%**
>
> Full detail and caveats in **§6**. The gain is **4.18×, not the 15.6× projected** —
> and the comparison is **not a clean A/B test** (§6 caveat, §10).

The **1160 baseline card was backed up before the rebuild** (§5), so the
comparison point is preserved even though the builder overwrites in place.

**Next action:** the open questions in **§10**, chiefly re-deriving a clean
baseline so the W+jets contribution can be isolated.

---

## 1. Corrections to the 2026-08-13 handoff

Three claims in the previous note were wrong. Each was checked against source,
not assumed.

### 1.1 `outputs/` is a symlink to EOS — AFS and EOS are ONE tree

```
outputs -> /eos/user/c/cgupta/higgscharm/outputs   (resolves /eos/home-c/cgupta/...)
```

The old note's §4 says "postprocess reads from AFS, not EOS", that the AFS
quarantine moved 39 items while "EOS reported 0 moved", and that 13 stale EOS
parquets need separate treatment. **All one tree seen twice.** The single `mv`
already moved both. Acting on the note as written risks a redundant second
cleanup.

It also means **AFS quota is irrelevant to postprocess output**. The AFS volume
sits at 92% of 10 GB (alarming-looking), but the 98 GB output tree is on EOS
(petabyte-scale, ~46% used).

### 1.2 `make_combine_inputs_v2.py` never globs `parquets_*` — stale dirs are inert

The old note flagged "CHECK THIS" on whether the card builder would pick up
stale merged parquets. It does not. Its only glob is `base_dir/"*Up"`; sample
lists come from `base.gather_samples(year, process_map)`, which iterates the
**dataset config** and maps each sample's `process` field. Proven directly:

```
vjets -> ['DYto2L_2Jets_10to50', 'DYto2L_2Jets_50',
          'WtoLNu_2Jets_0J', 'WtoLNu_2Jets_1J', 'WtoLNu_2Jets_2J']
old inclusive 'WtoLNu_2Jets' in list: False
```

So the leftover `parquets_TBbarQ`, `parquets_TbarBQ` and
`parquets_WtoLNu_2Jets` dirs **cannot** enter the card and **cannot**
double-count W+jets. No cleanup needed.

### 1.3 The `mva` dir-count check is misleading

The old note says: `find ... -name mva -type d | wc -l` — "baseline was 14, must
grow". **It will not grow.** Those 14 are one per *variation*
(12 shift dirs + nominal + `mva_labeled`), not per dataset, and inference
refreshes them in place. Applying the check literally would wrongly suggest
failure.

**Use the per-variation sample-list check instead** (§4.2) — that is what
actually catches the silent-drop bug.

---

## 2. Environment on the new laptop — SSH multiplexing

**There is no headless lxplus login on this machine.** A valid Kerberos TGT is
NOT sufficient (`Permission denied (publickey,gssapi-with-mic,keyboard-interactive)`),
the local key is not registered at CERN, there is no sshfs mount, and there is no
Ollama — so **`vault-search` is unavailable here** and the `code` tier cannot be
indexed.

The working setup (`~/.ssh/config`):

```
Host lxplus lx980
    User cgupta
    ControlMaster auto
    ControlPath ~/.ssh/cm-%r@%h:%p
    ControlPersist 8h
    ServerAliveInterval 30
    TCPKeepAlive yes
Host lxplus
    HostName lxplus.cern.ch
Host lx980
    HostName lxplus980.cern.ch     # pinned: tmux + /tmp scratch live here
```

The **user logs in once interactively** (`ssh -MNf lx980`); every later
`ssh lx980 '<cmd>'` reuses the socket with no re-auth.

### Three traps hit this session

1. **Never use a login shell.** `ssh lx980 'bash -lc "..."'` auto-starts zellij,
   which panics `could not get terminal attribute: ENOTTY` and eats all output.
   Use `bash -c`.
2. **Host keys are per-node.** `lxplus980.cern.ch` was not in `known_hosts`
   (only `lxplus.cern.ch` was), so `ssh -MNf` died on
   `Host key verification failed` **before prompting** — `-N -f` shows no error.
   All three lxplus980 fingerprints are **identical** to the trusted
   `lxplus.cern.ch` ones (CERN shares one host key across the pool), so adding
   them trusts nothing new.
3. **`lxplus.cern.ch` is round-robin.** After a socket death, reconnecting via
   the generic alias lands on a *different* node where the tmux session and
   `/tmp` files do not exist. Always reconnect via `lx980`.

### ⚠️ THE BIG ONE: lxplus kills your jobs on logout

`/etc/systemd/logind.conf` has **`KillUserProcesses = yes`** and `Linger` was
`no`. When the SSH master socket died at **12:57:48**, systemd reaped the tmux
server and **killed the running postprocess** — the log's last-write time matches
the socket death exactly. tmux being "detached" does NOT protect you.

**FIXED PERMANENTLY:**

```bash
loginctl enable-linger cgupta     # succeeded; Linger=yes
```

Verify with `loginctl show-user cgupta | grep -i Linger` before starting any long
job. Without this, every long run is hostage to the SSH connection.

---

## 3. Partition completeness — verified properly (the old note's 550/550 was not checked)

The previous note asserted 550/550 partitions. This session **measured** it, and
on stronger evidence than a partition count. The key insight: `sumw_records/` is
written for **every chunk processed regardless of selection**, while `base/` only
appears if events survive. So "ran but nothing survived" and "job died" are
distinguishable.

| sample | dirs | ran | dead | ran-but-empty | sumw chunks | unique input files | fileset files |
|---|---|---|---|---|---|---|---|
| 0J | 229 | **229** | **0** | 104 | 7,283 | 3,432 | 3,432 |
| 1J | 178 | **178** | **0** | 0 | 5,469 | 2,669 | 2,669 |
| 2J | 143 | **143** | **0** | 0 | 3,920 | 2,135 | 2,135 |
| **total** | **550** | **550** | **0** | 104 | 16,672 | **8,236** | **8,236** |

**Unique input-file UUIDs recovered from `sumw_records` = 8,236 = the fileset
count exactly.** Every input file was read.

The 104 empty 0J partitions are genuinely *"ran, zero survivors"* — they carry
full `sumw_records` and merely lack `base/`. 229 − 104 = **125**, which is
exactly the merged-file count. Physically expected: 0J means no additional
ME-level jet, against a selection demanding ≥1 c-jet.

> This is the discipline mistake #2 of the old note warns about. **Count against
> the expected total, and prefer a selection-independent record (`sumw_records`)
> over anything the selection can zero out.**

---

## 4. Pipeline steps run

### 4.1 Postprocess

Pre-flight replicated postprocess's own discovery path
(`glob(outputs/*/*.coffea)` → `get_sample_name` → config lookup) **before**
launching, to predict the `KeyError: 'TBbarQ'` blocker rather than hit it:

```
coffea files 1017 | distinct samples 53 | config entries 85 | ORPHANS 0
W+jets present: WtoLNu_2Jets_0J, _1J, _2J   (inclusive absent)
```

The `TBbarQ` blocker was genuinely cleared by the previous session's quarantine.
Note the raw partition dirs were the culprit — `parquets_TBbarQ` was *not*, since
the glob only reaches dirs containing `.coffea`.

**Run 1** (12:12) was killed by the logout reaper at 12:57 (§2), after completing
the **merge stage** (all 12 shift dirs) and 46/53 samples of histogram filling.

**Run 2** (13:43, `--skipmerging` to reuse the completed merge) →
**`POSTPROCESS_EXIT=0`, 53/53 samples, no errors**, done 14:14.

> `--skipmerging` saved ~30 min. **There is NO `--mva` flag** — `README_HToWW.md`
> documented one that does not exist; **fixed this session** (backup
> `README_HToWW.md.bak_pre_mvaflag_20260814_122053`). Real flags:
> `--postprocess --output_format --skipmerging --plot --blind --nworkers ...`

### 4.2 Inference

```bash
python3 scripts/mva/run_inference.py --workflow hww_combine_2dcat --year 2022postEE \
    --model-path .../SimpleMLP_MultiClass/epochs_30/nominal/best_model.pt \
    --bhive-config HPlusCHToWW_2dcats
```

`--variation` defaults to `None` → `discover_variations()` returns nominal + every
dir containing `*.parquet` directly or an `mva/` subdir. Partition dirs and
`parquets_*` hold only subdirs, so they are correctly skipped.

**`INFERENCE_EXIT=0`, 14 variations** (nominal + 12 shifts + `mva_labeled`), 32 min.

**The verification that matters** — per-variation scored-sample lists:

| variation | scored files | 0J | 1J | 2J | old inclusive |
|---|---|---|---|---|---|
| nominal | 67 | Y | Y | Y | absent |
| each of 12 `CMS_*` shifts | 47 | Y | Y | Y | **present (stale)** |

The stale `WtoLNu_2Jets.parquet` in the shift dirs' `mva/` is dated
**Aug 10 17:35** — a leftover from the *previous* inference run. Its **input** was
correctly quarantined (it lives in `2022postEE_old_inclusive_wjets/merged/<shift>/`),
so nothing was re-scored. **`run_inference` writes new outputs but never deletes
stale ones.** Provably inert via §1.2, so it was left alone.

(nominal 67 vs shifts 47 = data eras, which carry no object shifts.)

### 4.3 Datacard

```bash
python3 scripts/combine/make_combine_inputs_v2.py --workflow hww_combine_2dcat --year 2022postEE
```

Six processes, six channels, 10 bins each.

---

## 5. The 1160 baseline card was BACKED UP before the rebuild

`make_combine_inputs_v2.py` **overwrites in place**, which would have destroyed
the only reference point. Backed up first:

```
/eos/user/c/cgupta/higgscharm/outputs/combine/
    v11_hplusc_2dcat.txt.baseline1160_20260814_150636   (19,847 B)
    v11_hplusc_2dcat.root.baseline1160_20260814_150636  (1,133,932 B)
```

Sizes match the originals exactly. **Rollback = copy these back.**

### n_eff measurement method — validated against the baseline first

`n_eff = (Σw)² / Σσ²`, read from the datacard ROOT file. Validated on the
untouched baseline **before** applying it to the new card:

```
SR_hplusc_vjets: rate=1507.7234  sum_err2=8125.65  n_eff=279.8  rel_stat_err=5.98%
```

Reproduces the known 280 / 5.98% exactly.

---

## 6. RESULTS ✅

```
combine -M AsymptoticLimits v11_hplusc_2dcat.txt -t -1 --run blind \
        --noFitAsimov --mass 120 -n JetBinnedWJets      # LIMIT_EXIT=0
```

| quantity | baseline (2026-08-12) | jet-binned | change |
|---|---|---|---|
| **expected limit (50%)** | **1160** | **1034** | **−126 (−10.9%)** |
| V+jets `n_eff` (SR_hplusc) | 279.8 | **1169.6** | **×4.18** |
| V+jets rel. stat. err (SR) | 5.98% | **2.92%** | **halved** |
| V+jets Σσ² (SR) | 8125.65 | 1983.65 | ÷4.1 |
| V+jets rate (SR_hplusc) | 1507.72 | 1523.15 | +1.0% |

Full expected band: **517 / 707 / 1034 / 1599 / 2480**.

### The gain is 4.18×, NOT the projected 15.6×

The previous session projected `n_eff` ~4,400 / ~1.5% and explicitly said to
re-measure rather than trust it. **That warning was correct.** The 15.6× was an
*effective-luminosity* estimate over the whole samples; the SR gain depends on
which events survive the ≥1 c-jet selection, and negrw was already recovering
part of the cancellation loss in the baseline. **4.18× is the real number.**

### The yield barely moved — this is a statistics gain, not a yield change

V+jets SR rate moved only **+1.0%** (1507.72 → 1523.15) while the statistical
error **halved**. That is the signature you want. A large rate shift would have
indicated a normalisation bug (double-count, wrong xsec, negrw renorm failure).
It did not happen — and §1.2 independently proves the old inclusive cannot enter
the card.

### ⚠️ CAVEAT — the comparison is not purely a W+jets A/B test

Other processes also moved between the two cards, though **only W+jets was
intentionally changed**:

| process | baseline SR | new SR | Δ |
|---|---|---|---|
| hplusc | 0.2610 | 0.260 | −0.4% |
| higgsbkg | 131.09 | 132.47 | +1.1% |
| **tt** | **16938.76** | **17744.25** | **+4.8%** |
| **st** | **1486.76** | **1542.85** | **+3.8%** |
| diboson | 599.53 | 609.30 | +1.6% |
| vjets | 1507.72 | 1523.15 | +1.0% |

Most likely cause: this session **re-merged all 887 partitions from scratch**,
whereas the Aug-12 baseline used whatever merge existed then — so the new card
probably has *more complete* `tt`/`st` inputs. (`TBbarQ`/`TbarBQ` were disabled
before the baseline was built, so that is not the explanation.)

**Direction matters:** more background yield normally makes a limit *worse*, so
this effect works **against** the improvement. The true W+jets contribution is
therefore plausibly **larger** than 126 units, not smaller. But this is
**unverified** — see §10.

Also logged: `Clipped 67 non-positive nominal bins to floor`, 1626 histograms
written, 6 object-shift systematics folded. The clip count was **not** compared
against the baseline build (no log kept from Aug 12).

---

## 7. NEW FINDING — 10 declared samples are silently missing from the analysis

The card builder logged 10 `[skip]` lines. **All pre-existing** (verified: no
partition dirs, no scored parquets anywhere, so the Aug-12 baseline skipped them
too — the comparison is unaffected). But they represent real statistics being
dropped:

| process | missing samples |
|---|---|
| `tt` | `TTto2L2Nu-ext`, `TTto4Q-ext`, `TTtoLNu2Q-ext` |
| `st` | `TWminusto2L2Nu-ext`, `TWminusto4Q-ext`, `TWminustoLNu2Q-ext`, `TbarWplusto2L2Nu-ext`, `TbarWplusto4Q-ext`, `TbarWplustoLNu2Q-ext` |
| `diboson` | `WZto3LNu` |

All are **active (not commented out) in `2022postEE_nanov12.yaml`** but were never
processed. The `-ext` samples roughly double the available `tt`/`st` statistics.
Since autoMCStats is the dominant systematic (−255 of −523), this is plausibly
the *next* lever after W+jets — though `tt`/`st` already have ≤1.1% relative
stat error, so the gain is likely much smaller than the V+jets one.

**Action:** decide whether to process them. Unrelated to W+jets; do not bundle.

---

## 8. Reproduce / resume

```bash
# 0. access (user must do this once - see §2)
ssh -MNf lx980

# 1. ALWAYS check before a long job
ssh lx980 'loginctl show-user cgupta | grep -i Linger'   # must be Linger=yes

# 2. env
export MAMBA_EXE=/eos/user/c/cgupta/EPR_task/b-hive/micromamba/micromamba
export MAMBA_ROOT_PREFIX=/eos/user/c/cgupta/EPR_task/b-hive/micromamba
cd /afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm

# 3. combine env
source /cvmfs/cms.cern.ch/cmsset_default.sh
cd /afs/cern.ch/user/c/cgupta/CMSSW_14_1_0_pre4/src && eval "$(scram runtime -sh)"
```

Helper scripts left on lxplus `/tmp` (node **lxplus980**, so they die with the
node): `postproc.sh`, `infer.sh`, `card.sh`, `limit.sh`, `verify_parts.py`,
`verify_mva.py`, `check_gather.py`, `neff.py`.

---

## 9. Mistakes made this session

1. **Repeated the old note's 550/550 as if verified.** Called the sparse 0J merge
   "benign" from reasoning alone. The user pushed back; the proper check (§3)
   confirmed it but on far stronger evidence. **Do not launder an inherited claim
   into a verified one.**
2. **Wrongly guessed `parquets_TBbarQ` caused the `KeyError`.** Reading the glob
   showed it only reaches dirs containing `.coffea`. Caught before acting.
3. **Claimed tmux would survive the SSH drop.** It did not — `KillUserProcesses`
   (§2). Cost a 45-minute postprocess run.
4. **Said the stale shift-dir `WtoLNu_2Jets.parquet` was "freshly scored".** It
   was an Aug 10 leftover; timestamps corrected the story.
5. **Nested-quoting through `ssh 'bash -c "..."'` mangled a Python f-string.**
   Write the script locally and pipe it: `cat f.py | ssh lx980 'cat > /tmp/f.py'`.
6. **Twice misread the card build's phase from its log** — called an empty `ps`
   "the process died" (wrong PID via `tail -1`), and called the finished
   per-sample loop "writing now" when a 13-cycle object-shift pass was still to
   come. Both produced over-optimistic ETAs. **Measure a line rate; do not infer
   progress from what the code "should" be doing.**
7. **Listed LOWESS smoothing as a cost of the card build without checking.** It
   is `smooth_shapes: false` (disabled 2026-07-31 because negrw *replaces*
   template smoothing). The user caught this. Smoothing and clipping also run
   once at the end, never per cycle.

---

## 10. OPEN QUESTIONS / NEXT ACTIONS

1. **⚠️ Isolate the true W+jets effect (highest priority).** `tt` (+4.8%) and
   `st` (+3.8%) moved between the cards even though only W+jets changed (§6
   caveat). The 1160 baseline is from **2026-08-12**, before this session
   re-merged everything. **Until a baseline is rebuilt from the current
   inputs with only the inclusive W+jets restored, the 126-unit improvement
   cannot be attributed wholly to W+jets.** Since the background yields moved
   *up*, the W+jets gain is probably *understated* — but verify, do not assume.
   The rollback material for exactly this test is in §5 and §7 of
   [[2026-08-13-wjets-session-handoff]].
2. **Per-process `n_eff` comparison was never completed.** The script
   (`/tmp/cmp_cards.py`, laptop copy in the job scratch) opens both cards and
   diffs rate + `n_eff` per channel × process. The SSH master died before it
   finished; **only the SR yields were recovered, from the logs.** Re-run it.
3. **Compare the "Clipped 67 non-positive nominal bins" count** against a
   baseline build. Expected to grow with sparser shift templates, but unverified.
4. **Re-run the frozen-autoMCStats test.** The whole premise was that
   autoMCStats costs −255, of which −225 is the SR. With SR V+jets `n_eff` now
   4.18× larger, re-measure how much of that penalty remains — that tells you
   whether V+jets statistics is still the leading lever or whether the next
   systematic (`scalevar_muF`, −69) has taken over.
5. **The 10 missing samples of §7** — decide whether to process them.
6. **`mva_labeled` is scored as a 14th pseudo-variation** by
   `discover_variations()` (it contains an `mva/` subdir). Harmless but wasteful;
   consider adding it to the skip list alongside `mva`/`training`/`filelists`.
