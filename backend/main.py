from flask import Flask
from flask_cors import CORS
from routes.profile import get_profile
from routes.padel_iq import calculate_padel_iq
# Eliminar: from routes.clubs import create_club, get_club
from config.firebase import db, bucket
import os

app = Flask(__name__)
CORS(app)

# Registrar rutas con prefijo /api/
app.route('/api/get_profile', methods=['GET'])(get_profile)
app.route('/api/calculate_padel_iq', methods=['POST'])(calculate_padel_iq)
# Eliminar: app.route('/api/clubs/create', methods=['POST'])(create_club)
# Eliminar: app.route('/api/clubs/<club_id>', methods=['GET'])(get_club)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))