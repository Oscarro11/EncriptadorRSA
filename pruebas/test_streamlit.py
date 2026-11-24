"""Pruebas de los flujos web con el ejecutor oficial de Streamlit."""

from pathlib import Path
import unittest

from streamlit.testing.v1 import AppTest


APP = Path(__file__).resolve().parents[1] / "app_streamlit.py"


class PruebasWeb(unittest.TestCase):
    def setUp(self):
        self.app = AppTest.from_file(str(APP), default_timeout=15).run()
        self.assertFalse(self.app.exception)

    def encriptar(self, mensaje):
        self.app.text_area(key="mensaje").set_value(mensaje)
        self.app.button[0].click().run()
        self.assertFalse(self.app.exception)

    def desencriptar(self, cifrado, longitud):
        self.app.text_area(key="cifrado").set_value(cifrado)
        self.app.text_input(key="longitud").set_value(str(longitud))
        self.app.button[1].click().run()
        self.assertFalse(self.app.exception)

    def test_ejemplo_y_espacios(self):
        for mensaje in ("RSA", "  A  ", " ", "AB  "):
            self.encriptar(mensaje)
            resultado = self.app.session_state["resultado_encriptar"]
            if mensaje == "RSA":
                self.assertEqual(resultado.cifrado, "026054 123875")
                self.assertEqual(resultado.longitud, 3)
                self.assertEqual(self.app.dataframe[0].value.iloc[0]["Bloque c"], "026054")
            self.desencriptar(resultado.cifrado, resultado.longitud)
            recuperado = self.app.session_state["resultado_desencriptar"]
            self.assertEqual(recuperado.mensaje, mensaje)
            self.assertIn(mensaje, [bloque.value for bloque in self.app.code])

    def test_error_limpia_resultado(self):
        self.encriptar("RSA")
        self.encriptar("ñ")
        self.assertIsNone(self.app.session_state["resultado_encriptar"])
        self.assertTrue(self.app.error)
        self.assertEqual(len(self.app.dataframe), 0)
        self.desencriptar("026054 123875", 3)
        self.desencriptar("026054 123875", 2)
        self.assertIsNone(self.app.session_state["resultado_desencriptar"])

    def test_limites_y_exponente_mayor_que_phi(self):
        self.app.text_input(key="encriptar_e").set_value("136169")
        self.encriptar("RSA")
        self.assertEqual(self.app.session_state["resultado_encriptar"].cifrado, "026054 123875")
        self.app.text_input(key="encriptar_p").set_value("999999999999999999999")
        self.encriptar("RSA")
        self.assertIsNone(self.app.session_state["resultado_encriptar"])
        self.assertTrue(self.app.error)
        self.app.text_input(key="encriptar_p").set_value("367")
        self.encriptar("A" * 2001)
        self.assertIsNone(self.app.session_state["resultado_encriptar"])

    def test_sesiones_independientes(self):
        self.encriptar("RSA")
        otra = AppTest.from_file(str(APP), default_timeout=15).run()
        self.assertFalse(otra.exception)
        self.assertEqual(len(otra.code), 0)
        self.assertEqual(self.app.session_state["resultado_encriptar"].mensaje, "RSA")


if __name__ == "__main__":
    unittest.main()
