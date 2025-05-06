WEIGHTS = {
    "entrenamiento": {
        "TECNICA_WEIGHT": 0.7,
        "RITMO_WEIGHT": 0.15,
        "REPETICION_WEIGHT": 0.15
    },
    "juego": {
        "TECNICA_WEIGHT": 0.4,
        "COBERTURA_WEIGHT": 0.3,
        "RITMO_WEIGHT": 0.3
    }
}

GOLPE_FACTORS = {
    "practica": {"tecnica": 1.0, "ritmo": 1.0, "repeticion": 1.0, "fuerza": 1.0},
    "derecha": {"tecnica": 1.0, "cobertura": 1.1, "ritmo": 1.2, "fuerza": 1.2},
    "reves": {"tecnica": 1.0, "cobertura": 1.0, "ritmo": 1.1, "fuerza": 1.1},
    "volea": {"tecnica": 1.0, "cobertura": 1.0, "ritmo": 1.0, "fuerza": 1.0},
    "bandeja": {"tecnica": 1.0, "cobertura": 1.0, "ritmo": 1.0, "fuerza": 1.2},
    "smash": {"tecnica": 1.0, "cobertura": 1.0, "ritmo": 1.0, "fuerza": 1.5},
    "globo": {"tecnica": 1.0, "cobertura": 1.0, "ritmo": 1.0, "fuerza": 0.8},
    "saque": {"tecnica": 1.0, "cobertura": 1.0, "ritmo": 1.0, "fuerza": 1.3},
    "bandaPared": {"tecnica": 1.0, "cobertura": 1.0, "ritmo": 1.0, "fuerza": 1.0},
    "vibora": {"tecnica": 1.0, "cobertura": 1.0, "ritmo": 1.0, "fuerza": 1.2}
}