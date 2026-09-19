# Copyright 2026 Zyvor AI Labs · https://zyvor.dev
# SPDX-License-Identifier: LicenseRef-Zyvor-Production-1.0
"""Cilium-style help: wordmark, colors, and human-readable command groups."""

from __future__ import annotations

import os

import typer
from rich.console import Console
from rich.text import Text
from typer import _click as typer_click
from typer.main import get_command_name
from typer.models import CommandInfo, TyperInfo

# Figlet "slant" ARGUS — the same kind of wordmark Cilium prints above help.
# Printed unwrapped, before Rich help, so the art is not reflowed. No brackets,
# so Rich markup cannot eat the logo.
BANNER_ART = r"""
    ___    ____  ________  _______
   /   |  / __ \/ ____/ / / / ___/
  / /| | / /_/ / / __/ / / /\__ \
 / ___ |/ _, _/ /_/ / /_/ /___/ /
/_/  |_/_/ |_|\____/\____//____/
""".strip("\n")

TAGLINE = "Zyvor Argus — autonomous testing, security, and monitoring"

# Root panels, in the order they should appear. Commands are listed before
# groups by Typer, so Operate (serve, version) leads; group order below
# puts Testing, then Security, then Watch.
ROOT_GROUP_ORDER = (
    "test",
    "flow",
    "vision",
    "api",
    "guard",
    "redteam",
    "watch",
    "intel",
    "ask",
)

ROOT_COMMAND_PANELS = {
    "serve": "Operate",
    "version": "Operate",
}

ROOT_GROUP_PANELS = {
    "test": "Testing",
    "flow": "Testing",
    "vision": "Testing",
    "api": "Testing",
    "guard": "Security",
    "redteam": "Security",
    "watch": "Watch",
    "intel": "Watch",
    "ask": "Watch",
}

# Every subcommand must be listed. apply_theme fails import if one is missing.
SUBCOMMAND_PANELS: dict[str, dict[str, str]] = {
    "test": {
        "run": "Run",
        "exec": "Run",
        "generate": "Author",
        "create": "Author",
        "import-codegen": "Author",
        "discover": "Discover",
    },
    "flow": {
        "run": "Journeys",
        "realtime": "Journeys",
    },
    "vision": {
        "regression": "Visual",
        "route-sweep": "Visual",
    },
    "api": {
        "test": "Contracts",
        "ai-test": "Contracts",
        "auth-test": "Contracts",
        "har-replay": "Contracts",
    },
    "watch": {
        "vitals": "Monitors",
        "audit": "Monitors",
    },
    "guard": {
        "misconfig-scan": "Scan",
        "cve-lookup": "Scan",
        "port-scan": "Scan",
        "tls-cipher-scan": "Scan",
        "dast-scan": "Scan",
        "injection-scan": "Scan",
        "csrf-probe": "Scan",
        "ssrf-probe": "Scan",
        "auth-attack-scan": "Scan",
        "idor-scan": "Scan",
        "exploit-poc": "Attack",
        "attack-chain": "Attack",
        "host-pentest": "Attack",
        "cloud-pentest": "Attack",
        "pr-gate": "Gate",
    },
    "redteam": {
        "llm": "Red team",
    },
    "ask": {
        "ingest": "Knowledge",
        "evaluate": "Knowledge",
    },
    "intel": {
        "health": "Health",
        "select": "Health",
        "quarantine-add": "Quarantine",
        "quarantine-list": "Quarantine",
        "quarantine-release": "Quarantine",
    },
}

_LOGO_STYLES = ("#ddd6fe", "#c4b5fd", "#a78bfa", "#8b5cf6", "#7c3aed")


_STYLES_INSTALLED = False


