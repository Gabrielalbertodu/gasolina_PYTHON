"""
database/database.py

Gerencia conexões e operações com o banco de dados SQLite.

Operações disponíveis:
- salvar_previsao: insere nova previsão com suas fontes
- obter_ultima_previsao: busca a previsão mais recente
- obter_historico: busca as N previsões mais recentes
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

from database.models import SCHEMA

# Caminho do arquivo SQLite
DB_PATH = Path("data") / "gasolina.sqlite3"


class Database:
    """Gerenciador simples do banco de dados SQLite."""

    def __init__(self, caminho: Path = DB_PATH):
        self.caminho = caminho
        self.caminho.parent.mkdir(exist_ok=True)
        self._criar_tabelas()

    def _criar_tabelas(self) -> None:
        """Executa o schema para criar as tabelas (se não existirem)."""
        with sqlite3.connect(self.caminho) as conn:
            conn.executescript(SCHEMA)

    def _conectar(self) -> sqlite3.Connection:
        """Retorna conexão com row_factory para retornar dicionários."""
        conn = sqlite3.connect(self.caminho)
        conn.row_factory = sqlite3.Row
        return conn

    def salvar_previsao(
        self,
        previsao: str,
        probabilidade: float,
        explicacao: str,
        indicadores: Dict[str, Any],
        fontes: List[str],
    ) -> int:
        """
        Salva uma nova previsão no banco de dados.

        Args:
            previsao: 'Alta', 'Queda' ou 'Estabilidade'
            probabilidade: valor entre 0.0 e 1.0
            explicacao: texto explicativo da previsão
            indicadores: dicionário com dolar, brent, wti, gasolina, risco
            fontes: lista com nomes das fontes consultadas

        Returns:
            ID da previsão inserida
        """
        with self._conectar() as conn:
            cursor = conn.cursor()

            # Insere a previsão
            cursor.execute(
                """
                INSERT INTO previsoes
                    (data_hora, previsao, probabilidade, explicacao,
                     dolar, brent, wti, gasolina, risco)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.now().isoformat(),
                    previsao,
                    probabilidade,
                    explicacao,
                    indicadores.get("dolar"),
                    indicadores.get("brent"),
                    indicadores.get("wti"),
                    indicadores.get("gasolina"),
                    indicadores.get("risco"),
                ),
            )

            previsao_id = cursor.lastrowid

            # Insere as fontes
            for fonte in fontes:
                cursor.execute(
                    "INSERT INTO fontes (previsao_id, nome) VALUES (?, ?)",
                    (previsao_id, fonte),
                )

            conn.commit()
            return previsao_id

    def obter_ultima_previsao(self) -> Optional[Dict[str, Any]]:
        """Retorna a previsão mais recente ou None."""
        with self._conectar() as conn:
            row = conn.execute(
                "SELECT * FROM previsoes ORDER BY data_hora DESC LIMIT 1"
            ).fetchone()
            return dict(row) if row else None

    def obter_historico(self, limite: int = 20) -> List[Dict[str, Any]]:
        """Retorna as N previsões mais recentes."""
        with self._conectar() as conn:
            rows = conn.execute(
                "SELECT * FROM previsoes ORDER BY data_hora DESC LIMIT ?",
                (limite,),
            ).fetchall()
            return [dict(r) for r in rows]

    def obter_fontes(self, previsao_id: int) -> List[str]:
        """Retorna a lista de fontes de uma previsão específica."""
        with self._conectar() as conn:
            rows = conn.execute(
                "SELECT nome FROM fontes WHERE previsao_id = ?",
                (previsao_id,),
            ).fetchall()
            return [r[0] for r in rows]


# Instância global compartilhada por toda a aplicação
db = Database()
