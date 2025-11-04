import streamlit as st
import pandas as pd
import sqlite3
import io
from datetime import datetime

st.set_page_config(page_title="Classificação | Vledger", page_icon="⚙️", layout="wide")
st.title("⚙️ Classificação de Lançamentos")
st.caption("Classifique o extrato com base no plano contábil da empresa selecionada")

# ----------------------------
# Banco de dados
# ----------------------------
def conectar():
    return sqlite3.connect("vledger.db")

def listar_empresas():
    conn = conectar()
    empresas = conn.execute("SELECT id, nome_empresa FROM empresas ORDER BY nome_empresa").fetchall()
    conn.close()
    return empresas

def listar_referencias(empresa_id):
    conn = conectar()
    refs = conn.execute(
        "SELECT nome, conta_d, conta_e FROM referencias WHERE empresa_id=? ORDER BY nome",
        (empresa_id,)
    ).fetchall()
    conn.close()
    return refs

def salvar_classificacoes(empresa_id, df):
    conn = conectar()
    for _, row in df.iterrows():
        conn.execute(
            "INSERT INTO classificacoes (empresa_id, descricao, debito, credito, valor, data_processamento) VALUES (?, ?, ?, ?, ?, ?)",
            (
                empresa_id,
                str(row.get("Descrição", "")),
                str(row.get("Débito", "")),
                str(row.get("Crédito", "")),
                float(row.get("Valor", 0)) if pd.notna(row.get("Valor")) else 0.0,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
    conn.commit()
    conn.close()

# ----------------------------
# Seleção de empresa
# ----------------------------
empresas = listar_empresas()
if len(empresas) == 0:
    st.warning("Nenhuma empresa cadastrada. Vá até a página **Empresas** e cadastre pelo menos uma.")
    st.stop()

empresa_dict = {e[1]: e[0] for e in empresas}
empresa_nome = st.selectbox("Selecione a empresa", list(empresa_dict.keys()))
empresa_id = empresa_dict[empresa_nome]

st.markdown(f"📊 **Classificando lançamentos da empresa:** `{empresa_nome}`")

# ----------------------------
# Upload do extrato
# ----------------------------
arquivo_extrato = st.file_uploader("Anexe o extrato (CSV ou XLSX)", type=["csv", "xlsx"])

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
    st.subheader("📄 Pré-visualização do extrato")
    st.dataframe(df_extrato.head(15))

# ----------------------------
# Classificação
# ----------------------------
if st.button("Executar classificação"):
    refs = listar_referencias(empresa_id)
    if len(refs) == 0:
        st.error("Nenhuma referência encontrada para esta empresa.")
        st.stop()

    df = df_extrato.copy()
    df["Débito"] = ""
    df["Crédito"] = ""

    colunas = [c.lower() for c in df.columns]
    col_desc = None
    for c in df.columns:
        if "descr" in c.lower() or "hist" in c.lower():
            col_desc = c
            break
    if not col_desc and len(df.columns) >= 2:
        col_desc = df.columns[1]
        st.warning(f"Não encontrei uma coluna de descrição. Usando '{col_desc}'.")

    for i, row in df.iterrows():
        desc = str(row[col_desc]).lower()
        for nome, conta_d, conta_e in refs:
            if nome.lower() in desc:
                df.at[i, "Débito"] = conta_d
                df.at[i, "Crédito"] = conta_e
                break

    st.success("Classificação concluída ✅")
    st.dataframe(df.head(15))

    # Permite salvar no banco
    if st.button("💾 Salvar classificações no banco"):
        salvar_classificacoes(empresa_id, df)
        st.success("Lançamentos salvos com sucesso no banco!")

    # Download Excel
    towrite = io.BytesIO()
    df.to_excel(towrite, index=False, sheet_name="Classificacao_Vledger")
    towrite.seek(0)
    st.download_button(
        label="📥 Baixar resultado (XLSX)",
        data=towrite,
        file_name=f"classificacao_{empresa_nome}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )