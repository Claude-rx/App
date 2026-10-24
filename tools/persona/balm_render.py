"""Product renders of the SKINOFAB PDRN Plumping Balm: a matte black twist-up stick in the foundation's packaging system.

usage: <python with bpy> balm_render.py <out_dir> [shot ...] [--samples 160] [--size 1600]
shots: front (capped, facing), card (capped + uncapped), open (uncapped, cap lying), bullet (macro of the balm),
       duo (2 sticks), trio (3 sticks), tilt (one stick at 30 degrees, for the how-to), jar (an unbranded white cream
       jar, open, for the stick-vs-jar comparison)

The packaging follows brand/adaptive-peptide-foundation/product-sheet-overview.webp: soft-touch matte black, the white
SKINOFAB wordmark vertical (S at the top), the product name in small spaced Montserrat caps under it, the net weight,
nothing else on the front; a cool light-grey studio sweep. Size: 22.6 mm diameter x 100 mm capped (a 10 g stick).
The label is printed through the shader from object coordinates (no UV seam), from label_texture(); Blender's bpy
module renders it on the CPU (pip install bpy==5.2.3).
"""
import math, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
LOGO = ROOT / 'brand' / 'adaptive-peptide-foundation' / '00-logo.png'
FONT = Path(__file__).resolve().parent / 'assets' / 'fonts' / 'Montserrat-VF.ttf'
args = sys.argv[1:]
def opt(name, default):
    if name in args:
        i = args.index(name); v = args[i + 1]; del args[i:i + 2]; return type(default)(v)
    return default
SAMPLES, SIZE = opt('--samples', 160), opt('--size', 1600)
OUT = Path(args[0]); OUT.mkdir(parents=True, exist_ok=True)
SHOTS = args[1:] or ['front', 'card', 'open', 'bullet', 'duo', 'trio', 'tilt']

# geometry, in cm
R, R_CAP = 1.13, 1.16            # body and cap radius (22.6 mm stick)
Z_BASE, Z_BODY0, Z_BODY1 = 0.62, 0.66, 6.80   # twist ring 0..0.62, body 0.66..6.80
Z_CAP1 = 10.0                    # capped height 100 mm
LABEL_H = Z_BODY1 - Z_BODY0

# as on the foundation: the name in two lines, the key actives smaller on their own line, then the weight
LABEL = [('PLUMPING', 'Medium', 1.0), ('BALM', 'Medium', 1.0), (None, None, 1.0),
         ('PDRN · VOLUFILINE', 'SemiBold', 0.84), (None, None, 1.5), ('10 g / 0.35 oz', 'Regular', 0.8)]


