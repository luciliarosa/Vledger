import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# =========================================
# Funções utilitárias e banco de dados
# =========================================
def conectar():
    return sqlite3.connect("vledger.db")

def ensure_tables_and_columns():
    conn = conectar()
    cur = conn.cursor()

    # 1) garante que a tabela empresas exista
    cur.execute("""
        CREATE TABLE IF NOT EXISTS empresas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_empresa TEXT NOT NULL,
            cnpj TEXT,
            responsavel TEXT,
            data_cadastro TEXT
        )
    """)

    # 2) cria a tabela referencias se não existir (com todas as colunas corretas)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS referencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            conta_d TEXT,
            conta_e TEXT,
            data_cadastro TEXT,
            FOREIGN KEY (empresa_id) REFERENCES empresas (id)
        )
    """)

    # 3) garantir que a coluna data_cadastro exista
    cur.execute("PRAGMA table_info(referencias)")
    cols = [row[1] for row in cur.fetchall()]
    if "data_cadastro" not in cols:
        try:
            cur.execute("ALTER TABLE referencias ADD COLUMN data_cadastro TEXT")
            conn.commit()
            print("Added column data_cadastro to referencias")
        except Exception as e:
            print("Could not add column data_cadastro:", e)

    conn.close()


def ensure_empresa_id_column():
    """Garante que a coluna empresa_id exista na tabela referencias"""
    conn = conectar()
    cur = conn.cursor()

    cur.execute("PRAGMA table_info(referencias)")
    cols = [row[1] for row in cur.fetchall()]

    if "empresa_id" not in cols:
        st.warning("⚙️ Atualizando estrutura da tabela 'referencias'...")

        # Renomeia a tabela antiga
        cur.execute("ALTER TABLE referencias RENAME TO referencias_old")

        # Cria a nova tabela com a estrutura correta
        cur.execute("""
            CREATE TABLE referencias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id INTEGER NOT NULL,
                nome TEXT NOT NULL,
                conta_d TEXT,
                conta_e TEXT,
                data_cadastro TEXT,
                FOREIGN KEY (empresa_id) REFERENCES empresas (id)
            )
        """)

        # Copia os dados antigos
        try:
            cur.execute("""
                INSERT INTO referencias (id, nome, conta_d, conta_e, data_cadastro)
                SELECT id, nome, conta_d, conta_e, data_cadastro FROM referencias_old
            """)
        except Exception as e:
            st.error(f"Erro ao migrar dados antigos: {e}")

        # Remove a tabela antiga
        cur.execute("DROP TABLE referencias_old")
        conn.commit()
        st.success("✅ Estrutura da tabela 'referencias' atualizada com sucesso!")

    conn.close()


# Executa verificações ao abrir a página
ensure_tables_and_columns()
ensure_empresa_id_column()


# =========================================
# Página: Referências (Plano Contábil)
# =========================================
st.set_page_config(page_title="Plano Contábil | Vledger", page_icon="📘", layout="wide")

st.title("📘 Plano Contábil")
st.caption("Gerencie as referências contábeis de cada empresa")


# =========================================
# Funções CRUD
# =========================================
def listar_empresas():
    conn = conectar()
    empresas = conn.execute("SELECT id, nome_empresa FROM empresas ORDER BY nome_empresa").fetchall()
    conn.close()
    return empresas

def inserir_referencia(empresa_id, nome, conta_d, conta_e):
    conn = conectar()
    data_cadastro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn.execute(
        "INSERT INTO referencias (empresa_id, nome, conta_d, conta_e, data_cadastro) VALUES (?, ?, ?, ?, ?)",
        (empresa_id, nome, conta_d, conta_e, data_cadastro),
    )
    conn.commit()
    conn.close()

def listar_referencias(empresa_id):
    conn = conectar()
    refs = conn.execute(
        "SELECT id, nome, conta_d, conta_e, data_cadastro FROM referencias WHERE empresa_id=? ORDER BY nome",
        (empresa_id,)
    ).fetchall()
    conn.close()
    return refs

def atualizar_referencia(ref_id, nome, conta_d, conta_e):
    conn = conectar()
    conn.execute("UPDATE referencias SET nome=?, conta_d=?, conta_e=? WHERE id=?",
                 (nome, conta_d, conta_e, ref_id))
    conn.commit()
    conn.close()

def excluir_referencia(ref_id):
    conn = conectar()
    conn.execute("DELETE FROM referencias WHERE id=?", (ref_id,))
    conn.commit()
    conn.close()

def importar_referencias_csv(empresa_id, df):
    conn = conectar()
    for _, row in df.iterrows():
        nome = str(row.get("Nome", "")).strip()
        conta_d = str(row.get("Conta_D", "")).strip()
        conta_e = str(row.get("Conta_E", "")).strip()
        if nome:
            data_cadastro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            conn.execute(
                "INSERT INTO referencias (empresa_id, nome, conta_d, conta_e, data_cadastro) VALUES (?, ?, ?, ?, ?)",
                (empresa_id, nome, conta_d, conta_e, data_cadastro),
            )
    conn.commit()
    conn.close()


# =========================================
# Seleção da empresa
# =========================================
empresas = listar_empresas()
if len(empresas) == 0:
    st.warning("Nenhuma empresa cadastrada. Vá até a página **Empresas** e cadastre pelo menos uma.")
    st.stop()

empresa_dict = {e[1]: e[0] for e in empresas}
empresa_nome = st.selectbox("Selecione a empresa", list(empresa_dict.keys()))
empresa_id = empresa_dict[empresa_nome]

st.markdown(f"📊 **Plano contábil da empresa:** `{empresa_nome}`")


# =========================================
# Layout de seções organizadas
# =========================================
with st.expander("➕ Adicionar nova referência"):
    with st.form("form_add_ref", clear_on_submit=True):
        nome = st.text_input("Descrição / Palavra-chave *")
        conta_d = st.text_input("Conta Débito")
        conta_e = st.text_input("Conta Crédito")
        submitted = st.form_submit_button("Salvar")

        if submitted:
            if nome.strip() == "":
                st.warning("O campo 'Descrição / Palavra-chave' é obrigatório.")
            else:
                inserir_referencia(empresa_id, nome, conta_d, conta_e)
                st.success(f"Referência **{nome}** adicionada com sucesso!")

with st.expander("📥 Importar referências de arquivo (CSV ou XLSX)"):
    uploaded_file = st.file_uploader("Selecione um arquivo de referência", type=["csv", "xlsx"])
    if uploaded_file:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.dataframe(df)
            if st.button("Importar referências do arquivo"):
                importar_referencias_csv(empresa_id, df)
                st.success("Referências importadas com sucesso!")
                st.experimental_rerun()
        except Exception as e:
            st.error(f"Erro ao ler o arquivo: {e}")

with st.expander("📋 Referências cadastradas"):
    refs = listar_referencias(empresa_id)
    if len(refs) == 0:
        st.info("Nenhuma referência cadastrada para esta empresa.")
    else:
        df_refs = pd.DataFrame(refs, columns=["ID", "Nome", "Conta Débito", "Conta Crédito", "Data Cadastro"])
        st.dataframe(df_refs, use_container_width=True)

with st.expander("⚙️ Editar ou excluir referência"):
    refs = listar_referencias(empresa_id)
    if len(refs) == 0:
        st.info("Nenhuma referência para editar.")
    else:
        ref_dict = {f"{r[1]} (ID: {r[0]})": r for r in refs}
        escolha = st.selectbox("Selecione uma referência", list(ref_dict.keys()))
        ref = ref_dict[escolha]

        nome_edit = st.text_input("Descrição / Palavra-chave", ref[1])
        conta_d_edit = st.text_input("Conta Débito", ref[2] or "")
        conta_e_edit = st.text_input("Conta Crédito", ref[3] or "")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Salvar alterações"):
                atualizar_referencia(ref[0], nome_edit, conta_d_edit, conta_e_edit)
                st.success("Referência atualizada com sucesso!")
                st.experimental_rerun()
        with col2:
            if st.button("🗑️ Excluir referência"):
                excluir_referencia(ref[0])
                st.warning(f"Referência '{ref[1]}' excluída.")
                st.experimental_rerun()