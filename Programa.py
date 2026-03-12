
# ---------------------------------------------------------------------------
# IMPORTACIONES
# ---------------------------------------------------------------------------
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os

# ---------------------------------------------------------------------------
# CONSTANTES DE CONFIGURACIÓN
# ---------------------------------------------------------------------------

# Nombre del archivo de base de datos que se creará en la carpeta del script
NOMBRE_BD = "inventario.db"

# Stock mínimo por defecto para nuevos productos
STOCK_MINIMO_DEFAULT = 5

# Paleta de colores de la interfaz (tonos suaves, femeninos y profesionales)
COLOR_FONDO          = "#FDF6F0"   # Blanco cálido (fondo principal)
COLOR_PANEL          = "#FFFFFF"   # Blanco puro (paneles de formulario)
COLOR_ACENTO         = "#C9748F"   # Rosa oscuro (botones principales)
COLOR_ACENTO_HOVER   = "#B05C78"   # Rosa más oscuro (hover de botones)
COLOR_ALERTA         = "#E07B54"   # Naranja suave (botón de alerta)
COLOR_ALERTA_HOVER   = "#C8613C"   # Naranja más oscuro (hover alerta)
COLOR_ELIMINAR       = "#D9534F"   # Rojo suave (botón eliminar)
COLOR_ELIMINAR_HOVER = "#C9302C"   # Rojo más oscuro (hover eliminar)
COLOR_TEXTO          = "#3D2B2B"   # Marrón oscuro (texto principal)
COLOR_TEXTO_SUAVE    = "#7A6060"   # Marrón medio (etiquetas secundarias)
COLOR_BORDE          = "#E8D5CB"   # Rosa claro (bordes y separadores)
COLOR_TABLA_FILA1    = "#FFFFFF"   # Blanco (filas pares de la tabla)
COLOR_TABLA_FILA2    = "#FFF0EC"   # Rosado muy suave (filas impares)
COLOR_ENCABEZADO     = "#C9748F"   # Rosa (encabezado de la tabla)

# Fuentes
FUENTE_TITULO  = ("Segoe UI", 16, "bold")
FUENTE_SUBTIT  = ("Segoe UI", 11, "bold")
FUENTE_NORMAL  = ("Segoe UI", 10)
FUENTE_TABLA   = ("Segoe UI", 10)
FUENTE_BOTON   = ("Segoe UI", 10, "bold")


# ---------------------------------------------------------------------------
# CAPA DE DATOS — Manejo de la base de datos SQLite
# ---------------------------------------------------------------------------

