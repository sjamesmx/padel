import pytest
import os
from app.services import firebase
import firebase_admin
from unittest.mock import MagicMock

def test_initialize_firebase_development(monkeypatch, mocker):
    monkeypatch.setenv("ENVIRONMENT", "development")
    mocker.patch("firebase_admin._apps", {})
    called = {}

    def mock_logger_info(msg):
        called["info"] = msg

    monkeypatch.setattr(firebase.logger, "info", mock_logger_info)
    firebase.initialize_firebase()
    assert "Using Firestore emulator" in called["info"]

def test_initialize_firebase_production(monkeypatch, mocker):
    monkeypatch.setenv("ENVIRONMENT", "production")
    mocker.patch("firebase_admin._apps", {})
    mock_cred = mocker.Mock()
    mocker.patch("app.core.config.settings.FIREBASE_CREDENTIALS", "fake_path.json")
    mocker.patch("firebase_admin.credentials.Certificate", return_value=mock_cred)
    mocker.patch("firebase_admin.initialize_app", return_value=None)
    called = {}

    def mock_logger_info(msg):
        called["info"] = msg

    monkeypatch.setattr(firebase.logger, "info", mock_logger_info)
    firebase.initialize_firebase()
    assert "Using Firestore emulator" in called["info"]

def test_initialize_firebase_exception(monkeypatch, mocker):
    monkeypatch.setenv("ENVIRONMENT", "production")
    mocker.patch("firebase_admin._apps", {})
    mocker.patch("app.core.config.settings.FIREBASE_CREDENTIALS", "fake_path.json")
    mocker.patch("firebase_admin.credentials.Certificate", side_effect=Exception("fail"))
    called = {}

    def mock_logger_error(msg):
        called["error"] = msg

    monkeypatch.setattr(firebase.logger, "error", mock_logger_error)
    with pytest.raises(Exception):
        firebase.initialize_firebase()
    assert "Error initializing Firebase" in called["error"]

def test_get_firebase_client_development(monkeypatch, mocker):
    monkeypatch.setenv("ENVIRONMENT", "development")
    mock_client = mocker.Mock()
    mocker.patch("firebase_admin.firestore.client", return_value=mock_client)
    client = firebase.get_firebase_client()
    assert client == mock_client

def test_get_firebase_client_production(monkeypatch, mocker):
    monkeypatch.setenv("ENVIRONMENT", "production")
    mock_firestore_client = mocker.Mock()
    mocker.patch("firebase_admin.firestore.client", return_value=mock_firestore_client)
    assert firebase.get_firebase_client() == mock_firestore_client

def test_get_firebase_client_exception(monkeypatch, mocker):
    monkeypatch.setenv("ENVIRONMENT", "production")
    mocker.patch("firebase_admin.firestore.client", side_effect=Exception("fail"))
    called = {}

    def mock_logger_error(msg):
        called["error"] = msg

    monkeypatch.setattr(firebase.logger, "error", mock_logger_error)
    with pytest.raises(Exception):
        firebase.get_firebase_client()
    assert "Error getting Firestore client" in called["error"] 