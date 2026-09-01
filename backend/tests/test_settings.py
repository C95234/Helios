import importlib

from app import settings


def test_default_origins_include_local_dev():
    assert "http://localhost:5173" in settings.ALLOWED_ORIGINS


def test_allowed_origins_parses_env_var(monkeypatch):
    monkeypatch.setenv("HELIOS_ALLOWED_ORIGINS", "https://helios.example.com, https://www.helios.example.com")
    reloaded = importlib.reload(settings)
    assert reloaded.ALLOWED_ORIGINS == ["https://helios.example.com", "https://www.helios.example.com"]
    importlib.reload(settings)  # restaure l'etat par defaut pour les autres tests
