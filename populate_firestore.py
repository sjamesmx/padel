import firebase_admin
from firebase_admin import credentials, firestore
import json

# Inicializar Firebase
cred = credentials.Certificate('/Users/jaime/padel/backend/firebase-cred.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# Datos de prueba
user_data = {
    'name': 'Test User',
    'email': 'test@example.com',
    'padel_iq': 80.4,
    'fuerza': 75.0
}

# Poblar datos
try:
    db.collection('users').document('xDeNWnTpkWYJzFYXI2K1gE78Rox2').set(user_data)
    print("Datos poblados exitosamente en Firestore.")
except Exception as e:
    print(f"Error al poblar datos: {str(e)}")