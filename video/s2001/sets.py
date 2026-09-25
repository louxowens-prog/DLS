"""Blender sets for the 2001-style short. Run inside Python with `bpy` (Blender as a module).

Each build_* function constructs one set in an empty scene and returns an `animate(u)` callback
(u = 0..1 across the shot) that moves camera/objects for that moment. Screens that will receive
composited display graphics are registered by name in SCREENS so their projected corners can be
exported for 2D compositing (the digital stand-in for the film's rear-projected 16mm displays).
"""
import math
import random

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

BAND_W, BAND_H = 1080, 490      # 2.20:1
SCREENS = {}


# ---------------------------------------------------------------- scene plumbing

def reset(samples=16):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 4
    sc.render.use_persistent_data = True
    sc.render.resolution_x, sc.render.resolution_y = BAND_W, BAND_H
    sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    w = bpy.data.worlds.new("world")
    w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = (0, 0, 0, 1)
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.0
    sc.world = w
    SCREENS.clear()
    return sc


def camera(loc, look_at, lens=24):
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    cam.data.lens = lens
    cam.data.clip_end = 5000
    aim(cam, loc, look_at)
    return cam


def aim(obj, loc, look_at):
    obj.location = Vector(loc)
    d = Vector(look_at) - Vector(loc)
    obj.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


def sun(rot_deg, energy=5.0, angle=0.3):
    s = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN"))
    bpy.context.scene.collection.objects.link(s)
    s.data.energy = energy
    s.data.angle = math.radians(angle)          # tiny angle = hard, film-set sun
    s.rotation_euler = tuple(math.radians(a) for a in rot_deg)
    return s


