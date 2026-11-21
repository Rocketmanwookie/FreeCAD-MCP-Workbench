"""Machinist Engineering Drawing (11x17" ANSI B) for NEMA 23 + BK12 CNC Bracket.

Generates an exact 11" x 17" (431.8 x 279.4 mm) landscape shop drawing PDF
projected directly from nema23-bk12-cnc-bracket.step, with:
- Third-angle orthographic views (Top, Front, Right) + Isometric pictorial
- True hidden lines, center marks, measured machinist dimensions & hole callouts
- Clean ANSI B machinist title block & revision table left blank for filling out
  (plus real interactive PDF AcroForm text fields overlaid in every blank cell!)
"""

from __future__ import annotations

import os
import re
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mplconfig")

from cad import step
import cad.eng_drawing as ed
from cad.eng_drawing import Sheet, SHEET_SIZES, _render_sheet, _write_pdf

# Register exact 11" x 17" ANSI B landscape sheet size (431.8 x 279.4 mm)
SHEET_SIZES["ANSI-B"] = (431.8, 279.4)

HERE = Path(__file__).parent
STEP_PATH = HERE / "nema23-bk12-cnc-bracket.step"
OUT_PDF = HERE / "nema23-bk12-cnc-bracket-drawing-11x17.pdf"

# Exact model datum dimensions (matching nema23-bk12-cnc-bracket.step)
BASE_W = 120.0
BASE_Y_MIN = -74.0
BASE_Y_MAX = 82.0
T_BASE = 10.0
T_FACE = 10.0
FACE_W = 78.0
FACE_H = 76.0
MOTOR_Z = 44.0
NEMA23_PILOT_DIA = 38.5
NEMA23_HALF_BOLT = 47.14 / 2.0  # 23.57
BK12_PAD_Z = 19.0
BK12_PAD_W = 64.0
BK12_PAD_Y_MIN = -74.0
BK12_PAD_Y_MAX = -42.0
BK12_Y_MID = -57.5
BK12_HALF_BOLT = 23.0
SLOT_X = 49.5
SLOT_Y = (-57.5, 12.0, 60.0)


