import sqlite3

DB_NAME = "financeiro.db"
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

# Limpar tabelas antigas
c.execute("DROP TABLE IF EXISTS matriz_gastos")
c.execute("DROP TABLE IF EXISTS matriz_totais")

# Tabela das linhas de despesas
c.execute('''
    CREATE TABLE matriz_gastos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        despesa TEXT UNIQUE,
        janeiro REAL DEFAULT 0,
        fevereiro REAL DEFAULT 0,
        marco REAL DEFAULT 0,
        abril REAL DEFAULT 0,
        maio REAL DEFAULT 0,
        junho REAL DEFAULT 0,
        julho REAL DEFAULT 0,
        agosto REAL DEFAULT 0,
        setembro REAL DEFAULT 0,
        outubro REAL DEFAULT 0,
        novembro REAL DEFAULT 0,
        dezembro REAL DEFAULT 0
    )
''')

# Tabela das rendas mensais
c.execute('''
    CREATE TABLE matriz_totais (
        tipo TEXT PRIMARY KEY,
        janeiro REAL DEFAULT 0,
        fevereiro REAL DEFAULT 0,
        marco REAL DEFAULT 0,
        abril REAL DEFAULT 0,
        maio REAL DEFAULT 0,
        junho REAL DEFAULT 0,
        julho REAL DEFAULT 0,
        agosto REAL DEFAULT 0,
        setembro REAL DEFAULT 0,
        outubro REAL DEFAULT 0,
        novembro REAL DEFAULT 0,
        dezembro REAL DEFAULT 0
    )
''')

# Dados exatos da sua planilha
despesas_originais = [
    ("IMPOSTO ANUAL", [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    ("CARREFOUR", [1544, 1999, 2890, 2595, 1860, 2260, 2965, 2700, 3400, 0, 0, 0]),
    ("Emprestimo MP", [262.2, 262.2, 262.2, 262.2, 262.2, 262.2, 0, 0, 0, 0, 0, 0]),
    ("MERCADO PAGO", [3900, 4331, 4840, 4293, 4670, 4700, 0, 340, 1800, 340, 340, 340]),
    ("INTERNET VIVO", [0, 0, 0, 0, 127.75, 160, 165, 165, 168, 165, 165, 165]),
    ("Celular Raissa", [55, 55, 55, 55, 61.3, 60, 60, 60, 60, 60, 60, 60]),
    ("VAN ISABELA", [0, 283, 283, 283, 283, 283, 283, 283, 283, 283, 283, 283]),
    ("MATRICULA ISABELA", [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    ("ESCOLA ISABELA", [0, 668.8, 668.8, 668.8, 668.8, 668.8, 668.8, 668.8, 668.8, 668.8, 668.8, 668.8]),
    ("LIVROS ISABELA", [0, 223.9, 223.9, 223.9, 223.9, 223.9, 223.9, 223.9, 223.9, 223.9, 223.9, 223.9]),
    ("PARCELA CARRO", [3359.41, 3359.41, 3359.41, 3359.41, 3359.41, 3359.41, 3359.41, 3359.41, 3359.41, 3359.41, 3359.41, 3359.41]),
    ("ALARME", [0, 0, 0, 0, 101, 0, 100.01, 100.01, 100.01, 100.01, 100.01, 100.01]),
    ("LUZ", [0, 0, 0, 0, 492.24, 0, 519.59, 526.12, 0, 0, 0, 0]),
    ("AGUA", [0, 0, 0, 0, 240, 0, 124, 301.62, 0, 0, 0, 0]),
    ("IPVA ANDRE", [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    ("FILTRO DE AGUA + SOFA", [240, 240, 240, 240, 240, 240, 0, 0, 0, 0, 0, 0]),
    ("IPVA RAISSA", [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    ("Faculdade andre", [0, 0, 0, 0, 0, 0, 124.75, 124.75, 124.75, 124.75, 124.75, 124.75]),
    ("GASTOS ANDRE ***", [0, 0, 0, 0, 54, 0, 0, 0, 400, 0, 0, 0]),
    ("GASTOS FIXOS MP", [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
]

for nome, vals in despesas_originais:
    c.execute('''
        INSERT INTO matriz_gastos (despesa, janeiro, fevereiro, marco, abril, maio, junho, julho, agosto, setembro, outubro, novembro, dezembro)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (nome, *vals))

# Renda por mês original
rendas = [6820, 6770, 6720.9, 6678.93, 6800, 6800, 6568.74, 6823, 5100, 5100, 5100, 6990]
c.execute('''
    INSERT INTO matriz_totais (tipo, janeiro, fevereiro, marco, abril, maio, junho, julho, agosto, setembro, outubro, novembro, dezembro)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', ("Renda por mês", *rendas))

conn.commit()
conn.close()
print("Banco recriado idêntico à planilha com sucesso!")
