# BC Eyeball Build — All Colorways

**Pipeline:** BC Build Pipeline  
**Scale:** 12 mm radius (standard FiveM eye prop)  
**Geometry per eye:** sclera + iris disc + pupil disc + cornea cap  
**Tris per eye:** 588  

---

## Colorways

| File | Label | Iris Kd | For |
|---|---|---|---|
| `brown_eye.obj` | Buda brown | 0.38 0.22 0.08 | Buda |
| `baby_blue_eye.obj` | Girls baby blue | 0.53 0.78 0.92 | Mustang + girls |
| `dark_brown_eye.obj` | Dark brown / near-black | 0.18 0.09 0.03 | Alt dark |
| `green_eye.obj` | Emerald green | 0.20 0.55 0.25 | Alt green |
| `hazel_eye.obj` | Hazel / amber | 0.58 0.42 0.12 | Alt hazel |

---

## Materials (per eye, 4 mats)

| Mat | Role | Notes |
|---|---|---|
| `sclera` | White of eye | Warm white, Ns 80, slight spec |
| `iris` | Colored ring | High spec Ns 200, colorway-specific Kd |
| `pupil` | Black centre | Near-black, Ns 500 |
| `cornea` | Dome overlay | Near-white, Ns 900, Ni 1.37 (glass-like) |

---

## Rebuild

```bash
python3 scripts/build_eyeballs.py
```
