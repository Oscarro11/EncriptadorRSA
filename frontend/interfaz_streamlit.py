"""Presentación web de RSA Studio; utiliza el backend sin modificarlo."""

from html import escape
from pathlib import Path

import streamlit as st

from backend.rsa import desencriptar, encriptar
from backend.validaciones import convertir_entero

MAX_MENSAJE = 2000
MAX_CIFRADO = 6999  # 1000 bloques de seis dígitos y sus separadores.


def _parametros(campos: dict[str, str]) -> tuple[int, int, int]:
    """Limita trabajo en la web antes de invocar las validaciones matemáticas."""
    if any(len(valor) > 32 for valor in campos.values()):
        raise ValueError("La versión web admite hasta 32 caracteres por parámetro.")
    p, q, e = (convertir_entero(campos[nombre], nombre) for nombre in ("p", "q", "e"))
    if not (2 <= p < 1000000 and 2 <= q < 1000000):
        raise ValueError("p y q deben estar entre 2 y 999999 para el módulo del proyecto.")
    return p, q, e


def _resumen(resultado, es_cifrado: bool) -> None:
    if resultado is None:
        valores = ["—"] * 6
    else:
        datos = resultado.parametros
        clave = (f"Pública ({datos.e}, {datos.n})" if es_cifrado else
                 f"d = {resultado.exponente_privado} · Privada "
                 f"({resultado.exponente_privado}, {datos.n})")
        valores = [datos.n, datos.phi, datos.mcd, resultado.longitud,
                   "Sí · espacio 032" if resultado.relleno else "No", clave]
    nombres = ["MÓDULO n", "FUNCIÓN φ", "MCD(e, φ)", "LONGITUD L", "RELLENO", "CLAVE RSA"]
    with st.container(border=True):
        st.subheader("Resumen matemático")
        st.caption("Valores calculados y datos necesarios para recuperar el texto.")
        tarjetas = "".join(
            f'<div class="rsa-metric"><span>{escape(nombre)}</span>'
            f'<strong>{escape(str(valor))}</strong></div>'
            for nombre, valor in zip(nombres, valores)
        )
        st.markdown(f'<div class="rsa-grid">{tarjetas}</div>', unsafe_allow_html=True)


def _pagina(operacion: str) -> None:
    es_cifrado = operacion == "encriptar"
    titulo = "Encriptar mensaje" if es_cifrado else "Desencriptar mensaje"
    clave_resultado = f"resultado_{operacion}"
    clave_error = f"error_{operacion}"
    st.header(titulo)
    st.caption("Transforma texto ASCII en bloques RSA de seis dígitos." if es_cifrado else
               "Recupera exactamente el mensaje utilizando C y L.")

    with st.form(f"formulario_{operacion}"):
        st.subheader("Parámetros RSA")
        st.caption("Dos primos distintos y un exponente público coprimo con φ.")
        campos = {}
        for columna, nombre, valor in zip(st.columns(3), ("p", "q", "e"), ("367", "373", "17")):
            with columna:
                campos[nombre] = st.text_input(nombre, valor, max_chars=32, key=f"{operacion}_{nombre}")
        st.divider()
        if es_cifrado:
            texto = st.text_area("Mensaje original · M", height=120,
                                 key="mensaje", help="ASCII 32–126. Los espacios se conservan.")
            st.caption("Hasta 2000 caracteres. Sin tildes, ñ, tabulaciones ni saltos de línea.")
        else:
            texto = st.text_area("Mensaje cifrado · C", height=120,
                                 key="cifrado", help="Bloques de seis dígitos separados por un espacio.")
            longitud_texto = st.text_input("Longitud original · L", max_chars=4, key="longitud")
        enviado = st.form_submit_button("↗ ENCRIPTAR" if es_cifrado else "↙ DESENCRIPTAR", type="primary")

    if enviado:
        st.session_state[clave_resultado] = None
        st.session_state[clave_error] = None
        try:
            p, q, e = _parametros(campos)
            limite = MAX_MENSAJE if es_cifrado else MAX_CIFRADO
            if len(texto) > limite:
                raise ValueError(f"La entrada supera el límite web de {limite} caracteres.")
            if es_cifrado:
                resultado = encriptar(texto, p, q, e)
            else:
                longitud = convertir_entero(longitud_texto, "L")
                resultado = desencriptar(texto, longitud, p, q, e)
            st.session_state[clave_resultado] = resultado
        except (TypeError, ValueError) as error:
            st.session_state[clave_error] = str(error)

    resultado = st.session_state.get(clave_resultado)
    error = st.session_state.get(clave_error)
    if error:
        st.error(f"Revisa los datos: {error}")
    elif resultado is not None:
        st.success("Operación completada")
        st.caption("Resultado del último envío. Si cambias los datos, vuelve a pulsar el botón de operación.")
    else:
        st.caption("● Esperando datos")
    _resumen(resultado, es_cifrado)

    with st.container(border=True):
        st.subheader("Resultado · Cifrado C" if es_cifrado else "Resultado · Mensaje original M")
        if resultado is None:
            st.caption("El resultado aparecerá aquí al completar la operación.")
        else:
            salida = resultado.cifrado if es_cifrado else resultado.mensaje
            st.code(salida, language=None)
            st.caption("Usa el icono de copiar del bloque. La descarga conserva exactamente los espacios.")
            st.download_button("DESCARGAR RESULTADO", salida.encode("utf-8"),
                               file_name="cifrado.txt" if es_cifrado else "mensaje.txt",
                               mime="text/plain", key=f"descarga_{operacion}", on_click="ignore")
            if es_cifrado:
                st.caption("Longitud original · L — cópiala por separado y guárdala junto con C.")
                st.code(str(resultado.longitud), language=None)

    with st.container(border=True):
        st.subheader("Detalle de bloques")
        st.caption("Cada fila conserva los caracteres, códigos ASCII y bloques numéricos.")
        if resultado is None:
            st.caption("Sin bloques para mostrar.")
        else:
            st.dataframe([
                {"N.º": b.numero, "Caracteres": repr(b.caracteres), "ASCII": b.ascii,
                 "Bloque m": b.bloque_original, "Bloque c": b.bloque_cifrado}
                for b in resultado.detalles
            ], hide_index=True, width="stretch")


def main() -> None:
    st.set_page_config(page_title="RSA Studio | Matemática Discreta", page_icon="◈", layout="wide")
    estilos = Path(__file__).with_name("estilos_streamlit.css").read_text(encoding="utf-8")
    st.markdown(f"<style>{estilos}</style>", unsafe_allow_html=True)
    st.title("◈ RSA STUDIO")
    st.markdown('<p class="rsa-eyebrow">CRIPTOGRAFÍA / DASHBOARD ACADÉMICO</p>'
                '<p class="rsa-status">● RSA / WEB</p>', unsafe_allow_html=True)
    for pestaña, operacion in zip(st.tabs(["01 ENCRIPTAR", "02 DESENCRIPTAR"]),
                                 ("encriptar", "desencriptar")):
        with pestaña:
            _pagina(operacion)
    st.info("Demostración académica. No utilices esta implementación para proteger información real.")
    st.markdown('<p class="rsa-footer">MM2015 / PROYECTO RSA</p>', unsafe_allow_html=True)