def install_styles() -> None:
    """Recolor Typer's Rich help. Safe to call more than once.

    Typer forces a color terminal when ``GITHUB_ACTIONS`` is set, which
    defeats ``NO_COLOR``. Help rendering checks the variable itself so
    pipes and CI stay plain.
    """
    global _STYLES_INSTALLED
    from typer import rich_utils

    rich_utils.STYLE_OPTION = "bold cyan"
    rich_utils.STYLE_SWITCH = "bold bright_green"
    rich_utils.STYLE_USAGE = "bold #c4b5fd"
    rich_utils.STYLE_USAGE_COMMAND = "bold cyan"
    rich_utils.STYLE_HELPTEXT_FIRST_LINE = "bold"
    rich_utils.STYLE_COMMANDS_PANEL_BORDER = "#7c3aed"
    rich_utils.STYLE_OPTIONS_PANEL_BORDER = "cyan"
    rich_utils.STYLE_COMMANDS_TABLE_FIRST_COLUMN = "bold cyan"
    rich_utils.STYLE_REQUIRED_SHORT = "bold #c4b5fd"
    if _STYLES_INSTALLED:
        return
    original = rich_utils._get_rich_console

    def _get_rich_console(stderr: bool = False):
        if not os.environ.get("NO_COLOR"):
            return original(stderr=stderr)
        saved = (rich_utils.COLOR_SYSTEM, rich_utils.FORCE_TERMINAL)
        rich_utils.COLOR_SYSTEM = None
        rich_utils.FORCE_TERMINAL = False
        try:
            return original(stderr=stderr)
        finally:
            rich_utils.COLOR_SYSTEM, rich_utils.FORCE_TERMINAL = saved

    rich_utils._get_rich_console = _get_rich_console
    _STYLES_INSTALLED = True


def print_banner() -> None:
    """Print the wordmark. Color is off when stdout is not a TTY or NO_COLOR is set."""
    no_color = bool(os.environ.get("NO_COLOR"))
    console = Console(
        highlight=False,
        no_color=True if no_color else None,
        force_terminal=False if no_color else None,
    )
    logo = Text(no_wrap=True, overflow="ignore")
    for index, line in enumerate(BANNER_ART.splitlines()):
        if index:
            logo.append("\n")
        logo.append(line, style=f"bold {_LOGO_STYLES[index % len(_LOGO_STYLES)]}")
    console.print(logo, crop=False, overflow="ignore", no_wrap=True)
    console.print(Text(TAGLINE, style="italic #c4b5fd"))
    console.print()


class ArgusTyperGroup(typer.core.TyperGroup):
    """Root Click group: wordmark, then Typer's grouped Rich help."""

    def format_help(self, ctx: typer_click.Context, formatter: typer_click.HelpFormatter) -> None:
        print_banner()
        super().format_help(ctx, formatter)


def apply_theme(app: typer.Typer) -> None:
    """Assign help panels and group order. Does not touch the legacy CLI."""
    install_styles()
    _assign_panels(
        app.registered_commands,
        ROOT_COMMAND_PANELS,
        label="argus",
    )
    by_name = {info.name: info for info in app.registered_groups}
    missing_groups = [name for name in ROOT_GROUP_PANELS if name not in by_name]
    extra_groups = [name for name in by_name if name not in ROOT_GROUP_PANELS]
    if missing_groups or extra_groups:
        raise RuntimeError(
            f"argus group panel map out of date: missing={missing_groups} extra={extra_groups}"
        )
    ordered: list[TyperInfo] = []
    for name in ROOT_GROUP_ORDER:
        info = by_name[name]
        info.rich_help_panel = ROOT_GROUP_PANELS[name]
        child = info.typer_instance
        if child is not None:
            _assign_panels(
                child.registered_commands,
                SUBCOMMAND_PANELS[name],
                label=f"argus {name}",
            )
        ordered.append(info)
    app.registered_groups = ordered


def _command_name(info: CommandInfo) -> str:
    if info.name:
        return info.name
    if info.callback is None:
        return ""
    return get_command_name(info.callback.__name__)


def _assign_panels(
    commands: list[CommandInfo],
    panels: dict[str, str],
    *,
    label: str,
) -> None:
    found = {_command_name(info): info for info in commands}
    missing = [name for name in panels if name not in found]
    extra = [name for name in found if name not in panels]
    if missing or extra:
        raise RuntimeError(f"{label} panel map out of date: missing={missing} extra={extra}")
    for name, panel in panels.items():
        found[name].rich_help_panel = panel
