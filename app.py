# -*- coding: utf-8 -*-
"""
Created on Mon July 1 15:34:08 2024
@author: sebas
"""
# LIBRERIAS GENERALES *****************************************
import os
import shutil
from flask import Flask, render_template, Response, request, redirect, jsonify
from flask_socketio import SocketIO, emit
import cv2
from werkzeug.utils import secure_filename
import json
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Image


# CLASES CREADAS PROPIAS **************************************
from camera import VideoCamera
from database import Database
from audio import Reproductor
from report import Report

app = Flask(
    __name__,
    static_url_path="",
    static_folder="static",
    template_folder="templates",
)
socketio = SocketIO(app)

db = Database()
report = Report()
audio = Reproductor()
video = VideoCamera()
video.set_mode("procesada")


# FUNCION REPORT
@app.route("/reporte", methods=["POST"])
def reporte():

    try:

        data = request.get_json()
        idUsuario = data.get("idUsuario")
        usuario = db.get_user_data(idUsuario)
        pruebas = db.fetch_test(idUsuario)

        cedula = usuario[2]

        print("pruebas: ", pruebas)
        print("cedula: ", cedula)

        fechaInforme = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Crear el PDF
        pdf_filename = "static/reportes/reporte_" + fechaInforme + ".pdf"
        c = canvas.Canvas(pdf_filename, pagesize=A4)
        width, height = A4

        # Agregar encabezado y datos del usuario en la primera página
        report.add_page_header(
            c,
            "Reporte de Análisis de Superficie Plantar",
            fechaInforme,
        )
        report.add_user_info(c, usuario)

        y_position = height - 300
        contador = 0

        # Crear la ruta de la carpeta
        carpeta_original = f"static/usuarios/{cedula}/fotos/original/"

        # Contar archivos en la carpeta
        cntImagenes = len(
            [
                nombre
                for nombre in os.listdir(carpeta_original)
                if os.path.isfile(os.path.join(carpeta_original, nombre))
            ]
        )

        # Agregar datos de las pruebas
        for prueba in pruebas:
            contador += 1

            if y_position < 300:  # Umbral para crear una nueva página
                report.new_page(c)
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
            report.add_table(c, table_data, 50, y_position - 70)
            y_position -= 80

            # Agregar segunda tabla con imágenes
            table_data2 = [
                ["Normal", "PseudoColor"],
                [
                    Image(
                        "static/usuarios/"
                        + cedula
                        + "/fotos/procesada/"
                        + str(cntImagenes)
                        + "_imagen_normal.png",
                        width=150,
                        height=150,
                    ),
                    Image(
                        "static/usuarios/"
                        + cedula
                        + "/fotos/procesada/"
                        + str(cntImagenes)
                        + "_imagen_pseudo.png",
                        width=150,
                        height=150,
                    ),
                ],
            ]

            if y_position < 300:  # Umbral para crear una nueva página
                report.new_page(c)
                y_position = height - 50

            report.add_table(c, table_data2, 50, y_position - 200)
            y_position -= 180

            # Agregar tercera tabla con imágenes
            table_data3 = [
                ["Procesada", "Máscara"],
                [
                    Image(
                        "static/usuarios/"
                        + cedula
                        + "/fotos/procesada/"
                        + str(cntImagenes)
                        + "_imagen_procesada.png",
                        width=150,
                        height=150,
                    ),
                    Image(
                        "static/usuarios/"
                        + cedula
                        + "/fotos/procesada/"
                        + str(cntImagenes)
                        + "_imagen_mask.png",
                        width=150,
                        height=150,
                    ),
                ],
            ]

            if y_position < 300:  # Umbral para crear una nueva página
                report.new_page(c)
                y_position = height - 50

            report.add_table(c, table_data3, 50, y_position - 200)
            y_position -= 220

        c.save()
        print("PDF creado exitosamente:", pdf_filename)

        # Obtener la ruta del directorio actual del script
        current_dir = os.path.dirname(__file__)
        # Construir la ruta completa al directorio de reportes
        reportes_dir = os.path.join(current_dir, "static", "reportes")

        # Construir la ruta completa al archivo PDF generado
        pdf_filename = os.path.join(reportes_dir, "reporte_" + fechaInforme + ".pdf")
        # Abrir el PDF automáticamente
        if os.name == "nt":  # Para Windows
            os.startfile(pdf_filename)

        audio.play_reporte()

        return jsonify({"status": "success"})

    except Exception as err:
        audio.play_error()
        return jsonify({"status": "error", "message": str(err)})


