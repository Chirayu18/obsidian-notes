import os, re, shutil, glob

B = "/eos/user/c/cgupta/higgscharm/outputs/hww_combine_2dcat/2022postEE"
Q = "/eos/user/c/cgupta/higgscharm/outputs/hww_combine_2dcat/2022postEE_old_inclusive_wjets/partitions"

names = sorted(os.listdir(Q))
incl = [n for n in names if re.fullmatch(r"WtoLNu_2Jets(_\d+)?", n)]
jetb = [n for n in names if re.match(r"WtoLNu_2Jets_[012]J", n)]
other = [n for n in names if n not in incl and n not in jetb]
print(f"quarantine total={len(names)} inclusive={len(incl)} jetbinned={len(jetb)} other={len(other)}")
if other:
    print("  OTHER (unexpected):", other[:5])

moved = merged_files = 0
for n in jetb:
    src, dst = os.path.join(Q, n), os.path.join(B, n)
    if not os.path.exists(dst):
        try:
            shutil.move(src, dst); moved += 1
        except Exception as e:
            print("  skip", n, type(e).__name__)
        continue
    # dst exists (job recreated it): merge file-by-file, never overwrite
    for root, _, files in os.walk(src):
        rel = os.path.relpath(root, src)
        tgt = os.path.join(dst, rel) if rel != "." else dst
        os.makedirs(tgt, exist_ok=True)
        for f in files:
            s, d = os.path.join(root, f), os.path.join(tgt, f)
            try:
                if not os.path.exists(d):
                    shutil.move(s, d); merged_files += 1
                else:
                    os.remove(s)      # identical chunk written twice
            except FileNotFoundError:
                pass                  # a running job moved it first
    shutil.rmtree(src, ignore_errors=True)

print(f"moved whole dirs: {moved}   merged individual files: {merged_files}")
rem = sorted(os.listdir(Q))
print(f"quarantine now: {len(rem)}  (all should be inclusive)")
bad = [n for n in rem if not re.fullmatch(r"WtoLNu_2Jets(_\d+)?", n)]
print("non-inclusive left:", bad if bad else "NONE")
for S in ("0J", "1J", "2J"):
    live = glob.glob(f"{B}/WtoLNu_2Jets_{S}") + glob.glob(f"{B}/WtoLNu_2Jets_{S}_*")
    print(f"  live {S}: {len(live)} dirs")
