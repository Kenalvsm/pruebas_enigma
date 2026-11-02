import hashlib
import json
import struct
from pathlib import Path

import pytest
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from enigma import aes
from enigma.errors import AuthenticationError, ContainerError, ValidationError


@pytest.mark.parametrize("data", [b"", b"\x00", bytes(range(256)), "Español\r\n".encode()])
def test_roundtrip_and_layout(tmp_path, data):
    source = tmp_path / "original.bin"
    source.write_bytes(data)
    encrypted = aes.encrypt_file(source)
    payload = encrypted.path.read_bytes()
    assert len(payload) == len(data) + 53
    magic, version, iterations, salt, nonce = struct.unpack(">4sBI16s12s", payload[:37])
    assert (magic, version, iterations) == (b"R2AE", 1, 200_000)
    assert len(salt) == 16
    assert len(nonce) == 12
    # Consumidor independiente del cifrado incremental de la aplicación.
    key = hashlib.pbkdf2_hmac("sha256", encrypted.password.encode("ascii"), salt, iterations, 32)
    assert AESGCM(key).decrypt(nonce, payload[37:], payload[:37]) == data
    recovered = tmp_path / "recuperado.bin"
    assert aes.decrypt_file(encrypted.path, recovered, encrypted.password) == recovered
    assert recovered.read_bytes() == data
    assert source.read_bytes() == data
    assert encrypted.password not in repr(encrypted)


def test_passwords_use_secrets_and_required_alphabet(monkeypatch):
    calls = []

    def choice(alphabet):
        calls.append(alphabet)
        return "Z"

    monkeypatch.setattr(aes.secrets, "choice", choice)
    assert aes.generate_password() == "Z" * 16
    assert calls == [aes.PASSWORD_ALPHABET] * 16


def test_fresh_password_salt_and_nonce(tmp_path):
    source = tmp_path / "original"
    source.write_bytes(b"contenido")
    a = aes.encrypt_file(source, tmp_path / "a.enc")
    b = aes.encrypt_file(source, tmp_path / "b.enc")
    assert a.password != b.password
    for result in (a, b):
        assert len(result.password) == 16
        assert all(c in aes.PASSWORD_ALPHABET for c in result.password)
    assert a.path.read_bytes()[9:25] != b.path.read_bytes()[9:25]
    assert a.path.read_bytes()[25:37] != b.path.read_bytes()[25:37]


@pytest.mark.parametrize("password", ["", "short", "a" * 17, "á" * 16, "!" * 16])
def test_invalid_password_format(tmp_path, password):
    source = tmp_path / "data.enc"
    source.write_bytes(b"x" * 53)
    with pytest.raises(ValidationError):
        aes.decrypt_file(source, tmp_path / "out", password)
    assert not (tmp_path / "out").exists()


def test_wrong_password_does_not_publish_plaintext(tmp_path):
    source = tmp_path / "original"
    source.write_bytes(b"secret" * 100)
    result = aes.encrypt_file(source)
    wrong = ("A" if result.password[0] != "A" else "B") + result.password[1:]
    with pytest.raises(AuthenticationError):
        aes.decrypt_file(result.path, tmp_path / "out", wrong)
    assert not (tmp_path / "out").exists()
    assert list(tmp_path.glob("*.part")) == []
    assert source.read_bytes() == b"secret" * 100


@pytest.mark.parametrize("offset", [0, 4, 5, 9, 25, 37, -1])
def test_tampered_header_ciphertext_and_tag(tmp_path, offset):
    source = tmp_path / "original"
    source.write_bytes(b"secret")
    result = aes.encrypt_file(source)
    payload = bytearray(result.path.read_bytes())
    payload[offset] ^= 1
    result.path.write_bytes(payload)
    with pytest.raises((ContainerError, AuthenticationError)):
        aes.decrypt_file(result.path, tmp_path / "out", result.password)
    assert not (tmp_path / "out").exists()
    assert list(tmp_path.glob("*.part")) == []


