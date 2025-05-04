from flask import Flask
from flask_cors import CORS
import logging
import os

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Starting main.py import process")

try:
    logger.info("Attempting to import routes.profile")
    from routes.profile import get_profile
    logger.info("Successfully imported routes.profile")
except Exception as e:
    logger.error(f"Error importing routes.profile: {str(e)}", exc_info=True)
    raise

try:
    logger.info("Attempting to import routes.padel_iq")
    from routes.padel_iq import calculate_padel_iq
    logger.info("Successfully imported routes.padel_iq")
except Exception as e:
    logger.error(f"Error importing routes.padel_iq: {str(e)}", exc_info=True)
    raise

try:
    logger.info("Attempting to import config.firebase")
    from config.firebase import db, bucket
    logger.info("Successfully imported config.firebase")
except Exception as e:
    logger.error(f"Error importing config.firebase: {str(e)}", exc_info=True)
    raise

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
logger.info("Starting Flask application")

app.route('/api/get_profile', methods=['GET'])(get_profile)
app.route('/api/calculate_padel_iq', methods=['POST'])(calculate_padel_iq)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))