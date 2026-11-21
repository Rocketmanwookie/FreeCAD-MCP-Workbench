"""Qt Command classes for the FreeCAD MCP Workbench menu & toolbar.

Defines seven toolbar/menu entries with 64x64 SVG icons from Resources/icons/:
- Start RPC Server
- Stop RPC Server
- Auto-Start Server (checkable)
- Remote Connections (checkable)
- Configure Allowed IPs
- Set Auth Token
- AI Client Setup Guide (in-FreeCAD dialog for Codex, Claude, Antigravity, Cursor)
"""

import os
import shutil
import FreeCAD
import FreeCADGui
from PySide import QtWidgets
from typing import Any

from rpc_server.ip_filter import validate_allowed_ips
from rpc_server.settings import load_settings, save_settings

_WORKBENCH_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ICONS_DIR = os.path.join(_WORKBENCH_DIR, "Resources", "icons")


def _icon_path(filename: str) -> str:
    path = os.path.join(_ICONS_DIR, filename)
    return path if os.path.isfile(path) else ""


def _report_server_command(message: str, error: bool = False) -> None:
    """Show command feedback even when the Report View is closed."""
    printer = FreeCAD.Console.PrintError if error else FreeCAD.Console.PrintMessage
    printer(message + "\n")
    try:
        FreeCADGui.getMainWindow().statusBar().showMessage(message, 15000)
    except Exception:
        pass


def _persist_settings(settings: dict[str, Any]) -> bool:
    try:
        save_settings(settings)
    except Exception as exc:
        _report_server_command(f"Settings were not saved: {exc}", error=True)
        return False
    return True


class StartRPCServerCommand:
    def GetResources(self):
        return {
            "Pixmap": _icon_path("StartRPCServer.svg"),
            "MenuText": "Start RPC Server",
            "ToolTip": "Start the FreeCAD MCP XML-RPC server on port 9875",
        }

    def Activated(self, checked: int = 0) -> None:
        try:
            from . import rpc_server
            msg = rpc_server.start_rpc_server()
        except Exception as exc:
            _report_server_command(f"RPC Server failed to start: {type(exc).__name__}: {exc}", error=True)
            return
        _report_server_command(msg)

    def IsActive(self):
        return True


class StopRPCServerCommand:
    def GetResources(self):
        return {
            "Pixmap": _icon_path("StopRPCServer.svg"),
            "MenuText": "Stop RPC Server",
            "ToolTip": "Stop the running FreeCAD MCP XML-RPC server",
        }

    def Activated(self, checked: int = 0) -> None:
        try:
            from . import rpc_server
            msg = rpc_server.stop_rpc_server()
        except Exception as exc:
            _report_server_command(f"RPC Server failed to stop: {type(exc).__name__}: {exc}", error=True)
            return
        _report_server_command(msg)

    def IsActive(self):
        return True


class ToggleRemoteConnectionsCommand:
    def GetResources(self):
        settings = load_settings()
        return {
            "Pixmap": _icon_path("RemoteAccess.svg"),
            "MenuText": "Remote Connections",
            "ToolTip": "Enable or disable remote connections for the RPC server.",
            "Checkable": bool(settings.get("remote_enabled", False)),
        }

    def Activated(self, checked=0):
        from . import rpc_server
        settings = load_settings()
        settings["remote_enabled"] = bool(checked)
        if not _persist_settings(settings):
            return

        if settings["remote_enabled"]:
            allowed_ips = settings.get("allowed_ips", "127.0.0.1")
            FreeCAD.Console.PrintMessage(
                f"Remote connections enabled. Allowed IPs: {allowed_ips}\n"
            )
            if not settings.get("auth_token", ""):
                FreeCAD.Console.PrintWarning(
                    "Remote connections have no auth token configured — anyone on "
                    "an allowed IP can execute code in FreeCAD. Set one via "
                    "'Set Auth Token' in the FreeCAD MCP menu.\n"
                )
        else:
            FreeCAD.Console.PrintMessage("Remote connections disabled.\n")

        if rpc_server.rpc_server_instance:
            FreeCAD.Console.PrintMessage(
                "Restart the RPC server for changes to take effect.\n"
            )

    def IsActive(self):
        return True


