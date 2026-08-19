import sys
sys.path.insert(0,"/afs/cern.ch/user/c/cgupta/higgscharm_thomas/higgscharm_thomas_new/higgscharm")
import correctionlib
from analysis.working_points.utils import correction_files
f = correction_files["ctagging"]["2022postEE"]
print("file:", f)
cs = correctionlib.CorrectionSet.from_file(f)
ev = cs["particleNet_wp_values"]
for wp in ["L","M","T"]:
    cvb = ev.evaluate(wp, "CvB")
    cvl = ev.evaluate(wp, "CvL")
    print("  {}: CvB>{:.4f}  CvL>{:.4f}".format(wp, cvb, cvl))
