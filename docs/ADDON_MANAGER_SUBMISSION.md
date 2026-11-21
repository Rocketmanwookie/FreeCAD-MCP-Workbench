# Distributing & Submitting to the FreeCAD Addon Manager

This repository follows the official [FreeCAD Workbench Creation](https://wiki.freecad.org/Workbench_creation) and [FreeCAD Package Metadata](https://wiki.freecad.org/Package_Metadata) standards so users can install it **directly inside FreeCAD**.

---

## 1. Before Pushing to GitHub

Replace `YOUR_USERNAME` with your GitHub username in:
- `package.xml` (`<url type="repository">`, `<url type="bugtracker">`, `<url type="readme">`, `<url type="documentation">`)
- `pyproject.toml` (`[project.urls]`)
- `README.md`

Then push to GitHub on the `main` branch:
```bash
git remote add origin https://github.com/YOUR_USERNAME/FreeCAD-MCP-Workbench.git
git push -u origin main
```

---

## 2. Install Immediately Inside FreeCAD via Custom Repository URL (No PR Needed)

Anyone on another computer can add this workbench directly inside FreeCAD's Addon Manager without waiting for an upstream PR:

1. Open FreeCAD → **Edit → Preferences → Addon Manager**.
2. Under **Custom Repositories**, click **+** and enter:
   - **Repository URL:** `https://github.com/YOUR_USERNAME/FreeCAD-MCP-Workbench`
   - **Branch:** `main`
3. Click **OK**, then open **Tools → Addon Manager**.
4. Search for **FreeCAD MCP Workbench** and click **Install**.
5. Restart FreeCAD → switch to the **FreeCAD MCP** workbench in the workbench dropdown.

---

## 3. Validate Locally with FreeCAD's Addon Manager Developer Tools

Before submitting to the official FreeCAD Addons catalog:

1. Open FreeCAD → **Edit → Preferences → Addon Manager** and enable **Addon developer mode**.
2. Open **Tools → Addon Manager → Developer tools...**.
3. Point it at your local clone of `FreeCAD-MCP-Workbench`.
4. Confirm `package.xml` validates cleanly:
   - `<name>FreeCAD MCP Workbench</name>`
   - `<classname>FreeCADMCPWorkbench</classname>` matches `InitGui.py`
   - `<subdirectory>./</subdirectory>` resolves `Init.py` and `InitGui.py` at the root
   - `<icon>Resources/icons/FreeCADMCPWorkbench.svg</icon>` renders cleanly

---

## 4. Submit to the Official FreeCAD Workbench List (`FreeCAD-addons`)

To make **FreeCAD MCP Workbench** appear by default in FreeCAD's built-in Addon Manager for every FreeCAD user:

1. Fork [https://github.com/FreeCAD/FreeCAD-addons](https://github.com/FreeCAD/FreeCAD-addons).
2. Clone your fork and add this repository as a submodule (or edit `.gitmodules` in alphabetical order):
   ```bash
   git submodule add -b main https://github.com/YOUR_USERNAME/FreeCAD-MCP-Workbench.git FreeCAD-MCP-Workbench
   ```
3. Commit and push to your fork:
   ```bash
   git commit -m "Add FreeCAD-MCP-Workbench"
   git push origin master
   ```
4. Open a Pull Request against `FreeCAD/FreeCAD-addons`. The FreeCAD Addon Manager CI bot automatically validates `package.xml`, `LICENSE`, `README.md`, and `Resources/icons/FreeCADMCPWorkbench.svg`.

---

## 5. FreeCAD Workbench Standards Checklist

This repo satisfies every item from [wiki.freecad.org/Workbench_creation](https://wiki.freecad.org/Workbench_creation):

- [x] `Init.py` at workbench root (console + GUI module path setup)
- [x] `InitGui.py` at workbench root defining `class FreeCADMCPWorkbench(Workbench)` with `MenuText`, `ToolTip`, `Icon`, `Initialize()`, `Activated()`, `Deactivated()`, `ContextMenu()`, `GetClassName()`, and `Gui.addWorkbench(FreeCADMCPWorkbench())`
- [x] `Resources/icons/FreeCADMCPWorkbench.svg` (64×64 vector SVG workbench icon) + 64×64 SVG command icons for all 7 toolbar actions
- [x] `package.xml` (`format="1"`, `xmlns="https://wiki.freecad.org/Package_Metadata"`) with matching `<classname>`, `<subdirectory>./</subdirectory>`, `<icon>`, `<license>`, and `<tag>` metadata
- [x] `LICENSE` (MIT), `README.md`, and deployable `pyproject.toml` (`freecad-mcp` console script)
