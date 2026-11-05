import pytest

from src.cifrado import cifrar, descifrar, validar_clave


@pytest.mark.parametrize(
    ("texto", "clave", "esperado"),
    [
        ("HOLA", "BC", "IQMC"),
        ("CIFRADO", "CLAVE", "ETFMEFZ"),
        ("cifrado", "clave", "etfmefz"),
        ("Z", "B", "A"),
        ("A", "Z", "Z"),
        ("Ñandú 123", "B", "Ñboeú 123"),
        ("Hola, mundo!", "B", "Ipmb, nvoep!"),
    ],
)
def test_cifrar_esperado(texto: str, clave: str, esperado: str) -> None:
    assert cifrar(texto, clave) == esperado


@pytest.mark.parametrize(
    ("texto", "clave", "esperado"),
    [
        ("IQMC", "BC", "HOLA"),
        ("ETFMEFZ", "CLAVE", "CIFRADO"),
        ("etfmefz", "clave", "cifrado"),
        ("A", "B", "Z"),
        ("Z", "Z", "A"),
        ("Ñboeú 123", "B", "Ñandú 123"),
        ("Ipmb, nvoep!", "B", "Hola, mundo!"),
    ],
)
def test_descifrar_esperado(texto: str, clave: str, esperado: str) -> None:
    assert descifrar(texto, clave) == esperado


def test_ida_y_vuelta() -> None:
    texto = "En un lugar de la Mancha, de cuyo nombre no quiero acordarme."
    assert descifrar(cifrar(texto, "clave"), "clave") == texto


def test_acentos_y_enie_no_avanzan_la_clave() -> None:
    assert cifrar("año", "B") == "bñp"
    assert cifrar("áé", "B") == "áé"


def test_la_clave_se_normaliza() -> None:
    assert cifrar("HOLA", "bc") == cifrar("HOLA", "BC")


def test_texto_vacio() -> None:
    assert cifrar("", "A") == ""
    assert descifrar("", "A") == ""


def test_clave_de_64_letras() -> None:
    assert validar_clave("A" * 64) == "a" * 64


@pytest.mark.parametrize(
    "clave", ["", "A" * 65, "clave1", "clave con espacios", "ñandu", "-"]
)
def test_clave_invalida(clave: str) -> None:
    with pytest.raises(ValueError):
        validar_clave(clave)
