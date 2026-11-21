# Cut Sheet & Machining Spec — NEMA 23 + BK12 CNC Mount Bracket

- **Part Number:** `N23-BK12-001`
- **Material:** 6061-T6 Aluminum (recommended)
- **Finished Envelope:** `120.0 mm (X) × 156.0 mm (Y) × 76.0 mm (Z)`
- **Finished Volume / Mass:** `292.5 cm³` / `790 g` (in 6061-T6 @ `2.70 g/cm³`)
- **CAD Files:** `nema23-bk12-cnc-bracket.step`, `nema23-bk12-cnc-bracket.FCStd`
- **Created By:** FreeCAD MCP Server (`freecad-mcp`)

---

## Coordinate Datum Reference

All coordinates in this cut sheet match the STEP / FreeCAD model origin:
- **`X = 0.00`:** Symmetry centerline (`X = -60.0` left edge to `+60.0` right edge)
- **`Y = 0.00`:** Front face of the NEMA 23 vertical faceplate (`Y = -74.0` front BK12 edge to `+82.0` rear motor edge)
- **`Z = 0.00`:** Bottom CNC table seating surface (datum `A`, flatness `≤ 0.03 mm`)

---

## Option A: Monolithic CNC Billet Cut Sheet (Matches FEA Model)

### Raw Stock Required
| Stock Item | Alloy | Minimum Cut Blank (mm) | Standard US Stock Equivalent | Rough Mass | Finish Mass |
| :--- | :--- | :--- | :--- | :---: | :---: |
| 1× Rectangular Billet | 6061-T6 Al | **`125 × 165 × 82`** (+5 mm/side allowance) | `5.0" × 6.5" × 3.25"` bar (`127 × 165 × 82.6 mm`) | `~4.57 kg` | `0.79 kg` |

### Critical Machining Tolerances
- **Shaft Coaxiality (CRITICAL):**
  - NEMA 23 pilot bore centerline: **`Z = 44.00 ± 0.05 mm`**, **`X = 0.00 ± 0.03 mm`**
  - BK12 pedestal top pad height: **`Z = 19.00 ± 0.03 mm`** (parallel to Datum `A` `Z = 0` within `0.02 mm`) → yields `19.00 + 25.00 = 44.00 mm` coaxial alignment.
  - NEMA 23 faceplate (`Y = 0` & `Y = 10`): perpendicular to Datum `A` within `0.05 mm` over `76 mm`.
- **NEMA 23 Pilot Bore:** `Ø38.50 +0.10 / -0.00 mm` (slip fit on `Ø38.1 mm` motor boss).
- **General Unspecified Tolerances:** ISO 2768-m (`±0.15 mm`).

### Recommended 3-Op CNC Machining Sequence
1. **Op 1 (Top / `+Z` up):** Clamp billet in vise on bottom `6 mm` carrier stock. Rough & finish outer profile (`120 × 156 mm`, `R6` corners), base top (`Z = 10.0`), BK12 pedestal pad (`Z = 19.00 ±0.03`), front/rear twin webs (`8 mm` thick, `X = ±31..±39`, `R3` inner floor fillets), and vertical faceplate walls (`Y = 0..10`, `X = -39..+39`). Drill & mill 6× `8.4 × 18.0 mm` wing slots; spot, drill `Ø4.2 mm`, chamfer `0.6 mm × 45°`, and tap **2× `M5 × 0.8`** in the BK12 pedestal.
2. **Op 2 (Flip / `-Z` up):** Soft-jaw clamp on finished `120 × 156` outer perimeter. Face off carrier stock to exact `Z = 0.00` (Datum `A`, verifying `10.00 mm` base thickness and `19.00 ±0.03 mm` BK12 pedestal height). Deburr bottom edges of slots & tap holes.
3. **Op 3 (Front / `-Y` up, or 90° angle plate):** Register Datum `A` (`Z = 0`) against precision vise/angle plate. Mill `R5` top faceplate corners (`Z = 76.0`). Interpolate **`Ø38.50 mm`** center pilot bore at `(X = 0, Z = 44.00)` with `0.8 mm` front chamfer & `1.2 mm` rear chamfer (back-chamfer tool or flip). Drill **4× `Ø5.50 mm`** M5 clearance holes on the `47.14 × 47.14 mm` square with `0.6 mm` chamfers.

---

## Option B: Plate-Stock Fabrication Cut List (Saw + Mill + TIG Weld / Bolt)

Use this cut list if building from standard flat bar stock instead of hogging a solid billet. **Important:** Leave `+1.0 mm` finish allowance on the BK12 pedestal height (`10 mm` bar) and face-mill it down to exact `Z = 19.00 mm` **after** welding/assembly so thermal distortion doesn't throw off shaft alignment.

### Piece-by-Piece Cut List

