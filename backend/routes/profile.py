from flask import Blueprint
from firebase_admin import firestore
import logging
import uuid

profile_bp = Blueprint('profile', __name__)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@profile_bp.route('/api/get_profile', methods=['GET'])
def get_profile():
    request_id = "profile-" + str(uuid.uuid4())
    logger.info(f"Starting get_profile request [Request ID: {request_id}]")
    try:
        db = firestore.client()
        user_ref = db.collection('users').document('xDeNWnTpkWYJzFYXI2K1gE78Rox2')
        user_doc = user_ref.get()
        if user_doc.exists:
            logger.info(f"User profile retrieved [Request ID: {request_id}]")
            return user_doc.to_dict(), 200
        logger.warning(f"User not found [Request ID: {request_id}]")
        return {"error": "User not found"}, 404
    except Exception as e:
        logger.error(f"Error in get_profile: {str(e)} [Request ID: {request_id}]", exc_info=True)
        return {"error": "Internal server error"}, 500