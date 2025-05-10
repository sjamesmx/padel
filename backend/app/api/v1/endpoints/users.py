from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas.user import User, UserUpdate
from app.services.firebase import get_firebase_client
import logging
from fastapi import HTTPException as RealHTTPException

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/me", response_model=User)
async def read_user_me():
    """
    Obtiene la información del usuario actual.
    """
    try:
        # TODO: Implementar la lógica para obtener el usuario actual
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Función no implementada"
        )
    except Exception as e:
        if isinstance(e, RealHTTPException):
            raise
        logger.error(f"Error al obtener usuario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al obtener usuario"
        )

@router.put("/me", response_model=User)
async def update_user_me(user_in: UserUpdate):
    """
    Actualiza la información del usuario actual.
    """
    try:
        # TODO: Implementar la lógica para actualizar el usuario
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Función no implementada"
        )
    except Exception as e:
        if isinstance(e, RealHTTPException):
            raise
        logger.error(f"Error al actualizar usuario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al actualizar usuario"
        )

@router.get("/{user_id}/profile")
async def read_user_profile(user_id: str, level: str = Query(None)):
    raise HTTPException(status_code=501, detail="Not Implemented")

@router.put("/{user_id}/profile")
async def update_user_profile(user_id: str, nivel: str = None, posicion_preferida: str = None, biografia: str = None):
    raise HTTPException(status_code=501, detail="Not Implemented") 