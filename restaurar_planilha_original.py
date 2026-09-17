import sqlite3

DB_NAME = "/root/financeiro/financeiro.db"
conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

c.execute("DROP TABLE IF EXISTS matriz_gastos")
c.execute("DROP TABLE IF EXISTS matriz_totais")
c.execute("DROP TABLE IF EXISTS matriz_pagos")

c.execute('''
    CREATE TABLE matriz_gastos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        despesa TEXT UNIQUE,
        janeiro REAL,
        fevereiro REAL,
        marco REAL,
        abril REAL,
        maio REAL,
        junho REAL,
        julho REAL,
        agosto REAL,
        setembro REAL,
        outubro REAL,
        novembro REAL,
        dezembro REAL
    )
''')

c.execute('''
    CREATE TABLE matriz_totais (
        tipo TEXT PRIMARY KEY,
        janeiro REAL,
        fevereiro REAL,
        marco REAL,
        abril REAL,
        maio REAL,
        junho REAL,
        julho REAL,
        agosto REAL,
        setembro REAL,
        outubro REAL,
        novembro REAL,
        dezembro REAL
    )
''')

c.execute('''
    CREATE TABLE matriz_pagos (
        despesa_id INTEGER,
        mes TEXT,
        pago INTEGER DEFAULT 0,
        PRIMARY KEY (despesa_id, mes)
    )
''')

# Matriz exata da planilha "Gastos mes a mes 2026.xlsx"
planilha_gastos = [
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

for nome, vals in planilha_gastos:
    c.execute('''
        INSERT INTO matriz_gastos (despesa, janeiro, fevereiro, marco, abril, maio, junho, julho, agosto, setembro, outubro, novembro, dezembro)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (nome, *vals))

# Rendas originais
rendas = [6820, 6770, 6720.9, 6678.93, 6800, 6800, 6568.74, 6823, 5100, 5100, 5100, 6990]
c.execute('''
    INSERT INTO matriz_totais (tipo, janeiro, fevereiro, marco, abril, maio, junho, julho, agosto, setembro, outubro, novembro, dezembro)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', ("Renda por mês", *rendas))

conn.commit()
conn.close()
print("Planilha original restaurada com sucesso no SQLite!")
