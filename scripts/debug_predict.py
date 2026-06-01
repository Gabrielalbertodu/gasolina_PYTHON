import sys
import pandas as pd
sys.path.insert(0, 'projeto_gasolina')
from model.previsao import PredisorGasolina

# Indicadores baseados na última entrada do banco
features = {
    'dolar_reais': 5.0462,
    'brent_usd': 82.0,
    'wti_usd': 78.0,
    'petroleo_medio': (82.0+78.0)/2,
    'gasolina_reais': 6.15,
    'risco_noticias': 0.8666666666666667,
    'confianca_noticias': 0.0,
    'num_noticias': 10,
}

X = pd.DataFrame([features])
predictor = PredisorGasolina()
res = predictor.prever(X)
print('Features:', X.to_dict(orient='records')[0])
print('Resultado:', res)
