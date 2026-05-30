"""
preprocessing/tratamento.py

Transforma os dados coletados em features (variáveis) para o modelo de ML.

A principal tarefa é:
1. Analisar o sentimento das notícias (palavras de risco vs. estabilidade)
2. Combinar todos os indicadores em um DataFrame pronto para o modelo
"""

import pandas as pd
from typing import List, Dict, Tuple


# Palavras que indicam RISCO (tendem a elevar o preço)
PALAVRAS_RISCO = {
    "guerra": 2.0,
    "war": 2.0,
    "sancao": 2.0,
    "sançao": 2.0,
    "sanctions": 2.0,
    "embargo": 2.0,
    "conflito": 1.5,
    "conflict": 1.5,
    "crise": 1.5,
    "crisis": 1.5,
    "tensao": 1.0,
    "instabilidade": 1.0,
}

# Palavras que indicam ESTABILIDADE (tendem a reduzir o preço)
PALAVRAS_CONFIANCA = {
    "acordo": 1.0,
    "agreement": 1.0,
    "deal": 1.0,
    "diplomacia": 1.0,
    "negociacao": 1.0,
    "estavel": 1.0,
    "stable": 1.0,
    "estabilidade": 1.5,
    "stability": 1.5,
}


def analisar_sentimento(noticias: List[Dict]) -> Tuple[float, float]:
    """
    Analisa o sentimento das notícias.

    Para cada notícia, verifica quais palavras-chave de risco ou
    estabilidade aparecem no título e acumula os pesos.

    Args:
        noticias: Lista de dicts com chave 'titulo'.

    Returns:
        Tupla (score_risco, score_confianca), ambos entre 0 e 2.
    """
    risco_total = 0.0
    confianca_total = 0.0

    for noticia in noticias:
        titulo = noticia.get("titulo", "").lower()
        # Remover acentos simples para aumentar cobertura
        titulo = _remover_acentos(titulo)

        for palavra, peso in PALAVRAS_RISCO.items():
            if palavra in titulo:
                risco_total += peso

        for palavra, peso in PALAVRAS_CONFIANCA.items():
            if palavra in titulo:
                confianca_total += peso

    # Normaliza pelo número de notícias para evitar inflação
    n = max(1, len(noticias))
    score_risco = min(2.0, risco_total / n)
    score_confianca = min(2.0, confianca_total / n)

    return score_risco, score_confianca


def construir_features(
    dolar: float,
    brent: float,
    wti: float,
    gasolina: float,
    noticias: List[Dict],
) -> pd.DataFrame:
    """
    Cria o DataFrame de features que o modelo receberá.

    Features geradas:
    - dolar_reais: cotação USD/BRL
    - brent_usd: preço do Brent em dólares
    - wti_usd: preço do WTI em dólares
    - petroleo_medio: média entre Brent e WTI
    - gasolina_reais: preço médio da gasolina no Brasil
    - risco_noticias: score de risco geopolítico (0 a 2)
    - confianca_noticias: score de estabilidade (0 a 2)
    - num_noticias: quantidade de notícias coletadas

    Args:
        dolar: Cotação USD/BRL
        brent: Preço Brent em USD
        wti: Preço WTI em USD
        gasolina: Preço médio da gasolina em R$
        noticias: Lista de notícias coletadas

    Returns:
        DataFrame com uma linha (pronto para model.predict)
    """
    risco, confianca = analisar_sentimento(noticias)

    features = {
        "dolar_reais": dolar,
        "brent_usd": brent,
        "wti_usd": wti,
        "petroleo_medio": (brent + wti) / 2,
        "gasolina_reais": gasolina,
        "risco_noticias": risco,
        "confianca_noticias": confianca,
        "num_noticias": len(noticias),
    }

    return pd.DataFrame([features])


def _remover_acentos(texto: str) -> str:
    """Remove acentos comuns para facilitar a busca de palavras-chave."""
    substituicoes = {
        "ã": "a", "á": "a", "â": "a", "à": "a",
        "é": "e", "ê": "e", "è": "e",
        "í": "i", "î": "i",
        "ó": "o", "ô": "o", "õ": "o",
        "ú": "u", "û": "u",
        "ç": "c",
    }
    for original, substituto in substituicoes.items():
        texto = texto.replace(original, substituto)
    return texto
