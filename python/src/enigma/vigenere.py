"""Vigenère educativo: solo A-Z avanza la clave; se conserva el resto del texto."""

from enigma.errors import ValidationError


def validate_key(key: str) -> str:
    if not 1 <= len(key) <= 64 or not all("A" <= c <= "Z" or "a" <= c <= "z" for c in key):
        raise ValidationError("La clave Vigenère debe contener entre 1 y 64 letras A-Z.")
    return key.upper()


def _transform(text: str, key: str, direction: int) -> str:
    key = validate_key(key)
    result = []
    index = 0
    for character in text:
        if "A" <= character <= "Z":
            base = ord("A")
        elif "a" <= character <= "z":
            base = ord("a")
        else:
            result.append(character)
            continue
        shift = ord(key[index % len(key)]) - ord("A")
        result.append(chr(base + (ord(character) - base + direction * shift) % 26))
        index += 1
    return "".join(result)


def encrypt(text: str, key: str) -> str:
    return _transform(text, key, 1)


def decrypt(text: str, key: str) -> str:
    return _transform(text, key, -1)
