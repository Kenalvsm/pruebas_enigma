"""Selección por teclado con flechas y Enter, sin dependencias externas."""

import os
import re
import shutil
import sys
from collections.abc import Callable, Iterator
from contextlib import contextmanager

from enigma.errors import OperationCancelled, ValidationError
from enigma.terminal import _windows_ansi, badge, frame


class TerminalUnavailable(ValidationError):
    """El selector requiere entrada interactiva y control de cursor."""


@contextmanager
def _keyboard() -> Iterator[None]:
    if os.name == "nt":
        yield
        return
    import termios
    import tty

    descriptor = sys.stdin.fileno()
    previous = termios.tcgetattr(descriptor)
    try:
        tty.setcbreak(descriptor)
        yield
    finally:
        termios.tcsetattr(descriptor, termios.TCSADRAIN, previous)


def _read_windows_key() -> str:
    import msvcrt

    character = msvcrt.getwch()
    if character in {"\x00", "\xe0"}:
        return {"H": "up", "P": "down", "G": "home", "O": "end"}.get(msvcrt.getwch(), "")
    return _decode_key(character)


def _read_posix_key() -> str:
    import select

    descriptor = sys.stdin.fileno()
    raw = os.read(descriptor, 1)
    if not raw:
        raise EOFError
    character = raw.decode("ascii", errors="ignore")
    if not character:
        return ""
    if character == "\x1b" and select.select([descriptor], [], [], 0.05)[0]:
        prefix = os.read(descriptor, 1)
        if prefix in {b"[", b"O"} and select.select([descriptor], [], [], 0.05)[0]:
            key = os.read(descriptor, 1)
            return {b"A": "up", b"B": "down", b"H": "home", b"F": "end"}.get(key, "")
        return ""
    return _decode_key(character)


def _decode_key(character: str) -> str:
    if character == "\x03":
        raise KeyboardInterrupt
    if character in {"\r", "\n"}:
        return "enter"
    if character == "\x1b":
        return "escape"
    if not character:
        raise EOFError
    return {"k": "up", "j": "down"}.get(character, "")


def _read_key() -> str:
    return _read_windows_key() if os.name == "nt" else _read_posix_key()


def _row_count(text: str) -> int:
    columns = max(1, shutil.get_terminal_size().columns)
    lines = re.sub(r"\x1b\[[0-9;]*m", "", text).split("\n")
    return sum(max(1, (len(line) + columns - 1) // columns) for line in lines)


def select_option(
    title: str,
    choices: list[tuple[str, str]],
    *,
    render: Callable[[int], str] | None = None,
    cancel_value: str | None = None,
) -> str:
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise TerminalUnavailable(
            "El selector necesita una terminal interactiva. Abre iniciar_enigma.bat "
            "o ejecuta python -m enigma en una terminal."
        )
    if os.environ.get("TERM") == "dumb" or (os.name == "nt" and not _windows_ansi()):
        raise TerminalUnavailable(
            "Esta terminal no permite mover el selector. Usa Windows Terminal "
            "en Windows o una terminal con soporte ANSI en Linux."
        )

    selected = 0
    previous_rows = 0
    try:
        with _keyboard():
            sys.stdout.write("\x1b[?25l")
            while True:
                screen = render(selected) if render is not None else ""
                if not screen or _row_count(screen) > shutil.get_terminal_size().lines - 1:
                    rows = [badge(f" {title} ", "blue"), ""]
                    rows.extend(
                        badge(f"> {label}", "green") if index == selected else f"  {label}"
                        for index, (_, label) in enumerate(choices)
                    )
                    rows.extend(["", "Arriba/Abajo: mover | Enter: elegir | Esc: volver"])
                    screen = frame(rows)
                if previous_rows:
                    sys.stdout.write(f"\x1b[{previous_rows}A\r\x1b[J")
                sys.stdout.write(screen + "\n")
                sys.stdout.flush()
                previous_rows = _row_count(screen)
                key = _read_key()
                if key == "enter":
                    return choices[selected][0]
                if key == "escape":
                    if cancel_value is not None:
                        return cancel_value
                    raise OperationCancelled
                if key == "up":
                    selected = (selected - 1) % len(choices)
                elif key == "down":
                    selected = (selected + 1) % len(choices)
                elif key == "home":
                    selected = 0
                elif key == "end":
                    selected = len(choices) - 1
    finally:
        sys.stdout.write("\x1b[?25h")
        sys.stdout.flush()
