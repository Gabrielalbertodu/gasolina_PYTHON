"""
dashboard/dashboard.py

Interface web do sistema usando Streamlit.

Para executar:
    streamlit run dashboard/dashboard.py

Funcionalidades:
- Botão para gerar nova previsão
- Exibição da última previsão (tendência, confiança, data)
- Indicadores econômicos utilizados
- Fontes consultadas
- Histórico de previsões com gráfico
"""

import sys
import os

# Garante que o diretório raiz do projeto está no path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd

from database.database import db
from model.previsao import PredisorGasolina
from preprocessing.tratamento import construir_features
from data_collectors import (
    coletar_dolar,
    coletar_petroleo,
    coletar_noticias,
    coletar_gasolina,
)

# Configuração da página
st.set_page_config(
    page_title="Gasolina IA",
    page_icon="⛽",
    layout="wide",
)

st.title("⛽ Gasolina IA")
st.caption("Previsão de tendência do preço da gasolina com base em indicadores econômicos e geopolíticos.")

# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("⚙️ Controle")

    if st.button("Gerar Nova Previsão", type="primary", use_container_width=True):
        with st.spinner("Coletando dados e gerando previsão..."):
            try:
                # 1. Coleta de dados
                dolar = coletar_dolar() or 5.20
                petroleo = coletar_petroleo() or (82.0, 78.0)
                gasolina_dados = coletar_gasolina() or {"gasolina_media": 6.15}
                noticias = coletar_noticias() or []

                brent, wti = petroleo
                gasolina = gasolina_dados["gasolina_media"]

                # 2. Engenharia de features
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

                # 4. Salvar no banco
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
                    fontes=["AwesomeAPI (Dólar)", "Yahoo Finance (Petróleo)", "Google News", "ANP (Gasolina)"],
                )

                st.success("✅ Previsão salva com sucesso!")
                st.rerun()

            except Exception as e:
                st.error(f"Erro ao gerar previsão: {e}")

    st.divider()
    st.caption("O sistema atualiza automaticamente às 08:00 e 20:00.")

# ── Conteúdo Principal ────────────────────────────────────────────────────────

ultima = db.obter_ultima_previsao()

if not ultima:
    st.warning("⚠️ Nenhuma previsão disponível. Clique em **Gerar Nova Previsão** no menu lateral.")
    st.stop()

# ── Resumo da Última Previsão ─────────────────────────────────────────────────

st.subheader("📊 Última Previsão")

emoji_tendencia = {"Alta": "📈", "Queda": "📉", "Estabilidade": "➡️"}
emoji = emoji_tendencia.get(ultima["previsao"], "❓")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Tendência", f"{emoji} {ultima['previsao']}")

with col2:
    st.metric("Confiança", f"{ultima['probabilidade']:.0%}")

with col3:
    st.metric("Gerada em", ultima["data_hora"][:16].replace("T", " "))

st.info(f"💬 {ultima['explicacao']}")

# ── Indicadores ───────────────────────────────────────────────────────────────

st.subheader("📉 Indicadores Utilizados")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("💵 USD/BRL", f"R$ {ultima.get('dolar') or 0:.2f}")
with col2:
    st.metric("🛢️ Brent", f"US$ {ultima.get('brent') or 0:.2f}")
with col3:
    st.metric("🛢️ WTI", f"US$ {ultima.get('wti') or 0:.2f}")
with col4:
    st.metric("⛽ Gasolina Média", f"R$ {ultima.get('gasolina') or 0:.2f}")

# ── Fontes ────────────────────────────────────────────────────────────────────

st.subheader("📚 Fontes Consultadas")
fontes = db.obter_fontes(ultima["id"])

if fontes:
    for f in fontes:
        st.write(f"✓ {f}")
else:
    st.write("Nenhuma fonte registrada.")

# ── Histórico ─────────────────────────────────────────────────────────────────

st.subheader("🕘 Histórico de Previsões")
historico = db.obter_historico(30)

if historico:
    df = pd.DataFrame(historico)
    df["data_hora"] = pd.to_datetime(df["data_hora"])
    df = df.sort_values("data_hora")

    # Gráfico de confiança ao longo do tempo
    st.line_chart(
        df.set_index("data_hora")[["probabilidade"]],
        use_container_width=True,
    )

    # Tabela resumida
    st.dataframe(
        df[["data_hora", "previsao", "probabilidade"]]
        .rename(columns={
            "data_hora": "Data/Hora",
            "previsao": "Tendência",
            "probabilidade": "Confiança",
        })
        .sort_values("Data/Hora", ascending=False)
        .head(15),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("Sem histórico ainda.")
