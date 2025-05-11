from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.core.security import create_access_token, verify_password, get_password_hash
from app.schemas.user import User, UserCreate, Token
from app.schemas.auth import (
    TokenRefreshRequest, TokenRefreshResponse, LogoutRequest, ForgotPasswordRequest, ResetPasswordRequest
)
from app.services.firebase import get_firebase_client
from datetime import datetime, timedelta
import logging
from uuid import uuid4

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/signup", response_model=User, summary="Registro de usuario", tags=["auth"])
async def signup(user_in: UserCreate):
    """
    Registra un nuevo usuario en el sistema.
    - Requiere email, nombre, nivel, posición preferida y contraseña.
    - Devuelve los datos del usuario creado.
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

@router.post("/login", response_model=TokenRefreshResponse, summary="Inicio de sesión", tags=["auth"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Inicia sesión de un usuario existente.
    - Requiere email y contraseña.
    - Devuelve un access token JWT para autenticación y un refresh token.
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
        # Validar contraseña (si está hasheada, usar verify_password)
        if 'hashed_password' in user_data:
            if not verify_password(form_data.password, user_data['hashed_password']):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Credenciales incorrectas"
                )
        elif 'password' in user_data:
            if form_data.password != user_data['password']:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Credenciales incorrectas"
                )
        # Crear access token
        access_token = create_access_token(data={"sub": user_data['email']})
        # Crear refresh token
        refresh_token = str(uuid4())
        expires_at = datetime.utcnow() + timedelta(days=7)
        db.collection("refresh_tokens").document(refresh_token).set({
            "user_email": user_data['email'],
            "expires_at": expires_at,
            "revoked": False
        })
        return TokenRefreshResponse(
            access_token=access_token,
            token_type="bearer",
            refresh_token=refresh_token
        )
    except Exception as e:
        logger.error(f"Error al iniciar sesión: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al iniciar sesión"
        )

@router.post("/logout", summary="Cerrar sesión", tags=["auth"])
async def logout(request: LogoutRequest):
    """
    Cierra la sesión del usuario invalidando el refresh token.
    - Requiere refresh token válido.
    """
    db = get_firebase_client()
    token_doc = db.collection("refresh_tokens").document(request.refresh_token)
    token_doc.set({"revoked": True})
    return {"detail": "Sesión cerrada correctamente"}

@router.post("/refresh", response_model=TokenRefreshResponse, summary="Refrescar token de acceso", tags=["auth"])
async def refresh_token(request: TokenRefreshRequest):
    """
    Refresca el token de acceso usando un refresh token válido.
    - Devuelve un nuevo access token y refresh token.
    """
    db = get_firebase_client()
    token_doc = db.collection("refresh_tokens").document(request.refresh_token).get()
    if not token_doc.exists or token_doc.to_dict().get("revoked"):
        raise HTTPException(status_code=401, detail="Refresh token inválido o revocado")
    token_data = token_doc.to_dict()
    if datetime.utcnow() > token_data["expires_at"].replace(tzinfo=None):
        raise HTTPException(status_code=401, detail="Refresh token expirado")
    user_email = token_data["user_email"]
    access_token = create_access_token({"sub": user_email})
    # Opcional: emitir nuevo refresh token y revocar el anterior
    new_refresh_token = str(uuid4())
    expires_at = datetime.utcnow() + timedelta(days=7)
    db.collection("refresh_tokens").document(new_refresh_token).set({
        "user_email": user_email,
        "expires_at": expires_at,
        "revoked": False
    })
    token_doc.reference.set({"revoked": True}, merge=True)
    return TokenRefreshResponse(
        access_token=access_token,
        token_type="bearer",
        refresh_token=new_refresh_token
    )

@router.post("/forgot-password", summary="Solicitar recuperación de contraseña", tags=["auth"])
async def forgot_password(request: ForgotPasswordRequest):
    """
    Solicita la recuperación de contraseña para un usuario registrado.
    - Envía un email (simulado) con instrucciones y token de recuperación.
    """
    db = get_firebase_client()
    users_ref = db.collection('users')
    query = users_ref.where('email', '==', request.email)
    results = query.get()
    if not results:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    reset_token = str(uuid4())
    expires_at = datetime.utcnow() + timedelta(hours=1)
    db.collection("password_reset_tokens").document(reset_token).set({
        "user_email": request.email,
        "expires_at": expires_at,
        "used": False
    })
    # Simulación de envío de email (en producción, integrar con un servicio real)
    logger.info(f"Token de recuperación para {request.email}: {reset_token}")
    return {"detail": "Se ha enviado un email con instrucciones para restablecer la contraseña"}

@router.post("/reset-password", summary="Restablecer contraseña", tags=["auth"])
async def reset_password(request: ResetPasswordRequest):
    """
    Restablece la contraseña de un usuario usando un token de recuperación válido.
    - Requiere token de recuperación y nueva contraseña.
    """
    db = get_firebase_client()
    token_doc = db.collection("password_reset_tokens").document(request.token).get()
    if not token_doc.exists:
        raise HTTPException(status_code=400, detail="Token de recuperación inválido")
    token_data = token_doc.to_dict()
    if token_data.get("used"):
        raise HTTPException(status_code=400, detail="Token ya utilizado")
    if datetime.utcnow() > token_data["expires_at"].replace(tzinfo=None):
        raise HTTPException(status_code=400, detail="Token expirado")
    user_email = token_data["user_email"]
    # Actualizar contraseña del usuario
    users_ref = db.collection('users')
    query = users_ref.where('email', '==', user_email)
    results = query.get()
    if not results:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    user_ref = results[0].reference
    hashed_password = get_password_hash(request.new_password)
    user_ref.update({"hashed_password": hashed_password})
    token_doc.reference.set({"used": True}, merge=True)
    return {"detail": "Contraseña restablecida correctamente"} 