# FUNCION PAGINA PRINCIPAL
@app.route("/")
def index():
    if video.state():
        video.set_mode("procesada")
        video.stop()
    audio.play_intro()
    return render_template("index.html")


@app.route("/dashboard")
def dashboard():
    if video.state():
        video.stop()
    # try:
    # Configuración de la conexión a la base de datos
    # db = Database(db_config)
    cuentaU = db.get_number_users()
    # db = Database(db_config)
    cuentaP = db.get_number_plantillas()

    cuentaT = db.get_number_tests()

    # Crear la ruta de la carpeta
    carpeta_reportes = f"static/reportes"

    # Contar archivos en la carpeta
    cntReportes = len(
        [
            nombre
            for nombre in os.listdir(carpeta_reportes)
            if os.path.isfile(os.path.join(carpeta_reportes, nombre))
        ]
    )

    return render_template(
        "dashboard.html",
        cuentaU=cuentaU,
        cuentaP=cuentaP,
        cuentaT=cuentaT,
        reportes=cntReportes,
    )


# except Exception as e:
#      audio.play_error()
#     return render_template("usuarios.html", errorbase="error: " + str(e))


@app.route("/calibracion")
def calibracion():
    variables = db.fetch_configuraciones()
    return render_template("calibracion.html", variables=variables)


@app.route("/plantillas")
def plantillas():

    if video.state():
        video.set_mode("procesada")
        video.stop()

    try:
        # Configuración de la conexión a la base de datos
        # db = Database(db_config)
        plantillas = db.fetch_plantillas()
        return render_template("plantillas.html", plantillas=plantillas)

    except Exception as e:
        audio.play_error()
        return render_template("plantillas.html", errorbase="error")


@app.route("/usuarios")
def usuarios():

    if video.state():
        video.set_mode("procesada")
        video.stop()

    try:
        # Configuración de la conexión a la base de datos
        # db = Database(db_config)
        users = db.fetch_users()
        return render_template("usuarios.html", users=users)

    except Exception as e:
        audio.play_error()
        return render_template("usuarios.html", errorbase="error")


@app.route("/analyzer", methods=["GET"])
def analyzer():
    usuario = request.args.get("usuario")
    usuario = json.loads(usuario)
    variables = db.fetch_configuraciones()
    return render_template("analizer.html", usuario=usuario, variables=variables)


