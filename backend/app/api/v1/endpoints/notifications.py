from fastapi import APIRouter, HTTPException, Depends, status, Query
from firebase_admin import firestore, messaging
from app.core.deps import get_current_user
from app.schemas.user import UserInDB
from typing import Optional, List, Dict
from datetime import datetime
import uuid
import logging
from pydantic import BaseModel

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PushNotification(BaseModel):
    title: str
    body: str
    data: Optional[Dict] = None
    image: Optional[str] = None

def get_db():
    try:
        return firestore.client()
    except ValueError as e:
        logger.error(f"Error inicializando Firestore: {str(e)}")
        raise HTTPException(status_code=500, detail="Error inicializando Firestore")

@router.get("/", response_model=List[Dict], summary="Listar notificaciones", tags=["notifications"])
async def list_notifications(
    current_user: UserInDB = Depends(get_current_user),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    unread_only: bool = Query(False, description="Filtrar solo notificaciones no leídas")
):
    """
    Lista las notificaciones del usuario.
    - Soporta paginación.
    - Permite filtrar por estado de lectura.
    """
    try:
        db = get_db()
        query = db.collection("notifications").where("user_id", "==", current_user.id)
        
        if unread_only:
            query = query.where("read", "==", False)
            
        query = query.order_by("created_at", direction=firestore.Query.DESCENDING)
        
        # Aplicar paginación
        notifications = query.limit(limit).offset(offset).get()
        
        return [n.to_dict() for n in notifications]
        
    except Exception as e:
        logger.error(f"Error al listar notificaciones: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al listar notificaciones"
        )

@router.post("/{notification_id}/read", response_model=dict, summary="Marcar notificación como leída", tags=["notifications"])
async def mark_notification_read(
    notification_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Marca una notificación como leída.
    - Verifica la propiedad de la notificación.
    - Actualiza el estado y la fecha de lectura.
    """
    try:
        db = get_db()
        notif = db.collection("notifications").document(notification_id).get()
        
        if not notif.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notificación no encontrada"
            )
            
        notif_data = notif.to_dict()
        if notif_data.get("user_id") != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para marcar esta notificación"
            )
            
        db.collection("notifications").document(notification_id).update({
            "read": True,
            "read_at": datetime.now()
        })
        
        return {"message": "Notificación marcada como leída"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al marcar notificación como leída: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al marcar notificación como leída"
        )

@router.delete("/{notification_id}", response_model=dict, summary="Eliminar notificación", tags=["notifications"])
async def delete_notification(
    notification_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Elimina una notificación.
    - Verifica la propiedad de la notificación.
    - Elimina la notificación de la base de datos.
    """
    try:
        db = get_db()
        notif = db.collection("notifications").document(notification_id).get()
        
        if not notif.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notificación no encontrada"
            )
            
        notif_data = notif.to_dict()
        if notif_data.get("user_id") != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para eliminar esta notificación"
            )
            
        db.collection("notifications").document(notification_id).delete()
        
        return {"message": "Notificación eliminada"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al eliminar notificación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar notificación"
        )

@router.post("/send-push", response_model=dict, summary="Enviar notificación push", tags=["notifications"])
async def send_push_notification(
    user_id: str,
    notification: PushNotification,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Envía una notificación push a un usuario.
    - Verifica que el usuario tenga un token de dispositivo.
    - Envía la notificación a través de Firebase Cloud Messaging.
    - Guarda la notificación en la base de datos.
    """
    try:
        db = get_db()
        
        # Verificar token de dispositivo
        user_doc = db.collection("users").document(user_id).get()
        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
            
        user_data = user_doc.to_dict()
        device_token = user_data.get("device_token")
        
        if not device_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario no tiene un token de dispositivo registrado"
            )
            
        # Crear mensaje
        message = messaging.Message(
            notification=messaging.Notification(
                title=notification.title,
                body=notification.body,
                image=notification.image
            ),
            data=notification.data or {},
            token=device_token
        )
        
        # Enviar notificación
        response = messaging.send(message)
        
        # Guardar en base de datos
        notification_id = str(uuid.uuid4())
        notification_data = {
            "notification_id": notification_id,
            "user_id": user_id,
            "type": "push",
            "title": notification.title,
            "body": notification.body,
            "data": notification.data,
            "image": notification.image,
            "created_at": datetime.now(),
            "read": False,
            "push_id": response
        }
        
        db.collection("notifications").document(notification_id).set(notification_data)
        
        return {
            "message": "Notificación push enviada",
            "notification_id": notification_id,
            "push_id": response
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al enviar notificación push: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al enviar notificación push"
        )

@router.post("/send-email", response_model=dict, summary="Enviar notificación por email", tags=["notifications"])
async def send_email_notification(
    user_id: str,
    subject: str = Query(..., description="Asunto del email"),
    body: str = Query(..., description="Contenido del email"),
    template: Optional[str] = Query(None, description="Plantilla de email a usar"),
    data: Optional[Dict] = None,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Envía una notificación por email a un usuario.
    - Verifica que el usuario tenga un email válido.
    - Envía el email usando el servicio de email.
    - Guarda la notificación en la base de datos.
    """
    try:
        db = get_db()
        
        # Verificar usuario
        user_doc = db.collection("users").document(user_id).get()
        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado"
            )
            
        user_data = user_doc.to_dict()
        email = user_data.get("email")
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario no tiene un email registrado"
            )
            
        # TODO: Implementar envío de email usando el servicio de email
        # Por ahora solo simulamos el envío
        
        # Guardar en base de datos
        notification_id = str(uuid.uuid4())
        notification_data = {
            "notification_id": notification_id,
            "user_id": user_id,
            "type": "email",
            "title": subject,
            "body": body,
            "template": template,
            "data": data,
            "created_at": datetime.now(),
            "read": False
        }
        
        db.collection("notifications").document(notification_id).set(notification_data)
        
        return {
            "message": "Notificación por email enviada",
            "notification_id": notification_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al enviar notificación por email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al enviar notificación por email"
        ) 