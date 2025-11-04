import streamlit as st
import pandas as pd
import sqlite3
import io
from datetime import datetime

# -----------------------------
# Página: Classificação de Extratos
# -----------------------------

st.set_page_config(page_title="Classificação - Vledger", page_icon="📘", layout="wide")

st.title("Classificação de Extratos")
st.caption("Use as referências salvas para preencher automaticamente as contas Débito e Crédito.")

st.markdown("---")

# ============================================
# 1️⃣ Carregar referências do banco SQLite
# ============================================
def carregar_referencias():
    try:
        conn = sqlite3.connect("vledger.db")
        df = pd.read_sql_query("SELECT * FROM referencias", conn)
        conn.close()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar referências: {e}")
        return pd.DataFrame()

df_ref = carregar_referencias()

if df_ref.empty:
    st.warning("Nenhuma referência encontrada. Vá até a aba **Referências** e cadastre os nomes e contas primeiro.")
    st.stop()

# Mostrar as referências
with st.expander("Ver referências cadastradas"):
    st.dataframe(df_ref)

# ============================================
# 2️⃣ Upload do extrato
# ============================================
arquivo_extrato = st.file_uploader("📎 Envie o extrato bancário (CSV ou XLSX)", type=["csv", "xlsx"])

@st.cache_data
def read_table(uploaded_file):
    if uploaded_file is None:
        return None
    name = uploaded_file.name.lower()
    try:
        if name.endswith(".csv"):
            return pd.read_csv(uploaded_file)
        elif name.endswith(".xlsx") or name.endswith(".xls"):
            return pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Erro ao ler o arquivo: {e}")
        return None

df_extrato = read_table(arquivo_extrato)

if df_extrato is not None:
    st.subheader("Pré-visualização do extrato")
    st.dataframe(df_extrato.head(15))

st.markdown("---")

# ============================================
# 3️⃣ Executar Classificação
# ============================================
if st.button("Executar Classificação Automática"):
    if df_extrato is None:
        st.error("Envie um extrato para iniciar a classificação.")
        st.stop()

    df = df_extrato.copy()
    ref = df_ref.copy()

    # Detectar a coluna de descrição
    col_desc = None
    for c in df.columns:
        if c.strip().lower() in ["descrição", "descricao", "description", "historico", "hist"]:
            col_desc = c
            break
    if col_desc is None:
        if len(df.columns) >= 2:
            col_desc = df.columns[1]
            st.warning(f"Não encontrei uma coluna chamada 'Descrição'. Usando: {col_desc}")
        else:
            st.error("Não foi possível identificar a coluna de descrição.")
            st.stop()

    # Adicionar colunas de resultado
    df["Débito"] = ""
    df["Crédito"] = ""
    df["_match"] = ""

    # Loop de correspondência
    for i, row in df.iterrows():
        desc = str(row[col_desc]).lower() if pd.notna(row[col_desc]) else ""
        matched = False
        for j, r in ref.iterrows():
            chave = str(r["nome"]).lower()
            if chave in desc:
                df.at[i, "Débito"] = r["conta_d"]
                df.at[i, "Crédito"] = r["conta_e"]
                df.at[i, "_match"] = r["nome"]
                matched = True
                break
        if not matched:
            df.at[i, "Débito"] = ""
            df.at[i, "Crédito"] = ""

    # Mostrar resultado
    st.success("Classificação concluída!")
    st.subheader("Resultado (pré-visualização)")
    st.dataframe(df.head(15))

    # Linhas não classificadas
    not_found = df[df["Débito"] == ""]
    if not not_found.empty:
        st.warning(f"Foram encontradas {len(not_found)} linhas sem correspondência automática.")
        with st.expander("Visualizar linhas não classificadas"):
            st.dataframe(not_found[[col_desc]])

    # Resumo de correspondências
    st.subheader("Resumo de correspondências encontradas")
    resumo = df["_match"].value_counts().rename_axis("Referência").reset_index(name="Ocorrências")
    st.table(resumo)

    # Exportar para Excel
    towrite = io.BytesIO()
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    df.to_excel(towrite, index=False, sheet_name="Classificação")
    towrite.seek(0)
    st.download_button(
        label=f"Baixar Resultado (Vledger_{now}.xlsx)",
        data=towrite,
        file_name=f"Vledger_{now}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

# Rodapé
st.markdown("---")
st.caption("Vledger — Inteligência para seus lançamentos contábeis")