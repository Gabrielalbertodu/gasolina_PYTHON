"""
scheduler/tarefas.py

Agenda execução automática das previsões com APScheduler.

Por padrão, executa todos os dias às 08:00 e 20:00.
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler

logger = logging.getLogger(__name__)


def agendar_previsoes(funcao_previsao, horas: list = None) -> BackgroundScheduler:
    """
    Registra e inicia o agendador de previsões.

    Args:
        funcao_previsao: Função que será chamada nos horários agendados.
                         Deve coletar dados, gerar previsão e salvar no BD.
        horas: Lista de horas do dia (inteiros). Padrão: [8, 20]

    Returns:
        Instância do scheduler em execução.
    """
    if horas is None:
        horas = [8, 20]

    scheduler = BackgroundScheduler()

    for hora in horas:
        scheduler.add_job(
            func=funcao_previsao,
            trigger="cron",
            hour=hora,
            minute=0,
            id=f"previsao_{hora}h",
            name=f"Previsão diária às {hora:02d}:00",
            replace_existing=True,
        )
        logger.info(f"[scheduler] Agendado: {hora:02d}:00")

    scheduler.start()
    logger.info("[scheduler] Iniciado com sucesso.")

    return scheduler


def parar_scheduler(scheduler: BackgroundScheduler) -> None:
    """Para o scheduler de forma segura."""
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("[scheduler] Parado.")
