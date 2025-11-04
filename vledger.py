import streamlit as st

st.set_page_config(page_title="Vledger", page_icon="📘", layout="wide")

# Cabeçalho
st.title("📘 Vledger")
st.caption("Inteligência para seus lançamentos contábeis")

st.markdown("---")
st.write("👋 Bem-vindo ao **Vledger**!")

# Layout de menu principal
col1, col2 = st.columns(2)

with col1:
    st.subheader("Classificação de Extratos")
    st.write("Classifique automaticamente seus lançamentos contábeis com base nas referências.")
    if st.button("Ir para Classificação ➡️"):
        st.switch_page("pages/classificacao.py")

with col2:
    st.subheader("Cadastro de Referências")
    st.write("Gerencie as palavras-chave e contas usadas nas classificações.")
    if st.button("Ir para Referências ➡️"):
        st.switch_page("pages/referencia.py")

st.markdown("---")
st.caption("© 2025 Vledger — Inteligência para seus lançamentos contábeis")