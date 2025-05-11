from fastapi import APIRouter, HTTPException, Depends
from firebase_admin import firestore
from app.core.deps import get_current_user
from app.schemas.user import UserInDB
from typing import List, Optional
import uuid
from datetime import datetime
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

def get_db():
    """Obtiene la instancia de Firestore."""
    try:
        return firestore.client()
    except ValueError as e:
        logger.error(f"Error inicializando Firestore: {str(e)}")
        raise HTTPException(status_code=500, detail="Error inicializando Firestore")

@router.post("/request/{target_user_id}")
async def send_friend_request(
    target_user_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Envía una solicitud de amistad a otro usuario."""
    db = get_db()
    
    # Verificar que el usuario objetivo existe
    target_user = db.collection("users").document(target_user_id).get()
    if not target_user.exists:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Verificar que no existe una solicitud previa
    existing_request = db.collection("friend_requests").where(
        "from_user_id", "==", current_user.id
    ).where(
        "to_user_id", "==", target_user_id
    ).where(
        "status", "in", ["pending", "accepted"]
    ).get()
    
    if existing_request:
        raise HTTPException(
            status_code=400,
            detail="Ya existe una solicitud de amistad pendiente o aceptada"
        )
    
    # Crear la solicitud
    request_id = str(uuid.uuid4())
    request_data = {
        "request_id": request_id,
        "from_user_id": current_user.id,
        "to_user_id": target_user_id,
        "status": "pending",
        "created_at": firestore.SERVER_TIMESTAMP
    }
    
    db.collection("friend_requests").document(request_id).set(request_data)
    
    return {
        "message": "Solicitud de amistad enviada",
        "request_id": request_id
    }

@router.post("/accept/{request_id}")
async def accept_friend_request(
    request_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Acepta una solicitud de amistad."""
    db = get_db()
    
    # Obtener la solicitud
    request = db.collection("friend_requests").document(request_id).get()
    if not request.exists:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    
    request_data = request.to_dict()
    
    # Verificar que la solicitud es para el usuario actual
    if request_data["to_user_id"] != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="No autorizado para aceptar esta solicitud"
        )
    
    # Verificar que la solicitud está pendiente
    if request_data["status"] != "pending":
        raise HTTPException(
            status_code=400,
            detail="La solicitud ya no está pendiente"
        )
    
    # Actualizar estado de la solicitud
    db.collection("friend_requests").document(request_id).update({
        "status": "accepted",
        "accepted_at": firestore.SERVER_TIMESTAMP
    })
    
    # Crear la amistad bidireccional
    friendship_id = str(uuid.uuid4())
    friendship_data = {
        "friendship_id": friendship_id,
        "user_id_1": request_data["from_user_id"],
        "user_id_2": current_user.id,
        "created_at": firestore.SERVER_TIMESTAMP
    }
    
    db.collection("friendships").document(friendship_id).set(friendship_data)
    
    return {
        "message": "Solicitud de amistad aceptada",
        "friendship_id": friendship_id
    }

@router.post("/reject/{request_id}")
async def reject_friend_request(
    request_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Rechaza una solicitud de amistad."""
    db = get_db()
    
    # Obtener la solicitud
    request = db.collection("friend_requests").document(request_id).get()
    if not request.exists:
        raise HTTPException(status_code=404, detail="Solicitud no encontrada")
    
    request_data = request.to_dict()
    
    # Verificar que la solicitud es para el usuario actual
    if request_data["to_user_id"] != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="No autorizado para rechazar esta solicitud"
        )
    
    # Verificar que la solicitud está pendiente
    if request_data["status"] != "pending":
        raise HTTPException(
            status_code=400,
            detail="La solicitud ya no está pendiente"
        )
    
    # Actualizar estado de la solicitud
    db.collection("friend_requests").document(request_id).update({
        "status": "rejected",
        "rejected_at": firestore.SERVER_TIMESTAMP
    })
    
    return {
        "message": "Solicitud de amistad rechazada"
    }

@router.get("/list")
async def get_friends_list(
    current_user: UserInDB = Depends(get_current_user)
):
    """Obtiene la lista de amigos del usuario."""
    db = get_db()
    
    # Obtener todas las amistades del usuario
    friendships = db.collection("friendships").where(
        "user_id_1", "==", current_user.id
    ).get()
    
    friendships.extend(
        db.collection("friendships").where(
            "user_id_2", "==", current_user.id
        ).get()
    )
    
    # Obtener información de los amigos
    friends = []
    for friendship in friendships:
        friend_id = (
            friendship.get("user_id_2")
            if friendship.get("user_id_1") == current_user.id
            else friendship.get("user_id_1")
        )
        
        friend = db.collection("users").document(friend_id).get()
        if friend.exists:
            friend_data = friend.to_dict()
            friends.append({
                "user_id": friend_id,
                "username": friend_data.get("username"),
                "padel_iq": friend_data.get("padel_iq"),
                "force_category": friend_data.get("force_category"),
                "friendship_id": friendship.id,
                "friendship_date": friendship.get("created_at")
            })
    
    return {
        "friends": friends,
        "total": len(friends)
    }

@router.get("/pending")
async def get_pending_requests(
    current_user: UserInDB = Depends(get_current_user)
):
    """Obtiene las solicitudes de amistad pendientes."""
    db = get_db()
    
    # Obtener solicitudes pendientes
    requests = db.collection("friend_requests").where(
        "to_user_id", "==", current_user.id
    ).where(
        "status", "==", "pending"
    ).get()
    
    # Obtener información de los remitentes
    pending_requests = []
    for request in requests:
        request_data = request.to_dict()
        sender = db.collection("users").document(request_data["from_user_id"]).get()
        
        if sender.exists:
            sender_data = sender.to_dict()
            pending_requests.append({
                "request_id": request.id,
                "from_user": {
                    "user_id": sender.id,
                    "username": sender_data.get("username"),
                    "padel_iq": sender_data.get("padel_iq"),
                    "force_category": sender_data.get("force_category")
                },
                "created_at": request_data.get("created_at")
            })
    
    return {
        "pending_requests": pending_requests,
        "total": len(pending_requests)
    }

@router.delete("/{friendship_id}")
async def delete_friendship(
    friendship_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Elimina una amistad."""
    db = get_db()
    
    # Obtener la amistad
    friendship = db.collection("friendships").document(friendship_id).get()
    if not friendship.exists:
        raise HTTPException(status_code=404, detail="Amistad no encontrada")
    
    friendship_data = friendship.to_dict()
    
    # Verificar que el usuario es parte de la amistad
    if current_user.id not in [friendship_data["user_id_1"], friendship_data["user_id_2"]]:
        raise HTTPException(
            status_code=403,
            detail="No autorizado para eliminar esta amistad"
        )
    
    # Eliminar la amistad
    db.collection("friendships").document(friendship_id).delete()
    
    # Actualizar el estado de la solicitud de amistad si existe
    requests = db.collection("friend_requests").where(
        "from_user_id", "in", [friendship_data["user_id_1"], friendship_data["user_id_2"]]
    ).where(
        "to_user_id", "in", [friendship_data["user_id_1"], friendship_data["user_id_2"]]
    ).where(
        "status", "==", "accepted"
    ).get()
    
    for request in requests:
        db.collection("friend_requests").document(request.id).update({
            "status": "deleted",
            "deleted_at": firestore.SERVER_TIMESTAMP
        })
    
    return {
        "message": "Amistad eliminada correctamente"
    } 