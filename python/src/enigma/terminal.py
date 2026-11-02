"""Acentos de terminal con la paleta Enigma y texto de contraste fijo."""

import os
import re
import shutil
import sys

PALETTE = {
    "magenta": (201, 0, 104),  # #C90068
    "blue": (0, 3, 201),  # #0003C9
    "green": (0, 201, 98),  # #00C962
    "yellow": (201, 198, 0),  # #C9C600
}


def _windows_ansi() -> bool:
    """Activa secuencias VT en la consola de este proceso, si están disponibles."""
    import ctypes
    from ctypes import wintypes

    try:
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.GetStdHandle.argtypes = [wintypes.DWORD]
        kernel.GetStdHandle.restype = wintypes.HANDLE
        kernel.GetConsoleMode.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
        kernel.GetConsoleMode.restype = wintypes.BOOL
        kernel.SetConsoleMode.argtypes = [wintypes.HANDLE, wintypes.DWORD]
        kernel.SetConsoleMode.restype = wintypes.BOOL
        handle = kernel.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = wintypes.DWORD()
        if not kernel.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        return bool(kernel.SetConsoleMode(handle, mode.value | 0x0004))
    except OSError, AttributeError:
        return False


def badge(text: str, color: str) -> str:
    # Mantener legibles los archivos de salida, terminales sin color y lectores
    # que solicitan explícitamente texto sin formato mediante NO_COLOR.
    if "NO_COLOR" in os.environ or os.environ.get("TERM") == "dumb" or not sys.stdout.isatty():
        return text
    if os.name == "nt" and not _windows_ansi():
        return text
    background = ";".join(map(str, PALETTE[color]))
    foreground = "0;0;0" if color in {"green", "yellow"} else "255;255;255"
    return f"\033[38;2;{foreground}m\033[48;2;{background}m{text}\033[0m"


def frame(lines: list[str], width: int = 56) -> str:
    """Enmarca el menú sin contar los códigos de color como caracteres visibles."""
    visible = [re.sub(r"\x1b\[[0-9;]*m", "", line) for line in lines]
    width = max(width, max(map(len, visible), default=0))
    if shutil.get_terminal_size().columns < width + 4:
        return "\n".join(lines)
    try:
        "╭╮╰╯─│".encode(sys.stdout.encoding or "utf-8")
        top_left, top_right, bottom_left, bottom_right, horizontal, vertical = "╭╮╰╯─│"
    except UnicodeEncodeError, LookupError:
        top_left = top_right = bottom_left = bottom_right = "+"
        horizontal, vertical = "-", "|"
    top = f"{top_left}{horizontal * (width + 2)}{top_right}"
    rows = [
        f"{vertical} {line}{' ' * (width - len(plain))} {vertical}"
        for line, plain in zip(lines, visible, strict=True)
    ]
    bottom = f"{bottom_left}{horizontal * (width + 2)}{bottom_right}"
    return "\n".join([top, *rows, bottom])


def section(title: str, color: str) -> str:
    width = min(48, max(12, shutil.get_terminal_size().columns - 2))
    return f"\n{badge(f' {title} ', color)}\n{'-' * width}"
