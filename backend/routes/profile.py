from flask import jsonify, request
from config.firebase import db

def create_profile():
    data = request.json
    user_id = data['user_id']
    profile = {
        'name': data['name'],
        'email': data['email'],
        'level': data.get('level', 'beginner'),
        'location': data.get('location', '')
    }
    db.collection('users').document(user_id).set(profile)
    return jsonify({'message': 'Perfil creado'}), 200

def get_profile():
    user_id = request.args.get('user_id')
    doc = db.collection('users').document(user_id).get()
    if doc.exists:
        return jsonify(doc.to_dict()), 200
    return jsonify({'error': 'Usuario no encontrado'}), 404