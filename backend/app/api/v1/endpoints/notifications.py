from fastapi import APIRouter, HTTPException, Depends
from firebase_admin import firestore
from app.core.deps import get_current_user
from app.schemas.user import UserInDB
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

# Listar notificaciones
@router.get("/")
async def list_notifications(current_user: UserInDB = Depends(get_current_user)):
    db = get_db()
    notifs = db.collection("notifications").where("user_id", "==", current_user.id).order_by("created_at", direction=firestore.Query.DESCENDING).limit(100).get()
    return [n.to_dict() for n in notifs]

# Marcar como leída
@router.post("/{notification_id}/read")
async def mark_notification_read(notification_id: str, current_user: UserInDB = Depends(get_current_user)):
    db = get_db()
    notif = db.collection("notifications").document(notification_id).get()
    if not notif.exists or notif.to_dict().get("user_id") != current_user.id:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    db.collection("notifications").document(notification_id).update({"read": True, "read_at": firestore.SERVER_TIMESTAMP})
    return {"message": "Notificación marcada como leída"}

# Eliminar notificación
@router.delete("/{notification_id}")
async def delete_notification(notification_id: str, current_user: UserInDB = Depends(get_current_user)):
    db = get_db()
    notif = db.collection("notifications").document(notification_id).get()
    if not notif.exists or notif.to_dict().get("user_id") != current_user.id:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    db.collection("notifications").document(notification_id).delete()
    return {"message": "Notificación eliminada"} 