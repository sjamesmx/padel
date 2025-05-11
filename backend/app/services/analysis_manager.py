import logging
from datetime import datetime
import cv2
import numpy as np
import requests
import mediapipe as mp
from typing import Dict, Any, Tuple, List
from ..core.config import settings

logger = logging.getLogger(__name__)

class AnalysisManager:
    """Administra el análisis de videos de pádel."""
    
    def __init__(self):
        self.default_params = {
            'velocidad_umbral': 0.0001,
            'max_segment_duration': 1.5,
            'frame_skip': 12,
            'scale_factor': 0.8,
            'min_detection_confidence': 0.5,
            'min_tracking_confidence': 0.5
        }
        
        # Inicializar MediaPipe Pose
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=2,
            min_detection_confidence=self.default_params['min_detection_confidence'],
            min_tracking_confidence=self.default_params['min_tracking_confidence']
        )
        
        # Definir puntos clave para el análisis
        self.WRIST_RIGHT = self.mp_pose.PoseLandmark.RIGHT_WRIST
        self.WRIST_LEFT = self.mp_pose.PoseLandmark.LEFT_WRIST
        self.ELBOW_RIGHT = self.mp_pose.PoseLandmark.RIGHT_ELBOW
        self.ELBOW_LEFT = self.mp_pose.PoseLandmark.LEFT_ELBOW
        self.SHOULDER_RIGHT = self.mp_pose.PoseLandmark.RIGHT_SHOULDER
        self.SHOULDER_LEFT = self.mp_pose.PoseLandmark.LEFT_SHOULDER

    def _calculate_angle(self, a: Tuple[float, float], b: Tuple[float, float], c: Tuple[float, float]) -> float:
        """Calcula el ángulo entre tres puntos."""
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)
        
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0/np.pi)
        
        if angle > 180.0:
            angle = 360-angle
            
        return angle

    def _calculate_velocity(self, pos1: Tuple[float, float], pos2: Tuple[float, float], time_diff: float) -> float:
        """Calcula la velocidad entre dos puntos."""
        if time_diff == 0:
            return 0
        return np.sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2) / time_diff

    def _detect_stroke(self, landmarks, prev_landmarks, frame_time: float) -> Dict[str, Any]:
        """Detecta y clasifica un golpe basado en el movimiento."""
        if not landmarks or not prev_landmarks:
            return None

        # Obtener posiciones de muñecas
        right_wrist = (landmarks[self.WRIST_RIGHT].x, landmarks[self.WRIST_RIGHT].y)
        left_wrist = (landmarks[self.WRIST_LEFT].x, landmarks[self.WRIST_LEFT].y)
        prev_right_wrist = (prev_landmarks[self.WRIST_RIGHT].x, prev_landmarks[self.WRIST_RIGHT].y)
        prev_left_wrist = (prev_landmarks[self.WRIST_LEFT].x, prev_landmarks[self.WRIST_LEFT].y)

        # Calcular velocidades
        right_velocity = self._calculate_velocity(prev_right_wrist, right_wrist, 1/30)  # Asumiendo 30fps
        left_velocity = self._calculate_velocity(prev_left_wrist, left_wrist, 1/30)

        # Calcular ángulos
        right_elbow_angle = self._calculate_angle(
            (landmarks[self.SHOULDER_RIGHT].x, landmarks[self.SHOULDER_RIGHT].y),
            (landmarks[self.ELBOW_RIGHT].x, landmarks[self.ELBOW_RIGHT].y),
            (landmarks[self.WRIST_RIGHT].x, landmarks[self.WRIST_RIGHT].y)
        )
        
        left_elbow_angle = self._calculate_angle(
            (landmarks[self.SHOULDER_LEFT].x, landmarks[self.SHOULDER_LEFT].y),
            (landmarks[self.ELBOW_LEFT].x, landmarks[self.ELBOW_LEFT].y),
            (landmarks[self.WRIST_LEFT].x, landmarks[self.WRIST_LEFT].y)
        )

        # Detectar golpe basado en velocidad y ángulos
        is_stroke = False
        stroke_type = None
        stroke_quality = 0.0

        # Umbrales para detección
        VELOCITY_THRESHOLD = 0.11  # Ajustado +10% respecto a 0.1
        ANGLE_THRESHOLD = 90

        if right_velocity > VELOCITY_THRESHOLD and right_elbow_angle > ANGLE_THRESHOLD:
            is_stroke = True
            stroke_type = "derecha"
            stroke_quality = min(1.0, right_velocity * 2)  # Normalizar calidad
        elif left_velocity > VELOCITY_THRESHOLD and left_elbow_angle > ANGLE_THRESHOLD:
            is_stroke = True
            stroke_type = "reves"
            stroke_quality = min(1.0, left_velocity * 2)

        if is_stroke:
            return {
                'tipo': stroke_type,
                'calidad': stroke_quality,
                'max_wrist_speed': max(right_velocity, left_velocity),
                'max_elbow_angle': max(right_elbow_angle, left_elbow_angle),
                'inicio': frame_time,
                'posicion_cancha': 'fondo'  # Por ahora fijo, se puede mejorar con detección de posición
            }
        
        return None

    def _estimate_court_coverage(self, poses: list) -> float:
        """Estima la cobertura de cancha (porcentaje del ancho recorrido)."""
        positions = []
        for pose in poses:
            if pose:
                # Usar hombros y caderas para estimar el centro
                try:
                    shoulder_x = (pose[self.SHOULDER_LEFT].x + pose[self.SHOULDER_RIGHT].x) / 2
                    hip_x = (pose[23].x + pose[24].x) / 2  # 23: LEFT_HIP, 24: RIGHT_HIP
                    center_x = (shoulder_x + hip_x) / 2
                    positions.append(center_x)
                except Exception:
                    continue
        if positions:
            court_coverage = (max(positions) - min(positions)) * 100  # Porcentaje del ancho
            return round(court_coverage, 2)
        return 0.0

    def procesar_video_entrenamiento(self, video_url: str, user_id: str, player_position: Dict[str, Any] = None) -> Dict[str, Any]:
        """Procesa un video de entrenamiento."""
        try:
            # Descargar el video
            local_path = f"temp_video_{user_id}.mp4"
            response = requests.get(video_url, stream=True, timeout=10)
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=16384):
                    if chunk:
                        f.write(chunk)

            # Analizar el video
            cap = cv2.VideoCapture(local_path)
            if not cap.isOpened():
                raise ValueError("No se pudo abrir el video")

            # Obtener información del video
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            video_duration = total_frames / fps if fps > 0 else 0

            # Procesar frames
            golpes = []
            frame_count = 0
            prev_landmarks = None
            last_stroke_time = 0
            min_stroke_interval = 0.5  # Segundos mínimos entre golpes
            poses = []

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count % self.default_params['frame_skip'] == 0:
                    # Procesar frame
                    frame = cv2.resize(frame, (640, 480))
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Detectar pose
                    results = self.pose.process(frame_rgb)
                    
                    if results.pose_landmarks:
                        poses.append(results.pose_landmarks.landmark)
                        current_time = frame_count / fps
                        
                        # Detectar golpe
                        if prev_landmarks and (current_time - last_stroke_time) > min_stroke_interval:
                            stroke = self._detect_stroke(
                                results.pose_landmarks.landmark,
                                prev_landmarks.landmark,
                                current_time
                            )
                            
                            if stroke:
                                golpes.append(stroke)
                                last_stroke_time = current_time
                        
                        prev_landmarks = results.pose_landmarks

                frame_count += 1

            cap.release()

            # Calcular métricas
            total_golpes = len(golpes)
            tecnica_total = sum(g['calidad'] for g in golpes)
            tecnica = (tecnica_total / total_golpes) if total_golpes > 0 else 0
            ritmo = (total_golpes / video_duration) * 120 if video_duration > 0 else 0
            fuerza = sum(g['max_wrist_speed'] for g in golpes) / total_golpes if total_golpes > 0 else 0
            court_coverage = self._estimate_court_coverage(poses)

            # Calcular Padel IQ
            padel_iq = (tecnica * 0.4 + ritmo * 0.3 + fuerza * 0.3) * 100

            # Limpiar archivo temporal
            import os
            if os.path.exists(local_path):
                os.remove(local_path)

            return {
                "padel_iq": padel_iq,
                "metrics": {
                    "tecnica": tecnica * 100,
                    "ritmo": ritmo,
                    "fuerza": fuerza * 100,
                    "total_golpes": total_golpes,
                    "video_duration": video_duration,
                    "court_coverage": court_coverage,
                    "golpes_detallados": golpes
                }
            }

        except Exception as e:
            logger.error(f"Error al procesar video de entrenamiento: {str(e)}")
            raise

    def procesar_video_juego(self, video_url: str, user_id: str, player_position: Dict[str, Any] = None, game_splits: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Procesa un video de juego."""
        try:
            # Descargar el video
            local_path = f"temp_video_{user_id}.mp4"
            response = requests.get(video_url, stream=True, timeout=10)
            response.raise_for_status()
            
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=16384):
                    if chunk:
                        f.write(chunk)

            # Analizar el video
            cap = cv2.VideoCapture(local_path)
            if not cap.isOpened():
                raise ValueError("No se pudo abrir el video")

            # Obtener información del video
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            video_duration = total_frames / fps if fps > 0 else 0

            # Procesar frames
            golpes = []
            frame_count = 0
            prev_landmarks = None
            last_stroke_time = 0
            min_stroke_interval = 0.5  # Segundos mínimos entre golpes
            poses = []

            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count % self.default_params['frame_skip'] == 0:
                    # Procesar frame
                    frame = cv2.resize(frame, (640, 480))
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Detectar pose
                    results = self.pose.process(frame_rgb)
                    
                    if results.pose_landmarks:
                        poses.append(results.pose_landmarks.landmark)
                        current_time = frame_count / fps
                        
                        # Detectar golpe
                        if prev_landmarks and (current_time - last_stroke_time) > min_stroke_interval:
                            stroke = self._detect_stroke(
                                results.pose_landmarks.landmark,
                                prev_landmarks.landmark,
                                current_time
                            )
                            
                            if stroke:
                                # Ajustar posición según player_position
                                if player_position:
                                    stroke['posicion_cancha'] = player_position.get('zone', 'fondo')
                                golpes.append(stroke)
                                last_stroke_time = current_time
                        
                        prev_landmarks = results.pose_landmarks

                frame_count += 1

            cap.release()

            # Calcular métricas
            total_golpes = len(golpes)
            tecnica_total = sum(g['calidad'] for g in golpes)
            tecnica = (tecnica_total / total_golpes) if total_golpes > 0 else 0
            ritmo = (total_golpes / video_duration) * 120 if video_duration > 0 else 0
            fuerza = sum(g['max_wrist_speed'] for g in golpes) / total_golpes if total_golpes > 0 else 0
            court_coverage = self._estimate_court_coverage(poses)

            # Calcular Padel IQ
            padel_iq = (tecnica * 0.4 + ritmo * 0.3 + fuerza * 0.3) * 100

            # Limpiar archivo temporal
            import os
            if os.path.exists(local_path):
                os.remove(local_path)

            return {
                "padel_iq": padel_iq,
                "metrics": {
                    "tecnica": tecnica * 100,
                    "ritmo": ritmo,
                    "fuerza": fuerza * 100,
                    "total_golpes": total_golpes,
                    "video_duration": video_duration,
                    "court_coverage": court_coverage,
                    "golpes_detallados": golpes
                }
            }

        except Exception as e:
            logger.error(f"Error al procesar video de juego: {str(e)}")
            raise 