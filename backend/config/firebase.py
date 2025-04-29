import os
from firebase_admin import credentials, firestore, initialize_app, storage
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Inicializar Firebase y definir db y bucket globalmente
cred_path = os.getenv('FIREBASE_CRED_PATH', '/app/firebase-cred.json')
print(f"Checking credentials path: {cred_path}")
if not os.path.exists(cred_path):
    raise ValueError(f"Firebase credentials file not found at {cred_path}")
cred = credentials.Certificate(cred_path)

# Especificar el storageBucket al inicializar la app
firebase_config = {
    'storageBucket': 'padelyzer-app.firebasestorage.app'  # Nombre del bucket proporcionado
}
initialize_app(cred, firebase_config)

# Definir db y bucket como variables globales
db = firestore.client()
bucket = storage.bucket()