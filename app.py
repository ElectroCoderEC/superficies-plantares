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

# CLASES CREADAS PROPIAS **************************************
from camera import VideoCamera
from database import Database
from audio import Reproductor


app = Flask(
    __name__,
    static_url_path="",
    static_folder="static",
    template_folder="templates",
)
socketio = SocketIO(app)

db = Database()
audio = Reproductor()
video = VideoCamera()
video.set_mode("procesada")


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
    print("datooo", cuentaP)

    return render_template("dashboard.html", cuentaU=cuentaU, cuentaP=cuentaP)


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

        audio.play_registro()
        return jsonify({"status": "success"})
    # return redirect("/usuarios")

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
        frame, valorIzquierda, valorDerecha, tipoIzquierda, tipoDerecha, txtBien = (
            camera.get_frame()
        )
        socketio.emit(
            "status_update",
            {
                "Pizquierdo": valorIzquierda,
                "Pderecho": valorDerecha,
                "Tizquierdo": tipoIzquierda,
                "Tderecho": tipoDerecha,
                "txtBien": txtBien,
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


if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=5000, debug=True)
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
