import pytest

from enigma import vigenere
from enigma.errors import ValidationError


def test_known_vector():
    assert vigenere.encrypt("ATTACKATDAWN", "LEMON") == "LXFOPVEFRNHR"
    assert vigenere.decrypt("LXFOPVEFRNHR", "lemon") == "ATTACKATDAWN"


@pytest.mark.parametrize("key", ["a", "Z", "MiClave", "z" * 64])
def test_roundtrip_spanish_and_unicode(key):
    text = "¡Hola, Señor! Mañana: café, pingüino. ÁÉÍÓÚ ñÑ 123 😀\r\nAbZ\tfin"
    encrypted = vigenere.encrypt(text, key)
    assert vigenere.decrypt(encrypted, key) == text
    for original, transformed in zip(text, encrypted, strict=True):
        if not original.isascii() or not original.isalpha():
            assert transformed == original
        else:
            assert original.isupper() == transformed.isupper()


def test_non_ascii_does_not_advance_key():
    assert vigenere.encrypt("A ñ-Á1 a\nA", "BC") == "B ñ-Á1 c\nB"
    assert vigenere.encrypt("", "A") == ""


@pytest.mark.parametrize("key", ["", "a" * 65, "ñ", "Á", "ABC DEF", "A1", "A!", "K", "ß"])
def test_invalid_keys(key):
    with pytest.raises(ValidationError):
        vigenere.encrypt("texto", key)
    with pytest.raises(ValidationError):
        vigenere.decrypt("texto", key)
