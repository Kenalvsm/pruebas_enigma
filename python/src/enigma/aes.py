"""AES-256-GCM incremental con el contenedor R2AE v1 del contrato técnico."""

import os
import secrets
import string
import struct
from dataclasses import dataclass, field
from pathlib import Path

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from enigma.errors import AuthenticationError, ContainerError, ValidationError
from enigma.files import atomic_output, input_file, new_destination

MAGIC = b"R2AE"
VERSION = 1
ITERATIONS = 200_000
SALT_SIZE = 16
NONCE_SIZE = 12
TAG_SIZE = 16
HEADER = struct.Struct(">4sBI16s12s")
HEADER_SIZE = HEADER.size
OVERHEAD = HEADER_SIZE + TAG_SIZE
CHUNK_SIZE = 1024 * 1024
PASSWORD_ALPHABET = string.ascii_uppercase + string.ascii_lowercase + string.digits
# Límite de GCM para un único mensaje (2**39 - 256 bits).
MAX_PLAINTEXT_SIZE = (1 << 36) - 32


@dataclass(frozen=True)
class EncryptionResult:
    path: Path
    # No revelar la contraseña al imprimir o registrar el objeto.
    password: str = field(repr=False)


def generate_password() -> str:
    return "".join(secrets.choice(PASSWORD_ALPHABET) for _ in range(16))


def _validate_password(password: str) -> bytes:
    if len(password) != 16 or any(c not in PASSWORD_ALPHABET for c in password):
        raise ValidationError("La contraseña AES debe tener 16 caracteres A-Z, a-z o 0-9.")
    return password.encode("ascii")


def _derive_key(password: bytes, salt: bytes) -> bytes:
    return PBKDF2HMAC(
        algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITERATIONS
    ).derive(password)


def _parse_header(header: bytes) -> tuple[bytes, bytes]:
    if len(header) != HEADER_SIZE:
        raise ContainerError("Cabecera R2AE incompleta.")
    magic, version, iterations, salt, nonce = HEADER.unpack(header)
    if magic != MAGIC:
        raise ContainerError("El archivo no es un contenedor R2AE.")
    if version != VERSION:
        raise ContainerError(f"Versión R2AE no compatible: {version}.")
    # v1 fija 200.000. No ejecutar costes arbitrarios indicados por archivos no fiables.
    if iterations != ITERATIONS:
        raise ContainerError("R2AE v1 requiere 200.000 iteraciones PBKDF2.")
    return salt, nonce


def encrypt_file(source: str | Path, destination: str | Path | None = None) -> EncryptionResult:
    """Cifra un archivo nuevo; la contraseña siempre se genera automáticamente."""
    source = input_file(source)
    destination = new_destination(destination if destination is not None else f"{source}.enc")
    password = generate_password()
    salt = secrets.token_bytes(SALT_SIZE)
    nonce = secrets.token_bytes(NONCE_SIZE)
    header = HEADER.pack(MAGIC, VERSION, ITERATIONS, salt, nonce)
    key = _derive_key(_validate_password(password), salt)
    encryptor = Cipher(algorithms.AES(key), modes.GCM(nonce)).encryptor()
    encryptor.authenticate_additional_data(header)
    with source.open("rb") as original, atomic_output(destination) as output:
        if os.fstat(original.fileno()).st_size > MAX_PLAINTEXT_SIZE:
            raise ValidationError("El archivo supera el límite de un mensaje AES-GCM.")
        output.write(header)
        total = 0
        while block := original.read(CHUNK_SIZE):
            total += len(block)
            if total > MAX_PLAINTEXT_SIZE:
                raise ValidationError("El archivo supera el límite de un mensaje AES-GCM.")
            output.write(encryptor.update(block))
        output.write(encryptor.finalize())
        output.write(encryptor.tag)
    return EncryptionResult(destination, password)


def decrypt_file(source: str | Path, destination: str | Path, password: str) -> Path:
    """Publica el texto recuperado únicamente después de verificar la etiqueta."""
    source = input_file(source)
    destination = new_destination(destination)
    password_bytes = _validate_password(password)
    try:
        with source.open("rb") as original:
            size = os.fstat(original.fileno()).st_size
            if size < OVERHEAD:
                raise ContainerError("Contenedor R2AE truncado: faltan cabecera o etiqueta.")
            if size - OVERHEAD > MAX_PLAINTEXT_SIZE:
                raise ContainerError("El contenedor supera el límite de un mensaje AES-GCM.")
            header = original.read(HEADER_SIZE)
            salt, nonce = _parse_header(header)
            original.seek(-TAG_SIZE, os.SEEK_END)
            tag = original.read(TAG_SIZE)
            if len(tag) != TAG_SIZE:
                raise ContainerError("El contenedor se ha truncado durante la lectura.")
            original.seek(HEADER_SIZE)
            key = _derive_key(password_bytes, salt)
            decryptor = Cipher(algorithms.AES(key), modes.GCM(nonce, tag)).decryptor()
            decryptor.authenticate_additional_data(header)
            with atomic_output(destination) as output:
                remaining = size - OVERHEAD
                while remaining:
                    block = original.read(min(CHUNK_SIZE, remaining))
                    if not block:
                        raise ContainerError("El contenedor se ha truncado durante la lectura.")
                    remaining -= len(block)
                    output.write(decryptor.update(block))
                if original.read(TAG_SIZE) != tag or original.read(1):
                    raise ContainerError("El contenedor ha cambiado durante la lectura.")
                output.write(decryptor.finalize())
    except InvalidTag as error:
        raise AuthenticationError(
            "Contraseña incorrecta o archivo alterado. No se ha publicado ningún resultado."
        ) from error
    return destination
