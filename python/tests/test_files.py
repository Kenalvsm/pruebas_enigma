import errno
import os
from pathlib import Path

import pytest

from enigma import files
from enigma.errors import ValidationError


def test_text_preserves_utf8_bom_and_line_endings(tmp_path):
    source = tmp_path / "entrada.TXT"
    data = b"\xef\xbb\xbfEspa\xc3\xb1ol\r\nsiguiente\n"
    source.write_bytes(data)
    target = tmp_path / "salida.txt"
    assert files.write_text(target, files.read_text(source)) == target
    assert target.read_bytes() == data
    assert source.read_bytes() == data


def test_invalid_inputs_and_destinations(tmp_path):
    with pytest.raises(FileNotFoundError):
        files.input_file(tmp_path / "ausente")
    with pytest.raises(ValidationError, match="regular"):
        files.input_file(tmp_path)
    binary = tmp_path / "entrada.bin"
    binary.write_bytes(b"abc")
    with pytest.raises(ValidationError, match="UTF-8"):
        files.read_text(binary)
    with pytest.raises(ValidationError, match=".txt"):
        files.write_text(binary, "no reemplazar")
    with pytest.raises(ValidationError, match="carpeta"):
        files.write_text(tmp_path / "no-existe" / "salida.txt", "texto")
    bad_utf8 = tmp_path / "incorrecto.txt"
    bad_utf8.write_bytes(b"\xff")
    with pytest.raises(UnicodeDecodeError):
        files.read_text(bad_utf8)


def test_existing_destination_never_overwritten(tmp_path):
    target = tmp_path / "salida.txt"
    target.write_text("original")
    with pytest.raises(FileExistsError):
        files.write_text(target, "cambio")
    assert target.read_text() == "original"


def test_destination_created_by_another_process(tmp_path):
    target = tmp_path / "salida.txt"
    with pytest.raises(FileExistsError), files.atomic_output(target) as output:
        output.write(b"nuestro contenido")
        target.write_bytes(b"otro proceso")
    assert target.read_bytes() == b"otro proceso"
    assert list(tmp_path.glob("*.part")) == []


@pytest.mark.parametrize("error", [OSError(errno.ENOSPC, "Disco lleno"), PermissionError("Acceso")])
def test_publish_error_leaves_no_output_or_temporary(tmp_path, monkeypatch, error):
    target = tmp_path / "salida.txt"

    def fail(*args):
        raise error

    monkeypatch.setattr(files.os, "link", fail)
    with pytest.raises(OSError):
        files.write_text(target, "contenido")
    assert not target.exists()
    assert list(tmp_path.iterdir()) == []


def test_fsync_disk_full_cleanup(tmp_path, monkeypatch):
    def fail(*args):
        raise OSError(errno.ENOSPC, "Disco lleno")

    monkeypatch.setattr(files.os, "fsync", fail)
    with pytest.raises(OSError):
        files.write_text(tmp_path / "salida.txt", "contenido")
    assert list(tmp_path.iterdir()) == []


def test_interrupted_write_cleanup(tmp_path):
    with pytest.raises(KeyboardInterrupt), files.atomic_output(tmp_path / "salida") as output:
        output.write(b"parcial")
        raise KeyboardInterrupt
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("foto.png.enc", "foto.recuperado.png"),
        ("copia.ENC", "copia.recuperado"),
        ("renombrado", "renombrado.recuperado"),
        (".enc", "archivo.recuperado"),
        ("datos.bin", "datos.recuperado.bin"),
    ],
)
def test_suggested_name(source, expected):
    assert files.suggested_decrypted_path(Path(source)) == Path(expected)


@pytest.mark.skipif(os.name == "nt", reason="En Windows crear symlinks necesita privilegios.")
def test_dangling_symlink_not_replaced(tmp_path):
    target = tmp_path / "salida"
    target.symlink_to(tmp_path / "ausente")
    with pytest.raises(FileExistsError):
        files.new_destination(target)
    assert target.is_symlink()
