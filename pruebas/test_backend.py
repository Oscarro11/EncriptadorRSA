"""Pruebas con assert del backend RSA.

Ejecutar desde la raíz proyecto_rsa/: python -m pruebas.test_backend
math.gcd y pow se utilizan únicamente como referencias en este archivo.
"""

from math import gcd, isqrt

from backend.exponenciacion import potencia_modular
from backend.inverso_modular import calcular_inverso_modular
from backend.mcd import calcular_mcd
from backend.primalidad import es_primo
from backend.rsa import calcular_parametros, desencriptar, encriptar
from backend.validaciones import (
    convertir_entero,
    validar_cifrado,
    validar_entero,
    validar_longitud,
    validar_mensaje,
)


def comprobar_error(funcion, tipo_error: type[Exception], *argumentos) -> None:
    """Comprueba que la función lance el error indicado con un mensaje."""
    try:
        funcion(*argumentos)
    except tipo_error as error:
        assert str(error), "El error debe tener una explicación."
    except Exception as error:
        raise AssertionError(
            f"Se esperaba {tipo_error.__name__} y ocurrió {type(error).__name__}."
        ) from error
    else:
        raise AssertionError(
            f"{funcion.__name__}{argumentos!r} debía lanzar {tipo_error.__name__}."
        )


def probar_primalidad() -> None:
    """Comprueba primos, compuestos y límites de división tentativa."""
    for numero in (2, 3, 5, 7, 97, 367, 373, 997):
        assert es_primo(numero)
    for numero in (-7, -1, 0, 1, 4, 9, 91, 121, 1001):
        assert not es_primo(numero)
    for numero in range(2, 1000):
        esperado = all(numero % d != 0 for d in range(2, isqrt(numero) + 1))
        assert es_primo(numero) == esperado
    comprobar_error(es_primo, TypeError, 7.0)
    comprobar_error(es_primo, TypeError, True)


def probar_mcd() -> None:
    """Compara Euclides iterativo con math.gcd."""
    for a in range(-30, 31):
        for b in range(-30, 31):
            if a != 0 or b != 0:
                assert calcular_mcd(a, b) == gcd(a, b)
    assert calcular_mcd(17, 136152) == 1
    comprobar_error(calcular_mcd, ValueError, 0, 0)
    comprobar_error(calcular_mcd, TypeError, "8", 12)


def probar_inverso_modular() -> None:
    """Verifica la identidad del inverso y lo compara con pow."""
    for modulo in range(2, 70):
        for a in range(-10, 80):
            if gcd(a, modulo) == 1:
                inverso = calcular_inverso_modular(a, modulo)
                assert 1 <= inverso < modulo
                assert (a * inverso) % modulo == 1
                assert inverso == pow(a, -1, modulo)
            else:
                comprobar_error(calcular_inverso_modular, ValueError, a, modulo)
    assert calcular_inverso_modular(17, 136152) == 8009
    comprobar_error(calcular_inverso_modular, ValueError, 3, 1)
    comprobar_error(calcular_inverso_modular, TypeError, 3.5, 11)


def probar_exponenciacion() -> None:
    """Compara cuadrados sucesivos con pow de tres argumentos."""
    for modulo in (2, 7, 11, 97, 136891):
        for base in (-10, 0, 1, 7, 82083, 999999):
            for exponente in (0, 1, 2, 3, 17, 100, 136153):
                assert potencia_modular(base, exponente, modulo) == pow(
                    base, exponente, modulo
                )
    comprobar_error(potencia_modular, ValueError, 2, -1, 7)
    comprobar_error(potencia_modular, ValueError, 2, 3, 1)
    comprobar_error(potencia_modular, TypeError, 2, 3.0, 7)


def probar_ejemplo_oficial() -> None:
    """Comprueba exactamente el caso RSA de la página 4 del Parcial 3."""
    cifrado = encriptar("RSA", 367, 373, 17)
    assert cifrado.parametros.n == 136891
    assert cifrado.parametros.phi == 136152
    assert cifrado.parametros.mcd == 1
    assert cifrado.longitud == 3
    assert cifrado.relleno is True
    assert cifrado.mensaje_con_relleno == "RSA "
    assert [b.bloque_original for b in cifrado.detalles] == ["082083", "065032"]
    assert cifrado.cifrado == "026054 123875"

    recuperado = desencriptar(cifrado.cifrado, 3, 367, 373, 17)
    assert recuperado.exponente_privado == 8009
    assert recuperado.mensaje_con_relleno == "RSA "
    assert recuperado.mensaje == "RSA"
    assert recuperado.relleno is True
    assert [b.bloque_cifrado for b in recuperado.detalles] == [
        "026054", "123875"
    ]


