import logging
from flask import Blueprint, request, jsonify
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from services.notification_service import send_notification

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

matchmaking_bp = Blueprint('matchmaking', __name__)

# Firestore client
db = firestore.client()

def calculate_distance(loc1, loc2):
    """Calcula la distancia aproximada entre dos ubicaciones (latitud, longitud)."""
    if not loc1 or not loc2 or 'latitude' not in loc1 or 'longitude' not in loc1 or 'latitude' not in loc2 or 'longitude' not in loc2:
        return float('inf')
    lat1, lon1 = loc1['latitude'], loc1['longitude']
    lat2, lon2 = loc2['latitude'], loc2['longitude']
    # Fórmula simplificada para distancia (aproximada, sin usar haversine)
    distance = ((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2) ** 0.5
    return distance

@matchmaking_bp.route('/api/matchmaking/find_matches', methods=['POST'])
def find_matches():
    """Encuentra jugadores compatibles para un partido."""
    data = request.get_json()
    user_id = data.get('user_id')
    max_distance = data.get('max_distance', 10.0)

    if not user_id:
        return jsonify({'error': 'Falta user_id'}), 400

    # Obtener datos del usuario
    user_ref = db.collection('users').document(user_id)
    user = user_ref.get()
    if not user.exists:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    user_data = user.to_dict()

    padel_iq = user_data.get('padel_iq')
    if padel_iq is None:
        return jsonify({'error': 'El usuario no tiene Padel IQ asignado'}), 400

    user_clubs = user_data.get('clubs', [])
    user_availability = user_data.get('availability', [])
    user_location = user_data.get('location', {})

    # Normalizar clubes y horarios (eliminar espacios y convertir a minúsculas)
    user_clubs = [club.strip().lower() for club in user_clubs]
    user_availability = [avail.strip().lower() for avail in user_availability]

    logger.info(f"Usuario {user_id}: Padel IQ={padel_iq}, Clubes={user_clubs}, Disponibilidad={user_availability}, Ubicación={user_location}")

    # Buscar usuarios compatibles
    users = db.collection('users').where(filter=FieldFilter('onboarding_status', '==', 'completed')).get()
    compatible_users = []

    for other_user in users:
        if other_user.id == user_id:
            continue

        other_data = other_user.to_dict()
        other_padel_iq = other_data.get('padel_iq')
        if other_padel_iq is None:
            logger.debug(f"Usuario {other_user.id} descartado: Sin Padel IQ")
            continue

        # Criterio 1: Padel IQ similar (±5 puntos)
        padel_iq_diff = abs(padel_iq - other_padel_iq)
        if padel_iq_diff > 5:
            logger.debug(f"Usuario {other_user.id} descartado: Diferencia de Padel IQ ({padel_iq_diff}) > 5")
            continue

        # Criterio 2: Mismo club de preferencia
        other_clubs = other_data.get('clubs', [])
        other_clubs = [club.strip().lower() for club in other_clubs]
        common_clubs = set(user_clubs).intersection(other_clubs)
        if not common_clubs:
            logger.debug(f"Usuario {other_user.id} descartado: Sin clubes comunes (Clubes: {other_clubs})")
            continue

        # Criterio 3: Horarios compatibles
        other_availability = other_data.get('availability', [])
        other_availability = [avail.strip().lower() for avail in other_availability]
        common_availability = set(user_availability).intersection(other_availability)
        if not common_availability:
            logger.debug(f"Usuario {other_user.id} descartado: Sin horarios comunes (Disponibilidad: {other_availability})")
            continue

        # Criterio 4: Proximidad geográfica
        other_location = other_data.get('location', {})
        distance = calculate_distance(user_location, other_location)
        if distance > max_distance:
            logger.debug(f"Usuario {other_user.id} descartado: Distancia ({distance}) > {max_distance}")
            continue

        compatible_users.append({
            'user_id': other_user.id,
            'padel_iq': other_padel_iq,
            'clubs': list(common_clubs),
            'availability': list(common_availability),
            'distance': distance
        })
        logger.debug(f"Usuario {other_user.id} compatible: Padel IQ={other_padel_iq}, Clubes={list(common_clubs)}, Disponibilidad={list(common_availability)}, Distancia={distance}")

    compatible_users.sort(key=lambda x: abs(x['padel_iq'] - padel_iq))
    logger.info(f"Encontrados {len(compatible_users)} usuarios compatibles para {user_id}")
    return jsonify({'compatible_users': compatible_users}), 200

@matchmaking_bp.route('/api/matchmaking/send_request', methods=['POST'])
def send_request():
    """Envía una solicitud de partido a otro usuario."""
    data = request.get_json()
    user_id = data.get('user_id')
    target_user_id = data.get('target_user_id')
    club = data.get('club')
    schedule = data.get('schedule')

    if not user_id or not target_user_id or not club or not schedule:
        return jsonify({'error': 'Faltan datos requeridos (user_id, target_user_id, club, schedule)'}), 400

    user_ref = db.collection('users').document(user_id)
    user = user_ref.get()
    if not user.exists:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    target_user_ref = db.collection('users').document(target_user_id)
    target_user = target_user_ref.get()
    if not target_user.exists:
        return jsonify({'error': 'Usuario objetivo no encontrado'}), 404

    match_request_ref = db.collection('match_requests').document()
    match_request_ref.set({
        'from_user_id': user_id,
        'to_user_id': target_user_id,
        'club': club,
        'schedule': schedule,
        'status': 'pending',
        'timestamp': firestore.SERVER_TIMESTAMP
    })

    send_notification(target_user_id, f"Tienes una nueva solicitud de partido de {user_id} para el {schedule} en {club}. ¿Aceptas?")

    logger.info(f"Solicitud de partido enviada de {user_id} a {target_user_id}")
    return jsonify({'message': 'Solicitud de partido enviada exitosamente'}), 200

@matchmaking_bp.route('/api/matchmaking/respond_request', methods=['POST'])
def respond_request():
    """Responde a una solicitud de partido (aceptar o rechazar)."""
    data = request.get_json()
    user_id = data.get('user_id')
    request_id = data.get('request_id')
    response = data.get('response')

    if not user_id or not request_id or not response:
        return jsonify({'error': 'Faltan datos requeridos (user_id, request_id, response)'}), 400

    if response not in ['accept', 'reject']:
        return jsonify({'error': 'Respuesta no válida (debe ser "accept" o "reject")'}), 400

    request_ref = db.collection('match_requests').document(request_id)
    request_doc = request_ref.get()
    if not request_doc.exists:
        return jsonify({'error': 'Solicitud no encontrada'}), 404

    request_data = request_doc.to_dict()
    if request_data['to_user_id'] != user_id:
        return jsonify({'error': 'No tienes permiso para responder a esta solicitud'}), 403

    if request_data['status'] != 'pending':
        return jsonify({'error': 'Esta solicitud ya ha sido respondida'}), 400

    request_ref.update({'status': response})

    from_user_id = request_data['from_user_id']
    club = request_data['club']
    schedule = request_data['schedule']
    if response == 'accept':
        send_notification(from_user_id, f"{user_id} ha aceptado tu solicitud de partido para el {schedule} en {club}.")
        match_ref = db.collection('matches').document()
        match_ref.set({
            'user1_id': from_user_id,
            'user2_id': user_id,
            'club': club,
            'schedule': schedule,
            'timestamp': firestore.SERVER_TIMESTAMP
        })
    else:
        send_notification(from_user_id, f"{user_id} ha rechazado tu solicitud de partido para el {schedule} en {club}.")

    logger.info(f"Solicitud {request_id} respondida por {user_id}: {response}")
    return jsonify({'message': f"Solicitud {response} exitosamente"}), 200

@matchmaking_bp.route('/api/matchmaking/get_requests', methods=['GET'])
def get_requests():
    """Obtiene las solicitudes de partido pendientes para un usuario."""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'Falta user_id'}), 400

    requests = db.collection('match_requests').where(filter=FieldFilter('to_user_id', '==', user_id)).where(filter=FieldFilter('status', '==', 'pending')).get()
    pending_requests = []

    for req in requests:
        req_data = req.to_dict()
        pending_requests.append({
            'request_id': req.id,
            'from_user_id': req_data['from_user_id'],
            'club': req_data['club'],
            'schedule': req_data['schedule'],
            'timestamp': req_data.get('timestamp')
        })

    logger.info(f"Obtenidas {len(pending_requests)} solicitudes pendientes para {user_id}")
    return jsonify({'pending_requests': pending_requests}), 200