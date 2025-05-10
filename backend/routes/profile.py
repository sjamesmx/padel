from flask import Blueprint, request
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
    
    # Obtener el user_id de los query parameters
    user_id = request.args.get('user_id')
    if not user_id:
        logger.warning(f"No user_id provided [Request ID: {request_id}]")
        return {"error": "user_id is required"}, 400
        
    try:
        db = firestore.client()
        logger.info(f"Attempting to fetch user {user_id} [Request ID: {request_id}]")
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        if user_doc.exists:
            user_data = user_doc.to_dict()
            logger.info(f"User profile retrieved: {user_data} [Request ID: {request_id}]")
            return user_data, 200
        logger.warning(f"User not found in Firestore [Request ID: {request_id}]")
        return {"error": "User not found", "details": f"No user found with ID: {user_id}"}, 404
    except Exception as e:
        logger.error(f"Error in get_profile: {str(e)} [Request ID: {request_id}]", exc_info=True)
        return {"error": "Internal server error", "details": str(e)}, 500