"""Construcción de parámetros, encriptación y desencriptación RSA."""

from .exponenciacion import potencia_modular
from .inverso_modular import calcular_inverso_modular
from .mcd import calcular_mcd
from .modelos import (
    DetalleBloque,
    ParametrosRSA,
    ResultadoDesencriptacion,
    ResultadoEncriptacion,
)
from .primalidad import es_primo
from .validaciones import (
    validar_cifrado,
    validar_entero,
    validar_longitud,
    validar_mensaje,
)


def calcular_parametros(p: int, q: int, e: int) -> ParametrosRSA:
    """Valida p, q y e; calcula n, phi y su MCD."""
    for nombre, valor in (("p", p), ("q", q), ("e", e)):
        validar_entero(valor, nombre)

    if not es_primo(p) or not es_primo(q):
        raise ValueError("p y q deben ser números primos.")

    if p == q:
        raise ValueError("p y q deben ser distintos.")

    n = p * q

    if not 126126 < n < 1000000:
        raise ValueError(
            "El módulo n debe cumplir 126126 < n < 1000000."
        )

    phi = (p - 1) * (q - 1)

    if e <= 1:
        raise ValueError("El exponente e debe ser mayor que 1.")

    mcd = calcular_mcd(e, phi)

    if mcd != 1:
        raise ValueError(
            "e y phi deben ser primos relativos (MCD = 1)."
        )

    return ParametrosRSA(p, q, e, n, phi, mcd)


def encriptar(
    mensaje: str, p: int, q: int, e: int
) -> ResultadoEncriptacion:
    """Encripta parejas ASCII y devuelve el cifrado y sus detalles."""
    validar_mensaje(mensaje)
    parametros = calcular_parametros(p, q, e)

    longitud = len(mensaje)
    relleno = longitud % 2 == 1
    texto = mensaje + ' ' if relleno else mensaje

    detalles = []
    bloques_cifrados = []

    for indice in range(0, len(texto), 2):
        pareja = texto[indice:indice + 2]

        ascii_bloque = ''.join(
            f"{ord(caracter):03d}" for caracter in pareja
        )

        m = int(ascii_bloque)
        c = potencia_modular(m, e, parametros.n)

        cifrado_bloque = f"{c:06d}"

        bloques_cifrados.append(cifrado_bloque)

        detalles.append(
            DetalleBloque(
                indice // 2 + 1,
                pareja,
                ascii_bloque,
                f"{m:06d}",
                cifrado_bloque,
            )
        )

    return ResultadoEncriptacion(
        parametros,
        mensaje,
        longitud,
        relleno,
        texto,
        ' '.join(bloques_cifrados),
        detalles,
    )


def desencriptar(
    cifrado: str,
    longitud: int,
    p: int,
    q: int,
    e: int
) -> ResultadoDesencriptacion:
    """Recupera el mensaje y verifica códigos ASCII y relleno."""
    parametros = calcular_parametros(p, q, e)

    bloques = validar_cifrado(cifrado, parametros.n)
    validar_longitud(longitud, len(bloques))

    d = calcular_inverso_modular(e, parametros.phi)

    detalles = []
    parejas = []

    for indice, c in enumerate(bloques, start=1):
        m = potencia_modular(c, d, parametros.n)

        bloque_original = f"{m:06d}"

        codigo_1 = int(bloque_original[:3])
        codigo_2 = int(bloque_original[3:])

        if not (
            32 <= codigo_1 <= 126
            and 32 <= codigo_2 <= 126
        ):
            raise ValueError(
                f"El bloque {indice} no produce dos caracteres ASCII válidos."
            )

        pareja = chr(codigo_1) + chr(codigo_2)

        parejas.append(pareja)

        detalles.append(
            DetalleBloque(
                indice,
                pareja,
                bloque_original,
                bloque_original,
                f"{c:06d}",
            )
        )

    texto = ''.join(parejas)
    relleno = longitud % 2 == 1

    if relleno:
        if not texto.endswith(' '):
            raise ValueError(
                "La longitud impar exige un espacio de relleno al final."
            )

        mensaje = texto[:-1]
    else:
        mensaje = texto

    return ResultadoDesencriptacion(
        parametros,
        cifrado,
        longitud,
        relleno,
        d,
        texto,
        mensaje,
        detalles,
    )