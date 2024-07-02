# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 15:34:08 2023

@author: sebas
"""

from flask import Flask, render_template, Response
from flask_socketio import SocketIO, emit
import cv2
import numpy as np

app = Flask(__name__)
#app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

def video_stream():
    cap = cv2.VideoCapture(0)
    while True:
        success, image = cap.read()
        if success:
            image = cv2.resize(image, (640, 480))
            image = cv2.imencode('.jpg', image)[1].tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + image + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)