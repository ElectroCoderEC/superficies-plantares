# -*- coding: utf-8 -*-
"""
Created on Wed Feb  8 15:34:08 2023

@author: sebas
"""

"""
from main import app

if __name__ == '__main__':
    app.run(debug=True)
"""

from flask import Flask, render_template, Response, request, redirect, jsonify

import cv2
import numpy as np
import math
import pygame
import threading
import time
import pickle

import mysql.connector


app = Flask(
    __name__,
    static_url_path="",
    static_folder="static",
    template_folder="templates",
)


# Inicializar pygame para la reproducción de audio
pygame.init()
pygame.mixer.init()
# audio bienvenida
audio_file1 = "bien.mp3"
sound1 = pygame.mixer.Sound(audio_file1)
# colocarse correctamente
audio_file2 = "coloquese.mp3"
sound2 = pygame.mixer.Sound(audio_file2)
# Calculo
audio_file3 = "medicion.mp3"
sound3 = pygame.mixer.Sound(audio_file3)

malcolocado = 0
factor = 12.3


# Función para reproducir el audio
def play_audio1():
    sound1.play()


def play_audio2():
    sound2.play()


def play_audio3():
    sound3.play()


# Crear un hilo para la reproducción de audio
audio_thread = threading.Thread(target=play_audio1)
audio_thread.start()

pseudo_color = None


# Función para calcular los puntos de una línea perpendicular
def calculate_perpendicular_points(px, py, m, length):
    if m != float("inf"):
        dx = length / math.sqrt(1 + m**2)
        dy = m * dx
    else:
        dx = 0
        dy = length
    perp_x1 = int(px - dx)
    perp_y1 = int(py - dy)
    perp_x2 = int(px + dx)
    perp_y2 = int(py + dy)
    return (perp_x1, perp_y1), (perp_x2, perp_y2)


def pendiente(x1, y1, x2, y2):
    # Calcular la pendiente de la línea original
    if x2 != x1:
        m1 = (y2 - y1) / (x2 - x1)
    else:
        m1 = float("inf")
    # Calcular la pendiente de la línea perpendicular
    if m1 != float("inf"):
        m2 = -1 / m1
    else:
        m2 = 0
    # Calcular el punto medio de la línea original
    mid_x = (x1 + x2) // 2
    mid_y = (y1 + y2) // 2
    return m2


def get_extreme2(cont, valor):
    if len(cont) == 0:
        return None, None, None, None, None, None
    cont = cont[:, 0, :]  # Obtener los puntos del contorno
    x, y = cont[:, 0], cont[:, 1]

    if len(x) == 0 or len(y) == 0:
        return None, None, None, None, None, None
    # Encontrar los índices de los puntos extremos en x e y
    leftmost_idx = np.argmin(x)
    rightmost_idx = np.argmax(x)
    topmost_idx = np.argmin(y)
    bottommost_idx = np.argmax(y)
    # Encontrar los puntos extremos
    left = cont[leftmost_idx]
    right = cont[rightmost_idx]
    top = cont[topmost_idx]
    bottom = cont[bottommost_idx]
    # Discriminar entre superior e inferior
    y_median = np.median(y)  # Mediana de las coordenadas
    # Inicializar puntos superiores
    left_top = None
    right_top = None
    # Encontrar puntos superiores
    for point in cont:
        if point[1] < y_median:  # Está arriba de la mediana
            if left_top is None or point[0] < left_top[0]:
                left_top = point
            if right_top is None or point[0] > right_top[0]:
                right_top = point
    if valor == 0:
        pass
        # print("Izquierda")
    elif valor == 1:
        # print("Derecha")
        # Invertir los puntos para la parte derecha
        left, right = right, left
        left_top, right_top = right_top, left_top
        # print(bottom, right, right_top)
    return bottom, right, right_top, left


def distance_point_to_line(x, y, A, B, C):
    return np.abs(A * x + B * y + C) / np.sqrt(A**2 + B**2)


# Función para combinar contornos
def combinar_contornos(contornos1, contornos2):
    contornos_combinados = contornos1 + contornos2
    return contornos_combinados


def find_intersections(contour, line_point1, line_point2):
    intersections = []

    for i in range(len(contour)):
        point1 = contour[i][0]
        point2 = contour[(i + 1) % len(contour)][0]

        x1, y1 = point1
        x2, y2 = point2
        x3, y3 = line_point1
        x4, y4 = line_point2

        # Calcular las coordenadas del punto de intersección entre las líneas (x1, y1)-(x2, y2) y (x3, y3)-(x4, y4)
        # Usando la fórmula del método de determinantes para la intersección de dos líneas
        denominator = ((x1 - x2) * (y3 - y4)) - ((y1 - y2) * (x3 - x4))

        if denominator != 0:
            intersect_x = (
                ((x1 * y2) - (y1 * x2)) * (x3 - x4)
                - (x1 - x2) * ((x3 * y4) - (y3 * x4))
            ) / denominator
            intersect_y = (
                ((x1 * y2) - (y1 * x2)) * (y3 - y4)
                - (y1 - y2) * ((x3 * y4) - (y3 * x4))
            ) / denominator

            # Verificar si el punto de intersección está dentro del segmento de línea
            if min(x1, x2) <= intersect_x <= max(x1, x2) and min(
                y1, y2
            ) <= intersect_y <= max(y1, y2):
                intersections.append((int(intersect_x), int(intersect_y)))

    return intersections


