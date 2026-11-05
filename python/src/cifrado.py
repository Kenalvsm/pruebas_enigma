"""Cifrado Vigenere sobre A-Z; el resto de caracteres no avanza la clave."""

import string

LETRAS = string.ascii_lowercase
LONGITUD_MAXIMA_CLAVE = 64


def validar_clave(clave: str) -> str:
    """Devuelve la clave en minusculas; exige de 1 a 64 letras A-Z."""
    if not clave.isascii() or not clave.isalpha():
        raise ValueError("La clave solo admite letras A-Z")
    if not 1 <= len(clave) <= LONGITUD_MAXIMA_CLAVE:
        raise ValueError("La clave debe tener entre 1 y 64 letras")
    return clave.lower()


def _desplazar(texto: str, clave: str, signo: int) -> str:
    """Aplica el desplazamiento a las letras ASCII y copia el resto intacto."""
    clave = validar_clave(clave)
    salida: list[str] = []
    posicion = 0
    for caracter in texto:
        if caracter not in string.ascii_letters:
            salida.append(caracter)
            continue
        base = LETRAS.index(caracter.lower())
        desplazamiento = LETRAS.index(clave[posicion % len(clave)])
        letra = LETRAS[(base + signo * desplazamiento) % 26]
        salida.append(letra.upper() if caracter.isupper() else letra)
        posicion += 1
    return "".join(salida)


def cifrar(texto: str, clave: str) -> str:
    """Cifra con Vigenere conservando mayusculas, espacios, signos y tildes."""
    return _desplazar(texto, clave, 1)


def descifrar(texto: str, clave: str) -> str:
    """Revierte cifrar y devuelve el texto original."""
    return _desplazar(texto, clave, -1)
