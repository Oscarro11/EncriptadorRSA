"""Algoritmo de Euclides para el máximo común divisor."""

from .validaciones import validar_entero


def calcular_mcd(a: int, b: int) -> int:
    """Calcula el MCD de dos enteros, no ambos cero."""
    validar_entero(a, "a")
    validar_entero(b, "b")

    if a == 0 and b == 0:
        raise ValueError("El MCD de cero y cero no está definido.")

    a, b = abs(a), abs(b)

    while b != 0:
        a, b = b, a % b

    return a