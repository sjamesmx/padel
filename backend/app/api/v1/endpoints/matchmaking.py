from fastapi import APIRouter, HTTPException, Depends
from firebase_admin import firestore
from app.core.deps import get_current_user
from app.schemas.user import UserInDB
from typing import Optional
import uuid
import logging

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db():
    try:
        return firestore.client()
    except ValueError as e:
        logger.error(f"Error inicializando Firestore: {str(e)}")
        raise HTTPException(status_code=500, detail="Error inicializando Firestore")

# Buscar partido
@router.post("/find_match")
async def find_match(level: Optional[str] = None, position: Optional[str] = None, current_user: UserInDB = Depends(get_current_user)):
    db = get_db()
    # Simulación: crear una búsqueda de partido
    search_id = str(uuid.uuid4())
    search_data = {
        "search_id": search_id,
        "user_id": current_user.id,
        "level": level,
        "position": position,
        "status": "searching",
        "created_at": firestore.SERVER_TIMESTAMP
    }
    db.collection("match_searches").document(search_id).set(search_data)
    # Buscar partidos compatibles (simulado)
    matches = db.collection("matches").where("status", "==", "open").get()
    available_matches = [m.to_dict() for m in matches]
    return {"message": "Búsqueda iniciada", "search_id": search_id, "available_matches": available_matches}

# Cancelar búsqueda
@router.delete("/find_match")
async def cancel_find_match(current_user: UserInDB = Depends(get_current_user)):
    db = get_db()
    # Buscar búsqueda activa
    searches = db.collection("match_searches").where("user_id", "==", current_user.id).where("status", "==", "searching").get()
    for s in searches:
        db.collection("match_searches").document(s.id).update({"status": "cancelled"})
    # Notificar a los jugadores de partidos abiertos donde esté este usuario
    matches = db.collection("matches").where("status", "==", "open").get()
    for match in matches:
        match_data = match.to_dict()
        players = match_data.get("players", [])
        if current_user.id in players:
            for player_id in players:
                if player_id != current_user.id:
                    notif_id = str(uuid.uuid4())
                    db.collection("notifications").document(notif_id).set({
                        "notification_id": notif_id,
                        "user_id": player_id,
                        "type": "match_cancelled",
                        "from_user_id": current_user.id,
                        "match_id": match.id,
                        "created_at": firestore.SERVER_TIMESTAMP,
                        "read": False
                    })
            # Opcional: remover al usuario del partido
            players = [pid for pid in players if pid != current_user.id]
            db.collection("matches").document(match.id).update({"players": players})
    return {"message": "Búsqueda cancelada"}

# Obtener partidos disponibles
@router.get("/get_matches")
async def get_matches(current_user: UserInDB = Depends(get_current_user)):
    db = get_db()
    matches = db.collection("matches").where("status", "==", "open").get()
    return [m.to_dict() for m in matches]

# Aceptar partido
@router.post("/accept/{match_id}")
async def accept_match(match_id: str, current_user: UserInDB = Depends(get_current_user)):
    db = get_db()
    match = db.collection("matches").document(match_id).get()
    if not match.exists:
        raise HTTPException(status_code=404, detail="Partido no encontrado")
    match_data = match.to_dict()
    # Simulación: añadir usuario al partido
    players = match_data.get("players", [])
    if current_user.id in players:
        raise HTTPException(status_code=400, detail="Ya estás en este partido")
    players.append(current_user.id)
    db.collection("matches").document(match_id).update({"players": players})
    # Notificar a los demás jugadores que un nuevo jugador se ha unido
    for player_id in players:
        if player_id != current_user.id:
            notif_id = str(uuid.uuid4())
            db.collection("notifications").document(notif_id).set({
                "notification_id": notif_id,
                "user_id": player_id,
                "type": "match_joined",
                "from_user_id": current_user.id,
                "match_id": match_id,
                "created_at": firestore.SERVER_TIMESTAMP,
                "read": False
            })
    # Si el partido se llena (ejemplo: 4 jugadores), notificar a todos
    if len(players) == 4:
        for player_id in players:
            notif_id = str(uuid.uuid4())
            db.collection("notifications").document(notif_id).set({
                "notification_id": notif_id,
                "user_id": player_id,
                "type": "match_full",
                "match_id": match_id,
                "created_at": firestore.SERVER_TIMESTAMP,
                "read": False
            })
        db.collection("matches").document(match_id).update({"status": "full"})
    return {"message": "Te has unido al partido", "match_id": match_id, "players": players}

# Rechazar partido
@router.post("/reject/{match_id}")
async def reject_match(match_id: str, current_user: UserInDB = Depends(get_current_user)):
    db = get_db()
    match = db.collection("matches").document(match_id).get()
    if not match.exists:
        raise HTTPException(status_code=404, detail="Partido no encontrado")
    match_data = match.to_dict()
    # Simulación: marcar como rechazado para el usuario
    db.collection("matches").document(match_id).update({f"rejected_{current_user.id}": True})
    # Notificar a los demás jugadores
    players = match_data.get("players", [])
    for player_id in players:
        if player_id != current_user.id:
            notif_id = str(uuid.uuid4())
            db.collection("notifications").document(notif_id).set({
                "notification_id": notif_id,
                "user_id": player_id,
                "type": "match_rejected",
                "from_user_id": current_user.id,
                "match_id": match_id,
                "created_at": firestore.SERVER_TIMESTAMP,
                "read": False
            })
    return {"message": "Has rechazado el partido", "match_id": match_id}

# Detalles de partido
@router.get("/{match_id}")
async def get_match_details(match_id: str, current_user: UserInDB = Depends(get_current_user)):
    db = get_db()
    match = db.collection("matches").document(match_id).get()
    if not match.exists:
        raise HTTPException(status_code=404, detail="Partido no encontrado")
    return match.to_dict()

@router.get("/matches")
async def get_matches_list():
    raise HTTPException(status_code=501, detail="Not Implemented")

@router.post("/create_match")
async def create_match():
    raise HTTPException(status_code=501, detail="Not Implemented") 