def probar_mensajes_validos() -> None:
    """Comprueba recuperación exacta de ASCII, espacios y longitudes."""
    mensajes = (
        "AB", "ABC", "Hola Mundo", "aBcD", "123456", "!?.,;:()",
        "A  B", "  AB", "AB  ", " AB ", " A ", " ", "  ",
        "ABC ", "  A  ", "~!@#$%^&*()_+", "Hola, RSA 2026!",
        chr(32) + chr(126),
    )
    for mensaje in mensajes:
        cifrado = encriptar(mensaje, 367, 373, 17)
        recuperado = desencriptar(
            cifrado.cifrado, cifrado.longitud, 367, 373, 17
        )
        assert recuperado.mensaje == mensaje, repr(mensaje)
        assert cifrado.longitud == len(mensaje)
        assert cifrado.relleno == (len(mensaje) % 2 == 1)
        assert len(cifrado.detalles) == (len(mensaje) + 1) // 2
        assert all(len(b.bloque_original) == 6 for b in cifrado.detalles)
        assert all(len(b.bloque_cifrado) == 6 for b in cifrado.detalles)

    phi = (367 - 1) * (373 - 1)
    e_grande = phi + 17
    assert gcd(e_grande, phi) == 1
    cifrado = encriptar("Texto", 367, 373, e_grande)
    assert desencriptar(
        cifrado.cifrado, cifrado.longitud, 367, 373, e_grande
    ).mensaje == "Texto"


def probar_validaciones() -> None:
    """Rechaza tipos, caracteres, parámetros y cifrados incorrectos."""
    assert convertir_entero("+367", "p") == 367
    assert convertir_entero("-2", "p") == -2
    for texto in ("", " 17", "17 ", "1.7", "abc", "١٧", "17\n", "+"):
        comprobar_error(convertir_entero, ValueError, texto, "e")
    comprobar_error(convertir_entero, TypeError, 17, "e")
    comprobar_error(validar_entero, TypeError, True, "p")

    for parametros in (
        (367, 367, 17), (365, 373, 17), (367, 371, 17),
        (2, 3, 5), (1009, 1013, 17), (367, 373, 1), (367, 373, 2),
    ):
        comprobar_error(calcular_parametros, ValueError, *parametros)
    comprobar_error(calcular_parametros, TypeError, "367", 373, 17)
    comprobar_error(calcular_parametros, TypeError, 367, 373, True)

    for mensaje in ("", "á", "ñ", "A\nB", "A\tB", "😀", "A\rB"):
        comprobar_error(validar_mensaje, ValueError, mensaje)
    comprobar_error(validar_mensaje, TypeError, 123)

    for cifrado in (
        "", "26054", "0026054", "026054  123875", " 026054",
        "026054 ", "026054\n123875", "026054\t123875",
        "02605a", "-26054", "１２３４５６", "136891", "999999",
    ):
        comprobar_error(validar_cifrado, ValueError, cifrado, 136891)
    comprobar_error(validar_cifrado, TypeError, 26054, 136891)
    assert validar_cifrado("000000 000001", 136891) == [0, 1]

    for longitud in (0, -1, 1, 2, 5, 6):
        comprobar_error(validar_longitud, ValueError, longitud, 2)
    comprobar_error(validar_longitud, TypeError, "3", 2)
    comprobar_error(validar_longitud, ValueError, 1, 0)
    validar_longitud(3, 2)
    validar_longitud(4, 2)


def probar_descifrado_invalido() -> None:
    """Rechaza ASCII fuera de rango y ausencia del relleno exigido."""
    n = 367 * 373
    e = 17
    # 031065 corresponde a un código ASCII 031, que no es imprimible.
    cifrado_ascii_invalido = potencia_modular(31065, e, n)
    comprobar_error(
        desencriptar, ValueError,
        f"{cifrado_ascii_invalido:06d}", 2, 367, 373, e,
    )
    # 065066 corresponde a AB, sin espacio de relleno final.
    cifrado_sin_relleno = potencia_modular(65066, e, n)
    comprobar_error(
        desencriptar, ValueError,
        f"{cifrado_sin_relleno:06d}", 1, 367, 373, e,
    )
    comprobar_error(
        desencriptar, ValueError, "026054 123875", 2, 367, 373, 17
    )


def ejecutar_pruebas() -> None:
    """Ejecuta los grupos y presenta sus resultados."""
    grupos = (
        probar_primalidad,
        probar_mcd,
        probar_inverso_modular,
        probar_exponenciacion,
        probar_ejemplo_oficial,
        probar_mensajes_validos,
        probar_validaciones,
        probar_descifrado_invalido,
    )
    for grupo in grupos:
        grupo()
        print(f"OK: {grupo.__name__}")
    print(f"\n{len(grupos)} grupos de pruebas superados.")


if __name__ == "__main__":
    ejecutar_pruebas()
