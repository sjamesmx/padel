from flask import Blueprint, request, jsonify
from config.mock_firebase import client
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dashboard_bp = Blueprint('dashboard', __name__)
db = client()

@dashboard_bp.route('/get_analysis_details/<analysis_id>', methods=['GET'])
def get_analysis_details(analysis_id):
    """Obtiene los detalles de un análisis específico."""
    try:
        # Obtener el documento del análisis
        analisis_ref = db.collection('video_analisis').document(analysis_id)
        analisis_doc = analisis_ref.get()
        
        if not analisis_doc:
            return jsonify({'error': 'Análisis no encontrado'}), 404
            
        return jsonify(analisis_doc.to_dict())
        
    except Exception as e:
        logger.error(f"Error al obtener detalles del análisis: {str(e)}")
        return jsonify({'error': str(e)}), 500

@dashboard_bp.route('/get_user_analytics', methods=['GET'])
def get_user_analytics():
    """Obtiene las estadísticas y análisis del usuario."""
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400
            
        # Obtener el perfil del usuario
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if not user_doc:
            return jsonify({'error': 'Usuario no encontrado'}), 404
            
        user_data = user_doc.to_dict()
        
        # Obtener todos los análisis del usuario
        analisis_ref = db.collection('video_analisis')
        analisis_docs = [doc for doc in analisis_ref.document() if doc.get('user_id') == user_id]
        
        # Calcular estadísticas generales
        estadisticas = {
            'total_analisis': len(analisis_docs),
            'analisis_por_tipo': {
                'entrenamiento': len([doc for doc in analisis_docs if doc.get('tipo_video') == 'entrenamiento']),
                'partido': len([doc for doc in analisis_docs if doc.get('tipo_video') == 'partido'])
            },
            'ultimo_analisis': user_data.get('ultimo_analisis'),
            'tipo_ultimo_analisis': user_data.get('tipo_ultimo_analisis'),
            'fecha_ultimo_analisis': user_data.get('fecha_ultimo_analisis')
        }
        
        # Obtener detalles del último análisis si existe
        ultimo_analisis = None
        if user_data.get('ultimo_analisis'):
            ultimo_analisis_ref = db.collection('video_analisis').document(user_data['ultimo_analisis'])
            ultimo_analisis_doc = ultimo_analisis_ref.get()
            if ultimo_analisis_doc:
                ultimo_analisis = ultimo_analisis_doc.to_dict()
        
        return jsonify({
            'perfil_usuario': user_data,
            'estadisticas': estadisticas,
            'ultimo_analisis': ultimo_analisis
        })
        
    except Exception as e:
        logger.error(f"Error al obtener estadísticas del usuario: {str(e)}")
        return jsonify({'error': str(e)}), 500 