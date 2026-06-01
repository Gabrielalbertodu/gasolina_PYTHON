"""
app.py

Ponto de entrada principal do sistema.

Inicializa:
1. Banco de dados
2. Modelo de previsão
3. API FastAPI
4. Scheduler de automação (previsões às 08:00 e 20:00)

Para executar:
    python app.py
    (API disponível em http://localhost:8000)

Para o dashboard:
    streamlit run dashboard/dashboard.py
"""

import logging
import uvicorn

from database.database import db
from model.previsao import PredisorGasolina
from api.routes import criar_api
from scheduler.tarefas import agendar_previsoes
from data_collectors import (
    coletar_dolar,
    coletar_petroleo,
    coletar_noticias,
    coletar_gasolina,
)
from preprocessing.tratamento import construir_features

# Configuração básica de log
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def executar_previsao() -> None:
    """
    Coleta dados, gera previsão e salva no banco.
    Esta função é chamada pelo scheduler e também pode ser
    chamada manualmente para testes.
    """
    logger.info("Iniciando ciclo de previsão...")

    try:
        # 1. Coleta
        dolar = coletar_dolar() or 5.20
        petroleo = coletar_petroleo() or (82.0, 78.0)
        gasolina_dados = coletar_gasolina() or {"gasolina_media": 6.15}
        noticias = coletar_noticias() or []

        brent, wti = petroleo
        gasolina = gasolina_dados["gasolina_media"]

        logger.info(f"Dados coletados: dolar={dolar:.2f}, brent={brent:.2f}, wti={wti:.2f}, noticias={len(noticias)}")

        # 2. Features
        features = construir_features(
            dolar=dolar,
            brent=brent,
            wti=wti,
            gasolina=gasolina,
            noticias=noticias,
        )

        # 3. Previsão
        predictor = PredisorGasolina()
        resultado = predictor.prever(features)

        # 4. Salvar
        db.salvar_previsao(
            previsao=resultado["tendencia"],
            probabilidade=resultado["probabilidade"],
            explicacao=resultado["explicacao"],
            indicadores={
                "dolar": dolar,
                "brent": brent,
                "wti": wti,
                "gasolina": gasolina,
                "risco": features["risco_noticias"].iloc[0],
            },
            fontes=[
                "AwesomeAPI (Dólar)",
                "Yahoo Finance (Petróleo)",
                "Google News (Notícias)",
                "ANP (Gasolina Brasil)",
            ],
        )

        logger.info(
            f"Previsão salva: {resultado['tendencia']} "
            f"({resultado['probabilidade']:.1%})"
        )

    except Exception as e:
        logger.error(f"Erro no ciclo de previsão: {e}", exc_info=True)


def main() -> None:
    """Inicializa todos os componentes e sobe a API."""
    logger.info("=== Gasolina IA ===")

    # Modelo + API
    predictor = PredisorGasolina()
    app = criar_api(db, predictor)

    # Scheduler automático
    scheduler = agendar_previsoes(executar_previsao, horas=[8, 20])

    # Executa uma previsão inicial ao subir (opcional)
    logger.info("Executando previsão inicial...")
    executar_previsao()

    # Sobe a API
    logger.info("API disponível em http://localhost:8000")
    logger.info("Documentação em http://localhost:8000/docs")

    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    finally:
        from scheduler.tarefas import parar_scheduler
        parar_scheduler(scheduler)


if __name__ == "__main__":
    main()
