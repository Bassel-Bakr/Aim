"""A right hand in a claw grip on a modern symmetrical mouse, rendered for the Tension page.

    blender -b -P hand_scene.py -- --out file.png [--view front|threequarter|side|top] [--zones] [--forces] [--final]

build.py runs this for the page; call it directly only to try a new view.

The mouse is a parametric shell loosely modelled on current lightweight symmetrical mice. The hand
and forearm are metaballs, so joints blend into one smooth surface, converted to a mesh whose faces
are coloured by the part of the skeleton they are nearest to. Every finger is posed by flexion angles
only, so no joint can bend backwards. A sidecar JSON gives label anchor points in image space.
"""
import json
import math
import sys
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def arg(name, default=None):
    return argv[argv.index(name) + 1] if name in argv else default


OUT = arg("--out", "render.png")
VIEW = arg("--view", "front")
ZONES, FORCES, FINAL = "--zones" in argv, "--forces" in argv, "--final" in argv

K = 0.574  # a metaball's surface sits at K * radius at the default threshold

# Mouse: 1 unit is about 10 mm. Length 12.5, width about 6.2, height 4.0 with the hump behind centre.
HALF_L = 6.25
SECTION_N = 2.7


def planform(y):
    """Half width at y: slight waist in the middle, blunt rounded front and back."""
    t = y / HALF_L
    base = 3.12 - 0.2 * math.exp(-((y - 0.4) / 2.3) ** 2) + 0.04 * max(0.0, y - 2.0) / 4.25
    p = 3.2 if y < 0 else 5.5
    return base * max(0.0, 1 - abs(t) ** p) ** (1 / p)


def height(y):
    """Crown height at y: hump at y = -1.6, long gentle slope to the buttons, rounded back."""
    t = y / HALF_L
    hump = 2.15 + 1.85 * math.exp(-((y + 1.6) / 4.0) ** 2)
    p = 2.6 if y < 0 else 7.0
    return hump * max(0.0, 1 - abs(t) ** p) ** (1 / p)


def section(y, theta):
    """Surface point on the cross-section at y; theta 0 = right side at the pad, pi/2 = crown."""
    a, b = planform(y), height(y)
    c, s = math.cos(theta), math.sin(theta)
    return Vector((a * math.copysign(abs(c) ** (2 / SECTION_N), c), y, b * abs(s) ** (2 / SECTION_N)))


def surface_frame(y, theta):
    p = section(y, theta)
    y0, y1 = max(y - 0.01, -HALF_L + 0.02), min(y + 0.01, HALF_L - 0.02)
    dy = section(y1, theta) - section(y0, theta)
    dt = section(y, theta + 0.01) - section(y, theta - 0.01)
    n = dt.cross(dy).normalized()
    outward = Vector((p.x, 0, p.z - 0.5)).normalized()
    return p, (n if n.dot(outward) > 0 else -n)


def theta_at_x(x, y):
    lo, hi = 0.02, math.pi - 0.02
    for _ in range(40):
        mid = (lo + hi) / 2
        if section(y, mid).x > x:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def on_top(x, y, lift):
    p, n = surface_frame(y, theta_at_x(x, y))
    return p + n * lift


def on_side(side, y, z, lift):
    s = min(0.999, max(0.0, z / height(y))) ** (SECTION_N / 2)
    theta = math.asin(s)
    if side < 0:
        theta = math.pi - theta
    p, n = surface_frame(y, theta)
    return p + n * lift


# Skeleton.
PITCH = math.radians(19)
F = Vector((0, math.cos(PITCH), math.sin(PITCH)))   # along the palm toward the knuckles
U = Vector((0, -math.sin(PITCH), math.cos(PITCH)))  # out of the back of the hand
X = Vector((1, 0, 0))
CONTACT = on_top(0.25, -4.1, 0.0)                    # palm heel on the rear of the hump
PALM_T = 2.0
PALM_BACK = CONTACT - F * 1.4 + U * (PALM_T / 2)
PALM_FRONT = CONTACT + F * 5.8 + U * (PALM_T / 2 + 0.15)
WRIST = PALM_BACK - F * 1.9 + U * 0.1
ELBOW = Vector((-2.2, WRIST.y - 21.0, 2.2))


