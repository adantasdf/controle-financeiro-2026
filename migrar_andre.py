import os
import sqlite3

DB_PATH = "/home/ubuntu/financeiro/financas.db"
ANO = 2026
TARGET_USER = "andre"

RENDAS = {
    'Janeiro': 6820.0,
    'Fevereiro': 6770.0,
    'Março': 6720.9,
    'Abril': 6678.93,
    'Maio': 6800.0,
    'Junho': 6800.0,
    'Julho': 6568.74,
    'Agosto': 6823.0,
    'Setembro': 5100.0,
    'Outubro': 5100.0,
    'Novembro': 5100.0,
    'Dezembro': 6990.0,
}

DESPESAS = {
    'AGUA': {
        'Abril': (0.0, 0),
        'Agosto': (301.62, 1),
        'Dezembro': (0.0, 0),
        'Fevereiro': (0.0, 0),
        'Janeiro': (0.0, 0),
        'Julho': (124.0, 1),
        'Junho': (0.0, 0),
        'Maio': (240.0, 1),
        'Março': (0.0, 0),
        'Novembro': (0.0, 0),
        'Outubro': (0.0, 0),
        'Setembro': (0.0, 0),
    },
    'ALARME': {
        'Abril': (0.0, 0),
        'Agosto': (100.01, 1),
        'Dezembro': (100.01, 0),
        'Fevereiro': (0.0, 0),
        'Janeiro': (0.0, 0),
        'Julho': (100.01, 1),
        'Junho': (0.0, 0),
        'Maio': (101.0, 1),
        'Março': (0.0, 0),
        'Novembro': (100.01, 0),
        'Outubro': (100.01, 0),
        'Setembro': (100.01, 1),
    },
    'CARREFOUR': {
        'Abril': (2595.0, 1),
        'Agosto': (2700.0, 1),
        'Dezembro': (0.0, 0),
        'Fevereiro': (1999.0, 1),
        'Janeiro': (1544.0, 1),
        'Julho': (2965.0, 1),
        'Junho': (2260.0, 1),
        'Maio': (1860.0, 1),
        'Março': (2890.0, 1),
        'Novembro': (0.0, 0),
        'Outubro': (0.0, 0),
        'Setembro': (3400.0, 1),
    },
    'Celular Raissa': {
        'Abril': (55.0, 1),
        'Agosto': (60.0, 1),
        'Dezembro': (60.0, 0),
        'Fevereiro': (55.0, 1),
        'Janeiro': (55.0, 1),
        'Julho': (60.0, 1),
        'Junho': (60.0, 1),
        'Maio': (61.3, 1),
        'Março': (55.0, 1),
        'Novembro': (60.0, 0),
        'Outubro': (60.0, 0),
        'Setembro': (60.0, 1),
    },
    'ESCOLA ISABELA': {
        'Abril': (668.8, 1),
        'Agosto': (668.8, 1),
        'Dezembro': (668.8, 0),
        'Fevereiro': (668.8, 1),
        'Janeiro': (0.0, 0),
        'Julho': (668.8, 1),
        'Junho': (668.8, 1),
        'Maio': (668.8, 1),
        'Março': (668.8, 1),
        'Novembro': (668.8, 0),
        'Outubro': (668.8, 0),
        'Setembro': (668.8, 0),
    },
    'Emprestimo MP': {
        'Abril': (262.2, 1),
        'Agosto': (0.0, 0),
        'Dezembro': (0.0, 0),
        'Fevereiro': (262.2, 1),
        'Janeiro': (262.2, 1),
        'Julho': (0.0, 0),
        'Junho': (262.2, 0),
        'Maio': (262.2, 1),
        'Março': (262.2, 1),
        'Novembro': (0.0, 0),
        'Outubro': (0.0, 0),
        'Setembro': (0.0, 0),
    },
    'FILTRO DE AGUA + SOFA': {
        'Abril': (240.0, 1),
        'Agosto': (0.0, 0),
        'Dezembro': (0.0, 0),
        'Fevereiro': (240.0, 1),
        'Janeiro': (240.0, 1),
        'Julho': (0.0, 0),
        'Junho': (240.0, 1),
        'Maio': (240.0, 0),
        'Março': (240.0, 1),
        'Novembro': (0.0, 0),
        'Outubro': (0.0, 0),
        'Setembro': (0.0, 0),
    },
    'Faculdade andre': {
        'Abril': (0.0, 0),
        'Agosto': (124.75, 1),
        'Dezembro': (124.75, 0),
        'Fevereiro': (0.0, 0),
        'Janeiro': (0.0, 0),
        'Julho': (124.75, 1),
        'Junho': (0.0, 0),
        'Maio': (0.0, 0),
        'Março': (0.0, 0),
        'Novembro': (124.75, 0),
        'Outubro': (124.75, 0),
        'Setembro': (124.75, 1),
    },
    'GASTOS ANDRE ***': {
        'Abril': (0.0, 0),
        'Agosto': (0.0, 0),
        'Dezembro': (0.0, 0),
        'Fevereiro': (0.0, 0),
        'Janeiro': (0.0, 0),
        'Julho': (0.0, 0),
        'Junho': (0.0, 0),
        'Maio': (54.0, 0),
        'Março': (0.0, 0),
        'Novembro': (0.0, 0),
        'Outubro': (0.0, 0),
        'Setembro': (400.0, 1),
    },
    'GASTOS FIXOS MP': {
        'Abril': (0.0, 0),
        'Agosto': (0.0, 0),
        'Dezembro': (0.0, 0),
        'Fevereiro': (0.0, 0),
        'Janeiro': (0.0, 0),
        'Julho': (0.0, 0),
        'Junho': (0.0, 0),
        'Maio': (0.0, 0),
        'Março': (0.0, 0),
        'Novembro': (0.0, 0),
        'Outubro': (0.0, 0),
        'Setembro': (0.0, 0),
    },
    'IMPOSTO ANUAL': {
        'Abril': (0.0, 0),
        'Agosto': (0.0, 0),
        'Dezembro': (0.0, 0),
        'Fevereiro': (0.0, 0),
        'Janeiro': (0.0, 0),
        'Julho': (0.0, 0),
        'Junho': (0.0, 0),
        'Maio': (0.0, 0),
        'Março': (0.0, 0),
        'Novembro': (0.0, 0),
        'Outubro': (0.0, 0),
        'Setembro': (0.0, 0),
    },
    'INTERNET VIVO': {
        'Abril': (0.0, 0),
        'Agosto': (165.0, 1),
        'Dezembro': (165.0, 0),
        'Fevereiro': (0.0, 0),
        'Janeiro': (0.0, 0),
        'Julho': (165.0, 1),
        'Junho': (160.0, 1),
        'Maio': (127.75, 1),
        'Março': (0.0, 0),
        'Novembro': (165.0, 0),
        'Outubro': (165.0, 0),
        'Setembro': (168.0, 1),
    },
    'IPVA ANDRE': {
        'Abril': (0.0, 0),
        'Agosto': (0.0, 0),
        'Dezembro': (0.0, 0),
        'Fevereiro': (0.0, 0),
        'Janeiro': (0.0, 0),
        'Julho': (0.0, 0),
        'Junho': (0.0, 0),
        'Maio': (0.0, 0),
        'Março': (0.0, 0),
        'Novembro': (0.0, 0),
        'Outubro': (0.0, 0),
        'Setembro': (0.0, 0),
    },
    'IPVA RAISSA': {
        'Abril': (0.0, 0),
        'Agosto': (0.0, 0),
        'Dezembro': (0.0, 0),
        'Fevereiro': (0.0, 0),
        'Janeiro': (0.0, 0),
        'Julho': (0.0, 0),
        'Junho': (0.0, 0),
        'Maio': (0.0, 0),
        'Março': (0.0, 0),
        'Novembro': (0.0, 0),
        'Outubro': (0.0, 0),
        'Setembro': (0.0, 0),
    },
    'LIVROS ISABELA': {
        'Abril': (223.9, 1),
        'Agosto': (223.9, 1),
        'Dezembro': (223.9, 0),
        'Fevereiro': (223.9, 1),
        'Janeiro': (0.0, 0),
        'Julho': (223.9, 1),
        'Junho': (223.9, 1),
        'Maio': (223.9, 1),
        'Março': (223.9, 1),
        'Novembro': (223.9, 0),
        'Outubro': (223.9, 0),
        'Setembro': (223.9, 0),
    },
    'LUZ': {
        'Abril': (0.0, 0),
        'Agosto': (526.12, 1),
        'Dezembro': (0.0, 0),
        'Fevereiro': (0.0, 0),
        'Janeiro': (0.0, 0),
        'Julho': (519.59, 1),
        'Junho': (0.0, 0),
        'Maio': (492.24, 1),
        'Março': (0.0, 0),
        'Novembro': (0.0, 0),
        'Outubro': (0.0, 0),
        'Setembro': (0.0, 0),
    },
    'MATRICULA ISABELA': {
        'Abril': (0.0, 0),
        'Agosto': (0.0, 0),
        'Dezembro': (0.0, 0),
        'Fevereiro': (0.0, 0),
        'Janeiro': (0.0, 0),
        'Julho': (0.0, 0),
        'Junho': (0.0, 0),
        'Maio': (0.0, 0),
        'Março': (0.0, 0),
        'Novembro': (0.0, 0),
        'Outubro': (0.0, 0),
        'Setembro': (0.0, 0),
    },
    'MERCADO PAGO': {
        'Abril': (4293.0, 1),
        'Agosto': (340.0, 1),
        'Dezembro': (340.0, 0),
        'Fevereiro': (4331.0, 1),
        'Janeiro': (3900.0, 1),
        'Julho': (0.0, 0),
        'Junho': (4700.0, 1),
        'Maio': (4670.0, 1),
        'Março': (4840.0, 1),
        'Novembro': (340.0, 0),
        'Outubro': (340.0, 0),
        'Setembro': (1800.0, 1),
    },
    'PARCELA CARRO': {
        'Abril': (3359.41, 1),
        'Agosto': (3359.41, 1),
        'Dezembro': (3359.41, 0),
        'Fevereiro': (3359.41, 1),
        'Janeiro': (3359.41, 1),
        'Julho': (3359.41, 1),
        'Junho': (3359.41, 1),
        'Maio': (3359.41, 1),
        'Março': (3359.41, 1),
        'Novembro': (3359.41, 0),
        'Outubro': (3359.41, 0),
        'Setembro': (3359.41, 1),
    },
    'VAN ISABELA': {
        'Abril': (283.0, 1),
        'Agosto': (283.0, 1),
        'Dezembro': (283.0, 0),
        'Fevereiro': (283.0, 1),
        'Janeiro': (0.0, 0),
        'Julho': (283.0, 1),
        'Junho': (283.0, 1),
        'Maio': (283.0, 1),
        'Março': (283.0, 1),
        'Novembro': (283.0, 0),
        'Outubro': (283.0, 0),
        'Setembro': (283.0, 0),
    },
}


