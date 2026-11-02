from pathlib import Path
from unittest.mock import Mock

import pytest

from enigma import dialogs
from enigma.errors import OperationCancelled, ValidationError


@pytest.fixture
def native_dialogs(monkeypatch):
    import tkinter as tk
    from tkinter import filedialog

    root = Mock()
    monkeypatch.setattr(tk, "Tk", lambda: root)
    return root, filedialog


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


def test_desktop_failure_is_controlled(monkeypatch):
    import tkinter as tk

    def no_display():
        raise tk.TclError("sin pantalla")

    monkeypatch.setattr(tk, "Tk", no_display)
    with pytest.raises(ValidationError, match="sesión de escritorio"):
        dialogs.choose_path("Abrir")
