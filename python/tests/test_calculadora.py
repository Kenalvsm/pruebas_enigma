import pytest

from src.calculadora import dividir, multiplicar, restar, sumar


@pytest.mark.parametrize(
    ("a", "b", "esperado"),
    [(2, 3, 5), (0, 0, 0), (-4, 3, -1), (10**6, 1, 10**6 + 1)],
)
def test_sumar(a: int, b: int, esperado: int) -> None:
    assert sumar(a, b) == esperado


@pytest.mark.parametrize(
    ("a", "b", "esperado"),
    [(5, 3, 2), (3, 5, -2), (0, 0, 0), (-2, -3, 1)],
)
def test_restar(a: int, b: int, esperado: int) -> None:
    assert restar(a, b) == esperado


@pytest.mark.parametrize(
    ("a", "b", "esperado"),
    [(2, 3, 6), (0, 7, 0), (-4, 3, -12), (-2, -3, 6), (10**6, 10**6, 10**12)],
)
def test_multiplicar(a: int, b: int, esperado: int) -> None:
    assert multiplicar(a, b) == esperado


@pytest.mark.parametrize(
    ("a", "b", "esperado"),
    [(10, 2, 5.0), (7, 2, 3.5), (0, 5, 0.0), (-9, 3, -3.0)],
)
def test_dividir(a: float, b: float, esperado: float) -> None:
    assert dividir(a, b) == esperado


@pytest.mark.parametrize(("a", "b"), [(1, 0), (0, 0), (-3, 0.0)])
def test_dividir_entre_cero(a: float, b: float) -> None:
    with pytest.raises(ValueError):
        dividir(a, b)
