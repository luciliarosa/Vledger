import streamlit as st
import pandas as pd
import sqlite3
import io
from datetime import datetime

st.set_page_config(page_title="Classificação | Vledger", page_icon="⚙️", layout="wide")
st.title("⚙️ Classificação de Lançamentos")
st.caption("Classifique o extrato com base no plano contábil da empresa selecionada")

# ==========================================================
# BANCO DE DADOS
# ==========================================================
def conectar():
    return sqlite3.connect("vledger.db")

def inicializar_tabela_classificacoes():
    conn = conectar()
    cur = conn.cursor()

    # Cria tabela se não existir
    cur.execute("""
        CREATE TABLE IF NOT EXISTS classificacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER NOT NULL,
            descricao TEXT,
            debito TEXT,
            credito TEXT,
            valor REAL,
            data_movimento TEXT,
            data_processamento TEXT,
            FOREIGN KEY (empresa_id) REFERENCES empresas (id)
        )
    """)

    # Verifica colunas existentes
    cur.execute("PRAGMA table_info(classificacoes)")
    cols = [row[1] for row in cur.fetchall()]

    # Adiciona colunas faltantes
    colunas_necessarias = {
        "empresa_id": "INTEGER NOT NULL DEFAULT 1",
        "descricao": "TEXT",
        "debito": "TEXT",
        "credito": "TEXT",
        "valor": "REAL",
        "data_movimento": "TEXT",
        "data_processamento": "TEXT"
    }

    for col, tipo in colunas_necessarias.items():
        if col not in cols:
            try:
                cur.execute(f"ALTER TABLE classificacoes ADD COLUMN {col} {tipo}")
                print(f"✅ Coluna adicionada: {col}")
            except Exception as e:
                print(f"⚠️ Erro ao adicionar coluna {col}: {e}")

    conn.commit()
    conn.close()

# Executa a verificação automática da tabela
inicializar_tabela_classificacoes()


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

