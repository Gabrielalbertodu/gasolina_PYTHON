"""
tests/test_model.py

Testes unitários para o modelo de Machine Learning.

Execução:
    pytest tests/test_model.py -v
"""

import pytest
import pandas as pd

from model.treinamento import treinar_modelo, COLUNAS
from model.previsao import PredisorGasolina
from preprocessing.tratamento import construir_features, analisar_sentimento


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def predictor():
    """Instância compartilhada do predictor para todos os testes."""
    return PredisorGasolina()


@pytest.fixture
def features_alta():
    """Features que representam cenário de ALTA pressão."""
    return construir_features(
        dolar=6.00,       # dólar alto
        brent=95.0,       # petróleo caro
        wti=90.0,
        gasolina=6.80,
        noticias=[
            {"titulo": "Guerra no Oriente Médio afeta fornecimento"},
            {"titulo": "Sanções econômicas ao petróleo"},
            {"titulo": "Embargo de petróleo aprovado"},
        ],
    )


@pytest.fixture
def features_neutras():
    """Features em valores neutros."""
    return construir_features(
        dolar=5.20,
        brent=82.0,
        wti=78.0,
        gasolina=6.15,
        noticias=[],
    )


# ── Testes do Treinamento ─────────────────────────────────────────────────────

def test_treinar_modelo_retorna_pipeline():
    """Verifica que treinar_modelo retorna um Pipeline válido."""
    from sklearn.pipeline import Pipeline
    modelo = treinar_modelo()
    assert isinstance(modelo, Pipeline)


def test_modelo_tem_classes_corretas():
    """Verifica que o modelo classifica exatamente 3 classes."""
    modelo = treinar_modelo()
    classes = set(modelo.named_steps["classificador"].classes_)
    assert classes == {"Alta", "Queda", "Estabilidade"}


def test_modelo_colunas():
    """Verifica que as colunas de entrada estão definidas corretamente."""
    assert "dolar_reais" in COLUNAS
    assert "brent_usd" in COLUNAS
    assert "risco_noticias" in COLUNAS
    assert len(COLUNAS) == 8


# ── Testes do Predictor ───────────────────────────────────────────────────────

def test_prever_retorna_estrutura(predictor, features_neutras):
    """Verifica a estrutura do resultado da previsão."""
    resultado = predictor.prever(features_neutras)

    assert "tendencia" in resultado
    assert "probabilidade" in resultado
    assert "probabilidades" in resultado
    assert "explicacao" in resultado


def test_tendencia_valida(predictor, features_neutras):
    """Verifica que a tendência é sempre um valor válido."""
    resultado = predictor.prever(features_neutras)
    assert resultado["tendencia"] in ("Alta", "Queda", "Estabilidade")


def test_probabilidade_valida(predictor, features_neutras):
    """Verifica que a probabilidade está entre 0 e 1."""
    resultado = predictor.prever(features_neutras)
    assert 0.0 <= resultado["probabilidade"] <= 1.0


def test_todas_probabilidades_somam_um(predictor, features_neutras):
    """Verifica que as probabilidades de todas as classes somam 1.0."""
    resultado = predictor.prever(features_neutras)
    total = sum(resultado["probabilidades"].values())
    assert abs(total - 1.0) < 0.001


def test_explicacao_nao_vazia(predictor, features_neutras):
    """Verifica que a explicação é uma string não vazia."""
    resultado = predictor.prever(features_neutras)
    assert isinstance(resultado["explicacao"], str)
    assert len(resultado["explicacao"]) > 10


# ── Testes do Pré-processamento ───────────────────────────────────────────────

def test_sentimento_noticias_vazias():
    """Notícias vazias devem retornar score zero."""
    risco, confianca = analisar_sentimento([])
    assert risco == 0.0
    assert confianca == 0.0


def test_sentimento_detecta_risco():
    """Notícias com palavras de risco devem gerar score > 0."""
    noticias = [
        {"titulo": "Guerra no Oriente Médio"},
        {"titulo": "Embargo de petróleo anunciado"},
    ]
    risco, _ = analisar_sentimento(noticias)
    assert risco > 0


def test_sentimento_detecta_confianca():
    """Notícias com palavras de estabilidade devem gerar confiança > 0."""
    noticias = [
        {"titulo": "Acordo de paz firmado entre países"},
        {"titulo": "Mercado estável após negociação"},
    ]
    _, confianca = analisar_sentimento(noticias)
    assert confianca > 0


def test_construir_features_shape(features_neutras):
    """Verifica que features têm a forma correta para o modelo."""
    assert features_neutras.shape == (1, 8)
    assert list(features_neutras.columns) == COLUNAS
