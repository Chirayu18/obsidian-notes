import glob, os, collections, pyarrow.parquet as pq
B="/eos/user/c/cgupta/higgscharm/outputs/hww_combine_2dcat/2022postEE"
seen=collections.defaultdict(list)
for d in glob.glob(f"{B}/WtoLNu_2Jets_0J")+glob.glob(f"{B}/WtoLNu_2Jets_0J_*"):
    for f in glob.glob(f"{d}/sumw_records/*.parquet"):
        seen[os.path.basename(f)].append(f)
dups={k:v for k,v in seen.items() if len(v)>1}
print(f"unique names={len(seen)}  names with >1 copy={len(dups)}")
same=diff=0
for k,v in list(dups.items())[:400]:
    vals=[]
    for f in v:
        try: vals.append(round(sum(pq.read_table(f).column("sumw").to_pylist()),3))
        except Exception: vals.append(None)
    if len(set(vals))==1: same+=1
    else:
        diff+=1
        if diff<=3: print("  DIFFERING:",k,vals,[os.path.dirname(x).split('/')[-2] for x in v])
print(f"identical-value duplicates: {same}   differing: {diff}")
ex=list(dups.items())[0]
print("\nexample name:",ex[0])
for f in ex[1]: print("   ",f.replace(B+'/',''))
