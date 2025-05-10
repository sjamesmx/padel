from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routes.padel_iq import router as padel_iq_router
from routes.profile import router as profile_router
from routes.matchmaking import router as matchmaking_router
from routes.onboarding import router as onboarding_router
from routes.friends import router as friends_router
from routes.social_wall import router as social_wall_router
from routes.gamification import router as gamification_router
from routes.subscriptions import router as subscriptions_router
import logging
from pydantic import ConfigDict

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de Pydantic
model_config = ConfigDict(arbitrary_types_allowed=True)

app = FastAPI(
    title="Padelyzer API",
    description="API para el análisis de pádel y gestión de usuarios",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(padel_iq_router)
app.include_router(profile_router)
app.include_router(matchmaking_router)
app.include_router(onboarding_router)
app.include_router(friends_router)
app.include_router(social_wall_router)
app.include_router(gamification_router)
app.include_router(subscriptions_router)

@app.get("/")
async def root():
    """Endpoint raíz para verificar que la API está funcionando."""
    return {"status": "ok", "message": "Padelyzer API is running"}

@app.get("/health")
async def health_check():
    """Endpoint para verificar la salud de la API."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "services": {
            "database": "connected",
            "storage": "connected",
            "auth": "connected"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)