class BaseDeDatos:
    """
    Gestiona toda la comunicación con la base de datos SQLite.

    Esta clase encapsula (agrupa) las operaciones de base de datos para que
    el resto del código no tenga que preocuparse por SQL directamente.

    Atributos:
        ruta_bd (str): Ruta completa al archivo inventario.db
    """

    def __init__(self):
        """
        Constructor: define la ruta de la BD y crea la tabla si no existe.
        Se ejecuta automáticamente al crear un objeto BaseDeDatos().
        """
        # Guardamos la BD en la misma carpeta donde está este script
        carpeta_script = os.path.dirname(os.path.abspath(__file__))
        self.ruta_bd = os.path.join(carpeta_script, NOMBRE_BD)

        # Creamos la tabla de productos si aún no existe
        self._crear_tabla()

    def _crear_tabla(self):
        """
        Crea la tabla 'productos' en la BD si todavía no existe.
        El prefijo '_' indica que es un método interno (uso privado).

        Columnas de la tabla:
            id           : Número único que identifica cada producto (PK autoincremental)
            nombre       : Nombre del producto (texto, obligatorio)
            precio       : Precio en COP (número decimal, obligatorio)
            cantidad     : Unidades disponibles actualmente (entero, obligatorio)
            stock_minimo : Cantidad mínima antes de lanzar alerta (entero, obligatorio)
        """
        with sqlite3.connect(self.ruta_bd) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS productos (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre       TEXT    NOT NULL,
                    precio       REAL    NOT NULL,
                    cantidad     INTEGER NOT NULL,
                    stock_minimo INTEGER NOT NULL
                )
            """)
            conn.commit()

    # -----------------------------------------------------------------------
    # CREATE — Agregar un nuevo producto
    # -----------------------------------------------------------------------
    def agregar_producto(self, nombre: str, precio: float,
                         cantidad: int, stock_minimo: int) -> None:
        """
        Inserta un nuevo producto en la base de datos.

        Parámetros:
            nombre       (str)   : Nombre del producto cosmético.
            precio       (float) : Precio en pesos colombianos (COP).
            cantidad     (int)   : Unidades disponibles al momento del registro.
            stock_minimo (int)   : Nivel mínimo de stock permitido.
        """
        with sqlite3.connect(self.ruta_bd) as conn:
            conn.execute(
                "INSERT INTO productos (nombre, precio, cantidad, stock_minimo) "
                "VALUES (?, ?, ?, ?)",
                (nombre, precio, cantidad, stock_minimo)
            )
            conn.commit()

    # -----------------------------------------------------------------------
    # READ — Leer productos de la base de datos
    # -----------------------------------------------------------------------
    def obtener_todos(self) -> list:
        """
        Retorna todos los productos ordenados por nombre.

        Retorna:
            list: Lista de tuplas con la forma (id, nombre, precio, cantidad, stock_minimo).
        """
        with sqlite3.connect(self.ruta_bd) as conn:
            cursor = conn.execute(
                "SELECT id, nombre, precio, cantidad, stock_minimo "
                "FROM productos ORDER BY nombre"
            )
            return cursor.fetchall()

    def obtener_por_id(self, producto_id: int) -> tuple:
        """
        Busca y retorna un producto específico por su ID.

        Parámetros:
            producto_id (int): El identificador único del producto.

        Retorna:
            tuple: Tupla con los datos del producto, o None si no existe.
        """
        with sqlite3.connect(self.ruta_bd) as conn:
            cursor = conn.execute(
                "SELECT id, nombre, precio, cantidad, stock_minimo "
                "FROM productos WHERE id = ?",
                (producto_id,)
            )
            return cursor.fetchone()

    def obtener_bajo_stock(self) -> list:
        """
        Retorna los productos cuya cantidad actual es menor que su stock mínimo.

        Retorna:
            list: Lista de tuplas de productos con stock crítico.
        """
        with sqlite3.connect(self.ruta_bd) as conn:
            cursor = conn.execute(
                "SELECT id, nombre, precio, cantidad, stock_minimo "
                "FROM productos WHERE cantidad < stock_minimo ORDER BY nombre"
            )
            return cursor.fetchall()

    # -----------------------------------------------------------------------
    # UPDATE — Actualizar un producto existente
    # -----------------------------------------------------------------------
    def actualizar_producto(self, producto_id: int, nombre: str, precio: float,
                            cantidad: int, stock_minimo: int) -> None:
        """
        Modifica los datos de un producto ya existente.

        Parámetros:
            producto_id  (int)   : ID del producto a modificar.
            nombre       (str)   : Nuevo nombre.
            precio       (float) : Nuevo precio en COP.
            cantidad     (int)   : Nueva cantidad disponible.
            stock_minimo (int)   : Nuevo stock mínimo.
        """
        with sqlite3.connect(self.ruta_bd) as conn:
            conn.execute(
                "UPDATE productos SET nombre=?, precio=?, cantidad=?, "
                "stock_minimo=? WHERE id=?",
                (nombre, precio, cantidad, stock_minimo, producto_id)
            )
            conn.commit()

    # -----------------------------------------------------------------------
    # DELETE — Eliminar un producto
    # -----------------------------------------------------------------------
    def eliminar_producto(self, producto_id: int) -> None:
        """
        Elimina permanentemente un producto de la base de datos.

        Parámetros:
            producto_id (int): ID del producto a eliminar.
        """
        with sqlite3.connect(self.ruta_bd) as conn:
            conn.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
            conn.commit()

    def buscar_productos(self, texto: str) -> list:
        """
        Busca productos cuyo nombre contenga el texto indicado (insensible a mayúsculas).

        Parámetros:
            texto (str): Fragmento de texto a buscar en el nombre del producto.

        Retorna:
            list: Lista de tuplas con los productos encontrados.
        """
        with sqlite3.connect(self.ruta_bd) as conn:
            cursor = conn.execute(
                "SELECT id, nombre, precio, cantidad, stock_minimo "
                "FROM productos WHERE nombre LIKE ? ORDER BY nombre",
                (f"%{texto}%",)
            )
            return cursor.fetchall()


# ---------------------------------------------------------------------------
# CAPA DE PRESENTACIÓN — Interfaz gráfica con tkinter
# ---------------------------------------------------------------------------

class AplicacionInventario:
    """
    Clase principal de la interfaz gráfica de usuario (GUI).

    Organiza toda la ventana y sus componentes visuales.
    Se comunica con BaseDeDatos para leer y escribir información.

    Atributos:
        ventana  (tk.Tk)      : Ventana principal de la aplicación.
        bd       (BaseDeDatos): Instancia de la capa de datos.
        id_seleccionado (int) : ID del producto actualmente seleccionado en la tabla.
    """

    def __init__(self, ventana: tk.Tk):
        """
        Constructor: recibe la ventana raíz y construye toda la interfaz.

        Parámetros:
            ventana (tk.Tk): La ventana principal creada en el bloque main.
        """
        self.ventana = ventana
        self.bd = BaseDeDatos()

        # Almacena el ID del producto seleccionado en la tabla (None = ninguno)
        self.id_seleccionado = None

        # Configuración inicial de la ventana
        self._configurar_ventana()

        # Construcción de cada sección visual
        self._crear_encabezado()
        self._crear_area_principal()

        # Cargamos los productos al iniciar
        self.actualizar_tabla()

    # -----------------------------------------------------------------------
    # CONFIGURACIÓN GENERAL DE LA VENTANA
    # -----------------------------------------------------------------------

    def _configurar_ventana(self):
        """Configura las propiedades básicas de la ventana principal."""
        self.ventana.title("✿ Gestión de Inventario — Cosméticos")
        self.ventana.geometry("1100x680")
        self.ventana.minsize(900, 580)
        self.ventana.configure(bg=COLOR_FONDO)
        self.ventana.resizable(True, True)

        # Centramos la ventana en la pantalla
        self.ventana.update_idletasks()
        ancho  = self.ventana.winfo_width()
        alto   = self.ventana.winfo_height()
        x = (self.ventana.winfo_screenwidth()  - ancho) // 2
        y = (self.ventana.winfo_screenheight() - alto)  // 2
        self.ventana.geometry(f"+{x}+{y}")

    # -----------------------------------------------------------------------
    # SECCIÓN: ENCABEZADO SUPERIOR
    # -----------------------------------------------------------------------

    def _crear_encabezado(self):
        """Crea la barra superior con el título de la aplicación."""
        frame_encabezado = tk.Frame(
            self.ventana,
            bg=COLOR_ACENTO,
            height=70
        )
        frame_encabezado.pack(fill="x", side="top")
        frame_encabezado.pack_propagate(False)   # Impide que el frame se encoja

        # Título principal
        tk.Label(
            frame_encabezado,
            text="✿  Inventario de Productos Cosméticos",
            font=FUENTE_TITULO,
            bg=COLOR_ACENTO,
            fg="#FFFFFF"
        ).pack(side="left", padx=24, pady=16)

        # Subtítulo a la derecha
        tk.Label(
            frame_encabezado,
            text="Base de datos: inventario.db",
            font=("Segoe UI", 9),
            bg=COLOR_ACENTO,
            fg="#F7D6E0"
        ).pack(side="right", padx=24)

    # -----------------------------------------------------------------------
    # SECCIÓN: ÁREA PRINCIPAL (formulario + tabla)
    # -----------------------------------------------------------------------

    def _crear_area_principal(self):
        """
        Crea el área central dividida en dos columnas:
        - Izquierda: formulario de datos y botones de acción
        - Derecha  : tabla con la lista de productos y búsqueda
        """
        frame_principal = tk.Frame(self.ventana, bg=COLOR_FONDO)
        frame_principal.pack(fill="both", expand=True, padx=16, pady=12)

        # Columna izquierda — formulario
        self._crear_panel_formulario(frame_principal)

        # Columna derecha — tabla de productos
        self._crear_panel_tabla(frame_principal)

    # -----------------------------------------------------------------------
    # PANEL IZQUIERDO: FORMULARIO
    # -----------------------------------------------------------------------

    def _crear_panel_formulario(self, contenedor):
        """
        Construye el panel de la izquierda con los campos del formulario
        y los botones de acción.

        Parámetros:
            contenedor (tk.Frame): El frame padre donde se inserta este panel.
        """
        frame_form = tk.Frame(
            contenedor,
            bg=COLOR_PANEL,
            relief="flat",
            bd=0
        )
        frame_form.pack(side="left", fill="y", padx=(0, 12), pady=0)
        frame_form.configure(width=280)
        frame_form.pack_propagate(False)

        # Borde decorativo izquierdo (línea de color)
        tk.Frame(frame_form, bg=COLOR_ACENTO, width=4).pack(
            side="left", fill="y"
        )

        # Contenido del formulario
        cuerpo = tk.Frame(frame_form, bg=COLOR_PANEL)
        cuerpo.pack(side="left", fill="both", expand=True, padx=14, pady=14)

        # --- Título del panel ---
        tk.Label(
            cuerpo,
            text="Datos del Producto",
            font=FUENTE_SUBTIT,
            bg=COLOR_PANEL,
            fg=COLOR_ACENTO
        ).pack(anchor="w", pady=(0, 12))

        # --- Campos del formulario ---
        # Usamos un diccionario para guardar las variables de cada campo
        self.campos = {}

        definicion_campos = [
            ("nombre",       "Nombre del producto",        "Ej: Labial matte rojo"),
            ("precio",       "Precio (COP $)",             "Ej: 35000"),
            ("cantidad",     "Cantidad disponible",        "Ej: 20"),
            ("stock_minimo", "Stock mínimo (unidades)",    "Ej: 5"),
        ]

        for clave, etiqueta, placeholder in definicion_campos:
            self._crear_campo(cuerpo, clave, etiqueta, placeholder)

        # Separador visual
        ttk.Separator(cuerpo, orient="horizontal").pack(fill="x", pady=14)

        # --- Botones CRUD ---
        self._crear_botones_crud(cuerpo)

        # --- Botón especial: Alerta de stock ---
        ttk.Separator(cuerpo, orient="horizontal").pack(fill="x", pady=(8, 12))
        self._crear_boton_alerta(cuerpo)

        # Etiqueta de estado (mensajes de éxito/error)
        self.lbl_estado = tk.Label(
            cuerpo,
            text="",
            font=("Segoe UI", 9, "italic"),
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO_SUAVE,
            wraplength=230,
            justify="left"
        )
        self.lbl_estado.pack(anchor="w", pady=(10, 0))

    def _crear_campo(self, contenedor, clave: str, etiqueta: str, placeholder: str):
        """
        Crea una etiqueta y su campo de texto (Entry) asociado.

        Parámetros:
            contenedor  (tk.Frame) : Frame donde se inserta el campo.
            clave       (str)      : Clave interna para acceder al valor del campo.
            etiqueta    (str)      : Texto descriptivo que aparece encima del campo.
            placeholder (str)      : Texto de ayuda que se muestra dentro del campo vacío.
        """
        # Etiqueta descriptiva
        tk.Label(
            contenedor,
            text=etiqueta,
            font=("Segoe UI", 9),
            bg=COLOR_PANEL,
            fg=COLOR_TEXTO_SUAVE
        ).pack(anchor="w", pady=(6, 1))

        # Variable de tkinter para leer el valor del campo fácilmente
        var = tk.StringVar()
        self.campos[clave] = var

        # Campo de texto
        entry = tk.Entry(
            contenedor,
            textvariable=var,
            font=FUENTE_NORMAL,
            fg=COLOR_TEXTO,
            bg="#FDF0ED",
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=COLOR_BORDE,
            highlightcolor=COLOR_ACENTO
        )
        entry.pack(fill="x", ipady=7)

        # Comportamiento del placeholder (texto de ayuda)
        entry.insert(0, placeholder)
        entry.config(fg="#AAAAAA")

        def al_entrar(event, e=entry, p=placeholder):
            """Limpia el placeholder cuando el usuario hace clic en el campo."""
            if e.get() == p:
                e.delete(0, "end")
                e.config(fg=COLOR_TEXTO)

        def al_salir(event, e=entry, p=placeholder):
            """Restaura el placeholder si el campo queda vacío."""
            if e.get() == "":
                e.insert(0, p)
                e.config(fg="#AAAAAA")

        entry.bind("<FocusIn>",  al_entrar)
        entry.bind("<FocusOut>", al_salir)

        # Guardamos también la referencia al widget para poder limpiar el placeholder
        entry._placeholder = placeholder

    def _crear_botones_crud(self, contenedor):
        """
        Crea los cuatro botones de operaciones CRUD en el formulario.

        Parámetros:
            contenedor (tk.Frame): Frame donde se insertan los botones.
        """
        # --- Agregar ---
        self._boton(
            contenedor,
            texto="＋  Agregar Producto",
            color=COLOR_ACENTO,
            hover=COLOR_ACENTO_HOVER,
            comando=self.accion_agregar
        ).pack(fill="x", pady=(0, 6))

        # --- Actualizar ---
        self._boton(
            contenedor,
            texto="✎  Actualizar Seleccionado",
            color="#7BAE9C",
            hover="#5E9480",
            comando=self.accion_actualizar
        ).pack(fill="x", pady=(0, 6))

        # --- Limpiar formulario ---
        self._boton(
            contenedor,
            texto="↺  Limpiar Formulario",
            color="#A0A0A0",
            hover="#808080",
            comando=self.limpiar_formulario
        ).pack(fill="x", pady=(0, 6))

        # --- Eliminar ---
        self._boton(
            contenedor,
            texto="✕  Eliminar Seleccionado",
            color=COLOR_ELIMINAR,
            hover=COLOR_ELIMINAR_HOVER,
            comando=self.accion_eliminar
        ).pack(fill="x")

    def _crear_boton_alerta(self, contenedor):
        """
        Crea el botón especial para mostrar productos con stock crítico.

        Parámetros:
            contenedor (tk.Frame): Frame donde se inserta el botón.
        """
        self._boton(
            contenedor,
            texto="⚠  Ver Alertas de Stock",
            color=COLOR_ALERTA,
            hover=COLOR_ALERTA_HOVER,
            comando=self.accion_alerta_stock
        ).pack(fill="x")

    def _boton(self, contenedor, texto: str, color: str,
               hover: str, comando) -> tk.Button:
        """
        Crea y retorna un botón estilizado con efecto hover (cambio de color al pasar el cursor).

        Parámetros:
            contenedor (tk.Frame)  : Frame donde se inserta el botón.
            texto      (str)       : Texto que muestra el botón.
            color      (str)       : Color de fondo normal del botón.
            hover      (str)       : Color de fondo al pasar el cursor.
            comando    (callable)  : Función que se ejecuta al hacer clic.

        Retorna:
            tk.Button: El botón creado (para poder hacer .pack() después).
        """
        btn = tk.Button(
            contenedor,
            text=texto,
            font=FUENTE_BOTON,
            bg=color,
            fg="#FFFFFF",
            activebackground=hover,
            activeforeground="#FFFFFF",
            relief="flat",
            cursor="hand2",         # Cambia el cursor a una mano al pasar por encima
            bd=0,
            padx=10,
            pady=8,
            command=comando
        )
        # Efecto hover: cambia el color al entrar y al salir el cursor
        btn.bind("<Enter>", lambda e, b=btn, h=hover: b.config(bg=h))
        btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c))
        return btn

    # -----------------------------------------------------------------------
    # PANEL DERECHO: TABLA DE PRODUCTOS
    # -----------------------------------------------------------------------

    def _crear_panel_tabla(self, contenedor):
        """
        Construye el panel derecho con la barra de búsqueda, la tabla de
        productos y la barra de desplazamiento.

        Parámetros:
            contenedor (tk.Frame): El frame padre donde se inserta este panel.
        """
        frame_tabla = tk.Frame(contenedor, bg=COLOR_FONDO)
        frame_tabla.pack(side="left", fill="both", expand=True)

        # --- Barra de búsqueda ---
        self._crear_barra_busqueda(frame_tabla)

        # --- Tabla (Treeview) ---
        self._crear_treeview(frame_tabla)

        # --- Etiqueta con total de registros ---
        self.lbl_total = tk.Label(
            frame_tabla,
            text="",
            font=("Segoe UI", 9),
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO_SUAVE
        )
        self.lbl_total.pack(anchor="e", padx=4, pady=(4, 0))

    def _crear_barra_busqueda(self, contenedor):
        """
        Crea la barra de búsqueda en tiempo real (filtra mientras se escribe).

        Parámetros:
            contenedor (tk.Frame): Frame donde se inserta la barra.
        """
        frame_busq = tk.Frame(contenedor, bg=COLOR_FONDO)
        frame_busq.pack(fill="x", pady=(0, 8))

        tk.Label(
            frame_busq,
            text="🔍  Buscar:",
            font=FUENTE_NORMAL,
            bg=COLOR_FONDO,
            fg=COLOR_TEXTO
        ).pack(side="left", padx=(0, 6))

        self.var_busqueda = tk.StringVar()
        # Cada vez que cambia el texto de búsqueda, filtramos la tabla
        self.var_busqueda.trace_add("write", self._al_buscar)

        tk.Entry(
            frame_busq,
            textvariable=self.var_busqueda,
            font=FUENTE_NORMAL,
            fg=COLOR_TEXTO,
            bg="#FFFFFF",
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=COLOR_BORDE,
            highlightcolor=COLOR_ACENTO
        ).pack(side="left", fill="x", expand=True, ipady=6)

        # Botón para limpiar la búsqueda
        tk.Button(
            frame_busq,
            text="✕",
            font=("Segoe UI", 9, "bold"),
            bg=COLOR_BORDE,
            fg=COLOR_TEXTO,
            relief="flat",
            cursor="hand2",
            padx=8,
            command=lambda: self.var_busqueda.set("")
        ).pack(side="left", padx=(4, 0))

    def _crear_treeview(self, contenedor):
        """
        Crea la tabla (Treeview de ttk) con columnas y su barra de scroll.
        También configura el estilo visual de la tabla.

        Parámetros:
            contenedor (tk.Frame): Frame donde se inserta la tabla.
        """
        # Aplicamos estilos personalizados al Treeview
        estilo = ttk.Style()
        estilo.theme_use("clam")

        estilo.configure(
            "Inventario.Treeview",
            background=COLOR_TABLA_FILA1,
            foreground=COLOR_TEXTO,
            rowheight=32,
            fieldbackground=COLOR_TABLA_FILA1,
            font=FUENTE_TABLA
        )
        estilo.configure(
            "Inventario.Treeview.Heading",
            background=COLOR_ENCABEZADO,
            foreground="#FFFFFF",
            font=("Segoe UI", 10, "bold"),
            relief="flat"
        )
        estilo.map(
            "Inventario.Treeview",
            background=[("selected", COLOR_ACENTO)],
            foreground=[("selected", "#FFFFFF")]
        )

        # Frame que contendrá la tabla y el scroll
        frame_tv = tk.Frame(contenedor, bg=COLOR_FONDO)
        frame_tv.pack(fill="both", expand=True)

        # Scroll vertical
        scroll_y = ttk.Scrollbar(frame_tv, orient="vertical")
        scroll_y.pack(side="right", fill="y")

        # Definición de columnas
        columnas = ("id", "nombre", "precio", "cantidad", "stock_minimo")

        self.tabla = ttk.Treeview(
            frame_tv,
            columns=columnas,
            show="headings",
            style="Inventario.Treeview",
            yscrollcommand=scroll_y.set,
            selectmode="browse"     # Solo permite seleccionar una fila a la vez
        )

        scroll_y.config(command=self.tabla.yview)

        # Encabezados y anchos de columna
        self.tabla.heading("id",           text="ID",            anchor="center")
        self.tabla.heading("nombre",       text="Nombre",        anchor="w")
        self.tabla.heading("precio",       text="Precio (COP)",  anchor="e")
        self.tabla.heading("cantidad",     text="Cantidad",      anchor="center")
        self.tabla.heading("stock_minimo", text="Stock Mínimo",  anchor="center")

        self.tabla.column("id",           width=50,  minwidth=40,  anchor="center")
        self.tabla.column("nombre",       width=280, minwidth=150, anchor="w")
        self.tabla.column("precio",       width=140, minwidth=100, anchor="e")
        self.tabla.column("cantidad",     width=100, minwidth=80,  anchor="center")
        self.tabla.column("stock_minimo", width=110, minwidth=90,  anchor="center")

        # Etiqueta especial para filas con stock crítico (color rojo suave)
        self.tabla.tag_configure("critico", background="#FFE8E8", foreground="#C0392B")
        # Colores alternos para filas normales
        self.tabla.tag_configure("fila_par",   background=COLOR_TABLA_FILA1)
        self.tabla.tag_configure("fila_impar", background=COLOR_TABLA_FILA2)

        self.tabla.pack(fill="both", expand=True)

        # Al seleccionar una fila, cargamos sus datos en el formulario
        self.tabla.bind("<<TreeviewSelect>>", self._al_seleccionar_fila)

    # -----------------------------------------------------------------------
    # LÓGICA DE LA INTERFAZ — Eventos y acciones
    # -----------------------------------------------------------------------

    def _al_buscar(self, *args):
        """
        Callback que se ejecuta cada vez que el texto de búsqueda cambia.
        Filtra la tabla en tiempo real sin necesidad de pulsar un botón.

        *args: tkinter pasa argumentos automáticamente al usar trace_add,
               por eso los capturamos con *args aunque no los usemos.
        """
        texto = self.var_busqueda.get().strip()
        if texto:
            productos = self.bd.buscar_productos(texto)
        else:
            productos = self.bd.obtener_todos()
        self._poblar_tabla(productos)

    def _al_seleccionar_fila(self, event):
        """
        Cuando el usuario hace clic en una fila de la tabla, carga
        los datos de ese producto en el formulario para editarlos.

        Parámetros:
            event: Evento de tkinter (no lo usamos directamente).
        """
        seleccion = self.tabla.selection()
        if not seleccion:
            return  # No hay nada seleccionado, salimos

        fila = self.tabla.item(seleccion[0])["values"]
        # fila = (id, nombre, precio, cantidad, stock_minimo)
        self.id_seleccionado = fila[0]

        # Rellenamos el formulario con los datos de la fila seleccionada
        placeholders = {
            "nombre":       "Ej: Labial matte rojo",
            "precio":       "Ej: 35000",
            "cantidad":     "Ej: 20",
            "stock_minimo": "Ej: 5",
        }
        valores = {
            "nombre":       str(fila[1]),
            "precio":       str(fila[2]),
            "cantidad":     str(fila[3]),
            "stock_minimo": str(fila[4]),
        }
        for clave, var in self.campos.items():
            var.set(valores[clave])

        self._mostrar_estado(f"Producto #{self.id_seleccionado} seleccionado.")

    def _poblar_tabla(self, productos: list):
        """
        Limpia la tabla y la vuelve a llenar con la lista de productos recibida.
        Aplica colores alternativos por fila y marca en rojo los de stock crítico.

        Parámetros:
            productos (list): Lista de tuplas (id, nombre, precio, cantidad, stock_minimo).
        """
        # Eliminamos todas las filas actuales
        for item in self.tabla.get_children():
            self.tabla.delete(item)

        for i, producto in enumerate(productos):
            pid, nombre, precio, cantidad, stock_min = producto

            # Formateamos el precio con separador de miles y símbolo $
            precio_formato = f"$ {precio:,.0f}"

            # Determinamos el tag (estilo) de la fila
            if cantidad < stock_min:
                tag = "critico"
            elif i % 2 == 0:
                tag = "fila_par"
            else:
                tag = "fila_impar"

            self.tabla.insert(
                "",
                "end",
                values=(pid, nombre, precio_formato, cantidad, stock_min),
                tags=(tag,)
            )

        # Actualizamos el contador de registros
        total = len(productos)
        self.lbl_total.config(
            text=f"{total} producto{'s' if total != 1 else ''} mostrado{'s' if total != 1 else ''}"
        )

    def actualizar_tabla(self):
        """Recarga todos los productos desde la BD y los muestra en la tabla."""
        self.var_busqueda.set("")   # Limpiamos la búsqueda activa
        productos = self.bd.obtener_todos()
        self._poblar_tabla(productos)

    # -----------------------------------------------------------------------
    # ACCIONES CRUD — Lo que ocurre al pulsar cada botón
    # -----------------------------------------------------------------------

    def _leer_formulario(self) -> dict | None:
        """
        Lee y valida los valores del formulario.

        Retorna:
            dict: Diccionario con los valores validados, o None si hay errores.
                  Claves: 'nombre' (str), 'precio' (float),
                          'cantidad' (int), 'stock_minimo' (int).
        """
        placeholders = {
            "nombre":       "Ej: Labial matte rojo",
            "precio":       "Ej: 35000",
            "cantidad":     "Ej: 20",
            "stock_minimo": "Ej: 5",
        }

        # Leemos cada campo, ignorando el texto placeholder
        valores = {}
        for clave, var in self.campos.items():
            valor = var.get().strip()
            if valor == placeholders[clave] or valor == "":
                messagebox.showwarning(
                    "Campo vacío",
                    f"El campo «{clave.replace('_', ' ')}» es obligatorio."
                )
                return None
            valores[clave] = valor

        # Validamos que precio sea un número positivo
        try:
            precio = float(valores["precio"].replace(",", "").replace("$", "").strip())
            if precio <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "El precio debe ser un número positivo.")
            return None

        # Validamos que cantidad sea un entero no negativo
        try:
            cantidad = int(valores["cantidad"])
            if cantidad < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "La cantidad debe ser un número entero no negativo.")
            return None

        # Validamos que stock mínimo sea un entero positivo
        try:
            stock_minimo = int(valores["stock_minimo"])
            if stock_minimo < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "El stock mínimo debe ser al menos 1.")
            return None

        return {
            "nombre":       valores["nombre"],
            "precio":       precio,
            "cantidad":     cantidad,
            "stock_minimo": stock_minimo
        }

    def accion_agregar(self):
        """
        Se ejecuta al pulsar «Agregar Producto».
        Valida el formulario y, si es correcto, inserta el producto en la BD.
        """
        datos = self._leer_formulario()
        if datos is None:
            return  # Hubo un error de validación, no continuamos

        self.bd.agregar_producto(
            datos["nombre"],
            datos["precio"],
            datos["cantidad"],
            datos["stock_minimo"]
        )
        self.limpiar_formulario()
        self.actualizar_tabla()
        self._mostrar_estado(f"✓ Producto «{datos['nombre']}» agregado.")

    def accion_actualizar(self):
        """
        Se ejecuta al pulsar «Actualizar Seleccionado».
        Requiere que haya un producto seleccionado en la tabla.
        """
        if self.id_seleccionado is None:
            messagebox.showinfo(
                "Sin selección",
                "Primero selecciona un producto en la tabla para actualizarlo."
            )
            return

        datos = self._leer_formulario()
        if datos is None:
            return

        self.bd.actualizar_producto(
            self.id_seleccionado,
            datos["nombre"],
            datos["precio"],
            datos["cantidad"],
            datos["stock_minimo"]
        )
        self.limpiar_formulario()
        self.actualizar_tabla()
        self._mostrar_estado(f"✓ Producto #{self.id_seleccionado} actualizado.")

    def accion_eliminar(self):
        """
        Se ejecuta al pulsar «Eliminar Seleccionado».
        Pide confirmación antes de eliminar permanentemente el producto.
        """
        if self.id_seleccionado is None:
            messagebox.showinfo(
                "Sin selección",
                "Primero selecciona un producto en la tabla para eliminarlo."
            )
            return

        nombre = self.campos["nombre"].get()
        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Estás segura de que deseas eliminar el producto:\n\n"
            f"«{nombre}» (ID: {self.id_seleccionado})?\n\n"
            f"Esta acción no se puede deshacer."
        )
        if not confirmar:
            return  # El usuario canceló

        self.bd.eliminar_producto(self.id_seleccionado)
        self.limpiar_formulario()
        self.actualizar_tabla()
        self._mostrar_estado(f"✓ Producto eliminado correctamente.")

    def accion_alerta_stock(self):
        """
        Se ejecuta al pulsar «Ver Alertas de Stock».
        Muestra en una ventana emergente solo los productos con stock crítico,
        es decir, aquellos cuya cantidad actual < stock mínimo.
        """
        productos_criticos = self.bd.obtener_bajo_stock()

        if not productos_criticos:
            messagebox.showinfo(
                "✿ Sin alertas",
                "¡Todo está en orden! No hay productos con stock por debajo "
                "del nivel mínimo definido."
            )
            return

        # Creamos una ventana emergente (Toplevel) para mostrar las alertas
        ventana_alerta = tk.Toplevel(self.ventana)
        ventana_alerta.title("⚠ Alertas de Stock Crítico")
        ventana_alerta.configure(bg=COLOR_FONDO)
        ventana_alerta.resizable(False, False)

        # Centramos la ventana emergente sobre la ventana principal
        ventana_alerta.transient(self.ventana)
        ventana_alerta.grab_set()   # Bloquea la ventana principal hasta cerrar esta

        # --- Encabezado de la alerta ---
        frame_enc = tk.Frame(ventana_alerta, bg=COLOR_ALERTA, height=55)
        frame_enc.pack(fill="x")
        frame_enc.pack_propagate(False)

        tk.Label(
            frame_enc,
            text=f"⚠  {len(productos_criticos)} producto(s) con stock crítico",
            font=FUENTE_SUBTIT,
            bg=COLOR_ALERTA,
            fg="#FFFFFF"
        ).pack(padx=20, pady=14)

        # --- Tabla de alertas ---
        frame_tabla = tk.Frame(ventana_alerta, bg=COLOR_FONDO)
        frame_tabla.pack(fill="both", expand=True, padx=16, pady=16)

        columnas = ("nombre", "cantidad", "stock_minimo", "faltante")
        tabla_alertas = ttk.Treeview(
            frame_tabla,
            columns=columnas,
            show="headings",
            style="Inventario.Treeview",
            height=min(len(productos_criticos), 12)
        )

        tabla_alertas.heading("nombre",       text="Producto")
        tabla_alertas.heading("cantidad",     text="Cantidad actual")
        tabla_alertas.heading("stock_minimo", text="Stock mínimo")
        tabla_alertas.heading("faltante",     text="Unidades faltantes")

        tabla_alertas.column("nombre",       width=220, anchor="w")
        tabla_alertas.column("cantidad",     width=130, anchor="center")
        tabla_alertas.column("stock_minimo", width=120, anchor="center")
        tabla_alertas.column("faltante",     width=140, anchor="center")

        tabla_alertas.tag_configure("alerta", background="#FFE8E8", foreground="#C0392B")

        for prod in productos_criticos:
            _, nombre, _, cantidad, stock_min = prod
            faltante = stock_min - cantidad
            tabla_alertas.insert(
                "",
                "end",
                values=(nombre, cantidad, stock_min, f"⚠ {faltante}"),
                tags=("alerta",)
            )

        tabla_alertas.pack(fill="both")

        # --- Botón de cierre ---
        tk.Button(
            ventana_alerta,
            text="Cerrar",
            font=FUENTE_BOTON,
            bg=COLOR_ACENTO,
            fg="#FFFFFF",
            relief="flat",
            cursor="hand2",
            padx=24,
            pady=8,
            command=ventana_alerta.destroy
        ).pack(pady=(0, 16))

        # Calculamos el tamaño de la ventana emergente según el contenido
        ventana_alerta.update_idletasks()
        ancho  = max(650, ventana_alerta.winfo_reqwidth()  + 20)
        alto   = ventana_alerta.winfo_reqheight() + 20
        x = self.ventana.winfo_x() + (self.ventana.winfo_width()  - ancho) // 2
        y = self.ventana.winfo_y() + (self.ventana.winfo_height() - alto)  // 2
        ventana_alerta.geometry(f"{ancho}x{alto}+{x}+{y}")

    # -----------------------------------------------------------------------
    # UTILIDADES DE LA INTERFAZ
    # -----------------------------------------------------------------------

    def limpiar_formulario(self):
        """
        Limpia todos los campos del formulario y deselecciona
        cualquier fila activa en la tabla.
        """
        placeholders = {
            "nombre":       "Ej: Labial matte rojo",
            "precio":       "Ej: 35000",
            "cantidad":     "Ej: 20",
            "stock_minimo": "Ej: 5",
        }
        for clave, var in self.campos.items():
            var.set(placeholders[clave])

        # Restauramos el color de los placeholders (texto gris)
        for widget in self.ventana.winfo_children():
            self._restaurar_color_placeholder(widget, placeholders)

        # Deseleccionamos la fila activa en la tabla
        self.tabla.selection_remove(self.tabla.selection())
        self.id_seleccionado = None

    def _restaurar_color_placeholder(self, widget, placeholders: dict):
        """
        Recorre recursivamente los widgets para restaurar el color gris
        en los campos Entry que tienen el texto placeholder.

        Parámetros:
            widget     (tk.Widget) : Widget a revisar.
            placeholders (dict)    : Diccionario de textos placeholder.
        """
        if isinstance(widget, tk.Entry):
            for ph in placeholders.values():
                if widget.get() == ph:
                    widget.config(fg="#AAAAAA")
                    break
            else:
                widget.config(fg=COLOR_TEXTO)
        # Revisamos también los widgets hijos (contenidos dentro de frames, etc.)
        for hijo in widget.winfo_children():
            self._restaurar_color_placeholder(hijo, placeholders)

    def _mostrar_estado(self, mensaje: str):
        """
        Muestra un mensaje temporal en la etiqueta de estado del formulario.
        Después de 3 segundos, el mensaje desaparece automáticamente.

        Parámetros:
            mensaje (str): El texto a mostrar.
        """
        self.lbl_estado.config(text=mensaje)
        # after() ejecuta una función después de N milisegundos
        self.ventana.after(3000, lambda: self.lbl_estado.config(text=""))


# ---------------------------------------------------------------------------
# PUNTO DE ENTRADA PRINCIPAL
# ---------------------------------------------------------------------------

def main():
    """
    Función principal que inicializa y lanza la aplicación.

    Al separar la lógica de inicio en una función main(), hacemos el código
    más limpio y reutilizable (buena práctica en Python).
    """
    # Creamos la ventana raíz de tkinter
    ventana_raiz = tk.Tk()

    # Creamos la aplicación, pasándole la ventana raíz
    app = AplicacionInventario(ventana_raiz)

    # Iniciamos el bucle de eventos (mantiene la ventana abierta y activa)
    ventana_raiz.mainloop()


# ---------------------------------------------------------------------------
# Patrón estándar de Python: solo ejecuta main() si este archivo se corre
# directamente (no si es importado como módulo por otro script).
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    main()