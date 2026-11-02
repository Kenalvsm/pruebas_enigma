"""Menú en español. Las operaciones criptográficas no dependen de la consola."""

import argparse
import getpass
from pathlib import Path

from enigma import __version__, aes, vigenere
from enigma.dialogs import ENCRYPTED_FILES, TEXT_FILES, choose_path
from enigma.errors import EnigmaError, OperationCancelled, ValidationError
from enigma.files import read_text, suggested_decrypted_path, write_text
from enigma.selector import TerminalUnavailable, select_option
from enigma.terminal import badge, frame, section


def _menu(selected: int = 0) -> str:
    def item(index: int, label: str, color: str) -> str:
        if selected == index:
            return "    " + badge(f"> {label} ", color)
        return f"      {label}"

    return "\n" + frame(
        [
            "",
            f"  {badge(' E N I G M A ', 'magenta')}     {badge(' RETO 02 ', 'blue')}",
            "  Cifrado de texto y archivos",
            f"  .----------------.----------------.   v{__version__}",
            "  |  A B C > X Y Z |  0 1 > # * +  |",
            "  '----------------'----------------'",
            "",
            "  VIGENÈRE / TEXTO",
            item(0, "Cifrar Vigenère", "magenta"),
            item(1, "Descifrar Vigenère", "blue"),
            "",
            "  AES / ARCHIVOS",
            item(2, "Cifrar archivo AES", "green"),
            item(3, "Descifrar archivo AES", "yellow"),
            "",
            item(4, "Salir", "blue"),
            "",
            "  Arriba/Abajo: mover | Enter: elegir | Esc: salir",
            "  Los archivos se seleccionan en el explorador.",
            "",
        ]
    )


def _vigenere_operation(encrypting: bool) -> None:
    action = "CIFRAR" if encrypting else "DESCIFRAR"
    print(section(f"VIGENÈRE / {action}", "magenta" if encrypting else "blue"))
    mode = select_option("Origen del texto", [("1", "Texto por consola"), ("2", "Archivo .txt")])
    if mode == "1":
        text = input("Texto: ")
    elif mode == "2":
        text = read_text(choose_path("Seleccionar archivo de texto", filetypes=TEXT_FILES))
    else:
        raise ValidationError("Origen del texto no válido.")
    key = getpass.getpass("Clave Vigenère (1-64 letras A-Z): ")
    operation = vigenere.encrypt if encrypting else vigenere.decrypt
    result = operation(text, key)
    mode = select_option(
        "Qué hacer con el resultado",
        [("1", "Mostrar"), ("2", "Guardar .txt"), ("3", "Mostrar y guardar")],
    )
    if mode not in {"1", "2", "3"}:
        raise ValidationError("Acción de resultado no válida.")
    if mode in {"1", "3"}:
        print(f"\n{badge('Resultado:', 'blue')}\n{result}")
    if mode in {"2", "3"}:
        destination = write_text(
            choose_path(
                "Guardar resultado Vigenère",
                save=True,
                default=Path("resultado.txt"),
                filetypes=TEXT_FILES,
                extension=".txt",
            ),
            result,
        )
        print(f"{badge('OK', 'green')} Resultado guardado en: {destination}")


def _encrypt_aes() -> None:
    print(section("AES / CIFRAR ARCHIVO", "green"))
    source = choose_path("Seleccionar archivo para cifrar con AES")
    destination = choose_path(
        "Guardar archivo cifrado",
        save=True,
        default=Path(f"{source}.enc"),
        filetypes=ENCRYPTED_FILES,
        extension=".enc",
    )
    print(f"{badge('AES', 'blue')} Cifrando archivo...")
    result = aes.encrypt_file(source, destination)
    print(f"{badge('OK', 'green')} Archivo cifrado: {result.path}")
    print(f"Contraseña generada: {result.password}")
    print(
        f"{badge('Atención:', 'yellow')} "
        "Guárdala ahora y compártela por un canal separado. No se guarda en el archivo."
    )


def _decrypt_aes() -> None:
    print(section("AES / DESCIFRAR ARCHIVO", "yellow"))
    source = choose_path("Seleccionar contenedor R2AE", filetypes=ENCRYPTED_FILES)
    destination = choose_path(
        "Guardar archivo recuperado", save=True, default=suggested_decrypted_path(source)
    )
    password = getpass.getpass("Contraseña original (16 caracteres): ")
    print(f"{badge('AES', 'blue')} Descifrando y verificando archivo...")
    result = aes.decrypt_file(source, destination, password)
    print(f"{badge('OK', 'green')} Archivo recuperado y autenticado: {result}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Enigma: menú local de Vigenère y AES/R2AE.")
    parser.add_argument("--version", action="version", version=f"Enigma {__version__}")
    parser.parse_args(argv)
    while True:
        try:
            option = select_option(
                "ENIGMA · Reto 02",
                [
                    ("1", "Cifrar Vigenère"),
                    ("2", "Descifrar Vigenère"),
                    ("3", "Cifrar archivo AES"),
                    ("4", "Descifrar archivo AES"),
                    ("0", "Salir"),
                ],
                render=_menu,
                cancel_value="0",
            )
            if option == "0":
                print("Hasta pronto.")
                return 0
            if option == "1":
                _vigenere_operation(True)
            elif option == "2":
                _vigenere_operation(False)
            elif option == "3":
                _encrypt_aes()
            elif option == "4":
                _decrypt_aes()
            else:
                print(
                    f"{badge('Aviso:', 'yellow')} Opción no válida. Elige una opción del selector."
                )
        except OperationCancelled:
            print(f"{badge('Aviso:', 'yellow')} Operación cancelada. Volviendo al menú.")
        except EOFError, KeyboardInterrupt:
            print("\nOperación cancelada. Hasta pronto.")
            return 0
        except TerminalUnavailable as error:
            print(f"Error: {error}")
            return 1
        except (EnigmaError, OSError, UnicodeError, MemoryError) as error:
            message = str(error) or "Recursos insuficientes para completar la operación."
            print(f"{badge('Error:', 'yellow')} {message}")
            print("Puedes intentarlo de nuevo desde el menú.")