# Ruta para manejar el envío del formulario
@app.route("/submit", methods=["POST"])
def submit():

    try:
        # db = Database(db_config)
        nombre = request.form["nuevoNombre"]
        cedula = request.form["nuevoCedula"]
        telefono = request.form["nuevoTelefono"]
        estatura = request.form["nuevoEstatura"]
        edad = request.form["nuevoEdad"]
        peso = request.form["nuevoPeso"]
        genero = request.form["gender"]
        imagen = request.form["nuevaFotoOculta"]
        imagenInput = request.files["nuevaFoto"]

        # Crear las carpetas necesarias dentro de 'static'
        static_path = os.path.join(app.root_path, "static/usuarios")
        base_path = os.path.join(static_path, cedula)
        fotos_path = os.path.join(base_path, "fotos")
        reportes_path = os.path.join(base_path, "reportes")
        perfil_path = os.path.join(fotos_path, "perfil")
        original_path = os.path.join(fotos_path, "original")
        procesada_path = os.path.join(fotos_path, "procesada")

        os.makedirs(fotos_path, exist_ok=True)
        os.makedirs(perfil_path, exist_ok=True)
        os.makedirs(original_path, exist_ok=True)
        os.makedirs(procesada_path, exist_ok=True)
        os.makedirs(reportes_path, exist_ok=True)

        img = None
        if (("hombre" in imagen) or ("mujer" in imagen)) and len(
            imagenInput.filename
        ) == 0:

            if "hombre" in imagen:
                img = cv2.imread("static/assets/images/hombre.png")
                imagen = "static/assets/images/hombre.png"
            elif "mujer" in imagen:
                img = cv2.imread("static/assets/images/mujer.png")
                imagen = "static/assets/images/mujer.png"

            img = cv2.imread(imagen, cv2.IMREAD_UNCHANGED)
            cv2.imwrite(perfil_path + "/perfil.png", img)

        else:

            file = request.files["nuevaFoto"]
            if file:
                filename = secure_filename(file.filename)
                file_path = perfil_path + "/" + filename
                file.save(file_path)

                # Leer y guardar la imagen usando OpenCV
                img = cv2.imread(file_path, cv2.IMREAD_UNCHANGED)
                cv2.imwrite(perfil_path + "/perfil.png", img)

        db.insert_user(
            nombre,
            cedula,
            telefono,
            estatura,
            edad,
            peso,
            genero,
            "usuarios/" + cedula + "/fotos/perfil/perfil.png",
        )

        audio.play_registro()
        return jsonify({"status": "success"})
    # return redirect("/usuarios")

    except Exception as err:
        audio.play_error()
        return jsonify({"status": "error", "message": str(err)})


# Ruta para manejar el envío del formulario PLANTILLA
@app.route("/submitPlantilla", methods=["POST"])
def submitPlantilla():

    try:
        # db = Database(db_config)
        nombre = request.form["nuevoPlantilla"]
        descripcion = request.form["nuevoDescripcion"]
        db.insert_pie(nombre, descripcion)

        # audio.play_registro()
        return jsonify({"status": "success"})
    # return redirect("/usuarios")

    except Exception as err:
        audio.play_error()
        return jsonify({"status": "error", "message": str(err)})


def tipoPie(tipo):

    if tipo == "plano":
        numero = "1"
    elif tipo == "plano normal":
        numero = "2"
    elif tipo == "plano":
        numero = "3"
    elif tipo == "normal cavo":
        numero = "4"
    elif tipo == "cavo":
        numero = "5"
    elif tipo == "cavo fuerte":
        numero = "6"
    elif tipo == "cavo extremo":
        numero = "7"
    else:
        numero = "0"

    return numero


@app.route("/set_guardar", methods=["POST"])
def set_guardar():
    try:
        data = request.get_json()

        txtizquierda = data["tipoIzquierdo"]
        id_izquierda = tipoPie(txtizquierda.lower())

        txtderecha = data["tipoDerecho"]
        id_derecha = tipoPie(txtderecha.lower())

        id_usuario = data["idUsuario"]
        x_izquierdo = data["xI"]
        y_izquierdo = data["yI"]
        porcentaje_izquierda = data["valorIzquierdo"]
        id_plantilla_izquierda = txtizquierda
        x_derecha = data["xD"]
        y_derecha = data["yD"]
        porcentaje_derecha = data["valorDerecho"]
        id_plantilla_derecha = txtderecha
        foto = data["foto"]

        db.insert_prueba(
            id_usuario,
            x_izquierdo,
            y_izquierdo,
            porcentaje_izquierda,
            id_plantilla_izquierda,
            x_derecha,
            y_derecha,
            porcentaje_derecha,
            id_plantilla_derecha,
            foto,
        )

        audio.play_prueba()
        return jsonify({"status": "success"})

    except Exception as err:
        audio.play_error()
        return jsonify({"status": "error", "message": str(err)})


