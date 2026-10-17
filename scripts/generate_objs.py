"""
Standalone OBJ generator for Mustang's jewelry set.
No Blender required — produces geometry-equivalent meshes.
Run: python3 scripts/generate_objs.py
"""

import math, os

OUT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mustang_set")
os.makedirs(OUT, exist_ok=True)

def uv_sphere(cx, cy, cz, r, segs=8, rings=6):
    verts, faces = [], []
    for ri in range(rings + 1):
        phi = math.pi * ri / rings
        for si in range(segs):
            theta = 2 * math.pi * si / segs
            verts.append((
                cx + r * math.sin(phi) * math.cos(theta),
                cy + r * math.sin(phi) * math.sin(theta),
                cz + r * math.cos(phi)
            ))
    for ri in range(rings):
        for si in range(segs):
            a = ri * segs + si
            b = ri * segs + (si + 1) % segs
            c = (ri + 1) * segs + (si + 1) % segs
            d = (ri + 1) * segs + si
            faces.append((a, b, c, d))
    return verts, faces

def torus(cx, cy, cz, maj_r, min_r, maj_segs=24, min_segs=8, rot_z=0.0):
    verts, faces = [], []
    for mi in range(maj_segs):
        angle_maj = 2 * math.pi * mi / maj_segs + rot_z
        for ni in range(min_segs):
            angle_min = 2 * math.pi * ni / min_segs
            x = (maj_r + min_r * math.cos(angle_min)) * math.cos(angle_maj)
            y = (maj_r + min_r * math.cos(angle_min)) * math.sin(angle_maj)
            z = min_r * math.sin(angle_min)
            verts.append((cx + x, cy + y, cz + z))
    for mi in range(maj_segs):
        for ni in range(min_segs):
            a = mi * min_segs + ni
            b = mi * min_segs + (ni + 1) % min_segs
            c = ((mi + 1) % maj_segs) * min_segs + (ni + 1) % min_segs
            d = ((mi + 1) % maj_segs) * min_segs + ni
            faces.append((a, b, c, d))
    return verts, faces

def cylinder(cx, cy, cz, r, h, verts_n=8):
    verts, faces = [], []
    verts.append((cx, cy, cz)); bc = 0
    for i in range(verts_n):
        a = 2 * math.pi * i / verts_n
        verts.append((cx + r * math.cos(a), cy + r * math.sin(a), cz))
    tc = len(verts); verts.append((cx, cy, cz + h))
    for i in range(verts_n):
        a = 2 * math.pi * i / verts_n
        verts.append((cx + r * math.cos(a), cy + r * math.sin(a), cz + h))
    for i in range(verts_n):
        b = 1 + i; t = tc + 1 + i
        nb = 1 + (i + 1) % verts_n; nt = tc + 1 + (i + 1) % verts_n
        faces.append((b, nb, nt, t))
        faces.append((bc, 1 + (i + 1) % verts_n, 1 + i))
        faces.append((tc, tc + 1 + i, tc + 1 + (i + 1) % verts_n))
    return verts, faces

def cube(cx, cy, cz, sx, sy, sz):
    hx, hy, hz = sx/2, sy/2, sz/2
    v = [
        (cx-hx, cy-hy, cz-hz), (cx+hx, cy-hy, cz-hz),
        (cx+hx, cy+hy, cz-hz), (cx-hx, cy+hy, cz-hz),
        (cx-hx, cy-hy, cz+hz), (cx+hx, cy-hy, cz+hz),
        (cx+hx, cy+hy, cz+hz), (cx-hx, cy+hy, cz+hz),
    ]
    f = [(0,1,2,3),(4,7,6,5),(0,4,5,1),(2,6,7,3),(0,3,7,4),(1,5,6,2)]
    return v, f

MTL = '''newmtl rg_gold
Ns 250.000000
Ka 1.000000 1.000000 1.000000
Kd 0.796000 0.498000 0.388000
Ks 0.980000 0.960000 0.900000
Ke 0.000000 0.000000 0.000000
Ni 1.450000
d 1.000000
illum 2
newmtl pink_saph
Ns 500.000000
Ka 1.000000 1.000000 1.000000
Kd 0.918000 0.412000 0.631000
Ks 0.990000 0.990000 0.990000
Ke 0.000000 0.000000 0.000000
Ni 1.770000
d 1.000000
illum 2'''

class ObjWriter:
    def __init__(self):
        self.verts = []
        self.faces = []

    def add(self, verts, faces, mat):
        base = len(self.verts)
        self.verts.extend(verts)
        for f in faces:
            self.faces.append((mat, tuple(base + vi + 1 for vi in f)))

    def tri_count(self):
        return sum(len(f) - 2 for _, f in self.faces)

    def write(self, path):
        base = os.path.splitext(os.path.basename(path))[0]
        with open(path, 'w') as f:
            f.write(f'mtllib {base}.mtl\n')
            for v in self.verts:
                f.write(f'v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n')
            cur_mat = None
            for mat, face in self.faces:
                if mat != cur_mat:
                    f.write(f'usemtl {mat}\n')
                    cur_mat = mat
                f.write('f ' + ' '.join(str(vi) for vi in face) + '\n')
        with open(path.replace('.obj', '.mtl'), 'w') as f:
            f.write(MTL)


