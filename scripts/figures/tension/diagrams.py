"""Theme-aware inline SVG diagrams for the Tension page. Colours come from the .aim-figure classes in
aim.css, so each diagram follows the reader's scheme and picked colour. build.py splices them into the
page; call it rather than this module.
"""
import math

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


def lane_label(x, y, name, note):
    """A lane's name and a short note on one line, top-left inside its panel. The fig-name and fig-note
    classes let aim.css enlarge them on phones, where a fitted diagram scales its text down."""
    return (f'<text x="{x}" y="{y}"><tspan font-size="16" font-weight="700" class="fig-ink fig-name">{name}</tspan>'
            f'<tspan dx="10" font-size="13" font-weight="500" class="fig-muted fig-note">{note}</tspan></text>')


def crosshair(cls, x, y):
    r = 12
    return (f'<circle cx="{x}" cy="{y}" r="{r}" class="{cls}" stroke-width="2.8" fill="none"/>'
            f'<path d="M{x - r - 8} {y}H{x - r + 6}M{x + r - 6} {y}H{x + r + 8}'
            f'M{x} {y - r - 8}V{y - r + 6}M{x} {y + r - 6}V{y + r + 8}" class="{cls}" stroke-width="2.8"/>')


# Tracking: a target strafes at constant speed with quick turns, and three crosshairs chase it.
# Too tight is a stiff, underdamped follower that runs ahead, overshoots each turn and trembles.
# Too loose is a stick-slip follower that stalls until it falls behind, then darts after the target.
# Balanced follows with a hair of lag. Each follower is simulated for several cycles and the last
# one is kept, so the CSS animation loops seamlessly.
TRK_T = 5.0          # seconds per left-right-left cycle
TRK_FRAMES = 160     # keyframes per cycle
TRK_W, TRK_LANE_H, TRK_TOP = 600, 104, 4
TRK_X0, TRK_X1 = 24, 576
TRK_A = (TRK_X1 - TRK_X0) / 2 - 26
TRK_CX = (TRK_X0 + TRK_X1) / 2


def trk_target(t):
    """Target offset from centre: a triangle wave, rounded just before each turn."""
    phase = (t / TRK_T) % 1.0
    tri = 4 * phase - 1 if phase < 0.5 else 3 - 4 * phase
    if abs(tri) > 0.94:
        excess = abs(tri) - 0.94
        tri = math.copysign(0.94 + excess - excess ** 2 / 0.12, tri)
    return tri * TRK_A


def trk_simulate(step):
    """Run a follower for several cycles and keep the last, so the loop is seamless."""
    dt = TRK_T / 2000
    x, v = 0.0, 0.0
    state = {}
    out = []
    for i in range(2000 * 6):
        t = i * dt
        x, v = step(t, x, v, dt, state)
        if i >= 2000 * 5:
            out.append(x)
    return out


def trk_tight(t, x, v, dt, state):
    k, c = 61.0, 2.3
    a = k * (trk_target(t + 0.094) - x) - c * v
    v += a * dt
    x += v * dt
    return x, v


def trk_loose(t, x, v, dt, state):
    err = trk_target(t) - x
    moving = state.get("moving", False)
    if not moving and abs(err) > 55:
        moving = True
    if moving and abs(err) < 5:
        moving = False
    state["moving"] = moving
    speed = 4 * TRK_A / TRK_T
    v = math.copysign(speed * 2.0, err) if moving else 0.0
    x += v * dt
    return x, v


def trk_balanced(t, x, v, dt, state):
    return trk_target(t - 0.047), 0.0


def trk_tremor(i, n):
    t = i / n
    return 3.2 * math.sin(t * 2 * math.pi * 23) + 2.2 * math.sin(t * 2 * math.pi * 37 + 1.3)


