import streamlit as st
import pandas as pd
import sqlite3
import io

st.set_page_config(page_title="Referências - Vledger", page_icon="📘", layout="wide")

st.title("Cadastro de Referências")
st.caption("Gerencie as palavras-chave e contas usadas na classificação automática de lançamentos.")

# ============================================
# 1️⃣ Banco de dados
# ============================================
def init_db():
    conn = sqlite3.connect("vledger.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS referencias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE,
            conta_d INTEGER,
            conta_e INTEGER
        )
    """)
    conn.commit()
    conn.close()

def carregar_referencias():
    conn = sqlite3.connect("vledger.db")
    df = pd.read_sql_query("SELECT * FROM referencias", conn)
    conn.close()
    return df

def inserir_referencia(nome, conta_d, conta_e):
    conn = sqlite3.connect("vledger.db")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO referencias (nome, conta_d, conta_e) VALUES (?, ?, ?)", (nome, conta_d, conta_e))
    conn.commit()
    conn.close()

def atualizar_referencia(id_ref, nome, conta_d, conta_e):
    conn = sqlite3.connect("vledger.db")
    c = conn.cursor()
    c.execute("UPDATE referencias SET nome=?, conta_d=?, conta_e=? WHERE id=?", (nome, conta_d, conta_e, id_ref))
    conn.commit()
    conn.close()

def excluir_referencia(id_ref):
    conn = sqlite3.connect("vledger.db")
    c = conn.cursor()
    c.execute("DELETE FROM referencias WHERE id=?", (id_ref,))
    conn.commit()
    conn.close()

init_db()

# ============================================
# 2️⃣ Seção: Adicionar nova referência
# ============================================
with st.expander("➕ Adicionar Nova Referência", expanded=False):
    with st.form("form_add_ref", clear_on_submit=True):
        nome = st.text_input("Nome (palavra-chave da descrição)")
        conta_d = st.number_input("Conta Débito", min_value=0, step=1)
        conta_e = st.number_input("Conta Crédito", min_value=0, step=1)
        submitted = st.form_submit_button("Salvar Referência")

        if submitted:
            if nome.strip() == "":
                st.error("O campo Nome é obrigatório.")
            else:
                inserir_referencia(nome.strip(), conta_d, conta_e)
                st.success(f"Referência '{nome}' adicionada com sucesso!")

# ============================================
# 3️⃣ Seção: Importar arquivo modelo
# ============================================
with st.expander("📤 Importar Modelo de Referência", expanded=False):
    st.info("Envie uma planilha com as colunas: **Nome**, **Conta_D**, **Conta_E**.")

    # Modelo para download
    modelo = pd.DataFrame({
        "Nome": ["Intermedica", "Amil", "Unimed"],
        "Conta_D": [282, 310, 295],
        "Conta_E": [537, 537, 537]
    })
    buffer = io.BytesIO()
    modelo.to_excel(buffer, index=False)
    buffer.seek(0)
    st.download_button("📥 Baixar Modelo de Referência", data=buffer, file_name="modelo_referencia.xlsx")

    arquivo_upload = st.file_uploader("Envie seu arquivo (CSV ou XLSX)", type=["csv", "xlsx"])

    if arquivo_upload:
        try:
            if arquivo_upload.name.endswith(".csv"):
                df_upload = pd.read_csv(arquivo_upload)
            else:
                df_upload = pd.read_excel(arquivo_upload)

            cols_lower = [c.lower() for c in df_upload.columns]
            if not all(col in cols_lower for col in ["nome", "conta_d", "conta_e"]):
                st.error("O arquivo deve conter as colunas Nome, Conta_D e Conta_E.")
            else:
                for _, row in df_upload.iterrows():
                    inserir_referencia(str(row["Nome"]), int(row["Conta_D"]), int(row["Conta_E"]))
                st.success(f"{len(df_upload)} referências importadas com sucesso!")
        except Exception as e:
            st.error(f"Erro ao importar: {e}")

# ============================================
# 4️⃣ Seção: Referências cadastradas
# ============================================
with st.expander("🧾 Referências Cadastradas", expanded=True):
    df = carregar_referencias()
    if df.empty:
        st.info("Nenhuma referência cadastrada ainda.")
    else:
        st.dataframe(df, use_container_width=True)

        # Editar / excluir
        st.markdown("#### ✏️ Editar ou Excluir Referência")

        nomes = df["nome"].tolist()
        escolha = st.selectbox("Selecione uma referência", options=[""] + nomes)

        if escolha:
            ref_row = df[df["nome"] == escolha].iloc[0]
            with st.form("form_edit_ref"):
                novo_nome = st.text_input("Nome", ref_row["nome"])
                novo_d = st.number_input("Conta Débito", value=int(ref_row["conta_d"]), min_value=0, step=1)
                novo_e = st.number_input("Conta Crédito", value=int(ref_row["conta_e"]), min_value=0, step=1)

                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Salvar Alterações"):
                        atualizar_referencia(ref_row["id"], novo_nome, novo_d, novo_e)
                        st.success("Referência atualizada!")
                with col2:
                    if st.form_submit_button("Excluir"):
                        excluir_referencia(ref_row["id"])
                        st.warning("Referência excluída!")

st.markdown("---")
st.caption("Vledger — Inteligência para seus lançamentos contábeis")