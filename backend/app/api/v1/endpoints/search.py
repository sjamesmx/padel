from fastapi import APIRouter, HTTPException, Query, Depends
from firebase_admin import firestore
from app.core.deps import get_current_user
from app.schemas.user import UserInDB
from typing import Optional, List
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

# Buscar usuarios (requiere autenticación)
@router.get("/users")
async def search_users(
    query: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    level: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: UserInDB = Depends(get_current_user)
):
    db = get_db()
    users_ref = db.collection("users")
    users_query = users_ref
    if location:
        users_query = users_query.where("location", "==", location)
    if level:
        users_query = users_query.where("level", "==", level)
    if email:
        users_query = users_query.where("email", "==", email)
    users = users_query.get()
    # Filtrado por texto (simulado, para producción usar Algolia/ElasticSearch)
    results = []
    for u in users:
        data = u.to_dict()
        if query:
            if (
                query.lower() in data.get("username", "").lower() or
                query.lower() in data.get("email", "").lower() or
                query.lower() in data.get("location", "").lower()
            ):
                results.append(data)
        else:
            results.append(data)
    return results[offset:offset+limit]

# Buscar contenido (posts/videos) (requiere autenticación)
@router.get("/content")
async def search_content(
    query: Optional[str] = Query(None),
    type: Optional[str] = Query(None, description="Tipo de contenido: post o video"),
    user_id: Optional[str] = Query(None),
    from_date: Optional[str] = Query(None, description="Fecha desde (YYYY-MM-DD)"),
    to_date: Optional[str] = Query(None, description="Fecha hasta (YYYY-MM-DD)"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: UserInDB = Depends(get_current_user)
):
    db = get_db()
    if type == "video":
        ref = db.collection("videos")
    else:
        ref = db.collection("posts")
    content_query = ref
    if user_id:
        content_query = content_query.where("user_id", "==", user_id)
    # NOTA: Firestore no soporta filtros de rango sobre diferentes campos a la vez, ni contains nativo
    items = content_query.get()
    results = []
    for i in items:
        data = i.to_dict()
        # Filtro por texto
        if query:
            if (
                query.lower() in data.get("content", "").lower() or
                query.lower() in data.get("title", "").lower()
            ):
                pass
            else:
                continue
        # Filtro por fecha (simulado, requiere que los documentos tengan un campo 'created_at' tipo string YYYY-MM-DD)
        if from_date and data.get("created_at") and data["created_at"] < from_date:
            continue
        if to_date and data.get("created_at") and data["created_at"] > to_date:
            continue
        results.append(data)
    return results[offset:offset+limit]

@router.post("/players")
async def search_players():
    raise HTTPException(status_code=501, detail="Not Implemented")

@router.get("/nearby")
async def get_nearby_players():
    raise HTTPException(status_code=501, detail="Not Implemented") 