"""
BC Eyeball Build — Crimson Gaze series
Anatomically correct eyeball: convex iris disc, clear cornea dome.
Uses Meshy AI Crimson Gaze texture maps as reference.

Geometry (per eye):
  sclera   — UV sphere, full eye globe
  iris     — CONVEX cap segment (not a flat disc, not concave)
  pupil    — flat disc inset on iris centre
  cornea   — large clear convex dome over entire front face

Outputs: eyeballs/crimson_gaze_{colorway}.obj + .mtl
"""

import math, os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT  = os.path.join(BASE, "eyeballs")
os.makedirs(OUT, exist_ok=True)

# Texture maps from Meshy AI Crimson Gaze export
TEXTURES = {
    "diffuse":      "crimson_gaze_diffuse.png",
    "normal":       "crimson_gaze_normal.png",
    "roughness":    "crimson_gaze_roughness.png",
    "displacement": "crimson_gaze_displacement.png",
}

COLORWAYS = {
    "brown": {
        "iris":   (0.38, 0.22, 0.08),
        "pupil":  (0.04, 0.02, 0.01),
        "label":  "Buda brown",
    },
    "baby_blue": {
        "iris":   (0.53, 0.78, 0.92),
        "pupil":  (0.05, 0.05, 0.10),
        "label":  "Girls baby blue",
    },
    "dark_brown": {
        "iris":   (0.18, 0.09, 0.03),
        "pupil":  (0.03, 0.01, 0.01),
        "label":  "Dark brown / near-black",
    },
    "green": {
        "iris":   (0.20, 0.55, 0.25),
        "pupil":  (0.04, 0.07, 0.04),
        "label":  "Emerald green",
    },
    "hazel": {
        "iris":   (0.58, 0.42, 0.12),
        "pupil":  (0.05, 0.04, 0.02),
        "label":  "Hazel / amber",
    },
}

SCLERA_COLOR = (0.96, 0.94, 0.90)
CORNEA_COLOR = (0.98, 0.99, 1.00)  # near-white, very slight blue
EYE_R = 0.012                        # 12 mm globe radius

# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

def uv_sphere(cx, cy, cz, r, segs=20, rings=14):
    """Full UV sphere."""
    verts, uvs, faces = [], [], []
    for ri in range(rings + 1):
        phi = math.pi * ri / rings
        v   = ri / rings
        for si in range(segs):
            theta = 2 * math.pi * si / segs
            u     = si / segs
            verts.append((
                cx + r * math.sin(phi) * math.cos(theta),
                cy + r * math.sin(phi) * math.sin(theta),
                cz + r * math.cos(phi),
            ))
            uvs.append((u, 1.0 - v))
    for ri in range(rings):
        for si in range(segs):
            a = ri * segs + si
            b = ri * segs + (si + 1) % segs
            c = (ri + 1) * segs + (si + 1) % segs
            d = (ri + 1) * segs + si
            faces.append((a, b, c, d))
    return verts, uvs, faces


def convex_cap(cx, cy, cz, r, phi_end, segs=24, rings=8):
    """
    Convex spherical cap from pole (phi=0) down to phi_end.
    phi=0 is the +Z pole (front of eye).
    Results in a dome that bulges OUTWARD — correct for iris and cornea.
    """
    verts, uvs, faces = [], [], []
    for ri in range(rings + 1):
        phi = phi_end * ri / rings
        sp, cp = math.sin(phi), math.cos(phi)
        for si in range(segs):
            theta = 2 * math.pi * si / segs
            verts.append((
                cx + r * sp * math.cos(theta),
                cy + r * sp * math.sin(theta),
                cz + r * cp,
            ))
            uvs.append((si / segs, ri / rings))
    for ri in range(rings):
        for si in range(segs):
            a = ri * segs + si
            b = ri * segs + (si + 1) % segs
            c = (ri + 1) * segs + (si + 1) % segs
            d = (ri + 1) * segs + si
            faces.append((a, b, c, d))
    return verts, uvs, faces


def flat_disc(cx, cy, cz, r, segs=20):
    """Flat disc at fixed z, facing +Z."""
    verts, uvs, faces = [], [], []
    verts.append((cx, cy, cz))
    uvs.append((0.5, 0.5))
    for i in range(segs):
        a = 2 * math.pi * i / segs
        verts.append((cx + r * math.cos(a), cy + r * math.sin(a), cz))
        uvs.append((0.5 + 0.5 * math.cos(a), 0.5 + 0.5 * math.sin(a)))
    for i in range(segs):
        faces.append((0, i + 1, (i + 1) % segs + 1))
    return verts, uvs, faces


# ---------------------------------------------------------------------------
# OBJ writer
# ---------------------------------------------------------------------------

class ObjWriter:
    def __init__(self):
        self.verts = []
        self.uvs   = []
        self.faces = []

    def add(self, verts, uvs, faces, mat):
        vb = len(self.verts)
        ub = len(self.uvs)
        self.verts.extend(verts)
        self.uvs.extend(uvs)
        for f in faces:
            self.faces.append((mat, tuple((vb + vi + 1, ub + vi + 1) for vi in f)))

    def tri_count(self):
        return sum(len(f) - 2 for _, f in self.faces)

    def write(self, path, mtl_text):
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
            fh.write(mtl_text)


