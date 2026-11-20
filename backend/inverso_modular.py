"""Inverso modular mediante el algoritmo extendido de Euclides."""

from .validaciones import validar_entero


def calcular_inverso_modular(a: int, modulo: int) -> int:
    """Devuelve el inverso de a módulo modulo, cuando existe."""
    validar_entero(a, "a")
    validar_entero(modulo, "El módulo")

    if modulo <= 1:
        raise ValueError("El módulo debe ser mayor que 1.")

    resto_anterior, resto = modulo, a % modulo
    coef_anterior, coef = 0, 1

    while resto != 0:
        cociente = resto_anterior // resto

        resto_anterior, resto = (
            resto,
            resto_anterior - cociente * resto
        )

        coef_anterior, coef = (
            coef,
            coef_anterior - cociente * coef
        )

    if resto_anterior != 1:
        raise ValueError(
            "No existe inverso modular: los números no son coprimos."
        )

    return coef_anterior % modulo