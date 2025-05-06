import logging
from flask import Blueprint, jsonify, request
from firebase_admin import firestore
from .config import WEIGHTS, GOLPE_FACTORS
from .metrics import calculate_tecnica, adjust_tecnica, calculate_coverage, calculate_ritmo, calculate_repeticion, calculate_fuerza, determine_player_level, determine_force_category
from .procesar_videos_entrenamiento import procesar_video_entrenamiento

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear blueprint para las rutas
padel_iq_bp = Blueprint('padel_iq', __name__)

@padel_iq_bp.route('/api/calculate_padel_iq', methods=['POST'])
def calculate_padel_iq():
    """Calcula el Padel IQ y la métrica de fuerza basada en los datos de video recibidos."""
    try:
        # Obtener datos de la solicitud
        data = request.get_json()
        user_id = data.get('user_id')
        video_url = data.get('video_url')
        videos = data.get('videos', {})
        tipo_video = data.get('tipo_video')
        player_identifier = data.get('player_identifier')

        if not user_id:
            logger.error("Falta user_id en la solicitud")
            return jsonify({"error": "Falta user_id"}), 400

        if video_url and tipo_video and not videos:
            tipo_golpe = "practica"
            videos = {tipo_golpe: video_url}
        elif not videos or not tipo_video:
            logger.error("Faltan parámetros en la solicitud")
            return jsonify({"error": "Faltan parámetros"}), 400

        if tipo_video == "juego" and not player_identifier:
            logger.error("Debe especificar el jugador objetivo para videos de juego real")
            return jsonify({"error": "Debe especificar el jugador objetivo para videos de juego real"}), 400

        tecnica_scores = []
        cobertura_scores = []
        ritmo_scores = []
        repeticion_scores = []
        fuerza_scores = []
        detected_strokes = []
        detected_positions = []

        # Procesar cada tipo de golpe en los videos
        for tipo_golpe, video_url in videos.items():
            if video_url:
                if tipo_video == "entrenamiento":
                    # Procesamiento específico para videos de entrenamiento
                    golpes_clasificados, video_duration = procesar_video_entrenamiento(video_url)
                    
                    # Calcular métricas basadas en golpes_clasificados
                    shot_count = sum(len(golpes) for golpes in golpes_clasificados.values())
                    # Calcular avg_speed basado en las velocidades de la muñeca
                    wrist_speeds = [golpe['max_wrist_speed'] for golpes in golpes_clasificados.values() for golpe in golpes]
                    avg_speed = sum(wrist_speeds) / len(wrist_speeds) if wrist_speeds else 0.0
                    context_detected = True
                    # Simular un objeto target_player para compatibilidad
                    target_player = type('obj', (object,), {'frames': [type('frame', (object,), {'normalized_bounding_box': type('box', (object,), {'left': 0.1, 'right': 0.2, 'top': 0.1, 'bottom': 0.2})})] * 793})
                else:
                    # Procesamiento para videos de juego (no implementado por ahora)
                    logger.error("Procesamiento de videos de juego no implementado en esta fase.")
                    return jsonify({"error": "Procesamiento de videos de juego no implementado en esta fase."}), 501

                # Cálculo de métricas
                ritmo = calculate_ritmo([], video_duration, tipo_golpe, GOLPE_FACTORS, shot_count)
                tecnica = calculate_tecnica(target_player, tipo_golpe, context_detected, GOLPE_FACTORS, ritmo, avg_speed)
                fuerza = calculate_fuerza(avg_speed, tipo_golpe, GOLPE_FACTORS)

                # Solo calcular cobertura para videos de juego
                cobertura = 0
                if tipo_video == "juego":
                    cobertura = calculate_coverage(target_player, tipo_golpe, GOLPE_FACTORS, video_duration, avg_speed)

                if tipo_video == "entrenamiento":
                    repeticion = calculate_repeticion(target_player, [], tipo_golpe, GOLPE_FACTORS, shot_count)
                    repeticion_scores.append(repeticion)
                    tecnica = adjust_tecnica(tecnica, tipo_video, repeticion, ritmo)
                    detected_strokes.append({
                        "type": tipo_golpe,
                        "tecnica": tecnica,
                        "ritmo": ritmo,
                        "repeticion": repeticion,
                        "fuerza": fuerza,
                        "golpes_clasificados": golpes_clasificados  # Añadir resultados del análisis
                    })
                else:
                    tecnica = adjust_tecnica(tecnica, tipo_video, 0, ritmo)
                    detected_strokes.append({
                        "type": tipo_golpe,
                        "tecnica": tecnica,
                        "cobertura": cobertura,
                        "ritmo": ritmo,
                        "fuerza": fuerza
                    })

                tecnica_scores.append(tecnica)
                cobertura_scores.append(cobertura)
                ritmo_scores.append(ritmo)
                fuerza_scores.append(fuerza)
                detected_positions.append(player_identifier if tipo_video == "juego" else "jugador unico")

        # Calcular promedios de métricas
        avg_tecnica = sum(tecnica_scores) / len(tecnica_scores) if tecnica_scores else 0
        avg_cobertura = sum(cobertura_scores) / len(cobertura_scores) if cobertura_scores else 0
        avg_ritmo = sum(ritmo_scores) / len(ritmo_scores) if ritmo_scores else 0
        avg_repeticion = sum(repeticion_scores) / len(repeticion_scores) if repeticion_scores else 0
        force_level = sum(fuerza_scores) / len(fuerza_scores) if fuerza_scores else 0

        # Cálculo del Padel IQ
        if tipo_video == "entrenamiento":
            padel_iq = (0.5 * avg_tecnica) + (0.3 * avg_ritmo) + (0.2 * avg_repeticion)
            logger.info(f"Calculated Padel IQ for training: tecnica={avg_tecnica}, ritmo={avg_ritmo}, repeticion={avg_repeticion}")
        else:
            padel_iq = (0.5 * avg_tecnica) + (0.1 * avg_cobertura) + (0.4 * avg_ritmo)
            logger.info(f"Calculated Padel IQ for game: tecnica={avg_tecnica}, cobertura={avg_cobertura}, ritmo={avg_ritmo}")

        # Determinar nivel del jugador y categoría de fuerza
        player_level = determine_player_level(padel_iq)
        force_category = determine_force_category(force_level)

        # Almacenar en Firestore
        db = firestore.client()
        user_ref = db.collection('users').document(user_id)
        user_ref.set({
            'padel_iq': padel_iq,
            'player_level': player_level,
            'force_level': force_level,
            'force_category': force_category,
            'detected_strokes': detected_strokes,
            'detected_positions': detected_positions
        }, merge=True)
        logger.info(f"Almacenado en Firestore para user_id {user_id}: padel_iq={padel_iq}, force_level={force_level}, force_category={force_category}")

        # Preparar respuesta
        response = {
            "padel_iq": padel_iq,
            "player_level": player_level,
            "force_level": force_level,
            "force_category": force_category,
            "detected_strokes": detected_strokes,
            "detected_positions": detected_positions
        }
        logger.info(f"Padel IQ calculado para {player_identifier}: {padel_iq}")
        return jsonify(response), 200

    except Exception as e:
        logger.error(f"Error al calcular Padel IQ: {str(e)}")
        return jsonify({"error": str(e)}), 500