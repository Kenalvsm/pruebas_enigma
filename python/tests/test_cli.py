import builtins
from pathlib import Path

import pytest

from enigma import aes, cli
from enigma.errors import OperationCancelled


def scripted_input(monkeypatch, answers, passwords=(), paths=()):
    answers = iter(answers)
    passwords = iter(passwords)
    paths = iter(paths)

    def choose_path(title, **options):
        value = next(paths)
        if value is None:
            return options["default"]
        return Path(value)

    monkeypatch.setattr(builtins, "input", lambda _: next(answers))
    monkeypatch.setattr(cli, "select_option", lambda *args, **kwargs: next(answers))
    monkeypatch.setattr(cli.getpass, "getpass", lambda _: next(passwords))
    monkeypatch.setattr(cli, "choose_path", choose_path)


def test_invalid_option_and_exit(monkeypatch, capsys):
    scripted_input(monkeypatch, ["no", "0"])
    assert cli.main([]) == 0
    assert "Opción no válida" in capsys.readouterr().out


def test_vigenere_console_encrypt_and_decrypt(monkeypatch, capsys):
    scripted_input(
        monkeypatch,
        ["1", "1", "ATTACKATDAWN", "1", "2", "1", "LXFOPVEFRNHR", "1", "0"],
        ["LEMON", "LEMON"],
    )
    assert cli.main([]) == 0
    output = capsys.readouterr().out
    assert "LXFOPVEFRNHR" in output
    assert "ATTACKATDAWN" in output


def test_vigenere_file_show_and_save(tmp_path, monkeypatch, capsys):
    source = tmp_path / "entrada.txt"
    source.write_bytes("Hola ñ\r\n".encode())
    target = tmp_path / "salida.txt"
    scripted_input(monkeypatch, ["1", "2", "3", "0"], ["B"], [source, target])
    assert cli.main([]) == 0
    assert target.read_bytes() == "Ipmb ñ\r\n".encode()
    assert "Resultado guardado" in capsys.readouterr().out


def test_vigenere_save_without_display(tmp_path, monkeypatch, capsys):
    target = tmp_path / "salida.txt"
    scripted_input(monkeypatch, ["1", "1", "HOLA", "2", "0"], ["A"], [target])
    assert cli.main([]) == 0
    assert target.read_text() == "HOLA"
    assert "Resultado:\n" not in capsys.readouterr().out


@pytest.mark.parametrize(
    ("answers", "passwords"),
    [
        (["1", "x", "0"], []),
        (["1", "1", "texto", "x", "0"], ["A"]),
        (["1", "1", "texto", "0"], ["ñ"]),
        (["3", "0"], []),
        (["1", "2", "0"], []),
    ],
)
def test_controlled_errors_return_to_menu(monkeypatch, capsys, answers, passwords):
    scripted_input(monkeypatch, answers, passwords, ["ausente.txt", None])
    assert cli.main([]) == 0
    assert "Error:" in capsys.readouterr().out


def test_aes_encrypt_shows_generated_password(tmp_path, monkeypatch, capsys):
    source = tmp_path / "datos.bin"
    source.write_bytes(b"data")
    scripted_input(monkeypatch, ["3", "0"], paths=[source, None])
    assert cli.main([]) == 0
    output = capsys.readouterr().out
    assert "Contraseña generada: " in output
    password = output.split("Contraseña generada: ")[1].splitlines()[0]
    aes.decrypt_file(f"{source}.enc", tmp_path / "out", password)
    assert (tmp_path / "out").read_bytes() == b"data"


def test_aes_decrypt_uses_safe_default_name(tmp_path, monkeypatch, capsys):
    source = tmp_path / "datos.bin"
    source.write_bytes(b"data")
    result = aes.encrypt_file(source)
    scripted_input(monkeypatch, ["4", "0"], [result.password], [result.path, None])
    assert cli.main([]) == 0
    assert (tmp_path / "datos.recuperado.bin").read_bytes() == b"data"
    assert source.read_bytes() == b"data"
    assert result.password not in capsys.readouterr().out


def test_aes_wrong_password_returns_to_menu(tmp_path, monkeypatch, capsys):
    source = tmp_path / "datos"
    source.write_bytes(b"data")
    result = aes.encrypt_file(source)
    wrong = ("A" if result.password[0] != "A" else "B") + result.password[1:]
    scripted_input(monkeypatch, ["4", "0"], [wrong], [result.path, None])
    assert cli.main([]) == 0
    assert not (tmp_path / "datos.recuperado").exists()
    assert "Contraseña incorrecta" in capsys.readouterr().out


@pytest.mark.parametrize("error", [EOFError, KeyboardInterrupt])
def test_user_cancellation(monkeypatch, capsys, error):
    def cancel(_):
        raise error

    monkeypatch.setattr(builtins, "input", cancel)
    monkeypatch.setattr(cli, "select_option", lambda *args, **kwargs: cancel(""))
    assert cli.main([]) == 0
    assert "cancelada" in capsys.readouterr().out


def test_memory_error_returns_to_menu(monkeypatch, capsys):
    scripted_input(monkeypatch, ["3", "0"])

    def fail():
        raise MemoryError

    monkeypatch.setattr(cli, "_encrypt_aes", fail)
    assert cli.main([]) == 0
    assert "Recursos insuficientes" in capsys.readouterr().out


def test_cancel_file_dialog_returns_to_menu(monkeypatch, capsys):
    scripted_input(monkeypatch, ["3", "0"])

    def cancel(*args, **kwargs):
        raise OperationCancelled

    monkeypatch.setattr(cli, "choose_path", cancel)
    assert cli.main([]) == 0
    assert "Volviendo al menú" in capsys.readouterr().out


@pytest.mark.parametrize("flag", ["--version", "--help"])
def test_command_information(flag, capsys):
    with pytest.raises(SystemExit) as error:
        cli.main([flag])
    assert error.value.code == 0
    assert "Enigma" in capsys.readouterr().out
