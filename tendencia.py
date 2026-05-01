def prever_tendencia(vendas):
    if len(vendas) < 3:
        return 0
    return round(sum(vendas[-3:]) / 3, 2)