def trk_keyframes(name, xs, extra=None):
    n = len(xs)
    parts = []
    for f in range(TRK_FRAMES + 1):
        i = min(int(f / TRK_FRAMES * n), n - 1)
        dx = xs[i] + (extra(f, TRK_FRAMES) if extra else 0)
        parts.append(f"{f / TRK_FRAMES * 100:.3g}%{{transform:translate({dx:.1f}px,0)}}")
    return f"@keyframes {name}{{{''.join(parts)}}}"


def tracking():
    tg = [trk_target(i * TRK_T / TRK_FRAMES) for i in range(TRK_FRAMES + 1)]
    lanes = [
        ("Too tight", "Overshoots and shakes", "fig-accent-stroke", trk_simulate(trk_tight), trk_tremor),
        ("Too loose", "Lags and stalls", "fig-cool-stroke", trk_simulate(trk_loose), None),
        ("Balanced", "Stays on the target", "fig-ink-stroke", trk_simulate(trk_balanced), None),
    ]
    h = TRK_TOP * 2 + TRK_LANE_H * 3 - 8
    css = [trk_keyframes("aimTrkTarget", tg)]
    body = []
    for i, (name, note, cls, xs, extra) in enumerate(lanes):
        top = TRK_TOP + TRK_LANE_H * i
        y = top + 64
        body.append(f'<rect x="8" y="{top}" width="{TRK_W - 16}" height="{TRK_LANE_H - 8}" rx="12" class="fig-panel"/>')
        body.append(lane_label(TRK_X0, top + 26, name, note))
        body.append(f'<path d="M{TRK_X0} {y}H{TRK_X1}" class="fig-grid-stroke" stroke-width="1" stroke-dasharray="2 6"/>')
        body.append(f'<g class="aim-trk-anim" style="animation-name:aimTrkTarget"><circle cx="{TRK_CX}" cy="{y}" r="15" class="fig-target"/></g>')
        anim = f"aimTrkCursor{i}"
        css.append(trk_keyframes(anim, xs, extra))
        for lag, opacity in ((0.22, 0.14), (0.11, 0.3)):
            body.append(f'<g class="aim-trk-anim" style="animation-name:{anim};animation-delay:{-TRK_T + lag:.2f}s;opacity:{opacity}">{crosshair(cls, TRK_CX, y)}</g>')
        body.append(f'<g class="aim-trk-anim" style="animation-name:{anim}">{crosshair(cls, TRK_CX, y)}</g>')
    css.append(f".aim-trk-anim{{animation-duration:{TRK_T}s;animation-timing-function:linear;animation-iteration-count:infinite}}")
    # Readers who ask for less motion get one telling frame, just after the targets turn.
    css.append("@media (prefers-reduced-motion:reduce){.aim-trk-anim{animation-play-state:paused;"
               f"animation-delay:-{TRK_T * 0.54:.2f}s!important}}}}")
    return (f'<svg viewBox="0 0 {TRK_W} {h}" class="fig-fit" role="img" aria-labelledby="fig-tracking-title">'
            '<title id="fig-tracking-title">Three crosshairs chase a target that strafes left and right at '
            'a constant speed. Too tight: the crosshair runs ahead, overshoots at each turn and shakes. '
            'Too loose: it stalls, falls behind, then catches up in bursts. Balanced: it stays on the '
            'target.</title>'
            f'<style>{"".join(css)}</style>' + "".join(body) + "</svg>")


# Flick: two lanes flick between the same three targets, each with a tension meter at its left edge,
# under a strip that lights up the current phase. Managed builds tension to prepare, peaks for the
# flick and drops it before landing just short, so a small smooth micro-correction finishes the
# flick. Held keeps tension near lockout, so every flick overshoots and wobbles before it settles.
FLK_SEG = 2.2               # seconds per flick
FLK_N = 3
FLK_T = FLK_SEG * FLK_N
FLK_FRAMES = 240
FLK_W, FLK_LANE_H, FLK_TOP = 600, 126, 40
FLK_MX = 40                 # meter x
FLK_TX = [90, 430, 250]     # target x per stop, measured from the meter
FLK_TY = [-12, 8, 18]       # target y offset per stop