def draw_fillable_ansi_b_titleblock(doc, sheet_w: float, sheet_h: float):
    """Replace default title block lines/text with a crisp ANSI B machinist title block
    and return list of (field_name, x0_mm, y0_mm, x1_mm, y1_mm, font_pt, default_val)
    for interactive PDF AcroForm fields."""
    from ezdxf.enums import TextEntityAlignment

    msp = doc.modelspace()
    m = 10.0  # Frame margin (mm)

    # Remove default title block entities (everything on layer TITLE)
    for e in list(msp):
        if e.dxf.layer == "TITLE":
            msp.delete_entity(e)

    # Draw outer + inner double ANSI border with zone ticks (A-D vertical, 1-8 horizontal)
    bx0, by0, bx1, by1 = m, m, sheet_w - m, sheet_h - m
    # Clear existing SHEET polyline and draw crisp ANSI B border with zone markers
    for e in list(msp):
        if e.dxf.layer == "SHEET":
            msp.delete_entity(e)
    msp.add_lwpolyline([(bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1)], close=True, dxfattribs={"layer": "SHEET"})
    # Outer zone trim border 5 mm outside inner frame
    zx0, zy0, zx1, zy1 = bx0 - 4.5, by0 - 4.5, bx1 + 4.5, by1 + 4.5
    msp.add_lwpolyline([(zx0, zy0), (zx1, zy0), (zx1, zy1), (zx0, zy1)], close=True, dxfattribs={"layer": "TITLE"})

    def add_txt(val: str, x: float, y: float, h: float, align=TextEntityAlignment.MIDDLE_LEFT, layer="TITLE"):
        t = msp.add_text(val, height=h, dxfattribs={"layer": layer, "style": "CAD"})
        t.set_placement((x, y), align=align)
        return t

    # Horizontal zone dividers (1..8 right-to-left or left-to-right; standard ASME Y14.1: 8..1 left-to-right)
    n_cols = 8
    col_w = (bx1 - bx0) / n_cols
    for i in range(n_cols):
        cx = bx0 + (i + 0.5) * col_w
        zone_num = str(n_cols - i)
        add_txt(zone_num, cx, by1 + 2.25, 2.2, TextEntityAlignment.MIDDLE_CENTER)
        add_txt(zone_num, cx, by0 - 2.25, 2.2, TextEntityAlignment.MIDDLE_CENTER)
        if i > 0:
            tx = bx0 + i * col_w
            msp.add_line((tx, by1), (tx, zy1), dxfattribs={"layer": "TITLE"})
            msp.add_line((tx, by0), (tx, zy0), dxfattribs={"layer": "TITLE"})

    # Vertical zone dividers (A..D bottom-to-top)
    n_rows = 4
    row_h = (by1 - by0) / n_rows
    for j in range(n_rows):
        cy = by0 + (j + 0.5) * row_h
        zone_let = chr(ord("A") + j)
        add_txt(zone_let, bx0 - 2.25, cy, 2.2, TextEntityAlignment.MIDDLE_CENTER)
        add_txt(zone_let, bx1 + 2.25, cy, 2.2, TextEntityAlignment.MIDDLE_CENTER)
        if j > 0:
            ty = by0 + j * row_h
            msp.add_line((bx0, ty), (zx0, ty), dxfattribs={"layer": "TITLE"})
            msp.add_line((bx1, ty), (zx1, ty), dxfattribs={"layer": "TITLE"})

    # ==========================================================================
    # FILLABLE ANSI B MACHINIST TITLE BLOCK (bottom-right: 192 x 48 mm)
    # ==========================================================================
    tw, th = 192.0, 48.0
    tx0, ty0 = bx1 - tw, by0
    tx1, ty1 = bx1, by0 + th

    # Outer heavy box
    msp.add_lwpolyline([(tx0, ty0), (tx1, ty0), (tx1, ty1), (tx0, ty1)], close=True, dxfattribs={"layer": "SHEET"})

    # Main vertical split: Left approvals/meta (76 mm) | Right title/part/scale (116 mm)
    x_mid = tx0 + 76.0
    msp.add_line((x_mid, ty0), (x_mid, ty1), dxfattribs={"layer": "SHEET"})

    fields: list[tuple[str, float, float, float, float, float, str]] = []

    def add_field(name: str, x0: float, y0: float, x1: float, y1: float, label: str, font_pt: float = 9.0, prefill: str = ""):
        # Label in top-left of cell
        add_txt(label, x0 + 1.4, y1 - 2.2, 1.7, TextEntityAlignment.MIDDLE_LEFT)
        if prefill:
            # Static pre-filled value centered vertically below label
            add_txt(prefill, x0 + 2.0, y0 + (y1 - y0 - 3.2) / 2.0, 2.6, TextEntityAlignment.MIDDLE_LEFT)
        else:
            # Interactive fillable AcroForm text box inside cell below label
            fields.append((name, x0 + 1.0, y0 + 0.8, x1 - 1.0, y1 - 3.6, font_pt, ""))

    # --- LEFT COLUMN (76 mm wide, 4 rows of 12 mm each) ---
    # Row 4 (top, y=36..48): DRAWN BY | DATE
    # Row 3 (y=24..36):      CHECKED BY | DATE
    # Row 2 (y=12..24):      APPROVED BY | DATE
    # Row 1 (y=0..12):       MATERIAL | FINISH
    for r in (12.0, 24.0, 36.0):
        msp.add_line((tx0, ty0 + r), (x_mid, ty0 + r), dxfattribs={"layer": "TITLE"})
    x_date = tx0 + 48.0
    msp.add_line((x_date, ty0 + 12.0), (x_date, ty1), dxfattribs={"layer": "TITLE"})
    x_fin = tx0 + 44.0
    msp.add_line((x_fin, ty0), (x_fin, ty0 + 12.0), dxfattribs={"layer": "TITLE"})

    add_field("drawn_by",    tx0,    ty0 + 36, x_date, ty0 + 48, "DRAWN BY",    8.5)
    add_field("drawn_date",  x_date, ty0 + 36, x_mid,  ty0 + 48, "DATE",        8.5)
    add_field("checked_by",  tx0,    ty0 + 24, x_date, ty0 + 36, "CHECKED BY",  8.5)
    add_field("checked_date",x_date, ty0 + 24, x_mid,  ty0 + 36, "DATE",        8.5)
    add_field("approved_by", tx0,    ty0 + 12, x_date, ty0 + 24, "APPROVED BY", 8.5)
    add_field("approved_date",x_date,ty0 + 12, x_mid,  ty0 + 24, "DATE",        8.5)
    add_field("material",    tx0,    ty0,      x_fin,  ty0 + 12, "MATERIAL",    8.5)
    add_field("finish",      x_fin,  ty0,      x_mid,  ty0 + 12, "FINISH",      8.5)

    # --- RIGHT COLUMN (116 mm wide) ---
    # Top row (y=36..48): COMPANY / SHOP
    # Row 3   (y=22..36): DRAWING TITLE
    # Row 2   (y=10..22): SIZE (16mm) | DWG / PART NO. (78mm) | REV (22mm)
    # Row 1   (y=0..10):  SCALE (28mm) | UNITS (22mm) | PROJECTION (38mm) | SHEET (28mm)
    for r in (10.0, 22.0, 36.0):
        msp.add_line((x_mid, ty0 + r), (tx1, ty0 + r), dxfattribs={"layer": "TITLE"})

    add_field("company", x_mid, ty0 + 36, tx1, ty0 + 48, "COMPANY / SHOP", 10.0)
    add_field("drawing_title", x_mid, ty0 + 22, tx1, ty0 + 36, "DRAWING TITLE", 11.0)

    x_pn = x_mid + 21.0
    x_rev = tx1 - 20.0
    msp.add_line((x_pn, ty0 + 10), (x_pn, ty0 + 22), dxfattribs={"layer": "TITLE"})
    msp.add_line((x_rev, ty0 + 10), (x_rev, ty0 + 22), dxfattribs={"layer": "TITLE"})
    add_field("size", x_mid, ty0 + 10, x_pn, ty0 + 22, "SIZE", 8.5, prefill="B 11x17")
    add_field("part_number", x_pn, ty0 + 10, x_rev, ty0 + 22, "PART / DWG NO.", 10.0)
    add_field("revision", x_rev, ty0 + 10, tx1, ty0 + 22, "REV", 10.0)

    # Bottom technical strip (pre-filled drawing facts)
    x_u = x_mid + 26.0
    x_p = x_u + 22.0
    x_s = x_p + 40.0
    for xv in (x_u, x_p, x_s):
        msp.add_line((xv, ty0), (xv, ty0 + 10), dxfattribs={"layer": "TITLE"})
    add_field("scale", x_mid, ty0, x_u, ty0 + 10, "SCALE", 8.5, prefill="1:2")
    add_field("units", x_u, ty0, x_p, ty0 + 10, "UNITS", 8.5, prefill="MM")
    add_field("projection", x_p, ty0, x_s, ty0 + 10, "PROJECTION", 8.5, prefill="THIRD ANGLE")
    add_field("sheet_num", x_s, ty0, tx1, ty0 + 10, "SHEET", 8.5, prefill="1 OF 1")

    # ==========================================================================
    # BLANK REVISION TABLE (top-right inside frame, fillable!)
    # ==========================================================================
    rev_cols = [("REV", 14.0), ("ZONE", 16.0), ("DESCRIPTION", 64.0), ("DATE", 24.0), ("APPR.", 18.0)]
    rw = sum(w for _, w in rev_cols)
    rh = 6.0
    rx0, ry_top = bx1 - rw, by1
    n_blank_revs = 3
    total_rh = (n_blank_revs + 1) * rh
    msp.add_lwpolyline([(rx0, ry_top - total_rh), (bx1, ry_top - total_rh), (bx1, ry_top), (rx0, ry_top)], close=True, dxfattribs={"layer": "SHEET"})

    # Header row
    y_hdr = ry_top - rh
    msp.add_line((rx0, y_hdr), (bx1, y_hdr), dxfattribs={"layer": "TITLE"})
    cx = rx0
    for idx, (col_lbl, cw) in enumerate(rev_cols):
        if idx > 0:
            msp.add_line((cx, ry_top - total_rh), (cx, ry_top), dxfattribs={"layer": "TITLE"})
        add_txt(col_lbl, cx + cw / 2.0, y_hdr + rh / 2.0, 2.0, TextEntityAlignment.MIDDLE_CENTER)
        cx += cw

    # 3 blank fillable revision rows
    for r_idx in range(n_blank_revs):
        ry0 = y_hdr - (r_idx + 1) * rh
        if r_idx < n_blank_revs - 1:
            msp.add_line((rx0, ry0), (bx1, ry0), dxfattribs={"layer": "TITLE"})
        cx = rx0
        for col_lbl, cw in rev_cols:
            fname = f"rev_{r_idx + 1}_{col_lbl.lower().rstrip('.')}"
            fields.append((fname, cx + 0.7, ry0 + 0.6, cx + cw - 0.7, ry0 + rh - 0.6, 8.0, ""))
            cx += cw

    # Reposition NOTES cleanly in bottom-left above bottom frame (clear of views & title block!)
    for e in list(msp):
        if e.dxf.layer == "NOTES" and e.dxftype() == "TEXT":
            txt = e.dxf.text
            if txt.startswith(("1.", "2.", "3.", "4.", "5.", "6.", "NOTES")):
                msp.delete_entity(e)

    shop_notes = [
        "NOTES (UNLESS OTHERWISE SPECIFIED):",
        "1. GENERAL TOLERANCES PER ISO 2768-m (±0.15 MM). DIMENSIONS IN MILLIMETERS.",
        "2. RECOMMENDED MATERIAL: 6061-T6 ALUMINUM. BREAK ALL SHARP EDGES 0.5 x 45°.",
        "3. DATUM A (BOTTOM Z=0) FLAT WITHIN 0.03 MM. FACEPLATE PERPENDICULAR TO A WITHIN 0.05 MM.",
        "4. COAXIALITY: BK12 PAD Z=19.00 ±0.03 MM & NEMA 23 PILOT BORE Z=44.00 ±0.05 MM.",
        "5. ALL 3 INNER BASE FILLETS R3.0; OUTER BASE CORNERS R6.0; TOP FACEPLATE CORNERS R5.0.",
        "6. CAD MODEL GENERATED BY FREECAD MCP SERVER (freecad-mcp).",
    ]
    ny = by0 + 3.0 + (len(shop_notes) - 1) * 4.4
    for i, line in enumerate(shop_notes):
        h = 2.3 if i == 0 else 2.0
        add_txt(line, bx0 + 3.0, ny - i * 4.4, h, TextEntityAlignment.BOTTOM_LEFT, layer="NOTES")

    return fields


