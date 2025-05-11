from fastapi import APIRouter, HTTPException, Depends
from firebase_admin import firestore
from app.core.deps import get_current_user
from app.schemas.user import UserInDB
from typing import List, Dict, Optional
import uuid
import logging

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ACHIEVEMENTS = [
    {"achievement_id": "first_match", "name": "Primer partido", "description": "Juega tu primer partido."},
    {"achievement_id": "ten_matches", "name": "10 partidos", "description": "Juega 10 partidos."},
    {"achievement_id": "pro_subscription", "name": "Pro", "description": "Suscríbete al plan Pro."}
]

REWARDS = [
    {"reward_id": "free_analysis", "name": "Análisis gratis", "description": "Obtén un análisis de video gratis.", "required_achievements": ["first_match"]},
    {"reward_id": "discount_pro", "name": "Descuento Pro", "description": "Descuento en suscripción Pro.", "required_achievements": ["ten_matches"]}
]

def get_db():
    try:
        return firestore.client()
    except ValueError as e:
        logger.error(f"Error inicializando Firestore: {str(e)}")
        raise HTTPException(status_code=500, detail="Error inicializando Firestore")

# Listar logros posibles
@router.get("/achievements")
async def get_achievements():
    return ACHIEVEMENTS

# Desbloquear un logro
@router.post("/achievements/{achievement_id}/unlock")
async def unlock_achievement(achievement_id: str, current_user: UserInDB = Depends(get_current_user)):
    db = get_db()
    # Validar logro
    if achievement_id not in [a["achievement_id"] for a in ACHIEVEMENTS]:
        raise HTTPException(status_code=404, detail="Logro no válido")
    # Marcar como desbloqueado
    doc_ref = db.collection("user_achievements").document(current_user.id)
    doc = doc_ref.get()
    if not doc.exists:
        unlocked = []
    else:
        unlocked = doc.to_dict().get("achievements", [])
    if achievement_id in unlocked:
        return {"message": "Logro ya desbloqueado"}
    unlocked.append(achievement_id)
    doc_ref.set({"user_id": current_user.id, "achievements": unlocked, "updated_at": firestore.SERVER_TIMESTAMP}, merge=True)
    return {"message": "Logro desbloqueado", "achievement_id": achievement_id}

# Ver logros desbloqueados
@router.get("/achievements/{user_id}")
async def get_user_achievements(user_id: str):
    db = get_db()
    doc = db.collection("user_achievements").document(user_id).get()
    if not doc.exists:
        return {"user_id": user_id, "achievements": []}
    return {"user_id": user_id, "achievements": doc.to_dict().get("achievements", [])}

# Listar recompensas
@router.get("/rewards")
async def get_rewards():
    return REWARDS

# Canjear recompensa
@router.post("/rewards/{reward_id}/claim")
async def claim_reward(reward_id: str, current_user: UserInDB = Depends(get_current_user)):
    db = get_db()
    # Validar recompensa
    reward = next((r for r in REWARDS if r["reward_id"] == reward_id), None)
    if not reward:
        raise HTTPException(status_code=404, detail="Recompensa no válida")
    # Verificar logros requeridos
    user_achievements = db.collection("user_achievements").document(current_user.id).get().to_dict() or {}
    unlocked = user_achievements.get("achievements", [])
    if not all(a in unlocked for a in reward.get("required_achievements", [])):
        raise HTTPException(status_code=400, detail="No cumples los requisitos para esta recompensa")
    # Marcar recompensa como canjeada
    doc_ref = db.collection("user_rewards").document(current_user.id)
    doc = doc_ref.get()
    if not doc.exists:
        claimed = []
    else:
        claimed = doc.to_dict().get("rewards", [])
    if reward_id in claimed:
        return {"message": "Recompensa ya canjeada"}
    claimed.append(reward_id)
    doc_ref.set({"user_id": current_user.id, "rewards": claimed, "updated_at": firestore.SERVER_TIMESTAMP}, merge=True)
    return {"message": "Recompensa canjeada", "reward_id": reward_id}

# Progreso de gamificación
@router.get("/progress/{user_id}")
async def get_gamification_progress(user_id: str):
    db = get_db()
    achievements_doc = db.collection("user_achievements").document(user_id).get()
    rewards_doc = db.collection("user_rewards").document(user_id).get()
    achievements = achievements_doc.to_dict().get("achievements", []) if achievements_doc.exists else []
    rewards = rewards_doc.to_dict().get("rewards", []) if rewards_doc.exists else []
    total_achievements = len(ACHIEVEMENTS)
    unlocked = len(achievements)
    progress = int((unlocked / total_achievements) * 100) if total_achievements else 0
    return {
        "user_id": user_id,
        "achievements": achievements,
        "rewards": rewards,
        "progress_percent": progress
    } 