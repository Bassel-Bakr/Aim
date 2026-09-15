"""Theme-aware inline SVG diagrams for the Tension page. Colours come from the .aim-figure classes in
aim.css, so each diagram follows the reader's scheme and picked colour. build.py splices them into the
page; call it rather than this module.
"""
import math

def path(points):
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in points)


def text(x, y, s, cls="fig-ink", anchor="middle", size=15, weight=600):
    return (f'<text x="{x}" y="{y}" class="{cls}" text-anchor="{anchor}" font-size="{size}" '
            f'font-weight="{weight}">{s}</text>')


def scale():
    w, h = 760, 250
    out = [f'<svg viewBox="0 0 {w} {h}" role="img" aria-labelledby="fig-scale-title">',
           '<title id="fig-scale-title">A tension scale from too loose to too tight. Too loose lags behind '
           'and stops. Balanced is a firm hold and one continuous motion. Too tight jitters ahead, '
           'overcorrects and locks out.</title>']
    x0, x1, y = 40, 720, 92
    seg = (x1 - x0) / 3
    names = [("Too loose", "fig-cool-fill", ["Lags behind the target", "Stops and restarts", "Feels sluggish"]),
             ("Balanced", "fig-ink-fill", ["Firm, not hard, hold", "One continuous motion", "Releases after a flick"]),
             ("Too tight", "fig-accent-fill", ["Jitters ahead of the target", "Skips and overcorrects", "Tires fast, locks out"])]
    for i, (name, cls, symptoms) in enumerate(names):
        left = x0 + i * seg
        opacity = "1" if i == 1 else "0.85"
        out.append(f'<rect x="{left + 3:.1f}" y="{y}" width="{seg - 6:.1f}" height="16" rx="8" class="{cls}" '
                   f'opacity="{opacity}"/>')
        cx = left + seg / 2
        out.append(text(cx, y - 16, name, size=18, weight=700))
        for j, s in enumerate(symptoms):
            out.append(text(cx, y + 52 + j * 28, s, "fig-muted", size=17, weight=500))
    out.append(f'<path d="M{x0 + seg * 1.5 - 9} {y - 44} L{x0 + seg * 1.5 + 9} {y - 44} L{x0 + seg * 1.5} {y - 34} Z" '
               'class="fig-ink-fill"/>')
    out.append(text(x0, 22, "less grip force", "fig-muted", "start", 13, 500))
    out.append(text(x1, 22, "more grip force", "fig-muted", "end", 13, 500))
    out.append(f'<path d="M{x0 + 120} 18 L{x1 - 120} 18" class="fig-grid-stroke" stroke-width="1.5" '
               'marker-end="url(#fig-arrow)"/>')
    out.insert(2, '<defs><marker id="fig-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
                  'markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10 Z" class="fig-grid-fill"/></marker></defs>')
    out.append("</svg>")
    return "".join(out)


def tracking():
    w, h = 760, 270
    pw, ph, top = 216, 150, 58
    lefts = [30, 272, 514]
    out = [f'<svg viewBox="0 0 {w} {h}" role="img" aria-labelledby="fig-tracking-title">',
           '<title id="fig-tracking-title">Three graphs of crosshair position against a strafing target over '
           'time. Too tight: the crosshair jitters and overshoots ahead at each change of direction. Too '
           'loose: it lags behind in stalls and catch-ups. Balanced: it follows the target closely.</title>']

    def target(t):
        return math.sin(t * 2 * math.pi * 1.25)

    cases = [
        ("Too tight", "fig-accent-stroke",
         lambda t: target(t + 0.035) * 1.12 + 0.13 * math.sin(t * 2 * math.pi * 9.5) * (0.4 + abs(math.cos(t * 2 * math.pi * 1.25)))),
        ("Too loose", "fig-cool-stroke",
         lambda t: target(math.floor((t - 0.06) * 14) / 14) * 0.88),
        ("Balanced", "fig-ink-stroke",
         lambda t: target(t - 0.008) * 0.98 + 0.025 * math.sin(t * 2 * math.pi * 6)),
    ]
    for (name, cls, fn), left in zip(cases, lefts):
        mid = top + ph / 2
        out.append(f'<rect x="{left}" y="{top}" width="{pw}" height="{ph}" rx="10" class="fig-panel"/>')
        out.append(f'<path d="M{left + 12} {mid} L{left + pw - 12} {mid}" class="fig-grid-stroke" stroke-width="1"/>')
        steps = 240
        tgt = [(left + 12 + (pw - 24) * i / steps, mid - target(i / steps) * ph * 0.34) for i in range(steps + 1)]
        cur = [(left + 12 + (pw - 24) * i / steps, mid - fn(i / steps) * ph * 0.34) for i in range(steps + 1)]
        out.append(f'<path d="{path(tgt)}" class="fig-muted-stroke" stroke-width="3" stroke-dasharray="7 6" fill="none"/>')
        out.append(f'<path d="{path(cur)}" class="{cls}" stroke-width="3.2" fill="none" stroke-linejoin="round"/>')
        out.append(text(left + pw / 2, top - 18, name, size=18, weight=700))
        out.append(text(left + pw / 2, top + ph + 24, "time", "fig-muted", size=13, weight=500))
    ly = h - 16
    out.append(f'<path d="M{250} {ly - 5} L{290} {ly - 5}" class="fig-muted-stroke" stroke-width="3" stroke-dasharray="7 6"/>')
    out.append(text(298, ly, "target", "fig-muted", "start", 14, 500))
    out.append(f'<path d="M{400} {ly - 5} L{440} {ly - 5}" class="fig-ink-stroke" stroke-width="3.2"/>')
    out.append(text(448, ly, "your crosshair", "fig-muted", "start", 14, 500))
    out.append("</svg>")
    return "".join(out)


