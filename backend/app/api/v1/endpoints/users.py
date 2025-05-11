from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas.user import User, UserUpdate, PrivacyUpdateRequest, PreferencesUpdateRequest, DeleteAccountRequest, UserInDB
from app.services.firebase import get_firebase_client
from app.core.security import verify_password, get_password_hash
from app.core.deps import get_current_user
import logging
from fastapi import HTTPException as RealHTTPException

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/me", response_model=User)
async def read_user_me(current_user: UserInDB = Depends(get_current_user)):
    """
    Obtiene la información del usuario actual.
    """
    return current_user

@router.put("/me", response_model=User)
async def update_user_me(user_in: UserUpdate, current_user: UserInDB = Depends(get_current_user)):
    """
    Actualiza la información del usuario actual.
    """
    try:
        db = get_firebase_client()
        user_ref = db.collection('users').document(current_user.id)
        update_data = user_in.dict(exclude_unset=True)
        user_ref.update(update_data)
        user_doc = user_ref.get()
        user_data = user_doc.to_dict()
        user_data['id'] = user_ref.id
        return UserInDB(**user_data)
    except Exception as e:
        logger.error(f"Error al actualizar usuario: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al actualizar usuario")

@router.get("/{user_id}/profile")
async def read_user_profile(user_id: str, level: str = Query(None)):
    raise HTTPException(status_code=501, detail="Not Implemented")

@router.put("/{user_id}/profile")
async def update_user_profile(user_id: str, nivel: str = None, posicion_preferida: str = None, biografia: str = None):
    raise HTTPException(status_code=501, detail="Not Implemented")

@router.delete("/me")
async def delete_user_me(request: DeleteAccountRequest, current_user: UserInDB = Depends(get_current_user)):
    """Elimina la cuenta del usuario autenticado."""
    try:
        db = get_firebase_client()
        user_ref = db.collection('users').document(current_user.id)
        user_data = user_ref.get().to_dict()
        if not verify_password(request.password, user_data.get('hashed_password', '')):
            raise HTTPException(status_code=403, detail="Contraseña incorrecta")
        user_ref.delete()
        # Opcional: eliminar datos relacionados (amigos, análisis, etc.)
        return {"detail": "Cuenta eliminada correctamente"}
    except Exception as e:
        logger.error(f"Error al eliminar cuenta: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al eliminar cuenta")

@router.put("/me/privacy")
async def update_privacy_me(request: PrivacyUpdateRequest, current_user: UserInDB = Depends(get_current_user)):
    """Actualiza la configuración de privacidad del usuario."""
    try:
        db = get_firebase_client()
        user_ref = db.collection('users').document(current_user.id)
        user_ref.update({"privacy": request.privacy.dict()})
        return {"detail": "Privacidad actualizada"}
    except Exception as e:
        logger.error(f"Error al actualizar privacidad: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al actualizar privacidad")

@router.put("/me/preferences")
async def update_preferences_me(request: PreferencesUpdateRequest, current_user: UserInDB = Depends(get_current_user)):
    """Actualiza las preferencias del usuario."""
    try:
        db = get_firebase_client()
        user_ref = db.collection('users').document(current_user.id)
        user_ref.update({"preferences": request.preferences.dict()})
        return {"detail": "Preferencias actualizadas"}
    except Exception as e:
        logger.error(f"Error al actualizar preferencias: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al actualizar preferencias") 