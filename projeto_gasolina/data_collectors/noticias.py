"""
data_collectors/noticias.py

Coleta notícias sobre petróleo e geopolítica via Google News RSS.
"""

import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus
from datetime import datetime
from typing import List, Dict


# Termos de busca relevantes para o sistema
QUERIES = [
    "petroleo guerra sancoes OPEP",
    "gasolina preco Brasil",
    "conflito internacional energia",
    "economia global dolar",
]


def coletar_noticias() -> List[Dict]:
    """
    Coleta notícias de várias queries e remove duplicatas.

    Returns:
        Lista de dicionários com título, url, fonte e data.
    """
    todas = []
    urls_vistos = set()

    for query in QUERIES:
        for noticia in _buscar_rss(query):
            if noticia["url"] not in urls_vistos:
                urls_vistos.add(noticia["url"])
                todas.append(noticia)

    return todas[:15]  # Limita a 15 notícias


def _buscar_rss(query: str) -> List[Dict]:
    """Busca notícias via Google News RSS para uma query."""
    try:
        url = (
            f"https://news.google.com/rss/search"
            f"?q={quote_plus(query)}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        )
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        root = ET.fromstring(response.content)
        noticias = []

        for item in root.findall(".//item")[:5]:
            titulo = _texto(item, "title")
            link = _texto(item, "link")
            fonte = _texto(item, "source") or "Google News"
            data = _texto(item, "pubDate") or datetime.now().isoformat()

            if titulo and link:
                noticias.append({
                    "titulo": titulo,
                    "url": link,
                    "fonte": fonte,
                    "publicada_em": data,
                })

        return noticias

    except Exception as e:
        print(f"[noticias] Erro na query '{query}': {e}")
        return []


def _texto(elemento, tag: str) -> str:
    """Extrai texto de um tag XML com segurança."""
    try:
        found = elemento.find(tag)
        return (found.text or "").strip() if found is not None else ""
    except Exception:
        return ""
