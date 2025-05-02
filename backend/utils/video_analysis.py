import cv2
import numpy as np
import requests
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_video(url, stroke):
    try:
        # Validar la URL
        if not url.startswith("http://") and not url.startswith("https://"):
            raise ValueError("Invalid URL: Must start with http:// or https://")

        logger.info(f"Downloading video for {stroke} from {url}")
        # Descargar el video con un timeout más corto
        response = requests.get(url, timeout=5, stream=True)
        response.raise_for_status()  # Lanza una excepción si la solicitud falla

        video_path = f"/tmp/{stroke}.mp4"
        with open(video_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # Filtra chunks vacíos
                    f.write(chunk)

        logger.info(f"Processing video for {stroke}")
        # Validación básica del video (simulación de detección de movimientos)
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("Could not open video file")

        # Verificar duración del video
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps == 0 or frame_count == 0:
            raise ValueError("Invalid video: Could not determine duration or frame rate")

        duration = frame_count / fps
        if duration < 3:  # Suponemos que un video de pádel debe durar al menos 3 segundos
            raise ValueError("Video too short: No detectable paddle movements")

        # Simulación de validación de movimientos (reemplazar con MediaPipe más adelante)
        if "URL_" in url:
            raise ValueError("No detectable paddle movements in the provided video sample")

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
        logger.info(f"Finished processing video for {stroke}")
        return metrics
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to download video: {str(e)}")
    except Exception as e:
        raise Exception(f"Error processing video: {str(e)}")