# ---------------------------------------------------------------------------
# MTL generator — references Crimson Gaze texture maps
# ---------------------------------------------------------------------------

def make_mtl(iris_rgb, pupil_rgb, colorway_key):
    diff_tex  = TEXTURES["diffuse"]
    norm_tex  = TEXTURES["normal"]
    rough_tex = TEXTURES["roughness"]

    def mat(name, kd, ks, ns, ni, map_kd=None, map_bump=None, d=1.0, illum=2):
        r, g, b = kd
        sr, sg, sb = ks
        lines = [
            f"newmtl {name}",
            f"Ns {ns:.1f}",
            f"Ka 0.05 0.05 0.05",
            f"Kd {r:.4f} {g:.4f} {b:.4f}",
            f"Ks {sr:.4f} {sg:.4f} {sb:.4f}",
            f"Ke 0.0 0.0 0.0",
            f"Ni {ni:.4f}",
            f"d {d:.2f}",
            f"illum {illum}",
        ]
        if map_kd:
            lines.append(f"map_Kd {map_kd}")
        if map_bump:
            lines.append(f"map_bump {map_bump}")
            lines.append(f"norm {map_bump}")
        return "\n".join(lines) + "\n"

    ir, ig, ib = iris_rgb

    return (
        # Sclera — warm white, diffuse texture carries vein detail
        mat("sclera",
            kd=SCLERA_COLOR, ks=(0.35, 0.35, 0.35), ns=90, ni=1.40,
            map_kd=diff_tex, map_bump=norm_tex) + "\n" +

        # Iris — colorway tint blended over diffuse, high specular
        mat("iris",
            kd=iris_rgb, ks=(0.50, 0.50, 0.50), ns=220, ni=1.45,
            map_kd=diff_tex, map_bump=norm_tex) + "\n" +

        # Pupil — near-black, mirror-like
        mat("pupil",
            kd=pupil_rgb, ks=(0.08, 0.08, 0.08), ns=600, ni=1.50) + "\n" +

        # Cornea — clear glass dome, IOR 1.376, near-zero diffuse, max spec
        # illum 4 = transparent + raytrace; d=0.92 slight transparency hint
        mat("cornea",
            kd=CORNEA_COLOR, ks=(0.95, 0.97, 1.00), ns=950, ni=1.376,
            d=0.92, illum=4)
    )


# ---------------------------------------------------------------------------
# Build one anatomically correct eye
# ---------------------------------------------------------------------------

def build_eye(colorway_key):
    c = COLORWAYS[colorway_key]
    w = ObjWriter()
    R = EYE_R

    # 1. Sclera — full UV sphere (eye globe)
    v, u, f = uv_sphere(0, 0, 0, R, segs=20, rings=14)
    w.add(v, u, f, "sclera")

    # 2. Iris — CONVEX cap sitting on front of sclera
    #    phi_end = ~32° gives a nicely rounded iris ring that matches the
    #    anatomy: iris fills roughly 30–35% of the visible globe front.
    #    We use a slightly smaller radius (R * 0.995) so it sits just inside
    #    the sclera surface, preventing z-fighting.
    IRIS_PHI = math.radians(32)
    v, u, f = convex_cap(0, 0, 0, R * 0.997, IRIS_PHI, segs=24, rings=8)
    w.add(v, u, f, "iris")

    # 3. Pupil — small flat disc at the front pole of the iris cap
    #    z offset: R * cos(0) = R, pulled in slightly
    PUPIL_R = R * 0.14          # pupil ≈ 14% of globe radius
    PUPIL_Z = R * 0.992         # just behind cornea inner surface
    v, u, f = flat_disc(0, 0, PUPIL_Z, PUPIL_R, segs=20)
    w.add(v, u, f, "pupil")

    # 4. Cornea — larger convex clear dome over the whole front face
    #    phi_end = ~40° covers the entire iris + limbus area.
    #    Radius slightly larger (R * 1.012) so it floats over iris and sclera.
    CORNEA_PHI = math.radians(40)
    v, u, f = convex_cap(0, 0, 0, R * 1.012, CORNEA_PHI, segs=24, rings=7)
    w.add(v, u, f, "cornea")

    mtl = make_mtl(c["iris"], c["pupil"], colorway_key)
    return w, mtl


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

counts = {}
for key, data in COLORWAYS.items():
    w, mtl = build_eye(key)
    path = os.path.join(OUT, f"crimson_gaze_{key}.obj")
    w.write(path, mtl)
    counts[key] = w.tri_count()
    print(f"  crimson_gaze_{key}.obj  {w.tri_count()} tris  — {data['label']}")

print(f"\nTotal colorways: {len(counts)}  |  avg tris: {sum(counts.values())//len(counts)}")
print("Done.")
