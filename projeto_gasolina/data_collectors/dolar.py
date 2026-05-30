"""
data_collectors/dolar.py

Coleta a cotação do dólar (USD/BRL) via AwesomeAPI.
"""

import requests
from typing import Optional


def coletar_dolar() -> Optional[float]:
    """
    Retorna a cotação atual do dólar em reais.

    Returns:
        Valor do dólar (ex: 5.20) ou None se falhar.
    """
    try:
        url = "https://economia.awesomeapi.com.br/json/last/USD-BRL"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return float(data["USDBRL"]["bid"])
    except Exception as e:
        print(f"[dolar] Erro ao coletar cotação: {e}")
        return None
