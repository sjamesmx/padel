import numpy as np

def calculate_padel_iq_granular(golpe):
    """Calcula scores granulares para un golpe y un Padel IQ combinado."""
    max_elbow_angle = golpe.get('max_elbow_angle', 0)
    max_wrist_speed = golpe.get('max_wrist_speed', 0)
    tipo = golpe.get('tipo', '')

    # Calcular score de técnica (basado en ángulo del codo y velocidad de muñeca)
    tecnica = min(100, max_elbow_angle / 180 * 50 + max_wrist_speed * 10)  # Normalizado a 100

    # Calcular score de fuerza (basado en velocidad de muñeca)
    fuerza = min(100, max_wrist_speed * 20)  # Normalizado a 100

    # Calcular score de ritmo (simulado, basado en velocidad relativa)
    ritmo = min(100, max_wrist_speed * 15)  # Normalizado a 100

    # Calcular score de repetición (simulado, basado en tipo de golpe)
    repeticion = 50  # Valor base; podría ajustarse con más datos

    # Combinar scores para el Padel IQ del golpe
    padel_iq = (tecnica * 0.4 + fuerza * 0.3 + ritmo * 0.2 + repeticion * 0.1)

    return {
        'tecnica': tecnica,
        'fuerza': fuerza,
        'ritmo': ritmo,
        'repeticion': repeticion,
        'padel_iq': padel_iq
    }