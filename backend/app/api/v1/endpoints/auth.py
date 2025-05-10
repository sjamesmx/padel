from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.core.security import create_access_token, verify_password
from app.schemas.user import User, UserCreate, Token
from app.services.firebase import get_firebase_client
from datetime import datetime
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/signup", response_model=User)
async def signup(user_in: UserCreate):
    """
    Registra un nuevo usuario.
    """
    try:
        db = get_firebase_client()
        
        # Verificar si el usuario ya existe
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', user_in.email)
        results = query.get()
        
        if results:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El email ya está registrado"
            )
        
        # Crear nuevo usuario
        user_ref = users_ref.document()
        user_data = {
            'email': user_in.email,
            'name': user_in.name,
            'nivel': user_in.nivel,
            'posicion_preferida': user_in.posicion_preferida,
            'fecha_registro': datetime.now(),
            'ultimo_analisis': None,
            'tipo_ultimo_analisis': None,
            'fecha_ultimo_analisis': None
        }
        user_ref.set(user_data)
        
        return {**user_data, 'id': user_ref.id}
        
    except Exception as e:
        logger.error(f"Error al registrar usuario: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al registrar usuario"
        )

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Inicia sesión de un usuario.
    """
    try:
        db = get_firebase_client()
        
        # Buscar usuario
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', form_data.username)
        results = query.get()
        
        if not results:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas"
            )
        
        user_doc = results[0]
        user_data = user_doc.to_dict()
        
        # Crear token de acceso
        access_token = create_access_token(data={"sub": user_data['email']})
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
        
    except Exception as e:
        logger.error(f"Error al iniciar sesión: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al iniciar sesión"
        ) 