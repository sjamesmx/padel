import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# ---------- TESTS PARA /signup ----------
def test_signup_success(mocker):
    mock_db = mocker.Mock()
    mock_users = mocker.Mock()
    mock_query = mocker.Mock()
    mock_users.where.return_value = mock_query
    mock_query.get.return_value = []
    mock_user_ref = mocker.Mock()
    mock_users.document.return_value = mock_user_ref
    mock_db.collection.return_value = mock_users
    mocker.patch("app.services.firebase.get_firebase_client", return_value=mock_db)

    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "nivel": "intermedio",
        "posicion_preferida": "derecha"
    }
    response = client.post("/api/v1/auth/signup", json=user_data)
    assert response.status_code == 200
    assert response.json()["email"] == user_data["email"]

def test_signup_email_exists(mocker):
    mock_db = mocker.Mock()
    mock_users = mocker.Mock()
    mock_query = mocker.Mock()
    mock_users.where.return_value = mock_query
    mock_query.get.return_value = [mocker.Mock()]
    mock_db.collection.return_value = mock_users
    mocker.patch("app.services.firebase.get_firebase_client", return_value=mock_db)

    user_data = {
        "email": "exists@example.com",
        "name": "Test User",
        "nivel": "intermedio",
        "posicion_preferida": "derecha"
    }
    response = client.post("/api/v1/auth/signup", json=user_data)
    assert response.status_code == 400
    assert "ya está registrado" in response.text

def test_signup_db_error(mocker):
    mocker.patch("app.services.firebase.get_firebase_client", side_effect=Exception("DB error"))
    user_data = {
        "email": "fail@example.com",
        "name": "Test User",
        "nivel": "intermedio",
        "posicion_preferida": "derecha"
    }
    response = client.post("/api/v1/auth/signup", json=user_data)
    assert response.status_code == 500
    assert "Error al registrar usuario" in response.text

# ---------- TESTS PARA /login ----------
def test_login_success(mocker):
    mock_db = mocker.Mock()
    mock_users = mocker.Mock()
    mock_query = mocker.Mock()
    mock_users.where.return_value = mock_query
    mock_user_doc = mocker.Mock()
    mock_user_doc.to_dict.return_value = {
        "email": "login@example.com",
        "name": "Login User",
        "nivel": "avanzado",
        "posicion_preferida": "izquierda"
    }
    mock_query.get.return_value = [mock_user_doc]
    mock_db.collection.return_value = mock_users
    mocker.patch("app.services.firebase.get_firebase_client", return_value=mock_db)
    mocker.patch("app.core.security.create_access_token", return_value="fake-token")

    form_data = {
        "username": "login@example.com",
        "password": "anypass"
    }
    response = client.post("/api/v1/auth/login", data=form_data)
    assert response.status_code == 200
    assert response.json()["access_token"] == "fake-token"
    assert response.json()["token_type"] == "bearer"

def test_login_user_not_found(mocker):
    mock_db = mocker.Mock()
    mock_users = mocker.Mock()
    mock_query = mocker.Mock()
    mock_users.where.return_value = mock_query
    mock_query.get.return_value = []
    mock_db.collection.return_value = mock_users
    mocker.patch("app.services.firebase.get_firebase_client", return_value=mock_db)

    form_data = {
        "username": "notfound@example.com",
        "password": "anypass"
    }
    response = client.post("/api/v1/auth/login", data=form_data)
    assert response.status_code == 401
    assert "Credenciales incorrectas" in response.text

def test_login_db_error(mocker):
    mocker.patch("app.services.firebase.get_firebase_client", side_effect=Exception("DB error"))
    form_data = {
        "username": "fail@example.com",
        "password": "anypass"
    }
    response = client.post("/api/v1/auth/login", data=form_data)
    assert response.status_code == 500
    assert "Error al iniciar sesión" in response.text 