"""
data_collectors/gasolina.py

Coleta dados de preço de gasolina via CSV público da ANP.
"""

import requests
from io import StringIO
from typing import Optional, Dict, List
import pandas as pd

# URL do CSV de preços da ANP (Agência Nacional do Petróleo)
URL_ANP = (
    "https://www.gov.br/anp/pt-br/centrais-de-conteudo/dados-abertos/"
    "arquivos/shpc/qus/ultimas-4-semanas-gasolina-etanol.csv"
)


def _ler_csv_anp() -> pd.DataFrame:
    """Lê o CSV da ANP usando ponto e vírgula e retorna um DataFrame limpo."""
    response = requests.get(URL_ANP, timeout=20)
    response.raise_for_status()

    texto = response.content.decode("latin1")
    df = pd.read_csv(StringIO(texto), sep=";", encoding="latin1", dtype=str)
    df.columns = df.columns.str.strip().str.replace("\ufeff", "")
    return df


def _normalizar_preco(valor: str) -> Optional[float]:
    if pd.isna(valor) or valor is None:
        return None
    texto = str(valor).strip().replace(".", "").replace(",", ".")
    try:
        return float(texto)
    except ValueError:
        return None


def _filtrar_gasolina(df: pd.DataFrame) -> pd.DataFrame:
    if "Produto" not in df.columns or "Valor de Venda" not in df.columns:
        return pd.DataFrame()

    df = df[df["Produto"].str.contains("GASOLINA", case=False, na=False)].copy()
    df["Valor de Venda"] = df["Valor de Venda"].apply(_normalizar_preco)
    df["Data da Coleta"] = pd.to_datetime(df.get("Data da Coleta"), dayfirst=True, errors="coerce")
    return df.dropna(subset=["Valor de Venda", "Data da Coleta"])


def coletar_gasolina() -> Optional[Dict]:
    """
    Coleta preços de gasolina da ANP e calcula estatísticas.

    Returns:
        Dicionário com média, mínimo, máximo e total de amostras.
        Retorna None se a coleta falhar.
    """
    try:
        df = _ler_csv_anp()
        df = _filtrar_gasolina(df)

        if df.empty:
            return None

        precos = df["Valor de Venda"].astype(float).tolist()
        return {
            "gasolina_media": float(pd.Series(precos).mean()),
            "gasolina_min": float(pd.Series(precos).min()),
            "gasolina_max": float(pd.Series(precos).max()),
            "total_amostras": len(precos),
            "valores_de_venda": precos,
        }

    except Exception as e:
        print(f"[gasolina] Erro ao coletar ANP: {e}")
        return None


def coletar_gasolina_historico() -> Optional[List[Dict]]:
    """
    Coleta registros históricos de preços da ANP e retorna uma lista de dicionários
    com campos `data_hora` (datetime) e `gasolina` (float).
    """
    try:
        df = _ler_csv_anp()
        df = _filtrar_gasolina(df)

        if df.empty:
            return None

        registros = [
            {
                "data_hora": linha["Data da Coleta"],
                "gasolina": float(linha["Valor de Venda"]),
            }
            for _, linha in df.iterrows()
        ]

        return registros

    except Exception as e:
        print(f"[gasolina] Erro ao coletar histórico ANP: {e}")
        return None

