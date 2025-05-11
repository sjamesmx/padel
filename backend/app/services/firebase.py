import os
import logging
from firebase_admin import credentials, initialize_app, firestore
from google.cloud import firestore as google_firestore
from app.core.config import settings

logger = logging.getLogger(__name__)

def initialize_firebase():
    """Initialize Firebase with appropriate credentials based on environment."""
    try:
        # Check if we're using the emulator
        if os.environ.get("FIRESTORE_EMULATOR_HOST"):
            logger.info("Using Firestore emulator")
            initialize_app()
            return

        # Check if we're in a test environment
        if os.environ.get("PYTEST_CURRENT_TEST"):
            logger.info("Using mock Firestore client for tests")
            return

        # Production environment - require credentials
        cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        if not cred_path:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS must be set in production")

        if not os.path.exists(cred_path):
            raise FileNotFoundError(f"Credentials file not found at {cred_path}")

        cred = credentials.Certificate(cred_path)
        initialize_app(cred)
        logger.info("Firebase initialized with production credentials")

    except Exception as e:
        logger.error(f"Error initializing Firebase: {str(e)}")
        raise

def get_firebase_client():
    """Get Firestore client, using emulator if configured."""
    try:
        if os.environ.get("PYTEST_CURRENT_TEST"):
            return firestore.client()
        if os.environ.get("FIRESTORE_EMULATOR_HOST"):
            return firestore.client()
        return google_firestore.Client()
    except Exception as e:
        logger.error(f"Error getting Firestore client: {str(e)}")
        raise

def get_db():
    try:
        return firestore.client()
    except Exception as e:
        logging.error(f"Error getting Firestore client: {str(e)}")
        return None 