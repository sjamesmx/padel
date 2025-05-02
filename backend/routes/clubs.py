from flask import Blueprint, jsonify, request
from firebase_admin import firestore

clubs_bp = Blueprint('clubs', __name__)

@clubs_bp.route('/api/clubs/create', methods=['POST'])
def create_club():
    data = request.json
    db = firestore.client()
    club_ref = db.collection('clubs').document()
    club_data = {
        'club_id': club_ref.id,
        'name': data['name'],
        'city': data['city'],
        'events': [],
        'createdAt': firestore.SERVER_TIMESTAMP
    }
    club_ref.set(club_data)
    return jsonify({'club_id': club_ref.id, 'message': 'Club created'})

@clubs_bp.route('/api/clubs/<club_id>', methods=['GET'])
def get_club(club_id):
    db = firestore.client()
    club_ref = db.collection('clubs').document(club_id)
    club = club_ref.get()
    if club.exists:
        return jsonify(club.to_dict())
    return jsonify({'error': 'Club not found'}), 404