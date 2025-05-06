import logging
from google.cloud import videointelligence_v1
import re
import math
from .motion_analyzer import analyze_video_with_mediapipe_and_opencv

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_to_gs_url(firebase_url):
    """Convierte una URL de Firebase Storage a formato gs://."""
    match = re.match(r"https://firebasestorage\.googleapis\.com/v0/b/([^/]+)/o/([^?]+)", firebase_url)
    if not match:
        logger.error(f"Invalid Firebase Storage URL format: {firebase_url}")
        raise ValueError(f"Invalid Firebase Storage URL format: {firebase_url}")
    bucket_name = match.group(1)
    file_path = match.group(2)
    gs_url = f"gs://{bucket_name}/{file_path}"
    logger.info(f"Converted Firebase URL to gs:// format: {gs_url}")
    return gs_url

def iou(box1, box2):
    """Calcula el Intersection over Union (IoU) entre dos bounding boxes."""
    x_left = max(box1.left, box2.left)
    y_top = max(box1.top, box2.top)
    x_right = min(box1.right, box2.right)
    y_bottom = min(box1.bottom, box2.bottom)

    if x_right < x_left or y_bottom < y_top:
        return 0.0

    intersection_area = (x_right - x_left) * (y_bottom - y_top)
    box1_area = (box1.right - box1.left) * (box1.bottom - box1.top)
    box2_area = (box2.right - box2.left) * (box2.bottom - box2.top)
    union_area = box1_area + box2_area - intersection_area

    return intersection_area / union_area if union_area > 0 else 0.0

def merge_players(players):
    """Fusiona jugadores detectados que probablemente sean el mismo."""
    if not players:
        return []

    merged_players = []
    used = [False] * len(players)

    for i in range(len(players)):
        if used[i]:
            continue
        current_player = players[i]
        current_frames = current_player.frames
        used[i] = True

        for j in range(i + 1, len(players)):
            if used[j]:
                continue
            other_player = players[j]
            other_frames = other_player.frames

            overlap = False
            for frame1 in current_frames:
                for frame2 in other_frames:
                    if (hasattr(frame1.normalized_bounding_box, 'left') and hasattr(frame2.normalized_bounding_box, 'left')):
                        time_diff = abs((frame1.time_offset.seconds + frame1.time_offset.microseconds / 1e6) -
                                        (frame2.time_offset.seconds + frame2.time_offset.microseconds / 1e6))
                        if time_diff < 0.1:
                            iou_score = iou(frame1.normalized_bounding_box, frame2.normalized_bounding_box)
                            if iou_score > 0.2:
                                overlap = True
                                break
                if overlap:
                    break

            if overlap:
                current_frames.extend(other_frames)
                used[j] = True

        merged_player = type(current_player)(
            entity=current_player.entity,
            frames=sorted(current_frames, key=lambda f: f.time_offset.seconds + f.time_offset.microseconds / 1e6)
        )
        merged_players.append(merged_player)

    logger.info(f"Merged {len(players)} detected players into {len(merged_players)} unified players")
    return merged_players

def select_main_players(players, num_players):
    """Selecciona los jugadores principales basándose en el número de frames."""
    if not players:
        return []
    sorted_players = sorted(players, key=lambda p: len(p.frames), reverse=True)
    selected_players = sorted_players[:num_players]
    logger.info(f"Selected {len(selected_players)} main players out of {len(players)} detected players")
    return selected_players

def select_main_player(players):
    """Selecciona el jugador principal con más frames."""
    if not players:
        logger.error("No players detected in the video")
        return None

    main_player = max(players, key=lambda p: len(p.frames), default=None)
    logger.info(f"Selected main player with {len(main_player.frames)} frames out of {len(players)} detected players")
    return main_player

