import logging
import cv2
import numpy as np
import requests
import os
import mediapipe as mp

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar MediaPipe
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

def segmentar_video(ruta_video):
    """Segmenta el video en partes donde ocurren los golpes usando MediaPipe."""
    logger.info(f"Segmentando video: {ruta_video}")
    cap = cv2.VideoCapture(ruta_video)
    if not cap.isOpened():
        logger.error("No se pudo abrir el video")
        raise ValueError("No se pudo abrir el video")

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30  # Valor por defecto si no se puede determinar

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_duration = total_frames / fps
    logger.info(f"Duración del video: {video_duration} segundos")

    prev_wrist_right_pos = None
    prev_wrist_left_pos = None
    prev_elbow_pos = None
    prev_shoulder_pos = None
    segmentos = []
    inicio = None
    velocidad_umbral = 0.20  # Umbral para detectar los 11 golpes reales
    angle_change_umbral = 4  # Umbral de cambio de ángulo
    tiempo_minimo_entre_segmentos = 2.0  # Tiempo mínimo en segundos entre golpes
    ultimo_segmento_fin = -tiempo_minimo_entre_segmentos
    frame_count = 0
    movimiento_detectado = False
    lanzamiento_detectado = False
    lanzamiento_time = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Reducir resolución para optimizar
        frame = cv2.resize(frame, (640, 480))
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)

        if results.pose_landmarks:
            wrist_right = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
            wrist_left = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]
            elbow = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW]
            shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            current_wrist_right_pos = (wrist_right.x, wrist_right.y)
            current_wrist_left_pos = (wrist_left.x, wrist_left.y)
            current_elbow_pos = (elbow.x, elbow.y)
            current_shoulder_pos = (shoulder.x, shoulder.y)

            if prev_wrist_right_pos is not None and prev_wrist_left_pos is not None and prev_elbow_pos is not None and prev_shoulder_pos is not None:
                # Calcular velocidad de la muñeca derecha (golpe)
                distance_right = np.sqrt((current_wrist_right_pos[0] - prev_wrist_right_pos[0])**2 + (current_wrist_right_pos[1] - prev_wrist_right_pos[1])**2)
                velocidad_right = distance_right * fps

                # Calcular velocidad de la muñeca izquierda (lanzamiento)
                distance_left = np.sqrt((current_wrist_left_pos[0] - prev_wrist_left_pos[0])**2 + (current_wrist_left_pos[1] - prev_wrist_left_pos[1])**2)
                velocidad_left = distance_left * fps
                # Detectar movimiento ascendente de la muñeca izquierda (lanzamiento de la pelota)
                dy_left = prev_wrist_left_pos[1] - current_wrist_left_pos[1]  # Movimiento ascendente si dy_left > 0
                if dy_left > 0.1 and velocidad_left > 0.8:  # Umbrales ajustados para reducir falsos positivos
                    lanzamiento_detectado = True
                    lanzamiento_time = frame_count / fps
                    logger.debug(f"Lanzamiento detectado en t={lanzamiento_time}, dy_left={dy_left}, velocidad_left={velocidad_left}")

                # Calcular cambio de ángulo del brazo (muñeca derecha)
                vector_wrist = np.array([current_wrist_right_pos[0] - current_elbow_pos[0], current_wrist_right_pos[1] - current_elbow_pos[1]])
                vector_prev_wrist = np.array([prev_wrist_right_pos[0] - prev_elbow_pos[0], prev_wrist_right_pos[1] - prev_elbow_pos[1]])
                dot_product = np.dot(vector_wrist, vector_prev_wrist)
                norm1 = np.linalg.norm(vector_wrist)
                norm2 = np.linalg.norm(vector_prev_wrist)
                if norm1 > 0 and norm2 > 0:
                    cos_angle = dot_product / (norm1 * norm2)
                    cos_angle = np.clip(cos_angle, -1.0, 1.0)
                    angle_change = np.degrees(np.arccos(cos_angle))

                    current_time = frame_count / fps
                    if velocidad_right > velocidad_umbral and angle_change > angle_change_umbral and not movimiento_detectado and (current_time - ultimo_segmento_fin) > tiempo_minimo_entre_segmentos:
                        # Inicio de un segmento (golpe detectado)
                        inicio = frame_count / fps
                        movimiento_detectado = True
                        # Pasar información sobre el lanzamiento detectado al segmento
                        segmentos.append({'inicio': inicio, 'fin': None, 'lanzamiento_detectado': lanzamiento_detectado, 'lanzamiento_time': lanzamiento_time})
                    elif velocidad_right < velocidad_umbral / 2 and movimiento_detectado:
                        # Fin de un segmento
                        fin = frame_count / fps
                        segmentos[-1]['fin'] = fin
                        movimiento_detectado = False
                        ultimo_segmento_fin = fin
                        inicio = None
                        lanzamiento_detectado = False  # Reiniciar para el próximo segmento
                        lanzamiento_time = None

            prev_wrist_right_pos = current_wrist_right_pos
            prev_wrist_left_pos = current_wrist_left_pos
            prev_elbow_pos = current_elbow_pos
            prev_shoulder_pos = current_shoulder_pos
        else:
            prev_wrist_right_pos = None
            prev_wrist_left_pos = None
            prev_elbow_pos = None
            prev_shoulder_pos = None

        frame_count += 1

    # Si hay un segmento abierto al final del video, cerrarlo
    if movimiento_detectado and inicio is not None:
        fin = frame_count / fps
        segmentos[-1]['fin'] = fin

    logger.info(f"Segmentos detectados: {len(segmentos)}")
    return segmentos, video_duration