def flk_ease_out(u):
    return 1 - (1 - u) ** 3


def flk_smooth(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def flk_pose(t, kind):
    """Crosshair (x, y) offsets from lane centre and tension 0..1 at time t."""
    t %= FLK_T
    k = int(t // FLK_SEG)
    u = (t - k * FLK_SEG) / FLK_SEG
    ax, ay = FLK_TX[k - 1], FLK_TY[k - 1]       # start: previous stop
    bx, by = FLK_TX[k], FLK_TY[k]
    # Phases within a segment: prepare 0-0.22, flick 0.22-0.44, micro 0.44-0.74, shoot 0.74-1.
    if kind == "managed":
        if u < 0.22:
            p = 0.0
        elif u < 0.44:
            p = 0.93 * flk_ease_out((u - 0.22) / 0.22)
        else:
            p = 0.93 + 0.07 * flk_smooth((u - 0.44) / 0.3)
        tension = (0.2 + 0.35 * flk_smooth(u / 0.22) if u < 0.22 else
                   0.55 + 0.3 * flk_smooth((u - 0.22) / 0.08) if u < 0.30 else
                   0.85 - 0.62 * flk_smooth((u - 0.30) / 0.16) if u < 0.46 else
                   0.23 - 0.03 * flk_smooth((u - 0.46) / 0.3) if u < 0.8 else
                   0.2)
        wob = 0.0
    else:
        if u < 0.22:
            p = 0.0
        elif u < 0.4:
            p = 1.14 * flk_ease_out((u - 0.22) / 0.18)
        else:
            s = (u - 0.4) / 0.6
            p = 1 + 0.14 * math.exp(-4.2 * s) * math.cos(s * 2 * math.pi * 3.2)
        tension = 0.88 + 0.04 * math.sin(u * 2 * math.pi * 2)
        wob = 2.6 * math.sin(t * 2 * math.pi * 6) + 1.8 * math.sin(t * 2 * math.pi * 9.5 + 0.7)
    x = ax + (bx - ax) * p + wob
    y = ay + (by - ay) * p + wob * 0.6
    return x, y, tension


def flk_keyframes(name, values, fmt, prop="transform"):
    """Keyframes that skip any frame whose value matches both neighbours, since linear timing between
    equal values changes nothing."""
    text = [fmt(v) for v in values]
    parts = [f"{i / FLK_FRAMES * 100:.4g}%{{{prop}:{v}}}" for i, v in enumerate(text)
             if i in (0, len(text) - 1) or not (text[i - 1] == v == text[i + 1])]
    return f"@keyframes {name}{{{''.join(parts)}}}"


def flick():
    phases = [("Prepare", 0.0, 0.22), ("Flick", 0.22, 0.44), ("Micro", 0.44, 0.74), ("Shoot", 0.74, 1.0)]
    lanes = [("Managed", "Tense, flick, release", "managed", "fig-ink-stroke"),
             ("Held", "Tension never drops", "held", "fig-accent-stroke")]
    h = FLK_TOP + FLK_LANE_H * len(lanes) - 8
    css, body = [], []
    # Phase strip: each label lights up while its phase runs, in every flick of the loop.
    left = FLK_MX + 30
    step = (FLK_W - 8 - left) / len(phases)
    for pi, (label, a, b) in enumerate(phases):
        lit = []
        for i in range(FLK_FRAMES + 1):
            local = (i / FLK_FRAMES * FLK_T) % FLK_SEG / FLK_SEG
            lit.append(1.0 if a <= local < b else 0.28)
        anim = f"aimFlkPhase{pi}"
        css.append(flk_keyframes(anim, lit, lambda v: str(v), "opacity"))
        x = left + step * pi + step / 2
        body.append(f'<text x="{x:.0f}" y="24" text-anchor="middle" font-size="14" font-weight="700" class="fig-ink fig-phase aim-flk-anim" style="animation-name:{anim};animation-timing-function:steps(1,end)">{label.upper()}</text>')
    for li, (name, note, kind, cls) in enumerate(lanes):
        top = FLK_TOP + FLK_LANE_H * li
        cy = top + 70
        body.append(f'<rect x="8" y="{top}" width="{FLK_W - 16}" height="{FLK_LANE_H - 8}" rx="12" class="fig-panel"/>')
        body.append(lane_label(FLK_MX + 24, top + 26, name, note))
        # Tension meter: a track, a lockout band at the top, and a fill that scales from the bottom.
        m_top, m_bottom = top + 14, top + 92
        body.append(f'<rect x="{FLK_MX - 8}" y="{m_top}" width="16" height="{m_bottom - m_top}" rx="4" class="fig-grid-fill" opacity="0.35"/>')
        body.append(f'<rect x="{FLK_MX - 8}" y="{m_top}" width="16" height="{(m_bottom - m_top) * 0.16:.1f}" rx="4" class="fig-accent-fill" opacity="0.35"/>')
        fill_cls = "fig-accent-fill" if kind == "held" else "fig-ink-fill"
        name_bar = f"aimFlkBar{li}"
        body.append(f'<rect x="{FLK_MX - 8}" y="{m_top}" width="16" height="{m_bottom - m_top}" rx="4" class="{fill_cls} aim-flk-anim aim-flk-bar" style="animation-name:{name_bar}"/>')
        body.append(f'<text x="{FLK_MX}" y="{m_bottom + 15}" text-anchor="middle" font-size="10" font-weight="600" class="fig-muted fig-caption">TENSION</text>')
        samples = [flk_pose(i / FLK_FRAMES * FLK_T, kind) for i in range(FLK_FRAMES + 1)]
        css.append(flk_keyframes(name_bar, [s[2] for s in samples], lambda v: f"scaleY({v:.2f})"))
        # Targets, each flashing when the crosshair shoots it.
        for k in range(FLK_N):
            flash = []
            for i in range(FLK_FRAMES + 1):
                t = i / FLK_FRAMES * FLK_T
                local = (t - k * FLK_SEG) % FLK_T / FLK_SEG
                s = 1.0 + (0.45 * (1 - (local - 0.74) / 0.18) if 0.74 <= local < 0.92 else 0.0)
                flash.append(s)
            anim = f"aimFlkDot{li}{k}"
            css.append(flk_keyframes(anim, flash, lambda v: f"scale({v:.2f})"))
            body.append(f'<circle cx="{FLK_TX[k] + FLK_MX}" cy="{cy + FLK_TY[k]}" r="13" class="fig-target aim-flk-anim aim-flk-dot" style="animation-name:{anim}"/>')
        anim = f"aimFlkCursor{li}"
        css.append(flk_keyframes(anim, samples, lambda v: f"translate({v[0] + FLK_MX:.0f}px,{v[1]:.0f}px)"))
        body.append(f'<g class="aim-flk-anim" style="animation-name:{anim}">{crosshair(cls, 0, cy)}</g>')
    css.append(f".aim-flk-anim{{animation-duration:{FLK_T}s;animation-timing-function:linear;animation-iteration-count:infinite}}"
               ".aim-flk-bar,.aim-flk-dot{transform-box:fill-box;transform-origin:center}"
               ".aim-flk-bar{transform-origin:bottom}")
    css.append("@media (prefers-reduced-motion:reduce){.aim-flk-anim{animation-play-state:paused;"
               f"animation-delay:-{FLK_SEG * 0.5:.2f}s!important}}}}")
    return (f'<svg viewBox="0 0 {FLK_W} {h}" class="fig-fit" role="img" aria-labelledby="fig-flick-title">'
            '<title id="fig-flick-title">Two crosshairs flick between the same three targets, each with a '
            'tension meter. Managed: tension rises to prepare, peaks for the flick and drops before landing, '
            'and a small smooth correction finishes each flick. Held: tension stays near lockout, and every '
            'flick overshoots and wobbles before it settles.</title>'
            f'<style>{"".join(css)}</style>' + "".join(body) + "</svg>")


