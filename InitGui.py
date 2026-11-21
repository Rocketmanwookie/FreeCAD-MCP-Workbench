"""FreeCAD MCP Workbench — GUI workbench registration (InitGui.py).

Conforms to https://wiki.freecad.org/Workbench_creation and registers the
``FreeCADMCPWorkbench`` class referenced by ``package.xml``.
"""

import inspect as _inspect
import os as _os
import sys as _sys

try:
    _ADDON_DIR = _os.path.dirname(_os.path.abspath(__file__))
except NameError:
    _ADDON_DIR = _os.path.dirname(_os.path.abspath(_inspect.getfile(_inspect.currentframe())))

if _ADDON_DIR not in _sys.path:
    _sys.path.insert(0, _ADDON_DIR)


class FreeCADMCPWorkbench(Workbench):
    """FreeCAD Workbench exposing the Model Context Protocol (MCP) RPC bridge."""

    MenuText = "FreeCAD MCP"
    ToolTip = "Model Context Protocol (MCP) server workbench for AI-assisted CAD (Codex, Claude, Antigravity)"
    Icon = _os.path.join(_ADDON_DIR, "Resources", "icons", "FreeCADMCPWorkbench.svg")

    def Initialize(self):
        """Called once when the user first switches to this workbench."""
        from rpc_server import rpc_server  # noqa: F401 (registers GUI commands)

        self.command_list = [
            "Start_RPC_Server",
            "Stop_RPC_Server",
            "Toggle_Auto_Start",
            "Toggle_Remote_Connections",
            "Configure_Allowed_IPs",
            "Set_Auth_Token",
            "Show_Client_Setup",
        ]
        self.appendToolbar("FreeCAD MCP", self.command_list)
        self.appendMenu("FreeCAD MCP", self.command_list)

    def Activated(self):
        """Called every time the user activates this workbench."""
        pass

    def Deactivated(self):
        """Called every time the user leaves this workbench."""
        pass

    def ContextMenu(self, recipient):
        """Right-click context menu entries."""
        self.appendContextMenu("FreeCAD MCP", ["Start_RPC_Server", "Stop_RPC_Server", "Show_Client_Setup"])

    def GetClassName(self):
        return "Gui::PythonWorkbench"


Gui.addWorkbench(FreeCADMCPWorkbench())


def _auto_start_mcp():
    try:
        from rpc_server import rpc_server

        settings = rpc_server.load_settings()
        if not settings.get("auto_start_rpc", False):
            return

        msg = rpc_server.start_rpc_server()
        FreeCAD.Console.PrintMessage(f"[MCP] Auto-start: {msg}\n")
    except Exception as exc:
        FreeCAD.Console.PrintWarning(f"[MCP] Auto-start failed: {exc}\n")


from PySide import QtCore

QtCore.QTimer.singleShot(0, _auto_start_mcp)
