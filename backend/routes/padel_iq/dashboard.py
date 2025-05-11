from fastapi import APIRouter, Depends, HTTPException
from firebase_admin import firestore
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

def get_db():
    try:
        return firestore.client()
    except ValueError as e:
        logger.error(f"Error inicializando Firestore: {str(e)}")
        raise HTTPException(status_code=500, detail="Error inicializando Firestore")

@router.get("/dashboard")
async def get_dashboard(db: firestore.Client = Depends(get_db)):
    try:
        logger.info("Obteniendo dashboard")
        # Aquí puedes usar db para acceder a Firestore
        return {"message": "Dashboard del usuario"}
    except Exception as e:
        logger.error(f"Error obteniendo el dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error obteniendo el dashboard: {str(e)}") 