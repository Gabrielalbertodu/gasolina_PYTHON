from data_collectors import coletar_gasolina
import pandas as pd
import matplotlib.pyplot as plt


df = pd.read_csv("arquivos/shpc/qus/ultimas-4-semanas-gasolina-etanol.csv")
df_gasolina = df.groupby("Semana")["Preço de Venda"].mean().reset_index()
df_gasolina["Semana"] = pd.to_datetime(df_gasolina["Semana"])
print(df_gasolina)