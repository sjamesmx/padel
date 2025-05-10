import requests
import logging
import json
from datetime import datetime
import os
import sys

# Agregar el directorio padre al path para poder importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from create_test_video import create_test_video
from init_test_db import init_test_data
from config.mock_firebase import client

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración
BASE_URL = 'http://localhost:8080'

def test_complete_flow():
    """Prueba el flujo completo del sistema."""
    try:
        # 1. Crear video de prueba
        logger.info("Creando video de prueba...")
        video_path = create_test_video()
        
        # 2. Inicializar datos de prueba en Firestore Mock
        logger.info("Inicializando datos de prueba...")
        test_data = init_test_data()
        user_id = test_data['user_id']
        
        # 3. Procesar video de entrenamiento
        logger.info("Procesando video de entrenamiento...")
        video_data = {
            'video_url': f'file://{os.path.abspath(video_path)}',
            'user_id': user_id,
            'tipo_video': 'entrenamiento'
        }
        
        response = requests.post(
            f'{BASE_URL}/process_training_video',
            json=video_data
        )
        
        if response.status_code != 200:
            logger.error(f"Error al procesar video: {response.text}")
            return
            
        process_result = response.json()
        analysis_id = process_result.get('analysis_id')
        logger.info(f"Video procesado. ID del análisis: {analysis_id}")
        
        # 4. Obtener detalles del análisis
        logger.info("Obteniendo detalles del análisis...")
        response = requests.get(f'{BASE_URL}/dashboard/get_analysis_details/{analysis_id}')
        if response.status_code == 200:
            analysis_details = response.json()
            logger.info("Detalles del análisis obtenidos exitosamente")
            logger.debug(json.dumps(analysis_details, indent=2))
        else:
            logger.error(f"Error al obtener detalles del análisis: {response.text}")
        
        # 5. Obtener estadísticas del usuario
        logger.info("Obteniendo estadísticas del usuario...")
        response = requests.get(f'{BASE_URL}/dashboard/get_user_analytics', params={'user_id': user_id})
        if response.status_code == 200:
            user_analytics = response.json()
            logger.info("Estadísticas del usuario obtenidas exitosamente")
            logger.debug(json.dumps(user_analytics, indent=2))
        else:
            logger.error(f"Error al obtener estadísticas del usuario: {response.text}")
        
        # 6. Limpiar archivos temporales
        if os.path.exists(video_path):
            os.remove(video_path)
            logger.info("Archivos temporales eliminados")
        
        return {
            'success': True,
            'user_id': user_id,
            'analysis_id': analysis_id,
            'video_path': video_path
        }
        
    except Exception as e:
        logger.error(f"Error durante la prueba del flujo: {str(e)}")
        raise e

if __name__ == '__main__':
    logger.info("Iniciando prueba del flujo completo...")
    result = test_complete_flow()
    if result and result.get('success'):
        logger.info("Prueba del flujo completada exitosamente")
        logger.info(f"Resultados: {json.dumps(result, indent=2)}")
    else:
        logger.error("La prueba del flujo falló") 