@app.route("/save_imagen_procesada", methods=["POST"])
def save_imagen_procesada():
    try:
        data = request.get_json()
        cedula = data["cedula"]
        imagen_normal, imagen_mask, imagen_pseudo, imagen_procesada = video.get_images()
        # Crear la ruta de la carpeta
        carpeta = f"static/usuarios/{cedula}/fotos/procesada/"
        carpeta_original = f"static/usuarios/{cedula}/fotos/original/"

        # Asegurarse de que la carpeta existe
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)

        # Asegurarse de que la carpeta existe
        if not os.path.exists(carpeta_original):
            os.makedirs(carpeta_original)

        # Contar archivos en la carpeta
        contador = len(
            [
                nombre
                for nombre in os.listdir(carpeta_original)
                if os.path.isfile(os.path.join(carpeta_original, nombre))
            ]
        )
        contador = contador + 1
        # Crear el nombre del archivo con el contador
        nombre_fotoOriginal = f"{carpeta_original}{contador}_imagen_normal.png"

        nombre_archivo1 = f"{carpeta}{contador}_imagen_normal.png"
        nombre_archivo2 = f"{carpeta}{contador}_imagen_mask.png"
        nombre_archivo3 = f"{carpeta}{contador}_imagen_pseudo.png"
        nombre_archivo4 = f"{carpeta}{contador}_imagen_procesada.png"

        # Guardar la imagen
        cv2.imwrite(nombre_fotoOriginal, imagen_normal)

        cv2.imwrite(nombre_archivo1, imagen_normal)
        cv2.imwrite(nombre_archivo2, imagen_mask)
        cv2.imwrite(nombre_archivo3, imagen_pseudo)
        cv2.imwrite(nombre_archivo4, imagen_procesada)

        return jsonify(
            {"status": "success", "carpeta": carpeta, "foto": nombre_archivo4}
        )

    except Exception as err:
        audio.play_error()
        return jsonify({"status": "error", "message": str(err)})


@app.route("/select_user", methods=["POST"])
def select_user():
    data = request.get_json()
    id_usuario = data["idUsuario"]
    # db = Database(db_config)

    # Obtener la cédula del usuario a eliminar (asumiendo que tienes un método para eso)
    print(f"Obteniendo ID: {id_usuario}")
    usuario = db.get_user_data(id_usuario)
    print(f"Usuario obtenidooo: {usuario}")

    return jsonify({"redirect": "/analyzer", "usuario": usuario})
    # return render_template("analizer.html", usuario=usuario)


@app.route("/delete_user", methods=["POST"])
def delete_user():
    data = request.get_json()
    id_usuario = data["idUsuario"]
    # db = Database(db_config)

    # Obtener la cédula del usuario a eliminar (asumiendo que tienes un método para eso)
    print(f"Obteniendo cédula para el usuario con ID: {id_usuario}")
    cedula = db.get_user_cedula(id_usuario)
    print(f"Cédula obtenida: {cedula}")

    # Eliminar las carpetas asociadas al usuario
    static_path = os.path.join(app.root_path, "static/usuarios")
    user_folder = os.path.join(static_path, cedula)

    if os.path.exists(user_folder):
        shutil.rmtree(user_folder)

    # Eliminar el usuario de la base de datos
    # db = Database(db_config)
    db.delete_user(id_usuario)

    return jsonify({"message": "Usuario eliminado correctamente"})


@app.route("/delete_plantilla", methods=["POST"])
def delete_plantilla():
    data = request.get_json()
    id_plantilla = data["idPlantilla"]
    # db = Database(db_config)
    db.delete_pie(id_plantilla)
    return jsonify({"message": "Plantilla borrada correctamente"})


def video_stream(camera):
    if video.state() == False:
        video.start()

    while True:
        (
            frame,
            valorIzquierda,
            valorDerecha,
            tipoIzquierda,
            tipoDerecha,
            txtBien,
            xIzquierda,
            yIzquierda,
            xDerecha,
            yDerecha,
        ) = camera.get_frame()
        socketio.emit(
            "status_update",
            {
                "Pizquierdo": valorIzquierda,
                "Pderecho": valorDerecha,
                "Tizquierdo": tipoIzquierda,
                "Tderecho": tipoDerecha,
                "txtBien": txtBien,
                "xLeft": xIzquierda,
                "yLeft": yIzquierda,
                "xRight": xDerecha,
                "yRight": yDerecha,
            },
        )
        # socketio.sleep(0.1)
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n")


