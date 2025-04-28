from flask import Flask, request, jsonify
from firebase_admin import credentials, firestore, initialize_app
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Usa la ruta predeterminada para Cloud Run, con depuración
cred_path = os.getenv('FIREBASE_CRED_PATH', '/app/firebase-cred.json')
print(f"Checking credentials path: {cred_path}")
if not os.path.exists(cred_path):
    raise ValueError(f"Firebase credentials file not found at {cred_path}")
cred = credentials.Certificate(cred_path)
initialize_app(cred)
db = firestore.client()

@app.route('/create_profile', methods=['POST'])
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

@app.route('/get_profile', methods=['GET'])
def get_profile():
    user_id = request.args.get('user_id')
    doc = db.collection('users').document(user_id).get()
    if doc.exists:
        return jsonify(doc.to_dict()), 200
    return jsonify({'error': 'Usuario no encontrado'}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))