| Cut ID | Part Description | Qty | Stock Spec (6061-T6) | Saw Cut Blank (mm) | Finished Geometry (mm) | Notes |
| :---: | :--- | :---: | :--- | :--- | :--- | :--- |
| **C1** | Main Base Plate | 1 | `10 mm × 125 mm` bar | `122 × 160 × 10` | `120.0 × 156.0 × 10.0` (`R6` corners) | 6× `8.4 × 18.0` slots at `X = ±49.5`, `Y = -57.5, +12, +60` |
| **C2** | NEMA 23 Vertical Faceplate | 1 | `10 mm × 80 mm` bar | `80 × 70 × 10` | `78.0 W × 66.0 H × 10.0 T` (`R5` top corners) | Sits on top of C1 (`Z = 10..76`, `Y = 0..10`); pilot bore at `34.0 mm` above bottom edge of C2 (`Z = 44.0`) |
| **C3** | BK12 Riser Pedestal | 1 | `10 mm × 70 mm` bar | `66 × 35 × 10` | `64.0 W × 32.0 D × 9.00 H` | Skim `1.00 mm` off top after welding to hit `Z = 19.00 ±0.03 mm`; drill & tap 2× M5×0.8 |
| **C4** | Rear Stiffening Gussets | 2 | `8 mm × 65 mm` bar | `66 × 62 × 8` (or 1 rect split diagonally) | Right trapezoid: `64.0` base (`Y = 10..74`), `60.0` tall (`Z = 10..70`), `6 mm` top/rear lands | Positioned at `X = ±31.0..±39.0` (`62 mm` clear motor bay) |
| **C5** | Front Tie-Ribs | 2 | `8 mm × 40 mm` bar | `76 × 38 × 8` | Stepped trapezoid: `74.0` base (`Y = -74..0`), `36.0` tall at faceplate (`Z = 10..46`), `9.0` tall beside BK12 pad (`Z = 10..19`) | Positioned at `X = ±31.0..±39.0`, tying faceplate directly to BK12 pedestal |

### Total Flat Bar Stock Summary (Including ~3 mm Saw Kerf per Cut)
- **10 mm (3/8") × 125 mm (5") 6061-T6 Flat Bar:** `~300 mm` (`12"`) total length (yields C1 + C2 + C3)
- **8 mm (5/16") × 65 mm (2.5") 6061-T6 Flat Bar:** `~310 mm` (`12.5"`) total length (yields 2× C4 + 2× C5)

---

## Master Hole & Slot Coordinate Table

| Feature | Qty | Type & Size | Axis | X (mm) | Y (mm) | Z (mm) | Chamfer / Notes |
| :--- | :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| **NEMA 23 Pilot Bore** | 1 | `Ø38.50 +0.10/-0.00` Thru | `Y` | `0.00` | `0..10` | `44.00` | `0.8×45°` front (`Y=0`), `1.2×45°` motor side (`Y=10`) |
| **NEMA 23 Mount Holes** | 4 | `Ø5.50` Thru (M5 Clr) | `Y` | `±23.57` | `0..10` | `20.43`, `67.57` | `47.14 × 47.14 mm` square; `0.6×45°` front chamfer |
| **BK12 Mount Holes** | 2 | `Ø4.20` Thru → **Tap `M5×0.8`** | `Z` | `±23.00` | `-57.50` | `0..19` | `46.00 mm` pitch; `0.6×45°` top lead-in chamfer (`Z=19`) |
| **CNC Table Slots (Front)** | 2 | `8.40 W × 18.00 L` Thru (along Y) | `Z` | `±49.50` | `-57.50` | `0..10` | `9.6 mm` axial travel; fits M6 or M8 + DIN 125 washer |
| **CNC Table Slots (Mid)** | 2 | `8.40 W × 18.00 L` Thru (along Y) | `Z` | `±49.50` | `+12.00` | `0..10` | `9.6 mm` axial travel |
| **CNC Table Slots (Rear)** | 2 | `8.40 W × 18.00 L` Thru (along Y) | `Z` | `±49.50` | `+60.00` | `0..10` | `9.6 mm` axial travel |

---

## Pre-Assembly Inspection Checklist
1. Verify `Z = 0` base sits rock-free on a surface plate (`≤ 0.03 mm` flatness).
2. Confirm BK12 pad height = **`19.00 ± 0.03 mm`** and NEMA 23 bore center = **`44.00 ± 0.05 mm`** from `Z = 0`.
3. Dry-fit NEMA 23 pilot boss into `Ø38.5 mm` bore (smooth hand slip fit) and verify `2.4 mm` clearance on each side between motor body and gussets.
4. Torque 2× **Class 12.9 M5×25** BK12 bolts with blue Loctite 243 to `6.0 N·m`, verify smooth spin of ballscrew through jaw coupler with zero binding before tightening the 6× M8 table bolts.
