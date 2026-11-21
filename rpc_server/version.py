"""Addon version reported to the MCP server through get_rpc_status."""

from pathlib import Path
import xml.etree.ElementTree as ET


def _read_version() -> str:
    """Read the metadata version from package.xml regardless of XML namespace."""
    metadata = Path(__file__).resolve().parents[1] / "package.xml"
    root = ET.parse(metadata).getroot()
    for elem in root:
        tag = elem.tag.rsplit("}", 1)[-1]
        if tag == "version" and elem.text and elem.text.strip():
            return elem.text.strip()
    raise ValueError(f"Missing addon version in {metadata}")


__version__ = _read_version()

# Bump when the RPC contract changes in a way the MCP server must know about:
# a method or parameter is added or removed, or a response shape changes.
# Must match PROTOCOL_VERSION in src/freecad_mcp/version.py.
PROTOCOL_VERSION = 3
