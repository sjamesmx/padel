from flask import Flask
from flask_cors import CORS
from routes.profile import create_profile, get_profile
from routes.padel_iq import calculate_padel_iq
from config.firebase import db, bucket
import os

app = Flask(__name__)
CORS(app)

# Registrar rutas
app.route('/create_profile', methods=['POST'])(create_profile)
app.route('/get_profile', methods=['GET'])(get_profile)
app.route('/calculate_padel_iq', methods=['POST'])(calculate_padel_iq)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))