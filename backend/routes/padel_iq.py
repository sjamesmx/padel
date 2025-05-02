<<<<<<< HEAD
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
=======
from flask import jsonify, request, g
from config.firebase import db
from utils.video_analysis import analyze_video
import logging
import uuid
import numpy as np

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_padel_iq(metrics):
    # Calcular puntajes promedio por categoría
    # Para golpeo, sumamos todos los valores dentro de cada metric["golpeo"]
    total_golpeo = sum(sum(metric["golpeo"].values()) for metric in metrics.values())
    num_golpeo = sum(len(metric["golpeo"]) for metric in metrics.values())
    golpeo_score = total_golpeo / num_golpeo if num_golpeo > 0 else 0

    # Para movimiento, sumamos todos los valores dentro de cada metric["movimiento"]
    total_movimiento = sum(sum(metric["movimiento"].values()) for metric in metrics.values())
    num_movimiento = sum(len(metric["movimiento"]) for metric in metrics.values())
    movimiento_score = total_movimiento / num_movimiento if num_movimiento > 0 else 0

    # Para tecnica, sumamos todos los valores dentro de cada metric["tecnica"]
    total_tecnica = sum(sum(metric["tecnica"].values()) for metric in metrics.values())
    num_tecnica = sum(len(metric["tecnica"]) for metric in metrics.values())
    tecnica_score = total_tecnica / num_tecnica if num_tecnica > 0 else 0

    # Calcular Padel IQ (promedio ponderado)
    padel_iq = (0.4 * golpeo_score + 0.3 * movimiento_score + 0.3 * tecnica_score)

    # Clasificar en fuerza
    if padel_iq >= 85:
        fuerza = "Primera Fuerza (Profesional)"
    elif padel_iq >= 70:
        fuerza = "Segunda Fuerza (Avanzado)"
    elif padel_iq >= 55:
        fuerza = "Tercera Fuerza (Intermedio-Avanzado)"
    elif padel_iq >= 40:
        fuerza = "Cuarta Fuerza (Intermedio)"
    elif padel_iq >= 25:
        fuerza = "Quinta Fuerza (Principiantes-Intermedio)"
    else:
        fuerza = "Sexta Fuerza (Principiantes)"

    # Calcular métricas agregadas
    aggregated_metrics = {
        "golpeo": {k: v for metric in metrics.values() for k, v in metric["golpeo"].items()},
        "movimiento": {k: sum(metric["movimiento"][k] for metric in metrics.values()) / len(metrics) for k in metrics[list(metrics.keys())[0]]["movimiento"]},
        "tecnica": {k: sum(metric["tecnica"][k] for metric in metrics.values()) / len(metrics) for k in metrics[list(metrics.keys())[0]]["tecnica"]}
    }

    # Añadir log para depurar el retorno
    logger.info(f"Returning from calculate_padel_iq: padel_iq={padel_iq}, fuerza={fuerza}, aggregated_metrics={aggregated_metrics}")

    return padel_iq, fuerza, aggregated_metrics

def calculate_padel_iq_endpoint(*args, **kwargs):
    # Generar un identificador único para la solicitud
    request_id = str(uuid.uuid4())
    logger.info(f"Starting calculate_padel_iq request [Request ID: {request_id}]")

    # Verificar si la solicitud ya está siendo procesada
    if hasattr(g, 'processing_request') and g.processing_request:
        logger.warning(f"Request already being processed, ignoring duplicate invocation [Request ID: {request_id}]")
        return jsonify({"error": "Request already being processed"}), 429

    # Marcar que la solicitud está siendo procesada
    g.processing_request = True

    try:
        data = request.json
        if not data or 'user_id' not in data or 'videos' not in data:
            logger.error(f"Invalid request: user_id and videos are required [Request ID: {request_id}]")
            return jsonify({"error": "Invalid request: user_id and videos are required"}), 400

        user_id = data['user_id']
        videos = data['videos']
        logger.info(f"Processing videos for user {user_id}: {videos.keys()} [Request ID: {request_id}]")

        # Analizar cada video
        metrics = {}
        for stroke, url in videos.items():
            try:
                logger.info(f"Starting analysis for stroke {stroke} [Request ID: {request_id}]")
                metrics[stroke] = analyze_video(url, stroke)
                logger.info(f"Completed analysis for stroke {stroke} [Request ID: {request_id}]")
            except Exception as e:
                logger.error(f"Failed to analyze video for {stroke}: {str(e)} [Request ID: {request_id}]")
                return jsonify({"error": f"Failed to analyze video for {stroke}: {str(e)}"}), 400

        logger.info(f"Finished processing all videos [Request ID: {request_id}]")
        logger.info(f"Calculating Padel IQ [Request ID: {request_id}]")
        # Calcular Padel IQ y clasificar
        padel_iq, fuerza, aggregated_metrics = calculate_padel_iq(metrics)
        logger.info(f"Padel IQ calculated [Request ID: {request_id}]")

        # No guardamos en Firestore para simplificar
        logger.info(f"Returning response [Request ID: {request_id}]")
        return jsonify({"padel_iq": padel_iq, "fuerza": fuerza, "metrics": aggregated_metrics}), 200
    except Exception as e:
        logger.error(f"Internal server error: {str(e)} [Request ID: {request_id}]")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500
    finally:
        # Limpiar el contexto para permitir nuevas solicitudes
        g.processing_request = False
        logger.info(f"Finished calculate_padel_iq request [Request ID: {request_id}]")
>>>>>>> 85d2ff8062e6ccda6f9067adeb6155ac5e5ae046
