"""
api/routes.py

Define as rotas da API REST usando FastAPI.

Endpoints:
- GET /saude      → verifica se a API está no ar
- GET /previsao   → retorna a última previsão
- GET /historico  → lista as previsões salvas
"""

from fastapi import FastAPI, HTTPException
from datetime import datetime
from typing import Dict, List, Any


def criar_api(db, predictor) -> FastAPI:
    """
    Cria e configura a aplicação FastAPI.

    Args:
        db: instância de Database
        predictor: instância de PredisorGasolina

    Returns:
        Aplicação FastAPI configurada
    """
    app = FastAPI(
        title="Gasolina IA",
        description="Previsão de tendência do preço da gasolina no Brasil",
        version="1.0.0",
    )

    @app.get("/saude", tags=["Sistema"])
    def saude() -> Dict[str, str]:
        """Verifica se a API está funcionando."""
        return {"status": "ok", "timestamp": datetime.now().isoformat()}

    @app.get("/previsao", tags=["Previsões"])
    def obter_previsao() -> Dict[str, Any]:
        """
        Retorna a última previsão gerada.

        Exemplo de resposta:
        {
            "tendencia": "Alta",
            "probabilidade": 0.78,
            "fontes": ["AwesomeAPI", "Yahoo Finance", "Google News", "ANP"],
            ...
        }
        """
        previsao = db.obter_ultima_previsao()

        if not previsao:
            raise HTTPException(
                status_code=404,
                detail="Nenhuma previsão disponível. Execute o sistema primeiro.",
            )

        fontes = db.obter_fontes(previsao["id"])

        return {
            "tendencia": previsao["previsao"],
            "probabilidade": previsao["probabilidade"],
            "explicacao": previsao["explicacao"],
            "data_hora": previsao["data_hora"],
            "indicadores": {
                "dolar_reais": previsao.get("dolar"),
                "brent_usd": previsao.get("brent"),
                "wti_usd": previsao.get("wti"),
                "gasolina_media": previsao.get("gasolina"),
                "risco_noticias": previsao.get("risco"),
            },
            "fontes": fontes,
        }

    @app.get("/historico", tags=["Histórico"])
    def obter_historico(limite: int = 20) -> List[Dict[str, Any]]:
        """
        Lista as últimas N previsões salvas.

        Query param:
        - limite: número máximo de registros (padrão: 20)
        """
        previsoes = db.obter_historico(limite)

        return [
            {
                "id": p["id"],
                "data_hora": p["data_hora"],
                "tendencia": p["previsao"],
                "probabilidade": p["probabilidade"],
                "explicacao": p["explicacao"],
            }
            for p in previsoes
        ]

    return app
