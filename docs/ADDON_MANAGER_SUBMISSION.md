# Distributing & Submitting to the FreeCAD Addon Manager

This repository conforms to the official [FreeCAD Workbench Creation](https://wiki.freecad.org/Workbench_creation), [FreeCAD Package Metadata](https://wiki.freecad.org/Package_Metadata), and [FreeCAD Addon Manifest Schema (`v1.6`, Format 1)](https://github.com/FreeCAD/Addon-Manifest-Schema) standards so users can install it **directly inside FreeCAD**.

---

## 1. Install Immediately Inside FreeCAD via Custom Repository URL (No PR Needed)

Anyone on another computer can install this workbench straight from FreeCAD's Addon Manager right now:

1. Open FreeCAD → **Edit → Preferences → Addon Manager**.
2. Under **Custom Repositories**, click **+** and enter:
   - **Repository URL:** `https://github.com/Rocketmanwookie/FreeCAD-MCP-Workbench`
   - **Branch:** `main`
3. Click **OK**, then open **Tools → Addon Manager**.
4. Search for **FreeCAD MCP Workbench** and click **Install**.
5. Restart FreeCAD → switch to the **FreeCAD MCP** workbench in the workbench dropdown.

---

## 2. Submit to the Official FreeCAD 1.0+ Addon Index (`FreeCAD/Addons`)

FreeCAD 1.0+ / 1.1 sources its built-in Addon Manager catalog from **`FreeCAD/Addons`** (`Data/Index.json`) rather than the legacy pre-1.0 `FreeCAD/FreeCAD-addons` repository (see the [FreeCAD Addon Academy Publishing Guide](https://freecad.github.io/Addon-Academy/Guides/Publishing/Indexed)):

1. Fork [https://github.com/FreeCAD/Addons](https://github.com/FreeCAD/Addons).
2. Open `Data/Index.json` and insert the following entry in alphabetical order:
   ```json
   "FreeCAD-MCP-Workbench": [
     {
       "repository": "https://github.com/Rocketmanwookie/FreeCAD-MCP-Workbench",
       "git_ref": "main",
       "branch_display_name": "main",
       "freecad_min": "0.21.0",
       "zip_url": "https://github.com/Rocketmanwookie/FreeCAD-MCP-Workbench/archive/refs/heads/main.zip",
       "curated": false
     }
   ],
   ```
3. Commit, push to your fork, and open a Pull Request against `FreeCAD/Addons`.

*(If you also want visibility in legacy pre-1.0 FreeCAD versions, you can optionally submit a `.gitmodules` PR to the legacy [`FreeCAD/FreeCAD-addons`](https://github.com/FreeCAD/FreeCAD-addons) repository.)*

---

## 3. Version Lock Note (`package.xml` vs PyPI `freecad-mcp`)

- Keep `<version>` in `package.xml` (`0.1.32`) in sync with `pyproject.toml` and the PyPI `freecad-mcp` release so `get_rpc_status` reports `"version_check": "ok"` when users launch the MCP server via `uvx freecad-mcp`.
- Only bump `<version>` in `package.xml` when updating the bundled `rpc_server/` & `src/freecad_mcp/` server together (or when deploying exclusively from this repo via `uvx --from <repo> freecad-mcp`).

---

## 4. Local Validation Checklist

Validate `package.xml` anytime against both the official XSD schema and FreeCAD's parser:

```bash
# 1. Validate against official FreeCAD Addon-Manifest-Schema (v1.6, Format 1)
curl -fsSL https://github.com/FreeCAD/Addon-Manifest-Schema/releases/download/v1.6/Schema.xsd -o /tmp/fc_schema.xsd
xmllint --noout --schema /tmp/fc_schema.xsd package.xml

# 2. Validate with FreeCAD's Addon Manager Developer Tools
#    FreeCAD -> Edit -> Preferences -> Addon Manager -> enable Addon developer mode
#    Tools -> Addon Manager -> Developer tools... -> point to this repo
```

### FreeCAD Workbench Standards Checklist
- [x] `Init.py` at workbench root (console + GUI module path setup)
- [x] `InitGui.py` at workbench root defining `class FreeCADMCPWorkbench(Workbench)` with `MenuText`, `ToolTip`, `Icon`, `Initialize()`, `Activated()`, `Deactivated()`, `ContextMenu()`, `GetClassName()`, and `Gui.addWorkbench(FreeCADMCPWorkbench())`
- [x] `Resources/icons/FreeCADMCPWorkbench.svg` (64×64 vector SVG workbench icon) + 64×64 SVG command icons for all 7 toolbar actions
- [x] `package.xml` (`format="1"`, validated via `xmllint` against `FreeCAD/Addon-Manifest-Schema` `v1.6` and FreeCAD 1.1.4 `FreeCAD.Metadata` / `MetadataReader`) with `<classname>`, `<subdirectory>./</subdirectory>`, `<icon>`, `<author>`, `<maintainer>`, `<freecadmin>`, `<pythonmin>`, `<license>`, and ≥3 tags
- [x] `LICENSE` (MIT), `README.md`, and deployable `pyproject.toml` (`freecad-mcp` console script)
