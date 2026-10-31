import pytest

from src.calculadora import dividir, restar, sumar


def test_sumar() -> None:
    assert sumar(2, 3) == 5


def test_restar() -> None:
    assert restar(5, 3) == 2


def test_dividir() -> None:
    assert dividir(10, 2) == 5


def test_dividir_entre_cero() -> None:
    with pytest.raises(ValueError):
        dividir(1, 0)
