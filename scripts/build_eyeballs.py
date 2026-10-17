"""
BC Eyeball Build — 5 colorways
Each eye: sclera + iris + pupil + cornea highlight
Exports: eyeballs/{colorway}_eye.obj + .mtl

Colorways:
  brown      — Buda
  baby_blue  — Girls (Mustang etc.)
  dark_brown — near-black
  green      — emerald
  hazel      — amber/honey
"""

import math, os

BASE = os.path.dirname(os.path.dirname(__file__))
OUT  = os.path.join(BASE, "eyeballs")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------------------
# Colorway definitions
# ---------------------------------------------------------------------------
COLORWAYS = {
    "brown": {
        "iris":    (0.38, 0.22, 0.08),
        "pupil":   (0.04, 0.02, 0.01),
        "label":   "Buda brown",
    },
    "baby_blue": {
        "iris":    (0.53, 0.78, 0.92),
        "pupil":   (0.05, 0.05, 0.10),
        "label":   "Girls baby blue",
    },
    "dark_brown": {
        "iris":    (0.18, 0.09, 0.03),
        "pupil":   (0.03, 0.01, 0.01),
        "label":   "Dark brown / near-black",
    },
    "green": {
        "iris":    (0.20, 0.55, 0.25),
        "pupil":   (0.04, 0.07, 0.04),
        "label":   "Emerald green",
    },
    "hazel": {
        "iris":    (0.58, 0.42, 0.12),
        "pupil":   (0.05, 0.04, 0.02),
        "label":   "Hazel / amber",
    },
}

SCLERA_COLOR = (0.96, 0.94, 0.90)   # slightly warm white
CORNEA_COLOR = (0.95, 0.98, 1.00)   # near-white with blue tint
EYE_RADIUS   = 0.012                 # 12 mm — standard FiveM eye prop scale

# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def uv_sphere(cx, cy, cz, r, segs=16, rings=12):
    verts, uvs, faces = [], [], []
    for ri in range(rings + 1):
        phi = math.pi * ri / rings
        v   = ri / rings
        for si in range(segs):
            theta = 2 * math.pi * si / segs
            u     = si / segs
            x = cx + r * math.sin(phi) * math.cos(theta)
            y = cy + r * math.sin(phi) * math.sin(theta)
            z = cz + r * math.cos(phi)
            verts.append((x, y, z))
            uvs.append((u, 1.0 - v))
    for ri in range(rings):
        for si in range(segs):
            a = ri * segs + si
            b = ri * segs + (si + 1) % segs
            c = (ri + 1) * segs + (si + 1) % segs
            d = (ri + 1) * segs + si
            faces.append((a, b, c, d))
    return verts, uvs, faces


def disc(cx, cy, cz, r, segs=24, depth=0.0):
    """Flat disc (iris/pupil) facing +Z, slightly recessed by depth."""
    verts, uvs, faces = [], [], []
    # centre
    verts.append((cx, cy, cz + depth))
    uvs.append((0.5, 0.5))
    for i in range(segs):
        a = 2 * math.pi * i / segs
        verts.append((cx + r * math.cos(a), cy + r * math.sin(a), cz + depth))
        uvs.append((0.5 + 0.5 * math.cos(a), 0.5 + 0.5 * math.sin(a)))
    for i in range(segs):
        faces.append((0, i + 1, (i + 1) % segs + 1))
    return verts, uvs, faces


def cap_segment(cx, cy, cz, r, phi_start, phi_end, segs=16, rings=6):
    """Partial sphere cap — used for cornea dome."""
    verts, uvs, faces = [], [], []
    for ri in range(rings + 1):
        phi = phi_start + (phi_end - phi_start) * ri / rings
        for si in range(segs):
            theta = 2 * math.pi * si / segs
            x = cx + r * math.sin(phi) * math.cos(theta)
            y = cy + r * math.sin(phi) * math.sin(theta)
            z = cz + r * math.cos(phi)
            verts.append((x, y, z))
            uvs.append((si / segs, ri / rings))
    for ri in range(rings):
        for si in range(segs):
            a = ri * segs + si
            b = ri * segs + (si + 1) % segs
            c = (ri + 1) * segs + (si + 1) % segs
            d = (ri + 1) * segs + si
            faces.append((a, b, c, d))
    return verts, uvs, faces


