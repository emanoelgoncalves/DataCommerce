def prever_demanda(vendas):
    if not vendas:
        return 0, "Sem dados"

    media = sum(vendas) / len(vendas)

    if len(vendas) >= 2:
        tendencia = vendas[-1] - vendas[-2]
    else:
        tendencia = 0

    n = len(vendas)
    x = list(range(n))

    soma_x = sum(x)
    soma_y = sum(vendas)
    soma_xy = sum(x[i] * vendas[i] for i in range(n))
    soma_x2 = sum(i**2 for i in x)

    if (n * soma_x2 - soma_x**2) != 0:
        a = (n * soma_xy - soma_x * soma_y) / (n * soma_x2 - soma_x**2)
        b = (soma_y - a * soma_x) / n
        regressao = a * n + b
    else:
        regressao = media

    demanda = (media + regressao + vendas[-1]) / 3

    if demanda <= 6:
        status = "Baixa"
    elif demanda <= 10:
        status = "Média"
    else:
        status = "Alta"

    return round(demanda, 2), status