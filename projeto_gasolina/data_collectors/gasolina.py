"""
data_collectors/gasolina.py

Coleta dados de preço de gasolina via CSV público da ANP.
"""

import csv
import requests
from io import StringIO
from typing import Optional, Dict


# URL do CSV de preços da ANP (Agência Nacional do Petróleo)
URL_ANP = (
    "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/"
    "arquivos/shpc/qus/ultimas-4-semanas-gasolina-etanol.csv"
)


def coletar_gasolina() -> Optional[Dict]:
    """
    Coleta preços de gasolina da ANP e calcula estatísticas.

    Returns:
        Dicionário com média, mínimo, máximo e total de amostras.
        Retorna None se a coleta falhar.
    """
    try:
        response = requests.get(URL_ANP, timeout=15)
        response.raise_for_status()

        precos = _extrair_precos(response.text)

        if not precos:
            return None

        return {
            "gasolina_media": sum(precos) / len(precos),
            "gasolina_min": min(precos),
            "gasolina_max": max(precos),
            "total_amostras": len(precos),
        }

    except Exception as e:
        print(f"[gasolina] Erro ao coletar ANP: {e}")
        return None


def _extrair_precos(csv_texto: str) -> list:
    """Extrai lista de preços de venda do CSV da ANP."""
    precos = []

    try:
        reader = csv.DictReader(StringIO(csv_texto), delimiter=",")

        for linha in reader:
            # A ANP usa "Preço de Venda" como nome da coluna
            preco_str = linha.get("Preço de Venda") or linha.get("preco_venda")

            if preco_str:
                try:
                    preco = float(preco_str.replace(",", "."))
                    if preco > 0:
                        precos.append(preco)
                except ValueError:
                    continue

    except Exception as e:
        print(f"[gasolina] Erro no parse do CSV: {e}")

    return precos
