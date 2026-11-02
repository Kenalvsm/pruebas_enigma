"""Lectura y publicación de archivos nuevos sin reemplazar destinos existentes."""

import os
import stat
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager, suppress
from pathlib import Path
from typing import BinaryIO

from enigma.errors import ValidationError


def input_file(path: str | Path) -> Path:
    source = Path(path).expanduser()
    if not stat.S_ISREG(source.stat().st_mode):
        raise ValidationError("El origen debe ser un archivo regular.")
    return source


def new_destination(path: str | Path) -> Path:
    destination = Path(path).expanduser().absolute()
    # lexists también detecta enlaces simbólicos cuyo destino ya no existe.
    if os.path.lexists(destination):
        raise FileExistsError(f"El destino ya existe: {destination}. Elige otro nombre.")
    if not destination.parent.is_dir():
        raise ValidationError("La carpeta de destino no existe.")
    return destination


@contextmanager
def atomic_output(path: str | Path) -> Iterator[BinaryIO]:
    """Publica con un enlace duro atómico que falla si otro proceso creó el destino.

    El temporal se crea en el mismo volumen y se cierra antes de publicarse.
    No hay fallback a replace/rename que pueda sobrescribir en POSIX.
    """
    destination = new_destination(path)
    descriptor, name = tempfile.mkstemp(prefix=".enigma-", suffix=".part", dir=destination.parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            yield stream
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, destination)
    finally:
        # No ocultar el error original si el sistema impide limpiar el temporal.
        with suppress(OSError):
            temporary.unlink()


def read_text(path: str | Path) -> str:
    source = input_file(path)
    if source.suffix.lower() != ".txt":
        raise ValidationError("Vigenère requiere un archivo .txt en UTF-8.")
    # No normalizar CRLF ni eliminar BOM: se preserva todo el texto original.
    return source.read_bytes().decode("utf-8")


def write_text(path: str | Path, text: str) -> Path:
    destination = Path(path).expanduser()
    if destination.suffix.lower() != ".txt":
        raise ValidationError("El resultado Vigenère debe guardarse como .txt.")
    data = text.encode("utf-8")
    with atomic_output(destination) as stream:
        stream.write(data)
    return destination


def suggested_decrypted_path(source: str | Path) -> Path:
    source = Path(source)
    name = source.name[:-4] if source.name.lower().endswith(".enc") else source.name
    # Un nombre distinto facilita recuperar junto al original sin colisiones.
    original = Path(name) if name else Path("archivo")
    return source.with_name(f"{original.stem}.recuperado{original.suffix}")
