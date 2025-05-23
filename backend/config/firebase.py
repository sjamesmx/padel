import logging
import firebase_admin
from firebase_admin import credentials

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_firebase():
    """Inicializa la aplicación de Firebase."""
    logger.info("Starting firebase.py import process")
    cred_path = "/Users/jaime/padel/backend/firebase-cred.json"
    logger.info(f"Checking credential path: {cred_path}")
    
    try:
        cred = credentials.Certificate(cred_path)
        logger.info("Loaded credentials")
        firebase_admin.initialize_app(cred)
        logger.info("Initialized Firebase app")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {str(e)}")
        raise