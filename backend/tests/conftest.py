"""
Configuración de pytest para Padelyzer.
"""
import os
import sys
import pytest
from firebase_admin import firestore, initialize_app, delete_app, _apps
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import MagicMock, patch

# Agregar el directorio backend al PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture(scope="session", autouse=True)
def mock_firebase():
    """Mock Firebase for tests."""
    with patch('firebase_admin.initialize_app') as mock_init, \
         patch('firebase_admin.firestore.client') as mock_client:
        
        # Create a mock Firestore client
        mock_db = MagicMock()
        mock_client.return_value = mock_db
        
        # Mock collection operations
        mock_collection = MagicMock()
        mock_db.collection.return_value = mock_collection
        mock_collection.stream.return_value = []
        
        yield mock_db

@pytest.fixture(autouse=True)
def setup_and_teardown(mock_firebase):
    """Fixture para limpiar datos antes y después de cada prueba."""
    # Clear all collections before each test
    collections = ['users', 'videos', 'analysis']
    for collection in collections:
        mock_firebase.collection(collection).stream.return_value = []
    
    yield
    
    # Clear all collections after each test
    for collection in collections:
        mock_firebase.collection(collection).stream.return_value = []

@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app) 