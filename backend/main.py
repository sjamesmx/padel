import logging
from flask import Flask
from routes.padel_iq import padel_iq_bp

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Starting main.py import process")

# Importar y registrar el blueprint para profile
logger.info("Attempting to import routes.profile")
try:
    from routes.profile import profile_bp
    logger.info("Successfully imported routes.profile")
except ImportError as e:
    logger.error(f"Error importing routes.profile: {e}")
    raise

# Importar y registrar el blueprint para padel_iq
logger.info("Attempting to import routes.padel_iq")
try:
    logger.info("Successfully imported routes.padel_iq")
except ImportError as e:
    logger.error(f"Error importing routes.padel_iq: {e}")
    raise

# Inicializar Firebase
logger.info("Attempting to import config.firebase")
try:
    from config.firebase import initialize_firebase
    initialize_firebase()
    logger.info("Successfully imported config.firebase")
except ImportError as e:
    logger.error(f"Error importing config.firebase: {e}")
    raise

# Configurar la aplicación Flask
logger.info("Starting Flask application")
app = Flask(__name__)

# Registrar blueprints
app.register_blueprint(padel_iq_bp)
app.register_blueprint(profile_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)