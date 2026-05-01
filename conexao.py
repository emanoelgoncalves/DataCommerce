import mysql.connector

def conectar():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="ecommerce"
        )
    except mysql.connector.Error as erro:
        print("Erro ao conectar:", erro)
        return None