#!/usr/bin/env python3
"""Cross-platform installer for FreeCAD MCP across AI coding assistants.

Configures the FreeCAD MCP server and installs the reusable `freecad-mcp`
workflow skill (`skills/freecad-mcp/SKILL.md`) for:
  - Antigravity (`~/.gemini/config/mcp_config.json` + `~/.gemini/config/skills/`)
  - Codex       (`~/.codex/config.toml` + `~/.codex/skills/`)
  - Claude Code (`~/.claude.json` + `~/.claude/skills/`)
  - Claude Desktop (OS-specific `claude_desktop_config.json`)
  - Cursor      (`~/.cursor/mcp.json`)

Usage:
  python3 scripts/setup_mcp_clients.py --all
  python3 scripts/setup_mcp_clients.py --clients codex claude-code antigravity --dry-run
  python3 scripts/setup_mcp_clients.py --all --from-local-repo
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_SRC = REPO_ROOT / "skills" / "freecad-mcp"


def resolve_uvx() -> str:
    found = shutil.which("uvx")
    if found:
        return found
    for candidate in (
        Path.home() / ".local" / "bin" / "uvx",
        Path.home() / ".cargo" / "bin" / "uvx",
        Path.home() / ".local" / "share" / "mise" / "installs" / "uv" / "latest" / ".mise-bins" / "uvx",
    ):
        if candidate.exists():
            return str(candidate)
    return "uvx"


def build_args(from_local_repo: bool, only_text_feedback: bool) -> list[str]:
    args: list[str] = []
    if from_local_repo:
        args.extend(["--from", str(REPO_ROOT)])
    args.append("freecad-mcp")
    if only_text_feedback:
        args.append("--only-text-feedback")
    return args


def claude_desktop_config_path() -> Path:
    system = platform.system()
    if system == "Darwin":
        return Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"
    if system == "Windows":
        appdata = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
        return appdata / "Claude" / "claude_desktop_config.json"
    return Path.home() / ".config" / "Claude" / "claude_desktop_config.json"


def update_json_mcp(path: Path, server_name: str, command: str, args: list[str], dry_run: bool) -> None:
    data: dict = {}
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
    servers = data.setdefault("mcpServers", {})
    servers[server_name] = {"command": command, "args": args}
    if dry_run:
        print(f"[dry-run] Would write {server_name!r} to {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"[ok] Updated {path} with MCP server {server_name!r}")


def update_codex_toml(path: Path, command: str, args: list[str], dry_run: bool) -> None:
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    args_toml = ", ".join(json.dumps(a) for a in args)
    block = (
        "[mcp_servers.freecad]\n"
        f"command = {json.dumps(command)}\n"
        f"args = [{args_toml}]\n"
    )
    pattern = re.compile(r"(?ms)^\[mcp_servers\.freecad\]\n.*?(?=^\[|\Z)")
    if pattern.search(existing):
        updated = pattern.sub(block + "\n", existing)
    else:
        sep = "\n" if existing and not existing.endswith("\n\n") else ""
        updated = existing + sep + block
    if dry_run:
        print(f"[dry-run] Would update [mcp_servers.freecad] in {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(updated, encoding="utf-8")
    print(f"[ok] Updated {path} with [mcp_servers.freecad]")


def install_skill(dest_dir: Path, dry_run: bool) -> None:
    target = dest_dir / "freecad-mcp"
    if dry_run:
        print(f"[dry-run] Would install skill to {target}")
        return
    dest_dir.mkdir(parents=True, exist_ok=True)
    if target.is_symlink() or target.exists():
        if target.is_symlink():
            target.unlink()
        else:
            shutil.rmtree(target)
    try:
        target.symlink_to(SKILL_SRC, target_is_directory=True)
        print(f"[ok] Symlinked skill {target} -> {SKILL_SRC}")
    except OSError:
        shutil.copytree(SKILL_SRC, target)
        print(f"[ok] Copied skill to {target}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Configure FreeCAD MCP across AI coding assistants.")
    parser.add_argument(
        "--clients",
        nargs="+",
        choices=["antigravity", "codex", "claude-code", "claude-desktop", "cursor"],
        help="Specific clients to configure.",
    )
    parser.add_argument("--all", action="store_true", help="Configure all supported clients.")
    parser.add_argument(
        "--from-local-repo",
        action="store_true",
        help="Run the MCP server directly from this local repository via `uvx --from <repo> freecad-mcp`.",
    )
    parser.add_argument(
        "--only-text-feedback",
        action="store_true",
        help="Pass --only-text-feedback to disable automatic viewport screenshots.",
    )
    parser.add_argument("--no-skill", action="store_true", help="Skip installing the freecad-mcp SKILL.md.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned changes without modifying files.")
    args = parser.parse_args()

    selected = (
        ["antigravity", "codex", "claude-code", "claude-desktop", "cursor"]
        if args.all
        else (args.clients or [])
    )
    if not selected:
        parser.print_help()
        return 1

    uvx = resolve_uvx()
    mcp_args = build_args(args.from_local_repo, args.only_text_feedback)
    home = Path.home()

    print(f"Using uvx: {uvx}")
    print(f"MCP args:  {mcp_args}\n")

    if "antigravity" in selected:
        update_json_mcp(home / ".gemini" / "config" / "mcp_config.json", "freeCAD", uvx, mcp_args, args.dry_run)
        if not args.no_skill:
            install_skill(home / ".gemini" / "config" / "skills", args.dry_run)

    if "codex" in selected:
        update_codex_toml(home / ".codex" / "config.toml", uvx, mcp_args, args.dry_run)
        if not args.no_skill:
            install_skill(home / ".codex" / "skills", args.dry_run)

    if "claude-code" in selected:
        update_json_mcp(home / ".claude.json", "freecad", uvx, mcp_args, args.dry_run)
        if not args.no_skill:
            install_skill(home / ".claude" / "skills", args.dry_run)

    if "claude-desktop" in selected:
        update_json_mcp(claude_desktop_config_path(), "freecad", uvx, mcp_args, args.dry_run)

    if "cursor" in selected:
        update_json_mcp(home / ".cursor" / "mcp.json", "freecad", uvx, mcp_args, args.dry_run)

    print("\nDone! Restart your AI client(s) and make sure FreeCAD's MCP RPC server is running.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
