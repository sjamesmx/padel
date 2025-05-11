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

ONBOARDING_STEPS = [
    {"step_id": "profile", "name": "Completar perfil", "description": "Agrega tu información básica."},
    {"step_id": "preferences", "name": "Preferencias", "description": "Selecciona tus preferencias de juego."},
    {"step_id": "tutorial", "name": "Tutorial", "description": "Aprende a usar la plataforma."}
]

def get_db():
    try:
        return firestore.client()
    except ValueError as e:
        logger.error(f"Error inicializando Firestore: {str(e)}")
        raise HTTPException(status_code=500, detail="Error inicializando Firestore")

# Completar onboarding
@router.post("/")
async def complete_onboarding(current_user: UserInDB = Depends(get_current_user)):
    db = get_db()
    db.collection("onboarding").document(current_user.id).set({
        "user_id": current_user.id,
        "completed": True,
        "steps": {step["step_id"]: True for step in ONBOARDING_STEPS},
        "completed_at": firestore.SERVER_TIMESTAMP
    })
    return {"message": "Onboarding completado"}

# Estado de onboarding
@router.get("/status/{user_id}")
async def get_onboarding_status(user_id: str):
    db = get_db()
    doc = db.collection("onboarding").document(user_id).get()
    if not doc.exists:
        return {"user_id": user_id, "completed": False}
    data = doc.to_dict()
    return {"user_id": user_id, "completed": data.get("completed", False)}

# Listar pasos del onboarding
@router.get("/steps")
async def get_onboarding_steps():
    return ONBOARDING_STEPS

# Actualizar un paso específico
@router.put("/step/{step_id}")
async def update_onboarding_step(step_id: str, completed: bool, current_user: UserInDB = Depends(get_current_user)):
    db = get_db()
    doc_ref = db.collection("onboarding").document(current_user.id)
    doc = doc_ref.get()
    if not doc.exists:
        # Inicializar progreso si no existe
        steps = {step["step_id"]: False for step in ONBOARDING_STEPS}
    else:
        steps = doc.to_dict().get("steps", {step["step_id"]: False for step in ONBOARDING_STEPS})
    if step_id not in steps:
        raise HTTPException(status_code=404, detail="Paso no válido")
    steps[step_id] = completed
    # Si todos los pasos están completos, marcar onboarding como completado
    all_completed = all(steps.values())
    doc_ref.set({
        "user_id": current_user.id,
        "completed": all_completed,
        "steps": steps,
        "updated_at": firestore.SERVER_TIMESTAMP
    }, merge=True)
    return {"message": f"Paso '{step_id}' actualizado", "completed": all_completed}

# Progreso detallado
@router.get("/progress/{user_id}")
async def get_onboarding_progress(user_id: str):
    db = get_db()
    doc = db.collection("onboarding").document(user_id).get()
    if not doc.exists:
        steps = {step["step_id"]: False for step in ONBOARDING_STEPS}
        completed = False
    else:
        data = doc.to_dict()
        steps = data.get("steps", {step["step_id"]: False for step in ONBOARDING_STEPS})
        completed = data.get("completed", False)
    total = len(ONBOARDING_STEPS)
    done = sum(1 for v in steps.values() if v)
    progress = int((done / total) * 100) if total else 0
    return {
        "user_id": user_id,
        "steps": steps,
        "completed": completed,
        "progress_percent": progress
    } 