from flask import jsonify, request
from config.firebase import db
from utils.video_analysis import analyze_video, calculate_padel_iq

def calculate_padel_iq():
    data = request.json
    user_id = data['user_id']
    videos = data['videos']

    # Analizar cada video
    metrics = {}
    for stroke, url in videos.items():
        metrics[stroke] = analyze_video(url, stroke)

    # Calcular Padel IQ y clasificar
    padel_iq, fuerza, aggregated_metrics = calculate_padel_iq(metrics)

    # Guardar resultados en Firestore
    doc_ref = db.collection("profiles").document(user_id)
    doc_ref.update({
        "padel_iq": padel_iq,
        "fuerza": fuerza,
        "metrics": aggregated_metrics
    })

    return jsonify({"padel_iq": padel_iq, "fuerza": fuerza, "metrics": aggregated_metrics}), 200