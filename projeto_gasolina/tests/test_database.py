"""
tests/test_database.py

Testes unitários para o banco de dados SQLite.

Usa um banco temporário (em memória) para não interferir no banco real.

Execução:
    pytest tests/test_database.py -v
"""

import pytest
from pathlib import Path
import tempfile

from database.database import Database


# ── Fixture ───────────────────────────────────────────────────────────────────

@pytest.fixture
def db_temp():
    """Cria um banco de dados temporário para cada teste."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        caminho = Path(tmp_dir) / "test.sqlite3"
        yield Database(caminho=caminho)


@pytest.fixture
def previsao_exemplo():
    """Dados de uma previsão de exemplo."""
    return {
        "previsao": "Alta",
        "probabilidade": 0.78,
        "explicacao": "Dólar elevado e petróleo caro.",
        "indicadores": {
            "dolar": 5.50,
            "brent": 90.0,
            "wti": 85.0,
            "gasolina": 6.50,
            "risco": 1.2,
        },
        "fontes": ["AwesomeAPI", "Yahoo Finance", "Google News", "ANP"],
    }


# ── Testes ────────────────────────────────────────────────────────────────────

def test_banco_inicia_vazio(db_temp):
    """Banco novo deve não ter previsões."""
    assert db_temp.obter_ultima_previsao() is None
    assert db_temp.obter_historico() == []


def test_salvar_previsao_retorna_id(db_temp, previsao_exemplo):
    """Salvar previsão deve retornar um ID inteiro."""
    pid = db_temp.salvar_previsao(**previsao_exemplo)
    assert isinstance(pid, int)
    assert pid > 0


def test_obter_ultima_previsao(db_temp, previsao_exemplo):
    """Deve retornar a previsão recém-inserida."""
    db_temp.salvar_previsao(**previsao_exemplo)
    ultima = db_temp.obter_ultima_previsao()

    assert ultima is not None
    assert ultima["previsao"] == "Alta"
    assert abs(ultima["probabilidade"] - 0.78) < 0.001


def test_historico_aumenta(db_temp, previsao_exemplo):
    """Histórico deve crescer com cada inserção."""
    db_temp.salvar_previsao(**previsao_exemplo)
    db_temp.salvar_previsao(**previsao_exemplo)

    historico = db_temp.obter_historico()
    assert len(historico) == 2


def test_historico_limite(db_temp, previsao_exemplo):
    """O parâmetro limite deve ser respeitado."""
    for _ in range(5):
        db_temp.salvar_previsao(**previsao_exemplo)

    historico = db_temp.obter_historico(limite=3)
    assert len(historico) == 3


def test_fontes_salvas(db_temp, previsao_exemplo):
    """As fontes devem ser salvas corretamente."""
    pid = db_temp.salvar_previsao(**previsao_exemplo)
    fontes = db_temp.obter_fontes(pid)

    assert len(fontes) == 4
    assert "AwesomeAPI" in fontes


def test_tendencias_validas(db_temp):
    """Apenas tendências válidas devem ser aceitas pelo banco."""
    dados_base = {
        "probabilidade": 0.60,
        "explicacao": "Teste",
        "indicadores": {},
        "fontes": [],
    }

    # Valores válidos
    for tendencia in ("Alta", "Queda", "Estabilidade"):
        pid = db_temp.salvar_previsao(previsao=tendencia, **dados_base)
        assert pid > 0

    # Valor inválido deve gerar exceção
    with pytest.raises(Exception):
        db_temp.salvar_previsao(previsao="Invalido", **dados_base)


def test_historico_ordem_decrescente(db_temp):
    """O histórico deve ser retornado do mais recente para o mais antigo."""
    import time

    for valor in ["Alta", "Queda", "Estabilidade"]:
        db_temp.salvar_previsao(
            previsao=valor,
            probabilidade=0.70,
            explicacao="Teste",
            indicadores={},
            fontes=[],
        )
        time.sleep(0.01)  # Garante diferença de timestamp

    historico = db_temp.obter_historico()
    assert historico[0]["previsao"] == "Estabilidade"  # Último inserido primeiro