def add_acroform_fields_to_pdf(pdf_path: Path, fields: list[tuple[str, float, float, float, float, float, str]]):
    """Append real interactive PDF AcroForm text fields via a valid PDF incremental update
    (zero external dependencies; works in Chrome, Evince, Okular, Acrobat, Preview)."""
    raw = pdf_path.read_bytes()
    mm_to_pt = 72.0 / 25.4

    # Locate Root catalog, Page 1 object number, Size, and startxref in matplotlib PDF
    m_size = re.search(rb"/Size\s+(\d+)", raw)
    m_root = re.search(rb"/Root\s+(\d+)\s+0\s+R", raw)
    m_startxref = list(re.finditer(rb"startxref\s+(\d+)", raw))
    if not (m_size and m_root and m_startxref):
        raise RuntimeError("Could not parse PDF trailer for AcroForm injection")

    orig_size = int(m_size.group(1))
    root_num = int(m_root.group(1))
    prev_xref = int(m_startxref[-1].group(1))

    # Find Page object (has /Type /Page and not /Pages)
    m_page = re.search(rb"(\d+)\s+0\s+obj\s*<<(?:(?!/Type\s*/Pages).)*?/Type\s*/Page\b.*?>>", raw, re.S)
    if not m_page:
        raise RuntimeError("Could not locate Page 1 object in PDF")
    page_num = int(m_page.group(1))
    page_dict_bytes = m_page.group(0)
    # Extract existing Page dictionary body between << and >>
    page_inner = page_dict_bytes[page_dict_bytes.index(b"<<") + 2 : page_dict_bytes.rindex(b">>")]

    # Find Catalog dictionary body
    m_cat = re.search(rf"{root_num}\s+0\s+obj\s*<<(.*?)>>".encode(), raw, re.S)
    if not m_cat:
        raise RuntimeError("Could not locate Root catalog object in PDF")
    cat_inner = m_cat.group(1)

    next_id = orig_size
    font_id = next_id; next_id += 1
    acro_id = next_id; next_id += 1

    widget_ids = []
    objects: list[tuple[int, bytes]] = []

    # Standard Helvetica Type1 font object for AcroForm text fields
    objects.append((font_id, b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"))

    # Create one interactive Tx widget annotation per fillable title block / revision cell
    for fname, x0_mm, y0_mm, x1_mm, y1_mm, font_pt, val in fields:
        wid = next_id
        next_id += 1
        widget_ids.append(wid)
        rect = f"[{x0_mm * mm_to_pt:.2f} {y0_mm * mm_to_pt:.2f} {x1_mm * mm_to_pt:.2f} {y1_mm * mm_to_pt:.2f}]"
        # Subtle light-blue interactive tint on screen (transparent when printed: /F 4 = Print, no border)
        da = f"/Helv {font_pt:.1f} Tf 0 0 0 rg"
        wdict = (
            f"<< /Type /Annot /Subtype /Widget /FT /Tx "
            f"/T ({fname}) /V ({val}) "
            f"/Rect {rect} "
            f"/F 4 /Border [0 0 0] "
            f"/DA ({da}) "
            f"/P {page_num} 0 R >>"
        ).encode("ascii")
        objects.append((wid, wdict))

    kids_refs = " ".join(f"{wid} 0 R" for wid in widget_ids).encode("ascii")

    # AcroForm dictionary
    acro_dict = (
        b"<< /Fields [" + kids_refs + b"] "
        b"/NeedAppearances true "
        b"/DR << /Font << /Helv " + f"{font_id} 0 R".encode() + b" >> >> "
        b"/DA (/Helv 9 Tf 0 0 0 rg) >>"
    )
    objects.append((acro_id, acro_dict))

    # Updated Page 1 object adding /Annots
    if b"/Annots" in page_inner:
        new_page_inner = re.sub(rb"/Annots\s*\[[^\]]*\]", b"/Annots [" + kids_refs + b"]", page_inner)
    else:
        new_page_inner = page_inner + b"\n/Annots [" + kids_refs + b"]"
    objects.append((page_num, b"<<" + new_page_inner + b">>"))

    # Updated Catalog object adding /AcroForm
    if b"/AcroForm" in cat_inner:
        new_cat_inner = re.sub(rb"/AcroForm\s+\d+\s+0\s+R", f"/AcroForm {acro_id} 0 R".encode(), cat_inner)
    else:
        new_cat_inner = cat_inner + f"\n/AcroForm {acro_id} 0 R".encode()
    objects.append((root_num, b"<<" + new_cat_inner + b">>"))

    # Build incremental PDF append
    out = bytearray(raw)
    if not out.endswith(b"\n"):
        out.extend(b"\n")

    offsets: dict[int, int] = {}
    for obj_num, body in objects:
        offsets[obj_num] = len(out)
        out.extend(f"{obj_num} 0 obj\n".encode("ascii"))
        out.extend(body)
        out.extend(b"\nendobj\n")

    xref_pos = len(out)
    out.extend(b"xref\n")
    # Write individual single-entry subsections (valid per PDF 1.4+ spec)
    for obj_num in sorted(offsets):
        out.extend(f"{obj_num} 1\n".encode("ascii"))
        out.extend(f"{offsets[obj_num]:010d} 00000 n \n".encode("ascii"))

    # Preserve /Info reference if present in original trailer
    m_info = re.search(rb"/Info\s+(\d+\s+0\s+R)", raw)
    info_entry = b" /Info " + m_info.group(1) if m_info else b""

    out.extend(
        f"trailer\n<< /Size {next_id} /Root {root_num} 0 R{info_entry.decode('ascii')} /Prev {prev_xref} >>\n"
        f"startxref\n{xref_pos}\n%%EOF\n".encode("ascii")
    )
    pdf_path.write_bytes(bytes(out))


def build_drawing():
    part = step.read(STEP_PATH)

    # ANSI B (11x17" = 431.8 x 279.4 mm), 1:2 scale, Third Angle Projection
    sheet = Sheet(
        "ANSI-B",
        scale=0.5,
        title=" ",
        part_number="",
        material="",
        revision=" ",
        units="mm",
        projection="THIRD ANGLE",
        ink="mono",
        text_height=3.0,
    )

    # Balanced Third-Angle layout on 431.8 x 279.4 mm ANSI B sheet:
    # - Top view   (60 x 78 mm at 1:2): centered at (102, 202) -> X=[72..132], Y=[163..241]
    # - Front view (60 x 38 mm at 1:2): centered at (102, 91)  -> X=[72..132], Y=[72..110]
    # - Right view (78 x 38 mm at 1:2): centered at (288, 91)  -> X=[249..327], Y=[72..110]
    # - Iso view   (at 0.54 scale):     centered at (348, 184) -> upper-right below rev table
    top = sheet.view(part, "top", at=(102.0, 202.0), label="TOP VIEW (SCALE 1:2)")
    front = sheet.view(part, "front", at=(102.0, 91.0), label="FRONT VIEW (SCALE 1:2)")
    right = sheet.view(part, "right", at=(288.0, 91.0), label="RIGHT VIEW (SCALE 1:2)")
    iso = sheet.view(part, "iso", at=(348.0, 184.0), label="ISOMETRIC (REF)", hidden=False, centre_marks=False, scale=0.54)

    # ==========================================================================
    # TOP VIEW DIMENSIONS (X = -60..+60, Y = -74..+82; at 1:2, 1 model mm = 0.5 sheet mm)
    # ==========================================================================
    top.dim((-31.0, 42.0, T_BASE), (31.0, 42.0, T_BASE), orientation="h", offset=26.0)
    top.dim((-SLOT_X, SLOT_Y[2], T_BASE), (SLOT_X, SLOT_Y[2], T_BASE), orientation="h", offset=24.0)
    top.dim((-BASE_W / 2.0, BASE_Y_MAX, T_BASE), (BASE_W / 2.0, BASE_Y_MAX, T_BASE), orientation="h", offset=20.0)
    # Left side: BK12 pad depth (32) inner, Overall depth (156) outer
    top.dim((-BK12_PAD_W / 2.0, BK12_PAD_Y_MIN, BK12_PAD_Z), (-BK12_PAD_W / 2.0, BK12_PAD_Y_MAX, BK12_PAD_Z), orientation="v", offset=-24.0)
    top.dim((-BASE_W / 2.0, BASE_Y_MIN, T_BASE), (-BASE_W / 2.0, BASE_Y_MAX, T_BASE), orientation="v", offset=-20.0)
    # Bottom of Top view: BK12 bolt pitch (46) & BK12 pad width (64)
    top.dim((-BK12_HALF_BOLT, BK12_Y_MID, BK12_PAD_Z), (BK12_HALF_BOLT, BK12_Y_MID, BK12_PAD_Z), orientation="h", offset=-15.0)
    top.dim((-BK12_PAD_W / 2.0, BK12_PAD_Y_MIN, BK12_PAD_Z), (BK12_PAD_W / 2.0, BK12_PAD_Y_MIN, BK12_PAD_Z), orientation="h", offset=-15.0)
    # Right side vertical chain: 16.5, 69.5, 48.0 aligned on one crisp line
    top.dim((BASE_W / 2.0, BASE_Y_MIN, T_BASE), (SLOT_X, SLOT_Y[0], T_BASE), orientation="v", offset=12.0)
    top.dim((SLOT_X, SLOT_Y[0], T_BASE), (SLOT_X, SLOT_Y[1], T_BASE), orientation="v", offset=17.25)
    top.dim((SLOT_X, SLOT_Y[1], T_BASE), (SLOT_X, SLOT_Y[2], T_BASE), orientation="v", offset=17.25)
    # Callouts on Top view
    top.hole((BK12_HALF_BOLT, BK12_Y_MID, BK12_PAD_Z), 4.2, thru=True, thread="M5x0.8", count=2, angle=-22, label="BK12 MOUNT")
    top.note("6x SLOT 8.4 x 18.0 THRU (M6/M8)", (SLOT_X, SLOT_Y[2], T_BASE), offset=(26.0, 10.0))

    # ==========================================================================
    # FRONT VIEW DIMENSIONS (X = -60..+60, Z = 0..76; Y_sheet=[72..110])
    # ==========================================================================
    front.dim((-NEMA23_HALF_BOLT, 0.0, MOTOR_Z + NEMA23_HALF_BOLT), (NEMA23_HALF_BOLT, 0.0, MOTOR_Z + NEMA23_HALF_BOLT), orientation="h", offset=11.0)
    front.dim((-FACE_W / 2.0, 0.0, FACE_H), (FACE_W / 2.0, 0.0, FACE_H), orientation="h", offset=15.0)
    # Left side (3 evenly spaced vertical rows): 10 (row 1), 19 ±0.03 (row 2), 76 (row 3)
    front.dim((-BASE_W / 2.0, 0.0, 0.0), (-BASE_W / 2.0, 0.0, T_BASE), orientation="v", offset=-10.0)
    front.dim((-BK12_PAD_W / 2.0, BK12_PAD_Y_MIN, 0.0), (-BK12_PAD_W / 2.0, BK12_PAD_Y_MIN, BK12_PAD_Z), orientation="v", offset=-36.0, tol=0.03)
    front.dim((-FACE_W / 2.0, 0.0, 0.0), (-FACE_W / 2.0, 0.0, FACE_H), orientation="v", offset=-46.0)
    # Right side: 47.14 bolt height (inner) & 44 ±0.05 shaft centerline (outer)
    front.dim((NEMA23_HALF_BOLT, 0.0, MOTOR_Z - NEMA23_HALF_BOLT), (NEMA23_HALF_BOLT, 0.0, MOTOR_Z + NEMA23_HALF_BOLT), orientation="v", offset=26.0)
    front.dim((BASE_W / 2.0, 0.0, 0.0), (0.0, 0.0, MOTOR_Z), orientation="v", offset=18.0, tol=0.05)
    # Hole callouts on Front view (cleanly inside wide open gap between Front & Right)
    front.hole((NEMA23_HALF_BOLT, 0.0, MOTOR_Z + NEMA23_HALF_BOLT), 5.5, thru=True, count=4, angle=24, label="M5 CLR")
    front.hole((0.0, 0.0, MOTOR_Z), NEMA23_PILOT_DIA, thru=True, tol=(0.10, 0.0), angle=-14, label="NEMA 23 PILOT")

    # ==========================================================================
    # RIGHT VIEW DIMENSIONS (Y = -74..+82, Z = 0..76; X_sheet=[249..327], Y_sheet=[72..110])
    # ==========================================================================
    right.dim((31.0, BK12_PAD_Y_MAX, BK12_PAD_Z), (31.0, 0.0, BK12_PAD_Z), orientation="h", offset=38.0)
    right.dim((FACE_W / 2.0, 0.0, FACE_H), (FACE_W / 2.0, T_FACE, FACE_H), orientation="h", offset=10.0)
    right.dim((FACE_W / 2.0, T_FACE, T_BASE), (FACE_W / 2.0, 74.0, T_BASE), orientation="h", offset=43.0)
    # Vertical dims: 46 front tie-rib on left, 70 rear gusset on right
    right.dim((FACE_W / 2.0, 0.0, 0.0), (FACE_W / 2.0, 0.0, 46.0), orientation="v", offset=-48.0)
    right.dim((FACE_W / 2.0, T_FACE, 0.0), (FACE_W / 2.0, T_FACE, 70.0), orientation="v", offset=48.0)
    right.note("2x 8.0 THK WEBS", (39.0, 46.0, 38.0), offset=(28.0, 22.0))

    notices: list[str] = []
    doc = _render_sheet(sheet, index=1, count=1, label="NEMA23_BK12_BRACKET", warnings=notices)
    for n in notices:
        print("NOTICE:", n)

    fields = draw_fillable_ansi_b_titleblock(doc, sheet.width, sheet.height)
    _write_pdf([doc], [sheet], OUT_PDF)
    add_acroform_fields_to_pdf(OUT_PDF, fields)
    print(f"Wrote 11x17\" machinist drawing with {len(fields)} fillable fields: {OUT_PDF}")


if __name__ == "__main__":
    build_drawing()
