# Copyright 2026 Zyvor AI Labs · https://zyvor.dev
# SPDX-License-Identifier: Apache-2.0
"""Colored command output and an indeterminate progress spinner.

Plain text when stdout is not a terminal or NO_COLOR is set, so logs and
tests keep the same words.
"""

from __future__ import annotations

import os
import re
import sys
from collections.abc import Callable, Iterator
from contextlib import contextmanager

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

_GRADE = {
    "A": "bold green",
    "B": "green",
    "C": "yellow",
    "D": "yellow",
    "F": "bold red",
}
_SEVERITY = {
    "critical": "bold red",
    "high": "red",
    "medium": "yellow",
    "low": "green",
    "info": "cyan",
}


def _no_color() -> bool:
    return bool(os.environ.get("NO_COLOR"))


def _console(*, err: bool = False) -> Console:
    no_color = _no_color()
    return Console(
        stderr=err,
        highlight=False,
        soft_wrap=True,
        no_color=True if no_color else None,
        force_terminal=False if no_color else None,
    )


def _live(console: Console) -> bool:
    return bool(console.is_terminal) and not _no_color()


def style_for(text: str, *, err: bool = False) -> str | None:
    """Rich style for a status line. None means leave the default color."""
    if err or text.startswith(("Error", "Pipeline error", "NL parsing failed", "Test generation failed")):
        return "bold red"
    if text.lower().startswith("warning"):
        return "yellow"
    if text.startswith(("Results:", "Result:", "Partial results:")):
        failed = re.search(r"(\d+)\s+failed", text)
        if failed and int(failed.group(1)) > 0:
            return "bold yellow"
        ratio = re.search(r"(\d+)/(\d+)", text)
        if ratio:
            passed_n, total_n = int(ratio.group(1)), int(ratio.group(2))
            return "bold yellow" if passed_n < total_n else "bold green"
        return "bold green"
    grade = re.search(r"Grade:\s*([A-F])\b", text)
    if grade:
        return _GRADE.get(grade.group(1), "bold")
    severity = re.search(r"\[(critical|high|medium|low|info)\]", text, re.I)
    if severity:
        return _SEVERITY.get(severity.group(1).lower(), "yellow")
    if "[gap]" in text:
        return "yellow"
    if text.startswith(
        ("Report:", "PDF report:", "HAR file:", "Journey video:", "Trace", "Session saved", "PoC:")
    ):
        return "cyan"
    if re.fullmatch(r"argus \S+", text.strip()):
        return "bold #c4b5fd"
    if any(mark in text for mark in ("✓", "✅", "VERIFIED")) and "not verified" not in text:
        return "green"
    if any(mark in text for mark in ("✗", "❌")) or text.startswith("not verified"):
        return "red"
    if "⚠" in text:
        return "yellow"
    if text.startswith(("Running", "Starting", "Creating", "Generating", "Sweep")):
        return "bold cyan"
    if re.search(r"\b(failing|flaky)\b", text):
        return "yellow"
    if re.search(r"\bhealthy\b", text):
        return "green"
    return None


def echo(message: object = "", *, err: bool = False, nl: bool = True, **_ignored: object) -> None:
    """Print one status line. ``err`` goes to stderr, same as ``typer.echo``."""
    text = "" if message is None else str(message)
    console = _console(err=err)
    end = "\n" if nl else ""
    if not _live(console):
        file = sys.stderr if err else sys.stdout
        print(text, file=file, end=end)
        return
    console.print(text, style=style_for(text, err=err) or "", markup=False, highlight=False, end=end)


@contextmanager
def spin(message: str) -> Iterator[Callable[[str], None]]:
    """Indeterminate spinner. The yielded function updates the label.

    Not a terminal: each update is one plain line, and the block is silent
    if the label never changes.
    """
    console = _console()
    current = {"text": message}

    if not _live(console):
        printed: set[str] = set()

        def plain(update: str) -> None:
            if update not in printed:
                printed.add(update)
                print(update, file=sys.stdout)

        plain(message)
        yield plain
        return

    progress = Progress(
        SpinnerColumn("bouncingBar", style="bold cyan"),
        TextColumn("[bold cyan]{task.description}"),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    )
    task_id = progress.add_task(message, total=None)

    def live(update: str) -> None:
        current["text"] = update
        progress.update(task_id, description=update)

    progress.start()
    try:
        yield live
    finally:
        progress.stop()
