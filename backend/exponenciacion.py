"""Exponenciación modular mediante cuadrados sucesivos."""

from .validaciones import validar_entero


def potencia_modular(base: int, exponente: int, modulo: int) -> int:
    """Calcula base**exponente % modulo sin formar la potencia completa."""
    validar_entero(base, "La base")
    validar_entero(exponente, "El exponente")
    validar_entero(modulo, "El módulo")

    if exponente < 0:
        raise ValueError("El exponente no puede ser negativo.")

    if modulo <= 1:
        raise ValueError("El módulo debe ser mayor que 1.")

    resultado = 1
    base = base % modulo

    while exponente > 0:
        if exponente % 2 == 1:
            resultado = (resultado * base) % modulo

        base = (base * base) % modulo
        exponente //= 2

    return resultado