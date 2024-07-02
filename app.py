# -*- coding: utf-8 -*-
"""
Created on Mon July 1 15:34:08 2024
@author: sebas
"""
from flask import Flask, render_template, Response, request, redirect, jsonify
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


# sound3 = pygame.mixer.Sound(audio_file3)

audio = Reproductor()


@app.route("/")
def index():
    audio.play_bien()
    return render_template("index.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/analyzer")
def analyzer():
    return render_template("analizer.html")


@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/calibracion")
def calibracion():
    return render_template("calibracion.html")


@app.route("/usuarios")
def usuarios():

    try:
        # Configuración de la conexión a la base de datos

        db = Database(db_config)
        users = db.fetch_users()

        return render_template("usuarios.html", users=users)

    except Exception as e:
        return render_template("usuarios.html", errorbase="error")


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

        db.insert_user(
            nombre, cedula, telefono, estatura, edad, peso, genero, "fotoooo"
        )
        return jsonify({"status": "success"})
    # return redirect("/usuarios")

    except Exception as err:
        return jsonify({"status": "error", "message": str(err)})


@app.route("/delete_user", methods=["POST"])
def delete_user():
    data = request.get_json()
    id_usuario = data["idUsuario"]
    db = Database(db_config)
    db.delete_user(id_usuario)
    return jsonify({"message": "Usuario eliminado correctamente"})


def video_stream(camera):
    while True:
        frame = camera.get_frame()
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n")


@app.route("/video_feed")
def video_feed():
    return Response(
        video_stream(VideoCamera()),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


if __name__ == "__main__":
    app.run(debug=True)
