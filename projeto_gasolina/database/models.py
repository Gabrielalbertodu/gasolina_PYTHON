"""
database/models.py

Define o esquema (schema) do banco de dados SQLite.

Tabelas:
- previsoes: armazena cada previsão gerada
- fontes: armazena as fontes consultadas por previsão
"""

SCHEMA = """
-- Tabela principal: previsões geradas pelo sistema
CREATE TABLE IF NOT EXISTS previsoes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    data_hora   TEXT    NOT NULL,
    previsao    TEXT    NOT NULL CHECK(previsao IN ('Alta', 'Queda', 'Estabilidade')),
    probabilidade REAL  NOT NULL,
    explicacao  TEXT,
    dolar       REAL,
    brent       REAL,
    wti         REAL,
    gasolina    REAL,
    risco       REAL
);

-- Tabela de fontes: quais APIs foram consultadas em cada previsão
CREATE TABLE IF NOT EXISTS fontes (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    previsao_id   INTEGER NOT NULL,
    nome          TEXT    NOT NULL,
    FOREIGN KEY(previsao_id) REFERENCES previsoes(id) ON DELETE CASCADE
);

-- Índice para acelerar consultas por data
CREATE INDEX IF NOT EXISTS idx_previsoes_data ON previsoes(data_hora);
"""
