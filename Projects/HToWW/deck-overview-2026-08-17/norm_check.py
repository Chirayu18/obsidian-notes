import glob, pyarrow.parquet as pq

B = "/eos/user/c/cgupta/higgscharm/outputs/hww_combine_2dcat/2022postEE"
# 0J: 100/229 partitions done. Extrapolate sumw to the full sample and compare
# against the expected mean |genWeight| implied by xsec.
NEV = {"WtoLNu_2Jets_0J": (678397952, 229, 55760.0),
       "WtoLNu_2Jets_1J": (522553517, 178, 9529.0),
       "WtoLNu_2Jets_2J": (344572777, 143, 3532.0)}
LUMI = 26670.0  # /pb, 2022postEE

for S,(nev, npart_tot, xsec) in NEV.items():
    dirs = sorted(glob.glob(f"{B}/{S}_*"))
    tot = 0.0
    for d in dirs:
        for f in glob.glob(f"{d}/sumw_records/*.parquet"):
            tot += sum(pq.read_table(f).column("sumw").to_pylist())
    if not dirs: continue
    frac = len(dirs)/npart_tot
    proj = tot/frac
    mean_w = proj/nev
    # read_scale = lumi*xsec/sumw ; expected events at full sumw
    scale = LUMI*xsec/proj
    print(f"{S}:")
    print(f"   partitions done   : {len(dirs)}/{npart_tot}  ({100*frac:.0f}%)")
    print(f"   sumw so far       : {tot:,.3e}")
    print(f"   projected full sumw: {proj:,.3e}")
    print(f"   mean genWeight    : {mean_w:,.1f}")
    print(f"   read_scale        : {scale:.6f}   (lumi*xsec/sumw)")
    print(f"   -> effective evts : {proj*scale:,.0f}  vs lumi*xsec = {LUMI*xsec:,.0f}")
