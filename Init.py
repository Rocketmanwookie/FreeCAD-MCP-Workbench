"""FreeCAD MCP Workbench — headless & GUI module initialization (Init.py).

Executed by FreeCAD on startup in both GUI and console (freecadcmd) modes.
Ensures the workbench root directory is importable for rpc_server helpers.
"""

import inspect
import os
import sys

try:
    _MOD_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    _MOD_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

if _MOD_DIR not in sys.path:
    sys.path.insert(0, _MOD_DIR)
