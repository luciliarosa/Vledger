import streamlit as st
import sqlite3
from datetime import datetime

# =========================================
# Página: Empresas
# =========================================
st.set_page_config(page_title="Empresas | Vledger", page_icon="🏢", layout="wide")

st.title("🏢 Empresas")
st.caption("Gerencie as empresas cadastradas no Vledger")

# =========================================
# Funções auxiliares de banco de dados
# =========================================
def conectar():
    conn = sqlite3.connect("vledger.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS empresas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_empresa TEXT NOT NULL,
            cnpj TEXT,
            responsavel TEXT,
            data_cadastro TEXT
        )
    """)
    return conn

def inserir_empresa(nome, cnpj, responsavel):
    conn = conectar()
    data_cadastro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute("INSERT INTO empresas (nome_empresa, cnpj, responsavel, data_cadastro) VALUES (?, ?, ?, ?)",
                 (nome, cnpj, responsavel, data_cadastro))
    conn.commit()
    conn.close()

def listar_empresas():
    conn = conectar()
    empresas = conn.execute("SELECT * FROM empresas ORDER BY nome_empresa").fetchall()
    conn.close()
    return empresas

def atualizar_empresa(emp_id, nome, cnpj, responsavel):
    conn = conectar()
    conn.execute("UPDATE empresas SET nome_empresa=?, cnpj=?, responsavel=? WHERE id=?",
                 (nome, cnpj, responsavel, emp_id))
    conn.commit()
    conn.close()

def excluir_empresa(emp_id):
    conn = conectar()
    conn.execute("DELETE FROM empresas WHERE id=?", (emp_id,))
    conn.commit()
    conn.close()

# =========================================
# Layout principal
# =========================================

tab1, tab2, tab3 = st.tabs(["➕ Adicionar", "📋 Empresas Cadastradas", "⚙️ Editar / Excluir"])

# ----------------------------
# Aba 1 - Adicionar
# ----------------------------
with tab1:
    st.subheader("Adicionar nova empresa")

    with st.form("form_add_empresa", clear_on_submit=True):
        nome = st.text_input("Nome da empresa *")
        cnpj = st.text_input("CNPJ")
        responsavel = st.text_input("Responsável")
        submitted = st.form_submit_button("Salvar")

        if submitted:
            if nome.strip() == "":
                st.warning("O nome da empresa é obrigatório.")
            else:
                inserir_empresa(nome, cnpj, responsavel)
                st.success(f"Empresa **{nome}** cadastrada com sucesso!")

# ----------------------------
# Aba 2 - Listagem
# ----------------------------
with tab2:
    st.subheader("Empresas cadastradas")
    empresas = listar_empresas()

    if len(empresas) == 0:
        st.info("Nenhuma empresa cadastrada até o momento.")
    else:
        st.dataframe(
            empresas,
            column_config={
                0: "ID",
                1: "Nome da Empresa",
                2: "CNPJ",
                3: "Responsável",
                4: "Data de Cadastro",
            },
            use_container_width=True,
            hide_index=True,
        )

# ----------------------------
# Aba 3 - Editar / Excluir
# ----------------------------
with tab3:
    st.subheader("Editar ou excluir empresa")

    empresas = listar_empresas()
    if len(empresas) == 0:
        st.info("Nenhuma empresa cadastrada.")
    else:
        emp_dict = {f"{e[1]} (ID: {e[0]})": e for e in empresas}
        escolha = st.selectbox("Selecione a empresa", list(emp_dict.keys()))
        emp = emp_dict[escolha]

        nome_edit = st.text_input("Nome da empresa", emp[1])
        cnpj_edit = st.text_input("CNPJ", emp[2] or "")
        responsavel_edit = st.text_input("Responsável", emp[3] or "")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Salvar alterações"):
                atualizar_empresa(emp[0], nome_edit, cnpj_edit, responsavel_edit)
                st.success("Empresa atualizada com sucesso!")
                st.experimental_rerun()
        with col2:
            if st.button("🗑️ Excluir empresa"):
                excluir_empresa(emp[0])
                st.warning(f"Empresa '{emp[1]}' excluída.")
                st.experimental_rerun()