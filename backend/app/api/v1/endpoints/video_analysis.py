from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from app.core.config import settings
import logging
from fastapi import HTTPException as RealHTTPException
from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
from app.services.analysis_manager import AnalysisManager  # Ajusta la ruta si es necesario
from firebase_admin import firestore
from app.core.deps import get_current_user
from app.schemas.user import UserInDB
import uuid

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

# Constantes para validación
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB
MAX_VIDEO_DURATION = 3600  # 1 hora
ALLOWED_VIDEO_TYPES = ["video/mp4", "video/quicktime", "video/x-msvideo"]

# Endpoint para subir videos
@router.post("/upload")
async def upload_video(file: UploadFile = File(...), current_user: UserInDB = Depends(get_current_user)):
    """Sube un video para análisis con validaciones."""
    # Validar tipo de archivo
    if file.content_type not in ALLOWED_VIDEO_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no soportado. Tipos permitidos: {', '.join(ALLOWED_VIDEO_TYPES)}"
        )

    # Validar tamaño
    file_size = 0
    chunk_size = 1024 * 1024  # 1MB
    while chunk := await file.read(chunk_size):
        file_size += len(chunk)
        if file_size > MAX_VIDEO_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"El archivo excede el tamaño máximo permitido de {MAX_VIDEO_SIZE/1024/1024}MB"
            )
    await file.seek(0)

    # Validar duración (simulado)
    # En producción, esto debería usar ffprobe o similar
    video_duration = 0  # Simulado
    if video_duration > MAX_VIDEO_DURATION:
        raise HTTPException(
            status_code=400,
            detail=f"El video excede la duración máxima permitida de {MAX_VIDEO_DURATION/60} minutos"
        )

    # Procesar subida
    db = get_db()
    video_id = str(uuid.uuid4())
    video_url = f"https://storage.padzr.com/videos/{video_id}.mp4"
    
    # Guardar metadata con estado inicial
    video_doc = {
        "user_id": current_user.id,
        "filename": file.filename,
        "content_type": file.content_type,
        "video_url": video_url,
        "size_bytes": file_size,
        "duration_seconds": video_duration,
        "status": "uploaded",
        "uploaded_at": firestore.SERVER_TIMESTAMP,
        "analysis_status": "pending"
    }
    
    db.collection("videos").document(video_id).set(video_doc)
    
    return {
        "video_id": video_id,
        "video_url": video_url,
        "status": "uploaded",
        "message": "Video subido correctamente. El análisis comenzará pronto."
    }

@router.get("/analysis/history")
async def get_analysis_history(current_user: UserInDB = Depends(get_current_user)):
    """Devuelve el histórico de análisis del usuario autenticado."""
    db = get_db()
    analyses = db.collection("video_analysis").where("user_id", "==", current_user.id).order_by("created_at", direction=firestore.Query.DESCENDING).get()
    return [a.to_dict() for a in analyses]