def flick():
    w, h = 760, 300
    left, right, top, bottom = 70, 730, 50, 220
    out = [f'<svg viewBox="0 0 {w} {h}" role="img" aria-labelledby="fig-flick-title">',
           '<title id="fig-flick-title">Tension over one flick. A managed flick builds tension while preparing, '
           'peaks during the flick, releases before landing, stays low for the micro-correction, and builds '
           'again for the next flick. A held flick keeps tension high through the landing and drifts into '
           'lockout.</title>']
    phases = [("Prepare", 0.0, 0.18), ("Flick", 0.18, 0.36), ("Release", 0.36, 0.5), ("Micro", 0.5, 0.72),
              ("Shoot", 0.72, 0.8), ("Prepare", 0.8, 1.0)]
    span = right - left

    def X(t):
        return left + span * t

    def Y(v):
        return bottom - (bottom - top) * v

    out.append(f'<rect x="{left}" y="{Y(1.0)}" width="{span}" height="{Y(0.86) - Y(1.0):.1f}" class="fig-accent-fill" opacity="0.14"/>')
    out.append(text(left + 10, Y(1.0) + 17, "lockout", "fig-accent-text", "start", 13, 700))
    for i, (name, a, b) in enumerate(phases):
        if i:
            out.append(f'<path d="M{X(a):.1f} {top - 6} L{X(a):.1f} {bottom}" class="fig-grid-stroke" stroke-width="1" stroke-dasharray="3 5"/>')
        out.append(text((X(a) + X(b)) / 2, bottom + 28, name, "fig-muted", size=14, weight=600))
    out.append(f'<path d="M{left} {bottom} L{right} {bottom} M{left} {bottom} L{left} {top - 10}" class="fig-grid-stroke" stroke-width="1.5"/>')
    out.append(text(24, (top + bottom) / 2, "tension", "fig-muted", size=13, weight=500).replace(
        "<text ", f'<text transform="rotate(-90 24 {(top + bottom) / 2})" '))

    def smooth_curve(keys, steps=300):
        pts = []
        for i in range(steps + 1):
            t = i / steps
            for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
                if t0 <= t <= t1:
                    u = (t - t0) / (t1 - t0)
                    u = u * u * (3 - 2 * u)
                    pts.append((X(t), Y(v0 + (v1 - v0) * u)))
                    break
        return pts

    managed = [(0, 0.2), (0.16, 0.5), (0.26, 0.8), (0.4, 0.34), (0.5, 0.2), (0.72, 0.18), (0.8, 0.22), (0.96, 0.5), (1.0, 0.54)]
    held = [(0, 0.2), (0.16, 0.5), (0.26, 0.8), (0.4, 0.8), (0.5, 0.84), (0.72, 0.9), (0.8, 0.93), (0.96, 0.95), (1.0, 0.96)]
    out.append(f'<path d="{path(smooth_curve(held))}" class="fig-accent-stroke" stroke-width="3" stroke-dasharray="8 6" fill="none"/>')
    out.append(f'<path d="{path(smooth_curve(managed))}" class="fig-ink-stroke" stroke-width="3.4" fill="none"/>')
    out.append(text(X(0.6), Y(0.2) - 14, "managed", "fig-ink", size=14, weight=700))
    out.append(text(X(0.44), Y(0.8) + 24, "held", "fig-accent-text", size=14, weight=700))
    out.append("</svg>")
    return "".join(out)
