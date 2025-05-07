from flask import Blueprint, request, jsonify
from routes.padel_iq.video_processing import procesar_video_entrenamiento  # Importación corregida
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

onboarding_bp = Blueprint('onboarding', __name__)

@onboarding_bp.route('/api/process_training_video', methods=['POST'])
def process_training_video():
    data = request.get_json()
    video_url = data.get('video_url')
    try:
        golpes_clasificados, video_duration = procesar_video_entrenamiento(video_url)
        response = {
            'golpes_clasificados': golpes_clasificados,
            'video_duration': video_duration
        }
        return jsonify(response), 200
    except Exception as e:
        logger.error(f"Error processing training video: {str(e)}")
        return jsonify({'error': str(e)}), 500