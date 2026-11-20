"""Estructuras para comunicar resultados a la interfaz."""

from dataclasses import dataclass


@dataclass
class ParametrosRSA:
    """Parámetros matemáticos validados de RSA."""
    p: int
    q: int
    e: int
    n: int
    phi: int
    mcd: int


@dataclass
class DetalleBloque:
    """Representación de una pareja y su transformación RSA."""
    numero: int
    caracteres: str
    ascii: str
    bloque_original: str
    bloque_cifrado: str


@dataclass
class ResultadoEncriptacion:
    """Salida completa del proceso de encriptación."""
    parametros: ParametrosRSA
    mensaje: str
    longitud: int
    relleno: bool
    mensaje_con_relleno: str
    cifrado: str
    detalles: list[DetalleBloque]


@dataclass
class ResultadoDesencriptacion:
    """Salida completa del proceso de desencriptación."""
    parametros: ParametrosRSA
    cifrado: str
    longitud: int
    relleno: bool
    exponente_privado: int
    mensaje_con_relleno: str
    mensaje: str
    detalles: list[DetalleBloque]