def mat(name, color, rough=0.5, metal=0.0, emit=None, emit_strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = emit_strength
    return m


def box(name, loc, size, material, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=tuple(math.radians(r) for r in rot))
    o = bpy.context.object
    o.name = name
    o.scale = size
    o.data.materials.append(material)
    return o


def sphere(name, loc, r, material, seg=96, smooth=True):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=seg, ring_count=seg // 2)
    o = bpy.context.object
    o.name = name
    if smooth:
        bpy.ops.object.shade_smooth()
    o.data.materials.append(material)
    return o


def planet_mat(name, c1, c2, scale=3.0, bump=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    n = nt.nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = scale
    n.inputs["Detail"].default_value = 8
    cr = nt.nodes.new("ShaderNodeValToRGB")
    cr.color_ramp.elements[0].color = (*c1, 1)
    cr.color_ramp.elements[1].color = (*c2, 1)
    cr.color_ramp.elements[0].position = 0.45
    cr.color_ramp.elements[1].position = 0.62
    b = nt.nodes["Principled BSDF"]
    nt.links.new(n.outputs["Fac"], cr.inputs["Fac"])
    nt.links.new(cr.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.9
    if bump:
        bn = nt.nodes.new("ShaderNodeBump")
        bn.inputs["Strength"].default_value = bump
        nt.links.new(n.outputs["Fac"], bn.inputs["Height"])
        nt.links.new(bn.outputs["Normal"], b.inputs["Normal"])
    return m


def ground(name, size, material, strength=0.4, scale=0.6, sub=6, loc=(0, 0, 0)):
    bpy.ops.mesh.primitive_plane_add(size=size, location=loc)
    g = bpy.context.object
    g.name = name
    g.data.materials.append(material)
    s = g.modifiers.new("sub", "SUBSURF")
    s.subdivision_type = "SIMPLE"
    s.levels = s.render_levels = sub
    tex = bpy.data.textures.new(name + "tex", "CLOUDS")
    tex.noise_scale = scale
    dm = g.modifiers.new("disp", "DISPLACE")
    dm.texture = tex
    dm.strength = strength
    return g


def screen(name, loc, size, rot=(0, 0, 0)):
    """A dark display panel; its corners are exported for 2D compositing."""
    o = box(name, loc, size, mat(name + "m", (0.005, 0.005, 0.008), 0.3, emit=(0.02, 0.03, 0.05), emit_strength=1.0), rot)
    SCREENS[name] = o
    return o


def screen_corners():
    """Projected pixel corners (tl, tr, br, bl) of each screen's front face, in band pixels."""
    sc = bpy.context.scene
    cam = sc.camera
    out = {}
    for name, o in SCREENS.items():
        mw = o.matrix_world
        pts = []
        # the thin axis is the local axis with the smallest scale; use the face toward the camera
        sx, sy, sz = o.scale
        thin = min(range(3), key=lambda i: (sx, sy, sz)[i])
        axes = [i for i in range(3) if i != thin]
        cam_local = mw.inverted() @ cam.matrix_world.translation
        side = 0.5 if cam_local[thin] > 0 else -0.5
        for a, b in ((-0.5, 0.5), (0.5, 0.5), (0.5, -0.5), (-0.5, -0.5)):
            v = [0.0, 0.0, 0.0]
            v[thin] = side
            v[axes[0]] = a
            v[axes[1]] = b
            p = world_to_camera_view(sc, cam, mw @ Vector(v))
            pts.append((p.x * BAND_W, (1 - p.y) * BAND_H, p.z))
        # order as tl, tr, br, bl in image space
        pts.sort(key=lambda q: q[1])
        top = sorted(pts[:2], key=lambda q: q[0])
        bot = sorted(pts[2:], key=lambda q: q[0])
        out[name] = [top[0][:2], top[1][:2], bot[1][:2], bot[0][:2]]
    return out


# ---------------------------------------------------------------- sets

def earth_mat(name="earthm"):
    """Dark oceans, muted land, thin white cloud: Earth as photographed from orbit."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    land = nt.nodes.new("ShaderNodeTexNoise")
    land.inputs["Scale"].default_value = 1.6
    land.inputs["Detail"].default_value = 6
    lr = nt.nodes.new("ShaderNodeValToRGB")
    lr.color_ramp.elements[0].color = (0.006, 0.02, 0.07, 1)
    lr.color_ramp.elements[0].position = 0.54
    lr.color_ramp.elements[1].color = (0.11, 0.09, 0.055, 1)
    lr.color_ramp.elements[1].position = 0.56
    cloud = nt.nodes.new("ShaderNodeTexNoise")
    cloud.inputs["Scale"].default_value = 5.5
    cloud.inputs["Detail"].default_value = 10
    cr = nt.nodes.new("ShaderNodeValToRGB")
    cr.color_ramp.elements[0].position = 0.55
    cr.color_ramp.elements[1].position = 0.72
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    nt.links.new(land.outputs["Fac"], lr.inputs["Fac"])
    nt.links.new(cloud.outputs["Fac"], cr.inputs["Fac"])
    nt.links.new(cr.outputs["Color"], mix.inputs["Factor"])
    nt.links.new(lr.outputs["Color"], mix.inputs["A"])
    mix.inputs["B"].default_value = (0.85, 0.87, 0.9, 1)
    nt.links.new(mix.outputs["Result"], b.inputs["Base Color"])
    b.inputs["Roughness"].default_value = 0.8
    return m


def build_alignment():
    """The dawn alignment: Moon's limb below, Earth above it, the Sun cresting behind - thin crescents."""
    reset(24)
    bpy.context.scene.render.film_transparent = True
    moon = sphere("moon", (0, 40, -118), 110, planet_mat("moonm", (0.1, 0.1, 0.1), (0.4, 0.4, 0.39), 6.0, bump=0.5))
    earth = sphere("earth", (0, 260, 18), 42, earth_mat())
    sunobj = sphere("sunball", (0, 700, 80), 5, mat("sunm", (1, 1, 1), emit=(1, 0.98, 0.93), emit_strength=60))
    light = sun((-80, 0, 0), 9.0, 0.5)
    cam = camera((0, -40, -6), (0, 260, 20), lens=50)

    def animate(u):
        e = u * u * (3 - 2 * u)
        earth.location.z = 2 + 22 * e
        sunobj.location.z = 120 + 60 * e
        light.rotation_euler = (math.radians(-84 + 8 * e), 0, 0)    # light travels toward camera: thin crescents
    return animate


def build_centrifuge():
    """The ring corridor: seamless white floor curving up ahead, strip lights, consoles and display screens."""
    reset(16)
    R, width, n = 12.0, 3.2, 90
    white = mat("white", (0.8, 0.8, 0.78), 0.4)
    grey = mat("grey", (0.28, 0.28, 0.3), 0.5)
    lightm = mat("strip", (1, 1, 1), emit=(1, 0.98, 0.92), emit_strength=9)
    for i in range(n):
        a = 2 * math.pi * i / n
        seg = 2 * math.pi * R / n * 1.12
        rot = (0, -math.degrees(a), 0)
        box(f"floor{i}", (math.sin(a) * R, 0, -math.cos(a) * R), (seg, width, 0.1), white, rot)
        box(f"ceil{i}", (math.sin(a) * (R - 3.2), 0, -math.cos(a) * (R - 3.2)), (seg * 0.9, width, 0.08), grey, rot)
        if i % 3 == 0:
            box(f"strip{i}", (math.sin(a) * (R - 3.12), 0, -math.cos(a) * (R - 3.12)), (seg * 1.6, 0.5, 0.03), lightm, rot)
        for sgn in (-1, 1):
            box(f"wall{i}{sgn}", (math.sin(a) * (R - 1.6), sgn * width / 2, -math.cos(a) * (R - 1.6)), (seg, 0.08, 3.2),
                white, rot)
    for k, a_deg in enumerate((9, 17, 25)):
        a = math.radians(a_deg)
        for sgn in (-1, 1):
            loc = (math.sin(a) * (R - 1.25), sgn * (width / 2 - 0.08), -math.cos(a) * (R - 1.25))
            box(f"bezel{k}{sgn}", loc, (1.45, 0.05, 1.0), grey, (0, -math.degrees(a), 0))
            screen(f"scr{k}{'L' if sgn < 0 else 'R'}", (loc[0], loc[1] - sgn * 0.04, loc[2]), (1.25, 0.02, 0.82),
                   (0, -math.degrees(a), 0))
    cam = camera((0, 0, -R + 1.55), (4.0, 0, -R + 1.9), lens=14)

    def animate(u):
        a = math.radians(-5 + 4 * u)
        cam.location = (math.sin(a) * (R - 1.6), 0, -math.cos(a) * (R - 1.6))
        ahead = a + math.radians(38)
        aim(cam, cam.location, (math.sin(ahead) * (R - 1.2), 0, -math.cos(ahead) * (R - 1.2)))
    return animate


def rock(name, loc, r, material, seed=3, smooth=True):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, radius=r, location=loc)
    o = bpy.context.object
    o.name = name
    random.seed(seed)
    for v in o.data.vertices:
        n = v.co.normalized()
        v.co *= 0.85 + 0.2 * (math.sin(n.x * 5 + seed) * math.cos(n.y * 4 + seed) + 1) / 2 + 0.05 * random.random()
    o.scale = (1.3, 1.0, 0.75)
    if smooth:
        bpy.ops.object.shade_smooth()
    o.data.materials.append(material)
    return o


def build_monolith():
    """The excavation: a black 1:4:9 slab on grey regolith, floodlit, Earth hanging in black sky."""
    reset(16)
    bpy.context.scene.render.film_transparent = True
    regolith = mat("reg", (0.34, 0.33, 0.32), 0.95)
    g = ground("ground", 120, regolith, 0.35, 0.8)
    black = mat("mono", (0.003, 0.003, 0.004), 0.08)
    box("monolith", (0, 6, 2.16), (1.92, 0.48, 4.32), black)
    stonem = mat("stone", (0.45, 0.43, 0.4), 0.9)
    rock("rock", (1.3, 1.2, 0.3), 0.42, stonem)
    wood = mat("wood", (0.45, 0.3, 0.16), 0.8)
    for k in range(3):
        box(f"plank{k}", (-1.3 + k * 0.05, 0.9 + k * 0.22, 0.06 + k * 0.05), (1.5, 0.16, 0.06), wood, (0, 0, 10 * k - 8))
    rope = mat("rope", (0.6, 0.52, 0.35), 0.9)
    for z in (0.07, 0.14, 0.21):
        bpy.ops.mesh.primitive_torus_add(major_radius=0.26 - z * 0.2, minor_radius=0.04, location=(-0.1, 0.6, z))
        bpy.context.object.data.materials.append(rope)
    metal = mat("metal", (0.7, 0.7, 0.72), 0.25, 0.9)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.22, depth=0.07, location=(0.45, 0.5, 0.22), rotation=(math.radians(75), 0, 0.3))
    pul = bpy.context.object
    pul.data.materials.append(metal)
    cutter_mod = pul.modifiers.new("bool", "BOOLEAN")
    bpy.ops.mesh.primitive_cube_add(size=0.26, location=(0.56, 0.5, 0.33))
    cutter = bpy.context.object
    cutter.hide_render = True
    cutter_mod.object = cutter
    sphere("earth", (-9, 90, 30), 5, earth_mat())
    sun((70, 0, -150), 5.0, 0.25)
    for sx in (-1, 1):   # dig-site floodlights grazing the slab
        L = bpy.data.objects.new(f"flood{sx}", bpy.data.lights.new(f"flood{sx}", "SPOT"))
        bpy.context.scene.collection.objects.link(L)
        L.data.energy = 3500
        L.data.spot_size = math.radians(40)
        aim(L, (sx * 7, -2, 0.8), (0, 6, 2.6))
    cam = camera((0, -2.2, 0.45), (0, 6, 2.6), lens=20)

    def animate(u):
        cam.location = (0, -2.6 + 1.0 * u, 0.45 + 0.05 * u)
        aim(cam, cam.location, (0, 6, 2.7))
    return animate


def build_dawn():
    """Dawn of Man's tool, tumbling in slow motion against a burning sky (sets up the match cut)."""
    reset(16)
    w = bpy.context.scene.world
    nt = w.node_tree
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    cr = nt.nodes.new("ShaderNodeValToRGB")
    cr.color_ramp.elements[0].color = (1.0, 0.45, 0.12, 1)
    cr.color_ramp.elements[0].position = 0.02
    cr.color_ramp.elements[1].color = (0.05, 0.06, 0.16, 1)
    cr.color_ramp.elements[1].position = 0.45
    nt.links.new(tc.outputs["Generated"], sep.inputs["Vector"])
    nt.links.new(sep.outputs["Z"], cr.inputs["Fac"])
    nt.links.new(cr.outputs["Color"], nt.nodes["Background"].inputs["Color"])
    nt.nodes["Background"].inputs["Strength"].default_value = 1.0
    bpy.context.scene.render.film_transparent = True   # the photographic dawn plate goes behind in 2D
    wood = mat("wood", (0.33, 0.22, 0.13), 0.8)
    tool = box("tool", (0, 9, 3), (3.0, 0.24, 0.16), wood)
    bpy.ops.object.modifier_add(type="BEVEL")
    sun((70, 0, 180), 4.0, 0.25)
    cam = camera((0, 0, 0), (0, 9, 3.0), lens=40)

    def animate(u):
        tool.location = (0, 9, 2.4 + 1.2 * u)
        tool.rotation_euler = (0, math.radians(-40 + 300 * u), math.radians(18))
    return animate


def build_station():
    """A detailed white orbital station drifting above Earth's limb."""
    reset(24)
    bpy.context.scene.render.film_transparent = True
    sphere("earth", (0, 90, -95), 90, earth_mat())
    white = mat("hull", (0.82, 0.82, 0.8), 0.45)
    grey = mat("hull2", (0.45, 0.45, 0.47), 0.5)
    dark = mat("panel", (0.04, 0.04, 0.06), 0.3, 0.6)
    st = bpy.data.objects.new("station", None)
    bpy.context.scene.collection.objects.link(st)
    parts = []

    def add(o, m):
        if not o.data.materials:
            o.data.materials.append(m)
        o.parent = st
        parts.append(o)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.5, depth=6, vertices=48, location=(0, 0, 0), rotation=(0, math.radians(90), 0))
    bpy.ops.object.shade_smooth()
    add(bpy.context.object, white)
    bpy.ops.mesh.primitive_torus_add(major_radius=2.4, minor_radius=0.26, major_segments=96, minor_segments=24,
                                     rotation=(0, math.radians(90), 0))
    bpy.ops.object.shade_smooth()
    add(bpy.context.object, white)
    for k in range(4):
        a = k * math.pi / 2
        bpy.ops.mesh.primitive_cylinder_add(radius=0.08, depth=2.4, location=(0, math.cos(a) * 1.2, math.sin(a) * 1.2),
                                            rotation=(a + math.pi / 2, 0, 0))
        add(bpy.context.object, grey)
    random.seed(7)
    for k in range(120):   # greebles: the miniature makers' kit-bash detail
        x = random.uniform(-2.9, 2.9)
        a = random.uniform(0, 2 * math.pi)
        sz = random.uniform(0.05, 0.18)
        o = box(f"g{k}", (x, 0.5 * math.cos(a), 0.5 * math.sin(a)), (sz * 1.5, sz, sz * 0.6), grey if k % 3 else white,
                (math.degrees(a), 0, 0))
        add(o, grey)
    for k in range(0):
        a = k * 2 * math.pi / 48
        o = box(f"win{k}", (0, 2.4 * math.cos(a) * 1.01, 2.4 * math.sin(a) * 1.01), (0.2, 0.06, 0.06), dark)
        add(o, dark)
    for sx in (-1, 1):
        for j in range(4):
            o = box(f"solar{sx}{j}", (sx * 3.25, -1.35 + j * 0.9, 0), (0.03, 0.82, 1.2), dark)
            add(o, dark)
    sun((25, -35, 60), 6.0, 0.2)
    cam = camera((0, -20, 2.5), (0, 0, 0), lens=45)

    def animate(u):
        st.rotation_euler = (math.radians(10 + 25 * u), 0, math.radians(-25))
        st.location = (-0.8 + 1.6 * u, 0, 0.7)
    return animate


