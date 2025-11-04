import streamlit as st
import sqlite3
import pandas as pd

st.title("📚 Cadastro de Referências Contábeis")

# Conecta (ou cria) o banco local
conn = sqlite3.connect("vledger.db")
cursor = conn.cursor()

# Cria tabela se não existir
cursor.execute("""
CREATE TABLE IF NOT EXISTS referencias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    conta_d INTEGER,
    conta_e INTEGER
)
""")
conn.commit()

tabs = st.tabs(["➕ Nova Referência", "📋 Gerenciar Referências"])

# Aba 1 - Adicionar nova
with tabs[0]:
    with st.form("nova_ref_form"):
        nome = st.text_input("Nome")
        conta_d = st.number_input("Conta Débito", min_value=0, step=1)
        conta_e = st.number_input("Conta Crédito", min_value=0, step=1)
        submit = st.form_submit_button("Salvar")

        if submit:
            if nome.strip() == "":
                st.warning("Por favor, insira um nome válido.")
            else:
                cursor.execute(
                    "INSERT INTO referencias (nome, conta_d, conta_e) VALUES (?, ?, ?)",
                    (nome, conta_d, conta_e)
                )
                conn.commit()
                st.success(f"Referência '{nome}' salva com sucesso!")

# Aba 2 - Gerenciar
with tabs[1]:
    df_ref = pd.read_sql_query("SELECT * FROM referencias", conn)

    if df_ref.empty:
        st.info("Nenhuma referência cadastrada ainda.")
    else:
        st.write("Edite diretamente na tabela e clique em **Salvar alterações**.")
        edited_df = st.data_editor(df_ref, num_rows="dynamic", use_container_width=True)

        if st.button("💾 Salvar alterações"):
            for _, row in edited_df.iterrows():
                cursor.execute(
                    "UPDATE referencias SET nome=?, conta_d=?, conta_e=? WHERE id=?",
                    (row["nome"], row["conta_d"], row["conta_e"], row["id"])
                )
            conn.commit()
            st.success("Alterações salvas com sucesso!")

        delete_id = st.selectbox("Selecione o ID para excluir", df_ref["id"])
        if st.button("🗑️ Excluir referência selecionada"):
            cursor.execute("DELETE FROM referencias WHERE id=?", (delete_id,))
            conn.commit()
            st.warning("Referência excluída com sucesso!")