@router.get("/analysis/{video_id}")
async def get_analysis(video_id: str, current_user: UserInDB = Depends(get_current_user)):
    """Devuelve el detalle de un análisis específico."""
    db = get_db()
    doc = db.collection("video_analysis").document(video_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")
    analysis = doc.to_dict()
    if analysis.get("user_id") != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado para ver este análisis")
    return analysis

@router.get("/analysis/compare")
async def compare_analyses(video_id_1: str, video_id_2: str, current_user: UserInDB = Depends(get_current_user)):
    """Compara métricas entre dos análisis de video."""
    db = get_db()
    doc1 = db.collection("video_analysis").document(video_id_1).get()
    doc2 = db.collection("video_analysis").document(video_id_2).get()
    if not doc1.exists or not doc2.exists:
        raise HTTPException(status_code=404, detail="Uno o ambos análisis no encontrados")
    a1, a2 = doc1.to_dict(), doc2.to_dict()
    if a1.get("user_id") != current_user.id or a2.get("user_id") != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado para comparar estos análisis")
    # Comparar métricas clave
    comparison = {k: {"video_1": a1["metrics"].get(k), "video_2": a2["metrics"].get(k)} for k in set(a1["metrics"]).union(a2["metrics"])}
    return {"video_1": video_id_1, "video_2": video_id_2, "comparison": comparison}

@router.get("/analysis/recommendations")
async def get_recommendations(video_id: str, current_user: UserInDB = Depends(get_current_user)):
    """Ofrece recomendaciones personalizadas basadas en el análisis de un video."""
    db = get_db()
    doc = db.collection("video_analysis").document(video_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Análisis no encontrado")
    analysis = doc.to_dict()
    if analysis.get("user_id") != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado para ver este análisis")
    metrics = analysis.get("metrics", {})
    recs = []
    if metrics.get("tecnica", 0) < 60:
        recs.append("Mejora tu técnica con ejercicios de control de pala.")
    if metrics.get("ritmo", 0) < 50:
        recs.append("Trabaja en tu ritmo de juego con sesiones de intervalos.")
    if metrics.get("fuerza", 0) < 50:
        recs.append("Aumenta tu fuerza con ejercicios de muñeca y antebrazo.")
    if metrics.get("court_coverage", 0) < 0.5:
        recs.append("Mejora tu cobertura de pista con drills de desplazamiento.")
    if not recs:
        recs.append("¡Excelente desempeño! Sigue así para mantener tu nivel.")
    return {"video_id": video_id, "recommendations": recs}

@router.post("/process_training_video")
async def process_training_video():
    raise HTTPException(status_code=501, detail="Not Implemented")

def determine_force_category(padel_iq: float, tecnica: float, ritmo: float, fuerza: float) -> str:
    """Determina la categoría de fuerza del jugador basada en sus métricas."""
    # Primera fuerza: Padel IQ > 85 y todas las métricas > 80
    if padel_iq > 85 and tecnica > 80 and ritmo > 80 and fuerza > 80:
        return "primera_fuerza"
    # Segunda fuerza: Padel IQ > 75 y todas las métricas > 70
    elif padel_iq > 75 and tecnica > 70 and ritmo > 70 and fuerza > 70:
        return "segunda_fuerza"
    # Tercera fuerza: Padel IQ > 65 y todas las métricas > 60
    elif padel_iq > 65 and tecnica > 60 and ritmo > 60 and fuerza > 60:
        return "tercera_fuerza"
    # Cuarta fuerza: Padel IQ > 45 y todas las métricas > 40
    elif padel_iq > 45 and tecnica > 40 and ritmo > 40 and fuerza > 40:
        return "cuarta_fuerza"
    # Quinta fuerza: resto de jugadores
    else:
        return "quinta_fuerza"

@router.get("/analysis/status/{video_id}")
async def get_analysis_status(video_id: str, current_user: UserInDB = Depends(get_current_user)):
    """Consulta el estado actual del análisis de un video."""
    db = get_db()
    doc = db.collection("videos").document(video_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Video no encontrado")
    
    video_data = doc.to_dict()
    if video_data.get("user_id") != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado para ver este video")
    
    return {
        "video_id": video_id,
        "status": video_data.get("status", "unknown"),
        "analysis_status": video_data.get("analysis_status", "unknown"),
        "progress": video_data.get("analysis_progress", 0),
        "error": video_data.get("analysis_error"),
        "created_at": video_data.get("uploaded_at"),
        "completed_at": video_data.get("analysis_completed_at")
    }

@router.post("/calculate_padel_iq")
async def calculate_padel_iq(data: PadelIQRequest, current_user: UserInDB = Depends(get_current_user)):
    """Procesa un video y calcula métricas de Padel IQ. Guarda el análisis en Firestore."""
    # Extraer datos de la solicitud
    user_id = current_user.id
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
        # Actualizar estado del video
        db = get_db()
        video_id = str(uuid.uuid4())
        db.collection("videos").document(video_id).update({
            "analysis_status": "processing",
            "analysis_progress": 0,
            "analysis_started_at": firestore.SERVER_TIMESTAMP
        })

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
            db.collection("videos").document(video_id).update({
                "analysis_status": "error",
                "analysis_error": "Tipo de video no soportado"
            })
            raise HTTPException(status_code=400, detail="Tipo de video no soportado")

        metrics = result.get("metrics", {})
        padel_iq = result.get("padel_iq", 0.0)
        player_level = "Principiante" if padel_iq < 30 else "Intermedio" if padel_iq < 60 else "Avanzado"
        force_category = determine_force_category(
            padel_iq,
            metrics.get("tecnica", 0),
            metrics.get("ritmo", 0),
            metrics.get("fuerza", 0)
        )

        # Calcular métricas adicionales
        consistency_score = calculate_consistency_score(metrics)
        movement_patterns = analyze_movement_patterns(metrics)
        stroke_effectiveness = calculate_stroke_effectiveness(metrics)

        response = {
            "metrics": {
                **metrics,
                "consistency_score": consistency_score,
                "movement_patterns": movement_patterns,
                "stroke_effectiveness": stroke_effectiveness
            },
            "force_category": force_category,
            "force_level": metrics.get("fuerza", 0),
            "padel_iq": padel_iq,
            "player_level": player_level
        }

        # Guardar el análisis en Firestore
        analysis_doc = {
            "video_id": video_id,
            "user_id": user_id,
            "video_url": str(video_url),
            "tipo_video": tipo_video,
            "metrics": response["metrics"],
            "padel_iq": padel_iq,
            "player_level": player_level,
            "force_category": force_category,
            "force_level": metrics.get("fuerza", 0),
            "created_at": firestore.SERVER_TIMESTAMP,
            "analysis_status": "completed",
            "analysis_completed_at": firestore.SERVER_TIMESTAMP
        }
        db.collection("video_analysis").document(video_id).set(analysis_doc)
        
        # Actualizar estado del video
        db.collection("videos").document(video_id).update({
            "analysis_status": "completed",
            "analysis_progress": 100,
            "analysis_completed_at": firestore.SERVER_TIMESTAMP
        })

        logger.info(f"Análisis guardado en Firestore con video_id: {video_id}")
        response["video_id"] = video_id
        return response

    except Exception as e:
        logger.error(f"Error calculating Padel IQ: {str(e)}")
        # Actualizar estado del video con el error
        db.collection("videos").document(video_id).update({
            "analysis_status": "error",
            "analysis_error": str(e),
            "analysis_completed_at": firestore.SERVER_TIMESTAMP
        })
        raise HTTPException(status_code=500, detail=f"Error calculating Padel IQ: {str(e)}")

def calculate_consistency_score(metrics: dict) -> float:
    """Calcula un score de consistencia basado en la variabilidad de las métricas."""
    # Implementación simulada
    return 75.0

def analyze_movement_patterns(metrics: dict) -> dict:
    """Analiza patrones de movimiento del jugador."""
    # Implementación simulada
    return {
        "court_coverage": metrics.get("court_coverage", 0),
        "movement_efficiency": 0.8,
        "recovery_speed": 0.7
    }

def calculate_stroke_effectiveness(metrics: dict) -> dict:
    """Calcula la efectividad por tipo de golpe."""
    # Implementación simulada
    return {
        "derecha": 0.8,
        "reves": 0.7,
        "volea": 0.75,
        "smash": 0.85
    }

# Ejemplo de uso en un endpoint:
# @router.get("/video/firestore_test")
# async def firestore_test(db: firestore.Client = Depends(get_db)):
#     # Aquí puedes usar db para acceder a Firestore
#     return {"message": "Firestore está disponible"} 