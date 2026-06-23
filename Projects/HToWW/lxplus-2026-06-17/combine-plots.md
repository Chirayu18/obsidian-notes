---
tags:
  - plot
status: done
date: 2026-06-17
source: lxplus
---

# HToWW plots

Combine final plots (2022postEE, v11 & v32). Binaries live on EOS; links are CERNBox.

### autoMCStats issue — DY/W+jets SR undersampling (2026-06-23)
- **tags:** [plot]
- **Description:** (A) SR stack + MC-stat band exploding under the signal peak; (B) per-bin N_eff (DY≈10 vs others 10³–10⁴); (C) DY ±10⁵ generator weights. See [[2026-06-23-automcstats-rootcause]].
- **Embedded:** ![[automcstats_issue.png]]
- **Path:** `/eos/home-c/cgupta/HToWW/b-hive/docs/plots/combine_final/automcstats_issue.png`
- **Link:** https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/HToWW/b-hive/docs/plots/combine_final/automcstats_issue.png

### autoMCStats fix — DY template smoothing (2026-06-23)
- **tags:** [plot]
- **Description:** (D) raw vs smoothed DY SR template; (E) limit bars 771/1742/1399/1148. Smoothing 1742→1399. See [[2026-06-23-automcstats-rootcause]].
- **Embedded:** ![[automcstats_fix.png]]
- **Path:** `/eos/home-c/cgupta/HToWW/b-hive/docs/plots/combine_final/automcstats_fix.png`
- **Link:** https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/HToWW/b-hive/docs/plots/combine_final/automcstats_fix.png

### Limit comparison (stat + syst, 4-bar)
- **tags:** [plot]
- **Date:** 2026-06-17
- **Description:** v11 & v32 stat-only and with-systematics expected limits (±1σ/±2σ bands); AN-23-102 √L-scaled to 26.7 fb⁻¹ (syst=1148, stat=879). Our stat-only beats AN scaled; with-syst far worse → systematic inflation.
- **Path:** `/eos/home-c/cgupta/HToWW/b-hive/docs/plots/combine_final/limit_comparison_4bar.png`
- **Link:** https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/HToWW/b-hive/docs/plots/combine_final/limit_comparison_4bar.png

### Limit comparison (stat-only only)
- **tags:** [plot]
- **Date:** 2026-06-17
- **Description:** stat-only expected limits v11=771, v32=584 with bands, vs AN stat-only scaled=879. Our floors beat the AN's at equal lumi.
- **Path:** `/eos/home-c/cgupta/HToWW/b-hive/docs/plots/combine_final/limit_comparison_statonly.png`
- **Link:** https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/HToWW/b-hive/docs/plots/combine_final/limit_comparison_statonly.png

### CMS-style impacts — v11
- **tags:** [plot]
- **Date:** 2026-06-17
- **Description:** CMS-style impacts (pulls + Δr̂, r=1 Asimov). Top nuisances are `prop_binSR_hplusc_bin5/6/7` (autoMCStats) — MC-stat dominates.
- **Path:** `/eos/home-c/cgupta/HToWW/b-hive/docs/plots/combine_final/impacts_cms_v11.png`
- **Link:** https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/HToWW/b-hive/docs/plots/combine_final/impacts_cms_v11.png

### CMS-style impacts — v32
- **tags:** [plot]
- **Date:** 2026-06-17
- **Description:** CMS-style impacts for the 13-class kHCE v9 (argmax-with-prior). autoMCStats dominates here too.
- **Path:** `/eos/home-c/cgupta/HToWW/b-hive/docs/plots/combine_final/impacts_cms_v32.png`
- **Link:** https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/HToWW/b-hive/docs/plots/combine_final/impacts_cms_v32.png

### Uncertainty breakdown vs AN Table 18
- **tags:** [plot]
- **Date:** 2026-06-17
- **Description:** grouped |Δr|/r breakdown for v11 & v32 vs AN-23-102 Table 18. Our MC-stat ~41% vs AN 6.2%; our Bkg-Higgs ~1% vs AN 21%.
- **Path:** `/eos/home-c/cgupta/HToWW/b-hive/docs/plots/combine_final/breakdown_vs_AN.png`
- **Link:** https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/HToWW/b-hive/docs/plots/combine_final/breakdown_vs_AN.png

### Likelihood scans
- **tags:** [plot]
- **Date:** 2026-06-17
- **Description:** −2ΔlnL vs r for v11 & v32 (Asimov, r=1 injected) with 68/95% lines.
- **Path:** `/eos/home-c/cgupta/HToWW/b-hive/docs/plots/combine_final/likelihood_scan.png`
- **Link:** https://cernbox.cern.ch/files/spaces/eos/user/c/cgupta/HToWW/b-hive/docs/plots/combine_final/likelihood_scan.png
