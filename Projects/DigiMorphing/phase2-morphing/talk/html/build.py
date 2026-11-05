#!/usr/bin/env python3
"""Build the HTML deck: copy the figures into img/ and print deck.html to PDF with Chrome.

Usage (from this folder):  python3 build.py
Needs: google-chrome. Figures come from ../figures (../fetch_figures.sh); toy*.svg are made by the
toy generator (exact closing with the kernel's rules) and live in img/ directly.
Same build as the Higgs 2026 HTML deck; it prints slides that spill out of their box.
"""
import os, shutil, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "..", "figures")
IMG = os.path.join(HERE, "img")
COPY = ["CMSlogo_color.png", "VUB_logo.png", "bartosik_dual_quad.png", "schulz_run3_timeline.png",
        "count_difference.png", "cluster_size_phase1style.png", "display_1.png", "display_2_crop.png",
        "display_3_crop.png", "display_4_crop.png", "recovered_digis_gpu_vs_cpu.png", "difference_location.png",
        "clusters_per_module.png", "digis_per_module.png", "cluster_size_L1.png", "recovered_digis_difference.png"]


def images():
    os.makedirs(IMG, exist_ok=True)
    for f in COPY:
        shutil.copy(os.path.join(FIG, f), IMG)


def pdf(src="deck.html", out="phase2_morphing_html.pdf"):
    r = subprocess.run(["google-chrome", "--headless=new", "--disable-gpu", "--no-sandbox",
                        "--no-pdf-header-footer", "--virtual-time-budget=8000",
                        "--enable-logging=stderr", "--v=0",
                        "--print-to-pdf=" + os.path.join(HERE, out), "file://" + os.path.join(HERE, src)],
                       capture_output=True, text=True, timeout=180)
    warn = [l.split('"')[1] for l in r.stderr.splitlines() if "OVERFLOW" in l]
    print("\n".join(warn) if warn else "no overflow")
    print("wrote", out)


if __name__ == "__main__":
    images()
    pdf()
