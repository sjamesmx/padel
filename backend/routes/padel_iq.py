from flask import Blueprint, jsonify, request
from firebase_admin import firestore
from google.cloud import videointelligence_v1 as videointelligence
import traceback
from datetime import datetime

padel_iq_bp = Blueprint('padel_iq', __name__)

@padel_iq_bp.route('/api/calculate_padel_iq', methods=['POST'])
def calculate_padel_iq():
    try:
        data = request.json
        if not data or 'user_id' not in data or 'video_url' not in data:
            return jsonify({'error': 'Faltan user_id o video_url en la solicitud'}), 400

        user_id = data['user_id']
        video_url = data['video_url']

        # Simular clasificación de golpes con Video Intelligence API
        try:
            client = videointelligence.VideoIntelligenceServiceClient()
        except Exception as e:
            return jsonify({'error': f'Error inicializando Video Intelligence: {str(e)}'}), 500

        # En producción, analizar el video para detectar golpes
        # Por ahora, simular detección de múltiples golpes
        detected_strokes = [
            {'type': 'derecha', 'tecnica': 80, 'velocidad': 85, 'fuerza': 75},
            {'type': 'reves', 'tecnica': 78, 'velocidad': 80, 'fuerza': 70},
            {'type': 'smash', 'tecnica': 85, 'velocidad': 90, 'fuerza': 80}
        ]

        # Calcular Padel IQ promedio por golpe
        tecnica_avg = sum(stroke['tecnica'] for stroke in detected_strokes) / len(detected_strokes)
        velocidad_avg = sum(stroke['velocidad'] for stroke in detected_strokes) / len(detected_strokes)
        fuerza_avg = sum(stroke['fuerza'] for stroke in detected_strokes) / len(detected_strokes)
        padel_iq = 0.4 * tecnica_avg + 0.3 * velocidad_avg + 0.3 * fuerza_avg

        # Actualizar Firestore
        try:
            db = firestore.client()
            user_ref = db.collection('users').document(user_id)
            user_ref.update({
                'padel_iq': padel_iq,
                'fuerza': fuerza_avg,
                'last_updated': firestore.SERVER_TIMESTAMP,
                'strokes': firestore.ArrayUnion([{
                    'video_url': video_url,
                    'detected_strokes': detected_strokes,
                    'timestamp': datetime.now().isoformat()  # Usar timestamp del servidor
                }])
            })
        except Exception as e:
            return jsonify({'error': f'Error actualizando Firestore: {str(e)}'}), 500

        return jsonify({'padel_iq': padel_iq, 'fuerza': fuerza_avg})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': f'Error en el servidor: {str(e)}'}), 500