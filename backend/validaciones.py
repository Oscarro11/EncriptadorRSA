"""Validaciones de entradas del proyecto RSA."""


def validar_entero(valor: int, nombre: str) -> int:
    """Comprueba que el valor sea un entero (no booleano)."""
    if type(valor) is not int:
        raise TypeError(f"{nombre} debe ser un número entero.")
    return valor


def convertir_entero(texto: str, nombre: str) -> int:
    """Convierte un campo de la interfaz en un entero decimal."""
    if not isinstance(texto, str):
        raise TypeError(f"{nombre} debe ingresarse como texto.")

    if not texto or not texto.isascii() or not (
        texto.isdecimal() or
        (texto[0] in '+-' and len(texto) > 1 and texto[1:].isdecimal())
    ):
        raise ValueError(f"{nombre} debe contener un entero decimal.")

    return int(texto)


def validar_mensaje(mensaje: str) -> None:
    """Acepta texto no vacío formado únicamente por ASCII imprimible."""
    if not isinstance(mensaje, str):
        raise TypeError("El mensaje debe ser una cadena de texto.")

    if not mensaje:
        raise ValueError("El mensaje no puede estar vacío.")

    for posicion, caracter in enumerate(mensaje, start=1):
        if not 32 <= ord(caracter) <= 126:
            raise ValueError(
                f"Carácter no admitido en la posición {posicion}: "
                f"código {ord(caracter)}. Solo se permite ASCII 32 a 126."
            )


def validar_cifrado(cifrado: str, n: int) -> list[int]:
    """Valida bloques decimales de seis dígitos separados por un espacio."""
    if not isinstance(cifrado, str):
        raise TypeError("El cifrado debe ser una cadena de texto.")

    validar_entero(n, "n")

    if n <= 0:
        raise ValueError("n debe ser positivo.")

    bloques = cifrado.split(' ')

    if not cifrado or any(
        len(bloque) != 6 or any(digito not in '0123456789' for digito in bloque)
        for bloque in bloques
    ):
        raise ValueError(
            "C debe contener bloques de seis dígitos "
            "separados por un solo espacio."
        )

    numeros = [int(bloque) for bloque in bloques]

    if any(numero >= n for numero in numeros):
        raise ValueError("Cada bloque cifrado debe ser menor que n.")

    return numeros


def validar_longitud(longitud: int, cantidad_bloques: int) -> None:
    """Comprueba que L sea 2k o 2k-1 para k bloques no vacíos."""
    validar_entero(longitud, "L")
    validar_entero(cantidad_bloques, "La cantidad de bloques")

    if cantidad_bloques <= 0:
        raise ValueError("El cifrado debe contener al menos un bloque.")

    if longitud not in (2 * cantidad_bloques, 2 * cantidad_bloques - 1):
        raise ValueError(
            "L debe ser 2k o 2k-1, donde k es la cantidad de bloques."
        )