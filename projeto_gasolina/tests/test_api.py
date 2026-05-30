"""
tests/test_api.py

Testes unitários para a API FastAPI.

Execução:
    pytest tests/test_api.py -v
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from api.routes import criar_api


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def db_mock():
    """Mock do banco de dados para isolar os testes da API."""
    mock = MagicMock()

    # Previsão de exemplo
    mock.obter_ultima_previsao.return_value = {
        "id": 1,
        "data_hora": "2025-01-01T08:00:00",
        "previsao": "Alta",
        "probabilidade": 0.78,
        "explicacao": "Dólar elevado e petróleo caro.",
        "dolar": 5.50,
        "brent": 90.0,
        "wti": 85.0,
        "gasolina": 6.50,
        "risco": 1.2,
    }

    mock.obter_fontes.return_value = ["AwesomeAPI", "Yahoo Finance", "Google News", "ANP"]

    mock.obter_historico.return_value = [
        {
            "id": 1,
            "data_hora": "2025-01-01T08:00:00",
            "previsao": "Alta",
            "probabilidade": 0.78,
            "explicacao": "Teste",
        }
    ]

    return mock


@pytest.fixture
def predictor_mock():
    """Mock do predictor."""
    return MagicMock()


@pytest.fixture
def client(db_mock, predictor_mock):
    """Cliente de teste da API."""
    app = criar_api(db_mock, predictor_mock)
    return TestClient(app)


# ── Testes ────────────────────────────────────────────────────────────────────

def test_saude(client):
    """Verifica que o endpoint /saude retorna status ok."""
    response = client.get("/saude")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "timestamp" in response.json()


def test_previsao_retorna_dados(client):
    """Verifica estrutura da resposta do endpoint /previsao."""
    response = client.get("/previsao")
    assert response.status_code == 200

    data = response.json()
    assert "tendencia" in data
    assert "probabilidade" in data
    assert "fontes" in data
    assert "data_hora" in data
    assert data["tendencia"] in ("Alta", "Queda", "Estabilidade")
    assert 0.0 <= data["probabilidade"] <= 1.0


def test_previsao_sem_dados(db_mock, predictor_mock):
    """Verifica que retorna 404 quando não há previsão no banco."""
    db_mock.obter_ultima_previsao.return_value = None
    app = criar_api(db_mock, predictor_mock)
    client = TestClient(app)

    response = client.get("/previsao")
    assert response.status_code == 404


def test_historico_retorna_lista(client):
    """Verifica que /historico retorna uma lista."""
    response = client.get("/historico")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_historico_estrutura(client):
    """Verifica que cada item do histórico tem os campos esperados."""
    response = client.get("/historico")
    items = response.json()

    if items:
        item = items[0]
        assert "id" in item
        assert "data_hora" in item
        assert "tendencia" in item
        assert "probabilidade" in item
