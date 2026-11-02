"""Selectores nativos para abrir archivos y elegir destinos de guardado."""

from pathlib import Path

from enigma.errors import OperationCancelled, ValidationError

ALL_FILES = (("Todos los archivos", "*"),)
TEXT_FILES = (("Archivos de texto", "*.txt"),) + ALL_FILES
ENCRYPTED_FILES = (("Contenedores R2AE", "*.enc"),) + ALL_FILES


def choose_path(
    title: str,
    *,
    save: bool = False,
    default: Path | None = None,
    filetypes: tuple = ALL_FILES,
    extension: str = "",
) -> Path:
    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError as error:
        raise ValidationError(
            "El explorador necesita Tkinter. Instala Python con Tcl/Tk "
            "(en Linux, el paquete python3-tk de tu versión de Python)."
        ) from error

    root = None
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        options = {
            "parent": root,
            "title": title,
            "filetypes": filetypes,
            "initialdir": str(default.absolute().parent if default is not None else Path.cwd()),
        }
        if save:
            if default is not None:
                options["initialfile"] = default.name
            # La capa de archivos sigue rechazando cualquier sobrescritura.
            value = filedialog.asksaveasfilename(defaultextension=extension, **options)
        else:
            value = filedialog.askopenfilename(**options)
    except tk.TclError as error:
        raise ValidationError(
            "No se pudo abrir el explorador. Ejecuta Enigma en una sesión de escritorio."
        ) from error
    finally:
        if root is not None:
            root.destroy()

    if not value:
        raise OperationCancelled
    return Path(value)