def build_memory():
    """The logic-memory room: deep red, rows of glowing modules in one-point perspective."""
    reset(16)
    red = mat("redwall", (0.05, 0.0, 0.0), 0.5, emit=(1.0, 0.04, 0.02), emit_strength=0.18)
    dark = mat("floor", (0.02, 0.0, 0.0), 0.25)
    box("floor", (0, 8, -1.3), (3, 22, 0.1), dark)
    box("ceil", (0, 8, 1.6), (3, 22, 0.1), dark)
    slab = mat("slab", (0.3, 0.03, 0.03), 0.1, emit=(1.0, 0.2, 0.15), emit_strength=0.45)
    frame = mat("frame", (0.01, 0.0, 0.0), 0.4)
    for sgn in (-1, 1):
        box(f"wall{sgn}", (sgn * 1.55, 8, 0.15), (0.05, 22, 3), red)
        for k in range(14):
            box(f"slab{sgn}{k}", (sgn * 1.25, 1 + k * 1.2, 0.15), (0.45, 0.04, 1.3), slab)
            box(f"frm{sgn}{k}", (sgn * 1.25, 1 + k * 1.2, 0.84), (0.5, 0.06, 0.06), frame)
    cam = camera((0, -3, 0.15), (0, 20, 0.15), lens=22)

    def animate(u):
        cam.location = (0, -3 + 5 * u, 0.15)
        aim(cam, cam.location, (0, 20, 0.15))
    return animate


BUILDERS = {"alignment": build_alignment, "centrifuge": build_centrifuge, "monolith": build_monolith,
            "dawn": build_dawn, "station": build_station, "memory": build_memory}


def render_frame(path):
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
