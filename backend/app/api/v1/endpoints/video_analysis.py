from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from app.core.config import settings
import logging
from fastapi import HTTPException as RealHTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
from app.services.analysis_manager import AnalysisManager  # Ajusta la ruta si es necesario
from firebase_admin import firestore

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar AnalysisManager
analysis_manager = AnalysisManager()

# Definir el router de FastAPI
router = APIRouter()

# Modelos para validar las solicitudes
class PadelIQRequest(BaseModel):
    user_id: str
    video_url: HttpUrl
    tipo_video: str
    player_position: dict = {"side": "left", "zone": "back"}
    game_splits: dict = None

# Modelo para la respuesta
class VideoAnalysisResponse(BaseModel):
    padel_iq: float
    metrics: dict
    error: Optional[str] = None

def get_db():
    try:
        return firestore.client()
    except ValueError as e:
        logger.error(f"Error inicializando Firestore: {str(e)}")
        raise HTTPException(status_code=500, detail="Error inicializando Firestore")

# Endpoint para subir videos
@router.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    """Sube un video para análisis."""
    raise HTTPException(status_code=501, detail="Not Implemented")

@router.get("/analysis/{video_id}")
async def get_analysis(video_id: str):
    raise HTTPException(status_code=501, detail="Not Implemented")

@router.post("/process_training_video")
async def process_training_video():
    raise HTTPException(status_code=501, detail="Not Implemented")

# Endpoint para calcular Padel IQ
@router.post("/calculate_padel_iq")
async def calculate_padel_iq(data: PadelIQRequest):
    """Procesa un video y calcula métricas de Padel IQ."""
    # Extraer datos de la solicitud
    user_id = data.user_id
    video_url = data.video_url
    tipo_video = data.tipo_video
    player_position = data.player_position
    game_splits = data.game_splits

    # Validar datos requeridos
    if not user_id or not video_url or not tipo_video:
        logger.error("Faltan datos requeridos en la solicitud")
        raise HTTPException(status_code=400, detail="Faltan datos requeridos (user_id, video_url, tipo_video)")

    logger.info(f"Procesando video para user_id: {user_id}, video_url: {video_url}, tipo_video: {tipo_video}")

    try:
        # Procesar el video según el tipo
        if tipo_video == "entrenamiento":
            logger.info("Iniciando procesamiento de video de entrenamiento")
            result = analysis_manager.procesar_video_entrenamiento(
                video_url=video_url,
                user_id=user_id,
                player_position=player_position
            )
        elif tipo_video == "juego":
            logger.info("Iniciando procesamiento de video de juego")
            result = analysis_manager.procesar_video_juego(
                video_url=video_url,
                user_id=user_id,
                player_position=player_position,
                game_splits=game_splits
            )
        else:
            logger.error("Tipo de video no soportado")
            raise HTTPException(status_code=400, detail="Tipo de video no soportado")

        metrics = result.get("metrics", {})
        padel_iq = result.get("padel_iq", 0.0)
        player_level = "Principiante" if padel_iq < 30 else "Intermedio" if padel_iq < 60 else "Avanzado"
        force_category = "quinta_fuerza"

        response = {
            "metrics": metrics,
            "force_category": force_category,
            "force_level": metrics.get("fuerza", 0),
            "padel_iq": padel_iq,
            "player_level": player_level
        }

        logger.info(f"Calculated Padel IQ for {user_id}: {padel_iq}")
        return response

    except Exception as e:
        logger.error(f"Error calculating Padel IQ: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error calculating Padel IQ: {str(e)}")

# Ejemplo de uso en un endpoint:
# @router.get("/video/firestore_test")
# async def firestore_test(db: firestore.Client = Depends(get_db)):
#     # Aquí puedes usar db para acceder a Firestore
#     return {"message": "Firestore está disponible"} 