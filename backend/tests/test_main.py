import pytest
import sys
import os

# Añade el directorio backend al PATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_create_profile(client):
    response = client.post('/create_profile', json={
        'user_id': 'test123',
        'name': 'Test User',
        'email': 'test@example.com',
        'level': 'beginner',
        'location': 'Puebla'
    })
    assert response.status_code == 200
    assert response.json['message'] == 'Perfil creado'

def test_get_profile(client):
    client.post('/create_profile', json={
        'user_id': 'test123',
        'name': 'Test User',
        'email': 'test@example.com'
    })
    response = client.get('/get_profile?user_id=test123')
    assert response.status_code == 200
    assert response.json['email'] == 'test@example.com'