def label_texture(path):
    """The body's print, unrolled: width = circumference, the front (facing -Y) at a quarter of the width."""
    W = 4096
    H = round(W * LABEL_H / (2 * math.pi * R))
    tex = Image.new('L', (W, H), 0)
    px_cm = H / LABEL_H
    # the wordmark, vertical, S at the top: 3.5 cm long from 0.5 cm under the shoulder
    logo = np.asarray(Image.open(LOGO).convert('L')).astype(np.float32)
    ink = np.clip((189 - logo) / 150, 0, 1)
    ys, xs = np.where(ink > 0.2)
    ink = ink[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
    word = Image.fromarray((ink * 255).astype(np.uint8)).rotate(-90, expand=True)   # reads top to bottom
    L = round(3.45 * px_cm)
    word = word.resize((round(word.width * L / word.height), L), Image.LANCZOS)
    cx = W // 4
    top = round(0.42 * px_cm)
    tex.paste(word, (cx - word.width // 2, top), word)
    # the name and weight, small spaced caps under it
    d = ImageDraw.Draw(tex)
    y = top + L + round(0.38 * px_cm)
    cap = 0.13 * px_cm                       # cap height of the name lines (1.3 mm)
    for text, weight, scale in LABEL:
        if text is None: y += round(cap * scale); continue
        f = ImageFont.truetype(str(FONT), 40); f.set_variation_by_name(weight)
        # size the font so its cap height is cap * scale
        bb = f.getbbox('H'); size = 40 * cap * scale / (bb[3] - bb[1])
        f = ImageFont.truetype(str(FONT), round(size)); f.set_variation_by_name(weight)
        track = size * 0.16
        widths = [f.getlength(ch) for ch in text]
        total = sum(widths) + track * (len(text) - 1)
        x = cx - total / 2
        for ch, w in zip(text, widths):
            d.text((x, y), ch, font=f, fill=255, anchor='ls'); x += w + track
        y += round(cap * scale * 1.85)
    tex.save(path)                               # Blender samples v = 0 at the image's bottom row: no flip
    return path


import bpy, bmesh
from mathutils import Vector


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = 'NONE'
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = SAMPLES
    sc.cycles.use_denoising = True
    sc.render.resolution_x = sc.render.resolution_y = SIZE
    sc.render.film_transparent = False
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Medium High Contrast'
    sc.render.image_settings.file_format = 'PNG'
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs[0].default_value = (0.55, 0.57, 0.62, 1)
    w.node_tree.nodes['Background'].inputs[1].default_value = 0.25
    return sc


def mat_black(name='black', rough=0.48):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.012, 0.012, 0.013, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Specular IOR Level'].default_value = 0.55
    return m


def mat_label(tex_path):
    """Matte black with the white print, mapped by angle and height from object coordinates."""
    m = mat_black('label'); nt = m.node_tree; N, Lk = nt.nodes, nt.links
    b = N['Principled BSDF']
    tc = N.new('ShaderNodeTexCoord'); sep = N.new('ShaderNodeSeparateXYZ'); Lk.new(tc.outputs['Object'], sep.inputs[0])
    at = N.new('ShaderNodeMath'); at.operation = 'ARCTAN2'; Lk.new(sep.outputs['Y'], at.inputs[0]); Lk.new(sep.outputs['X'], at.inputs[1])
    u = N.new('ShaderNodeMath'); u.operation = 'MULTIPLY_ADD'; u.inputs[1].default_value = 1 / (2 * math.pi); u.inputs[2].default_value = 0.5
    Lk.new(at.outputs[0], u.inputs[0])
    v = N.new('ShaderNodeMath'); v.operation = 'MULTIPLY_ADD'; v.inputs[1].default_value = 1 / LABEL_H; v.inputs[2].default_value = 0.5   # local z: the body is centred on its origin
    Lk.new(sep.outputs['Z'], v.inputs[0])
    comb = N.new('ShaderNodeCombineXYZ'); Lk.new(u.outputs[0], comb.inputs[0]); Lk.new(v.outputs[0], comb.inputs[1])
    img = N.new('ShaderNodeTexImage'); img.image = bpy.data.images.load(str(tex_path)); img.extension = 'CLIP'
    img.image.colorspace_settings.name = 'Non-Color'; img.interpolation = 'Cubic'
    Lk.new(comb.outputs[0], img.inputs[0])
    mix = N.new('ShaderNodeMix'); mix.data_type = 'RGBA'
    mix.inputs['A'].default_value = (0.012, 0.012, 0.013, 1); mix.inputs['B'].default_value = (0.86, 0.86, 0.85, 1)
    Lk.new(img.outputs['Color'], mix.inputs['Factor']); Lk.new(mix.outputs['Result'], b.inputs['Base Color'])
    rough = N.new('ShaderNodeMapRange'); rough.inputs['To Min'].default_value = 0.48; rough.inputs['To Max'].default_value = 0.30
    Lk.new(img.outputs['Color'], rough.inputs['Value']); Lk.new(rough.outputs['Result'], b.inputs['Roughness'])
    return m


def mat_balm():
    m = bpy.data.materials.new('balm'); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.86, 0.53, 0.42, 1)    # warm nude, translucent
    b.inputs['Roughness'].default_value = 0.22
    b.inputs['Subsurface Weight'].default_value = 0.6
    b.inputs['Subsurface Radius'].default_value = (0.5, 0.3, 0.25)
    b.inputs['Subsurface Scale'].default_value = 0.15
    b.inputs['Coat Weight'].default_value = 0.35
    b.inputs['Coat Roughness'].default_value = 0.12
    return m


def mat_backdrop():
    m = bpy.data.materials.new('sweep'); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (0.80, 0.81, 0.85, 1)
    b.inputs['Roughness'].default_value = 0.92
    return m


def cylinder(name, r, z0, z1, mat, bevel=0.05, verts=192):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=z1 - z0, location=(0, 0, (z0 + z1) / 2))
    o = bpy.context.active_object; o.name = name
    if bevel:
        md = o.modifiers.new('bevel', 'BEVEL'); md.width = bevel; md.segments = 5; md.limit_method = 'ANGLE'
    bpy.ops.object.shade_smooth()
    o.data.materials.append(mat)
    return o


def sweep():
    """A light-grey studio sweep: floor, a 30 cm curve, then the wall."""
    prof = [(y, 0.0) for y in np.linspace(-90, 15, 22)]
    for a in np.linspace(0, math.pi / 2, 24)[1:]:
        prof.append((15 + 30 * math.sin(a), 30 - 30 * math.cos(a)))
    prof += [(45, z) for z in np.linspace(40, 140, 6)]
    me = bpy.data.meshes.new('sweep'); bm = bmesh.new()
    rows = []
    for x in (-120, 120):
        rows.append([bm.verts.new((x, y, z)) for y, z in prof])
    for i in range(len(prof) - 1):
        bm.faces.new((rows[0][i], rows[0][i + 1], rows[1][i + 1], rows[1][i]))
    bm.to_mesh(me); o = bpy.data.objects.new('sweep', me); bpy.context.collection.objects.link(o)
    for p in me.polygons: p.use_smooth = True
    o.data.materials.append(mat_backdrop())
    return o


def stick(label_mat, black, balm, capped=True, at=(0, 0, 0), rot=0.0, tilt=0.0):
    """One stick, its front facing -Y before rot (degrees about Z); tilt leans it back (degrees about X)."""
    parts = [cylinder('ring', R, 0, Z_BASE, black, 0.04),
             cylinder('body', R, Z_BODY0, Z_BODY1, label_mat, 0.035)]
    if capped:
        parts.append(cylinder('cap', R_CAP, Z_BODY1 + 0.04, Z_CAP1, black, 0.14))
    else:
        parts.append(cylinder('collar', R * 0.93, Z_BODY1 - 0.05, Z_BODY1 + 0.32, mat_black('collar', 0.3), 0.03))
        b = cylinder('bullet', R * 0.84, Z_BODY1, Z_BODY1 + 1.75, balm, 0.0, 128)
        # the slanted, rounded top of a balm bullet
        bpy.ops.mesh.primitive_cube_add(size=4, location=(0, 0, Z_BODY1 + 1.75 + 2 - 0.55))
        cut = bpy.context.active_object; cut.rotation_euler = (math.radians(24), 0, 0); cut.hide_render = True; cut.display_type = 'WIRE'
        md = b.modifiers.new('cut', 'BOOLEAN'); md.object = cut; md.operation = 'DIFFERENCE'
        bv = b.modifiers.new('round', 'BEVEL'); bv.width = 0.22; bv.segments = 8; bv.limit_method = 'ANGLE'
        parts += [b, cut]                                   # the cutter moves with its stick
    root = bpy.data.objects.new('stick', None); bpy.context.collection.objects.link(root)
    for p in parts: p.parent = root
    root.location = at; root.rotation_euler = (math.radians(tilt), 0, math.radians(rot))
    return root


def cap_lying(black, at, rot):
    c = cylinder('cap-lying', R_CAP, 0, Z_CAP1 - Z_BODY1 - 0.04, black, 0.14)
    c.rotation_euler = (math.radians(90), 0, math.radians(rot))
    c.location = (at[0], at[1], R_CAP)
    return c


def jar():
    """A generic, unbranded white cream jar with its lid leaning on it, and the cream inside."""
    white = bpy.data.materials.new('white'); white.use_nodes = True
    w = white.node_tree.nodes['Principled BSDF']
    w.inputs['Base Color'].default_value = (0.86, 0.86, 0.87, 1); w.inputs['Roughness'].default_value = 0.28
    cream = bpy.data.materials.new('cream'); cream.use_nodes = True
    c = cream.node_tree.nodes['Principled BSDF']
    c.inputs['Base Color'].default_value = (0.93, 0.91, 0.88, 1); c.inputs['Roughness'].default_value = 0.35
    c.inputs['Subsurface Weight'].default_value = 0.3
    body = cylinder('jar', 3.4, 0, 4.2, white, 0.0)
    hollow = cylinder('hollow', 3.08, 0.5, 5.0, white, 0.0); hollow.hide_render = True; hollow.display_type = 'WIRE'
    md = body.modifiers.new('hollow', 'BOOLEAN'); md.object = hollow; md.operation = 'DIFFERENCE'
    bv = body.modifiers.new('round', 'BEVEL'); bv.width = 0.12; bv.segments = 5; bv.limit_method = 'ANGLE'
    inner = cylinder('cream', 3.06, 0.5, 3.75, cream, 0.35)
    lid = cylinder('lid', 3.55, 0, 1.5, white, 0.3)
    lid.rotation_euler = (math.radians(74), 0, math.radians(-25)); lid.location = (5.6, 3.2, 3.4)
    return body


def lights(target=(0, 0, 5)):
    def area(name, loc, size, energy, shape='RECTANGLE', sy=None):
        l = bpy.data.lights.new(name, 'AREA'); l.energy = energy * 0.42; l.shape = shape; l.size = size   # 0.42: the 70-degree spread concentrates it
        if sy: l.size_y = sy
        l.spread = math.radians(70)                          # aimed at the product, not raking the sweep
        o = bpy.data.objects.new(name, l); bpy.context.collection.objects.link(o); o.location = loc
        d = Vector(target) - Vector(loc); o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
        return o
    area('key', (-26, -38, 46), 44, 9000)          # high and broad: no streak across the sweep
    area('strip-left', (-9, -7, 6), 2.2, 2400, 'RECTANGLE', 22)     # the soft vertical highlight on the black
    area('fill', (36, -26, 16), 34, 2600)
    area('top', (0, 4, 48), 40, 3600)
    area('rim', (8, 30, 14), 10, 2200)


def camera(loc, target, lens=100):
    c = bpy.data.cameras.new('cam'); c.lens = lens; c.dof.use_dof = False
    o = bpy.data.objects.new('cam', c); bpy.context.collection.objects.link(o); o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = o
    return o


def render(name):
    p = OUT / f'{name}.png'
    bpy.context.scene.render.filepath = str(p)
    bpy.ops.render.render(write_still=True)
    print('rendered', p)


tex = label_texture(OUT / 'label-texture.png')
for shot in SHOTS:
    sc = reset(); sweep(); black = mat_black(); lab = mat_label(tex); balm = mat_balm()
    if shot == 'front':
        stick(lab, black, balm); lights(); camera((0, -46, 6.0), (0, 0, 5.0), 100)
    elif shot == 'card':
        stick(lab, black, balm, True, (-1.55, 0.6, 0), 8); stick(lab, black, balm, False, (1.55, -0.4, 0), -6)
        lights(); camera((0, -48, 6.6), (0, 0, 4.9), 95)
    elif shot == 'open':
        stick(lab, black, balm, False, (-0.6, 0, 0), 4); cap_lying(black, (2.6, -2.2, 0), 60)
        lights(); camera((3, -46, 9.0), (0.6, -0.6, 4.0), 95)
    elif shot == 'bullet':
        stick(lab, black, balm, False, (0, 0, 0), 0); lights((0, 0, 7.6))
        sc.render.resolution_y = round(SIZE * 1.0); camera((0, -24, 11.2), (0, 0, 7.4), 100)
    elif shot == 'duo':
        stick(lab, black, balm, True, (-1.5, 0, 0), 6); stick(lab, black, balm, True, (1.5, 0, 0), -6)
        lights(); camera((0, -50, 6.4), (0, 0, 5.0), 95)
    elif shot == 'trio':
        stick(lab, black, balm, True, (-2.9, 0.8, 0), 10); stick(lab, black, balm, True, (0, -0.6, 0), 0)
        stick(lab, black, balm, True, (2.9, 0.8, 0), -10)
        lights(); camera((0, -54, 6.8), (0, 0, 4.9), 90)
    elif shot == 'tilt':
        stick(lab, black, balm, False, (0, 0, 1.2), -20, 0).rotation_euler = (0, math.radians(-32), math.radians(-20))
        lights(); camera((0, -46, 6.0), (0.5, 0, 5.0), 95)
    elif shot == 'jar':
        jar(); lights((0, 0, 2.5)); camera((0, -38, 25.0), (1.4, 0.4, 2.2), 85)
    render(shot)
