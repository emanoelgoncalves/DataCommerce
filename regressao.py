from sklearn.linear_model import LinearRegression
import numpy as np

def prever_regressao(vendas):
    if len(vendas) < 2:
        return 0

    x = np.array(range(1, len(vendas) + 1)).reshape(-1, 1)
    y = np.array(vendas)

    modelo = LinearRegression()
    modelo.fit(x, y)

    previsao = modelo.predict([[len(vendas) + 1]])
    resultado = float(previsao[0])

    if resultado < 0:
        return 0

    return round(resultado, 2)