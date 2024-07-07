# -*- coding: utf-8 -*-
"""
Created on Mon July 1 15:34:08 2024
@author: sebas
"""
# LIBRERIAS GENERALES *****************************************
import os
import shutil
from flask import Flask, render_template, Response, request, redirect, jsonify
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

db_config = {
    "user": "android",
    "password": "12345678",
    "host": "localhost",
    "database": "pies",
}

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
    return render_template("dashboard.html")


@app.route("/calibracion")
def calibracion():
    return render_template("calibracion.html")


@app.route("/usuarios")
def usuarios():

    if video.state():
        video.set_mode("procesada")
        video.stop()

    try:
        # Configuración de la conexión a la base de datos
        db = Database(db_config)
        users = db.fetch_users()
        return render_template("usuarios.html", users=users)

    except Exception as e:
        audio.play_error()
        return render_template("usuarios.html", errorbase="error")


@app.route("/analyzer", methods=["GET"])
def analyzer():
    usuario = request.args.get("usuario")
    usuario = json.loads(usuario)
    return render_template("analizer.html", usuario=usuario)


# Ruta para manejar el envío del formulario
@app.route("/submit", methods=["POST"])
def submit():

    try:
        db = Database(db_config)

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


@app.route("/select_user", methods=["POST"])
def select_user():
    data = request.get_json()
    id_usuario = data["idUsuario"]
    db = Database(db_config)

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
    db = Database(db_config)

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
    db = Database(db_config)
    db.delete_user(id_usuario)

    return jsonify({"message": "Usuario eliminado correctamente"})


def video_stream(camera):
    if video.state() == False:
        video.start()

    while True:
        frame = camera.get_frame()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n")


@app.route("/video_feed")
def video_feed():
    return Response(
        video_stream(video),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@app.route("/set_mode", methods=["POST"])
def set_mode():
    data = request.get_json()
    camera_mode = data.get("mode")
    video.set_mode(camera_mode)
    # print("EL DATO QUE LLEGA ES: ", camera_mode)
    return jsonify({"message": "Mode set to " + camera_mode})


@app.route("/set_controles", methods=["POST"])
def set_controles():
    data = request.get_json()
    tipo_control = data.get("control")
    valor_control = data.get("valor")

    video.set_hsv_val(tipo_control, valor_control)

    print("TIPOOOO: " + tipo_control + "  VALOR:" + valor_control)
    return jsonify({"message": "TIPOOOO: " + tipo_control + "  VALOR:" + valor_control})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
