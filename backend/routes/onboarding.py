from flask import Blueprint, request, jsonify
from routes.padel_iq.video_processing import procesar_video_entrenamiento, procesar_video_partido
from config.mock_firebase import client
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

onboarding_bp = Blueprint('onboarding', __name__)
db = client()

@onboarding_bp.route('/signup', methods=['POST'])
def signup():
    """Registra un nuevo usuario."""
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'missing required fields: email and password'}), 400

        # Crear usuario en Firestore
        user_ref = db.collection('users').document()
        user_data = {
            'email': data['email'],
            'fecha_registro': datetime.now(),
            'nivel': 'principiante',
            'posicion_preferida': 'drive',
            'ultimo_analisis': None,
            'tipo_ultimo_analisis': None,
            'fecha_ultimo_analisis': None
        }
        user_ref.set(user_data)

        return jsonify({
            'success': True,
            'user': {
                'uid': user_ref.id,
                'email': data['email']
            }
        })

    except Exception as e:
        logger.error(f"Error al registrar usuario: {str(e)}")
        return jsonify({'error': str(e)}), 500

@onboarding_bp.route('/login', methods=['POST'])
def login():
    """Inicia sesión de un usuario."""
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'missing required fields: email and password'}), 400

        # Buscar usuario en Firestore
        users_ref = db.collection('users')
        query = users_ref.where('email', '==', data['email'])
        results = query.get()

        if not results:
            return jsonify({'error': 'user not found'}), 404

        user_doc = results[0]
        return jsonify({
            'success': True,
            'user': {
                'uid': user_doc.id,
                'email': user_doc.get('email')
            }
        })

    except Exception as e:
        logger.error(f"Error al iniciar sesión: {str(e)}")
        return jsonify({'error': str(e)}), 500

@onboarding_bp.route('/process_training_video', methods=['POST'])
def process_training_video():
    """Procesa un video de entrenamiento o partido y almacena los resultados."""
    try:
        if 'video' not in request.files:
            return jsonify({'error': 'no video file provided'}), 400

        video_file = request.files['video']
        user_id = request.form.get('user_id')
        tipo_video = request.form.get('tipo_video', 'entrenamiento')

        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        # Guardar video temporalmente
        video_path = f'temp_{video_file.filename}'
        video_file.save(video_path)

        # Procesar el video según su tipo
        if tipo_video == 'entrenamiento':
            resultados = procesar_video_entrenamiento(video_path)
        else:
            resultados = procesar_video_partido(video_path)

        # Guardar resultados en Firestore
        analisis_data = {
            'user_id': user_id,
            'video_url': video_path,
            'tipo_video': tipo_video,
            'fecha_analisis': datetime.now(),
            'estado': 'completado',
            'resultados': resultados
        }

        # Crear documento en la colección de análisis
        analisis_ref = db.collection('video_analisis').document()
        analisis_ref.set(analisis_data)

        # Actualizar el perfil del usuario
        user_ref = db.collection('users').document(user_id)
        user_ref.update({
            'ultimo_analisis': analisis_ref.id,
            'tipo_ultimo_analisis': tipo_video,
            'fecha_ultimo_analisis': datetime.now()
        })

        return jsonify({
            'success': True,
            'analysis_id': analisis_ref.id,
            'resultados': resultados
        })

    except Exception as e:
        logger.error(f"Error al procesar video: {str(e)}")
        return jsonify({'error': str(e)}), 500

@onboarding_bp.route('/get_analysis/<analysis_id>', methods=['GET'])
def get_analysis(analysis_id):
    """Obtiene los resultados de un análisis específico."""
    try:
        doc_ref = db.collection('video_analisis').document(analysis_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return jsonify({'error': 'Análisis no encontrado'}), 404
            
        return jsonify(doc.to_dict())

    except Exception as e:
        logger.error(f"Error al obtener análisis: {str(e)}")
        return jsonify({'error': str(e)}), 500