---
name: freecad-mcp
description: Design, inspect, modify, export, and run FEA on parametric 3D CAD models directly inside a live FreeCAD window using the FreeCAD MCP server (`freecad` / `freeCAD`). Use when the user asks to build, edit, inspect, or simulate a model in FreeCAD (as opposed to build123d/text-to-cad or kernelcad).
metadata:
  short-description: Build and inspect 3D CAD models in FreeCAD via MCP
---

# FreeCAD MCP Workflow

Use the **`freecad`** (Codex/Claude: `mcp__freecad`) or **`freeCAD`** (Antigravity) MCP server tools to drive the user's running FreeCAD instance. In clients with deferred MCP tools (such as Codex), load/search the `mcp__freecad` tool namespace before starting.

## 1. Preflight & Connection Check

1. Call `get_rpc_status` first. It bypasses the GUI thread and confirms the FreeCAD RPC bridge (`127.0.0.1:9875`) is healthy and not stuck.
   - If unreachable, ask the user to open FreeCAD, switch to the **MCP Addon** workbench, and click **Start RPC Server**.
   - If `state` is `stuck`, tell the user FreeCAD needs a restart before retrying.
2. Call `list_documents` to see what is already open. Create a fresh document with `create_document` unless modifying an existing one.
3. **Stamp document attribution:** Whenever creating or building a part via the MCP server, set `doc.CreatedBy = "FreeCAD MCP Server (freecad-mcp)"` so FreeCAD's **File → Project Information → Created by** clearly records that the MCP server generated it.

## 2. Choose the Right Execution Tool

- **`execute_code`** (primary modeling tool): Runs FreeCAD Python (`FreeCAD`/`App`, `FreeCADGui`/`Gui`, `Part`, `PartDesign`, `Draft`, `Sketcher`) on the GUI thread against the live document. Prefer this over chaining many `create_object` calls for non-trivial geometry.
- **`create_object` / `edit_object` / `delete_object`**: Good for simple primitives, quick property tweaks, and creating `Fem::*` objects.
- **`execute_code_headless` + `reload_document`**: Use for heavy or crash-prone OpenCascade operations (helical threads with `makeHelix`/`makePipeShell`, complex lofts/sweeps, heavy B-spline booleans). Run the script headless to write the `.FCStd` file, then call `reload_document` to display it in the GUI.
- **`execute_code_async` + `get_async_status`**: ONLY for long pure-Python computations that do **not** touch the GUI or mutate the FreeCAD document tree.
- **Timeouts**: If a GUI tool times out, call `get_task_status` before retrying—a `timed_out_running` task may still finish mutating the document.

> **Token discipline:** Pass `include_screenshot: false` on intermediate `execute_code`, `create_object`, `edit_object`, `delete_object`, `get_object`, and `get_objects` calls. Take targeted screenshots with `get_view` at key milestones instead.

## 3. Modeling Best Practices in FreeCAD Python

1. **Organize assemblies cleanly:**
   - Group related parts with `doc.addObject("App::DocumentObjectGroup", "GroupName")` or `App::Part`.
   - Give every object a descriptive `Label` and distinct `ViewObject.ShapeColor` (RGB tuple of `0.0–1.0` floats) so sub-components are easy to distinguish in screenshots.
2. **Build parametrically & verify geometry in code:**
   - Define key dimensions as named constants at the top of the script (FreeCAD uses **millimeters**).
   - Call `doc.recompute()` after creating or modifying features.
   - Check `obj.Shape.isValid()`, `obj.Shape.Solids`, and `obj.Shape.BoundBox` in Python to catch empty booleans, inverted normals, or misaligned coordinates before rendering.
   - Wrap fragile fillets/chamfers in `try/except` or apply them after verifying the base boolean solid.
3. **Avoid re-creating duplicates on iteration:**
   - When re-running a build script, either remove and recreate named objects cleanly or update existing objects so stale geometry doesn't overlap.
4. **Standard parts & FEA:**
   - Use `get_parts_list` and `insert_part_from_library` for standard library fasteners/hardware when available.
   - For structural stress/deflection checks, set up geometry + `Fem::AnalysisPython` + material + mesh + constraints, then run `run_fem_analysis` (CalculiX).

## 4. Visual Verification Loop (Required Before Finishing)

After building or making major edits, visually inspect the model with `get_view`:

1. Call `Gui.SendMsgToActiveView("ViewFit")` (inside `execute_code` if needed) so the entire model is framed cleanly.
2. Capture screenshots with `get_view` across multiple angles (`"Isometric"`, `"Front"`, `"Top"`, `"Right"`, and `"Back"`/`"Left"`/`"Bottom"` as needed).
3. Inspect each view for:
   - Floating or disconnected parts
   - Unintended intersections / clipping
   - Wrong orientation, scale, or symmetry
   - Missing details requested by the user
4. Fix any visual defects and re-verify with `get_view` until clean.

## 5. Saving & Exporting

Save the native project and export deliverables via `execute_code` when requested (defaulting to a sensible path like `~/Projects/<name>/` if the user didn't specify one):

```python
import os, Part

out_dir = os.path.expanduser("~/Projects/my_model")
os.makedirs(out_dir, exist_ok=True)
doc = FreeCAD.ActiveDocument
doc.recompute()
doc.saveAs(os.path.join(out_dir, "model.FCStd"))

# Export STEP (CAD exchange / CNC)
shapes = [o for o in doc.Objects if hasattr(o, "Shape") and not o.Shape.isNull() and o.ViewObject.Visibility]
Part.export(shapes, os.path.join(out_dir, "model.step"))

# Export STL (3D printing)
# import Mesh
# Mesh.export(shapes, os.path.join(out_dir, "model.stl"))
```

Always report the saved file paths, key final dimensions, and any assumptions made.
