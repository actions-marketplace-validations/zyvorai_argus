# Copyright 2026 Zyvor AI Labs · https://zyvor.dev
# SPDX-License-Identifier: LicenseRef-Zyvor-Production-1.0
"""Colored status lines stay plain when color is off, and the spinner does not hang."""

from __future__ import annotations

from orchestrator import cli_ui as ui


def test_echo_is_plain_without_a_tty(capsys, monkeypatch) -> None:
    monkeypatch.setenv("NO_COLOR", "1")
    ui.echo("Results: 2 passed, 1 failed, 3 total")
    ui.echo("[gap] page /pricing — Pricing")
    ui.echo("Error: boom", err=True)
    captured = capsys.readouterr()
    assert captured.out == "Results: 2 passed, 1 failed, 3 total\n[gap] page /pricing — Pricing\n"
    assert captured.err == "Error: boom\n"
    assert "\x1b[" not in captured.out
    assert "\x1b[" not in captured.err


def test_cards_cover_headlines_and_leave_detail_lines_alone() -> None:
    assert ui.card_for("Results: 2 passed, 1 failed, 3 total") is not None
    assert ui.card_for("Grade: A (96/100) — 0 failing, 1 warning checks") is not None
    assert ui.card_for("argus 0.9.2") is not None
    assert ui.card_for("Report: reports/qa.html") is not None
    assert ui.card_for("Error: boom", err=True) is not None
    assert ui.card_for("[gap] page /pricing — Pricing") is None
    assert ui.style_for("Results: 1 passed, 0 failed, 1 total") == "bold green"
    assert ui.style_for("Results: 1 passed, 2 failed, 3 total") == "bold yellow"
    assert ui.style_for("Result: 1/2 steps passed") == "bold yellow"
    assert ui.style_for("Result: 2/2 steps passed") == "bold green"
    assert ui.style_for("Grade: A (90/100)") == "bold green"
    assert ui.style_for("Grade: F (10/100)") == "bold red"
    assert ui.style_for("  [high] missing header") == "red"
    assert ui.style_for("  [gap] route / — Home") == "yellow"
    assert ui.style_for("Error: no", err=True) == "bold red"
    assert ui.style_for("argus 0.9.2") == "bold #c4b5fd"
    assert ui.style_for("Report: reports/out.html") == "cyan"


def test_spin_prints_a_plain_label_when_not_a_tty(capsys) -> None:
    seen = []
    with ui.spin("Running QA pipeline") as tick:
        tick("Fetching requirements")
        seen.append("inside")
    assert seen == ["inside"]
    out = capsys.readouterr().out
    assert "Running QA pipeline" in out
    assert "Fetching requirements" in out
    assert "\x1b[" not in out