class ConfigureAllowedIPsCommand:
    def GetResources(self):
        return {
            "Pixmap": _icon_path("AllowedIPs.svg"),
            "MenuText": "Configure Allowed IPs",
            "ToolTip": "Set which IP addresses or subnets are allowed to connect to the RPC server.",
        }

    def Activated(self):
        from . import rpc_server
        settings = load_settings()
        current_ips = settings.get("allowed_ips", "127.0.0.1")
        text, ok = QtWidgets.QInputDialog.getText(
            None,
            "Allowed IP Addresses",
            "Enter allowed IP addresses or subnets (comma-separated):\n"
            "Examples: 127.0.0.1, 192.168.1.0/24, 10.0.0.5",
            QtWidgets.QLineEdit.Normal,
            current_ips,
        )
        if ok and text.strip():
            valid, errors = validate_allowed_ips(text.strip())
            if errors:
                QtWidgets.QMessageBox.warning(
                    None,
                    "Invalid IP Configuration",
                    "The following errors were found:\n\n"
                    + "\n".join(f"• {e}" for e in errors)
                    + ("\n\nOnly valid entries will be saved."
                       if valid else "\n\nNo valid entries found. Settings not changed."),
                )
            if not valid:
                FreeCAD.Console.PrintWarning("Allowed IPs not changed — no valid entries.\n")
                return
            normalised = ", ".join(valid)
            settings["allowed_ips"] = normalised
            if not _persist_settings(settings):
                return
            FreeCAD.Console.PrintMessage(f"Allowed IPs updated to: {normalised}\n")
            if rpc_server.rpc_server_instance:
                FreeCAD.Console.PrintMessage(
                    "Restart the RPC server for changes to take effect.\n"
                )
        else:
            FreeCAD.Console.PrintMessage("Allowed IPs not changed.\n")

    def IsActive(self):
        return True


class SetAuthTokenCommand:
    def GetResources(self):
        return {
            "Pixmap": _icon_path("AuthToken.svg"),
            "MenuText": "Set Auth Token",
            "ToolTip": "Set the shared-secret token clients must present to connect. Blank disables authentication.",
        }

    def Activated(self):
        from . import rpc_server
        settings = load_settings()
        current = settings.get("auth_token", "")
        text, ok = QtWidgets.QInputDialog.getText(
            None,
            "Auth Token",
            "Enter the auth token clients must present (leave blank to disable\n"
            "authentication). The MCP server passes it via --auth-token or the\n"
            "FREECAD_MCP_TOKEN environment variable.",
            QtWidgets.QLineEdit.Normal,
            current,
        )
        if not ok:
            FreeCAD.Console.PrintMessage("Auth token not changed.\n")
            return
        settings["auth_token"] = text.strip()
        if not _persist_settings(settings):
            return
        if settings["auth_token"]:
            FreeCAD.Console.PrintMessage("Auth token set — clients must authenticate.\n")
        else:
            FreeCAD.Console.PrintMessage("Auth token cleared — authentication disabled.\n")
        if rpc_server.rpc_server_instance:
            FreeCAD.Console.PrintMessage(
                "Restart the RPC server for changes to take effect.\n"
            )

    def IsActive(self):
        return True


class ToggleAutoStartCommand:
    def GetResources(self):
        settings = load_settings()
        return {
            "Pixmap": _icon_path("AutoStartRPC.svg"),
            "MenuText": "Auto-Start Server",
            "ToolTip": "Automatically start the RPC server when FreeCAD launches.",
            "Checkable": bool(settings.get("auto_start_rpc", False)),
        }

    def Activated(self, checked=0):
        settings = load_settings()
        settings["auto_start_rpc"] = bool(checked)
        if not _persist_settings(settings):
            return

        if settings["auto_start_rpc"]:
            FreeCAD.Console.PrintMessage(
                "MCP RPC server will start automatically on next FreeCAD launch.\n"
            )
        else:
            FreeCAD.Console.PrintMessage("MCP RPC server auto-start disabled.\n")

    def IsActive(self):
        return True