# Función para calcular la distancia euclidiana entre dos puntos
def distance(point1, point2):
    return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)


# Función para filtrar puntos de intersección que están muy cerca entre sí
def filter_close_points(intersections, min_distance=10):
    filtered_intersections = []
    for i in range(len(intersections)):
        is_close = False
        for j in range(i + 1, len(intersections)):
            if distance(intersections[i], intersections[j]) < min_distance:
                is_close = True
                break
        if not is_close:
            filtered_intersections.append(intersections[i])
    return filtered_intersections


def categorizar_pie(porcentaje):
    if porcentaje >= 0 and porcentaje < 35:
        return "plano"
    elif porcentaje >= 35 and porcentaje < 40:
        return "plano normal"
    elif porcentaje >= 40 and porcentaje < 55:
        return "normal"
    elif porcentaje >= 55 and porcentaje < 60:
        return "normal cavo"
    elif porcentaje >= 60 and porcentaje <= 74:
        return "cavo"
    elif porcentaje >= 75 and porcentaje <= 100:
        return "cavo fuerte"
    else:
        return "Porcentaje fuera de rango"


def detectar_contornos_planta(
    framed, lower_bound, upper_bound, lower_bound2, upper_bound2
):
    global malcolocado, pseudo_color

    try:
        #           DETECCION DE PLANTA
        # Convertir la imagen de BGR a HSV
        frame = framed.copy()
        frame2 = framed.copy()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # Threshold la imagen para obtener solo los píxeles dentro del rango de color
        mask = cv2.inRange(hsv, lower_bound, upper_bound)
        # Aplicar operaciones morfológicas para eliminar el ruido
        mask = cv2.erode(mask, None, iterations=1)
        # Detectar contornos en la imagen filtrada
        contours, _ = cv2.findContours(
            mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        # Definir la línea media del fotograma
        frame_width = frame.shape[1]
        middle_line = frame_width // 2
        # Listas para almacenar los contornos de cada pie
        contornos_izquierdo = []
        contornos_derecho = []
        # Puntos extremos inicializados a valores imposibles
        topmost_left = (0, frame.shape[0])
        bottommost_left = (0, 0)
        topmost_right = (frame_width, frame.shape[0])
        bottommost_right = (frame_width, 0)
        # Seleccionar los dos contornos más grandes
        sort = np.argsort([cv2.contourArea(x) for x in contours])
        i, j = sort[-2:]
        #            DETECCION DE DEDOS______________________________________
        frame2 = framed.copy()
        hsv2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2HSV)
        mask2 = cv2.inRange(hsv2, lower_bound2, upper_bound2)
        mask2 = cv2.erode(mask2, None, iterations=1)
        contours2, _ = cv2.findContours(
            mask2.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        frame_width2 = frame2.shape[1]
        middle_line2 = frame_width2 // 2
        contornos_izquierdo2 = []
        contornos_derecho2 = []
        topmost_left2 = (0, frame2.shape[0])
        bottommost_left2 = (0, 0)
        topmost_right2 = (frame_width2, frame2.shape[0])
        bottommost_right2 = (frame_width2, 0)
        highest_left_point2 = (0, frame.shape[0])  # Punto más alto izquierdo
        highest_right_point2 = (frame_width2, frame2.shape[0])  # Punto más alto derecho
        FUNCIONAL = True
    except:
        FUNCIONAL = False
        TIPO1 = ""
        TIPO2 = ""
    try:
        COLOCADO = False
        if FUNCIONAL:
            # Clasificar y procesar los contornos de las plantas
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 4050:  # tamaño de pie

                    # Calcular el momento para encontrar el centro del contorno
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        cX = int(M["m10"] / M["m00"])
                        cY = int(M["m01"] / M["m00"])
                    else:
                        cX, cY = 0, 0

                    # Dibujar el contorno
                    cv2.drawContours(frame, [contour], -1, (0, 255, 0), 1)
                    # Clasificar el contorno según su posición
                    if cX < middle_line:
                        contornos_izquierdo.append(contour)
                        # Actualizar puntos extremos para el pie izquierdo
                        topmost_left = min(
                            topmost_left,
                            tuple(contour[contour[:, :, 1].argmin()][0]),
                            key=lambda x: x[1],
                        )
                        bottommost_left = max(
                            bottommost_left,
                            tuple(contour[contour[:, :, 1].argmax()][0]),
                            key=lambda x: x[1],
                        )
                    else:
                        contornos_derecho.append(contour)
                        # Actualizar puntos extremos para el pie derecho
                        topmost_right = min(
                            topmost_right,
                            tuple(contour[contour[:, :, 1].argmin()][0]),
                            key=lambda x: x[1],
                        )
                        bottommost_right = max(
                            bottommost_right,
                            tuple(contour[contour[:, :, 1].argmax()][0]),
                            key=lambda x: x[1],
                        )

                    # Encontrar los puntos superiores e inferiores del contorno
                    topmost = tuple(contour[contour[:, :, 1].argmin()][0])
                    bottommost = tuple(contour[contour[:, :, 1].argmax()][0])
                    distanceT = np.sqrt(
                        (bottommost[0] - topmost[0]) ** 2
                        + (bottommost[1] - topmost[1]) ** 2
                    )
                    Tcm = distanceT / factor
                    print(Tcm)
                    # Calcular el punto medio entre topmost y bottommost
                    punto_medio = (
                        (topmost[0] + bottommost[0]) // 2,
                        (topmost[1] + bottommost[1]) // 2,
                    )
                    # Dibujar el punto medio en el fotograma
                    # cv2.circle(frame, punto_medio, 5, (0, 255, 0), -1)  # Verde

            # Dibujar el contorno dedos
            for contour2 in contours2:
                area = cv2.contourArea(contour2)
                if 10000 > area > 100:  # Tamaño de dedo gordo
                    M = cv2.moments(contour2)
                    if M["m00"] != 0:
                        cX = int(M["m10"] / M["m00"])
                        cY = int(M["m01"] / M["m00"])
                    else:
                        cX, cY = 0, 0

                    if cX < middle_line2:
                        contornos_izquierdo2.append(contour2)
                        topmost_left2 = min(
                            topmost_left2,
                            tuple(contour2[contour2[:, :, 1].argmin()][0]),
                            key=lambda x: x[1],
                        )
                        bottommost_left2 = max(
                            bottommost_left2,
                            tuple(contour2[contour2[:, :, 1].argmax()][0]),
                            key=lambda x: x[1],
                        )
                        if topmost_left2[1] < highest_left_point2[1]:
                            highest_left_point2 = topmost_left2
                    else:
                        contornos_derecho2.append(contour2)
                        topmost_right2 = min(
                            topmost_right2,
                            tuple(contour2[contour2[:, :, 1].argmin()][0]),
                            key=lambda x: x[1],
                        )
                        bottommost_right2 = max(
                            bottommost_right2,
                            tuple(contour2[contour2[:, :, 1].argmax()][0]),
                            key=lambda x: x[1],
                        )
                        if topmost_right2[1] < highest_right_point2[1]:
                            highest_right_point2 = topmost_right2

            #             GRAFICAR PUNTOS DE PLANTA Y DEDOS...................
            if len(contornos_izquierdo) > 0:
                for contour in contornos_izquierdo:
                    # Obtener los puntos extremos
                    bot1, right, right_top, left1 = get_extreme2(contour, 0)
                    if right is not None and right_top is not None:
                        # Asegurarse de que los puntos son tuplas con valores enteros
                        right = tuple(map(int, right))
                        left1 = tuple(map(int, left1))
                        right_top = tuple(map(int, right_top))
                        # Calcular el vector dirección entre right y right_top
                        vector = np.array(right_top) - np.array(right)
                        length = np.linalg.norm(vector)
                        # estender linea normal
                        extended_length = length * 0.7
                        extended_length2 = length * 0.2
                        direction_vector = vector / length
                        extended_point = tuple(
                            np.array(right_top) + extended_length * direction_vector
                        )
                        extended_point2 = tuple(
                            np.array(right) - extended_length2 * direction_vector
                        )
                        extended_point = tuple(map(int, extended_point))
                        # LINEA NORMAL
                        cv2.line(
                            frame,
                            tuple(map(int, extended_point)),
                            tuple(map(int, extended_point2)),
                            (255, 255, 255),
                            1,
                            cv2.LINE_AA,
                        )
                        x1, y1 = tuple(map(int, extended_point))
                        x2, y2 = tuple(map(int, extended_point2))
                        m2 = pendiente(x1, y1, x2, y2)
                        length = 100
                        x3, y3 = tuple(map(int, left1))
                        x4, y4 = tuple(map(int, highest_left_point2))
                        # LINEA PERPENDICULAR DEDO
                        (perp_max_x12, perp_max_y12), (perp_max_x22, perp_max_y22) = (
                            calculate_perpendicular_points(x4, y4, m2, length)
                        )
                        cv2.line(
                            frame,
                            (perp_max_x12, perp_max_y12),
                            (perp_max_x22, perp_max_y22),
                            (255, 0, 0),
                            1,
                            cv2.LINE_AA,
                        )
                        # LINEA PERPENDICULAR X
                        (perp_max_x132, perp_max_y132), (
                            perp_max_x232,
                            perp_max_y232,
                        ) = calculate_perpendicular_points(x3, y3, m2, length)
                        cv2.line(
                            frame,
                            (x3, y3),
                            (perp_max_x232, perp_max_y232),
                            (255, 0, 0),
                            1,
                            cv2.LINE_AA,
                        )
                        # INTERSECCION PUNTO DEDO
                        A = np.array(
                            [
                                [
                                    extended_point2[0] - extended_point[0],
                                    -(perp_max_x22 - perp_max_x12),
                                ],
                                [
                                    extended_point2[1] - extended_point[1],
                                    -(perp_max_y22 - perp_max_y12),
                                ],
                            ]
                        )
                        B = np.array(
                            [
                                perp_max_x12 - extended_point[0],
                                perp_max_y12 - extended_point[1],
                            ]
                        )
                        if np.linalg.det(A) != 0:
                            t, s = np.linalg.solve(A, B)
                            intersection_x = int(
                                extended_point[0]
                                + t * (extended_point2[0] - extended_point[0])
                            )
                            intersection_y = int(
                                extended_point[1]
                                + t * (extended_point2[1] - extended_point[1])
                            )
                            cv2.circle(
                                frame,
                                (intersection_x, intersection_y),
                                2,
                                (0, 255, 0),
                                -1,
                            )
                            print(
                                "Punto de intersección:",
                                (intersection_x, intersection_y),
                            )
                        # INTERSECCION PUNTO X
                        A2 = np.array(
                            [
                                [
                                    extended_point2[0] - extended_point[0],
                                    -(perp_max_x232 - x3),
                                ],
                                [
                                    extended_point2[1] - extended_point[1],
                                    -(perp_max_y232 - y3),
                                ],
                            ]
                        )
                        B2 = np.array([x3 - extended_point[0], y3 - extended_point[1]])
                        if np.linalg.det(A2) != 0:
                            t2, s = np.linalg.solve(A2, B2)
                            intersection_x2 = int(
                                extended_point[0]
                                + t2 * (extended_point2[0] - extended_point[0])
                            )
                            intersection_y2 = int(
                                extended_point[1]
                                + t2 * (extended_point2[1] - extended_point[1])
                            )
                            cv2.circle(
                                frame,
                                (intersection_x2, intersection_y2),
                                2,
                                (0, 255, 255),
                                -1,
                            )
                            print(
                                "Punto de intersección:",
                                (intersection_x2, intersection_y2),
                            )

                        m3 = pendiente(
                            perp_max_x12, perp_max_y12, perp_max_x22, perp_max_y22
                        )
                        (px3, py3), (px23, py23) = calculate_perpendicular_points(
                            x3, y3, m3, length
                        )
                        # LINEA PERPENDICULAR LEFT
                        cv2.line(
                            frame, (px3, py3), (px23, py23), (255, 0, 0), 1, cv2.LINE_AA
                        )
                        rx1, ry1 = right_top
                        distancia = np.sqrt(
                            (intersection_x - rx1) ** 2 + (intersection_y - ry1) ** 2
                        )
                        # Distancia fundamental
                        # print(f"Distancia: {distancia}")
                        mirror_x = 2 * rx1 - intersection_x
                        mirror_y = 2 * ry1 - intersection_y
                        # print(f"Punto espejo: ({mirror_x}, {mirror_y})")
                        # PUNTO ESPEJO
                        cv2.circle(
                            frame, (int(mirror_x), int(mirror_y)), 2, (0, 255, 255), -1
                        )
                        (espejo_x, espejo_y), (espejo_x1, espejo_y1) = (
                            calculate_perpendicular_points(
                                int(mirror_x), int(mirror_y), m2, length
                            )
                        )
                        # perpendicular espejo
                        cv2.line(
                            frame,
                            (mirror_x, mirror_y),
                            (espejo_x, espejo_y),
                            (255, 0, 0),
                            1,
                            cv2.LINE_AA,
                        )
                        line_point1 = (mirror_x, mirror_y)
                        line_point2 = (espejo_x, espejo_y)
                        intersections = find_intersections(
                            contour, line_point1, line_point2
                        )
                        # Filtrar los puntos de intersección que están muy cerca entre sí
                        filtered_intersections = filter_close_points(
                            intersections, min_distance=10
                        )

                        if len(filtered_intersections) >= 2:
                            inter1, inter2 = filtered_intersections[:2]
                            # Dibujar la recta entre los dos puntos de intersección
                            cv2.line(frame, inter1, inter2, (255, 0, 0), 2)
                            # Calcula la distancia euclidiana
                            distance = np.sqrt(
                                (inter1[0] - inter2[0]) ** 2
                                + (inter1[1] - inter2[1]) ** 2
                            )
                            Ycm = distance / factor
                            # print("La distancia entre los puntos es:", distance/13.3)
                            for point in filtered_intersections:
                                cv2.circle(
                                    frame, point, 2, (0, 255, 0), -1
                                )  # Dibuja un círculo verde en cada punto de intersección
                            # Calcular el punto medio
                            midpoint2 = (
                                ((inter1[0] + inter2[0]) // 2) - 20,
                                ((inter1[1] + inter2[1]) // 2) + 20,
                            )
                            # Texto y
                            text2 = "Y: {:.1f}".format(Ycm)
                            # Dibujar el texto en la imagen
                            cv2.putText(
                                frame,
                                text2,
                                midpoint2,
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.3,
                                (255, 0, 0),
                                1,
                                cv2.LINE_AA,
                            )

                        point1 = (intersection_x2, intersection_y2)
                        point2 = (x3, y3)

                        # Calcular el punto medio
                        midpoint = (
                            ((point1[0] + point2[0]) // 2) - 20,
                            ((point1[1] + point2[1]) // 2) + 20,
                        )
                        # Calcular la distancia euclidiana
                        distanceX = np.sqrt(
                            (point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2
                        )
                        Xcm = distanceX / factor
                        # Texto X
                        textx = "X: {:.1f}".format(Xcm)
                        # TIPO DE PIE
                        PIE_IZQUIERDO = ((Xcm - Ycm) / Xcm) * 100
                        izquierdo_porc = "%: {:.1f}".format(PIE_IZQUIERDO)
                        TIPO1 = categorizar_pie(PIE_IZQUIERDO)
                        print(TIPO1)
                        cv2.putText(
                            frame,
                            izquierdo_porc,
                            (200, 300),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.3,
                            (0, 0, 255),
                            1,
                            cv2.LINE_AA,
                        )
                        # Dibujar el texto en la imagen
                        cv2.putText(
                            frame,
                            textx,
                            midpoint,
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.3,
                            (255, 0, 0),
                            1,
                            cv2.LINE_AA,
                        )

                        # Dibujar círculos en los puntos extremos
                        cv2.circle(frame, right, 2, (255, 120, 0), -1)
                        cv2.circle(frame, right_top, 2, (255, 120, 0), -1)
                        cv2.circle(frame, bot1, 2, (255, 120, 0), -1)
                        cv2.circle(frame, left1, 2, (0, 0, 0), -1)
                        dibujar_rectangulo_y_texto_planta(
                            frame, contornos_izquierdo, "Izquierdo", TIPO1, (0, 0, 255)
                        )

            if len(contornos_derecho) > 0:
                for contour2 in contornos_derecho:
                    bot2, right2, right_top2, left2 = get_extreme2(contour2, 1)
                    if right2 is not None and right_top2 is not None:
                        # Asegurarse de que los puntos son tuplas con valores enteros
                        right2 = tuple(map(int, right2))
                        left2 = tuple(map(int, left2))
                        right_top2 = tuple(map(int, right_top2))
                        # Calcular el vector dirección entre right y right_top
                        vector2 = np.array(right_top2) - np.array(right2)
                        length2 = np.linalg.norm(vector2)
                        # extender linea normal
                        extended_length2 = length2 * 0.6
                        extended_length22 = length2 * 0.3
                        direction_vector2 = vector2 / length2
                        extended_point2 = tuple(
                            np.array(right_top2) + extended_length2 * direction_vector2
                        )
                        extended_point22 = tuple(
                            np.array(right2) - extended_length22 * direction_vector2
                        )
                        extended_point2 = tuple(map(int, extended_point2))
                        # LINEA NORMAL
                        cv2.line(
                            frame,
                            tuple(map(int, extended_point2)),
                            tuple(map(int, extended_point22)),
                            (255, 255, 255),
                            1,
                            cv2.LINE_AA,
                        )
                        x11, y11 = tuple(map(int, extended_point2))
                        x22, y22 = tuple(map(int, extended_point22))
                        m22 = pendiente(x11, y11, x22, y22)
                        length2 = 100
                        x33, y33 = tuple(map(int, left2))
                        x44, y44 = tuple(map(int, highest_right_point2))
                        # LINEA PERPENDICULAR DEDO
                        (perp_max_x13, perp_max_y13), (perp_max_x23, perp_max_y23) = (
                            calculate_perpendicular_points(x44, y44, m22, length2)
                        )
                        cv2.line(
                            frame,
                            (perp_max_x13, perp_max_y13),
                            (perp_max_x23, perp_max_y23),
                            (0, 0, 255),
                            1,
                            cv2.LINE_AA,
                        )
                        # LINEA PERPENDICULAR X
                        (perp_max_x133, perp_max_y133), (
                            perp_max_x233,
                            perp_max_y233,
                        ) = calculate_perpendicular_points(x33, y33, m22, length2)
                        cv2.line(
                            frame,
                            (x33, y33),
                            (perp_max_x133, perp_max_y133),
                            (0, 0, 255),
                            1,
                            cv2.LINE_AA,
                        )
                        # INTERSECCION PUNTO DEDO
                        A = np.array(
                            [
                                [
                                    extended_point22[0] - extended_point2[0],
                                    -(perp_max_x23 - perp_max_x13),
                                ],
                                [
                                    extended_point22[1] - extended_point2[1],
                                    -(perp_max_y23 - perp_max_y13),
                                ],
                            ]
                        )
                        B = np.array(
                            [
                                perp_max_x13 - extended_point2[0],
                                perp_max_y13 - extended_point2[1],
                            ]
                        )
                        if np.linalg.det(A) != 0:
                            t, s = np.linalg.solve(A, B)
                            intersection_x2 = int(
                                extended_point2[0]
                                + t * (extended_point22[0] - extended_point2[0])
                            )
                            intersection_y2 = int(
                                extended_point2[1]
                                + t * (extended_point22[1] - extended_point2[1])
                            )

                            cv2.circle(
                                frame,
                                (intersection_x2, intersection_y2),
                                2,
                                (0, 255, 0),
                                -1,
                            )
                            # print("Punto de intersección:", (intersection_x2, intersection_y2))
                        # INTERSECCION PUNTO DEDO
                        A22 = np.array(
                            [
                                [
                                    extended_point22[0] - extended_point2[0],
                                    -(perp_max_x133 - x33),
                                ],
                                [
                                    extended_point22[1] - extended_point2[1],
                                    -(perp_max_y133 - y33),
                                ],
                            ]
                        )
                        B22 = np.array(
                            [x33 - extended_point2[0], y33 - extended_point2[1]]
                        )
                        if np.linalg.det(A22) != 0:
                            t22, s = np.linalg.solve(A22, B22)
                            intersection_x22 = int(
                                extended_point2[0]
                                + t22 * (extended_point22[0] - extended_point2[0])
                            )
                            intersection_y22 = int(
                                extended_point2[1]
                                + t22 * (extended_point22[1] - extended_point2[1])
                            )
                            cv2.circle(
                                frame,
                                (intersection_x22, intersection_y22),
                                2,
                                (0, 255, 255),
                                -1,
                            )
                            # print("Punto de intersección:", (intersection_x22, intersection_y22))
                        # perpendicular LEFT
                        m33 = pendiente(
                            perp_max_x13, perp_max_y13, perp_max_x23, perp_max_y23
                        )
                        (px33, py33), (px233, py233) = calculate_perpendicular_points(
                            x33, y33, m33, length2
                        )
                        # Linea de la perpendicular left
                        cv2.line(
                            frame,
                            (px33, py33),
                            (px233, py233),
                            (0, 0, 255),
                            1,
                            cv2.LINE_AA,
                        )
                        rx2, ry2 = right_top2
                        distancia2 = np.sqrt(
                            (intersection_x2 - rx2) ** 2 + (intersection_y2 - ry2) ** 2
                        )
                        # Distancia fundamental
                        # print(f"Distancia: {distancia2}")
                        mirror_x2 = 2 * rx2 - intersection_x2
                        mirror_y2 = 2 * ry2 - intersection_y2
                        # print(f"Punto espejo: ({mirror_x2}, {mirror_y2})")
                        # Punto espejo
                        cv2.circle(
                            frame,
                            (int(mirror_x2), int(mirror_y2)),
                            2,
                            (0, 255, 255),
                            -1,
                        )
                        (espejo_x2, espejo_y2), (espejo_x12, espejo_y12) = (
                            calculate_perpendicular_points(
                                int(mirror_x2), int(mirror_y2), m22, length2
                            )
                        )
                        # Linea perpendicular espejo
                        cv2.line(
                            frame,
                            (mirror_x2, mirror_y2),
                            (espejo_x12, espejo_y12),
                            (0, 0, 255),
                            1,
                            cv2.LINE_AA,
                        )
                        # cv2.circle(frame, (espejo_x12, espejo_y12), 2, (0, 255, 255), -1)
                        line_point1 = (mirror_x2, mirror_y2)
                        line_point2 = (espejo_x12, espejo_y12)
                        intersections = find_intersections(
                            contour2, line_point1, line_point2
                        )
                        # Filtrar los puntos de intersección que están muy cerca entre sí
                        filtered_intersections = filter_close_points(
                            intersections, min_distance=10
                        )
                        # print("Intersections:", intersections)
                        # print("filtrados:", filtered_intersections)

                        if len(filtered_intersections) >= 2:
                            inter1, inter2 = filtered_intersections[:2]
                            # Dibujar la recta entre los dos puntos de intersección
                            cv2.line(frame, inter1, inter2, (255, 0, 0), 2)
                            distance2 = np.sqrt(
                                (inter1[0] - inter2[0]) ** 2
                                + (inter1[1] - inter2[1]) ** 2
                            )
                            Ycm2 = distance2 / factor

                            for point in filtered_intersections:
                                cv2.circle(
                                    frame, point, 2, (0, 255, 0), -1
                                )  # Dibuja un círculo verde en cada punto de intersección
                            # Calcular el punto medio
                            midpoint2 = (
                                ((inter1[0] + inter2[0]) // 2) - 20,
                                ((inter1[1] + inter2[1]) // 2) + 20,
                            )
                            # Texto y
                            text2 = "Y: {:.1f}".format(Ycm2)
                            # Dibujar el texto en la imagen
                            cv2.putText(
                                frame,
                                text2,
                                midpoint2,
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.3,
                                (0, 0, 255),
                                1,
                                cv2.LINE_AA,
                            )

                        # TEXTO X
                        point1 = (intersection_x22, intersection_y22)
                        point2 = (x33, y33)
                        # Calcular el punto medio
                        midpoint2 = (
                            ((point1[0] + point2[0]) // 2) - 10,
                            ((point1[1] + point2[1]) // 2) + 20,
                        )
                        distanceX2 = np.sqrt(
                            (point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2
                        )
                        Xcm2 = distanceX2 / factor
                        # Texto X
                        textx2 = "X: {:.1f}".format(Xcm2)
                        # TIPO DE PIE
                        PIE_DERECHO = ((Xcm2 - Ycm2) / Xcm2) * 100
                        PIE_DERECHO = abs(100 - PIE_DERECHO)
                        derecho_porc = "%: {:.1f}".format(PIE_DERECHO)
                        TIPO2 = categorizar_pie(PIE_DERECHO)
                        print(TIPO2)
                        cv2.putText(
                            frame,
                            derecho_porc,
                            (400, 300),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.3,
                            (0, 0, 255),
                            1,
                            cv2.LINE_AA,
                        )
                        # Dibujar el texto en la imagen
                        cv2.putText(
                            frame,
                            textx2,
                            midpoint2,
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.3,
                            (0, 0, 255),
                            1,
                            cv2.LINE_AA,
                        )
                        cv2.circle(frame, right2, 2, (255, 120, 0), -1)
                        cv2.circle(frame, right_top2, 2, (255, 120, 0), -1)
                        cv2.circle(frame, bot2, 2, (255, 120, 0), -1)
                        cv2.circle(frame, left2, 2, (0, 0, 0), -1)
                        dibujar_rectangulo_y_texto_planta(
                            frame, contornos_derecho, "Derecho", TIPO2, (255, 0, 0)
                        )

            # Combinar contornos seleccionados
            contornos_combinados_izquierdo = combinar_contornos(
                contornos_izquierdo, contornos_izquierdo2
            )
            contornos_combinados_derecho = combinar_contornos(
                contornos_derecho, contornos_derecho2
            )

            # Crear una máscara binaria de la misma dimensión que el frame
            mask = np.zeros(frame.shape[:2], dtype=np.uint8)

            # Dibujar los contornos combinados en la máscara
            cv2.drawContours(
                mask, contornos_combinados_izquierdo, -1, 255, thickness=cv2.FILLED
            )
            cv2.drawContours(
                mask, contornos_combinados_derecho, -1, 255, thickness=cv2.FILLED
            )

            # Recortar la imagen original usando la máscara
            recorte = cv2.bitwise_and(frame2, frame2, mask=mask)

            # Convertir la imagen recortada a escala de grises (opcional, si quieres pseudo color basado en escala de grises)
            recorte_gris = cv2.cvtColor(recorte, cv2.COLOR_BGR2GRAY)
            malcolocado = 0
            # Aplicar una colorización pseudo color a la imagen recortada
            pseudo_color = cv2.applyColorMap(recorte_gris, cv2.COLORMAP_HOT)
            # cv2.imshow("Imagen Pseudo Color", pseudo_color)
            # Dibujar los contornos detectados sobre el fotograma
            cv2.drawContours(
                frame, contornos_izquierdo2, -1, (255, 0, 0), 1
            )  # Contornos izquierdos en azul
            cv2.drawContours(
                frame, contornos_derecho2, -1, (0, 0, 255), 1
            )  # Contornos derechos en rojo
            # Dibujar los puntos extremos en el fotograma
            cv2.circle(frame, highest_right_point2, 4, (0, 0, 255), -1)
            cv2.circle(frame, highest_left_point2, 4, (255, 0, 0), -1)

        else:

            pass

    except Exception as e:
        TIPO1 = ""
        TIPO2 = ""
        print("COLOQUE BIEN LOS PIES:")
        malcolocado += 1
        print(malcolocado)
        # DECOMENTAR PARA QUE SUENE MAL COLOCADO
        """"
        if(malcolocado==10):
            audio_thread2 = threading.Thread(target=play_audio2)
            audio_thread2.start()        
        if malcolocado>50: 
            malcolocado=0            
        """
        print(e)

    return frame, mask


# Función para dibujar rectángulo y texto
def dibujar_rectangulo_y_texto_planta(frame, contornos, texto, tipo, color):
    if len(contornos) > 0:
        # Combinar todos los contornos en uno solo para encontrar el rectángulo envolvente
        todos_contornos = np.vstack(contornos)
        x, y, w, h = cv2.boundingRect(todos_contornos)
        # Calcular el área del rectángulo
        area_rectangulo = w * h
        # Verificar si el área del rectángulo es mayor a 1000
        if area_rectangulo > 1000 and h > 100 and w > 65:
            if w > 200:
                print("coloque bien")
            else:
                # Dibujar el rectángulo
                # cv2.rectangle(frame, (x, y), (x + w, y + h), color, 1)# rectangulo toda el area
                cv2.rectangle(
                    frame, (x + 10, y + h + 2), (x + w - 10, y + h + 40), color, -1
                )  # rectangulo texto
                # Poner el texto en el centro del rectángulo
                cv2.putText(
                    frame,
                    texto,
                    (x + 10, y + h + 15),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA,
                )
                cv2.putText(
                    frame,
                    tipo,
                    (x + 10, y + h + 35),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                    cv2.LINE_AA,
                )


# Función de callback para los trackbars (no hace nada, pero es necesaria)
def nothing(x):
    pass


# Función para mostrar el mensaje de "Sin cámara"
def mostrar_mensaje_sin_camara(self):
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.putText(
        frame,
        "Sin camara",
        (200, 240),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )
    return frame


# Crear una ventana para los controles deslizantes
cv2.namedWindow("Controles HSV", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Controles HSV", 300, 300)

# Crear los trackbars para ajustar los valores HSV
cv2.createTrackbar("Lower H", "Controles HSV", 30, 179, nothing)
cv2.createTrackbar("Lower S", "Controles HSV", 16, 255, nothing)
cv2.createTrackbar("Lower V", "Controles HSV", 103, 255, nothing)
cv2.createTrackbar("Upper H", "Controles HSV", 94, 179, nothing)
cv2.createTrackbar("Upper S", "Controles HSV", 255, 255, nothing)
cv2.createTrackbar("Upper V", "Controles HSV", 255, 255, nothing)

# Crear una ventana para los controles deslizantes
cv2.namedWindow("Controles HSV dedos", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Controles HSV dedos", 300, 300)

# Crear los trackbars para ajustar los valores HSV
cv2.createTrackbar("Lower H", "Controles HSV dedos", 40, 179, nothing)
cv2.createTrackbar("Lower S", "Controles HSV dedos", 16, 255, nothing)
cv2.createTrackbar("Lower V", "Controles HSV dedos", 87, 255, nothing)
cv2.createTrackbar("Upper H", "Controles HSV dedos", 100, 179, nothing)
cv2.createTrackbar("Upper S", "Controles HSV dedos", 255, 255, nothing)
cv2.createTrackbar("Upper V", "Controles HSV dedos", 255, 255, nothing)


# DECOMENTAR PARA QUE FUNCIONE LA IMAGEN
# Leer la imagen desde el archivo
# frame_original = cv2.imread('x6.jpg')
# DESCOMENTAR PARA FUNCIONE LA CAMARA
# cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT,1080)

h = 480
w = 640
# Crear una ventana para mostrar la cámara y el polígono
# cv2.namedWindow("COMPENSADA", cv2.WINDOW_NORMAL)  # Ajustar tamaño de ventana
# cv2.resizeWindow("COMPENSADA", w, h)  # Tamaño deseado para visualización
# Crear una ventana para mostrar la cámara y el polígono
# cv2.namedWindow("ORIGINAL", cv2.WINDOW_NORMAL)  # Ajustar tamaño de ventanaq
# cv2.resizeWindow("ORIGINAL", w, h)  # Tamaño deseado para visualización

# Cargar los parámetros de calibración guardados
cameraMatrix, dist = pickle.load(open("calibration.pkl", "rb"))


@app.route("/")
def index():
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
        db_config = {
            "user": "android",
            "password": "12345678",
            "host": "localhost",
            "database": "pies",
        }

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("usuarios.html", users=users)

    except Exception as e:
        return render_template("usuarios.html", errorbase="error")


# Ruta para manejar el envío del formulario
@app.route("/submit", methods=["POST"])
def submit():

    try:

        db_config = {
            "user": "android",
            "password": "12345678",
            "host": "localhost",
            "database": "pies",
        }

        nombre = request.form["nuevoNombre"]
        cedula = request.form["nuevoCedula"]
        telefono = request.form["nuevoTelefono"]
        estatura = request.form["nuevoEstatura"]
        edad = request.form["nuevoEdad"]
        peso = request.form["nuevoPeso"]
        genero = request.form["gender"]

        # Conectar a la base de datos y guardar los datos
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nombre,cedula,telefono,estatura,edad,peso,genero) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (nombre, cedula, telefono, estatura, edad, peso, genero),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"status": "success"})
    # return redirect("/usuarios")

    except mysql.connector.Error as err:
        return jsonify({"status": "error", "message": str(err)})


# Ruta para mostrar los datos de la base de datos
@app.route("/consulta")
def users():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("usuarios.html", users=users)


def video_stream():
    global pseudo_color
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    while True:
        success, image = cap.read()

        if success:
            frame = image
            original = frame
            # DESCOMENTAR PARA Q FUNCIONE CAMARA

            # DESCOMENTAR PARA Q FUNCIONE IMAGEN
            # frame = frame_original.copy()

            try:
                h, w = frame.shape[:2]
                # print(h,w)
                newCameraMatrix, roi = cv2.getOptimalNewCameraMatrix(
                    cameraMatrix, dist, (w, h), 1, (w, h)
                )
                # Undistort
                undistorted = cv2.undistort(
                    frame, cameraMatrix, dist, None, newCameraMatrix
                )
                # crop the image
                x, y, w, h = roi
                undistorted = undistorted[y : y + h, x : x + w]
                frame = undistorted
                frame = cv2.resize(frame, (640, 480))

                # Obtener los valores HSV actuales de los trackbars
                lower_h = cv2.getTrackbarPos("Lower H", "Controles HSV")
                lower_s = cv2.getTrackbarPos("Lower S", "Controles HSV")
                lower_v = cv2.getTrackbarPos("Lower V", "Controles HSV")
                upper_h = cv2.getTrackbarPos("Upper H", "Controles HSV")
                upper_s = cv2.getTrackbarPos("Upper S", "Controles HSV")
                upper_v = cv2.getTrackbarPos("Upper V", "Controles HSV")
                # Definir los límites de color en HSV basados en los valores de los trackbars
                lower_bound = np.array([lower_h, lower_s, lower_v])
                upper_bound = np.array([upper_h, upper_s, upper_v])

                # Obtener los valores HSV actuales de los trackbars
                lower_h2 = cv2.getTrackbarPos("Lower H", "Controles HSV dedos")
                lower_s2 = cv2.getTrackbarPos("Lower S", "Controles HSV dedos")
                lower_v2 = cv2.getTrackbarPos("Lower V", "Controles HSV dedos")
                upper_h2 = cv2.getTrackbarPos("Upper H", "Controles HSV dedos")
                upper_s2 = cv2.getTrackbarPos("Upper S", "Controles HSV dedos")
                upper_v2 = cv2.getTrackbarPos("Upper V", "Controles HSV dedos")
                # Definir los límites de color en HSV basados en los valores de los trackbars
                lower_bound2 = np.array([lower_h2, lower_s2, lower_v2])
                upper_bound2 = np.array([upper_h2, upper_s2, upper_v2])
                # Detectar y dibujar contornos en el fotograma
                planta, mask1 = detectar_contornos_planta(
                    frame, lower_bound, upper_bound, lower_bound2, upper_bound2
                )

                # cv2.imshow('Detectar mask', mask1)
                # cv2.imshow('COMPENSADA', planta)
                # cv2.imshow('ORIGINAL', original)

            # cv2.imshow('Imagen Pseudo Color', pseudo_color)
            except Exception as e:
                print("sin camara:")
                print(e)
                frame = mostrar_mensaje_sin_camara()
                # cv2.imshow('Detectar Contornos pies', frame)

                # Salir del bucle si se presiona la tecla 'q'

            # image = frame
            # image = cv2.resize(image, (640, 480))
            image = cv2.imencode(".jpg", planta)[1].tobytes()
            yield (
                b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + image + b"\r\n\r\n"
            )


@app.route("/delete_user", methods=["POST"])
def delete_user():
    data = request.get_json()
    id_usuario = data["idUsuario"]

    db_config = {
        "user": "android",
        "password": "12345678",
        "host": "localhost",
        "database": "pies",
    }

    # Conectar a la base de datos y eliminar el usuario
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM usuarios WHERE id = %s", (id_usuario,))
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Usuario eliminado correctamente"})


@app.route("/video_feed")
def video_feed():
    return Response(
        video_stream(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


if __name__ == "__main__":
    app.run(debug=True)
