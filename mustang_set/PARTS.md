# Mustang Jewelry Set — Part List

**Character:** Mustang  
**Colorway:** Rose Gold + Pink Sapphire  
**Pipeline:** BC Build Pipeline  
**Diamond library ref:** `01_diamond_library/pave_pink_sapphire_512.dds`  
**Export format:** OBJ + MTL (triangulated)

---

## Parts

### 1. Necklace — `necklace.obj`

| Detail | Value |
|---|---|
| Style | Cuban-link chain with pavé pendant cluster |
| Chain radius | 230 mm (≈ 18 in) |
| Link count | 60 alternating-rotation torus links |
| Pendant | 5 pavé pink-sapphire spheres, flush-set |
| Metal mat | `rg_gold` (Rose Gold: Kd 0.796 0.498 0.388) |
| Stone mat | `pink_saph` (Pink Sapphire: Kd 0.918 0.412 0.631) |
| **Tri count** | **12 000** |
| Verts | 6 040 |

---

### 2. Bracelet Stack — `bracelet_stack.obj`

Three bracelets stacked on the same wrist plane.

| Sub-piece | Style |
|---|---|
| A – Pavé band | Thin torus band with 36 flush-set sapphires |
| B – Tennis bracelet | 30 prong-set oval sapphires on a chain base |
| C – Bangle | Solid wide flat ring |

| Detail | Value |
|---|---|
| **Tri count** | **7 728** |
| Verts | 4 260 |

---

### 3. Earrings — `earrings.obj`

Drop studs (pair, exported as single mesh).

| Detail | Value |
|---|---|
| Style | Post stud + pavé dome + hanging teardrop |
| Stud dome | UV sphere r=7 mm with 6-ring + 1 centre sapphire layout |
| Drop | Elongated (z×1.6) sphere sapphire on a bail ring |
| **Tri count** | **1 568** |
| Verts | 916 |

---

### 4. Ring — `ring.obj`

| Detail | Value |
|---|---|
| Style | Wide band, full pavé top row, box-set oval centre |
| Shank | Torus maj_r 8.5 mm / min_r 3 mm (≈ US size 6) |
| Pavé row | 18 sapphires along top 180° arc |
| Centre stone | Oval pink sapphire in box setting |
| **Tri count** | **2 028** |
| Verts | 1 136 |

---

## Summary

| File | Tris | Verts |
|---|---|---|
| necklace.obj | 12 000 | 6 040 |
| bracelet_stack.obj | 7 728 | 4 260 |
| earrings.obj | 1 568 | 916 |
| ring.obj | 2 028 | 1 136 |
| **Total** | **23 324** | **12 352** |

---

## Materials

```
rg_gold    — Kd 0.796 0.498 0.388, Ks near-white, Ns 250, Ni 1.45
pink_saph  — Kd 0.918 0.412 0.631, Ks near-white, Ns 500, Ni 1.77
```

Texture slot references `01_diamond_library/pave_pink_sapphire_512.dds`.

---

## Build Notes

- No floating geometry: every stone is seated flush or prong-set.
- All Cuban-chain links interlock with alternating 90° rotation.
- Bracelet stack z-offset: A at +20 mm, B at 0, C at −20 mm.
- Earring pair exported as one mesh; split at x=0 for individual placement.
- Rebuild: `python3 scripts/generate_objs.py`
