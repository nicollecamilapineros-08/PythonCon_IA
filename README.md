# Gestión de Inventario — Productos Cosméticos

Aplicación de escritorio para gestionar el inventario de una tienda de cosméticos. Desarrollada en Python con interfaz gráfica (tkinter) y persistencia de datos local mediante SQLite.

---

## Requisitos

- Python 3.8 o superior
- Sistema operativo Windows (la interfaz está optimizada para este entorno)
- No requiere instalar librerías externas; tkinter y sqlite3 vienen incluidos con Python

---

## Ejecución

```bash
python inventario_cosmeticos.py
```

Al iniciarse, el programa crea automáticamente el archivo `inventario.db` en la misma carpeta del script. No se requiere configuración previa.

---

## Estructura del proyecto

```
inventario_cosmeticos.py   # Código fuente principal
inventario.db              # Base de datos (se genera al ejecutar)
README.md
```

---

## Funcionamiento general

La ventana principal se divide en dos secciones:

**Panel izquierdo — Formulario**
Contiene los campos para registrar o modificar un producto: nombre, precio en COP, cantidad disponible y stock mínimo. Desde aquí se ejecutan todas las operaciones sobre los datos.

**Panel derecho — Tabla de productos**
Muestra todos los productos registrados. Incluye una barra de búsqueda que filtra los resultados en tiempo real mientras se escribe. Los productos con stock crítico aparecen resaltados en rojo directamente en la tabla.

---

## Operaciones disponibles (CRUD)

| Acción | Descripción |
|---|---|
| Agregar producto | Rellena el formulario y pulsa "Agregar Producto". |
| Ver y buscar | Los productos se listan automáticamente. Usa la barra de búsqueda para filtrar por nombre. |
| Actualizar producto | Haz clic sobre una fila de la tabla para cargar sus datos en el formulario, modifica lo necesario y pulsa "Actualizar Seleccionado". |
| Eliminar producto | Selecciona una fila y pulsa "Eliminar Seleccionado". El sistema pedirá confirmación antes de proceder. |

---

## Control de stock

El botón **"Ver Alertas de Stock"** abre una ventana emergente que lista únicamente los productos cuya cantidad actual es menor al stock mínimo definido. Para cada producto en alerta se muestra el nombre, la cantidad actual, el mínimo requerido y las unidades faltantes.

El stock mínimo por defecto es de 5 unidades, aunque puede definirse un valor distinto para cada producto al momento de registrarlo.

---

## Datos almacenados por producto

| Campo | Tipo | Descripción |
|---|---|---|
| Nombre | Texto | Nombre del producto cosmético |
| Precio | Decimal | Precio en pesos colombianos (COP) |
| Cantidad | Entero | Unidades disponibles actualmente |
| Stock mínimo | Entero | Umbral mínimo antes de generar alerta |

---

## Notas

- El archivo `inventario.db` puede copiarse o respaldarse como cualquier otro archivo para conservar los datos.
- No se requiere conexión a internet en ningún momento.
- Si el archivo `.db` se elimina, la base de datos se recrea vacía al volver a ejecutar el programa.




# PROMPT UTILIZADO PARA CLAUDE: 


"Redacta el código preciso de Python para el desarrollo de una plataforma de gestión de inventario de productos cosméticos. 
Debe contar con capa de presentación (tkinter) que permita la gestión de eventos por parte del usuario. Diseño de interfaz de usuario: fondo claro, estructura visual agradable y controles interactivos accesibles, pensado para ejecutarse en un entorno Windows. Por otro lado, debe contar con persistencia de datos implementando sqlite3, con la cual se genere un archivo de base de datos local llamado inventario.db. El sistema debe permitir realizar operaciones de manipulación de datos (CRUD). Para cada producto debe registrarse mínimamente: Nombre, Precio (moneda colombiana COP), Cantidad y Stock Mínimo(5 unidades).
En cuanto al control de consistencia de inventario, es necesaria la existencia del botón de alerta que, al ejecutarlo muestre únicamente los productos cuya cantidad actual esté por debajo de su
stock mínimo definido. El resultado generado debe incluir estándar de documentación de código orientado a un programador junior, ten en cuenta las buenas prácticas y generar un código limpio y legible."

## Conversación con la IA (CLAUDE):

https://claude.ai/share/31f7bb23-ca56-4c22-848d-5f452129a2fa
