import logging
from app.config.firebase import initialize_firebase

logger = logging.getLogger(__name__)

def get_firebase_client():
    """Obtiene el cliente de Firestore usando la inicialización centralizada."""
    try:
        return initialize_firebase()
    except Exception as e:
        logger.error(f"Error getting Firestore client: {str(e)}")
        raise

def get_db():
    try:
        return initialize_firebase()
    except Exception as e:
        logger.error(f"Error getting Firestore client: {str(e)}")
        return None 