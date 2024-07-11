import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import mysql.connector
import datetime

# Conectar a la base de datos MySQL
conn = mysql.connector.connect(
    host="localhost", user="android", password="12345678", database="pies"
)
cursor = conn.cursor()

id_usuario = "20"

# Consultar datos del usuario
cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id_usuario,))
usuario = cursor.fetchone()

# Consultar datos de las pruebas
cursor.execute("SELECT * FROM pruebas WHERE id_usuario = %s", (id_usuario,))
pruebas = cursor.fetchall()

conn.close()

# Crear el PDF
pdf_filename = "reporte3.pdf"
c = canvas.Canvas(pdf_filename, pagesize=A4)
width, height = A4
styles = getSampleStyleSheet()


def add_page_header(c, title, fecha_reporte):
    # Agregar logo y título
    c.drawImage(
        "static/assets/images/espoch.png",
        50,
        height - 130,
        width=100,
        height=100,
        mask="auto",
    )

    c.setFont("Helvetica-Bold", 18)
    c.drawString(180, height - 70, title)
    c.setFont("Helvetica", 12)
    c.drawString(180, height - 100, f"Fecha del Reporte: {fecha_reporte}")


def add_user_info(c, usuario):
    datos_usuario = f"""
    Nombre: {usuario[1]}
    Cédula: {usuario[2]}
    Teléfono: {usuario[3]}
    Estatura: {usuario[4]} cm
    Edad: {usuario[5]} años
    Peso: {usuario[6]} Kg
    """
    c.setFont("Helvetica", 12)
    text_obj = c.beginText(40, height - 150)
    for line in datos_usuario.split("\n"):
        text_obj.textLine(line)
    c.drawText(text_obj)
    c.drawImage(
        "static/" + usuario[8], 400, height - 250, width=100, height=100, mask="auto"
    )

    # Dibujar una línea horizontal debajo de la información del usuario
    c.line(50, height - 260, width - 50, height - 260)


def add_table(c, data, x, y):
    table = Table(data)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("FONTSIZE", (0, 1), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )
    table.wrapOn(c, width - 100, height)
    table_width, table_height = table.wrap(0, 0)
    x_position = (width - table_width) / 2  # Centramos la tabla
    table.drawOn(c, x_position, y)


def new_page(c):
    c.showPage()


# Agregar encabezado y datos del usuario en la primera página
add_page_header(
    c,
    "Reporte de Análisis de Superficie Plantar",
    datetime.datetime.now().strftime("%Y-%m-%d"),
)
add_user_info(c, usuario)

y_position = height - 300
contador = 0
# Agregar datos de las pruebas
for prueba in pruebas:
    contador += 1

    if y_position < 300:  # Umbral para crear una nueva página
        new_page(c)
        y_position = (
            height - 50
        )  # Iniciar en una posición más alta en las nuevas páginas

    # Agregar fecha de la prueba
    fecha_prueba = prueba[11]
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position, f"Número de Prueba: {contador}")
    c.drawString(50, y_position - 18, f"Fecha de la Prueba: {fecha_prueba}")
    y_position -= 10

    # Crear tabla de datos de la prueba, omitiendo el primer dato y los dos últimos
    table_data = [
        [
            "X",
            "Y",
            "Porcentaje\nIzquierda",
            "Tipo",
            "X",
            "Y",
            "Porcentaje\nDerecha",
            "Tipo",
        ]
    ]

    prueba_datos = list(prueba[2:-2])

    # Redondear columnas específicas (3, 4, 7, 8)
    for i in [0, 1, 4, 5]:
        prueba_datos[i] = str(round(float(prueba_datos[i]), 2)) + " cm"

    c.setFont("Helvetica", 20)
    table_data.append(prueba_datos)
    add_table(c, table_data, 50, y_position - 70)
    y_position -= 80

    # Agregar segunda tabla con imágenes
    table_data2 = [
        ["Normal", "PseudoColor"],
        [
            Image("static/assets/images/espoch.png", width=150, height=150),
            Image("static/assets/images/espoch.png", width=150, height=150),
        ],
    ]

    if y_position < 300:  # Umbral para crear una nueva página
        new_page(c)
        y_position = height - 50

    add_table(c, table_data2, 50, y_position - 200)
    y_position -= 180

    # Agregar tercera tabla con imágenes
    table_data3 = [
        ["Procesada", "Máscara"],
        [
            Image("static/assets/images/espoch.png", width=150, height=150),
            Image("static/assets/images/espoch.png", width=150, height=150),
        ],
    ]

    if y_position < 300:  # Umbral para crear una nueva página
        new_page(c)
        y_position = height - 50

    add_table(c, table_data3, 50, y_position - 200)
    y_position -= 220

c.save()
print("PDF creado exitosamente:", pdf_filename)

# Obtener la ruta del directorio actual del script
current_dir = os.path.dirname(__file__)
# Construir la ruta completa al directorio de reportes
reportes_dir = os.path.join(current_dir, "static", "reportes")

# Construir la ruta completa al archivo PDF generado
pdf_filename = os.path.join(reportes_dir, "reporte_2024-07-11_13-27-30.pdf")
# Abrir el PDF automáticamente
if os.name == "nt":  # Para Windows
    os.startfile(pdf_filename)