def build_necklace():
    w = ObjWriter()
    CR = 0.23
    for i in range(60):
        a = 2 * math.pi * i / 60
        rot = a + (0 if i % 2 == 0 else math.pi / 2)
        v, f = torus(CR*math.cos(a), CR*math.sin(a), 0, 0.012, 0.004, maj_segs=12, min_segs=8, rot_z=rot)
        w.add(v, f, 'rg_gold')
    for sx, sy in [(0,0),(0.008,0.004),(-0.008,0.004),(0.004,-0.006),(-0.004,-0.006)]:
        v, f = uv_sphere(sx, sy - CR, -0.016, 0.005, segs=8, rings=6)
        w.add(v, f, 'pink_saph')
    return w


def build_bracelet_stack():
    w = ObjWriter()
    WR = 0.085
    v, f = torus(0, 0, 0.02, WR, 0.005, maj_segs=48, min_segs=8)
    w.add(v, f, 'rg_gold')
    for i in range(36):
        a = 2 * math.pi * i / 36
        v, f = uv_sphere(WR*math.cos(a), WR*math.sin(a), 0.026, 0.003, segs=6, rings=4)
        w.add(v, f, 'pink_saph')
    TR = WR + 0.004
    for i in range(30):
        a = 2 * math.pi * i / 30
        v, f = uv_sphere(TR*math.cos(a), TR*math.sin(a), 0, 0.004, segs=6, rings=4)
        w.add(v, f, 'pink_saph')
        v2, f2 = torus(TR*math.cos(a), TR*math.sin(a), 0, 0.004, 0.0012, maj_segs=8, min_segs=4)
        w.add(v2, f2, 'rg_gold')
    v, f = torus(0, 0, 0, TR, 0.0018, maj_segs=60, min_segs=6)
    w.add(v, f, 'rg_gold')
    v, f = torus(0, 0, -0.02, WR + 0.008, 0.007, maj_segs=48, min_segs=12)
    w.add(v, f, 'rg_gold')
    return w


def build_earrings():
    w = ObjWriter()
    for xoff in (-0.04, 0.04):
        v, f = cylinder(xoff, 0, -0.006, 0.0015, 0.012, verts_n=8)
        w.add(v, f, 'rg_gold')
        v, f = uv_sphere(xoff, 0, 0, 0.007, segs=12, rings=8)
        w.add(v, f, 'rg_gold')
        for si in range(6):
            a = 2 * math.pi * si / 6
            v, f = uv_sphere(xoff + 0.0045*math.cos(a), 0.0045*math.sin(a), 0.004, 0.0018, segs=6, rings=4)
            w.add(v, f, 'pink_saph')
        v, f = uv_sphere(xoff, 0, 0.006, 0.002, segs=6, rings=4)
        w.add(v, f, 'pink_saph')
        v, f = torus(xoff, 0, -0.009, 0.003, 0.0008, maj_segs=8, min_segs=4)
        w.add(v, f, 'rg_gold')
        sv, sf = uv_sphere(xoff, 0, -0.024, 0.006, segs=10, rings=8)
        sv = [(x, y, z * 1.6) for x, y, z in sv]
        w.add(sv, sf, 'pink_saph')
    return w


def build_ring():
    w = ObjWriter()
    FR = 0.0085
    v, f = torus(0, 0, 0, FR, 0.003, maj_segs=48, min_segs=10)
    w.add(v, f, 'rg_gold')
    for i in range(18):
        a = math.pi * i / 17 - math.pi / 2
        v, f = uv_sphere(FR*math.cos(a), FR*math.sin(a), 0.0036, 0.0016, segs=6, rings=4)
        w.add(v, f, 'pink_saph')
    v, f = cube(0, -FR - 0.005, 0.005, 0.010, 0.006, 0.0035)
    w.add(v, f, 'rg_gold')
    sv, sf = uv_sphere(0, -FR - 0.005, 0.009, 0.006, segs=12, rings=8)
    sv = [(x, y * 0.7, z * 0.5) for x, y, z in sv]
    w.add(sv, sf, 'pink_saph')
    return w


if __name__ == '__main__':
    for name, fn in [('necklace', build_necklace), ('bracelet_stack', build_bracelet_stack),
                     ('earrings', build_earrings), ('ring', build_ring)]:
        w = fn()
        w.write(os.path.join(OUT, f'{name}.obj'))
        print(f'{name}: {w.tri_count()} tris')
