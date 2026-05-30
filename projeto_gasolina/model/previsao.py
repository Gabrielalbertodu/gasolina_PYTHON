"""
model/previsao.py

Classe responsável por realizar previsões de tendência.

Usa o pipeline treinado em model/treinamento.py para classificar
os dados em: Alta, Queda ou Estabilidade.
"""

import pandas as pd
from typing import Dict

from model.treinamento import treinar_modelo


class PredisorGasolina:
    """Realiza previsões de tendência de preço de gasolina."""

    def __init__(self):
        """Treina o modelo na inicialização."""
        print("[modelo] Treinando modelo...")
        self.modelo = treinar_modelo()
        self.classes = self.modelo.named_steps["classificador"].classes_
        print(f"[modelo] Pronto. Classes: {list(self.classes)}")

    def prever(self, features: pd.DataFrame) -> Dict:
        """
        Realiza a previsão de tendência.

        Args:
            features: DataFrame com as colunas geradas em preprocessing/tratamento.py

        Returns:
            Dicionário com:
            - tendencia: 'Alta', 'Queda' ou 'Estabilidade'
            - probabilidade: confiança da previsão (0.0 a 1.0)
            - probabilidades: dict com probabilidade de cada classe
            - explicacao: texto explicativo para o usuário
        """
        tendencia = self.modelo.predict(features)[0]
        probs_array = self.modelo.predict_proba(features)[0]

        # Mapeia classe → probabilidade
        probabilidades = {
            classe: float(prob)
            for classe, prob in zip(self.classes, probs_array)
        }

        confianca = probabilidades[tendencia]
        explicacao = self._gerar_explicacao(features.iloc[0], tendencia, confianca)

        return {
            "tendencia": tendencia,
            "probabilidade": confianca,
            "probabilidades": probabilidades,
            "explicacao": explicacao,
        }

    def _gerar_explicacao(
        self, features: pd.Series, tendencia: str, confianca: float
    ) -> str:
        """Gera uma explicação em texto baseada nos valores das features."""
        dolar = features.get("dolar_reais", 0)
        petroleo = features.get("petroleo_medio", 0)
        risco = features.get("risco_noticias", 0)

        fatores = []

        if dolar > 5.5:
            fatores.append(f"dólar elevado (R$ {dolar:.2f})")
        elif dolar < 4.9:
            fatores.append(f"dólar baixo (R$ {dolar:.2f})")

        if petroleo > 85:
            fatores.append(f"petróleo caro (US$ {petroleo:.1f})")
        elif petroleo < 75:
            fatores.append(f"petróleo barato (US$ {petroleo:.1f})")

        if risco > 1.0:
            fatores.append("risco geopolítico elevado nas notícias")
        elif risco < 0.2:
            fatores.append("cenário geopolítico estável nas notícias")

        texto_fatores = ", ".join(fatores) if fatores else "indicadores em níveis neutros"

        return (
            f"Tendência de {tendencia.upper()} com confiança de {confianca:.0%}. "
            f"Fatores: {texto_fatores}."
        )
