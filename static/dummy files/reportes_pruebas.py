from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import mysql.connector
import datetime


# Conectar a la base de datos MySQL
conn = mysql.connector.connect(
    host="localhost", user="android", password="12345678", database="pies"
)
cursor = conn.cursor()

# Consultar datos del usuario
cursor.execute("SELECT * FROM usuarios WHERE id = 20")
usuario = cursor.fetchone()

# Consultar datos adicionales
cursor.execute("SELECT * FROM pruebas WHERE id_usuario = 20")
pruebas = cursor.fetchall()

conn.close()

# Crear el PDF
pdf_filename = "reporte.pdf"
c = canvas.Canvas(pdf_filename, pagesize=A4)
width, height = A4
styles = getSampleStyleSheet()

# Agregar logo y título
c.drawImage(
    "static/assets/images/espoch.png",
    50,
    height - 130,
    width=100,
    height=100,
    mask="auto",
)
c.setFont("Helvetica", 20)
c.drawString(170, height - 70, "Reporte de Análisis de Superficie Plantar")

# Agregar datos del usuario
c.setFont("Helvetica", 12)
fecha_reporte = datetime.datetime.now().strftime("%d-%m-%Y")
c.drawString(170, height - 100, f"Fecha del Reporte: {fecha_reporte}")

# Agregar datos del usuario
datos_usuario = f"""
Nombre: {usuario[1]}
Cédula: {usuario[2]}
Teléfono: {usuario[3]}
Estatura: {usuario[4]} cm
Edad: {usuario[5]} años
Peso: {usuario[6]} Kg
"""
c.setFont("Helvetica", 12)
text_obj = c.beginText(50, height - 150)
for line in datos_usuario.split("\n"):
    text_obj.textLine(line)
c.drawText(text_obj)


# Agregar imagen del usuario a la derecha con transparencia
c.drawImage(
    "static/" + usuario[8], 400, height - 250, width=100, height=100, mask="auto"
)


# Espacio entre secciones
y_position = height - 300

contador = 0
# Agregar datos de las pruebas
for prueba in pruebas:
    contador += 1
    # Agregar fecha de la prueba
    fecha_prueba = prueba[11]
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y_position, f"Número de Prueba: {contador}")
    c.drawString(50, y_position - 18, f"Fecha de la Prueba: {fecha_prueba}")
    y_position -= 10

    # Crear tabla de datos de la prueba
    table_data = [
        [
            "X",
            "Y",
            "Porcentaje Izquierda",
            "Tipo",
            "X",
            "Y",
            "Porcentaje Derecha",
            "Tipo",
        ]
    ]
    prueba_datos = list(prueba[2:-2])

    # Redondear columnas específicas (3, 4, 7, 8)
    for i in [0, 1, 4, 5]:
        prueba_datos[i] = str(round(float(prueba_datos[i]), 2)) + " cm"

    table_data.append(prueba_datos)

    table = Table(table_data)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )

    table.wrapOn(c, width, height)
    table.drawOn(c, 50, y_position - 70)
    y_position -= 140


c.save()
print("PDF creado exitosamente:", pdf_filename)
