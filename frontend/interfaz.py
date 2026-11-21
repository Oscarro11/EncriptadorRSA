"""Interfaz gráfica RSA con tkinter y ttk."""

import tkinter as tk
from tkinter import messagebox, ttk

from backend.modelos import DetalleBloque
from backend.rsa import desencriptar, encriptar
from backend.validaciones import convertir_entero


class AplicacionRSA(tk.Tk):
    """Ventana con pestañas para encriptar y desencriptar."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Proyecto RSA - Matemática Discreta")
        self.geometry("1020x750")
        self.minsize(820, 620)
        self._configurar_estilo()

        self.p_enc = tk.StringVar(value="367")
        self.q_enc = tk.StringVar(value="373")
        self.e_enc = tk.StringVar(value="17")
        self.p_des = tk.StringVar(value="367")
        self.q_des = tk.StringVar(value="373")
        self.e_des = tk.StringVar(value="17")
        self.longitud_des = tk.StringVar()

        self.pestanas = ttk.Notebook(self)
        self.pestanas.pack(fill="both", expand=True, padx=14, pady=14)
        self.pagina_enc = ttk.Frame(self.pestanas, padding=12)
        self.pagina_des = ttk.Frame(self.pestanas, padding=12)
        self.pestanas.add(self.pagina_enc, text="Encriptar")
        self.pestanas.add(self.pagina_des, text="Desencriptar")
        self._crear_encriptacion()
        self._crear_desencriptacion()

    def _configurar_estilo(self) -> None:
        """Aplica un estilo sencillo a los controles."""
        estilo = ttk.Style(self)
        if "clam" in estilo.theme_names():
            estilo.theme_use("clam")
        estilo.configure("Titulo.TLabel", font=("Arial", 16, "bold"))
        estilo.configure("Subtitulo.TLabel", font=("Arial", 10, "bold"))
        estilo.configure("Treeview", rowheight=26)
        estilo.configure("Treeview.Heading", font=("Arial", 10, "bold"))

    def _crear_parametros(
        self, padre: ttk.Frame, p: tk.StringVar,
        q: tk.StringVar, e: tk.StringVar
    ) -> None:
        """Construye los tres campos de parámetros RSA."""
        marco = ttk.LabelFrame(padre, text="Parámetros RSA", padding=10)
        marco.pack(fill="x", pady=(0, 10))
        for columna, (nombre, variable) in enumerate(
            (("p (primo)", p), ("q (primo)", q), ("e (exponente)", e))
        ):
            marco.columnconfigure(columna, weight=1)
            ttk.Label(marco, text=nombre).grid(
                row=0, column=columna, sticky="w", padx=5
            )
            ttk.Entry(marco, textvariable=variable, width=16).grid(
                row=1, column=columna, sticky="ew", padx=5, pady=4
            )

    def _crear_texto(self, padre: ttk.Frame, titulo: str, alto: int = 3) -> tk.Text:
        """Crea un campo de texto con desplazamiento horizontal."""
        marco = ttk.LabelFrame(padre, text=titulo, padding=8)
        marco.pack(fill="x", pady=(0, 10))
        texto = tk.Text(marco, height=alto, wrap="none", font=("Consolas", 11))
        barra = ttk.Scrollbar(marco, orient="horizontal", command=texto.xview)
        texto.configure(xscrollcommand=barra.set)
        texto.pack(fill="x")
        barra.pack(fill="x")
        return texto

    def _crear_detalles(self, padre: ttk.Frame) -> ttk.Treeview:
        """Crea la tabla de conversión ASCII y bloques RSA."""
        marco = ttk.LabelFrame(padre, text="Detalle de bloques", padding=8)
        marco.pack(fill="both", expand=True, pady=(10, 0))
        columnas = ("numero", "caracteres", "ascii", "original", "cifrado")
        tabla = ttk.Treeview(marco, columns=columnas, show="headings", height=7)
        titulos = ("N.º", "Pareja", "Códigos ASCII", "Bloque m", "Bloque c")
        anchos = (55, 140, 155, 145, 145)
        for columna, titulo, ancho in zip(columnas, titulos, anchos):
            tabla.heading(columna, text=titulo)
            tabla.column(columna, width=ancho, minwidth=70 if ancho > 55 else 45,
                         anchor="center", stretch=True)
        barra = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=barra.set)
        tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        return tabla

    def _crear_encriptacion(self) -> None:
        """Construye la pestaña de encriptación."""
        padre = self.pagina_enc
        ttk.Label(padre, text="Encriptación RSA", style="Titulo.TLabel").pack(
            anchor="w", pady=(0, 10)
        )
        self._crear_parametros(padre, self.p_enc, self.q_enc, self.e_enc)
        self.mensaje_enc = self._crear_texto(padre, "Mensaje original M (ASCII 32 a 126)")
        ttk.Button(padre, text="Encriptar mensaje", command=self._encriptar).pack(
            anchor="w", pady=(0, 10)
        )
        self.resumen_enc = tk.StringVar(value="n: —    φ: —    MCD(e, φ): —    L: —    Relleno: —")
        ttk.Label(padre, textvariable=self.resumen_enc, wraplength=900).pack(
            anchor="w", pady=(0, 5)
        )
        self.clave_enc = tk.StringVar(value="Llave pública (e, n): —")
        ttk.Label(padre, textvariable=self.clave_enc).pack(anchor="w", pady=(0, 5))
        self.cifrado_enc = self._crear_texto(padre, "Cifrado C (copiar junto con L)", 2)
        self.cifrado_enc.configure(state="disabled")
        self.tabla_enc = self._crear_detalles(padre)

    def _crear_desencriptacion(self) -> None:
        """Construye la pestaña de desencriptación."""
        padre = self.pagina_des
        ttk.Label(padre, text="Desencriptación RSA", style="Titulo.TLabel").pack(
            anchor="w", pady=(0, 10)
        )
        self._crear_parametros(padre, self.p_des, self.q_des, self.e_des)
        self.cifrado_des = self._crear_texto(
            padre, "Cifrado C (bloques de seis dígitos separados por un espacio)", 2
        )
        marco_l = ttk.Frame(padre)
        marco_l.pack(fill="x", pady=(0, 10))
        ttk.Label(marco_l, text="Longitud original L:").pack(side="left")
        ttk.Entry(marco_l, textvariable=self.longitud_des, width=12).pack(
            side="left", padx=10
        )
        ttk.Button(padre, text="Desencriptar mensaje", command=self._desencriptar).pack(
            anchor="w", pady=(0, 10)
        )
        self.resumen_des = tk.StringVar(value="n: —    φ: —    L: —    Relleno: —")
        ttk.Label(padre, textvariable=self.resumen_des, wraplength=900).pack(
            anchor="w", pady=(0, 5)
        )
        self.clave_des = tk.StringVar(value="Exponente privado d: —    Llave privada (d, n): —")
        ttk.Label(padre, textvariable=self.clave_des).pack(anchor="w", pady=(0, 5))
        self.mensaje_des = self._crear_texto(padre, "Mensaje original recuperado M", 2)
        self.mensaje_des.configure(state="disabled")
        self.tabla_des = self._crear_detalles(padre)

    @staticmethod
    def _poner_texto(campo: tk.Text, contenido: str) -> None:
        """Sustituye el contenido sin modificar los espacios del mensaje."""
        campo.configure(state="normal")
        campo.delete("1.0", "end")
        campo.insert("1.0", contenido)
        campo.configure(state="disabled")

    @staticmethod
    def _mostrar_detalles(tabla: ttk.Treeview, detalles: list[DetalleBloque]) -> None:
        """Carga las parejas ASCII y los bloques en la tabla."""
        for elemento in tabla.get_children():
            tabla.delete(elemento)
        for detalle in detalles:
            # repr permite distinguir espacios iniciales y finales.
            tabla.insert("", "end", values=(
                detalle.numero, repr(detalle.caracteres), detalle.ascii,
                detalle.bloque_original, detalle.bloque_cifrado,
            ))

    def _limpiar_encriptacion(self) -> None:
        """Elimina resultados anteriores antes de un nuevo intento."""
        self.resumen_enc.set("n: —    φ: —    MCD(e, φ): —    L: —    Relleno: —")
        self.clave_enc.set("Llave pública (e, n): —")
        self._poner_texto(self.cifrado_enc, "")
        self._mostrar_detalles(self.tabla_enc, [])

    def _limpiar_desencriptacion(self) -> None:
        """Elimina resultados anteriores antes de un nuevo intento."""
        self.resumen_des.set("n: —    φ: —    L: —    Relleno: —")
        self.clave_des.set("Exponente privado d: —    Llave privada (d, n): —")
        self._poner_texto(self.mensaje_des, "")
        self._mostrar_detalles(self.tabla_des, [])

    def _encriptar(self) -> None:
        """Lee entradas, encripta y presenta el resultado."""
        self._limpiar_encriptacion()
        try:
            p = convertir_entero(self.p_enc.get(), "p")
            q = convertir_entero(self.q_enc.get(), "q")
            e = convertir_entero(self.e_enc.get(), "e")
            # end-1c elimina solo el salto que tkinter agrega al Text.
            mensaje = self.mensaje_enc.get("1.0", "end-1c")
            resultado = encriptar(mensaje, p, q, e)
        except (TypeError, ValueError) as error:
            messagebox.showerror("Error de validación", str(error), parent=self)
            return

        datos = resultado.parametros
        self.resumen_enc.set(
            f"n: {datos.n}    φ: {datos.phi}    MCD(e, φ): {datos.mcd}    "
            f"L: {resultado.longitud}    Relleno: {'Sí' if resultado.relleno else 'No'}"
        )
        self.clave_enc.set(f"Llave pública (e, n): ({datos.e}, {datos.n})")
        self._poner_texto(self.cifrado_enc, resultado.cifrado)
        self._mostrar_detalles(self.tabla_enc, resultado.detalles)

    def _desencriptar(self) -> None:
        """Lee C y L, desencripta y presenta el resultado."""
        self._limpiar_desencriptacion()
        try:
            p = convertir_entero(self.p_des.get(), "p")
            q = convertir_entero(self.q_des.get(), "q")
            e = convertir_entero(self.e_des.get(), "e")
            longitud = convertir_entero(self.longitud_des.get(), "L")
            cifrado = self.cifrado_des.get("1.0", "end-1c")
            resultado = desencriptar(cifrado, longitud, p, q, e)
        except (TypeError, ValueError) as error:
            messagebox.showerror("Error de validación", str(error), parent=self)
            return

        datos = resultado.parametros
        self.resumen_des.set(
            f"n: {datos.n}    φ: {datos.phi}    L: {resultado.longitud}    "
            f"Relleno: {'Sí' if resultado.relleno else 'No'}"
        )
        self.clave_des.set(
            f"Exponente privado d: {resultado.exponente_privado}    "
            f"Llave privada (d, n): ({resultado.exponente_privado}, {datos.n})"
        )
        self._poner_texto(self.mensaje_des, resultado.mensaje)
        self._mostrar_detalles(self.tabla_des, resultado.detalles)