@pytest.mark.parametrize("length", [0, 1, 36, 37, 52, 54])
def test_truncated_containers(tmp_path, length):
    source = tmp_path / "original"
    source.write_bytes(b"secret")
    result = aes.encrypt_file(source)
    result.path.write_bytes(result.path.read_bytes()[:length])
    with pytest.raises((ContainerError, AuthenticationError)):
        aes.decrypt_file(result.path, tmp_path / "out", result.password)
    assert not (tmp_path / "out").exists()


def test_extra_bytes_rejected(tmp_path):
    source = tmp_path / "original"
    source.write_bytes(b"secret")
    result = aes.encrypt_file(source)
    with result.path.open("ab") as output:
        output.write(b"extra")
    with pytest.raises(AuthenticationError):
        aes.decrypt_file(result.path, tmp_path / "out", result.password)
    assert not (tmp_path / "out").exists()


def test_existing_or_same_destinations_preserved(tmp_path):
    source = tmp_path / "original"
    source.write_bytes(b"secret")
    with pytest.raises(FileExistsError):
        aes.encrypt_file(source, source)
    result = aes.encrypt_file(source)
    with pytest.raises(FileExistsError):
        aes.encrypt_file(source)
    with pytest.raises(FileExistsError):
        aes.decrypt_file(result.path, source, result.password)
    assert source.read_bytes() == b"secret"


def test_permission_error_reading_source(tmp_path, monkeypatch):
    source = tmp_path / "original"
    source.write_bytes(b"secret")
    original_open = Path.open

    def denied(self, *args, **kwargs):
        if self == source:
            raise PermissionError("Permiso denegado")
        return original_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", denied)
    with pytest.raises(PermissionError):
        aes.encrypt_file(source)
    assert not Path(f"{source}.enc").exists()
    assert list(tmp_path.glob("*.part")) == []


def test_write_failure_cleans_partial_ciphertext(tmp_path, monkeypatch):
    source = tmp_path / "original"
    source.write_bytes(b"secret")

    def fail(*args):
        raise OSError("Disco lleno")

    monkeypatch.setattr(aes.os, "fsync", fail)
    with pytest.raises(OSError):
        aes.encrypt_file(source)
    assert not Path(f"{source}.enc").exists()
    assert source.read_bytes() == b"secret"
    assert list(tmp_path.glob("*.part")) == []


def test_streaming_multiple_chunks(tmp_path, monkeypatch):
    monkeypatch.setattr(aes, "CHUNK_SIZE", 7)
    source = tmp_path / "original"
    data = bytes(range(100))
    source.write_bytes(data)
    result = aes.encrypt_file(source)
    aes.decrypt_file(result.path, tmp_path / "out", result.password)
    assert (tmp_path / "out").read_bytes() == data


def test_gcm_size_limit(tmp_path, monkeypatch):
    source = tmp_path / "original"
    source.write_bytes(b"secret")
    result = aes.encrypt_file(source)
    monkeypatch.setattr(aes, "MAX_PLAINTEXT_SIZE", 2)
    with pytest.raises(ValidationError, match="límite"):
        aes.encrypt_file(source, tmp_path / "too-big.enc")
    with pytest.raises(ContainerError, match="límite"):
        aes.decrypt_file(result.path, tmp_path / "out", result.password)
    assert not (tmp_path / "too-big.enc").exists()
    assert not (tmp_path / "out").exists()
    assert list(tmp_path.glob("*.part")) == []


@pytest.mark.parametrize("data", [b"", b"\x00", b"hola\r\n"])
def test_short_header_parser(data):
    with pytest.raises(ContainerError, match="Cabecera"):
        aes._parse_header(data)


def test_portable_reference_vectors(tmp_path):
    fixture = Path(__file__).with_name("fixtures") / "r2ae-v1.json"
    for vector in json.loads(fixture.read_text(encoding="utf-8"))["vectors"]:
        container = tmp_path / f"{vector['name']}.enc"
        output = tmp_path / f"{vector['name']}.out"
        container.write_bytes(bytes.fromhex(vector["container_hex"]))
        aes.decrypt_file(container, output, vector["password"])
        data = bytes.fromhex(vector["plaintext_hex"])
        assert output.read_bytes() == data
        assert hashlib.sha256(data).hexdigest() == vector["plaintext_sha256"]
