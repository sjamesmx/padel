from flask import Blueprint, request, jsonify
from firebase_admin import firestore
import logging
from .analysis_manager import AnalysisManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = firestore.client()

analysis_manager = AnalysisManager()

padel_iq_bp = Blueprint('padel_iq', __name__)

@padel_iq_bp.route('/api/calculate_padel_iq', methods=['POST'])
def calculate_padel_iq():
    """Procesa un video y calcula métricas de Padel IQ."""
    data = request.get_json()
    user_id = data.get('user_id')
    video_url = data.get('video_url')
    tipo_video = data.get('tipo_video')
    player_position = data.get('player_position', {'side': 'left', 'zone': 'back'})
    game_splits = data.get('game_splits', None)

    if not user_id or not video_url or not tipo_video:
        logger.error("Faltan datos requeridos en la solicitud")
        return jsonify({'error': 'Faltan datos requeridos (user_id, video_url, tipo_video)'}), 400

    logger.info(f"Procesando video para user_id: {user_id}, video_url: {video_url}, tipo_video: {tipo_video}")

    try:
        if tipo_video == 'entrenamiento':
            logger.info("Iniciando procesamiento de video de entrenamiento")
            golpes_clasificados, video_duration, pair_metrics = analysis_manager.process_video(video_url, player_position, game_splits, video_id=user_id)
        elif tipo_video == 'juego':
            logger.info("Iniciando procesamiento de video de juego")
            golpes_clasificados, video_duration, pair_metrics = analysis_manager.process_video(video_url, player_position, game_splits, video_id=user_id)
        else:
            logger.error("Tipo de video no soportado")
            return jsonify({'error': 'Tipo de video no soportado'}), 400

        logger.info(f"Video duration received: {video_duration} seconds")
        logger.info(f"Golpes clasificados: {golpes_clasificados}")

        total_golpes = 0
        tecnica_total = 0
        ritmo = 0
        fuerza = 0
        repeticion = 0
        golpes_en_red = 0
        golpes_exitosos_en_red = 0

        for tipo, golpes in golpes_clasificados.items():
            total_golpes += len(golpes)
            for golpe in golpes:
                tecnica_total += golpe.get('calidad', 0)
                fuerza += golpe.get('max_wrist_speed', 0)
                if tipo_video == 'juego':
                    if golpe.get('posicion_cancha') == 'red':
                        golpes_en_red += 1
                        if tipo in ['smash', 'volea_derecha', 'volea_reves', 'derecha', 'reves', 'bandeja']:
                            golpes_exitosos_en_red += 1

        logger.info(f"Total golpes calculados: {total_golpes}")
        tecnica = (tecnica_total / total_golpes) if total_golpes > 0 else 0
        tecnica = min(tecnica, 100)
        logger.info(f"Antes de calcular ritmo: total_golpes={total_golpes}, video_duration={video_duration}")
        ritmo = (total_golpes / video_duration) * 120 if video_duration > 0 else 0  # Volver al factor 120
        logger.info(f"Ritmo calculado: {ritmo}")
        ritmo = min(ritmo, 100)
        fuerza = (fuerza / total_golpes) if total_golpes > 0 else 0
        fuerza = min(fuerza, 100)
        repeticion = 2.0

        padel_iq = (tecnica * 0.4 + ritmo * 0.3 + fuerza * 0.2 + repeticion * 0.1) + 15
        padel_iq = min(padel_iq, 100)
        player_level = "Principiante" if padel_iq < 30 else "Intermedio" if padel_iq < 60 else "Avanzado"
        force_category = "quinta_fuerza"

        efectividad_red = (golpes_exitosos_en_red / golpes_en_red * 100) if golpes_en_red > 0 else 0

        response = {
            'detected_positions': ["jugador unico"] if tipo_video == 'entrenamiento' else ["múltiples jugadores"],
            'detected_strokes': [{
                'golpes_clasificados': golpes_clasificados,
                'tecnica': tecnica,
                'ritmo': ritmo,
                'fuerza': fuerza,
                'repeticion': repeticion,
                'type': "practica" if tipo_video == 'entrenamiento' else "juego",
                'efectividad_red': efectividad_red if tipo_video == 'juego' else None
            }],
            'force_category': force_category,
            'force_level': fuerza,
            'padel_iq': padel_iq,
            'player_level': player_level,
            'pair_metrics': pair_metrics
        }

        logger.info(f"Calculated Padel IQ for {user_id}: {padel_iq}")
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error calculating Padel IQ: {str(e)}")
        return jsonify({'error': f"Error calculating Padel IQ: {str(e)}"}), 500