def analizar_segmento(segmento, ruta_video):
    """Analiza un segmento específico para detectar y clasificar golpes."""
    logger.info(f"Analizando segmento: {segmento}")
    cap = cv2.VideoCapture(ruta_video)
    if not cap.isOpened():
        logger.error("No se pudo abrir el video")
        return []

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30

    inicio_frame = int(segmento['inicio'] * fps)
    fin_frame = int(segmento['fin'] * fps)

    # Mover el video al frame inicial
    cap.set(cv2.CAP_PROP_POS_FRAMES, inicio_frame)
    prev_wrist_pos = None
    prev_elbow_pos = None
    prev_shoulder_pos = None
    prev_hip_pos = None
    max_velocidad = 0
    movimiento_direccion = None
    max_elbow_angle = 0
    wrist_height = 0

    frame_count = inicio_frame
    while cap.isOpened() and frame_count <= fin_frame:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (640, 480))
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(frame_rgb)

        if results.pose_landmarks:
            wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
            elbow = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW]
            shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]

            current_wrist_pos = (wrist.x, wrist.y)
            current_elbow_pos = (elbow.x, elbow.y)
            current_shoulder_pos = (shoulder.x, shoulder.y)
            current_hip_pos = (hip.x, hip.y)

            # Calcular ángulo del codo
            vector1 = np.array([elbow.x - shoulder.x, elbow.y - shoulder.y])
            vector2 = np.array([wrist.x - elbow.x, wrist.y - elbow.y])
            dot_product = np.dot(vector1, vector2)
            norm1 = np.linalg.norm(vector1)
            norm2 = np.linalg.norm(vector2)
            if norm1 > 0 and norm2 > 0:
                cos_angle = dot_product / (norm1 * norm2)
                cos_angle = np.clip(cos_angle, -1.0, 1.0)
                angle_rad = np.arccos(cos_angle)
                angle_deg = np.degrees(angle_rad)
                if angle_deg > max_elbow_angle:
                    max_elbow_angle = angle_deg

            # Actualizar altura de la muñeca (para detectar globos, smashes, etc.)
            if wrist.y > wrist_height:
                wrist_height = wrist.y

            if prev_wrist_pos is not None and prev_elbow_pos is not None and prev_shoulder_pos is not None:
                distance = np.sqrt((current_wrist_pos[0] - prev_wrist_pos[0])**2 + (current_wrist_pos[1] - prev_wrist_pos[1])**2)
                velocidad = distance * fps

                # Determinar dirección del movimiento usando solo dx
                dx = current_wrist_pos[0] - prev_wrist_pos[0]
                is_derecha = dx > 0

                # Clasificar el tipo de golpe
                # Prioridad 1: Saque (lanzamiento de la pelota detectado)
                if segmento.get('lanzamiento_detectado', False) and (segmento['inicio'] - segmento.get('lanzamiento_time', float('inf')) < 1.0):
                    movimiento_direccion = "saque"
                # Prioridad 2: Smash (ángulo alto, velocidad alta)
                elif max_elbow_angle > 150 and velocidad > 1.5:
                    movimiento_direccion = "smash"
                # Prioridad 3: Bandeja (ángulo alto, velocidad moderada)
                elif max_elbow_angle > 120 and velocidad > 0.8:
                    movimiento_direccion = "bandeja"
                # Prioridad 4: Globo (ángulo abierto, velocidad baja)
                elif max_elbow_angle > 120 and velocidad < 1.5:
                    movimiento_direccion = "globo"
                # Prioridad 5: Defensivo (ángulo bajo, velocidad baja)
                elif max_elbow_angle < 90 and velocidad < 0.3:
                    movimiento_direccion = "defensivo"
                # Prioridad 6: Volea (ángulo cerrado, velocidad moderada)
                elif max_elbow_angle < 90 and velocidad > 0.1:
                    movimiento_direccion = "volea_" + ("derecha" if is_derecha else "reves")
                # Prioridad 7: Derecha o Revés (ángulo 90-150, velocidad moderada-alta)
                else:
                    movimiento_direccion = "derecha" if is_derecha else "reves"

                if velocidad > max_velocidad:
                    max_velocidad = velocidad

            prev_wrist_pos = current_wrist_pos
            prev_elbow_pos = current_elbow_pos
            prev_shoulder_pos = current_shoulder_pos
            prev_hip_pos = current_hip_pos
        else:
            prev_wrist_pos = None
            prev_elbow_pos = None
            prev_shoulder_pos = None
            prev_hip_pos = None

        frame_count += 1

    cap.release()

    if max_velocidad > 0.25 and movimiento_direccion:  # Ajustar umbral mínimo
        calidad = min(100, max_velocidad * 5)
        return [{
            'tipo': movimiento_direccion,
            'confianza': calidad / 100,
            'calidad': calidad,
            'max_elbow_angle': max_elbow_angle,
            'max_wrist_speed': max_velocidad,
            'inicio': segmento['inicio']
        }]
    else:
        logger.warning("No se detectaron golpes significativos en el segmento (velocidad insuficiente).")
        return []