def main():
  if not os.path.exists(DB_PATH):
    print(f"Erro: Banco de dados não encontrado em {DB_PATH}")
    return

  conn = sqlite3.connect(DB_PATH)
  cur = conn.cursor()

  # Busca o ID do usuário andre
  cur.execute("SELECT id FROM usuarios WHERE username = ?", (TARGET_USER,))
  row = cur.fetchone()
  if not row:
    print(f"Erro: Usuário '{TARGET_USER}' não encontrado no banco de dados!")
    conn.close()
    return

  user_id = row[0]
  print(f"Migrando dados para o usuário: {TARGET_USER} (ID: {user_id})")

  # Limpa o template padrão que foi criado no cadastro para o ano de 2026
  cur.execute(
      "DELETE FROM despesas WHERE user_id = ? AND ano = ?", (user_id, ANO)
  )
  cur.execute(
      "DELETE FROM rendas WHERE user_id = ? AND ano = ?", (user_id, ANO)
  )

  # Insere as rendas da planilha
  for mes, val in RENDAS.items():
    cur.execute(
        """
            INSERT INTO rendas (user_id, mes, ano, valor)
            VALUES (?, ?, ?, ?)
        """,
        (user_id, mes, ANO, val),
    )

  # Insere as despesas com o status de pago
  total_despesas = 0
  for cat, meses_data in DESPESAS.items():
    for mes, (val, pago) in meses_data.items():
      cur.execute(
          """
                INSERT INTO despesas (user_id, categoria, mes, ano, valor, pago)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
          (user_id, cat, mes, ANO, val, pago),
      )
      total_despesas += 1

  conn.commit()
  conn.close()
  print(
      f"✅ Migração concluída com sucesso! ({total_despesas} despesas e"
      f" {len(RENDAS)} rendas migradas para '{TARGET_USER}')"
  )


if __name__ == "__main__":
  main()
