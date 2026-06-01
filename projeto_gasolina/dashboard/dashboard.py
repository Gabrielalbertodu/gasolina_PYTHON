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
    coletar_gasolina_historico,
)
import matplotlib.pyplot as plt

# Configuração da página
st.set_page_config(
    page_title="Gasolina IA",
    page_icon="⛽",
    layout="wide",
)

st.title("Registro Gasolina")
st.caption("Previsão de tendência do preço da gasolina usando indicadores econômicos e geopolíticos.\nConfiabilidade mostra quanto o modelo acredita nessa previsão, em linguagem simples.")

# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("⚙️ Controle")

    if st.button("Gerar Nova Previsão", type="primary", use_container_width=True):
        with st.spinner("Coletando dados e gerando previsão..."):
            try:
                # 1. Coleta de dados
                dolar = coletar_dolar()
                petroleo = coletar_petroleo()
                gasolina_dados = coletar_gasolina()
                noticias = coletar_noticias() or []

                dolar_source = "AwesomeAPI" if dolar is not None else "fallback"
                if dolar is None:
                    dolar = 5.20

                brent_wti_source = "API Yahoo" if petroleo is not None else "fallback"
                if petroleo is None:
                    petroleo = (82.0, 78.0)

                gasolina_source = "ANP" if gasolina_dados is not None else "fallback"
                if gasolina_dados is None:
                    gasolina_dados = {"gasolina_media": 6.15}

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

# Coleta de referência para mostrar fontes e status ao carregar a página
# (não altera a previsão já salva, apenas indica se a consulta está funcionando).

page_dolar = coletar_dolar()
page_petroleo = coletar_petroleo()
page_gasolina_dados = coletar_gasolina()
page_noticias = coletar_noticias() or []

page_dolar_source = "AwesomeAPI" if page_dolar is not None else "fallback"
if page_dolar is None:
    page_dolar = 5.20

page_brent_wti_source = "API Yahoo" if page_petroleo is not None else "fallback"
if page_petroleo is None:
    page_petroleo = (82.0, 78.0)

page_brent, page_wti = page_petroleo
page_gasolina_source = "ANP" if page_gasolina_dados is not None else "fallback"
if page_gasolina_dados is None:
    page_gasolina_dados = {"gasolina_media": 6.15, "total_amostras": 0}

page_gasolina = page_gasolina_dados["gasolina_media"]
page_gasolina_amostras = page_gasolina_dados.get("total_amostras", 0)

ultima = db.obter_ultima_previsao()

if ultima:
    # ── Resumo da Última Previsão ─────────────────────────────────────────────────
    st.subheader("Última Previsão")

    emoji_tendencia = {"Alta": "📈", "Queda": "📉", "Estabilidade": "➡️"}
    emoji = emoji_tendencia.get(ultima["previsao"], "❓")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Tendência", f"{emoji} {ultima['previsao']}")

    with col2:
        st.metric("Confiabilidade", f"{ultima['probabilidade']:.3%}")

    with col3:
        st.metric("Gerada em", ultima["data_hora"][:16].replace("T", " "))

    st.info(
        "💬 " + ultima['explicacao'] + "\n\n" \
        "Confiabilidade é a chance do modelo estar certo sobre essa tendência, " \
        "quanto maior, mais ele acredita na previsão."
    )

    st.subheader("📉 Indicadores Utilizados")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("💵 USD/BRL", f"R$ {ultima.get('dolar') or 0:.2f}")
    with col2:
        st.metric("🛢️ Brent", f"US$ {ultima.get('brent') or 0:.2f}")
    with col3:
        st.metric("🛢️ WTI", f"US$ {ultima.get('wti') or 0:.2f}")
    with col4:
        st.metric("⛽ Último preço da gasolina usado", f"R$ {ultima.get('gasolina') or 0:.2f}")

else:
    st.warning(
        "⚠️ Nenhuma previsão disponível. Clique em **Gerar Nova Previsão** no menu lateral. "
        "Os dados históricos e de fontes ainda estão disponíveis abaixo."
    )

