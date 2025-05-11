from fastapi import APIRouter, HTTPException, Query, Depends
from firebase_admin import firestore
from app.core.deps import get_current_user
from app.schemas.user import UserInDB
from typing import List, Optional
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

@router.get("/")
async def get_social_wall(page: int = Query(1), limit: int = Query(10)):
    raise HTTPException(status_code=501, detail="Not Implemented")

@router.post("/")
async def post_social_wall():
    raise HTTPException(status_code=501, detail="Not Implemented")

@router.get("/{user_id}")
async def get_user_posts(user_id: str):
    raise HTTPException(status_code=501, detail="Not Implemented")

@router.post("/{post_id}/like")
async def like_post(post_id: str, current_user: UserInDB = Depends(get_current_user)):
    db = get_db()
    post = db.collection("posts").document(post_id).get()
    if not post.exists:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    post_data = post.to_dict()
    # Registrar el like (puedes mejorar la lógica para evitar duplicados)
    like_id = f"{current_user.id}_{post_id}"
    db.collection("likes").document(like_id).set({
        "like_id": like_id,
        "post_id": post_id,
        "user_id": current_user.id,
        "created_at": firestore.SERVER_TIMESTAMP
    })
    # Notificación automática al autor del post (si no es el mismo usuario)
    if post_data["user_id"] != current_user.id:
        notif_id = str(uuid.uuid4())
        db.collection("notifications").document(notif_id).set({
            "notification_id": notif_id,
            "user_id": post_data["user_id"],
            "type": "like_post",
            "from_user_id": current_user.id,
            "post_id": post_id,
            "created_at": firestore.SERVER_TIMESTAMP,
            "read": False
        })
    return {"message": "Like registrado"}

@router.post("/{post_id}/comment")
async def comment_post(post_id: str, content: str, current_user: UserInDB = Depends(get_current_user)):
    db = get_db()
    post = db.collection("posts").document(post_id).get()
    if not post.exists:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    post_data = post.to_dict()
    # Crear el comentario
    comment_id = str(uuid.uuid4())
    db.collection("comments").document(comment_id).set({
        "comment_id": comment_id,
        "post_id": post_id,
        "user_id": current_user.id,
        "content": content,
        "created_at": firestore.SERVER_TIMESTAMP
    })
    # Notificación automática al autor del post (si no es el mismo usuario)
    if post_data["user_id"] != current_user.id:
        notif_id = str(uuid.uuid4())
        db.collection("notifications").document(notif_id).set({
            "notification_id": notif_id,
            "user_id": post_data["user_id"],
            "type": "comment_post",
            "from_user_id": current_user.id,
            "post_id": post_id,
            "comment_id": comment_id,
            "created_at": firestore.SERVER_TIMESTAMP,
            "read": False
        })
    return {"message": "Comentario publicado", "comment_id": comment_id}

@router.get("/{post_id}/comments")
async def get_comments(post_id: str):
    raise HTTPException(status_code=501, detail="Not Implemented")

# --- Eliminación de posts y comentarios ---
@router.delete("/{post_id}")
async def delete_post(post_id: str, current_user: UserInDB = Depends(get_current_user)):
    db = get_db()
    post = db.collection("posts").document(post_id).get()
    if not post.exists:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    post_data = post.to_dict()
    if post_data["user_id"] != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="No autorizado para eliminar este post")
    db.collection("posts").document(post_id).delete()
    return {"message": "Post eliminado correctamente"}

@router.delete("/{post_id}/comments/{comment_id}")
async def delete_comment(post_id: str, comment_id: str, current_user: UserInDB = Depends(get_current_user)):
    db = get_db()
    comment = db.collection("comments").document(comment_id).get()
    if not comment.exists:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")
    comment_data = comment.to_dict()
    if comment_data["user_id"] != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="No autorizado para eliminar este comentario")
    db.collection("comments").document(comment_id).delete()
    return {"message": "Comentario eliminado correctamente"}

# --- Edición de posts y comentarios ---
@router.put("/{post_id}")
async def edit_post(post_id: str, content: str, current_user: UserInDB = Depends(get_current_user)):
    db = get_db()
    post = db.collection("posts").document(post_id).get()
    if not post.exists:
        raise HTTPException(status_code=404, detail="Post no encontrado")
    post_data = post.to_dict()
    if post_data["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado para editar este post")
    db.collection("posts").document(post_id).update({"content": content, "edited_at": firestore.SERVER_TIMESTAMP})
    return {"message": "Post editado correctamente"}

