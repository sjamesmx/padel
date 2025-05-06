import logging
import cv2
import mediapipe as mp
import requests
import os
import numpy as np
import math

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar MediaPipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

def download_video(video_url, local_path):
    """Descarga el video desde la URL y lo guarda localmente."""
    try:
        response = requests.get(video_url, stream=True)
        response.raise_for_status()
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        logger.info(f"Video descargado en {local_path}")
        return True
    except Exception as e:
        logger.error(f"Error al descargar el video: {str(e)}")
        return False

def analyze_motion_with_mediapipe(video_path):
    """Analiza el video con MediaPipe para calcular métricas de movimiento."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error("No se pudo abrir el video")
        return None, None

    frame_count = 0
    speeds = []
    prev_landmarks = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)

        if results.pose_landmarks:
            landmarks = results.pose_landmarks.landmark
            wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
            current_pos = (wrist.x, wrist.y)

            if prev_landmarks:
                prev_wrist = prev_landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
                prev_pos = (prev_wrist.x, prev_wrist.y)
                distance = math.sqrt((current_pos[0] - prev_pos[0])**2 + (current_pos[1] - prev_pos[1])**2)
                speed = distance * 30
                speeds.append(speed * 10)

            prev_landmarks = landmarks

        frame_count += 1

    cap.release()

    avg_speed = sum(speeds) / len(speeds) if speeds else 0
    logger.info(f"Análisis con MediaPipe completado: promedio de velocidad del brazo {avg_speed}, frames procesados {frame_count}")
    return avg_speed, frame_count

def detect_ball_with_opencv(video_path):
    """Detecta la pelota y cuenta los golpes usando OpenCV."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error("No se pudo abrir el video")
        return 0

    shot_count = 0
    prev_frame = None
    ball_detected = False

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Detectar círculos (para la pelota) con parámetros más sensibles
        circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, dp=1.5, minDist=20,
                                   param1=30, param2=15, minRadius=2, maxRadius=8)

        current_ball_detected = circles is not None
        if current_ball_detected:
            if prev_frame is not None:
                diff = cv2.absdiff(gray, prev_frame)
                _, thresh = cv2.threshold(diff, 15, 255, cv2.THRESH_BINARY)
                motion = cv2.countNonZero(thresh)
                if motion > 1000 and not ball_detected:  # Reducir umbral para detectar más golpes
                    shot_count += 1
        ball_detected = current_ball_detected
        prev_frame = gray.copy()

    cap.release()
    logger.info(f"Detectados {shot_count} golpes con OpenCV")
    return shot_count

def analyze_video_with_mediapipe_and_opencv(video_url):
    """Analiza el video con MediaPipe y OpenCV para obtener métricas avanzadas."""
    local_path = "temp_video.mp4"
    if not download_video(video_url, local_path):
        return None, None, None

    try:
        avg_speed, frame_count = analyze_motion_with_mediapipe(local_path)
        shot_count = detect_ball_with_opencv(local_path)
        os.remove(local_path)
        return avg_speed, frame_count, shot_count
    except Exception as e:
        logger.error(f"Error al analizar video con MediaPipe/OpenCV: {str(e)}")
        return None, None, None