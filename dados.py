import mysql.connector

def conectar():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="ecommerce"
        )
        return conn
    except:
        print("Erro ao conectar no banco")
        return None

def cadastrar_produto(nome, categoria, marca, preco, estoque, imagem):
    conn = conectar()
    cursor = conn.cursor()

    if not imagem:
        imagem = "sem_imagem.jpg"

    cursor.execute("""
        INSERT INTO produtos (nome, categoria, marca, preco, estoque, imagem)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (nome, categoria, marca, preco, estoque, imagem))

    conn.commit()
    cursor.close()
    conn.close()


def listar_produtos():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM produtos")
    dados = cursor.fetchall()

    cursor.close()
    conn.close()
    return dados


def buscar_produto_por_id(produto_id):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM produtos WHERE id = %s", (produto_id,))
    produto = cursor.fetchone()

    cursor.close()
    conn.close()
    return produto


def atualizar_produto(produto_id, nome, categoria, marca, preco, estoque, imagem):
    conn = conectar()
    cursor = conn.cursor()

    if not imagem:
        cursor.execute("""
            UPDATE produtos
            SET nome=%s, categoria=%s, marca=%s, preco=%s, estoque=%s
            WHERE id=%s
        """, (nome, categoria, marca, preco, estoque, produto_id))
    else:
        cursor.execute("""
            UPDATE produtos
            SET nome=%s, categoria=%s, marca=%s, preco=%s, estoque=%s, imagem=%s
            WHERE id=%s
        """, (nome, categoria, marca, preco, estoque, imagem, produto_id))

    conn.commit()
    cursor.close()
    conn.close()


def excluir_produto(produto_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM vendas WHERE produto_id=%s", (produto_id,))
    cursor.execute("DELETE FROM produtos WHERE id=%s", (produto_id,))

    conn.commit()
    cursor.close()
    conn.close()

def buscar_dados(nome):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM produtos WHERE nome = %s", (nome,))
    produto = cursor.fetchone()

    if not produto:
        return None

    cursor.execute("""
        SELECT * FROM vendas
        WHERE produto_id = %s
        ORDER BY data
    """, (produto["id"],))

    historico = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        "produto": produto,
        "historico": historico
    }


def cadastrar_venda(produto_id, quantidade, data):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT estoque FROM produtos WHERE id=%s", (produto_id,))
    produto = cursor.fetchone()

    if not produto:
        return False, "Produto não encontrado"

    if produto["estoque"] < int(quantidade):
        return False, "Estoque insuficiente"

    cursor.execute("""
        INSERT INTO vendas (produto_id, quantidade, data)
        VALUES (%s, %s, %s)
    """, (produto_id, quantidade, data))

    cursor.execute("""
        UPDATE produtos
        SET estoque = estoque - %s
        WHERE id = %s
    """, (quantidade, produto_id))

    conn.commit()
    cursor.close()
    conn.close()

    return True, "Venda cadastrada com sucesso"


def buscar_venda(venda_id):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT v.*, p.nome AS nome_produto
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        WHERE v.id = %s
    """, (venda_id,))

    venda = cursor.fetchone()

    cursor.close()
    conn.close()
    return venda


def atualizar_venda(venda_id, nova_quantidade, nova_data):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM vendas WHERE id=%s", (venda_id,))
    venda = cursor.fetchone()

    if not venda:
        return False, "Venda não encontrada"

    produto_id = venda["produto_id"]
    quantidade_antiga = venda["quantidade"]

    cursor.execute("SELECT estoque FROM produtos WHERE id=%s", (produto_id,))
    produto = cursor.fetchone()

    estoque_atual = produto["estoque"] + quantidade_antiga

    if estoque_atual < int(nova_quantidade):
        return False, "Estoque insuficiente para edição"

    cursor.execute("""
        UPDATE vendas
        SET quantidade=%s, data=%s
        WHERE id=%s
    """, (nova_quantidade, nova_data, venda_id))

    novo_estoque = estoque_atual - int(nova_quantidade)

    cursor.execute("""
        UPDATE produtos
        SET estoque=%s
        WHERE id=%s
    """, (novo_estoque, produto_id))

    conn.commit()
    cursor.close()
    conn.close()

    return True, "Venda atualizada"


def excluir_venda(venda_id):
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM vendas WHERE id=%s", (venda_id,))
    venda = cursor.fetchone()

    if venda:
        cursor.execute("""
            UPDATE produtos
            SET estoque = estoque + %s
            WHERE id = %s
        """, (venda["quantidade"], venda["produto_id"]))

    cursor.execute("DELETE FROM vendas WHERE id=%s", (venda_id,))

    conn.commit()
    cursor.close()
    conn.close()


def dashboard_resumo():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total FROM produtos")
    total_produtos = cursor.fetchone()["total"]

    cursor.execute("SELECT SUM(quantidade) AS total FROM vendas")
    total_vendido = cursor.fetchone()["total"] or 0

    cursor.execute("""
        SELECT SUM(v.quantidade * p.preco) AS total
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
    """)
    faturamento = cursor.fetchone()["total"] or 0

    cursor.close()
    conn.close()

    return {
        "total_produtos": total_produtos,
        "total_vendido": total_vendido,
        "faturamento": faturamento
    }


def relatorio_semestral():
    conn = conectar()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            p.nome,
            p.categoria,
            SUM(v.quantidade) AS total_unidades,
            SUM(v.quantidade * p.preco) AS total_reais
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        WHERE v.data >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
        GROUP BY p.id
        ORDER BY total_unidades DESC
    """)
    produtos = cursor.fetchall()

    cursor.execute("""
        SELECT p.nome, SUM(v.quantidade) AS total_unidades
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        GROUP BY p.id
        ORDER BY total_unidades DESC
        LIMIT 1
    """)
    produto_mais_vendido = cursor.fetchone()

    cursor.execute("""
        SELECT categoria, SUM(v.quantidade) AS total_unidades
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        GROUP BY categoria
        ORDER BY total_unidades DESC
        LIMIT 1
    """)
    categoria_mais_vendida = cursor.fetchone()

    cursor.execute("""
        SELECT p.nome, COALESCE(SUM(v.quantidade),0) AS total_unidades
        FROM produtos p
        LEFT JOIN vendas v ON p.id = v.produto_id
        GROUP BY p.id
        HAVING total_unidades <= 10
    """)
    baixa_venda = cursor.fetchall()

    cursor.execute("""
        SELECT SUM(v.quantidade) AS total_unidades,
               SUM(v.quantidade * p.preco) AS total_reais
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
    """)
    resumo = cursor.fetchone()

    cursor.execute("""
        SELECT p.nome, SUM(v.quantidade) AS total_unidades
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        GROUP BY p.id
    """)
    grafico_produtos = cursor.fetchall()

    cursor.execute("""
        SELECT p.categoria, SUM(v.quantidade) AS total_unidades
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        GROUP BY p.categoria
    """)
    grafico_categorias = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        "produtos": produtos,
        "produto_mais_vendido": produto_mais_vendido,
        "categoria_mais_vendida": categoria_mais_vendida,
        "baixa_venda": baixa_venda,
        "total_unidades": resumo["total_unidades"] or 0,
        "total_reais": resumo["total_reais"] or 0,
        "grafico_produtos": grafico_produtos,
        "grafico_categorias": grafico_categorias
    }