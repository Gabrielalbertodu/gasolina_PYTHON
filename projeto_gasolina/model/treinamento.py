"""
model/treinamento.py

Treina um RandomForestClassifier com dados sintéticos (bootstrap).

Por que dados sintéticos?
- Não existem datasets históricos prontos com todas as variáveis combinadas.
- Os dados são gerados com regras econômicas reais:
    * Dólar alto + Petróleo alto + Risco alto → Alta
    * Dólar baixo + Petróleo baixo + Confiança alta → Queda
    * Demais casos → Estabilidade

O modelo aprende essas regras e generaliza para dados reais.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

# Nomes das colunas de features (devem coincidir com preprocessing/tratamento.py)
COLUNAS = [
    "dolar_reais",
    "brent_usd",
    "wti_usd",
    "petroleo_medio",
    "gasolina_reais",
    "risco_noticias",
    "confianca_noticias",
    "num_noticias",
]


def treinar_modelo() -> Pipeline:
    """
    Gera dados sintéticos e treina o pipeline de ML.

    Returns:
        Pipeline treinado: StandardScaler → RandomForestClassifier
    """
    rng = np.random.default_rng(42)
    n_amostras = 900

    dados = []
    labels = []

    for _ in range(n_amostras):
        # Simula valores típicos com variação aleatória
        dolar = rng.normal(5.20, 0.45)
        brent = rng.normal(82.0, 12.0)
        wti = rng.normal(78.0, 12.0)
        gasolina = rng.normal(6.15, 0.55)
        risco = float(np.clip(rng.normal(0.5, 1.0), 0, 2))
        confianca = float(np.clip(rng.normal(0.3, 0.8), 0, 2))
        num_noticias = int(rng.integers(5, 50))
        petroleo_medio = (brent + wti) / 2

        # Calcula "pressão" de alta no preço da gasolina
        # Valores mais altos de pressão → tendência de ALTA
        pressao = (
            0.45 * (dolar - 5.20) +          # dólar influencia fortemente
            0.35 * ((petroleo_medio - 80) / 10) +  # petróleo normalizado
            0.25 * risco +                    # risco geopolítico
            -0.15 * confianca                 # estabilidade reduz pressão
        )

        # Define o rótulo com base na pressão
        if pressao > 0.8:
            label = "Alta"
        elif pressao < -0.6:
            label = "Queda"
        else:
            label = "Estabilidade"

        dados.append([
            dolar, brent, wti, petroleo_medio, gasolina,
            risco, confianca, num_noticias
        ])
        labels.append(label)

    X = pd.DataFrame(dados, columns=COLUNAS)
    y = np.array(labels)

    # Pipeline: normaliza os dados e treina a Random Forest
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("classificador", RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
        )),
    ])

    pipeline.fit(X, y)
    return pipeline