@router.put("/{post_id}/comments/{comment_id}")
async def edit_comment(post_id: str, comment_id: str, content: str, current_user: UserInDB = Depends(get_current_user)):
    db = get_db()
    comment = db.collection("comments").document(comment_id).get()
    if not comment.exists:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")
    comment_data = comment.to_dict()
    if comment_data["user_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado para editar este comentario")
    db.collection("comments").document(comment_id).update({"content": content, "edited_at": firestore.SERVER_TIMESTAMP})
    return {"message": "Comentario editado correctamente"}

# --- Notificaciones sociales ---
@router.get("/notifications")
async def get_notifications(current_user: UserInDB = Depends(get_current_user)):
    db = get_db()
    notifications = db.collection("notifications").where("user_id", "==", current_user.id).order_by("created_at", direction=firestore.Query.DESCENDING).limit(50).get()
    return [n.to_dict() for n in notifications]

@router.post("/notifications/mark_read")
async def mark_notifications_read(notification_ids: List[str], current_user: UserInDB = Depends(get_current_user)):
    db = get_db()
    for nid in notification_ids:
        notif = db.collection("notifications").document(nid).get()
        if notif.exists and notif.to_dict()["user_id"] == current_user.id:
            db.collection("notifications").document(nid).update({"read": True, "read_at": firestore.SERVER_TIMESTAMP})
    return {"message": "Notificaciones marcadas como leídas"}

# --- Reporte y moderación ---
@router.post("/{post_id}/report")
async def report_post(post_id: str, reason: str, current_user: UserInDB = Depends(get_current_user)):
    db = get_db()
    report_id = str(uuid.uuid4())
    report_data = {
        "report_id": report_id,
        "post_id": post_id,
        "user_id": current_user.id,
        "reason": reason,
        "status": "pending",
        "created_at": firestore.SERVER_TIMESTAMP
    }
    db.collection("post_reports").document(report_id).set(report_data)
    return {"message": "Reporte enviado"}

@router.post("/{post_id}/comments/{comment_id}/report")
async def report_comment(post_id: str, comment_id: str, reason: str, current_user: UserInDB = Depends(get_current_user)):
    db = get_db()
    report_id = str(uuid.uuid4())
    report_data = {
        "report_id": report_id,
        "comment_id": comment_id,
        "post_id": post_id,
        "user_id": current_user.id,
        "reason": reason,
        "status": "pending",
        "created_at": firestore.SERVER_TIMESTAMP
    }
    db.collection("comment_reports").document(report_id).set(report_data)
    return {"message": "Reporte de comentario enviado"}

@router.get("/moderation/reports")
async def get_reports(current_user: UserInDB = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Solo administradores pueden ver reportes")
    db = get_db()
    post_reports = db.collection("post_reports").where("status", "==", "pending").get()
    comment_reports = db.collection("comment_reports").where("status", "==", "pending").get()
    return {
        "post_reports": [r.to_dict() for r in post_reports],
        "comment_reports": [r.to_dict() for r in comment_reports]
    }

@router.post("/moderation/reports/{report_id}/resolve")
async def resolve_report(report_id: str, action: str, current_user: UserInDB = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Solo administradores pueden resolver reportes")
    db = get_db()
    # Buscar en ambos tipos de reportes
    post_report = db.collection("post_reports").document(report_id).get()
    comment_report = db.collection("comment_reports").document(report_id).get()
    if post_report.exists:
        db.collection("post_reports").document(report_id).update({"status": action, "resolved_at": firestore.SERVER_TIMESTAMP})
    elif comment_report.exists:
        db.collection("comment_reports").document(report_id).update({"status": action, "resolved_at": firestore.SERVER_TIMESTAMP})
    else:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    return {"message": f"Reporte resuelto con acción: {action}"}

# --- Bloqueo de usuarios ---
@router.post("/block/{target_user_id}")
async def block_user(target_user_id: str, current_user: UserInDB = Depends(get_current_user)):
    db = get_db()
    block_id = f"{current_user.id}_{target_user_id}"
    db.collection("user_blocks").document(block_id).set({
        "block_id": block_id,
        "user_id": current_user.id,
        "blocked_user_id": target_user_id,
        "created_at": firestore.SERVER_TIMESTAMP
    })
    return {"message": "Usuario bloqueado"}

@router.post("/unblock/{target_user_id}")
async def unblock_user(target_user_id: str, current_user: UserInDB = Depends(get_current_user)):
    db = get_db()
    block_id = f"{current_user.id}_{target_user_id}"
    db.collection("user_blocks").document(block_id).delete()
    return {"message": "Usuario desbloqueado"}

@router.get("/blocked")
async def get_blocked_users(current_user: UserInDB = Depends(get_current_user)):
    db = get_db()
    blocks = db.collection("user_blocks").where("user_id", "==", current_user.id).get()
    return [{"blocked_user_id": b.to_dict()["blocked_user_id"], "blocked_at": b.to_dict()["created_at"]} for b in blocks] 