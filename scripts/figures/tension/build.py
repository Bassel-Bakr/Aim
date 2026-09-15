"""Regenerates the figures on docs/wiki/fundamentals/tension.md.

    python scripts/figures/tension/build.py              # diagrams and renders
    python scripts/figures/tension/build.py --diagrams   # only the three inline SVG diagrams
    python scripts/figures/tension/build.py --renders    # only the two Blender renders

Diagrams are rewritten in place inside the page, matched by each <svg>'s aria-labelledby id, so edit
the drawing code in diagrams.py, never the SVG in the page. Renders run hand_scene.py in Blender (the
BLENDER environment variable, or blender on PATH), then add the callout labels and write WebP files
to docs/assets/images/tension/. Renders need Blender and Pillow; a GPU with OptiX makes them fast.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PAGE = ROOT / "docs" / "wiki" / "fundamentals" / "tension.md"
IMAGES = ROOT / "docs" / "assets" / "images" / "tension"

# name: (scene arguments, labels as anchor, text, offset x, offset y in render pixels)
RENDERS = {
    "grip-zones": (["--view", "front", "--zones"], [
        ("fingers", "Fingertips  ·  micro-corrections", -80, 330),
        ("wrist", "Wrist  ·  narrow, smooth motion", 160, 300),
        ("arm", "Forearm and shoulder  ·  wide, fast motion", -520, -80),
    ]),
    "grip-forces": (["--view", "threequarter", "--forces"], [
        ("squeeze_left", "Side squeeze", 80, -140),
        ("squeeze_right", "Side squeeze", -60, -140),
        ("press", "Downward press", 140, -150),
    ]),
}


def diagrams():
    sys.path.insert(0, str(HERE))
    import diagrams as d

    text = PAGE.read_text(encoding="utf-8")
    for name, svg in (("scale", d.scale()), ("tracking", d.tracking()), ("flick", d.flick())):
        pattern = re.compile(r'<svg [^>]*aria-labelledby="fig-%s-title".*?</svg>' % name, re.S)
        text, count = pattern.subn(lambda _: svg, text)
        if count != 1:
            sys.exit(f"expected one fig-{name} diagram in {PAGE.name}, found {count}")
    PAGE.write_text(text, encoding="utf-8", newline="\n")
    print(f"diagrams written to {PAGE.relative_to(ROOT)}")


def label(render, anchors, labels, out):
    from PIL import Image, ImageDraw, ImageFont

    img = Image.open(render).convert("RGB")
    draw = ImageDraw.Draw(img)
    font = None
    for name in ("seguisb.ttf", "C:/Windows/Fonts/seguisb.ttf", "DejaVuSans-Bold.ttf"):
        try:
            font = ImageFont.truetype(name, 34)
            break
        except OSError:
            continue
    font = font or ImageFont.load_default()
    ink, fill = (255, 255, 255), (20, 22, 28)
    for anchor, text, dx, dy in labels:
        ax, ay = anchors[anchor][0] * img.width, anchors[anchor][1] * img.height
        bx, by = ax + dx, ay + dy
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        w, h = right - left + 36, bottom - top + 24
        draw.line((ax, ay, bx, by), fill=fill, width=5)
        draw.ellipse((ax - 9, ay - 9, ax + 9, ay + 9), fill=fill, outline=ink, width=3)
        draw.rounded_rectangle((bx - w / 2, by - h / 2, bx + w / 2, by + h / 2), radius=h / 2, fill=fill)
        draw.text((bx - (right - left) / 2 - left, by - (bottom - top) / 2 - top), text, font=font, fill=ink)
    img.save(out, quality=88)


def renders():
    blender = os.environ.get("BLENDER") or shutil.which("blender")
    if not blender:
        sys.exit("Blender not found: set BLENDER to blender.exe or put blender on PATH.")
    IMAGES.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        for name, (scene_args, labels) in RENDERS.items():
            render = Path(tmp) / f"{name}.png"
            subprocess.run([blender, "-b", "-P", str(HERE / "hand_scene.py"), "--", "--out", str(render),
                            *scene_args, "--final"], check=True, capture_output=True)
            anchors = json.loads(render.with_suffix(".json").read_text())
            out = IMAGES / f"{name}.webp"
            label(render, anchors, labels, out)
            print(f"render written to {out.relative_to(ROOT)}")


if __name__ == "__main__":
    only = set(sys.argv[1:])
    if not only or "--diagrams" in only:
        diagrams()
    if not only or "--renders" in only:
        renders()
