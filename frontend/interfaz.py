"""Interfaz gráfica para las operaciones RSA."""

import tkinter as tk
from tkinter import messagebox, ttk

from backend.rsa import encriptar, desencriptar
from backend.validaciones import convertir_entero

FONDO = "#0A1128"
PANEL = "#001F54"
SECUNDARIO = "#034078"
ACENTO = "#1282A2"
BLANCO = "#FEFCFB"
MUTED = "#B5C8DB"
BORDE = "#184875"
EXITO = "#5DE1B4"
ERROR = "#FF9DAD"
FUENTE = "Segoe UI"


def _rectangulo_redondo(lienzo: tk.Canvas, x1: int, y1: int,
                       x2: int, y2: int, radio: int, color: str) -> None:
    """Dibuja un rectángulo redondeado."""
    if x2 <= x1 or y2 <= y1:
        return
    r = min(radio, (x2-x1)//2, (y2-y1)//2)
    puntos = [x1+r,y1,x2-r,y1,x2,y1,x2,y1+r,x2,y2-r,x2,y2,
              x2-r,y2,x1+r,y2,x1,y2,x1,y2-r,x1,y1+r,x1,y1]
    lienzo.create_polygon(puntos, smooth=True, splinesteps=12,
                          fill=color, outline="", tags="fondo_tarjeta")


class Tarjeta(tk.Canvas):
    """Panel de contenido."""

    def __init__(self, padre: tk.Widget, *, color: str = PANEL,
                 margen: int = 20, **opciones) -> None:
        super().__init__(padre, bg=FONDO, highlightthickness=0,
                         bd=0, **opciones)
        self.color = color
        self.margen = margen
        self.interior = tk.Frame(self, bg=color)
        self.ventana = self.create_window(margen, margen,
                                          anchor="nw", window=self.interior)
        self.bind("<Configure>", self._redibujar)
        self.interior.bind("<Configure>", self._ajustar_alto)

    def _ajustar_alto(self, _evento=None) -> None:
        alto = self.interior.winfo_reqheight() + 2*self.margen
        if self.winfo_height() != alto:
            self.configure(height=alto)

    def _redibujar(self, evento: tk.Event) -> None:
        self.delete("fondo_tarjeta")
        _rectangulo_redondo(self, 1, 1, evento.width-1,
                           evento.height-1, 18, self.color)
        self.tag_lower("fondo_tarjeta")
        self.itemconfigure(self.ventana, width=max(1, evento.width-2*self.margen))


def etiqueta(padre: tk.Widget, texto: str, *, tam: int = 11,
             color: str = BLANCO, negrita: bool = False,
             fondo: str = PANEL, **opciones) -> tk.Label:
    """Crea una etiqueta."""
    return tk.Label(padre, text=texto, bg=fondo, fg=color,
                    font=(FUENTE, tam, "bold" if negrita else "normal"),
                    anchor="w", **opciones)


class Boton(tk.Label):
    """Control de acción."""

    def __init__(self, padre: tk.Widget, texto: str, comando,
                 *, principal: bool = True) -> None:
        self.normal = ACENTO if principal else SECUNDARIO
        self.hover = "#159BBB" if principal else "#0B5792"
        super().__init__(padre, text=texto, bg=self.normal, fg=BLANCO,
                         font=(FUENTE, 11, "bold"), padx=18, pady=11,
                         cursor="hand2", takefocus=True)
        self.comando = comando
        self.bind("<Enter>", lambda _: self.configure(bg=self.hover))
        self.bind("<Leave>", lambda _: self.configure(bg=self.normal))
        self.bind("<Button-1>", lambda _: self.comando())
        self.bind("<Return>", lambda _: self.comando())
        self.bind("<space>", lambda _: self.comando())
        self.bind("<FocusIn>", lambda _: self.configure(relief="solid", bd=1))
        self.bind("<FocusOut>", lambda _: self.configure(relief="flat", bd=0))


class PaginaDesplazable(tk.Frame):
    """Contenedor desplazable."""

    def __init__(self, padre: tk.Widget) -> None:
        super().__init__(padre, bg=FONDO)
        self.lienzo = tk.Canvas(self, bg=FONDO, bd=0, highlightthickness=0)
        barra = ttk.Scrollbar(self, orient="vertical", command=self.lienzo.yview)
        self.lienzo.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        self.lienzo.pack(side="left", fill="both", expand=True)
        self.contenido = tk.Frame(self.lienzo, bg=FONDO)
        self.ventana = self.lienzo.create_window(0, 0, window=self.contenido,
                                                anchor="nw")
        self.contenido.bind("<Configure>", lambda _: self.lienzo.configure(
            scrollregion=self.lienzo.bbox("all")))
        self.lienzo.bind("<Configure>", lambda evento: self.lienzo.itemconfigure(
            self.ventana, width=evento.width))
        self.bind("<Enter>", self._activar_rueda)
        self.bind("<Leave>", self._desactivar_rueda)

    def _activar_rueda(self, _evento) -> None:
        self.bind_all("<MouseWheel>", self._rueda)
        self.bind_all("<Button-4>", self._rueda)
        self.bind_all("<Button-5>", self._rueda)

    def _desactivar_rueda(self, _evento) -> None:
        self.unbind_all("<MouseWheel>")
        self.unbind_all("<Button-4>")
        self.unbind_all("<Button-5>")

    def _rueda(self, evento) -> None:
        if getattr(evento, "num", None) == 4:
            paso = -3
        elif getattr(evento, "num", None) == 5:
            paso = 3
        else:
            paso = -int(evento.delta / 120) * 3
        self.lienzo.yview_scroll(paso, "units")


class AplicacionRSA(tk.Tk):
    """Ventana principal de la aplicación RSA."""

    def __init__(self) -> None:
        super().__init__()
        self.title("RSA Studio  |  Matemática Discreta")
        self.geometry("1160x820")
        self.minsize(750, 560)
        self.configure(bg=FONDO)
        self._estilos_tabla()
        self.pagina_actual = "encriptar"
        self.estado = tk.StringVar(value="Listo para operar  •  ASCII 32–126")
        self._crear_cabecera()
        self.area = tk.Frame(self, bg=FONDO)
        self.area.pack(fill="both", expand=True, padx=22, pady=(0, 12))
        self.paginas = {}
        for operacion in ("encriptar", "desencriptar"):
            pagina = PaginaDesplazable(self.area)
            self.paginas[operacion] = pagina
            self._construir_pagina(pagina.contenido, operacion)
        etiqueta(self, "MM2015  /  PROYECTO RSA", tam=9, color=MUTED,
                 fondo=FONDO).pack(side="bottom", anchor="w", padx=26, pady=(0, 10))
        self._mostrar_pagina("encriptar")

    def _estilos_tabla(self) -> None:
        estilo = ttk.Style(self)
        if "clam" in estilo.theme_names():
            estilo.theme_use("clam")
        estilo.configure("RSA.Treeview", background=PANEL, fieldbackground=PANEL,
                         foreground=BLANCO, rowheight=34, borderwidth=0,
                         font=(FUENTE, 10))
        estilo.configure("RSA.Treeview.Heading", background=SECUNDARIO,
                         foreground=BLANCO, relief="flat", padding=9,
                         font=(FUENTE, 10, "bold"))
        estilo.map("RSA.Treeview", background=[("selected", ACENTO)],
                   foreground=[("selected", BLANCO)])
        estilo.configure("RSA.Vertical.TScrollbar", background=SECUNDARIO,
                         troughcolor=PANEL, arrowcolor=BLANCO)

    def _crear_cabecera(self) -> None:
        cabecera = tk.Frame(self, bg=FONDO)
        cabecera.pack(fill="x", padx=26, pady=(22, 14))
        izquierda = tk.Frame(cabecera, bg=FONDO)
        izquierda.pack(side="left", fill="x", expand=True)
        etiqueta(izquierda, "◈  RSA STUDIO", tam=21, negrita=True,
                 fondo=FONDO).pack(anchor="w")
        etiqueta(izquierda, "CRIPTOGRAFÍA  /  DASHBOARD ACADÉMICO", tam=9,
                 color=MUTED, fondo=FONDO).pack(anchor="w", pady=(3, 0))
        self.navegacion = tk.Frame(self, bg=FONDO)
        self.navegacion.pack(fill="x", padx=26, pady=(0, 16))
        self.botones_nav = {}
        for clave, texto in (("encriptar", "01   ENCRIPTAR"),
                             ("desencriptar", "02   DESENCRIPTAR")):
            boton = tk.Label(self.navegacion, text=texto, font=(FUENTE, 11, "bold"),
                             fg=BLANCO, padx=22, pady=12, cursor="hand2",
                             takefocus=True)
            boton.pack(side="left", padx=(0, 10))
            boton.bind("<Button-1>", lambda _, c=clave: self._mostrar_pagina(c))
            boton.bind("<Return>", lambda _, c=clave: self._mostrar_pagina(c))
            boton.bind("<space>", lambda _, c=clave: self._mostrar_pagina(c))
            self.botones_nav[clave] = boton
        etiqueta(self.navegacion, "●  RSA / LOCAL", color=EXITO, tam=10,
                 fondo=FONDO).pack(side="right")

    def _mostrar_pagina(self, operacion: str) -> None:
        self.pagina_actual = operacion
        for pagina in self.paginas.values():
            pagina.pack_forget()
        self.paginas[operacion].pack(fill="both", expand=True)
        for clave, boton in self.botones_nav.items():
            boton.configure(bg=ACENTO if clave == operacion else PANEL)

    def _tarjeta(self, padre: tk.Widget, titulo: str,
                 subtitulo: str = "") -> tk.Frame:
        tarjeta = Tarjeta(padre)
        tarjeta.pack(fill="x", pady=(0, 14))
        interior = tarjeta.interior
        etiqueta(interior, titulo, tam=14, negrita=True).pack(anchor="w")
        if subtitulo:
            etiqueta(interior, subtitulo, tam=10, color=MUTED,
                     wraplength=850, justify="left").pack(anchor="w", pady=(4, 15))
        else:
            tk.Frame(interior, height=13, bg=PANEL).pack()
        return interior

    def _entrada(self, padre: tk.Widget, nombre: str, valor: str = "") -> tk.Entry:
        contenedor = tk.Frame(padre, bg=PANEL)
        contenedor.pack(side="left", fill="x", expand=True, padx=(0, 12))
        etiqueta(contenedor, nombre, tam=10, color=MUTED).pack(anchor="w", pady=(0, 6))
        campo = tk.Entry(contenedor, bg=SECUNDARIO, fg=BLANCO,
                         insertbackground=BLANCO, relief="flat",
                         highlightthickness=1, highlightbackground=BORDE,
                         highlightcolor=ACENTO, font=(FUENTE, 12),
                         bd=0, width=12)
        campo.insert(0, valor)
        campo.pack(fill="x", ipady=11)
        return campo

    def _texto(self, padre: tk.Widget, alto: int = 3,
               solo_lectura: bool = False) -> tk.Text:
        campo = tk.Text(padre, height=alto, wrap="none", bg=SECUNDARIO,
                        fg=BLANCO, insertbackground=BLANCO, selectbackground=ACENTO,
                        relief="flat", highlightthickness=1,
                        highlightbackground=BORDE, highlightcolor=ACENTO,
                        font=("Consolas", 11), padx=12, pady=10, undo=True)
        campo.pack(fill="x")
        if solo_lectura:
            campo.configure(state="disabled")
        return campo

    def _resultado(self, padre: tk.Widget, titulo: str,
                   *, con_copia: bool = False) -> tuple[tk.Text, tk.Frame]:
        interior = self._tarjeta(padre, titulo)
        campo = self._texto(interior, 2, solo_lectura=True)
        if con_copia:
            Boton(interior, "⧉  COPIAR RESULTADO",
                  lambda: self._copiar(campo.get("1.0", "end-1c")),
                  principal=False).pack(anchor="e", pady=(12, 0))
        return campo, interior

    def _tabla(self, padre: tk.Widget) -> ttk.Treeview:
        interior = self._tarjeta(
            padre, "Detalle de bloques",
            "Cada fila conserva los caracteres, códigos ASCII y bloques numéricos."
        )
        marco = tk.Frame(interior, bg=PANEL)
        marco.pack(fill="both", expand=True)
        columnas = ("numero", "pareja", "ascii", "m", "c")
        tabla = ttk.Treeview(marco, columns=columnas, show="headings",
                             height=7, style="RSA.Treeview")
        for clave, titulo, ancho in zip(columnas,
                                       ("N.º", "Caracteres", "ASCII", "Bloque m", "Bloque c"),
                                       (62, 140, 160, 160, 160)):
            tabla.heading(clave, text=titulo)
            tabla.column(clave, width=ancho, minwidth=55, anchor="center")
        barra = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=barra.set)
        tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        tabla.tag_configure("alterno", background="#092D5E")
        return tabla

    def _construir_pagina(self, padre: tk.Widget, operacion: str) -> None:
        es_cifrado = operacion == "encriptar"
        titulo = "Encriptar mensaje" if es_cifrado else "Desencriptar mensaje"
        descripcion = ("Transforma texto ASCII en bloques RSA de seis dígitos."
                       if es_cifrado else
                       "Recupera exactamente el mensaje utilizando C y L.")
        encabezado = tk.Frame(padre, bg=FONDO)
        encabezado.pack(fill="x", pady=(2, 16))
        etiqueta(encabezado, titulo, tam=23, negrita=True,
                 fondo=FONDO).pack(anchor="w")
        etiqueta(encabezado, descripcion, tam=11, color=MUTED,
                 fondo=FONDO).pack(anchor="w", pady=(4, 0))

        tarjeta = self._tarjeta(padre, "Parámetros RSA",
                              "Dos primos distintos y un exponente público coprimo con φ.")
        fila = tk.Frame(tarjeta, bg=PANEL)
        fila.pack(fill="x")
        entradas = {nombre: self._entrada(fila, nombre, valor)
                    for nombre, valor in (("p", "367"), ("q", "373"), ("e", "17"))}
        setattr(self, f"parametros_{operacion}", entradas)

        if es_cifrado:
            tarjeta = self._tarjeta(padre, "Mensaje original · M",
                                  "ASCII imprimible (32–126). Los espacios se conservan.")
            self.entrada_mensaje = self._texto(tarjeta, 4)
        else:
            tarjeta = self._tarjeta(padre, "Mensaje cifrado · C",
                                  "Pega los bloques de seis dígitos separados por un espacio.")
            self.entrada_cifrado = self._texto(tarjeta, 3)
            fila_l = tk.Frame(tarjeta, bg=PANEL)
            fila_l.pack(fill="x", pady=(12, 0))
            self.entrada_longitud = self._entrada(fila_l, "Longitud original · L")

        acciones = tk.Frame(padre, bg=FONDO)
        acciones.pack(fill="x", pady=(0, 14))
        Boton(acciones, "↗  ENCRIPTAR" if es_cifrado else "↙  DESENCRIPTAR",
              self._encriptar if es_cifrado else self._desencriptar).pack(side="left")
        self.estado_widgets = getattr(self, "estado_widgets", {})
        estado = etiqueta(acciones, "●  Esperando datos", tam=10, color=MUTED,
                          fondo=FONDO)
        estado.pack(side="left", padx=16)
        self.estado_widgets[operacion] = estado

        tarjeta = self._tarjeta(padre, "Resumen matemático",
                              "Valores calculados y datos necesarios para recuperar el texto.")
        grilla = tk.Frame(tarjeta, bg=PANEL)
        grilla.pack(fill="x")
        claves = (("n", "MÓDULO n"), ("phi", "FUNCIÓN φ"),
                  ("mcd", "MCD(e, φ)"), ("l", "LONGITUD L"),
                  ("relleno", "RELLENO"), ("clave", "CLAVE RSA"))
        valores = {}
        for indice, (clave, nombre) in enumerate(claves):
            celda = tk.Frame(grilla, bg=SECUNDARIO, padx=12, pady=10)
            celda.grid(row=indice//3, column=indice%3, sticky="nsew",
                       padx=4, pady=4)
            etiqueta(celda, nombre, tam=9, color=MUTED,
                     fondo=SECUNDARIO).pack(anchor="w")
            valor = tk.StringVar(value="—")
            etiqueta(celda, "", tam=12, negrita=True, fondo=SECUNDARIO,
                     textvariable=valor, wraplength=250,
                     justify="left").pack(anchor="w", pady=(5, 0))
            valores[clave] = valor
        for columna in range(3):
            grilla.grid_columnconfigure(columna, weight=1, uniform="resumen")
        setattr(self, f"resumen_{operacion}", valores)

        if es_cifrado:
            self.salida_cifrado, _ = self._resultado(
                padre, "Resultado · Cifrado C", con_copia=True)
            barra_l = tk.Frame(padre, bg=FONDO)
            barra_l.pack(fill="x", pady=(0, 12))
            Boton(barra_l, "⧉  COPIAR L", self._copiar_longitud,
                  principal=False).pack(side="left")
        else:
            self.salida_mensaje, _ = self._resultado(
                padre, "Resultado · Mensaje original M", con_copia=True)
        tabla = self._tabla(padre)
        setattr(self, f"tabla_{operacion}", tabla)

    @staticmethod
    def _escribir(campo: tk.Text, texto: str) -> None:
        """Actualiza un campo de texto."""
        campo.configure(state="normal")
        campo.delete("1.0", "end")
        campo.insert("1.0", texto)
        campo.configure(state="disabled")

    @staticmethod
    def _limpiar_tabla(tabla: ttk.Treeview) -> None:
        for fila in tabla.get_children():
            tabla.delete(fila)

    def _limpiar(self, operacion: str) -> None:
        for valor in getattr(self, f"resumen_{operacion}").values():
            valor.set("—")
        self._limpiar_tabla(getattr(self, f"tabla_{operacion}"))
        self._escribir(self.salida_cifrado if operacion == "encriptar"
                       else self.salida_mensaje, "")
        self.estado_widgets[operacion].configure(text="●  Esperando datos", fg=MUTED)

    def _detalles(self, operacion: str, detalles) -> None:
        tabla = getattr(self, f"tabla_{operacion}")
        self._limpiar_tabla(tabla)
        for indice, bloque in enumerate(detalles):
            tabla.insert("", "end", values=(
                bloque.numero, repr(bloque.caracteres), bloque.ascii,
                bloque.bloque_original, bloque.bloque_cifrado),
                tags=("alterno",) if indice % 2 else ())

    def _mostrar_resumen(self, operacion: str, resultado) -> None:
        datos = resultado.parametros
        valores = getattr(self, f"resumen_{operacion}")
        valores["n"].set(str(datos.n))
        valores["phi"].set(str(datos.phi))
        valores["mcd"].set(str(datos.mcd))
        valores["l"].set(str(resultado.longitud))
        valores["relleno"].set("Sí · espacio 032" if resultado.relleno else "No")
        if operacion == "encriptar":
            valores["clave"].set(f"Pública ({datos.e}, {datos.n})")
        else:
            valores["clave"].set(
                f"d = {resultado.exponente_privado}  ·  Privada "
                f"({resultado.exponente_privado}, {datos.n})")
        self._detalles(operacion, resultado.detalles)
        self.estado_widgets[operacion].configure(text="●  Operación completada", fg=EXITO)

    def _leer_parametros(self, operacion: str) -> tuple[int, int, int]:
        campos = getattr(self, f"parametros_{operacion}")
        return tuple(convertir_entero(campos[clave].get(), clave)
                     for clave in ("p", "q", "e"))

    def _encriptar(self) -> None:
        self._limpiar("encriptar")
        try:
            p, q, e = self._leer_parametros("encriptar")
            mensaje = self.entrada_mensaje.get("1.0", "end-1c")
            resultado = encriptar(mensaje, p, q, e)
        except (TypeError, ValueError) as error:
            self._error("encriptar", error)
            return
        self._mostrar_resumen("encriptar", resultado)
        self._escribir(self.salida_cifrado, resultado.cifrado)

    def _desencriptar(self) -> None:
        self._limpiar("desencriptar")
        try:
            p, q, e = self._leer_parametros("desencriptar")
            longitud = convertir_entero(self.entrada_longitud.get(), "L")
            cifrado = self.entrada_cifrado.get("1.0", "end-1c")
            resultado = desencriptar(cifrado, longitud, p, q, e)
        except (TypeError, ValueError) as error:
            self._error("desencriptar", error)
            return
        self._mostrar_resumen("desencriptar", resultado)
        self._escribir(self.salida_mensaje, resultado.mensaje)

    def _error(self, operacion: str, error: Exception) -> None:
        self.estado_widgets[operacion].configure(text="●  Revisa los datos", fg=ERROR)
        messagebox.showerror("Validación RSA", str(error), parent=self)

    def _copiar(self, contenido: str) -> None:
        """Copia el contenido al portapapeles."""
        if not contenido:
            messagebox.showinfo("Sin resultado", "Primero realiza una operación.",
                                parent=self)
            return
        self.clipboard_clear()
        self.clipboard_append(contenido)
        self.update_idletasks()
        self.estado_widgets[self.pagina_actual].configure(
            text="●  Copiado al portapapeles", fg=EXITO)

    def _copiar_longitud(self) -> None:
        longitud = self.resumen_encriptar["l"].get()
        self._copiar("" if longitud == "—" else longitud)
