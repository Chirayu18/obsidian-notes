#!/usr/bin/env python3
"""Build the HTML deck: convert CMS figures to PNG (with crops) and print deck.html to PDF.

Usage (from this folder):  python3 build.py           # images (if missing) + PDF
                            python3 build.py --images  # force re-conversion
                            python3 build.py sample.html  # print another file
Needs: pdftoppm (poppler), google-chrome. Figures come from ../figures (fetch_figures.sh).
"""
import os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "..", "figures")
IMG = os.path.join(HERE, "img")
DPI = 220

# name -> crop in pt as (left, bottom, right, top), same as the beamer trims
FIGS = {
    "HIG-21-018_Figure-aux_011": None,
    "HIG-21-008_Figure_001": None, "HIG-21-008_Figure_002-b": None, "HIG-21-008_Figure_003": None,
    "HIG-21-008_Figure_004": None, "HIG-21-008_Figure-aux_001": None,
    "HIG-21-012_Figure_002-a": None,
    "HIG-24-018_Figure_001": None, "HIG-24-018_Figure_002": None, "HIG-24-018_Figure_003": None,
    "HIG-24-018_Figure_004": None, "HIG-24-018_Figure_005": None, "HIG-24-018_Figure_006": None,
    "HIG-24-018_Figure_0B3": None, "HIG-24-018_Figure_0B6": None,
    "HIG-24-018_Figure_B12": None, "HIG-24-018_Figure_B13": None,
    "HIG-23-010_Figure_001": None, "HIG-23-010_Figure_006": None,
    "HIG-24-009_Figure_005": None, "HIG-24-009_Figure_006": None, "HIG-24-009_Figure_007": None,
    "HIG-24-009_Figure_008": None,
    "HIG-25-003_Figure_008-d": None,
    "HIG-23-013_Figure_006": (0, 0, 205, 0),
    "HIG-23-011_Figure_009": (180, 0, 0, 176),
    "SMP-22-012_Figure_005": None,
    "HIG-19-006_Figure_011-a": None, "HIG-19-006_Figure_014-a": None,
    "BTV-25-002_Figure_005": (0, 0, 197, 0),
    "BTV-25-002_Figure_022": (200, 0, 0, 0),
    "BTV-25-002_Figure_023": (0, 0, 199, 0),
    "PAS-TOP-26-003_Figure_009": None,
}
COPY = ["DP-2025-081_sl14_roc_c_tagging.png", "CMSlogo_color.png", "VUB_logo.png"]


def page_size(pdf):
    out = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
    line = [l for l in out.splitlines() if l.startswith("Page size")][0].split()
    return float(line[2]), float(line[4])


def images(force=False):
    os.makedirs(IMG, exist_ok=True)
    for name, crop in FIGS.items():
        out = os.path.join(IMG, name + ".png")
        if os.path.exists(out) and not force:
            continue
        pdf = os.path.join(FIG, name + ".pdf")
        cmd = ["pdftoppm", "-r", str(DPI), "-png", "-singlefile"]
        if crop:
            w, h = page_size(pdf)
            l, b, r, t = crop
            s = DPI / 72.0
            cmd += ["-x", str(int(l * s)), "-y", str(int(t * s)),
                    "-W", str(int((w - l - r) * s)), "-H", str(int((h - t - b) * s))]
        subprocess.run(cmd + [pdf, os.path.join(IMG, name)], check=True)
    for f in COPY:
        shutil.copy(os.path.join(FIG, f), IMG)


def pdf(src="deck.html", out="higgs2026_higgs_charm.pdf"):
    r = subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox",
                        "--no-pdf-header-footer", "--virtual-time-budget=8000",
                        "--enable-logging=stderr", "--v=0",
                        "--print-to-pdf=" + os.path.join(HERE, out), "file://" + os.path.join(HERE, src)],
                       capture_output=True, text=True, timeout=180)
    warn = [l.split('"')[1] for l in r.stderr.splitlines() if "OVERFLOW" in l]
    print("\n".join(warn) if warn else "no overflow")
    print("wrote", out)


if __name__ == "__main__":
    images(force="--images" in sys.argv)
    if "--no-pdf" in sys.argv:
        sys.exit(0)
    src = next((a for a in sys.argv[1:] if a.endswith(".html")), "deck.html")
    pdf(src, src.replace(".html", ".pdf") if src != "deck.html" else "higgs2026_higgs_charm.pdf")
