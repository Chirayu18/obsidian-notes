# Plots

---

## Plot Archive

```dataview
TABLE Date, Description, Link, Path
FROM "Projects/HToWW/Plots"
SORT Date DESC
```

---

## Adding New Plots

Create a new note in `Projects/HToWW/Plots/`, then run **Templater → Plot Entry**.
It asks for the EOS path + a description and auto-builds the CERNBox link
(handles the `/eos/home-c/cgupta` → `/eos/user/c/cgupta` conversion for you).
No need to hand-write frontmatter or remember the URL format anymore.

# Quick Commands

## Postprocessing

``` bash
[cgupta@lxplus916 higgscharm]$ python3 run_postprocess.py --help
usage: run_postprocess.py [-h] -w
                          {ctag_pnet_eff,hplusc,hww,hww_Top_CR,hww_Top_CR_high_mll_CR_MVApart1,hww_Top_CR_high_mll_CR_MVApart2,hww_Top_CR_high_mll_CR_MVApart3,hww_Top_CR_noMTl2Cut,hww_Top_CR_noMTllCut,hww_Top_CR_noMTllnoMTl2Cut,hww_Top_CR_noMTllnoMTl2noMllCut,hww_Top_CR_noMTllnoMTl2noMllnoPTllCut,hww_Top_CR_noMTllnoMTl2noMllnoPTllnoBaseMllCut,hww_base,hww_base_Hbkg_Hsig,hww_base_noPTllCut,hww_base_noPTllnoMllCut,hww_high_mll_CR,hww_high_mll_CR_0jet,hww_high_mll_CR_NoNjetCut,hww_high_mll_CR_UntaggedJetsCut,zplusl_os,zplusl_ss,zplusl_ss_intermediate,zplusl_ss_maximal,zplusll_os,zplusl_ss_minimal,zplusll_ss,ztoee,ztomumu,zzto4l,hww_MVA,hww_MVA_allCR}
                          -y {2022,2023,2022preEE,2022postEE,2023preBPix,2023postBPix} [--log] [--postprocess] [--plot] [--yratio_limits YRATIO_LIMITS YRATIO_LIMITS] [--extension {pdf,png}] [--group_by GROUP_BY] [--pass_axis PASS_AXIS] [--nocutflow]
                          [--output_format {coffea,parquet}] [--skipmerging] [--blind] [--mva]

optional arguments:
  -h, --help            show this help message and exit
  -w {ctag_pnet_eff,hplusc,hww,hww_Top_CR,hww_Top_CR_high_mll_CR_MVApart1,hww_Top_CR_high_mll_CR_MVApart2,hww_Top_CR_high_mll_CR_MVApart3,hww_Top_CR_noMTl2Cut,hww_Top_CR_noMTllCut,hww_Top_CR_noMTllnoMTl2Cut,hww_Top_CR_noMTllnoMTl2noMllCut,hww_Top_CR_noMTllnoMTl2noMllnoPTllCut,hww_Top_CR_noMTllnoMTl2noMllnoPTllnoBaseMllCut,hww_base,hww_base_Hbkg_Hsig,hww_base_noPTllCut,hww_base_noPTllnoMllCut,hww_high_mll_CR,hww_high_mll_CR_0jet,hww_high_mll_CR_NoNjetCut,hww_high_mll_CR_UntaggedJetsCut,zplusl_os,zplusl_ss,zplusl_ss_intermediate,zplusl_ss_maximal,zplusll_os,zplusl_ss_minimal,zplusll_ss,ztoee,ztomumu,zzto4l,hww_MVA,hww_MVA_allCR}, --workflow {ctag_pnet_eff,hplusc,hww,hww_Top_CR,hww_Top_CR_high_mll_CR_MVApart1,hww_Top_CR_high_mll_CR_MVApart2,hww_Top_CR_high_mll_CR_MVApart3,hww_Top_CR_noMTl2Cut,hww_Top_CR_noMTllCut,hww_Top_CR_noMTllnoMTl2Cut,hww_Top_CR_noMTllnoMTl2noMllCut,hww_Top_CR_noMTllnoMTl2noMllnoPTllCut,hww_Top_CR_noMTllnoMTl2noMllnoPTllnoBaseMllCut,hww_base,hww_base_Hbkg_Hsig,hww_base_noPTllCut,hww_base_noPTllnoMllCut,hww_high_mll_CR,hww_high_mll_CR_0jet,hww_high_mll_CR_NoNjetCut,hww_high_mll_CR_UntaggedJetsCut,zplusl_os,zplusl_ss,zplusl_ss_intermediate,zplusl_ss_maximal,zplusll_os,zplusl_ss_minimal,zplusll_ss,ztoee,ztomumu,zzto4l,hww_MVA,hww_MVA_allCR}
                        workflow to run
  -y {2022,2023,2022preEE,2022postEE,2023preBPix,2023postBPix}, --year {2022,2023,2022preEE,2022postEE,2023preBPix,2023postBPix}
                        Data year
  --log                 Enable log scale for y-axis
  --postprocess         Enable postprocessing
  --plot                Enable plotting
  --yratio_limits YRATIO_LIMITS YRATIO_LIMITS
                        Set y-axis ratio limits
  --extension {pdf,png}
                        Output file extension for plots
  --group_by GROUP_BY   Axis to group by (e.g., 'process', or a JSON dict)
  --pass_axis PASS_AXIS
                        Binary axis (e.g., 'is_passing_lepton')
  --nocutflow           Enable postprocessing
  --output_format {coffea,parquet}
                        Format of output files
  --skipmerging         Skip parquet outputs merging
  --blind               Blind data
  --mva                 Add MVA training labels to parquet files and generate filelists (hww workflow only)
```


# Notes

## Repository

- Repo size: 292 MB
- Total AFS area: 7.3 GB

# TODO

- [ ] Proceed with 2024 integration
- [ ] Proceed with sample generation for other ERAs