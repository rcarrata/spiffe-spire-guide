#!/usr/bin/env python3
"""Render .excalidraw files to plain SVG (for Antora image:: macros).

Handles rectangle, ellipse, diamond, line, arrow and text elements, which is
what scripts/gen_excalidraw.py emits and what a normal Excalidraw edit adds.
Not a pixel-perfect Excalidraw renderer: no hand-drawn roughness.

Usage: python3 -I scripts/excalidraw_to_svg.py <in.excalidraw>... <out_dir>
"""
import json
import sys
from html import escape
from pathlib import Path

FONT = "'Red Hat Text','Segoe UI',Helvetica,Arial,sans-serif"


def col(c):
    return "none" if c in (None, "", "transparent") else c


def render(doc):
    els = [e for e in doc["elements"] if not e.get("isDeleted")]
    xs, ys = [], []
    for e in els:
        if e["type"] in ("line", "arrow"):
            for px, py in e["points"]:
                xs.append(e["x"] + px)
                ys.append(e["y"] + py)
        else:
            xs += [e["x"], e["x"] + e["width"]]
            ys += [e["y"], e["y"] + e["height"]]
    pad = 20
    minx, miny = min(xs) - pad, min(ys) - pad
    w, h = max(xs) - minx + pad, max(ys) - miny + pad
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{minx:.0f} {miny:.0f} {w:.0f} {h:.0f}" '
           f'width="{w:.0f}" height="{h:.0f}" font-family="{FONT}">',
           '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="9" markerHeight="9" '
           'markerUnits="userSpaceOnUse" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="context-stroke"/></marker></defs>',
           f'<rect x="{minx:.0f}" y="{miny:.0f}" width="{w:.0f}" height="{h:.0f}" fill="#ffffff"/>']
    for e in els:
        stroke = col(e.get("strokeColor"))
        fill = col(e.get("backgroundColor"))
        sw = e.get("strokeWidth", 2)
        dash = ' stroke-dasharray="8 6"' if e.get("strokeStyle") == "dashed" else ""
        x, y, ew, eh = e["x"], e["y"], e["width"], e["height"]
        t = e["type"]
        if t == "rectangle":
            rx = 10 if e.get("roundness") else 0
            out.append(f'<rect x="{x}" y="{y}" width="{ew}" height="{eh}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{dash}/>')
        elif t == "ellipse":
            out.append(f'<ellipse cx="{x+ew/2}" cy="{y+eh/2}" rx="{ew/2}" ry="{eh/2}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{dash}/>')
        elif t == "diamond":
            pts = f"{x+ew/2},{y} {x+ew},{y+eh/2} {x+ew/2},{y+eh} {x},{y+eh/2}"
            out.append(f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{dash}/>')
        elif t in ("line", "arrow"):
            d = " ".join(("M" if i == 0 else "L") + f"{x+px:.1f} {y+py:.1f}" for i, (px, py) in enumerate(e["points"]))
            m = ""
            if t == "arrow":
                if e.get("endArrowhead"):
                    m += ' marker-end="url(#ah)"'
                if e.get("startArrowhead"):
                    m += ' marker-start="url(#ah)"'
            out.append(f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{sw}"{dash}{m}/>')
        elif t == "text":
            size = e.get("fontSize", 16)
            lh = size * e.get("lineHeight", 1.25)
            align = e.get("textAlign", "left")
            anchor, tx = {"center": ("middle", x + ew / 2), "right": ("end", x + ew)}.get(align, ("start", x))
            lines = e.get("text", "").split("\n")
            spans = "".join(f'<tspan x="{tx:.1f}" dy="{0 if i == 0 else lh:.1f}">{escape(l) or " "}</tspan>'
                            for i, l in enumerate(lines))
            out.append(f'<text x="{tx:.1f}" y="{y + size*0.95:.1f}" font-size="{size}" fill="{stroke}" text-anchor="{anchor}">{spans}</text>')
    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    *ins, outdir = sys.argv[1:]
    Path(outdir).mkdir(parents=True, exist_ok=True)
    for f in ins:
        p = Path(f)
        (Path(outdir) / (p.stem + ".svg")).write_text(render(json.loads(p.read_text())))
        print("svg", p.stem)
