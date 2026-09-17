import sqlite3

DB_NAME = "financeiro.db"

# 1. Rendas por mês extraídas da planilha
rendas_2026 = {
    "2026-01": 6820.0,
    "2026-02": 6770.0,
    "2026-03": 6720.90,
    "2026-04": 6678.93,
    "2026-05": 6800.0,
    "2026-06": 6800.0,
    "2026-07": 6568.74,
    "2026-08": 6823.0,
    "2026-09": 5100.0,
    "2026-10": 5100.0,
    "2026-11": 5100.0,
    "2026-12": 6990.0
}

# 2. Classificação de Categorias
def classificar(nome):
    n = nome.upper()
    if 'CARREFOUR' in n or 'MERCADO PAGO' in n:
        return 'Cartão de Crédito'
    elif 'EMPRESTIMO' in n:
        return 'Empréstimos'
    elif 'VIVO' in n or 'CELULAR' in n or 'ALARME' in n:
        return 'Serviços & Telefonia'
    elif 'ISABELA' in n:
        return 'Educação / Filhos'
    elif 'CARRO' in n or 'IPVA' in n:
        return 'Transporte'
    elif 'LUZ' in n or 'AGUA' in n or 'FILTRO' in n:
        return 'Moradia & Utilidades'
    elif 'FACULDADE' in n:
        return 'Educação'
    return 'Outros'

# 3. Matriz de gastos mês a mês (Jan a Dez/2026)
gastos_matriz = [
    ("CARREFOUR", [1544, 1999, 2890, 2595, 1860, 2260, 2965, 2700, 3400, 0, 0, 0]),
    ("Emprestimo MP", [262.2, 262.2, 262.2, 262.2, 262.2, 262.2, 0, 0, 0, 0, 0, 0]),
    ("MERCADO PAGO", [3900, 4331, 4840, 4293, 4670, 4700, 0, 340, 1800, 340, 340, 340]),
    ("INTERNET VIVO", [0, 0, 0, 0, 127.75, 160, 165, 165, 168, 165, 165, 165]),
    ("Celular Raissa", [55, 55, 55, 55, 61.3, 60, 60, 60, 60, 60, 60, 60]),
    ("VAN ISABELA", [0, 283, 283, 283, 283, 283, 283, 283, 283, 283, 283, 283]),
    ("ESCOLA ISABELA", [0, 668.8, 668.8, 668.8, 668.8, 668.8, 668.8, 668.8, 668.8, 668.8, 668.8, 668.8]),
    ("LIVROS ISABELA", [0, 223.9, 223.9, 223.9, 223.9, 223.9, 223.9, 223.9, 223.9, 223.9, 223.9, 223.9]),
    ("PARCELA CARRO", [3359.41, 3359.41, 3359.41, 3359.41, 3359.41, 3359.41, 3359.41, 3359.41, 3359.41, 3359.41, 3359.41, 3359.41]),
    ("ALARME", [0, 0, 0, 0, 101, 0, 100.01, 100.01, 100.01, 100.01, 100.01, 100.01]),
    ("LUZ", [0, 0, 0, 0, 492.24, 0, 519.59, 526.12, 0, 0, 0, 0]),
    ("AGUA", [0, 0, 0, 0, 240, 0, 124, 301.62, 0, 0, 0, 0]),
    ("FILTRO DE AGUA + SOFA", [240, 240, 240, 240, 240, 240, 0, 0, 0, 0, 0, 0]),
    ("Faculdade andre", [0, 0, 0, 0, 0, 0, 124.75, 124.75, 124.75, 124.75, 124.75, 124.75]),
    ("GASTOS ANDRE ***", [0, 0, 0, 0, 54, 0, 0, 0, 400, 0, 0, 0])
]

conn = sqlite3.connect(DB_NAME)
c = conn.cursor()

# Garantir criação das tabelas
c.execute("""CREATE TABLE IF NOT EXISTS rendas_mensais (mes_ano TEXT PRIMARY KEY, renda REAL DEFAULT 0.0)""")
c.execute("""CREATE TABLE IF NOT EXISTS transacoes (id INTEGER PRIMARY KEY AUTOINCREMENT, mes_ano TEXT, data TEXT, tipo TEXT, categoria TEXT, descricao TEXT, valor REAL, pago INTEGER DEFAULT 0)""")
c.execute("""CREATE TABLE IF NOT EXISTS categorias (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE)""")

# Limpar dados antigos caso queira reiniciar limpo
c.execute("DELETE FROM transacoes")
c.execute("DELETE FROM rendas_mensais")

# 1. Inserir Rendas
for mes_ano, r in rendas_2026.items():
    c.execute("INSERT OR REPLACE INTO rendas_mensais (mes_ano, renda) VALUES (?, ?)", (mes_ano, r))

# 2. Inserir Categorias
categorias_set = set(classificar(d[0]) for d in gastos_matriz)
for cat in categorias_set:
    c.execute("INSERT OR IGNORE INTO categorias (nome) VALUES (?)", (cat,))

# 3. Inserir Despesas
total_registros = 0
for nome_conta, valores in gastos_matriz:
    categoria = classificar(nome_conta)
    for mes_idx, val in enumerate(valores):
        if val and float(val) > 0:
            mes_num = str(mes_idx + 1).zfill(2)
            mes_ano = f"2026-{mes_num}"
            data_lancamento = f"{mes_ano}-10"
            # Jan a Ago como pagos (1), Setembro em diante como pendentes (0)
            pago = 1 if (mes_idx + 1) < 9 else 0
            c.execute("""
                INSERT INTO transacoes (mes_ano, data, tipo, categoria, descricao, valor, pago)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (mes_ano, data_lancamento, "Despesa", categoria, nome_conta, float(val), pago))
            total_registros += 1

conn.commit()
conn.close()

print(f"Migração concluída com sucesso! {total_registros} despesas e 12 meses de renda inseridos.")
