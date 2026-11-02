import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock

import pytest

from enigma import dialogs
from enigma.errors import OperationCancelled


@pytest.fixture
def native_dialogs(monkeypatch):
    tk = ModuleType("tkinter")
    native = ModuleType("tkinter.filedialog")
    tk.TclError = type("TclError", (Exception,), {})
    root = Mock()
    tk.Tk = lambda: root
    native.askopenfilename = Mock()
    native.asksaveasfilename = Mock()
    tk.filedialog = native
    monkeypatch.setitem(sys.modules, "tkinter", tk)
    monkeypatch.setitem(sys.modules, "tkinter.filedialog", native)
    return root, native


def test_open_path_with_spaces(native_dialogs, monkeypatch, tmp_path):
    root, native = native_dialogs
    source = tmp_path / "carpeta con espacios" / "entrada.txt"
    monkeypatch.setattr(native, "askopenfilename", lambda **kwargs: str(source))
    assert dialogs.choose_path("Abrir", filetypes=dialogs.TEXT_FILES) == source
    root.destroy.assert_called_once()


def test_save_keeps_proposed_name_and_directory(native_dialogs, monkeypatch, tmp_path):
    root, native = native_dialogs
    destination = tmp_path / "foto.png.enc"
    save = Mock(return_value=str(destination))
    monkeypatch.setattr(native, "asksaveasfilename", save)
    assert (
        dialogs.choose_path("Guardar", save=True, default=destination, extension=".enc")
        == destination
    )
    assert save.call_args.kwargs["initialfile"] == "foto.png.enc"
    assert Path(save.call_args.kwargs["initialdir"]) == tmp_path
    root.destroy.assert_called_once()


@pytest.mark.parametrize("save", [False, True])
def test_cancel_closes_window(native_dialogs, monkeypatch, save):
    root, native = native_dialogs
    monkeypatch.setattr(native, "askopenfilename", lambda **kwargs: "")
    monkeypatch.setattr(native, "asksaveasfilename", lambda **kwargs: "")
    with pytest.raises(OperationCancelled):
        dialogs.choose_path("Seleccionar", save=save)
    root.destroy.assert_called_once()


def test_desktop_failure_uses_terminal(native_dialogs, monkeypatch, tmp_path):
    import tkinter as tk

    def no_display():
        raise tk.TclError("sin pantalla")

    monkeypatch.setattr(tk, "Tk", no_display)
    source = tmp_path / "entrada.txt"
    monkeypatch.setattr("builtins.input", lambda _: str(source))
    assert dialogs.choose_path("Abrir") == source


@pytest.mark.parametrize("save", [False, True])
def test_missing_tkinter_uses_terminal(monkeypatch, tmp_path, save):
    monkeypatch.setitem(sys.modules, "tkinter", None)
    source = tmp_path / "carpeta con espacios" / "entrada.txt"
    monkeypatch.setattr("builtins.input", lambda _: f'"{source}"')
    assert dialogs.choose_path("Seleccionar", save=save) == source


def test_terminal_save_adds_extension(monkeypatch, tmp_path):
    monkeypatch.setitem(sys.modules, "tkinter", None)
    destination = tmp_path / "salida"
    monkeypatch.setattr("builtins.input", lambda _: str(destination))
    assert dialogs.choose_path("Guardar", save=True, extension=".enc") == destination.with_suffix(
        ".enc"
    )


@pytest.mark.parametrize("value", ["", "  ", '""'])
def test_terminal_cancel(monkeypatch, value):
    monkeypatch.setitem(sys.modules, "tkinter", None)
    monkeypatch.setattr("builtins.input", lambda _: value)
    with pytest.raises(OperationCancelled):
        dialogs.choose_path("Abrir")