class ShowClientSetupCommand:
    """In-FreeCAD dialog displaying copy-ready configs for Codex, Claude, Antigravity & Cursor."""

    def GetResources(self):
        return {
            "Pixmap": _icon_path("ClientSetup.svg"),
            "MenuText": "AI Client Setup",
            "ToolTip": "Show ready-to-copy MCP configuration snippets for Codex, Claude, Antigravity, and Cursor.",
        }

    def Activated(self):
        uvx_bin = shutil.which("uvx") or "uvx"
        setup_script = os.path.join(_WORKBENCH_DIR, "scripts", "setup_mcp_clients.py")

        guide = (
            "FreeCAD MCP Server — AI Client Setup Guide\n"
            "===========================================\n\n"
            "1. Start the RPC server in FreeCAD (Green Play button) and enable 'Auto-Start Server'.\n"
            "2. Ensure 'uv' / 'uvx' is installed: https://docs.astral.sh/uv/\n\n"
            f"ONE-COMMAND AUTO-SETUP (Codex, Claude Code, Claude Desktop, Antigravity, Cursor):\n"
            f"  python3 \"{setup_script}\" --all\n\n"
            "--- CODEX (~/.codex/config.toml) ---\n"
            f"  codex mcp add freecad -- {uvx_bin} freecad-mcp\n\n"
            "  [mcp_servers.freecad]\n"
            f"  command = \"{uvx_bin}\"\n"
            "  args = [\"freecad-mcp\"]\n\n"
            "--- ANTIGRAVITY (~/.gemini/config/mcp_config.json) ---\n"
            "  {\n"
            "    \"mcpServers\": {\n"
            "      \"freeCAD\": {\n"
            f"        \"command\": \"{uvx_bin}\",\n"
            "        \"args\": [\"freecad-mcp\"]\n"
            "      }\n"
            "    }\n"
            "  }\n\n"
            "--- CLAUDE CODE (~/.claude.json) & CLAUDE DESKTOP ---\n"
            f"  claude mcp add --scope user freecad -- {uvx_bin} freecad-mcp\n\n"
            "  {\n"
            "    \"mcpServers\": {\n"
            "      \"freecad\": {\n"
            f"        \"command\": \"{uvx_bin}\",\n"
            "        \"args\": [\"freecad-mcp\"]\n"
            "      }\n"
            "    }\n"
            "  }\n\n"
            "--- OFFLINE / LOCAL REPO DEPLOYMENT ---\n"
            f"  Use args: [\"--from\", \"{_WORKBENCH_DIR}\", \"freecad-mcp\"]\n"
            "  (Add \"--only-text-feedback\" to args to omit viewport screenshots.)\n"
        )

        dlg = QtWidgets.QDialog(FreeCADGui.getMainWindow())
        dlg.setWindowTitle("FreeCAD MCP — AI Client Setup")
        dlg.resize(700, 520)
        layout = QtWidgets.QVBoxLayout(dlg)

        text_box = QtWidgets.QPlainTextEdit()
        text_box.setReadOnly(True)
        text_box.setPlainText(guide)
        layout.addWidget(text_box)

        btn_row = QtWidgets.QHBoxLayout()
        copy_btn = QtWidgets.QPushButton("Copy All to Clipboard")
        copy_btn.clicked.connect(lambda: QtWidgets.QApplication.clipboard().setText(guide))
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(dlg.accept)
        btn_row.addWidget(copy_btn)
        btn_row.addStretch()
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

        dlg.exec_()

    def IsActive(self):
        return True


def register_commands() -> None:
    FreeCADGui.addCommand("Start_RPC_Server", StartRPCServerCommand())
    FreeCADGui.addCommand("Stop_RPC_Server", StopRPCServerCommand())
    FreeCADGui.addCommand("Toggle_Auto_Start", ToggleAutoStartCommand())
    FreeCADGui.addCommand("Toggle_Remote_Connections", ToggleRemoteConnectionsCommand())
    FreeCADGui.addCommand("Configure_Allowed_IPs", ConfigureAllowedIPsCommand())
    FreeCADGui.addCommand("Set_Auth_Token", SetAuthTokenCommand())
    FreeCADGui.addCommand("Show_Client_Setup", ShowClientSetupCommand())


def schedule_toggle_sync() -> None:
    """Compatibility no-op; toggle state is initialized by ``GetResources``."""
