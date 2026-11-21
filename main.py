"""Punto de entrada de la aplicación RSA."""

from frontend.interfaz import AplicacionRSA


def main() -> None:
    """Inicia la ventana principal."""
    aplicacion = AplicacionRSA()
    aplicacion.mainloop()


if __name__ == "__main__":
    main()
