from flask import Flask, render_template, request, redirect, url_for, session
from dados import (
    buscar_dados,
    cadastrar_produto,
    listar_produtos,
    excluir_produto,
    cadastrar_venda,
    buscar_venda,
    atualizar_venda,
    excluir_venda,
    buscar_produto_por_id,
    atualizar_produto,
    relatorio_semestral,
    dashboard_resumo
)
from media import prever_media
from regressao import prever_regressao
from tendencia import prever_tendencia
from demanda import prever_demanda

app = Flask(__name__)
app.secret_key = "chave_secreta_projeto"

USUARIO_FIXO = "funcionario"
SENHA_FIXA = "1234"


@app.route("/login", methods=["GET", "POST"])
def login():
    mensagem = ""

    if request.method == "POST":
        nome = request.form["nome"]
        senha = request.form["senha"]

        if nome == USUARIO_FIXO and senha == SENHA_FIXA:
            session["logado"] = True
            session["usuario"] = nome
            return redirect(url_for("dashboard"))
        else:
            mensagem = "Nome ou senha inválidos."

    return render_template("login.html", mensagem=mensagem)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
def dashboard():
    if not session.get("logado"):
        return redirect(url_for("login"))

    resumo = dashboard_resumo()

    return render_template(
        "dashboard.html",
        usuario=session.get("usuario"),
        total_produtos=resumo["total_produtos"],
        total_vendido=resumo["total_vendido"],
        faturamento=resumo["faturamento"]
    )


@app.route("/produto")
def home():
    if not session.get("logado"):
        return redirect(url_for("login"))

    nome = request.args.get("nome", "")

    if not nome:
        return render_template("index.html", vazio=True)

    dados = buscar_dados(nome)

    if not dados:
        return render_template("index.html", vazio=True)

    produto = dados["produto"]
    historico = dados["historico"]

    vendas = [h["quantidade"] for h in historico]
    total_unidades = sum(vendas)
    total_reais = total_unidades * float(produto["preco"])

    demanda_valor, status = prever_demanda(vendas)

    historico_formatado = []
    for h in historico:
        historico_formatado.append({
            "id": h["id"],
            "data": h["data"].strftime("%d/%m/%Y"),
            "quantidade": h["quantidade"],
            "total": h["quantidade"] * float(produto["preco"])
        })

    datas_grafico = [h["data"] for h in historico_formatado]
    quantidades_grafico = [h["quantidade"] for h in historico_formatado]

    return render_template(
        "index.html",
        vazio=False,
        id_produto=produto["id"],
        nome=produto["nome"],
        categoria=produto["categoria"],
        marca=produto["marca"],
        preco=produto["preco"],
        estoque=produto["estoque"],
        imagem=produto.get("imagem", "sem_imagem.jpg"),
        historico=historico_formatado,
        total_unidades=total_unidades,
        total_reais=total_reais,
        media=prever_media(vendas),
        regressao=prever_regressao(vendas),
        tendencia=prever_tendencia(vendas),
        demanda=demanda_valor,
        status=status,
        datas_grafico=datas_grafico,
        quantidades_grafico=quantidades_grafico
    )


@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if not session.get("logado"):
        return redirect(url_for("login"))

    if request.method == "POST":
        cadastrar_produto(
            request.form["nome"],
            request.form["categoria"],
            request.form["marca"],
            request.form["preco"],
            request.form["estoque"],
            request.form["imagem"]
        )
        return redirect(url_for("home", nome=request.form["nome"]))

    return render_template("cadastro.html")


@app.route("/produtos")
def produtos():
    if not session.get("logado"):
        return redirect(url_for("login"))

    lista = listar_produtos()
    return render_template("produtos.html", produtos=lista)


@app.route("/editar_produto/<int:produto_id>", methods=["GET", "POST"])
def editar_produto(produto_id):
    if not session.get("logado"):
        return redirect(url_for("login"))

    produto = buscar_produto_por_id(produto_id)

    if not produto:
        return redirect(url_for("produtos"))

    if request.method == "POST":
        atualizar_produto(
            produto_id,
            request.form["nome"],
            request.form["categoria"],
            request.form["marca"],
            request.form["preco"],
            request.form["estoque"],
            request.form["imagem"]
        )
        return redirect(url_for("produtos"))

    return render_template("editar_produto.html", produto=produto)


@app.route("/excluir_produto/<int:produto_id>")
def rota_excluir_produto(produto_id):
    if not session.get("logado"):
        return redirect(url_for("login"))

    excluir_produto(produto_id)
    return redirect(url_for("produtos"))


@app.route("/cadastro_venda", methods=["GET", "POST"])
def cadastro_venda():
    if not session.get("logado"):
        return redirect(url_for("login"))

    mensagem = ""

    if request.method == "POST":
        produto_id = request.form["produto_id"]
        quantidade = request.form["quantidade"]
        data = request.form["data"]
        nome_produto = request.form["nome_produto"]

        sucesso, mensagem = cadastrar_venda(produto_id, quantidade, data)

        if sucesso:
            return redirect(url_for("home", nome=nome_produto))

        return render_template(
            "cadastro_venda.html",
            produto_id=produto_id,
            nome_produto=nome_produto,
            mensagem=mensagem
        )

    produto_id = request.args.get("produto_id", "")
    nome_produto = request.args.get("nome", "")

    return render_template(
        "cadastro_venda.html",
        produto_id=produto_id,
        nome_produto=nome_produto,
        mensagem=mensagem
    )


@app.route("/editar_venda/<int:venda_id>", methods=["GET", "POST"])
def editar_venda(venda_id):
    if not session.get("logado"):
        return redirect(url_for("login"))

    venda = buscar_venda(venda_id)
    mensagem = ""

    if request.method == "POST":
        quantidade = request.form["quantidade"]
        data = request.form["data"]
        nome_produto = request.form["nome_produto"]

        sucesso, mensagem = atualizar_venda(venda_id, quantidade, data)

        if sucesso:
            return redirect(url_for("home", nome=nome_produto))

        venda = buscar_venda(venda_id)

    return render_template("editar_venda.html", venda=venda, mensagem=mensagem)


@app.route("/excluir_venda/<int:venda_id>/<nome_produto>")
def rota_excluir_venda(venda_id, nome_produto):
    if not session.get("logado"):
        return redirect(url_for("login"))

    excluir_venda(venda_id)
    return redirect(url_for("home", nome=nome_produto))


@app.route("/relatorio")
def relatorio():
    if not session.get("logado"):
        return redirect(url_for("login"))

    dados = relatorio_semestral()
    return render_template("relatorio.html", dados=dados)


if __name__ == "__main__":
    app.run(debug=True)