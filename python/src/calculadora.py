def sumar(a: int, b: int) -> int:
    """Devuelve la suma de dos enteros."""
    return a + b


def restar(a: int, b: int) -> int:
    """Devuelve la resta de dos enteros."""
    return a - b


def multiplicar(a: int, b: int) -> int:
    """Devuelve el producto de dos enteros."""
    return a * b


def dividir(a: float, b: float) -> float:
    """Devuelve la division de dos numeros."""
    if b == 0:
        raise ValueError("No se puede dividir entre cero")

    return a / b
