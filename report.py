import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


# Crear el PDF
pdf_filename = "reporte3.pdf"
c = canvas.Canvas(pdf_filename, pagesize=A4)
width, height = A4
styles = getSampleStyleSheet()


class Report:

    def __init__(self):
        self.sonido = None

    def add_page_header(self, c, title, fecha_reporte):
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

    def add_user_info(self, c, usuario):
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
            "static/" + usuario[8],
            400,
            height - 250,
            width=100,
            height=100,
            mask="auto",
        )

        # Dibujar una línea horizontal debajo de la información del usuario
        c.line(50, height - 260, width - 50, height - 260)

    def add_table(self, c, data, x, y):
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

    def new_page(self, c):
        c.showPage()
