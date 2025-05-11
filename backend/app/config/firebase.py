import firebase_admin
from firebase_admin import credentials, firestore
import os
import logging

logger = logging.getLogger(__name__)

def initialize_firebase():
    try:
        if not firebase_admin._apps:
            environment = os.getenv("ENVIRONMENT", "development")
            if environment == "development":
                logger.info("Inicializando Firebase para desarrollo con emulador")
                os.environ["FIRESTORE_EMULATOR_HOST"] = os.getenv("FIRESTORE_EMULATOR_HOST", "localhost:8080")
                firebase_admin.initialize_app()
            else:
                cred_path = os.getenv("FIREBASE_CRED_PATH")
                if not cred_path or not os.path.exists(cred_path):
                    logger.error(f"Archivo de credenciales no encontrado: {cred_path}")
                    raise FileNotFoundError(f"Archivo de credenciales no encontrado: {cred_path}")
                logger.info("Inicializando Firebase para producción")
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
        return firestore.client()
    except Exception as e:
        logger.error(f"Error inicializando Firebase: {str(e)}")
        raise RuntimeError(f"Error inicializando Firebase: {str(e)}")

def get_db():
    if not firebase_admin._apps:
        raise ValueError("Firebase no está inicializado. Asegúrate de llamar a initialize_firebase() primero.")
    return firestore.client() 