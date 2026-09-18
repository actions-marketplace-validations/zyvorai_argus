# Copyright 2026 Zyvor AI Labs · https://zyvor.dev
# SPDX-License-Identifier: AGPL-3.0-only OR LicenseRef-Argus-Commercial
"""Colored command output and a branded progress bar.

Plain text when stdout is not a terminal or NO_COLOR is set, so logs and
tests keep the same words.
"""

from __future__ import annotations

import os
import re
import sys
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager

from rich.console import Console, Group, RenderableType
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

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


def _metric(label: str, value: str, style: str) -> Text:
    block = Text()
    block.append(f"{value}\n", style=style)
    block.append(label, style="dim")
    return block


def card_for(text: str, *, err: bool = False) -> RenderableType | None:
    """A panel for headline lines. None means print the line as styled text."""
    if err or text.startswith(("Error", "Pipeline error", "NL parsing failed", "Test generation failed")):
        return Panel(
            Text(text, style="bold"),
            title="[bold red]failed[/]",
            title_align="left",
            border_style="red",
            padding=(0, 1),
            expand=False,
        )

    steps = re.fullmatch(r"Result:\s*(\d+)/(\d+)\s+steps passed", text.strip())
    if steps:
        passed_n, total_n = int(steps.group(1)), int(steps.group(2))
        bad = passed_n < total_n
        grid = Table.grid(padding=(0, 2))
        grid.add_row(
            _metric("passed", steps.group(1), "bold green" if not bad else "bold yellow"),
            _metric("steps", steps.group(2), "bold #c4b5fd"),
        )
        return Panel(
            grid,
            title="[bold yellow]journey[/]" if bad else "[bold green]journey[/]",
            title_align="left",
            border_style="yellow" if bad else "green",
            padding=(0, 1),
            expand=False,
        )

    results = re.fullmatch(
        r"Results:\s*(\d+)\s+passed,\s*(\d+)\s+failed(?:,\s*(\d+)\s+total)?",
        text.strip(),
    )
    if results:
        passed, failed = results.group(1), results.group(2)
        total = results.group(3) or str(int(passed) + int(failed))
        bad = int(failed) > 0
        grid = Table.grid(padding=(0, 2))
        grid.add_row(
            _metric("passed", passed, "bold green"),
            _metric("failed", failed, "bold red" if bad else "dim"),
            _metric("total", total, "bold #c4b5fd"),
        )
        return Panel(
            grid,
            title="[bold red]argus[/]" if bad else "[bold green]argus[/]",
            title_align="left",
            border_style="red" if bad else "green",
            padding=(0, 1),
            expand=False,
        )

    grade = re.match(r"Grade:\s*([A-F])\s*\((\d+)/100\)\s*[—-]\s*(.*)", text.strip())
    if grade:
        letter, score, rest = grade.group(1), grade.group(2), grade.group(3)
        body = Text()
        body.append(f"  {letter}  ", style=_GRADE.get(letter, "bold"))
        body.append(f"{score}", style="bold")
        body.append("/100\n", style="dim")
        body.append(f"  {rest}", style="dim")
        return Panel(
            body,
            title="[bold #c4b5fd]grade[/]",
            title_align="left",
            border_style="#7c3aed",
            padding=(0, 1),
            expand=False,
        )

    if re.fullmatch(r"argus \S+", text.strip()):
        name, version = text.strip().split(" ", 1)
        body = Text()
        body.append(name, style="bold #c4b5fd")
        body.append("  ")
        body.append(version, style="bold cyan")
        return Panel(body, border_style="#7c3aed", padding=(0, 1), expand=False)

    path = re.match(
        r"(Report|PDF report|HAR file|Journey video|Trace|Session saved as|PoC):\s*(.*)",
        text.strip(),
    )
    if path:
        body = Text()
        body.append(path.group(1), style="bold cyan")
        body.append("  ")
        body.append(path.group(2).strip(), style="#e9d5ff")
        return Panel(body, border_style="cyan", padding=(0, 1), expand=False)
    return None


def _stream_line(text: str, *, err: bool) -> Text:
    style = style_for(text, err=err) or ""
    line = Text()
    line.append("▌ ", style="bold red" if err else "bold #7c3aed")
    line.append(text, style=style)
    return line


def echo(message: object = "", *, err: bool = False, nl: bool = True, **_ignored: object) -> None:
    """Print one status line. ``err`` goes to stderr, same as ``typer.echo``."""
    text = "" if message is None else str(message)
    console = _console(err=err)
    end = "\n" if nl else ""
    if not _live(console):
        file = sys.stderr if err else sys.stdout
        print(text, file=file, end=end)
        return
    card = card_for(text, err=err)
    if card is not None and nl:
        console.print(card)
        return
    console.print(_stream_line(text, err=err), markup=False, highlight=False, end=end)


class _JobView:
    """Branded indeterminate bar. Mutate ``message``; Live redraws it."""

    def __init__(self, message: str) -> None:
        self.message = message
        self.started = time.monotonic()

    def __rich__(self) -> Panel:
        elapsed = time.monotonic() - self.started
        width, span = 32, 7
        travel = width - span
        cycle = travel * 2
        phase = int(elapsed * 18) % cycle
        pos = phase if phase <= travel else cycle - phase
        bar = Text()
        bar.append("━" * pos, style="#4c1d95")
        bar.append("━" * span, style="bold #e9d5ff")
        bar.append("━" * (width - span - pos), style="#2e1065")
        clock = Text(f"{elapsed:5.1f}s", style="dim")
        title = Text()
        title.append("argus", style="bold #c4b5fd")
        title.append("  ")
        title.append(self.message, style="bold")
        return Panel(
            Group(title, bar, clock),
            border_style="#7c3aed",
            padding=(0, 1),
            expand=False,
        )


@contextmanager
def spin(message: str) -> Iterator[Callable[[str], None]]:
    """Indeterminate progress bar. The yielded function updates the label.

    Not a terminal: each distinct label is one plain line.
    """
    console = _console()

    if not _live(console):
        printed: set[str] = set()

        def plain(update: str) -> None:
            if update not in printed:
                printed.add(update)
                print(update, file=sys.stdout)

        plain(message)
        yield plain
        return

    view = _JobView(message)

    def live(update: str) -> None:
        view.message = update

    with Live(view, console=console, refresh_per_second=16, transient=True):
        yield live
