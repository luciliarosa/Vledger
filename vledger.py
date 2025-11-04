import streamlit as st
import pandas as pd
import io
from datetime import datetime

# -----------------------------
# Vledger - Inteligência para seus lançamentos contábeis
# Single-file Streamlit app
# Save as Vledger_app.py and run: streamlit run Vledger_app.py
# -----------------------------

st.set_page_config(page_title="Vledger", page_icon="📘", layout="wide")

# App header
st.title("Vledger")
st.caption("Inteligência para seus lançamentos contábeis")

with st.expander("Sobre o Vledger"):
    st.write(
        "Vledger automatiza o preenchimento das contas Débito e Crédito a partir de um extrato. "
        "Faça upload do extrato (CSV/XLSX) e da tabela de referência (CSV/XLSX) e o sistema tentará "
        "identificar palavras-chave nas descrições para preencher as contas automaticamente."
    )

# Sidebar - configurações
st.sidebar.header("Configurações")
matching_mode = st.sidebar.selectbox(
    "Modo de correspondência",
    ("Substr (contém, padrão)", "Palavra inteira", "Regex")
)
case_sensitive = st.sidebar.checkbox("Case sensitive (sensível a maiúsc./minusc.)", value=False)
preview_rows = st.sidebar.slider("Linhas de pré-visualização", min_value=5, max_value=100, value=15)

st.sidebar.markdown("---")
st.sidebar.markdown("**Modelos / Ajuda**")
if st.sidebar.button("Baixar modelo de referência (CSV)"):
    sample_ref = pd.DataFrame(
        {
            "Nome": ["Intermedica", "Amil", "Unimed", "Sulamerica", "Bradesco"],
            "Conta_D": [282, 310, 295, 320, 400],
            "Conta_E": [537, 537, 537, 537, 537],
        }
    )
    towrite = io.BytesIO()
    sample_ref.to_csv(towrite, index=False)
    towrite.seek(0)
    st.download_button("Download referencia.csv", data=towrite, file_name="referencia_modelo.csv")

st.markdown("---")

# Uploads
col1, col2 = st.columns(2)
with col1:
    arquivo_extrato = st.file_uploader("Anexe o extrato (CSV ou XLSX)", type=["csv", "xlsx"] , key="extrato")
with col2:
    arquivo_ref = st.file_uploader("Anexe a tabela de referência (CSV ou XLSX)", type=["csv", "xlsx"], key="ref")

# Helper: leitura flexível de arquivos
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

# Lê os dados
df_extrato = read_table(arquivo_extrato)
df_ref = read_table(arquivo_ref)

# Mostra pré-visualização
if df_extrato is not None:
    st.subheader("Pré-visualização do extrato")
    st.dataframe(df_extrato.head(preview_rows))

if df_ref is not None:
    st.subheader("Tabela de referência")
    st.dataframe(df_ref)

# Validações simples
if st.button("Executar classificação"):
    if df_extrato is None or df_ref is None:
        st.error("Você precisa enviar tanto o extrato quanto a tabela de referência.")
    else:
        # Normaliza nomes das colunas esperadas
        df = df_extrato.copy()
        ref = df_ref.copy()

        # Tentativa de identificar colunas comuns
        # Procuramos por colunas que contenham as palavras-chave conhecidas
        col_desc = None
        for c in df.columns:
            if c.strip().lower() in ["descrição", "descricao", "description", "historico", "hist"]:
                col_desc = c
                break
        if col_desc is None:
            # fallback: assume a segunda coluna (como no exemplo original)
            if len(df.columns) >= 2:
                col_desc = df.columns[1]
                st.warning(f"Não encontrei uma coluna chamada 'Descrição'. Vou usar a coluna: {col_desc}")
            else:
                st.error("Não foi possível identificar a coluna de descrição. Certifique-se que o extrato tem uma coluna de texto para descrições.")
                st.stop()

        # Normaliza ref columns
        ref_cols = [c.strip().lower() for c in ref.columns]
        # Procurar colunas Nome / Conta_D / Conta_E
        try:
            name_col = ref.columns[[i for i, c in enumerate(ref_cols) if c in ("nome", "name")][0]]
            conta_d_col = ref.columns[[i for i, c in enumerate(ref_cols) if c in ("conta_d", "conta d", "contad", "debito")][0]]
            conta_e_col = ref.columns[[i for i, c in enumerate(ref_cols) if c in ("conta_e", "conta e", "contae", "credito")][0]]
        except Exception:
            st.error(
                "A tabela de referência precisa ter colunas Nome, Conta_D e Conta_E (ou variações). Exemplo: Nome, Conta_D, Conta_E"
            )
            st.stop()

        # Prepara colunas de resultado
        df["Débito"] = ""
        df["Crédito"] = ""
        df["_match_name"] = ""

        # Função de comparação
        def matches(description, pattern):
            if not case_sensitive:
                description = description.lower()
                pattern = pattern.lower()
            if matching_mode == "Substr (contém, padrão)":
                return str(pattern) in str(description)
            elif matching_mode == "Palavra inteira":
                # procura por palavra inteira (separadores: espaço, pontuação)
                import re

                pat = r"\b" + re.escape(str(pattern)) + r"\b"
                return re.search(pat, str(description)) is not None
            else:  # Regex
                import re

                try:
                    flags = 0 if case_sensitive else re.IGNORECASE
                    return re.search(pattern, description, flags) is not None
                except re.error:
                    return False

        # Loop de preenchimento
        for i, row in df.iterrows():
            desc = str(row[col_desc]) if pd.notna(row[col_desc]) else ""
            found = False
            for j, r in ref.iterrows():
                key = str(r[name_col])
                if matches(desc, key):
                    df.at[i, "Débito"] = r[conta_d_col]
                    df.at[i, "Crédito"] = r[conta_e_col]
                    df.at[i, "_match_name"] = key
                    found = True
                    break
            if not found:
                df.at[i, "Débito"] = ""
                df.at[i, "Crédito"] = ""

        st.success("Classificação concluída")
        st.subheader("Resultado (pré-visualização)")
        st.dataframe(df.head(preview_rows))

        # Exibir problemas / não encontrados
        not_found = df[df["Débito"] == ""].copy()
        if not not_found.empty:
            st.warning(f"Foram encontradas {len(not_found)} linhas sem correspondência automática.")
            with st.expander("Visualizar linhas sem correspondência"):
                st.dataframe(not_found[[col_desc, "Débito", "Crédito"]].head(preview_rows))

        # Permite download em Excel
        towrite = io.BytesIO()
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        try:
            df.to_excel(towrite, index=False, sheet_name="Vledger_Result")
            towrite.seek(0)
            st.download_button(
                label=f"Baixar resultado (XLSX) - Vledger_{now}.xlsx",
                data=towrite,
                file_name=f"Vledger_{now}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        except Exception as e:
            st.error(f"Erro ao gerar Excel: {e}")

        # Também permite ver a tabela de correspondências encontradas
        st.subheader("Resumo de correspondências")
        resumo = df["_match_name"].value_counts().rename_axis("Nome").reset_index(name="Contagens")
        if not resumo.empty:
            st.table(resumo)
        else:
            st.info("Nenhuma correspondência automática encontrada nas linhas selecionadas.")

# Rodapé
st.markdown("---")
st.caption("Vledger — Inteligência para seus lançamentos contábeis")