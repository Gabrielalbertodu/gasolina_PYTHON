"""
data_collectors/petroleo.py

Coleta preços do petróleo Brent e WTI via Yahoo Finance.
"""

import requests
from typing import Optional, Tuple


def coletar_petroleo() -> Optional[Tuple[float, float]]:
    """
    Retorna os preços do Brent e WTI em dólares.

    Returns:
        Tupla (brent_usd, wti_usd) ou None se falhar.
    """
    try:
        brent = _buscar_preco("BZ=F", "Brent")
        wti = _buscar_preco("CL=F", "WTI")

        if brent and wti:
            return (brent, wti)

        return None

    except Exception as e:
        print(f"[petroleo] Erro geral: {e}")
        return None


def _buscar_preco(simbolo: str, nome: str) -> Optional[float]:
    """Busca preço de fechamento recente de um símbolo no Yahoo Finance."""
    try:
        url = (
            f"https://query1.finance.yahoo.com/v8/finance/chart/"
            f"{simbolo}?range=5d&interval=1d"
        )
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        fechamentos = (
            data["chart"]["result"][0]["indicators"]["quote"][0]["close"]
        )
        validos = [c for c in fechamentos if c is not None]

        if validos:
            return float(validos[-1])

        return None

    except Exception as e:
        print(f"[petroleo] Erro ao buscar {nome}: {e}")
        return None
