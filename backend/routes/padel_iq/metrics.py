import logging
import math
import statistics

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def normalize_metric(value, min_val=0, max_val=100):
    """Normaliza un valor entre un rango mínimo y máximo."""
    if max_val == min_val:
        return 0
    return min(max_val, max(min_val, ((value - min_val) / (max_val - min_val)) * 100))

def calculate_tecnica(player, tipo_golpe, context_detected, golpe_factors, ritmo, avg_speed):
    """Calcula la métrica de técnica basada en los datos del jugador y MediaPipe."""
    tecnica_raw = 0
    positions = []
    for frame in player.frames:
        if hasattr(frame.normalized_bounding_box, 'left'):
            x = (frame.normalized_bounding_box.left + frame.normalized_bounding_box.right) / 2
            y = (frame.normalized_bounding_box.top + frame.normalized_bounding_box.bottom) / 2
            positions.append((x, y))
        else:
            logger.warning("Frame lacks bounding box data for technique calculation")

    if len(positions) > 1:
        x_coords = [pos[0] for pos in positions]
        y_coords = [pos[1] for pos in positions]
        x_variance = statistics.variance(x_coords) if len(x_coords) > 1 else 0
        y_variance = statistics.variance(y_coords) if len(y_coords) > 1 else 0
        total_variance = (x_variance + y_variance) / 2
        tecnica_raw = min(50, total_variance * 500)

    tecnica = normalize_metric(tecnica_raw, 0, 50)
    tecnica *= golpe_factors[tipo_golpe]["tecnica"]

    tecnica += normalize_metric(avg_speed, 0, 10) * 0.5
    tecnica = min(100, tecnica + (ritmo * 1.5))

    if context_detected:
        tecnica += 5
        tecnica = min(tecnica, 100)
        logger.info(f"Adjusted tecnica with context: {tecnica}")

    return tecnica

def adjust_tecnica(tecnica, video_type, repeticion, ritmo):
    """Ajusta la técnica según el tipo de video, repetición y ritmo."""
    return tecnica

def calculate_coverage(player, tipo_golpe, golpe_factors, video_duration, avg_speed):
    """Calcula la métrica de cobertura basada en el movimiento detectado."""
    total_distance = 0
    positions = []
    timestamps = []
    for frame in player.frames:
        if hasattr(frame.normalized_bounding_box, 'left') and hasattr(frame.normalized_bounding_box, 'right'):
            x = (frame.normalized_bounding_box.left + frame.normalized_bounding_box.right) / 2
            y = (frame.normalized_bounding_box.top + frame.normalized_bounding_box.bottom) / 2
            positions.append((x, y))
            timestamps.append(frame.time_offset.seconds + frame.time_offset.microseconds / 1e6)

    for i in range(1, len(positions)):
        x1, y1 = positions[i-1]
        x2, y2 = positions[i]
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        total_distance += distance

    speed = total_distance / video_duration if video_duration > 0 else 0
    coverage = normalize_metric(speed, 0, 0.05)
    coverage += normalize_metric(avg_speed, 0, 10) * 20
    coverage *= golpe_factors[tipo_golpe]["cobertura"]
    return min(coverage, 100)

def calculate_ritmo(annotation_results, video_duration, tipo_golpe, golpe_factors, shot_count):
    """Calcula la métrica de ritmo basada en las anotaciones, duración del video y OpenCV."""
    if video_duration <= 0:
        return 0
    # Usar shot_count directamente
    total_shot_count = shot_count
    ritmo_raw = total_shot_count / video_duration
    # Ajustar max_val basado en la duración del video (esperamos 1 golpe cada 10 segundos)
    max_val = video_duration / 10
    ritmo = normalize_metric(ritmo_raw, 0, max_val)
    ritmo *= golpe_factors[tipo_golpe]["ritmo"]
    return min(ritmo, 100)

def calculate_repeticion(player, annotation_results, tipo_golpe, golpe_factors, shot_count):
    """Calcula la métrica de repetición para videos de entrenamiento."""
    if not player.frames or len(player.frames) == 0:
        return 0
    # Usar shot_count directamente
    total_shot_count = shot_count
    repeticion_raw = total_shot_count / len(player.frames) if len(player.frames) > 0 else 0
    repeticion = normalize_metric(repeticion_raw * 100, 0, 2)  # Ajustar max_val para un rango más realista
    repeticion *= golpe_factors[tipo_golpe]["repeticion"]
    return min(repeticion, 100)

def calculate_fuerza(avg_speed, tipo_golpe, golpe_factors):
    """Calcula la métrica de fuerza basada en la velocidad del movimiento de la raqueta."""
    fuerza_raw = avg_speed * 1.2
    fuerza = normalize_metric(fuerza_raw, 0, 10)
    fuerza *= golpe_factors[tipo_golpe].get("fuerza", 1.0)
    return min(fuerza, 100)

def determine_player_level(padel_iq):
    """Determina el nivel del jugador basado en el Padel IQ."""
    if padel_iq >= 80:
        return "Avanzado"
    elif padel_iq >= 60:
        return "Intermedio"
    elif padel_iq >= 40:
        return "Principiante Avanzado"
    else:
        return "Principiante"

def determine_force_category(force_level):
    """Clasifica al jugador en una categoría de fuerza según el force_level."""
    if force_level >= 80:
        return "primera_fuerza"
    elif force_level >= 60:
        return "segunda_fuerza"
    elif force_level >= 40:
        return "tercera_fuerza"
    elif force_level >= 20:
        return "cuarta_fuerza"
    else:
        return "quinta_fuerza"