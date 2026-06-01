import sys
sys.path.insert(0, 'projeto_gasolina')
from data_collectors.gasolina import coletar_gasolina, coletar_gasolina_historico
from data_collectors import coletar_dolar, coletar_petroleo, coletar_noticias
from preprocessing.tratamento import construir_features
from model.previsao import PredisorGasolina
import pandas as pd

print('dolar', coletar_dolar())
print('petroleo', coletar_petroleo())
noticias = coletar_noticias()
print('noticias', len(noticias))
print(noticias[:3])
print('gasolina stats', coletar_gasolina())
regs = coletar_gasolina_historico()
print('historico size', len(regs) if regs else None)
if regs:
    df = pd.DataFrame(regs)
    df['data_hora'] = pd.to_datetime(df['data_hora'])
    print(df.head())
    print('months', df['data_hora'].dt.to_period('M').dt.to_timestamp().nunique())

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
