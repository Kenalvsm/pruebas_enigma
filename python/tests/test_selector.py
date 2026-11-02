import io
import sys
from contextlib import nullcontext
from types import SimpleNamespace

import pytest

from enigma import cli, selector
from enigma.errors import OperationCancelled


class Screen(io.StringIO):
    def isatty(self):
        return True


@pytest.fixture
def screen(monkeypatch):
    screen = Screen()
    monkeypatch.setattr(selector, "sys", SimpleNamespace(stdout=screen, stdin=Screen()))
    monkeypatch.setattr(selector, "_keyboard", nullcontext)
    monkeypatch.setattr(selector, "_windows_ansi", lambda: True)
    monkeypatch.delenv("TERM", raising=False)
    return screen


@pytest.mark.parametrize(
    ("keys", "expected"),
    [
        (["enter"], "a"),
        (["down", "enter"], "b"),
        (["up", "enter"], "c"),
        (["down", "down", "down", "enter"], "a"),
        (["end", "home", "enter"], "a"),
        (["end", "enter"], "c"),
        (["", "down", "enter"], "b"),
    ],
)
def test_navigation_and_cursor_restored(screen, monkeypatch, keys, expected):
    keys = iter(keys)
    monkeypatch.setattr(selector, "_read_key", lambda: next(keys))
    assert (
        selector.select_option("Operación", [("a", "Abrir"), ("b", "Guardar"), ("c", "Salir")])
        == expected
    )
    assert screen.getvalue().endswith("\x1b[?25h")


def test_escape_cancels_submenu(screen, monkeypatch):
    monkeypatch.setattr(selector, "_read_key", lambda: "escape")
    with pytest.raises(OperationCancelled):
        selector.select_option("Origen", [("a", "Texto")])
    assert screen.getvalue().endswith("\x1b[?25h")


def test_escape_exits_main_menu(screen, monkeypatch):
    monkeypatch.setattr(selector, "_read_key", lambda: "escape")
    assert selector.select_option("Menú", [("a", "Abrir")], cancel_value="exit") == "exit"


def test_interrupt_restores_cursor(screen, monkeypatch):
    def interrupt():
        raise KeyboardInterrupt

    monkeypatch.setattr(selector, "_read_key", interrupt)
    with pytest.raises(KeyboardInterrupt):
        selector.select_option("Menú", [("a", "Abrir")], render=lambda index: "ENIGMA")
    assert screen.getvalue().endswith("\x1b[?25h")


def test_redirected_input_does_not_loop(monkeypatch):
    monkeypatch.setattr(selector.sys, "stdin", io.StringIO())
    with pytest.raises(selector.TerminalUnavailable):
        selector.select_option("Menú", [("a", "Abrir")])


def test_unsupported_terminal_is_controlled(screen, monkeypatch):
    monkeypatch.setenv("TERM", "dumb")
    with pytest.raises(selector.TerminalUnavailable):
        selector.select_option("Menú", [("a", "Abrir")])


@pytest.mark.parametrize(
    ("characters", "key"),
    [
        (["\xe0", "H"], "up"),
        (["\x00", "P"], "down"),
        (["\xe0", "G"], "home"),
        (["\xe0", "O"], "end"),
        (["\r"], "enter"),
        (["\x1b"], "escape"),
        (["1"], ""),
    ],
)
def test_windows_keyboard_decodes_navigation(monkeypatch, characters, key):
    characters = iter(characters)
    monkeypatch.setitem(sys.modules, "msvcrt", SimpleNamespace(getwch=lambda: next(characters)))
    assert selector._read_windows_key() == key


@pytest.mark.parametrize("character", ["", "\x03"])
def test_keyboard_eof_and_interrupt(character):
    with pytest.raises((EOFError, KeyboardInterrupt)):
        selector._decode_key(character)


def test_main_menu_marks_selected_operation():
    screen = cli._menu(2)
    assert "> Cifrar archivo AES" in screen
    assert "> Cifrar Vigenère" not in screen
    assert "Enter: elegir" in screen


def test_cli_unavailable_terminal_exits(monkeypatch, capsys):
    def unavailable(*args, **kwargs):
        raise selector.TerminalUnavailable("Abre una terminal interactiva.")

    monkeypatch.setattr(cli, "select_option", unavailable)
    assert cli.main([]) == 1
    assert "terminal interactiva" in capsys.readouterr().out