@app.route("/video_feed")
def video_feed():
    return Response(
        video_stream(video),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@app.route("/set_check", methods=["POST"])
def setcheck():
    data = request.get_json()
    check = data.get("check")
    video.set_check(check)
    # print("EL DATO QUE LLEGA ES: ", camera_mode)
    return jsonify({"message": "Check: " + check})


@app.route("/set_mode", methods=["POST"])
def set_mode():
    data = request.get_json()
    camera_mode = data.get("mode")
    video.set_mode(camera_mode)
    # print("EL DATO QUE LLEGA ES: ", camera_mode)
    return jsonify({"message": "Mode set to " + camera_mode})


@app.route("/set_imagen", methods=["POST"])
def set_imagen():
    data = request.get_json()
    estado = data.get("estado")

    if estado == "ON":
        video.set_Capturar()

    elif estado == "OFF":
        video.set_reproducir()

    # print("EL DATO QUE LLEGA ES: ", camera_mode)
    return jsonify({"message": "ESTADO REPRODUCIENDO: " + estado})


@app.route("/set_controles", methods=["POST"])
def set_controles():
    data = request.get_json()
    tipo_control = data.get("control")
    valor_control = data.get("valor")

    video.set_hsv_val(tipo_control, valor_control)

    # print("TIPOOOO: " + tipo_control + "  VALOR:" + valor_control)
    return jsonify({"message": "TIPOOOO: " + tipo_control + "  VALOR:" + valor_control})


@app.route("/save_hsv", methods=["POST"])
def save_hsv():
    data = request.get_json()

    lower_h = data.get("lower-h")
    lower_s = data.get("lower-s")
    lower_v = data.get("lower-v")
    upper_h = data.get("upper-h")
    upper_s = data.get("upper-s")
    upper_v = data.get("upper-v")
    lower_h2 = data.get("lower-h-dedos")
    lower_s2 = data.get("lower-s-dedos")
    lower_v2 = data.get("lower-v-dedos")
    upper_h2 = data.get("upper-h-dedos")
    upper_s2 = data.get("upper-s-dedos")
    upper_v2 = data.get("upper-v-dedos")

    # print("TIPOOOO: " + tipo_control + "  VALOR:" + valor_control)

    try:
        # db = Database(db_config)
        db.update_hsv(
            lower_h,
            lower_s,
            lower_v,
            upper_h,
            upper_s,
            upper_v,
            lower_h2,
            lower_s2,
            lower_v2,
            upper_h2,
            upper_s2,
            upper_v2,
        )
        return jsonify({"status": "success"})

    # return redirect("/usuarios")

    except Exception as err:
        audio.play_error()
        return jsonify({"status": "error", "message": str(err)})


@app.route("/get_hsv", methods=["POST"])
def get_hsv():

    try:
        variables = db.fetch_configuraciones()
        socketio.emit("status_hsv", {"variables": variables})
        return jsonify({"status": "success"})

    except Exception as err:
        audio.play_error()
        return jsonify({"status": "error", "message": str(err)})


@app.route("/update_plantilla", methods=["POST"])
def update_plantilla():

    try:
        id = request.form["idPlantilla"]
        nombre = request.form["editarPlantilla"]
        descripcion = request.form["editarDescripcion"]

        db.update_plantilla(id, nombre, descripcion)
        return jsonify({"status": "success"})

    except Exception as err:
        audio.play_error()
        return jsonify({"status": "error", "message": str(err)})


@app.route("/get_plantilla", methods=["POST"])
def get_plantilla():

    try:
        data = request.get_json()
        id = data.get("idPlantilla")
        datos = db.get_plantilla(id)
        return jsonify({"status": "success", "plantilla": datos})

    except Exception as err:
        audio.play_error()
        return jsonify({"status": "error", "message": str(err)})


if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=5000, debug=True)
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
