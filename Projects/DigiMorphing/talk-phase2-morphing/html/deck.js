// Draws curved callout arrows. Each <i class="arrow" data-from=".." data-to=".." data-bend=".."> becomes
// an SVG path in its slide. Ends are "id:side" (n s e w ne nw se sw c) or "id@fx,fy", where fx, fy are
// fractions of an image box measured from its bottom-left corner (as read off the plot).
(function () {
  const NS = "http://www.w3.org/2000/svg";
  function point(slide, spec) {
    const sr = slide.getBoundingClientRect();
    let m = spec.match(/^([\w-]+)@([\d.]+),([\d.]+)$/);
    if (m) {
      const r = document.getElementById(m[1]).getBoundingClientRect();
      return [r.left - sr.left + (+m[2]) * r.width, r.top - sr.top + (1 - (+m[3])) * r.height];
    }
    m = spec.match(/^([\w-]+):(\w+)$/);
    const r = document.getElementById(m[1]).getBoundingClientRect();
    const x = { w: r.left, e: r.right, c: (r.left + r.right) / 2 };
    const y = { n: r.top, s: r.bottom, c: (r.top + r.bottom) / 2 };
    const s = m[2];
    const px = s.includes("w") ? x.w : s.includes("e") ? x.e : x.c;
    const py = s.includes("n") ? y.n : s.includes("s") ? y.s : y.c;
    return [px - sr.left, py - sr.top];
  }
  function draw() {
    document.querySelectorAll(".slide").forEach((slide) => {
      const svg = slide.querySelector("svg.arrows");
      if (!svg) return;
      svg.innerHTML = "";
      const defs = document.createElementNS(NS, "defs");
      defs.innerHTML = '<marker id="ah-' + Math.random().toString(36).slice(2) + '" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#e07a1f"/></marker>';
      svg.appendChild(defs);
      const mid = defs.querySelector("marker").id;
      slide.querySelectorAll("i.arrow").forEach((a) => {
        const [x1, y1] = point(slide, a.dataset.from);
        const [x2, y2] = point(slide, a.dataset.to);
        const b = parseFloat(a.dataset.bend || "0.3");
        const mx = (x1 + x2) / 2, my = (y1 + y2) / 2, dx = x2 - x1, dy = y2 - y1;
        const cx = mx - b * dy, cy = my + b * dx;
        const p = document.createElementNS(NS, "path");
        p.setAttribute("d", `M${x1},${y1} Q${cx},${cy} ${x2},${y2}`);
        p.setAttribute("fill", "none");
        p.setAttribute("stroke", "#e07a1f");
        p.setAttribute("stroke-width", "3.2");
        p.setAttribute("stroke-linecap", "round");
        p.setAttribute("marker-end", `url(#${mid})`);
        svg.appendChild(p);
      });
    });
    // flag content that spills out of its slide
    document.querySelectorAll(".slide").forEach((slide, i) => {
      const sr = slide.getBoundingClientRect();
      slide.querySelectorAll("*").forEach((el) => {
        if (el.closest("svg")) return;
        const r = el.getBoundingClientRect();
        if (r.width && (r.right > sr.right + 1 || r.bottom > sr.bottom + 1))
          console.warn("OVERFLOW slide " + (i + 1) + ": " + el.tagName + "." + el.className);
      });
    });
  }
  window.addEventListener("load", draw);
})();