def evaluar_calidad(golpes):
    """Evalúa la calidad de los golpes basándose en la confianza."""
    for golpe in golpes:
        golpe['calidad'] = golpe['confianza'] * 100  # Ya calculado en analizar_segmento
    return golpes

def clasificar_golpes(golpes):
    """Clasifica los golpes por tipo."""
    clasificacion = {}
    for golpe in golpes:
        tipo = golpe['tipo']
        if tipo not in clasificacion:
            clasificacion[tipo] = []
        clasificacion[tipo].append({
            'calidad': golpe['calidad'],
            'confianza': golpe['confianza'],
            'max_elbow_angle': golpe['max_elbow_angle'],
            'max_wrist_speed': golpe['max_wrist_speed'],
            'inicio': golpe['inicio']
        })
    return clasificacion

def procesar_video_entrenamiento(video_url, client=None):
    """Procesa un video de entrenamiento completo."""
    # Descargar el video desde la URL
    local_path = "temp_video_entrenamiento.mp4"
    logger.info(f"Descargando video desde {video_url} a {local_path}")
    response = requests.get(video_url, stream=True)
    response.raise_for_status()
    with open(local_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

    try:
        # Paso 1: Segmentación
        segmentos, video_duration = segmentar_video(local_path)

        # Paso 2 y 3: Análisis y evaluación de calidad
        golpes_totales = []
        for segmento in segmentos:
            golpes = analizar_segmento(segmento, local_path)
            golpes_evaluados = evaluar_calidad(golpes)
            golpes_totales.extend(golpes_evaluados)

        # Paso 4: Clasificación
        golpes_clasificados = clasificar_golpes(golpes_totales)

        # Limpiar archivo temporal
        os.remove(local_path)
        logger.info(f"Archivo temporal {local_path} eliminado")

        return golpes_clasificados, video_duration

    except Exception as e:
        logger.error(f"Error al procesar video de entrenamiento: {str(e)}")
        if os.path.exists(local_path):
            os.remove(local_path)
        raise e