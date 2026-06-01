import sys
sys.path.insert(0, 'projeto_gasolina')
from data_collectors.gasolina import coletar_gasolina, coletar_gasolina_historico
from data_collectors import coletar_dolar, coletar_petroleo, coletar_noticias
from preprocessing.tratamento import construir_features
from model.previsao import PredisorGasolina
import pandas as pd
import matplotlib.pyplot as plt

print('dolar', coletar_dolar())
print('petroleo', coletar_petroleo())
noticias = coletar_noticias()
print('noticias count', len(noticias))
print('first noticias', noticias[:2])
print('gasolina stats', {k: v for k, v in coletar_gasolina().items() if k != 'valores_de_venda'})
regs = coletar_gasolina_historico()
print('historico size', len(regs) if regs else None)
if regs:
    df = pd.DataFrame(regs)
    df['data_hora'] = pd.to_datetime(df['data_hora'])
    df['Mês'] = df['data_hora'].dt.to_period('M').dt.to_timestamp()
    mensal = df.groupby('Mês')['gasolina'].mean().round(3).reset_index()
    print('mensal count', len(mensal))
    print(mensal.head().to_string(index=False))
    fig, ax = plt.subplots(figsize=(6, 3))
    ax.plot(mensal['Mês'], mensal['gasolina'], marker='o')
    ax.set_title('Test plot')
    fig.savefig('scripts/validate_plot.png')
    print('plot saved to scripts/validate_plot.png')

if coletar_dolar() and coletar_petroleo() and coletar_gasolina():
    dolar = coletar_dolar() or 5.20
    brent, wti = coletar_petroleo() or (82.0, 78.0)
    gasolina = coletar_gasolina()['gasolina_media']
    noticias = coletar_noticias() or []
    features = construir_features(dolar=dolar, brent=brent, wti=wti, gasolina=gasolina, noticias=noticias)
    predictor = PredisorGasolina()
    resultado = predictor.prever(features)
    print('features', features.to_dict(orient='records'))
    print('resultado', resultado)
