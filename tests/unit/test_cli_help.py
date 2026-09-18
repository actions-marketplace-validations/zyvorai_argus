# Copyright 2026 Zyvor AI Labs · https://zyvor.dev
# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-Argus-Commercial
"""CLI help: wordmark, command groups, and plain output under NO_COLOR."""

from __future__ import annotations

import re
from importlib.metadata import PackageNotFoundError

from typer.testing import CliRunner

from orchestrator import cli
from orchestrator.cli_theme import BANNER_ART, SUBCOMMAND_PANELS, TAGLINE

runner = CliRunner()

_ANSI = re.compile(r"\x1b\[[0-9;]*m")


def _plain(text: str) -> str:
    return _ANSI.sub("", text)


def test_root_help_has_wordmark_and_groups() -> None:
    result = runner.invoke(cli.app, ["--help"])
    assert result.exit_code == 0, result.output
    out = _plain(result.stdout)
    for line in BANNER_ART.splitlines():
        assert line.rstrip() in out
    assert TAGLINE in out
    assert out.index("Operate") < out.index("Testing") < out.index("Security") < out.index("Watch")
    for name in (
        "serve",
        "version",
        "test",
        "flow",
        "vision",
        "api",
        "guard",
        "redteam",
        "watch",
        "intel",
        "ask",
    ):
        assert re.search(rf"(?m)^[^\n]*\b{name}\b", out), name


def test_subcommand_help_panels() -> None:
    for parent, panels in SUBCOMMAND_PANELS.items():
        result = runner.invoke(cli.app, [parent, "--help"])
        assert result.exit_code == 0, result.output
        out = _plain(result.stdout)
        assert BANNER_ART.splitlines()[0] not in out
        for command, panel in panels.items():
            assert panel in out, parent
            assert re.search(rf"\b{re.escape(command)}\b", out), f"{parent} {command}"


def test_no_color_still_lists_commands(monkeypatch) -> None:
    monkeypatch.setenv("NO_COLOR", "1")
    result = runner.invoke(cli.app, ["--help"])
    assert result.exit_code == 0, result.output
    assert "\x1b[" not in result.stdout
    out = result.stdout
    assert "Operate" in out
    assert "serve" in out
    assert "guard" in out


def test_legacy_help_is_unbranded() -> None:
    result = runner.invoke(cli.legacy_app, ["--help"])
    assert result.exit_code == 0, result.output
    out = _plain(result.stdout)
    assert BANNER_ART.splitlines()[0] not in out
    assert "deprecated" in out


def test_version_prints_installed_version() -> None:
    result = runner.invoke(cli.app, ["version"])
    assert result.exit_code == 0, result.output
    assert result.stdout.startswith("argus ")
    assert result.stdout.strip() != "argus unknown"


def test_version_unknown_when_package_missing(monkeypatch) -> None:
    def _missing(_name: str) -> str:
        raise PackageNotFoundError

    monkeypatch.setattr("importlib.metadata.version", _missing)
    result = runner.invoke(cli.app, ["version"])
    assert result.exit_code == 0, result.output
    assert result.stdout.strip() == "argus unknown"
