# exact toy closing (same rules as the kernel) -> SVG panels for the HTML deck
import sys
out = sys.argv[1]
R, C = 15, 9
real = {(r + 2, c) for r, c in [(9,1),(10,1),(8,1),(5,2),(6,2),(2,3),(3,3),(1,3),(2,7)]}
dil = {(r, c) for r in range(R) for c in range(C) if (r, c) not in real
       and any((r+a, c+b) in real for a in (-1,0,1) for b in (-1,0,1))}
filled = lambda r, c: (r, c) in real or (r, c) in dil or not (0 <= r < R)
rec = {p for p in dil if all(filled(p[0]+a, p[1]+b) for a, b in ((1,0),(-1,0),(0,1),(0,-1)))}
BLUE, ORANGE, GREEN, LINE = "#0b4f6c", "#f6c9a4", "#e07a1f", "#c9d6dd"
S = 18  # px per pixel
def panel(cells, x0, colour_of, w=C*S, h=R*S, stroke="#fff"):
    g = [f'<g transform="translate({x0},0)">', f'<rect width="{w}" height="{h}" fill="#fff" stroke="{LINE}"/>']
    for r in range(R):
        for c in range(C):
            col = colour_of(r, c)
            if col: g.append(f'<rect x="{c*S}" y="{(R-1-r)*S}" width="{S}" height="{S}" fill="{col}"/>')
    for c in range(1, C): g.append(f'<line x1="{c*S}" y1="0" x2="{c*S}" y2="{h}" stroke="{LINE}" stroke-width="0.8"/>')
    for r in range(1, R): g.append(f'<line x1="0" y1="{r*S}" x2="{w}" y2="{r*S}" stroke="{LINE}" stroke-width="0.8"/>')
    g.append('</g>'); return "\n".join(g)
A = lambda r, c: BLUE if (r, c) in real else None
B = lambda r, c: BLUE if (r, c) in real else (ORANGE if (r, c) in dil else None)
Cc = lambda r, c: BLUE if (r, c) in real else (GREEN if (r, c) in rec else None)
W, H = C*S, R*S
gap = 70
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-2 -2 {3*W+2*gap+4} {H+4}" font-family="Inter, sans-serif">']
svg += [panel(None, 0, A), panel(None, W+gap, B), panel(None, 2*(W+gap), Cc)]
for x in (W + 12, 2*W + gap + 12):
    svg.append(f'<path d="M{x},{H/2} l{gap-28},0" stroke="#e07a1f" stroke-width="4" marker-end="url(#a)"/>')
svg.insert(1, '<defs><marker id="a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#e07a1f"/></marker></defs>')
svg.append('</svg>')
open(f"{out}/toy.svg", "w").write("\n".join(svg))
for name, f in (("toy_before", A), ("toy_after", Cc)):
    open(f"{out}/{name}.svg", "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-2 -2 {W+4} {H+4}">' + panel(None, 0, f) + '</svg>')
print(len(real), len(dil), len(rec))
