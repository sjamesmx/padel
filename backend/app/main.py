from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router
from app.api.v1.endpoints import (
    friends,
    social_wall,
    matchmaking,
    subscriptions,
    search,
    onboarding,
    gamification,
    video_analysis
)
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_application() -> FastAPI:
    """
    Crea y configura la aplicación FastAPI.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=settings.DESCRIPTION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )

    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Incluir routers
    app.include_router(api_router, prefix=settings.API_V1_STR)
    app.include_router(friends.router, prefix=f"{settings.API_V1_STR}/friends", tags=["friends"])
    app.include_router(social_wall.router, prefix=f"{settings.API_V1_STR}/social_wall", tags=["social_wall"])
    app.include_router(matchmaking.router, prefix=f"{settings.API_V1_STR}/matchmaking", tags=["matchmaking"])
    app.include_router(subscriptions.router, prefix=f"{settings.API_V1_STR}/subscriptions", tags=["subscriptions"])
    app.include_router(search.router, prefix=f"{settings.API_V1_STR}/search", tags=["search"])
    app.include_router(onboarding.router, prefix=f"{settings.API_V1_STR}/onboarding", tags=["onboarding"])
    app.include_router(gamification.router, prefix=f"{settings.API_V1_STR}/gamification", tags=["gamification"])
    app.include_router(video_analysis.router, prefix=f"{settings.API_V1_STR}/video", tags=["video"])

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app

app = create_application() 