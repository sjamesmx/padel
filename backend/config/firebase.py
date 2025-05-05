from firebase_admin import credentials, firestore, storage, initialize_app
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Starting firebase.py import process")

try:
    # Inicializar Firebase
    cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', '/app/firebase-cred.json')
    logger.info(f"Checking credential path: {cred_path}")
    cred = credentials.Certificate(cred_path)
    logger.info("Loaded credentials")
    initialize_app(cred, {
        'storageBucket': 'pdzr-458820.firebasestorage.app'
    })
    logger.info("Initialized Firebase app")
    db = firestore.client()
    bucket = storage.bucket()
except Exception as e:
    logger.error(f"Error initializing Firebase: {str(e)}", exc_info=True)
    raise