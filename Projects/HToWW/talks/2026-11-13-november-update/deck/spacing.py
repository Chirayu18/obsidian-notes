"""Keeper 2026-11-13: restore spaces lost between words and numbers in the r2/r3 text.

Applied by build.py to visible text only (not tags, attributes, <code>, URLs).
"""
import re

# Whole phrases whose spaces were all lost (fixed by hand).
PHRASES = {
 'OtherHiggs16includesWHWW,WHtau,ggH,VBF,ZH,ggZH,ttHcomponents.': 'Other Higgs (16) includes WH→WW, WH→ττ, ggH, VBF, ZH, ggZH and ttH components.',
 'Countoneentryperdataset;allselectedbeforecuts.': 'Count one entry per dataset; all selected before cuts.',
 'StandardNanoAODv15preferredperprimary,latestprocessingandextretained;excludeBTV/JME/FastSim.': 'Standard NanoAODv15 preferred per primary, latest processing and ext retained; exclude BTV/JME/FastSim.',
 'NLODYunbinnedE/Mu/Tau10–50,>50;W14pTbins/options,HiggsSMWW/tauandttHchoices.': 'NLO DY unbinned e/μ/τ 10–50, >50; W in 14 pT bins/options; Higgs SM WW/ττ and ttH choices.',
 'missing2024samplesfromliteral2022primaryqueries.': 'missing 2024 samples from literal 2022 primary queries.',
 'selected73datasetoptions.': 'selected 73 dataset options.',
 'individualdecays mayoverlap:do not combineall.': 'individual decays may overlap: do not combine all.',
 'acknowledgement,newproductioncompletion': 'acknowledgement, new production completion',
 'Single-top−1.27/+1.67%,diboson3.7%,Vjets2.7%,Higgs5%are inheritedANprescriptions;not newlycalculated2024orRun3theoryerrors.': 'Single top −1.27/+1.67%, diboson 3.7%, V+jets 2.7%, Higgs 5% are inherited AN prescriptions, not newly calculated 2024 or Run 3 theory errors.',
 'BR1%iscurrentconfiguredprescription;merged-backgroundscopeisbroaderthandecaycomponents.': 'BR 1% is the current configured prescription; its merged-background scope is broader than the decay components.',
 'Features:14kinematic+11c-tagonehot+nSV.': 'Features: 14 kinematic + 11 c-tag one-hot + nSV.',
 'χ²139.4/20 v2185.5/20July, 120.1/155.6withnuisance in savedreport': 'χ² 139.4/20 (v2) vs 185.5/20 (July); 120.1/155.6 with the nuisance in the saved report',
 'tightμ/WP80e,20/10GeV': 'tight μ / WP80 e, 20/10 GeV',
 'discussionposition': 'discussion position', 'maxdifference': 'max difference', 'differentalphaSsteps': 'different αS steps',
 'withnuisance': 'with nuisance', 'savedreport': 'saved report', 'fromOctober': 'from October', 'SourceAugust': 'Source: August',
 'analysis-overviewtex': 'analysis-overview tex', 'H+cPDF': 'H+c PDF', 'H+b+3.36': 'H+b +3.36',
 'CentralH+c': 'Central H+c',
 'CorrectedH+c': 'Corrected H+c',
 'H+bPDF+αSoverlap': 'H+b PDF+αS overlap',
 'H+cαSrate': 'H+c αS rate',
 'HiggsBRscope': 'Higgs BR scope',
 'cuts,DeepJetmediumUL': 'cuts, DeepJet medium UL',
 'draftNOTSENT': 'draft NOT SENT',
 'mirroredDownare': 'mirrored Down are',
 'negrwfit-binclosure': 'negrw fit-bin closure',
 'processingclaim': 'processing claim',
 'provisionalc-tagcalibration': 'provisional c-tag calibration',
 'rawscanROOT': 'raw scan ROOT',
 'remainsmissing': 'remains missing',
 'universalcoverage': 'universal coverage',
 'ttHττcoverage': 'ttH→ττ coverage',
 'rate_tt andautoMCStats are fit/statisticalmodelchoices,not externaltheory uncertainties.': 'rate_tt and autoMCStats are fit/statistical model choices, not external theory uncertainties.',
}
KEEP_PREFIX = {'Run','UL','YR','el','v','NanoAODv','Summer','Winter','Higgs','PDF','LHC','md','ctag','ctag2d','Type',
               'coneRadius','etaJetMax','JMENano','below','above','Hdamp','LHA','HIG','AN','CMSSW','mH','sha','r','μ','pT','Nc','N','WP'}
KEEP_SUFFIX = {'FS','postEE','preEE','postBPix','preBPix','Jets','fr','px','em','nd','st','rd','th','D','Hz','pdgId'}
HEX = re.compile(r'^[0-9a-f]{7,}$')

def fix_token(t):
    core = t.strip('.,;:()“”"')
    if not core or '_' in core or '/' in core and re.search(r'\.\w{2,4}$', core) or HEX.match(core) \
       or re.fullmatch(r'[0-9a-f]{7}(,[0-9a-f]{7})+', core) or re.fullmatch(r'\d+to\d+', core) \
       or re.fullmatch(r'20\d\d(pre|post)(EE|BPix)', core) or core.startswith(('http', 'arXiv', 'AN-')) or 'PDF4LHC' in core:
        return t
    def l2d(m):
        w = m.group(1)
        return m.group(0) if (w in KEEP_PREFIX or len(w) < 2 or w.endswith('v')) else w + ' ' + m.group(2)
    def d2l(m):
        w = m.group(2)
        return m.group(0) if (w in KEEP_SUFFIX or len(w) < 2 or w.startswith(('FS', 'e-'))) else m.group(1) + ' ' + w
    t = re.sub(r'([A-Za-z]+)(\d)', l2d, t)
    t = re.sub(r'(\d)([A-Za-z]+)', d2l, t)
    return t

def fix_text(s):
    for a, b in PHRASES.items():
        s = s.replace(a, b)
    s = re.sub(r'([ντ²])(\d)', r'\1 \2', s)
    s = re.sub(r',(?=[a-z]{2,})', ', ', s)
    s = re.sub(r'(?<=[a-z]):(?=[A-Za-z0-9])', ': ', s)
    return re.sub(r'\S+', lambda m: fix_token(m.group(0)), s)

def fix_html(html):
    out, skip = [], 0
    for part in re.split(r'(<[^>]+>)', html):
        if part.startswith('<'):
            tag = re.match(r'</?(\w+)', part)
            if tag and tag.group(1).lower() in ('code', 'script', 'style'):
                skip += -1 if part.startswith('</') else 1
            out.append(part)
        else:
            out.append(part if skip else fix_text(part))
    return ''.join(out)
