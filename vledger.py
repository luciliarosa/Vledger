import streamlit as st
import sqlite3
from datetime import datetime

# =========================================
# Página principal do sistema
# =========================================
st.set_page_config(page_title="Vledger", page_icon="📘", layout="centered")

st.title("📘 Vledger")
st.caption("Inteligência para seus lançamentos contábeis")

st.markdown("---")

# =========================================
# Inicializa o banco de dados (garante as tabelas)
# =========================================
def inicializar_banco():
    conn = sqlite3.connect("vledger.db")
    cursor = conn.cursor()

    # Tabela de empresas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS empresas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_empresa TEXT NOT NULL,
            cnpj TEXT,
            responsavel TEXT,
            data_cadastro TEXT
        )
    """)

    # Tabela de referências (plano contábil)
    cursor.execute("""
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

    # Tabela de classificações (lançamentos)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS classificacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER NOT NULL,
            descricao TEXT,
            debito TEXT,
            credito TEXT,
            valor REAL,
            data_processamento TEXT,
            FOREIGN KEY (empresa_id) REFERENCES empresas (id)
        )
    """)
    conn.commit()
    conn.close()

inicializar_banco()

st.success("Banco de dados inicializado com sucesso ✅")

# =========================================
# Menu principal
# =========================================
st.markdown("### 🧭 Menu Principal")
st.write("Escolha uma das opções abaixo:")

col1, col2, col3 = st.columns(3)

with col1:
    st.page_link("pages/empresas.py", label="🏢 Empresas", icon="🏢")

with col2:
    st.page_link("pages/referencia.py", label="📘 Plano Contábil", icon="📘")

with col3:
    st.page_link("pages/classificacao.py", label="⚙️ Classificação", icon="⚙️")

st.markdown("---")

st.caption("💡 Vledger — Inteligência para seus lançamentos contábeis")