def finger_chain(base, target, lengths, bend):
    """Joints from base to target for a finger that only flexes toward `bend`.

    Segment directions are cos(a)*forward + sin(a)*bend, with cumulative angles knuckle,
    knuckle + middle and knuckle + middle * 5/3, as the last two joints of a finger move together.
    """
    base, target = Vector(base), Vector(target)
    b = Vector(bend).normalized()
    rel = target - base
    fwd = (rel - b * rel.dot(b)).normalized()
    goal = (rel.dot(fwd), rel.dot(b))
    best = None
    for knuckle in range(-35, 71):
        for middle in range(0, 101):
            angles = (knuckle, knuckle + middle, knuckle + middle * 5 / 3)
            px = sum(l * math.cos(math.radians(a)) for l, a in zip(lengths, angles))
            py = sum(l * math.sin(math.radians(a)) for l, a in zip(lengths, angles))
            err = (px - goal[0]) ** 2 + (py - goal[1]) ** 2 + 0.003 * middle
            if best is None or err < best[0]:
                best = (err, angles)
    pts = [base]
    for length, a in zip(lengths, best[1]):
        r = math.radians(a)
        pts.append(pts[-1] + (fwd * math.cos(r) + b * math.sin(r)) * length)
    return pts


# name: knuckle offset across the palm, knuckle offset back along F, phalanx lengths,
# radii at knuckle / middle / tip, fingertip contact as a function of fingertip radius.
FINGERS = {
    "index": (-2.05, 0.1, (3.1, 2.1, 1.7), (0.66, 0.58, 0.5), lambda r: on_top(-1.35, 4.3, r)),
    "middle": (-0.35, 0.0, (3.4, 2.3, 1.8), (0.68, 0.6, 0.52), lambda r: on_top(1.2, 4.6, r)),
    "ring": (1.3, 0.35, (3.35, 2.25, 1.75), (0.63, 0.55, 0.48), lambda r: on_side(1, 0.9, 1.2, r)),
    "pinky": (2.75, 1.1, (2.65, 1.8, 1.55), (0.55, 0.49, 0.43), lambda r: on_side(1, -1.6, 0.9, r)),
}
THUMB = ((2.4, 2.3, 1.85), (0.8, 0.66, 0.54), lambda r: on_side(-1, -0.2, 1.35, r))
THUMB_BASE = PALM_BACK + F * 2.2 - X * 2.6 - U * 0.35


JOINTS = {}


def build_skeleton():
    """Metaball elements as (kind, data, zone), and each finger's joints and radii."""
    elements, joints = [], {}
    palm_mid = (PALM_BACK + PALM_FRONT) / 2
    elements.append(("ellipsoid", (palm_mid, (3.35, (PALM_FRONT - PALM_BACK).length / 2 + 0.2, 1.0), F), "palm"))
    elements.append(("capsule", (PALM_FRONT - X * 2.1 - F * 0.35 - U * 0.25, PALM_FRONT + X * 2.5 - F * 0.95 - U * 0.25, 0.85), "palm"))
    elements.append(("ball", (PALM_BACK + F * 1.3 - X * 1.9 - U * 0.35, 1.3), "palm"))
    elements.append(("ball", (PALM_BACK + F * 1.0 + X * 1.8 - U * 0.3, 1.15), "palm"))
    # Wrist and forearm: closely spaced ovals, so the surface stays smooth instead of ribbed.
    arm_axis = (ELBOW - WRIST).normalized()
    for i in range(4):
        t = i / 3
        elements.append(("ellipsoid", (PALM_BACK.lerp(WRIST, t) - U * 0.15, (2.7 - 0.45 * t, 1.0, 1.05 - 0.05 * t), F), "wrist"))
    for i in range(1, 29):
        t = i / 28
        elements.append(("ellipsoid", (WRIST.lerp(ELBOW, t), (2.25 + 0.6 * t, 1.0, 1.25 + 0.55 * t), arm_axis), "arm"))
    for name, (dx, back, lengths, radii, contact) in FINGERS.items():
        radii = [v * 1.18 for v in radii]
        knuckle = PALM_FRONT - F * back + X * dx - U * 0.05
        pts = finger_chain(knuckle, contact(radii[2]), lengths, (0, 0, -1))
        joints[name] = (pts, radii)
        r = (radii[0], radii[1], radii[2], radii[2] * 0.92)
        for i in range(3):
            elements.append(("capsule", (pts[i], pts[i + 1], (r[i] + r[i + 1]) / 2), "fingers"))
    lengths, radii, contact = THUMB
    radii = [v * 1.15 for v in radii]
    pts = finger_chain(THUMB_BASE, contact(radii[2]), lengths, (1, 0.1, -0.55))
    joints["thumb"] = (pts, radii)
    r = (radii[0], radii[1], radii[2], radii[2] * 0.92)
    for i in range(3):
        elements.append(("capsule", (pts[i], pts[i + 1], (r[i] + r[i + 1]) / 2), "fingers" if i else "palm"))
    return elements, joints


def material(name, color, rough=0.55, emit=0.0, sss=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = rough
    if sss:
        bsdf.inputs["Subsurface Weight"].default_value = sss
        bsdf.inputs["Subsurface Radius"].default_value = (0.6, 0.3, 0.2)
        bsdf.inputs["Subsurface Scale"].default_value = 0.08
    if emit:
        bsdf.inputs["Emission Color"].default_value = (*color, 1)
        bsdf.inputs["Emission Strength"].default_value = emit
    return m


def shade_smooth(obj):
    for poly in obj.data.polygons:
        poly.use_smooth = True


def look(obj, target):
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = (Vector(target) - obj.location).to_track_quat("-Z", "Y")


def tube(a, b, r, mat):
    a, b = Vector(a), Vector(b)
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=r, depth=max((b - a).length, 1e-3), location=(a + b) / 2)
    obj = bpy.context.object
    obj.rotation_mode = "QUATERNION"
    obj.rotation_quaternion = (b - a).to_track_quat("Z", "Y")
    obj.data.materials.append(mat)
    shade_smooth(obj)
    for end in (a, b):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=end, segments=24, ring_count=12)
        s = bpy.context.object
        s.data.materials.append(mat)
        shade_smooth(s)


def build_mouse():
    rows, cols = 140, 72
    ys = [-HALF_L + 2 * HALF_L * (0.5 - 0.5 * math.cos(math.pi * i / (rows - 1))) for i in range(rows)]
    bm = bmesh.new()
    grid = [[bm.verts.new(section(y, math.pi * j / (cols - 1))) for j in range(cols)] for y in ys]
    for i in range(rows - 1):
        for j in range(cols - 1):
            bm.faces.new((grid[i][j], grid[i][j + 1], grid[i + 1][j + 1], grid[i + 1][j]))
        bm.faces.new((grid[i][cols - 1], grid[i][0], grid[i + 1][0], grid[i + 1][cols - 1]))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-4)
    me = bpy.data.meshes.new("mouse")
    bm.to_mesh(me)
    obj = bpy.data.objects.new("mouse", me)
    bpy.context.collection.objects.link(obj)
    shade_smooth(obj)
    me.materials.append(material("mouse", (0.03, 0.032, 0.038), 0.42))

    seam = material("seam", (0.0, 0.0, 0.0), 0.9)

    def groove(points):
        for a, b in zip(points, points[1:]):
            tube(a, b, 0.035, seam)

    groove([on_top(0.0, 0.6 + 0.3 * i, -0.005) for i in range(19)])
    for side in (-1, 1):
        groove([on_top(side * 0.1 * i, 0.6 - 0.008 * i * i, -0.005) for i in range(29)])
    tube(on_top(0, 2.3, 0.14), on_top(0, 3.35, 0.14), 0.26, material("wheel", (0.16, 0.16, 0.18), 0.5))
    side_btn = material("side", (0.05, 0.052, 0.06), 0.35)
    for y0, y1 in ((1.9, 0.9), (0.6, -0.4)):
        tube(on_side(-1, y0, 2.05, 0.02), on_side(-1, y1, 2.05, 0.02), 0.2, side_btn)


def build_hand(elements):
    mb = bpy.data.metaballs.new("hand")
    mb.resolution = 0.12
    mb.render_resolution = 0.06 if FINAL else 0.1
    obj = bpy.data.objects.new("hand", mb)
    bpy.context.collection.objects.link(obj)
    for kind, data, _zone in elements:
        e = mb.elements.new()
        if kind == "ball":
            c, r = data
            e.type, e.co, e.radius = "BALL", c, r / K
        elif kind == "capsule":
            a, b, r = Vector(data[0]), Vector(data[1]), data[2]
            e.type, e.co, e.radius = "CAPSULE", (a + b) / 2, r / K
            e.size_x = (b - a).length / 2
            e.rotation = (b - a).to_track_quat("X", "Z")
        else:
            c, (sx, sy, sz), axis = data
            e.type, e.co, e.radius = "ELLIPSOID", c, 1 / K
            e.size_x, e.size_y, e.size_z = sx, sy, sz
            e.rotation = Vector(axis).to_track_quat("Y", "Z")
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    mesh = bpy.data.meshes.new_from_object(obj.evaluated_get(dg))
    bpy.data.objects.remove(obj)
    hand = bpy.data.objects.new("hand_mesh", mesh)
    bpy.context.collection.objects.link(hand)
    shade_smooth(hand)

    skin = material("skin", (0.8, 0.62, 0.48), 0.5, sss=0.12)
    mats = {"palm": skin, "fingers": skin, "wrist": skin, "arm": skin}
    if ZONES:
        mats["fingers"] = material("z_fingers", (0.93, 0.42, 0.16), 0.5, 0.25)
        mats["wrist"] = material("z_wrist", (0.1, 0.55, 0.88), 0.5, 0.25)
        mats["arm"] = material("z_arm", (0.52, 0.34, 0.9), 0.5, 0.25)
    order = ["palm", "fingers", "wrist", "arm"]
    for name in order:
        mesh.materials.append(mats[name])

    def dist(p, kind, data):
        if kind == "ball":
            return (p - Vector(data[0])).length - data[1]
        if kind == "capsule":
            a, b, r = Vector(data[0]), Vector(data[1]), data[2]
            ab = b - a
            t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))
            return (p - (a + ab * t)).length - r
        return (p - Vector(data[0])).length - min(data[1]) * 0.8

    # A face is a finger's when it hugs that finger's bones and lies past its knuckle, so the colour
    # boundary is a clean ring at the knuckle rather than following whichever blob is nearest.
    chains = []
    for name, (pts, radii) in JOINTS.items():
        start = 1 if name == "thumb" else 0
        # Fingers cut at a plane across the knuckles, along the palm; the thumb at its own joint.
        axis = (pts[start + 1] - pts[start]).normalized() if name == "thumb" else F
        chains.append((pts, radii, pts[start], axis))

    def on_finger(p):
        for pts, radii, knuckle, axis in chains:
            if (p - knuckle).dot(axis) < 0.35:
                continue
            for i in range(3):
                a, b = pts[i], pts[i + 1]
                ab = b - a
                t = max(0.0, min(1.0, (p - a).dot(ab) / ab.length_squared))
                if (p - (a + ab * t)).length < radii[min(i, 2)] + 0.22:
                    return True
        return False

    # The wrist is one band across the joint, whichever element a face happens to sit nearest.
    band_a, band_b = PALM_BACK - F * 0.9, WRIST - F * 1.6
    ab = band_b - band_a
    for poly in mesh.polygons:
        p = poly.center
        if on_finger(p):
            zone = "fingers"
        else:
            t = (p - band_a).dot(ab) / ab.length_squared
            zone = "wrist" if 0 <= t <= 1 else ("arm" if t > 1 else "palm")
        poly.material_index = order.index(zone)


def arrow(tip, direction, length, mat, radius=0.12):
    """A slim arrow ending at tip; returns the tail point."""
    d = Vector(direction).normalized()
    tip = Vector(tip)
    head_len, head_r = 0.7, radius * 3.0
    bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=radius, depth=length - head_len,
                                        location=tip - d * (head_len + (length - head_len) / 2))
    shaft = bpy.context.object
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=head_r, radius2=0, depth=head_len,
                                    location=tip - d * head_len / 2)
    cone = bpy.context.object
    for part in (shaft, cone):
        part.rotation_mode = "QUATERNION"
        part.rotation_quaternion = d.to_track_quat("Z", "Y")
        part.data.materials.append(mat)
    return tip - d * length


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    build_mouse()
    bpy.ops.mesh.primitive_plane_add(size=120, location=(0, -6, -0.01))
    bpy.context.object.data.materials.append(material("pad", (0.085, 0.09, 0.1), 0.95))
    elements, joints = build_skeleton()
    JOINTS.update(joints)
    build_hand(elements)
    mp, mr = joints["middle"]
    anchors = {
        "fingers": (mp[1] + mp[2]) / 2 + Vector((0, 0, mr[1])),
        "wrist": WRIST + U * 1.3,
        "arm": WRIST.lerp(ELBOW, 0.35) + Vector((0, 0, 1.7)),
    }
    if FORCES:
        squeeze = material("squeeze", (0.1, 0.55, 0.88), 0.4, 0.8)
        press = material("press", (0.93, 0.42, 0.16), 0.4, 0.8)
        gap = 0.12
        tp, tr = joints["thumb"]
        rp, rr = joints["ring"]
        ip, ir = joints["index"]
        anchors["squeeze_left"] = arrow(tp[-1] - X * (tr[2] + gap), X, 3.0, squeeze)
        anchors["squeeze_right"] = arrow(rp[-1] + X * (rr[2] + gap), -X, 3.0, squeeze)
        press_dir = Vector((0.55, 0.0, -0.84)).normalized()
        anchors["press"] = arrow(ip[-1] - press_dir * (ir[2] + gap), press_dir, 2.8, press)
    return anchors


def lights_camera():
    world = bpy.data.worlds.new("world")
    bpy.context.scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.9, 0.9, 0.93, 1)
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.35
    for loc, energy, size in (((-12, 10, 22), 9000, 12), ((16, -6, 14), 2600, 10), ((0, 18, 6), 1500, 8)):
        bpy.ops.object.light_add(type="AREA", location=loc)
        light = bpy.context.object
        light.data.energy, light.data.size = energy, size
        look(light, (0, -2, 3))
    cams = {
        "front": ((-13.5, 16.0, 16.0), (0.3, -2.6, 3.2), 42),
        "threequarter": ((-6.5, 20.5, 17.5), (0.2, -1.6, 2.9), 42),
        "side": ((-26, -1.5, 6.5), (0, -2.8, 3.4), 48),
        "top": ((-4, -2, 30), (0, -2.5, 2.5), 40),
    }
    loc, target, lens = cams[VIEW]
    bpy.ops.object.camera_add(location=loc)
    cam = bpy.context.object
    look(cam, target)
    cam.data.lens = lens
    bpy.context.scene.camera = cam


def render(anchors):
    from bpy_extras.object_utils import world_to_camera_view
    scene = bpy.context.scene
    scene.render.resolution_x, scene.render.resolution_y = (1600, 1000) if FINAL else (800, 500)
    scene.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "OPTIX"
    prefs.get_devices()
    for d in prefs.devices:
        d.use = d.type == "OPTIX"
    scene.cycles.device = "GPU"
    scene.cycles.samples = 256 if FINAL else 32
    scene.cycles.use_denoising = True
    scene.view_settings.view_transform = "AgX"
    scene.render.filepath = str(Path(OUT).resolve())
    bpy.context.view_layer.update()
    out = {}
    for name, p in anchors.items():
        c = world_to_camera_view(scene, scene.camera, Vector(p))
        out[name] = [round(c.x, 4), round(1 - c.y, 4)]
    Path(OUT).with_suffix(".json").write_text(json.dumps(out))
    bpy.ops.render.render(write_still=True)


anchors = build()
lights_camera()
render(anchors)
