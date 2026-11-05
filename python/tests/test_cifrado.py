import pytest

from src.cifrado import cifrar, descifrar, validar_clave


def test_vector_conocido() -> None:
    assert cifrar("HOLA", "BC") == "IQMC"


def test_ida_y_vuelta() -> None:
    texto = "En un lugar de la Mancha, de cuyo nombre no quiero acordarme."
    assert descifrar(cifrar(texto, "clave"), "clave") == texto


def test_mayusculas_y_signos_se_conservan() -> None:
    assert cifrar("Hola, mundo!", "B") == "Ipmb, nvoep!"


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
