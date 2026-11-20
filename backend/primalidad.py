"""Comprobación de primalidad por división tentativa."""

from math import isqrt

from .validaciones import validar_entero


def es_primo(numero: int) -> bool:
    """Determina si un entero es primo probando divisores hasta su raíz."""
    validar_entero(numero, "El número")

    if numero < 2:
        return False

    if numero == 2:
        return True

    if numero % 2 == 0:
        return False

    for divisor in range(3, isqrt(numero) + 1, 2):
        if numero % divisor == 0:
            return False

    return True