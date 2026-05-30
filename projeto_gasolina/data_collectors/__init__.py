"""
data_collectors/__init__.py

Expõe as funções de coleta para facilitar importações.
"""

from data_collectors.noticias import coletar_noticias
from data_collectors.dolar import coletar_dolar
from data_collectors.petroleo import coletar_petroleo
from data_collectors.gasolina import coletar_gasolina

__all__ = [
    "coletar_noticias",
    "coletar_dolar",
    "coletar_petroleo",
    "coletar_gasolina",
]
