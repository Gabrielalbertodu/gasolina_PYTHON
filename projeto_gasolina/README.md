# ⛽ Gasolina IA — Previsão de Tendência do Preço da Gasolina

Sistema de previsão de **tendência** do preço da gasolina no Brasil baseado em:
- Cotação do dólar (USD/BRL)
- Preço do petróleo (Brent e WTI)
- Análise de notícias geopolíticas
- Dados históricos da ANP

> ⚠️ O sistema **não prevê o valor exato** da gasolina.  
> Ele classifica a tendência em: **Alta**, **Queda** ou **Estabilidade**.

---

## 🎯 Objetivo

Projeto acadêmico que demonstra a integração de:

- **Coleta automática de dados** de fontes públicas
- **Machine Learning** com Scikit-Learn
- **API REST** com FastAPI
- **Dashboard interativo** com Streamlit
- **Automação de previsões** com APScheduler
- **Persistência local** com SQLite

---

## 🚀 Instalação

### Pré-requisitos
- Python 3.10 ou superior

### Passos

```bash
cd projeto_gasolina
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate       # Linux/Mac
pip install -r requirements.txt
```

---

## ▶️ Execução

### API + Scheduler

```bash
python app.py
```

A API estará disponível em:
- **http://localhost:8000** — API
- **http://localhost:8000/docs** — Documentação Swagger

### Dashboard

Em outro terminal:

```bash
streamlit run dashboard/dashboard.py
```

O dashboard abre em **http://localhost:8501**.

### Testes

```bash
pytest tests/ -v
```

---

## 📡 Endpoints da API

| Método | Rota        | Descrição                     |
|--------|-------------|-------------------------------|
| GET    | `/saude`    | Verifica se a API está no ar  |
| GET    | `/previsao` | Retorna a última previsão     |
| GET    | `/historico`| Lista as previsões salvas     |

### Exemplo de resposta `/previsao`

```json
{
  "tendencia": "Alta",
  "probabilidade": 0.78,
  "explicacao": "Tendência de ALTA com confiança de 78%. Fatores: dólar elevado (R$ 5.80), petróleo caro (US$ 92.5).",
  "data_hora": "2025-01-15T08:00:00",
  "indicadores": {
    "dolar_reais": 5.80,
    "brent_usd": 95.0,
    "wti_usd": 90.0,
    "gasolina_media": 6.60,
    "risco_noticias": 1.4
  },
  "fontes": [
    "AwesomeAPI (Dólar)",
    "Yahoo Finance (Petróleo)",
    "Google News (Notícias)",
    "ANP (Gasolina Brasil)"
  ]
}
```

---

## 🏗️ Estrutura do Projeto

```
projeto_gasolina/
│
├── app.py                        # Ponto de entrada principal
├── api/
│   └── routes.py                 # Endpoints FastAPI
├── data_collectors/
│   ├── __init__.py               # Exporta funções de coleta
│   ├── dolar.py                  # AwesomeAPI (USD/BRL)
│   ├── petroleo.py               # Yahoo Finance (Brent/WTI)
│   ├── gasolina.py               # ANP (preço gasolina Brasil)
│   └── noticias.py               # RSS de notícias geopolíticas
├── preprocessing/
│   └── tratamento.py             # Engenharia de features
├── model/
│   ├── treinamento.py            # Treinamento do modelo
│   └── previsao.py               # Classe de previsão
├── database/
│   ├── models.py                 # Schema SQL
│   └── database.py               # Operações CRUD
├── scheduler/
│   └── tarefas.py                # Agendamento de previsões
├── dashboard/
│   └── dashboard.py              # Interface Streamlit
├── tests/
│   ├── test_api.py
│   ├── test_model.py
│   └── test_database.py
├── data/
│   └── gasolina.sqlite3          # Banco local gerado automaticamente
└── requirements.txt
```

---

## ⚙️ Tecnologias Utilizadas

| Tecnologia    | Uso                                      |
|---------------|------------------------------------------|
| Scikit-Learn  | Modelo de classificação                  |
| Pandas        | Manipulação de dados                     |
| NumPy         | Geração e processamento de dados         |
| FastAPI       | API REST                                 |
| Uvicorn       | Servidor ASGI                            |
| Streamlit     | Dashboard interativo                     |
| APScheduler   | Agendamento de previsões                 |
| SQLite        | Persistência local                       |
| Requests      | Coleta de dados via HTTP                 |
| Pytest        | Testes unitários                         |

---

## 🔄 Fluxo do Sistema

1. `app.py` inicializa o sistema
2. O modelo é treinado em `model/treinamento.py`
3. A API FastAPI é iniciada
4. O scheduler agenda previsões em `08:00` e `20:00`
5. Em cada ciclo, o app coleta:
   - dólar via AwesomeAPI
   - petróleo via Yahoo Finance
   - notícias geopolíticas via RSS
   - gasolina via ANP
6. O conjunto de dados é transformado em features
7. O modelo classifica a tendência e salva no SQLite
8. O dashboard e a API exibem os resultados

---

## 🧠 Como o modelo funciona

- Treina um `RandomForestClassifier` com dados sintéticos
- A saída é uma tendência: **Alta**, **Queda** ou **Estabilidade**
- A probabilidade representa a confiança do modelo na classe prevista
- O modelo não retorna o preço final da gasolina

---

## ℹ️ Observações importantes

- O dashboard usa o histórico ANP para gerar gráficos de evolução
- Se o gráfico não aparecer, verifique a coleta de ANP e a conexão com a internet
- O sistema tem fallback de valores quando alguma fonte externa estiver indisponível
- A previsão é um indicador de tendência, não uma estimativa de preço absoluto
| UC4 | Previsão automática      | Sistema      | APScheduler executa previsão às 08:00 e 20:00          |
| UC5 | Visualizar dashboard     | Usuário      | Acessa Streamlit para ver indicadores e gráficos       |

---

## ✅ Requisitos Funcionais

| ID   | Requisito                                                                 |
|------|---------------------------------------------------------------------------|
| RF01 | O sistema deve coletar cotação do dólar via AwesomeAPI                    |
| RF02 | O sistema deve coletar preço do petróleo Brent e WTI via Yahoo Finance    |
| RF03 | O sistema deve coletar notícias geopolíticas via Google News RSS           |
| RF04 | O sistema deve coletar dados de gasolina via CSV da ANP                   |
| RF05 | O modelo deve classificar a tendência em Alta, Queda ou Estabilidade      |
| RF06 | O sistema deve retornar a probabilidade da previsão                        |
| RF07 | O sistema deve salvar cada previsão no banco SQLite                        |
| RF08 | A API deve expor endpoints /previsao e /historico                          |
| RF09 | O dashboard deve exibir a última previsão e histórico                      |
| RF10 | O scheduler deve executar previsões automáticas às 08:00 e 20:00          |

---

## 🔒 Requisitos Não Funcionais

| ID    | Requisito                                                          |
|-------|--------------------------------------------------------------------|
| RNF01 | Código comentado e legível (PEP8)                                  |
| RNF02 | Arquitetura modular com responsabilidades separadas                 |
| RNF03 | Tratamento de erros em todas as chamadas externas                  |
| RNF04 | Uso exclusivo de fontes públicas e gratuitas                       |
| RNF05 | Rastreabilidade das fontes em cada previsão                        |
| RNF06 | Testes unitários cobrindo API, modelo e banco de dados             |
| RNF07 | Valores padrão (fallback) quando APIs externas falharem            |
| RNF08 | Banco de dados não armazena histórico completo de preços           |