def salvar_classificacoes_db(empresa_id, df):
    """Salva DataFrame já normalizado (colunas: descricao, debito, credito, valor, data_movimento)"""
    conn = conectar()
    cur = conn.cursor()
    for _, row in df.iterrows():
        descricao = str(row.get("descricao", ""))[:1000]
        debito = str(row.get("debito", ""))
        credito = str(row.get("credito", ""))
        try:
            valor = float(row.get("valor", 0.0)) if pd.notna(row.get("valor")) else 0.0
        except Exception:
            valor = 0.0
        data_mov = row.get("data_movimento")
        if pd.isna(data_mov) or data_mov is None:
            data_mov = datetime.now().strftime("%Y-%m-%d")
        elif isinstance(data_mov, pd.Timestamp):
            data_mov = data_mov.strftime("%Y-%m-%d")
        elif isinstance(data_mov, str):
            # assume already in iso or user input
            try:
                _ = pd.to_datetime(data_mov)
                data_mov = pd.to_datetime(data_mov).strftime("%Y-%m-%d")
            except Exception:
                data_mov = datetime.now().strftime("%Y-%m-%d")

        data_proc = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cur.execute(
            """
            INSERT INTO classificacoes (empresa_id, descricao, debito, credito, valor, data_movimento, data_processamento)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (empresa_id, descricao, debito, credito, valor, data_mov, data_proc)
        )
    conn.commit()
    conn.close()


def listar_classificacoes(empresa_id):
    conn = conectar()
    try:
        df = pd.read_sql_query(
            "SELECT descricao, debito, credito, valor, data_movimento, data_processamento FROM classificacoes WHERE empresa_id=? ORDER BY data_movimento DESC",
            conn,
            params=(empresa_id,),
        )
    except Exception:
        # Se algo falhar, retorna DataFrame vazio
        df = pd.DataFrame(columns=["descricao", "debito", "credito", "valor", "data_movimento", "data_processamento"])
    conn.close()
    return df


# ==========================================================
# UTILITÁRIAS: detectar colunas e normalizar dados
# ==========================================================
def find_column(columns, candidates):
    cols_lower = [c.lower() for c in columns]
    for cand in candidates:
        for i, c in enumerate(cols_lower):
            if cand in c:
                return columns[i]  # retorna nome original
    return None

def parse_number(value):
    """Tenta converter vários formatos numéricos (BR e EN)."""
    if pd.isna(value):
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value).strip()
    if s == "":
        return 0.0
    # remove currency symbols and spaces
    s = s.replace("R$", "").replace("$", "").strip()
    # if contains both '.' and ',', likely BR format like '1.234,56'
    if "." in s and "," in s:
        s = s.replace(".", "").replace(",", ".")
    else:
        # if only comma, treat as decimal separator
        if "," in s and "." not in s:
            s = s.replace(",", ".")
        # if only dots, keep as is (thousands maybe missing)
    try:
        return float(s)
    except:
        # fallback: try removing non-digits
        import re
        s2 = re.sub(r"[^\d\.\\-]", "", s)
        try:
            return float(s2)
        except:
            return 0.0

def parse_date(value):
    """Tenta converter vários formatos de data para pd.Timestamp ou None."""
    if pd.isna(value):
        return None
    try:
        # tenta conversão direta (aceita várias formas)
        dt = pd.to_datetime(value, dayfirst=True, errors="coerce")
        return dt
    except:
        return None


# ==========================================================
# SELEÇÃO DE EMPRESA
# ==========================================================
empresas = listar_empresas()
if len(empresas) == 0:
    st.warning("Nenhuma empresa cadastrada. Vá até a página **Empresas** e cadastre pelo menos uma.")
    st.stop()

empresa_dict = {e[1]: e[0] for e in empresas}
empresa_nome = st.selectbox("Selecione a empresa", list(empresa_dict.keys()))
empresa_id = empresa_dict[empresa_nome]

st.markdown(f"📊 **Classificando lançamentos da empresa:** `{empresa_nome}`")


# ==========================================================
# VISUALIZAÇÃO DE CLASSIFICAÇÕES EXISTENTES
# ==========================================================
st.subheader("📚 Classificações registradas")

df_class = listar_classificacoes(empresa_id)
if df_class.empty:
    st.info("Nenhuma classificação registrada ainda para esta empresa.")
else:
    # Agrupa por ano/mês
    df_class["data_movimento"] = pd.to_datetime(df_class["data_movimento"], errors="coerce")
    df_class["Ano"] = df_class["data_movimento"].dt.year
    df_class["Mês"] = df_class["data_movimento"].dt.strftime("%B")

    for ano in sorted(df_class["Ano"].dropna().unique(), reverse=True):
        with st.expander(f"📅 {int(ano)}"):
            df_ano = df_class[df_class["Ano"] == ano]
            for mes in sorted(df_ano["Mês"].dropna().unique()):
                with st.expander(f"🗓️ {mes} ({len(df_ano[df_ano['Mês']==mes])} lançamentos)"):
                    st.dataframe(
                        df_ano[df_ano["Mês"] == mes][
                            ["data_movimento", "descricao", "debito", "credito", "valor"]
                        ].sort_values("data_movimento"),
                        use_container_width=True
                    )


# ==========================================================
# UPLOAD DO EXTRATO
# ==========================================================
st.divider()
st.subheader("📥 Importar novo extrato")

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


# ==========================================================
# CLASSIFICAÇÃO AUTOMÁTICA
# ==========================================================
# Usamos session_state para manter o resultado da última classificação
if "last_classified_df" not in st.session_state:
    st.session_state["last_classified_df"] = None

if st.button("⚙️ Executar classificação"):
    if df_extrato is None:
        st.error("Envie um extrato antes de executar a classificação.")
        st.stop()

    refs = listar_referencias(empresa_id)
    if len(refs) == 0:
        st.error("Nenhuma referência encontrada para esta empresa.")
        st.stop()

    df = df_extrato.copy()

    # Detecta colunas
    desc_col = find_column(df.columns, ["descr", "description", "hist", "histórico", "historico"])
    date_col = find_column(df.columns, ["data", "date", "dt"])
    val_col  = find_column(df.columns, ["valor", "value", "amount", "amt", "vlr"])

    if desc_col is None:
        # fallback para segunda coluna
        if len(df.columns) >= 2:
            desc_col = df.columns[1]
            st.warning(f"Não encontrei coluna de descrição. Usando: {desc_col}")
        else:
            st.error("Não foi possível identificar a coluna de descrição no extrato.")
            st.stop()

    # Normaliza colunas para salvar facilmente
    df["descricao_norm"] = df[desc_col].astype(str)

    # normaliza valor
    if val_col is not None:
        df["valor_norm"] = df[val_col].apply(parse_number)
    else:
        # tenta colunas comuns ou cria zeros
        df["valor_norm"] = 0.0

    # normaliza data
    if date_col is not None:
        df["data_norm"] = df[date_col].apply(parse_date)
    else:
        # tenta detectar colunas com formato data mesmo se nome não óbvio
        possible_date = None
        for c in df.columns:
            parsed = pd.to_datetime(df[c], errors="coerce", dayfirst=True)
            if parsed.notna().sum() > 0:
                possible_date = c
                break
        if possible_date:
            df["data_norm"] = pd.to_datetime(df[possible_date], errors="coerce", dayfirst=True)
        else:
            df["data_norm"] = pd.NaT

    # Prepara colunas de saída
    df["Débito"] = ""
    df["Crédito"] = ""

    # Executa correspondência
    for i, row in df.iterrows():
        desc = str(row["descricao_norm"]).lower()
        matched = False
        for nome, conta_d, conta_e in refs:
            if nome is None:
                continue
            if nome.lower() in desc:
                df.at[i, "Débito"] = conta_d
                df.at[i, "Crédito"] = conta_e
                matched = True
                break

    st.success("Classificação concluída ✅")
    st.dataframe(df.head(15))

    # preenche o session_state com versão normalizada para salvar
    df_to_save = pd.DataFrame({
        "descricao": df["descricao_norm"],
        "debito": df["Débito"],
        "credito": df["Crédito"],
        "valor": df["valor_norm"],
        "data_movimento": df["data_norm"]
    })
    st.session_state["last_classified_df"] = df_to_save

# Botão para salvar - agora usa session_state
if st.session_state.get("last_classified_df") is not None:
    if st.button("💾 Salvar classificações no banco"):
        try:
            salvar_classificacoes_db(empresa_id, st.session_state["last_classified_df"])
            st.success("Lançamentos salvos com sucesso no banco!")
            # limpa o último resultado salvo
            st.session_state["last_classified_df"] = None
            st.rerun()
        except Exception as e:
            st.error(f"Erro ao salvar no banco: {e}")

# Download do último resultado (se houver)
if st.session_state.get("last_classified_df") is not None:
    towrite = io.BytesIO()
    tmp = st.session_state["last_classified_df"].copy()
    # formata data_movimento como string para Excel
    tmp["data_movimento"] = tmp["data_movimento"].apply(
        lambda x: x.strftime("%Y-%m-%d") if not pd.isna(x) and hasattr(x, "strftime") else (str(x) if pd.notna(x) else "")
    )
    tmp.to_excel(towrite, index=False, sheet_name="Classificacao_Vledger")
    towrite.seek(0)
    st.download_button(
        label="📤 Baixar resultado (XLSX)",
        data=towrite,
        file_name=f"classificacao_{empresa_nome}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )