"""A right hand in a claw grip on a modern symmetrical mouse, rendered for Tension Management.

    blender -b -P hand_scene.py -- --out file.png [--view front|threequarter|side|top|mouse]
        [--forces] [--final] [--no-hand] [--mouse-color r,g,b]

build.py runs this for the page; call it directly only to try a new view.

The mouse is "Razer Viper Mini" by kimberly.h, CC BY 4.0, from Sketchfab; see the note above MODEL.
The hand and forearm are metaballs, so joints blend into one smooth surface, converted to a mesh. The
hand is one flat grey, and the forearm wears a compression sleeve. Every finger is posed by flexion
angles only, so no joint can bend backwards. A sidecar JSON gives label anchor points in image space.
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def arg(name, default=None):
    return argv[argv.index(name) + 1] if name in argv else default


OUT = arg("--out", "render.png")
VIEW = arg("--view", "front")
FORCES, FINAL = "--forces" in argv, "--final" in argv

K = 0.574  # a metaball's surface sits at K * radius at the default threshold

# Mouse: 1 unit is 10 mm. The mouse is "Razer Viper Mini" by kimberly.h
# (https://sketchfab.com/3d-models/razer-viper-mini-85e1735704c645e5aaead0278a1038fe), licensed under
# CC BY 4.0. It is scaled to the real mouse's 118 mm length, turned so its front faces +y, recoloured
# in MOUSE_COLOR, and its logo and underside light strip are removed.
# models/razer-viper-mini/license.txt holds the credit.
MODEL = Path(__file__).resolve().parent / "models" / "razer-viper-mini" / "scene.gltf"
MOUSE_LENGTH = 11.8
# Shell colour as linear RGB, with metallic and roughness for the textured body and the smoother
# buttons. Glossy dark grey by default; --mouse-color r,g,b overrides the colour for a trial render.
MOUSE_COLOR = tuple(float(c) for c in arg("--mouse-color", "0.07,0.07,0.075").split(","))
MOUSE_METALLIC = 0.0
MOUSE_ROUGHNESS = {"Grain": 0.22, "Gloss": 0.12}
BVH = None


def load_mouse():
    """Import the mouse, place it on the pad centred at the origin, and keep a BVH of its surface for
    placing the hand."""
    from mathutils import Matrix
    from mathutils.bvhtree import BVHTree
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(MODEL))
    bpy.context.view_layer.update()
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    points = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
    lo = Vector((min(q.x for q in points), min(q.y for q in points), min(q.z for q in points)))
    hi = Vector((max(q.x for q in points), max(q.y for q in points), max(q.z for q in points)))
    centre = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
    place = (Matrix.Rotation(math.pi / 2, 4, "Z") @ Matrix.Scale(MOUSE_LENGTH / (hi.x - lo.x), 4) @
             Matrix.Translation(-centre))
    verts, polys = [], []
    for o in meshes:
        o.data.transform(place @ o.matrix_world)
        o.parent = None
        o.matrix_world = Matrix.Identity(4)
        name = o.data.materials[0].name
        if name == "Green":
            o.hide_render = True
            continue
        if name in ("Grain", "Gloss"):
            bsdf = next(n for n in o.data.materials[0].node_tree.nodes if n.type == "BSDF_PRINCIPLED")
            # The body's normal map carries the embossed logo, so the body goes without it.
            sockets = ("Base Color", "Metallic", "Roughness") + (("Normal",) if name == "Grain" else ())
            for socket in sockets:
                for link in list(bsdf.inputs[socket].links):
                    o.data.materials[0].node_tree.links.remove(link)
            bsdf.inputs["Base Color"].default_value = (*MOUSE_COLOR, 1)
            bsdf.inputs["Metallic"].default_value = MOUSE_METALLIC
            bsdf.inputs["Roughness"].default_value = MOUSE_ROUGHNESS[name]
        if name != "Skates":
            offset = len(verts)
            verts += [v.co.copy() for v in o.data.vertices]
            polys += [[offset + i for i in poly.vertices] for poly in o.data.polygons]
    for o in list(bpy.context.scene.objects):
        if o.type == "EMPTY":
            bpy.data.objects.remove(o)
    return BVHTree.FromPolygons(verts, polys)


def surface_hit(origin, direction, lift):
    loc, normal, _index, _dist = BVH.ray_cast(Vector(origin), Vector(direction).normalized())
    if loc is None:
        raise ValueError(f"no mouse surface from {origin} toward {direction}")
    if normal.dot(Vector(direction)) > 0:
        normal = -normal
    return loc + normal * lift


def on_top(x, y, lift):
    """The mouse surface straight below (x, y), lifted along its normal."""
    return surface_hit((x, y, 20.0), (0, 0, -1), lift)


def on_side(side, y, z, lift):
    """The mouse's right (side 1) or left (side -1) flank at height z."""
    return surface_hit((side * 20.0, y, z), (-side, 0, 0), lift)


BVH = load_mouse()


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
    knuckle + middle and knuckle + middle again: the joint nearest the tip stays straight, so the
    finger bends at two joints and rests on its pad.
    """
    base, target = Vector(base), Vector(target)
    b = Vector(bend).normalized()
    rel = target - base
    fwd = (rel - b * rel.dot(b)).normalized()
    goal = (rel.dot(fwd), rel.dot(b))
    best = None
    for knuckle in range(-35, 71):
        for middle in range(0, 101):
            angles = (knuckle, knuckle + middle, knuckle + middle)
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


# Phalanx lengths below are an adult hand's; the render uses them at FINGER_LENGTH, and the thumb at
# THUMB_LENGTH, so the fingers do not dwarf the mouse.
FINGER_LENGTH, THUMB_LENGTH = 0.85, 0.91
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


def build_skeleton():
    """Metaball elements as (kind, data), and each finger's joints and radii."""
    elements, joints = [], {}
    palm_mid = (PALM_BACK + PALM_FRONT) / 2
    elements.append(("ellipsoid", (palm_mid, (3.35, (PALM_FRONT - PALM_BACK).length / 2 + 0.2, 1.0), F)))
    elements.append(("capsule", (PALM_FRONT - X * 2.1 - F * 0.35 - U * 0.25, PALM_FRONT + X * 2.5 - F * 0.95 - U * 0.25, 0.85)))
    elements.append(("ball", (PALM_BACK + F * 1.3 - X * 1.9 - U * 0.35, 1.3)))
    elements.append(("ball", (PALM_BACK + F * 1.0 + X * 1.8 - U * 0.3, 1.15)))
    # Wrist and forearm: closely spaced ovals, so the surface stays smooth instead of ribbed.
    arm_axis = (ELBOW - WRIST).normalized()
    for i in range(4):
        t = i / 3
        elements.append(("ellipsoid", (PALM_BACK.lerp(WRIST, t) - U * 0.15, (2.7 - 0.45 * t, 1.0, 1.05 - 0.05 * t), F)))
    for i in range(1, 29):
        t = i / 28
        elements.append(("ellipsoid", (WRIST.lerp(ELBOW, t), (2.25 + 0.6 * t, 1.0, 1.25 + 0.55 * t), arm_axis)))
    for name, (dx, back, lengths, radii, contact) in FINGERS.items():
        radii = [v * 1.18 for v in radii]
        knuckle = PALM_FRONT - F * back + X * dx - U * 0.05
        lengths = [v * FINGER_LENGTH for v in lengths]
        pts = finger_chain(knuckle, contact(radii[2]), lengths, (0, 0, -1))
        joints[name] = (pts, radii)
        r = (radii[0], radii[1], radii[2], radii[2] * 0.92)
        for i in range(3):
            elements.append(("capsule", (pts[i], pts[i + 1], (r[i] + r[i + 1]) / 2)))
    lengths, radii, contact = THUMB
    radii = [v * 1.15 for v in radii]
    lengths = [v * THUMB_LENGTH for v in lengths]
    pts = finger_chain(THUMB_BASE, contact(radii[2]), lengths, (1, 0.1, -0.55))
    joints["thumb"] = (pts, radii)
    r = (radii[0], radii[1], radii[2], radii[2] * 0.92)
    for i in range(3):
        elements.append(("capsule", (pts[i], pts[i + 1], (r[i] + r[i + 1]) / 2)))
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


def smoothstep(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def build_hand(elements):
    mb = bpy.data.metaballs.new("hand")
    mb.resolution = 0.12
    mb.render_resolution = 0.06 if FINAL else 0.1
    obj = bpy.data.objects.new("hand", mb)
    bpy.context.collection.objects.link(obj)
    for kind, data in elements:
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

    # The sleeve starts in a clean ring past the wrist, cut in the shader rather than along mesh faces.
    # It stands slightly proud of the skin, so the cuff reads as an edge. UVs unwrap the arm, u around
    # and v along from the cuff, for the knit pattern.
    cuff = WRIST - F * 1.6
    axis = (ELBOW - cuff).normalized()
    e1 = (Vector((0, 0, 1)) - axis * axis.z).normalized()
    e2 = axis.cross(e1)
    for v in mesh.vertices:
        v.co = v.co + v.normal * 0.07 * smoothstep(-0.03, 0.03, (v.co - cuff).dot(axis))
    uv = mesh.uv_layers.new(name="sleeve")
    for loop in mesh.loops:
        p = mesh.vertices[loop.vertex_index].co - cuff
        along = p.dot(axis)
        d = p - axis * along
        uv.data[loop.index].uv = (math.atan2(d.dot(e2), d.dot(e1)) * 2.6, along)
    mesh.update()
    mesh.materials.append(hand_material())


def hand_material():
    """Flat grey skin, and past the cuff a compression sleeve: matte black knit with a ribbed cuff and
    two accent bands near it."""
    skin, base = (0.2, 0.2, 0.205), (0.012, 0.013, 0.015)
    m = bpy.data.materials.new("hand")
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Sheen Roughness"].default_value = 0.4
    uvn = nt.nodes.new("ShaderNodeUVMap")
    uvn.uv_map = "sleeve"
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(uvn.outputs["UV"], sep.inputs["Vector"])

    def math_node(op, a, b=None):
        n = nt.nodes.new("ShaderNodeMath")
        n.operation = op
        for i, x in enumerate((a, b)):
            if x is None:
                continue
            if isinstance(x, (int, float)):
                n.inputs[i].default_value = x
            else:
                nt.links.new(x, n.inputs[i])
        return n.outputs["Value"]

    u, v = sep.outputs["X"], sep.outputs["Y"]
    color = (0.78, 0.2, 0.12)
    band1 = math_node("MULTIPLY", math_node("GREATER_THAN", v, 1.4), math_node("LESS_THAN", v, 1.85))
    band2 = math_node("MULTIPLY", math_node("GREATER_THAN", v, 2.15), math_node("LESS_THAN", v, 2.35))
    mark = math_node("MAXIMUM", band1, band2)
    sleeve = math_node("GREATER_THAN", v, 0.0)
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.inputs["A"].default_value = (*base, 1)
    mix.inputs["B"].default_value = (*color, 1)
    nt.links.new(mark, mix.inputs["Factor"])
    cloth = nt.nodes.new("ShaderNodeMix")
    cloth.data_type = "RGBA"
    cloth.inputs["A"].default_value = (*skin, 1)
    nt.links.new(sleeve, cloth.inputs["Factor"])
    nt.links.new(mix.outputs["Result"], cloth.inputs["B"])
    nt.links.new(cloth.outputs["Result"], bsdf.inputs["Base Color"])
    nt.links.new(math_node("ADD", 0.55, math_node("MULTIPLY", sleeve, 0.1)), bsdf.inputs["Roughness"])
    nt.links.new(math_node("MULTIPLY", sleeve, 0.1), bsdf.inputs["Sheen Weight"])
    # Ribbed cuff: fine rings over the first stretch of sleeve, and a fine knit along the rest.
    ribs = math_node("MULTIPLY", math_node("SINE", math_node("MULTIPLY", v, 60)),
                     math_node("LESS_THAN", v, 0.8))
    knit = math_node("MULTIPLY", math_node("SINE", math_node("MULTIPLY", u, 90)), sleeve)
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.2
    bump.inputs["Distance"].default_value = 0.01
    height = math_node("MULTIPLY", math_node("ADD", ribs, math_node("MULTIPLY", knit, 0.08)), sleeve)
    nt.links.new(height, bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m


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
    bpy.ops.mesh.primitive_plane_add(size=120, location=(0, -6, -0.01))
    bpy.context.object.data.materials.append(material("pad", (0.085, 0.09, 0.1), 0.95))
    elements, joints = build_skeleton()
    if "--no-hand" not in argv:
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
        "mouse": ((-7.5, 11.5, 9.0), (0.2, 0.6, 1.6), 50),
        "threequarter": ((-6.5, 20.5, 17.5), (0.2, -1.6, 2.9), 42),
        "side": ((-60, 0.0, 2.2), (0, 0.0, 2.0), 110),
        "top": ((0, 0, 60), (0, 0.01, 0), 110),
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
