import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="Calculadora de Leilão", layout="centered")

# Ícones por tipo de item
ICONES = {
    "computador": "🖥️", "notebook": "💻", "carro": "🚗", "moto": "🏍️",
    "bicicleta": "🚲", "impressora": "🖨️", "servidor": "🗄️", "monitor": "🖥️",
    "celular": "📱", "caminhão": "🚚", "outro": "📦"
}

# Histórico de cálculos
if "historico" not in st.session_state:
    st.session_state["historico"] = []

# Título
st.markdown("<h1 style='text-align:center;color:#2E8B57;'>🛒 Calculadora de Leilão RFB</h1>", unsafe_allow_html=True)
st.markdown("Preencha os dados abaixo para calcular os encargos sobre o item leiloado:")

# Entradas
nome_item = st.text_input("📝 Nome do Item").strip().lower()
valor = st.number_input("💰 Valor Arrematado (R$)", min_value=0.0, step=100.0)
aliquota_icms = st.number_input("📄 Alíquota ICMS (%)", min_value=0.0, max_value=100.0, value=18.0)
taxa_arm = st.selectbox("🏬 Taxa de Armazenagem (%)", [5.0, 7.5])

# Função para ícone
def obter_icone(nome):
    for chave in ICONES:
        if chave in nome:
            return ICONES[chave]
    return ICONES["outro"]

# Cálculo
if st.button("🔍 Calcular Valor Total"):
    if valor > 0 and aliquota_icms > 0 and taxa_arm > 0:
        icms = valor * aliquota_icms / (100 - aliquota_icms)
        taxa_armazenagem = valor * taxa_arm / 100
        total = valor + icms + taxa_armazenagem
        icone = obter_icone(nome_item)

        resultado = {
            "Item": nome_item.title(),
            "Ícone": icone,
            "Valor (R$)": round(valor, 2),
            "ICMS (R$)": round(icms, 2),
            "Armazenagem (R$)": round(taxa_armazenagem, 2),
            "Total (R$)": round(total, 2)
        }

        st.session_state["historico"].append(resultado)

        st.success(f"{icone} Resultado para **{nome_item.title()}**")
        st.write(f"📄 ICMS: R$ {icms:.2f}")
        st.write(f"🏬 Armazenagem: R$ {taxa_armazenagem:.2f}")
        st.write(f"💵 Valor Total: **R$ {total:.2f}**")
    else:
        st.warning("Preencha todos os campos corretamente.")

# Histórico
if st.session_state["historico"]:
    st.markdown("---")
    st.markdown("### 📊 Histórico de Cálculos Realizados")
    df = pd.DataFrame(st.session_state["historico"])
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📄 Exportar Histórico para CSV",
        data=csv,
        file_name="calculos_leilao.csv",
        mime="text/csv"
    )
