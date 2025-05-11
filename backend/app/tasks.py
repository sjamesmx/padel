from celery import Celery
from app.services.analysis_manager import AnalysisManager
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurar Celery con Redis como broker y backend
celery_app = Celery(
    'padelyzer',
    broker='redis://localhost:6379/0',  # Redis local para desarrollo
    backend='redis://localhost:6379/0'
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hora de límite por tarea
    task_soft_time_limit=3300  # 55 minutos de límite suave
)

analysis_manager = AnalysisManager()

@celery_app.task
def analyze_video(user_id: str, video_url: str, tipo_video: str, player_position: dict):
    try:
        logger.info(f"Iniciando análisis asíncrono para user_id: {user_id}, video_url: {video_url}")
        # Aquí se debe reutilizar la lógica de análisis existente
        # Simulación: llamamos a analysis_manager.procesar_video_entrenamiento o procesar_video_juego
        if tipo_video == "entrenamiento":
            result = analysis_manager.procesar_video_entrenamiento(
                video_url=video_url,
                user_id=user_id,
                player_position=player_position
            )
        elif tipo_video == "juego":
            result = analysis_manager.procesar_video_juego(
                video_url=video_url,
                user_id=user_id,
                player_position=player_position,
                game_splits=None
            )
        else:
            raise ValueError("Tipo de video no soportado")
        logger.info(f"Análisis completado para user_id: {user_id}, padel_iq: {result.get('padel_iq', 0)}")
        return result
    except Exception as e:
        logger.error(f"Error en análisis asíncrono: {str(e)}")
        return {"error": str(e)} 