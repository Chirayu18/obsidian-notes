import sys

p = 'analysis/workflows/hww_combine_2dcat.yaml'
s = open(p).read()

# 1. uncomment top_pt
old1 = '''    # COMMENTED OUT until the reprocessing campaign produces weight_top_pt.
    # - top_pt'''
new1 = '''    - top_pt'''
if old1 not in s:
    sys.exit('ANCHOR 1 MISSING (top_pt)')
s = s.replace(old1, new1, 1)

# 2. uncomment higgs_plus_c -- find its commented block
import re
m = re.search(r'( *# COMMENTED OUT until the reprocessing campaign produces weight_higgs_plus_c; the\n(?: *#[^\n]*\n)*? *# - higgs_plus_c)', s)
if not m:
    sys.exit('ANCHOR 2 MISSING (higgs_plus_c)')
s = s.replace(m.group(1), '    - higgs_plus_c', 1)

# 3. comment out the flavor_composition_ggH lnN
old3 = '    flavor_composition_ggH: {higgsbkg: 1.066}'
new3 = ('    # SUPERSEDED by the per-event `higgs_plus_c` shape (higgsHFWeight).\n'
        '    # Kept commented so the two never double-count the same physics.\n'
        '    # flavor_composition_ggH: {higgsbkg: 1.066}')
if old3 not in s:
    sys.exit('ANCHOR 3 MISSING (flavor_composition_ggH)')
s = s.replace(old3, new3, 1)

open(p, 'w').write(s)
print('enabled top_pt + higgs_plus_c, disabled flavor_composition_ggH')
