from datetime import datetime
import hashlib
import io
import os
import secrets
import sqlite3
import time
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Controle Financeiro 2026",
    page_icon="💰",
    layout="wide"
)

# --- CONSTANTES E BANCO DE DADOS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "financas.db")
ANO = 2026
TIMEOUT_SESSAO = 300  # 5 minutos em segundos

MESES = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

CATEGORIAS_TEMPLATE = [
    "Moradia (Aluguel / Condomínio)",
    "Energia Elétrica",
    "Água & Saneamento",
    "Internet & Celular",
    "Supermercado & Alimentação",
    "Transporte & Combustível",
    "Cartão de Crédito",
    "Assinaturas & Lazer"
]

def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def hash_senha(senha: str) -> str:
    salt = "financas_sec_salt_2026_"
    return hashlib.sha256((salt + senha).encode("utf-8")).hexdigest()

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        senha_hash TEXT NOT NULL,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessoes (
        token TEXT PRIMARY KEY,
        user_id INTEGER NOT NULL,
        username TEXT NOT NULL,
        expira_em REAL NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS despesas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL DEFAULT 1,
        categoria TEXT NOT NULL,
        mes TEXT NOT NULL,
        ano INTEGER NOT NULL,
        valor REAL NOT NULL,
        pago INTEGER DEFAULT 0,
        UNIQUE(user_id, categoria, mes, ano)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rendas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL DEFAULT 1,
        mes TEXT NOT NULL,
        ano INTEGER NOT NULL,
        valor REAL NOT NULL,
        UNIQUE(user_id, mes, ano)
    )
    """)

    cursor.execute("DELETE FROM sessoes WHERE expira_em < ?", (time.time(),))
    conn.commit()
    conn.close()

init_db()

# --- SESSÕES PERSISTENTES (F5-PROOF) ---
def criar_sessao(user_id: int, username: str):
    token = secrets.token_urlsafe(24)
    expira = time.time() + TIMEOUT_SESSAO
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO sessoes (token, user_id, username, expira_em) VALUES (?, ?, ?, ?)",
                   (token, user_id, username, expira))
    conn.commit()
    conn.close()
    st.query_params["s"] = token
    st.session_state["user_id"] = user_id
    st.session_state["usuario_logado"] = username

    idx_mes = datetime.now().month - 1
    st.session_state["filtro_meses_mult"] = [MESES[idx_mes]]

def encerrar_sessao():
    token = st.query_params.get("s")
    if token:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessoes WHERE token = ?", (token,))
        conn.commit()
        conn.close()
        del st.query_params["s"]
    st.session_state.clear()

def verificar_sessao():
    token = st.query_params.get("s")
    if not token:
        return None

    agora = time.time()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, expira_em FROM sessoes WHERE token = ?", (token,))
    row = cursor.fetchone()

    if row:
        user_id, username, expira_em = row
        if agora <= expira_em:
            novo_expira = agora + TIMEOUT_SESSAO
            cursor.execute("UPDATE sessoes SET expira_em = ? WHERE token = ?", (novo_expira, token))
            conn.commit()
            conn.close()
            st.session_state["user_id"] = user_id
            st.session_state["usuario_logado"] = username
            return user_id, username
        else:
            cursor.execute("DELETE FROM sessoes WHERE token = ?", (token,))
            conn.commit()

    conn.close()
    if "s" in st.query_params:
        del st.query_params["s"]
    st.session_state.clear()
    return None

sessao_ativa = verificar_sessao()

# --- AUTENTICAÇÃO E GESTÃO DE USUÁRIO ---
def semear_dados_iniciais(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    for m in MESES:
        cursor.execute("""
            INSERT OR IGNORE INTO rendas (user_id, mes, ano, valor)
            VALUES (?, ?, ?, 0.0)
        """, (user_id, m, ANO))
        for cat in CATEGORIAS_TEMPLATE:
            cursor.execute("""
                INSERT OR IGNORE INTO despesas (user_id, categoria, mes, ano, valor, pago)
                VALUES (?, ?, ?, ?, 0.0, 0)
            """, (user_id, cat, m, ANO))
    conn.commit()
    conn.close()

def autenticar_usuario(username: str, senha: str):
    conn = get_connection()
    cursor = conn.cursor()
    h = hash_senha(senha)
    cursor.execute("SELECT id, username FROM usuarios WHERE username = ? AND senha_hash = ?", (username, h))
    user = cursor.fetchone()
    conn.close()
    return user

def alterar_senha_usuario(user_id: int, senha_atual: str, nova_senha: str):
    conn = get_connection()
    cursor = conn.cursor()
    h_atual = hash_senha(senha_atual)
    cursor.execute("SELECT id FROM usuarios WHERE id = ? AND senha_hash = ?", (user_id, h_atual))
    if not cursor.fetchone():
        conn.close()
        return False, "Senha atual incorreta."
    
    h_nova = hash_senha(nova_senha)
    cursor.execute("UPDATE usuarios SET senha_hash = ? WHERE id = ?", (h_nova, user_id))
    conn.commit()
    conn.close()
    return True, "Senha alterada com sucesso!"

def registrar_usuario(username: str, senha: str):
    conn = get_connection()
    cursor = conn.cursor()
    h = hash_senha(senha)
    try:
        cursor.execute("INSERT INTO usuarios (username, senha_hash) VALUES (?, ?)", (username, h))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        semear_dados_iniciais(user_id)
        return True, "Usuário cadastrado com sucesso!"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Este nome de usuário já está em uso. Escolha outro."

def render_auth_page():
    col1, col2, col3 = st.columns([1, 1.8, 1])
    with col2:
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 20px;">
                <h2 style="margin-bottom: 2px;">Painel Financeiro 2026</h2>
                <p style="color: #888888; font-size: 0.95rem; margin-top: 0;">Desenvolvido por André Dantas</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        tab_login, tab_cadastro = st.tabs(["🔐 Entrar", "✨ Criar Conta"])

        with tab_login:
            with st.form("form_login"):
                st.write("Acesse suas finanças:")
                user_login = st.text_input("Usuário")
                pwd_login = st.text_input("Senha", type="password")
                btn_login = st.form_submit_button("Entrar no Painel", use_container_width=True)

                if btn_login:
                    user_record = autenticar_usuario(user_login.strip(), pwd_login)
                    if user_record:
                        criar_sessao(user_record[0], user_record[1])
                        st.rerun()
                    else:
                        st.error("Usuário ou senha incorretos.")

        with tab_cadastro:
            with st.form("form_cadastro"):
                st.write("Crie sua conta pessoal:")
                user_novo = st.text_input("Novo Usuário")
                pwd_novo = st.text_input("Nova Senha", type="password")
                pwd_confirma = st.text_input("Confirmar Senha", type="password")
                btn_cadastrar = st.form_submit_button("Cadastrar e Iniciar", use_container_width=True)

                if btn_cadastrar:
                    user_limpo = user_novo.strip()
                    if not user_limpo or not pwd_novo or not pwd_confirma:
                        st.warning("Preencha todos os campos.")
                    elif len(pwd_novo) < 4:
                        st.warning("A senha deve ter pelo menos 4 caracteres.")
                    elif pwd_novo != pwd_confirma:
                        st.error("As senhas não coincidem.")
                    else:
                        sucesso, msg = registrar_usuario(user_limpo, pwd_novo)
                        if sucesso:
                            user_record = autenticar_usuario(user_limpo, pwd_novo)
                            criar_sessao(user_record[0], user_record[1])
                            st.rerun()
                        else:
                            st.error(msg)

if not sessao_ativa:
    render_auth_page()
    st.stop()

# --- SESSÃO DO USUÁRIO ---
USER_ID = st.session_state["user_id"]
USUARIO = st.session_state["usuario_logado"]

st.sidebar.caption(f"Conectado como: **{USUARIO}**")
if st.sidebar.button("Sair (Logout)", use_container_width=True):
    encerrar_sessao()
    st.rerun()

st.sidebar.divider()

# --- OPERAÇÕES COM DADOS ---
def carregar_dados():
    conn = get_connection()
    df_desp = pd.read_sql_query(
        "SELECT categoria, mes, valor, pago FROM despesas WHERE user_id = ? AND ano = ?",
        conn, params=(USER_ID, ANO)
    )
    df_renda = pd.read_sql_query(
        "SELECT mes, valor FROM rendas WHERE user_id = ? AND ano = ?",
        conn, params=(USER_ID, ANO)
    )
    conn.close()

    if df_desp.empty:
        df_pivot = pd.DataFrame(columns=["Despesa"] + MESES)
        df_pago = pd.DataFrame(columns=["Despesa"] + MESES)
        totais = [0.0] * 12
    else:
        df_pivot = df_desp.pivot(index="categoria", columns="mes", values="valor").fillna(0.0)
        df_pago = df_desp.pivot(index="categoria", columns="mes", values="pago").fillna(0)
        
        for m in MESES:
            if m not in df_pivot.columns:
                df_pivot[m] = 0.0
            if m not in df_pago.columns:
                df_pago[m] = 0
                
        df_pivot = df_pivot[MESES].reset_index().rename(columns={"categoria": "Despesa"})
        df_pago = df_pago[MESES].reset_index().rename(columns={"categoria": "Despesa"})
        totais = [df_desp[df_desp["mes"] == m]["valor"].sum() for m in MESES]

    rendas_dict = dict(zip(df_renda["mes"], df_renda["valor"])) if not df_renda.empty else {}
    rendas = [rendas_dict.get(m, 0.0) for m in MESES]
    sobras = [r - t for r, t in zip(rendas, totais)]

    df_resumo = pd.DataFrame({
        "Mês": MESES,
        "Total Gasto": totais,
        "Renda": rendas,
        "Sobra": sobras
    })

    return df_desp, df_pivot, df_pago, df_resumo, rendas_dict

def salvar_gasto(categoria: str, meses_alvo: list, valor: float, pago: bool):
    conn = get_connection()
    cursor = conn.cursor()
    pago_int = 1 if pago else 0
    for m in meses_alvo:
        cursor.execute("""
            INSERT INTO despesas (user_id, categoria, mes, ano, valor, pago)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, categoria, mes, ano) DO UPDATE SET 
                valor = excluded.valor,
                pago = excluded.pago
        """, (USER_ID, categoria, m, ANO, valor, pago_int))
    conn.commit()
    conn.close()

def salvar_renda(meses_alvo: list, novo_valor: float):
    conn = get_connection()
    cursor = conn.cursor()
    for m in meses_alvo:
        cursor.execute("""
            INSERT INTO rendas (user_id, mes, ano, valor)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, mes, ano) DO UPDATE SET valor = excluded.valor
        """, (USER_ID, m, ANO, novo_valor))
    conn.commit()
    conn.close()

def adicionar_categoria(categoria: str, meses_alvo: list):
    conn = get_connection()
    cursor = conn.cursor()
    for m in meses_alvo:
        cursor.execute("""
            INSERT OR IGNORE INTO despesas (user_id, categoria, mes, ano, valor, pago)
            VALUES (?, ?, ?, ?, 0.0, 0)
        """, (USER_ID, categoria, m, ANO))
    conn.commit()
    conn.close()

def remover_categoria(categoria: str, meses_alvo: list):
    conn = get_connection()
    cursor = conn.cursor()
    for m in meses_alvo:
        cursor.execute(
            "DELETE FROM despesas WHERE user_id = ? AND categoria = ? AND mes = ? AND ano = ?",
            (USER_ID, categoria, m, ANO)
        )
    conn.commit()
    conn.close()

# --- CARREGAR ESTADO ---
st.markdown(
    "<h1 style='text-align: center;'>Painel Financeiro 2026</h1>",
    unsafe_allow_html=True
)
df_desp_raw, df_despesas, df_pago, df_resumo, rendas_dict = carregar_dados()

# --- SELETOR MULTI-MÊS NA BARRA LATERAL ---
st.sidebar.header("Filtro de Meses")

idx_mes_atual = datetime.now().month - 1
mes_vigente = MESES[idx_mes_atual]

col_btn1, col_btn2 = st.sidebar.columns(2)
if col_btn1.button("Todos os Meses", use_container_width=True):
    st.session_state["filtro_meses_mult"] = MESES
    st.rerun()

if col_btn2.button("Mês Atual", use_container_width=True):
    st.session_state["filtro_meses_mult"] = [mes_vigente]
    st.rerun()

if "filtro_meses_mult" not in st.session_state:
    st.session_state["filtro_meses_mult"] = [mes_vigente]

selecao_bruta = st.sidebar.multiselect(
    "Meses Visíveis:",
    options=MESES,
    key="filtro_meses_mult"
)

meses_ativos = [m for m in MESES if m in selecao_bruta]
if not meses_ativos:
    meses_ativos = [mes_vigente]

rotulo_acao = ", ".join(meses_ativos) if len(meses_ativos) <= 2 else f"{len(meses_ativos)} meses selecionados"

if not df_desp_raw.empty:
    categorias_disponiveis = sorted(df_desp_raw[df_desp_raw["mes"].isin(meses_ativos)]["categoria"].unique().tolist())
else:
    categorias_disponiveis = []

st.sidebar.divider()
st.sidebar.subheader(f"Lançar / Atualizar ({rotulo_acao})")

if categorias_disponiveis:
    cat_sel = st.sidebar.selectbox("Despesa", categorias_disponiveis)
    
    sub_df = df_desp_raw[(df_desp_raw["categoria"] == cat_sel) & (df_desp_raw["mes"].isin(meses_ativos))]
    sub_com_valor = sub_df[sub_df["valor"] > 0]
    val_atual = float(sub_com_valor["valor"].iloc[-1]) if not sub_com_valor.empty else 0.0
    pago_atual = bool(sub_df["pago"].iloc[-1]) if (len(meses_ativos) == 1 and not sub_df.empty) else False

    novo_valor = st.sidebar.number_input("Valor (R$)", value=val_atual, step=10.0, format="%.2f")
    marcado_pago = st.sidebar.checkbox("✅ Marcar como Pago", value=pago_atual)

    texto_btn = f"Salvar em {meses_ativos[0]}" if len(meses_ativos) == 1 else f"Aplicar aos {len(meses_ativos)} Meses"
    if st.sidebar.button(texto_btn, use_container_width=True):
        salvar_gasto(cat_sel, meses_ativos, novo_valor, marcado_pago)
        st.sidebar.success(f"{cat_sel} salvo nos meses selecionados (R$ {novo_valor:,.2f})!")
        st.rerun()
else:
    st.sidebar.info("Nenhuma despesa encontrada nos meses selecionados.")

# Ajuste de Renda
st.sidebar.divider()
st.sidebar.subheader("Ajustar Renda")
renda_ref = float(rendas_dict.get(meses_ativos[0], 0.0)) if meses_ativos else 0.0
nova_renda = st.sidebar.number_input("Renda Mensal (R$)", value=renda_ref, step=50.0, format="%.2f")

texto_btn_renda = f"Salvar Renda em {meses_ativos[0]}" if len(meses_ativos) == 1 else f"Replicar Renda para {len(meses_ativos)} Meses"
if st.sidebar.button(texto_btn_renda, use_container_width=True):
    salvar_renda(meses_ativos, nova_renda)
    st.sidebar.success(f"Renda atualizada para R$ {nova_renda:,.2f}!")
    st.rerun()

# Nova Despesa
st.sidebar.divider()
st.sidebar.subheader("Nova Despesa")
nova_cat = st.sidebar.text_input("Nome da despesa", placeholder="Ex: Farmácia, Academia")
if st.sidebar.button("Adicionar aos Meses Selecionados", use_container_width=True):
    nome_limpo = nova_cat.strip()
    if nome_limpo:
        adicionar_categoria(nome_limpo, meses_ativos)
        st.sidebar.success(f"'{nome_limpo}' adicionada!")
        st.rerun()

# Remover Despesa
if categorias_disponiveis:
    st.sidebar.divider()
    st.sidebar.subheader("Remover Despesa")
    cat_para_remover = st.sidebar.selectbox("Selecione para remover", categorias_disponiveis, key="del_cat_mult")
    if st.sidebar.button("🗑️ Remover dos Meses Selecionados", use_container_width=True):
        remover_categoria(cat_para_remover, meses_ativos)
        st.sidebar.success(f"'{cat_para_remover}' removida!")
        st.rerun()

# --- SEGURANÇA: ALTERAÇÃO DE SENHA NA SIDEBAR ---
st.sidebar.divider()
with st.sidebar.expander("🔑 Alterar Senha"):
    with st.form("form_mudar_senha"):
        pwd_atual = st.text_input("Senha Atual", type="password")
        pwd_nova1 = st.text_input("Nova Senha", type="password")
        pwd_nova2 = st.text_input("Confirmar Nova Senha", type="password")
        btn_alterar = st.form_submit_button("Atualizar Senha", use_container_width=True)

        if btn_alterar:
            if not pwd_atual or not pwd_nova1 or not pwd_nova2:
                st.warning("Preencha todos os campos de senha.")
            elif len(pwd_nova1) < 4:
                st.warning("A nova senha deve ter no mínimo 4 caracteres.")
            elif pwd_nova1 != pwd_nova2:
                st.error("As novas senhas não coincidem.")
            else:
                ok, msg = alterar_senha_usuario(USER_ID, pwd_atual, pwd_nova1)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

# --- CONTROLE DE PRIVACIDADE ---
if "mostrar_valores" not in st.session_state:
    st.session_state["mostrar_valores"] = True

def toggle_visibilidade():
    st.session_state["mostrar_valores"] = not st.session_state["mostrar_valores"]

def formatar_valor(valor: float, delta: bool = False) -> str:
    if st.session_state["mostrar_valores"]:
        return f"R$ {valor:,.2f}" if not delta else f"{valor:,.2f}"
    return "R$ ••••••" if not delta else "••••••"

# --- INDICADORES CONSOLIDADOS DINÂMICOS ---
col_titulo, col_btn = st.columns([0.88, 0.12])

with col_titulo:
    if len(meses_ativos) == 1:
        st.subheader(f"Indicadores de {meses_ativos[0]}")
    elif len(meses_ativos) == 12:
        st.subheader("Indicadores Consolidados Anuais (2026)")
    else:
        st.subheader(f"Indicadores Consolidados: {rotulo_acao}")

with col_btn:
    rotulo_olho = "👁️ Ocultar" if st.session_state["mostrar_valores"] else "🙈 Mostrar"
    st.button(rotulo_olho, on_click=toggle_visibilidade, use_container_width=True)

df_resumo_filtrado = df_resumo[df_resumo["Mês"].isin(meses_ativos)]
total_gasto_sel = df_resumo_filtrado["Total Gasto"].sum()
total_renda_sel = df_resumo_filtrado["Renda"].sum()
total_sobra_sel = df_resumo_filtrado["Sobra"].sum()

conn = get_connection()
cursor = conn.cursor()
placeholders = ",".join("?" * len(meses_ativos))
cursor.execute(
    f"SELECT SUM(valor) FROM despesas WHERE user_id = ? AND ano = ? AND pago = 1 AND mes IN ({placeholders})",
    [USER_ID, ANO] + meses_ativos
)
total_pago_sel = cursor.fetchone()[0] or 0.0
conn.close()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Renda Total", formatar_valor(total_renda_sel))
c2.metric("Total Previsto", formatar_valor(total_gasto_sel))
c3.metric("Total Quitado", formatar_valor(total_pago_sel))
c4.metric(
    "Balanço / Sobra", 
    formatar_valor(total_sobra_sel), 
    delta=formatar_valor(total_sobra_sel, delta=True), 
    delta_color="normal"
)

st.divider()

# --- GRÁFICOS ---
col_graf, col_evol = st.columns([1, 1])

with col_graf:
    st.subheader("Maiores Despesas (Período Selecionado)")
    df_desp_filtrado = df_desp_raw[df_desp_raw["mes"].isin(meses_ativos)]
    if not df_desp_filtrado.empty:
        df_agrup = df_desp_filtrado.groupby("categoria", as_index=False)["valor"].sum()
        df_agrup = df_agrup[df_agrup["valor"] > 0].sort_values(by="valor", ascending=True)
        if not df_agrup.empty:
            fig_bar = px.bar(
                df_agrup, x="valor", y="categoria", orientation="h",
                text_auto=".2f", labels={"valor": "R$", "categoria": "Despesa"}
            )
            fig_bar.update_layout(xaxis_tickprefix="R$ ")
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Nenhum gasto com valor registrado no período.")
    else:
        st.info("Nenhum dado encontrado.")

with col_evol:
    st.subheader("Evolução Mensal (Renda vs Gasto)")
    fig_evol = px.line(df_resumo_filtrado, x="Mês", y=["Total Gasto", "Renda"], markers=True)
    fig_evol.update_layout(yaxis_tickprefix="R$ ")
    st.plotly_chart(fig_evol, use_container_width=True)

# --- TABELA DE DESPESAS COM ORDENAÇÃO DINÂMICA (PENDÊNCIAS NO TOPO) ---
st.subheader(f"Tabela de Despesas ({rotulo_acao})")

if not df_despesas.empty:
    colunas_tabela = ["Despesa"] + meses_ativos
    df_exibicao = df_despesas[colunas_tabela].copy()

    pago_indexed = df_pago.set_index("Despesa")
    valor_indexed = df_despesas.set_index("Despesa")

    mes_foco = meses_ativos[0]

    def classificar_status(nome_despesa):
        if nome_despesa not in pago_indexed.index or nome_despesa not in valor_indexed.index:
            return 1

        foi_pago = pago_indexed.loc[nome_despesa, mes_foco]
        valor_mes = valor_indexed.loc[nome_despesa, mes_foco]

        if foi_pago == 1:
            return 2  # Quitado
        elif valor_mes > 0:
            return 0  # Pendente ativo
        else:
            return 1  # R$ 0,00

    df_exibicao["_ordem_prioridade"] = df_exibicao["Despesa"].apply(classificar_status)

    df_exibicao = df_exibicao.sort_values(
        by=["_ordem_prioridade", "Despesa"], 
        ascending=[True, True]
    ).reset_index(drop=True)

    df_exibicao["Despesa"] = df_exibicao.apply(
        lambda r: f"✅ {r['Despesa']}" if r["_ordem_prioridade"] == 2 else r["Despesa"],
        axis=1
    )
    df_exibicao = df_exibicao.drop(columns=["_ordem_prioridade"])

    def colorir_celulas_pagas(val_df):
        estilo = pd.DataFrame('', index=val_df.index, columns=val_df.columns)
        for row_idx in val_df.index:
            nome_original = val_df.loc[row_idx, "Despesa"].replace("✅ ", "")
            if nome_original in pago_indexed.index:
                for m in meses_ativos:
                    if m in pago_indexed.columns and pago_indexed.loc[nome_original, m] == 1:
                        estilo.loc[row_idx, m] = 'background-color: #1e4620; color: #a3e635; font-weight: bold;'
        return estilo

    st.caption("🟢 Valores em verde indicam pagamentos quitados. Contas a pagar permanecem no topo.")
    styled_df = df_exibicao.style\
        .format({m: "R$ {:,.2f}" for m in meses_ativos})\
        .apply(colorir_celulas_pagas, axis=None)

    st.dataframe(styled_df, use_container_width=True)

    # --- SEÇÃO DE EXPORTAÇÃO (EXCEL & CSV) ---
    st.divider()
    col_exp1, col_exp2, col_vazio = st.columns([1.5, 1.5, 4])

    # Gera buffer Excel em memória com duas abas: Despesas e Resumo Mensal
    buffer_excel = io.BytesIO()
    with pd.ExcelWriter(buffer_excel, engine="openpyxl") as writer:
        df_despesas.to_excel(writer, index=False, sheet_name="Despesas 2026")
        df_resumo.to_excel(writer, index=False, sheet_name="Resumo Anual")
    bytes_excel = buffer_excel.getvalue()

    # Gera CSV da tabela corrente
    csv_bytes = df_exibicao.to_csv(index=False).encode("utf-8-sig")

    with col_exp1:
        st.download_button(
            label="📥 Baixar Excel Completo (.xlsx)",
            data=bytes_excel,
            file_name=f"Financas_2026_{USUARIO}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    with col_exp2:
        st.download_button(
            label="📄 Baixar Tabela (.csv)",
            data=csv_bytes,
            file_name=f"Despesas_{USUARIO}_{rotulo_acao}.csv",
            mime="text/csv",
            use_container_width=True
        )

# --- ASSINATURA / CRÉDITOS NO RODAPÉ DA SIDEBAR ---
st.sidebar.markdown("---")
st.sidebar.markdown(
    "<div style='text-align: center; color: #888888; font-size: 0.82rem;'>"
    "🛠️ <b>Sistema desenvolvido por André Dantas</b><br>"
    "Versão 2026 • Todos os direitos reservados"
    "</div>",
    unsafe_allow_html=True
)