# ── Status das fontes ─────────────────────────────────────────────────────────

st.subheader("🔎 Status das fontes")
status_cols = st.columns(4)
with status_cols[0]:
    st.write(f"**Dólar:** R$ {page_dolar:.4f} ({page_dolar_source})")
with status_cols[1]:
    st.write(f"**Petróleo:** Brent US$ {page_brent:.2f} / WTI US$ {page_wti:.2f} ({page_brent_wti_source})")
with status_cols[2]:
    st.write(
        f"**Gasolina ANP:** R$ {page_gasolina:.3f} ({page_gasolina_source})\n"
        f"Amostras: {page_gasolina_amostras}"
    )
with status_cols[3]:
    st.write(f"**Notícias coletadas:** {len(page_noticias)}")
# ── Fontes ────────────────────────────────────────────────────────────────────

st.subheader("Fontes Consultadas")
fontes = db.obter_fontes(ultima["id"]) if ultima else []

if fontes:
    for f in fontes:
        st.write(f"✓ {f}")
else:
    st.write("Nenhuma fonte registrada.")

# ── Evolução do Preço da Gasolina ─────────────────────────────────────────────

st.subheader("🕘 Evolução do Preço da Gasolina (média mensal)")

registries = coletar_gasolina_historico()

if registries:
    df = pd.DataFrame(registries)
    df["data_hora"] = pd.to_datetime(df["data_hora"])
    df = df.sort_values("data_hora")

    df["Mês"] = df["data_hora"].dt.to_period("M").dt.to_timestamp()
    mensal = (
        df.groupby("Mês")["gasolina"]
        .mean()
        .round(3)
        .reset_index()
        .rename(columns={"gasolina": "Preço Médio R$"})
    )

    st.markdown(
        "Fonte: ANP. O gráfico abaixo mostra a variação mensal do preço da gasolina regular "
        "com base nas coletas de posto de combustíveis."
    )

    col1, col2 = st.columns([2, 1])
    with col1:
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(mensal["Mês"], mensal["Preço Médio R$"], marker="o", linestyle="-", color="#0E7AFE")
        ax.bar(mensal["Mês"], mensal["Preço Médio R$"], alpha=0.25, color="#0E7AFE")
        ax.set_title("Preço médio mensal da gasolina")
        ax.set_ylabel("R$ por litro")
        ax.set_xlabel("Mês")
        ax.grid(axis="y", linestyle="--", alpha=0.6)
        fig.autofmt_xdate(rotation=45)
        st.pyplot(fig)

    with col2:
        ultimo_registro = df["data_hora"].dt.strftime("%Y-%m-%d").max()
        st.metric("Último registro", ultimo_registro)
        st.metric("Amostras de gasolina", len(df))
        st.metric("Meses na série", len(mensal))

    st.markdown("---")
    st.subheader("Evolução diária (média por dia)")
    daily = (
        df.groupby(df["data_hora"].dt.strftime("%Y-%m-%d"))["gasolina"]
        .mean()
        .round(3)
        .rename("Preço Médio R$")
    )
    st.line_chart(daily, use_container_width=True)

    st.subheader("Evolução semanal (média por semana)")
    weekly = (
        df.groupby(df["data_hora"].dt.to_period("W").apply(lambda x: x.start_time))["gasolina"]
        .mean()
        .round(3)
        .rename("Preço Médio R$")
    )
    st.line_chart(weekly, use_container_width=True)

    if len(mensal) > 1:
        st.subheader("Evolução mensal (média por mês)")
        st.bar_chart(mensal.set_index("Mês")["Preço Médio R$"], use_container_width=True)

    st.markdown("---")
    st.dataframe(mensal.sort_values("Mês", ascending=False).head(24), use_container_width=True, hide_index=True)

else:
    st.warning(
        "Não foi possível carregar o histórico de preços de gasolina da ANP. "
        "Verifique a conexão com a internet ou tente novamente mais tarde."
    )