def assign_player_positions(players):
    """Asigna posiciones a los jugadores basándose en sus coordenadas promedio."""
    if not players:
        return {}

    player_positions = {}
    assigned_positions = {}

    for i, player in enumerate(players):
        avg_x = 0
        avg_y = 0
        frame_count = 0
        for frame in player.frames:
            if hasattr(frame.normalized_bounding_box, 'left') and hasattr(frame.normalized_bounding_box, 'right'):
                avg_x += (frame.normalized_bounding_box.left + frame.normalized_bounding_box.right) / 2
                avg_y += (frame.normalized_bounding_box.top + frame.normalized_bounding_box.bottom) / 2
                frame_count += 1
            else:
                logger.warning(f"Frame {frame_count} of player {i} lacks bounding box data")
        if frame_count > 0:
            avg_x /= frame_count
            avg_y /= frame_count
            logger.info(f"Player {i} has valid bounding box data: avg_x={avg_x}, avg_y={avg_y}, frames={frame_count}")
            player_positions[i] = {"avg_x": avg_x, "avg_y": avg_y, "player": player}
        else:
            logger.warning(f"No valid frames with bounding box data for player {i}, total frames: {len(player.frames)}")

    for idx, pos_data in player_positions.items():
        avg_x = pos_data["avg_x"]
        avg_y = pos_data["avg_y"]
        if avg_y < 0.5:
            if avg_x < 0.5:
                assigned_positions["jugador 1"] = pos_data["player"]
            else:
                assigned_positions["jugador 2"] = pos_data["player"]
        else:
            if avg_x < 0.5:
                assigned_positions["jugador 3"] = pos_data["player"]
            else:
                assigned_positions["jugador 4"] = pos_data["player"]

    if len(assigned_positions) < len(players):
        remaining_players = [p for i, p in enumerate(players) if i not in [k for k, v in player_positions.items() if v["player"] in assigned_positions.values()]]
        remaining_players = sorted(remaining_players, key=lambda p: len(p.frames), reverse=True)
        for i, player in enumerate(remaining_players, start=1):
            position = f"jugador {i}"
            if position not in assigned_positions:
                assigned_positions[position] = player
                logger.info(f"Assigned position {position} to player with {len(player.frames)} frames (fallback method)")

    return assigned_positions

def find_closest_racket(player, rackets):
    """Encuentra la raqueta más cercana al jugador."""
    if not player.frames or not rackets:
        logger.warning("No frames for player or no rackets detected")
        return None

    player_frame = None
    for frame in player.frames:
        if hasattr(frame.normalized_bounding_box, 'left') and hasattr(frame.normalized_bounding_box, 'right'):
            player_frame = frame
            break

    if not player_frame:
        logger.warning("No valid bounding box found for player")
        return None

    player_center_x = (player_frame.normalized_bounding_box.left + player_frame.normalized_bounding_box.right) / 2
    player_center_y = (player_frame.normalized_bounding_box.top + player_frame.normalized_bounding_box.bottom) / 2

    closest_racket = None
    min_distance = float('inf')

    for racket in rackets:
        racket_frame = None
        for frame in racket.frames:
            if hasattr(frame.normalized_bounding_box, 'left') and hasattr(frame.normalized_bounding_box, 'right'):
                racket_frame = frame
                break

        if not racket_frame:
            logger.warning(f"No valid bounding box found for racket: {racket.entity.description}")
            continue

        racket_center_x = (racket_frame.normalized_bounding_box.left + racket_frame.normalized_bounding_box.right) / 2
        racket_center_y = (racket_frame.normalized_bounding_box.top + racket_frame.normalized_bounding_box.bottom) / 2

        distance = math.sqrt((player_center_x - racket_center_x)**2 + (player_center_y - racket_center_y)**2)
        if distance < min_distance:
            min_distance = distance
            closest_racket = racket

    return closest_racket

