# Bill of Materials (BOM) — NEMA 23 + BK12 CNC Router Table Mount

- **Assembly:** Integrated NEMA 23 Servo & BK12 Ballscrew Fixed-End Mount
- **Source Model:** `nema23-bk12-cnc-bracket.FCStd` / `nema23-bk12-cnc-bracket.step`
- **Created By:** FreeCAD MCP Server (`freecad-mcp`)
- **Datum / Units:** Millimeters (mm); coaxial shaft centerline at `Z = 44.0 mm` above table surface
- **FEA Summary:** 6061-T6 Aluminum, CalculiX 2.23 — Peak von Mises `12.74 MPa` (SF = `21.66×`), max deflection `4.2 µm` at `3,500 N` axial ballscrew thrust

---

## Manufactured Parts

| Item | Part Number | Description | Qty | Material | Finished Dimensions (mm) | Est. Mass | Notes |
| :---: | :--- | :--- | :---: | :--- | :--- | :---: | :--- |
| **1** | `N23-BK12-001` | Monolithic NEMA 23 + BK12 CNC Mount Bracket | 1 | 6061-T6 Aluminum | `120.0 × 156.0 × 76.0` (`292.5 cm³`) | `790 g` | Machine from billet (or fabricate from plate stock per `CUTSHEET.md`). Tap 2× M5×0.8 in BK12 pad. |

---

## Commercial Off-The-Shelf (COTS) Drivetrain Components

| Item | Component | Specification | Qty | Material | Key Dimensions (mm) | Notes |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| **2** | NEMA 23 Servo Motor | Standard NEMA 23 flange, Ø8 mm D-shaft (or Ø6.35/10 mm—match coupler bore) | 1 | Anodized Al / Steel | `57.2 × 57.2` flange, `Ø38.1` boss, `47.14` bolt square | Verify shaft Ø before ordering coupler hub. |
| **3** | BK12 Fixed Bearing Block | Standard BK12 angular-contact support block (fits SFU1605 / SFU1610) | 1 | Black-oxide S45C Steel | `60.0 W × 25.0 D × 43.0 H`, shaft center `25.0 mm` | Includes locknut & oil seals; `46.0 mm` bolt pitch. |
| **4** | Flexible Jaw Coupler | 3-piece zero-backlash jaw coupler (e.g. D25L30 or D26L32) | 1 | 7075/6061 Al + 98A PU Spider | `Ø25–26 × 30–32 L`, `8 mm × 10 mm` bores | Fits in `45.0 mm` open coupler bay; match bores to motor & ballscrew. |
| **5** | SFU1605 / SFU1610 Ballscrew | 16 mm ballscrew w/ standard BK12/BF12 machined end (`Ø12` bearing journal, `Ø10` coupler journal) | 1 | Hardened Bearing Steel | `Ø16 mm` screw (length per CNC axis) | Paired with BF12 floating support on opposite axis end. |

---

## Fasteners & Hardware

| Item | Fastener | Standard / Grade | Qty | Size | Location / Function | Recommended Torque & Prep |
| :---: | :--- | :--- | :---: | :--- | :--- | :--- |
| **6** | Socket Head Cap Screw | ISO 4762, Class 12.9 (or 18-8 SS) | 4 | `M5 × 16 mm` | NEMA 23 motor to faceplate (`47.14 mm` square, `Ø5.5` thru) | `5.0 N·m`; add 4× M5 locknuts + washers if motor ears are unthreaded (`M5 × 25 mm`). |
| **7** | Socket Head Cap Screw | ISO 4762, **Class 12.9** | 2 | `M5 × 25 mm` | BK12 block into `M5×0.8` tapped bracket pedestal (`X = ±23, Y = -57.5`) | `6.0 N·m` + **blue Loctite 243** (carries full axial ballscrew thrust). |
| **8** | Socket Head Cap Screw | ISO 4762, Class 10.9 / 12.9 | 6 | `M8 × 20 mm` *(or M6 × 20)* | Bracket outer wing slots (`8.4 × 18.0 mm`) to CNC table | `18–22 N·m` (M8) / `9–10 N·m` (M6). Length depends on T-nut engagement depth. |
| **9** | Flat Washer | DIN 125 / ISO 7089, Hardened Steel | 6 | `M8` (`16 mm OD × 1.6 mm`) | Under M8 table bolt heads on `8.4 × 18.0 mm` slots | Prevents galling on 6061-T6 aluminum slots during tensioning. |
| **10** | Table T-Slot Nut | Match CNC table T-slot profile | 6 | `M8` *(or M6)* | CNC router table T-slots | Verify T-slot width/depth on your router bed before ordering. |

### Optional Precision Upgrades
- **2 × Ø4 × 12 mm Dowel Pins (DIN 6325):** Press-fit between BK12 block and pedestal to eliminate any possibility of slip under rapid axis crash loads.
- **M5 Helicoil / Keensert Inserts (×2):** Recommended in the BK12 pedestal if the BK12 block will be removed and reinstalled frequently.
