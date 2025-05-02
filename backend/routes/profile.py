from flask import Blueprint, jsonify, request
from firebase_admin import firestore

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/api/get_profile', methods=['GET'])
def get_profile():
    user_id = request.headers.get('Authorization')  # Expecting user_id
    db = firestore.client()
    user_ref = db.collection('users').document(user_id)
    user_doc = user_ref.get()
    if user_doc.exists:
        return jsonify(user_doc.to_dict())
    else:
        default_data = {
            'email': 'unknown',
            'createdAt': firestore.SERVER_TIMESTAMP,
            'trialEnd': firestore.SERVER_TIMESTAMP,
            'referrals': 0,
            'plan': 'free',
            'padel_iq': 0,
            'fuerza': 0
        }
        user_ref.set(default_data)
        return jsonify(default_data)