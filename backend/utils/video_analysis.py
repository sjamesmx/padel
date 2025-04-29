import cv2
import numpy as np
import requests
import os

def analyze_video(url, stroke):
    # Descargar el video
    response = requests.get(url)
    video_path = f"/tmp/{stroke}.mp4"
    with open(video_path, "wb") as f:
        f.write(response.content)

    # Análisis básico con OpenCV (simulado por ahora)
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Simular métricas (en el futuro, usar MediaPipe o YOLO)
    metrics = {
        "golpeo": {stroke: np.random.uniform(50, 90)},
        "movimiento": {
            "velocidad": np.random.uniform(40, 80),
            "reaccion": np.random.uniform(50, 85),
            "cobertura": np.random.uniform(45, 90)
        },
        "tecnica": {
            "efectividad": np.random.uniform(50, 90),
            "precision": np.random.uniform(40, 85),
            "consistencia": np.random.uniform(45, 80)
        }
    }

    cap.release()
    os.remove(video_path)
    return metrics

def calculate_padel_iq(metrics):
    # Calcular puntajes promedio por categoría
    golpeo_score = sum(metric["golpeo"].values() for metric in metrics.values()) / sum(len(metric["golpeo"]) for metric in metrics.values())
    movimiento_score = sum(sum(metric["movimiento"].values()) for metric in metrics.values()) / sum(len(metric["movimiento"]) for metric in metrics.values())
    tecnica_score = sum(sum(metric["tecnica"].values()) for metric in metrics.values()) / sum(len(metric["tecnica"]) for metric in metrics.values())

    # Calcular Padel IQ (promedio ponderado)
    padel_iq = (0.4 * golpeo_score + 0.3 * movimiento_score + 0.3 * tecnica_score)

    # Clasificar en fuerza
    if padel_iq >= 85:
        fuerza = "Primera Fuerza (Profesional)"
    elif padel_iq >= 70:
        fuerza = "Segunda Fuerza (Avanzado)"
    elif padel_iq >= 55:
        fuerza = "Tercera Fuerza (Intermedio-Avanzado)"
    elif padel_iq >= 40:
        fuerza = "Cuarta Fuerza (Intermedio)"
    elif padel_iq >= 25:
        fuerza = "Quinta Fuerza (Principiante-Intermedio)"
    else:
        fuerza = "Sexta Fuerza (Principiante)"

    return padel_iq, fuerza, {
        "golpeo": {k: v for metric in metrics.values() for k, v in metric["golpeo"].items()},
        "movimiento": {k: sum(metric["movimiento"][k] for metric in metrics.values()) / len(metrics) for k in metrics[list(metrics.keys())[0]]["movimiento"]},
        "tecnica": {k: sum(metric["tecnica"][k] for metric in metrics.values()) / len(metrics) for k in metrics[list(metrics.keys())[0]]["tecnica"]}
    }