# ---------------------------------------------------------------------------
# OBJ writer
# ---------------------------------------------------------------------------

class ObjWriter:
    def __init__(self):
        self.verts = []
        self.uvs   = []
        self.faces = []   # (mat, [(vi, uvi), ...])

    def add(self, verts, uvs, faces, mat):
        vb = len(self.verts)
        ub = len(self.uvs)
        self.verts.extend(verts)
        self.uvs.extend(uvs)
        for f in faces:
            self.faces.append((mat, tuple((vb + vi + 1, ub + vi + 1) for vi in f)))

    def tri_count(self):
        return sum(len(f) - 2 for _, f in self.faces)

    def write(self, path, mtl_content):
        base = os.path.splitext(os.path.basename(path))[0]
        with open(path, "w") as fh:
            fh.write(f"mtllib {base}.mtl\n")
            for v in self.verts:
                fh.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
            for u in self.uvs:
                fh.write(f"vt {u[0]:.6f} {u[1]:.6f}\n")
            cur = None
            for mat, face in self.faces:
                if mat != cur:
                    fh.write(f"usemtl {mat}\n")
                    cur = mat
                fh.write("f " + " ".join(f"{vi}/{ui}" for vi, ui in face) + "\n")
        with open(path.replace(".obj", ".mtl"), "w") as fh:
            fh.write(mtl_content)


def make_mtl(iris_rgb, pupil_rgb):
    def mat(name, kd, ks=(0.1, 0.1, 0.1), ns=10, ni=1.5):
        r, g, b = kd
        sr, sg, sb = ks
        return (f"newmtl {name}\n"
                f"Ns {ns:.1f}\nKa 0.1 0.1 0.1\n"
                f"Kd {r:.3f} {g:.3f} {b:.3f}\n"
                f"Ks {sr:.3f} {sg:.3f} {sb:.3f}\n"
                f"Ke 0.0 0.0 0.0\nNi {ni:.2f}\nd 1.0\nillum 2\n")

    return (
        mat("sclera",  SCLERA_COLOR, ks=(0.3, 0.3, 0.3), ns=80,  ni=1.40) + "\n" +
        mat("iris",    iris_rgb,     ks=(0.4, 0.4, 0.4), ns=200, ni=1.45) + "\n" +
        mat("pupil",   pupil_rgb,    ks=(0.05,0.05,0.05),ns=500, ni=1.50) + "\n" +
        mat("cornea",  CORNEA_COLOR, ks=(0.9, 0.9, 0.9), ns=900, ni=1.37)
    )


# ---------------------------------------------------------------------------
# Build one eye
# ---------------------------------------------------------------------------

def build_eye(colorway_key):
    c  = COLORWAYS[colorway_key]
    w  = ObjWriter()
    R  = EYE_RADIUS

    # Sclera — full sphere
    v, u, f = uv_sphere(0, 0, 0, R, segs=16, rings=12)
    w.add(v, u, f, "sclera")

    # Iris disc — sits on front face of sclera (z = R * sin(phi_iris))
    IRIS_R  = R * 0.42        # iris fills ~42% of eye front
    IRIS_Z  = R * 0.88        # set slightly inside sclera surface
    v, u, f = disc(0, 0, IRIS_Z, IRIS_R, segs=24, depth=0.0)
    w.add(v, u, f, "iris")

    # Pupil — smaller disc on top of iris
    PUPIL_R = IRIS_R * 0.42
    v, u, f = disc(0, 0, IRIS_Z + 0.0001, PUPIL_R, segs=20, depth=0.0)
    w.add(v, u, f, "pupil")

    # Cornea cap — transparent dome over front
    v, u, f = cap_segment(0, 0, 0, R * 1.01, 0, math.pi * 0.28, segs=16, rings=5)
    w.add(v, u, f, "cornea")

    return w, make_mtl(c["iris"], c["pupil"])


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

counts = {}
for key, data in COLORWAYS.items():
    w, mtl = build_eye(key)
    path = os.path.join(OUT, f"{key}_eye.obj")
    w.write(path, mtl)
    counts[key] = w.tri_count()
    print(f"  {key}_eye.obj  {w.tri_count()} tris  — {data['label']}")

print(f"\nTotal colorways: {len(counts)}  |  avg tris: {sum(counts.values())//len(counts)}")
print("Done.")