def analyze_video(video_url, tipo_golpe, player_level, tipo_video, player_identifier, golpe_factors):
    """Analiza un video usando Google Cloud Video Intelligence y MediaPipe/OpenCV."""
    logger.info(f"Analyzing video for stroke type: {tipo_golpe}, player level: {player_level}, video_type: {tipo_video}, player_identifier: {player_identifier}, video_url: {video_url}")
    try:
        # Análisis con Google Cloud Video Intelligence
        gs_url = convert_to_gs_url(video_url)

        video_client = videointelligence_v1.VideoIntelligenceServiceClient()
        logger.info("Video Intelligence client initialized successfully")

        features = [
            videointelligence_v1.Feature.OBJECT_TRACKING,
            videointelligence_v1.Feature.LABEL_DETECTION,
            videointelligence_v1.Feature.SHOT_CHANGE_DETECTION
        ]
        logger.info(f"Features configured: {features}")

        operation = video_client.annotate_video(
            request={
                "features": features,
                "input_uri": gs_url,
                "output_uri": None
            }
        )
        logger.info("Video annotation operation started")
        result = operation.result(timeout=600)
        logger.info("Video analysis completed successfully")

        context_detected = False
        players = []
        rackets = []
        if result.annotation_results:
            for annotation in result.annotation_results:
                if annotation.object_annotations:
                    for obj in annotation.object_annotations:
                        description = obj.entity.description.lower()
                        logger.info(f"Detected object: {description} with {len(obj.frames)} frames")
                        if description in ["person", "jugador", "player"]:
                            players.append(obj)
                            logger.info(f"Detected player with {len(obj.frames)} frames")
                        elif description in ["racket", "raqueta", "paddle", "tennis racket", "sports equipment"]:
                            rackets.append(obj)
                            logger.info(f"Detected racket with {len(obj.frames)} frames")
                if annotation.segment_label_annotations:
                    for label in annotation.segment_label_annotations:
                        logger.info(f"Detected label: {label.entity.description}")
                        if "padel" in label.entity.description.lower() or "tennis" in label.entity.description.lower() or "sports" in label.entity.description.lower():
                            context_detected = True

        # Calcular la duración del video
        video_duration = 0
        if players and players[0].frames:
            last_frame = players[0].frames[-1]
            video_duration = last_frame.time_offset.seconds + last_frame.time_offset.microseconds / 1e6
        logger.info(f"Calculated video duration: {video_duration} seconds")

        # Análisis con MediaPipe y OpenCV
        avg_speed, frame_count, shot_count = analyze_video_with_mediapipe_and_opencv(video_url)
        if avg_speed is None or frame_count is None or shot_count is None:
            logger.warning("No se pudo realizar el análisis con MediaPipe/OpenCV, usando valores por defecto")
            avg_speed = 0
            frame_count = len(players[0].frames) if players and players[0].frames else 0
            shot_count = 0

        players = merge_players(players)

        if tipo_video == "entrenamiento":
            if not players:
                logger.error("No players detected in training video")
                return None, "No players detected in training video", 400
            target_player = select_main_player(players)
            if not target_player:
                logger.error("Could not select a main player for training video")
                return None, "Could not select a main player for training video", 400
        elif tipo_video == "juego":
            if len(players) < 4:
                logger.error(f"Video de juego debe contener al menos 4 jugadores, detectados: {len(players)}")
                return None, f"Video de juego debe contener al menos 4 jugadores, detectados: {len(players)}", 400
            if len(players) > 4:
                players = select_main_players(players, 4)
            if not player_identifier:
                logger.error("Debe especificar el jugador objetivo para videos de juego real")
                return None, "Debe especificar el jugador objetivo para videos de juego real", 400
            assigned_positions = assign_player_positions(players)
            if player_identifier not in assigned_positions:
                logger.error(f"Jugador objetivo '{player_identifier}' no encontrado")
                return None, f"Jugador objetivo '{player_identifier}' no encontrado", 400
            target_player = assigned_positions[player_identifier]
        else:
            logger.error(f"Tipo de video no válido: {tipo_video}. Debe ser 'entrenamiento' o 'juego'")
            return None, f"Tipo de video no válido: {tipo_video}. Debe ser 'entrenamiento' o 'juego'", 400

        if not context_detected:
            logger.error(f"No padel/tennis/sports context detected in video for stroke type {tipo_golpe}")
            return None, f"No padel/tennis/sports context detected in video for stroke type {tipo_golpe}", 400

        target_racket = find_closest_racket(target_player, rackets)
        if not target_racket:
            logger.warning(f"No racket detected for the target player in video for stroke type {tipo_golpe}. Proceeding with default values.")
        else:
            logger.info(f"Racket detected for the target player in video for stroke type {tipo_golpe}")

        return (target_player, rackets, result.annotation_results, video_duration, context_detected, avg_speed, shot_count), None, 200

    except Exception as e:
        logger.error(f"Error analyzing video for stroke type {tipo_golpe}: {str(e)}", exc_info=True)
        return None, f"Error analyzing video: {str(e)}", 500