def prever_media(vendas):
    if not vendas:
        return 0
    return round(sum(vendas) / len(vendas), 2)