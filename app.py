import sqlite3
from datetime import datetime

BANCO = "peladinha.db"


def conectar():
    conn = sqlite3.connect(BANCO, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def criar_banco():

    conn = conectar()
    cursor = conn.cursor()

    ####################################################
    # TABELA DE JOGADORAS
    ####################################################

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jogadoras(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        nome TEXT NOT NULL,

        nascimento TEXT,

        telefone TEXT,

        email TEXT,

        login TEXT UNIQUE,

        senha TEXT,

        tipo TEXT,

        status TEXT,

        foto TEXT,

        observacao TEXT,

        data_cadastro TEXT

    )
    """)

    ####################################################
    # ADMINISTRADORES
    ####################################################

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS administradores(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        nome TEXT,

        login TEXT UNIQUE,

        senha TEXT,

        nivel TEXT,

        ativo INTEGER DEFAULT 1

    )
    """)

    ####################################################
    # PRESENÇAS
    ####################################################

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS presencas(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        jogadora_id INTEGER,

        data TEXT,

        hora TEXT,

        tipo TEXT,

        status TEXT,

        FOREIGN KEY(jogadora_id)
        REFERENCES jogadoras(id)

    )
    """)

    ####################################################
    # FINANCEIRO
    ####################################################

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS financeiro(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        data TEXT,

        descricao TEXT,

        tipo TEXT,

        valor REAL

    )
    """)

    ####################################################
    # COMPROVANTES
    ####################################################

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS comprovantes(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        jogadora_id INTEGER,

        arquivo TEXT,

        observacao TEXT,

        data TEXT,

        status TEXT,

        FOREIGN KEY(jogadora_id)
        REFERENCES jogadoras(id)

    )
    """)
        ####################################################
    # AVISOS
    ####################################################

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS avisos(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        pix TEXT,

        vencimento TEXT,

        limite INTEGER,

        recado TEXT

    )
    """)

    ####################################################
    # REGULAMENTO
    ####################################################

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS regulamento(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        titulo TEXT,

        descricao TEXT

    )
    """)

    ####################################################
    # SORTEIOS
    ####################################################

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sorteios(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        data TEXT,

        hora TEXT,

        descricao TEXT

    )
    """)

    ####################################################
    # TIMES
    ####################################################

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS times(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        sorteio INTEGER,

        nome_time TEXT,

        jogadora TEXT

    )
    """)

    ####################################################
    # QUADRAS
    ####################################################

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quadras(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        nome TEXT,

        endereco TEXT,

        valor REAL,

        dia TEXT,

        horario TEXT

    )
    """)

    conn.commit()
        cursor.execute("""

    SELECT *

    FROM administradores

    WHERE login='admin'

    """)

    existe = cursor.fetchone()

    if existe is None:

        cursor.execute("""

        INSERT INTO administradores(

            nome,

            login,

            senha,

            nivel

        )

        VALUES(

            ?,?,?,?

        )

        """,(

            "Administrador",

            "admin",

            "123456",

            "MASTER"

        ))    cursor.execute("""

    SELECT *

    FROM avisos

    """)

    aviso = cursor.fetchone()

    if aviso is None:

        cursor.execute("""

        INSERT INTO avisos(

        pix,

        vencimento,

        limite,

        recado

        )

        VALUES(

        ?,?,?,?

        )

        """,(

        "",

        "Todo dia 10",

        15,

        "Bem-vindas ao Peladinha FC"

        ))    conn.commit()

    conn.close()


if __name__ == "__main__":

    criar_banco()

    print("Banco criado com sucesso.")
