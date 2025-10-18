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

# Entradas principais
nome_item = st.text_input("📝 Nome do Item").strip().lower()
valor = st.number_input("💰 Valor Arrematado (R$)", min_value=0.0, step=100.0)

# Função para entrada de taxa
def entrada_taxa(nome_taxa):
    modo = st.selectbox(f"Modo de {nome_taxa}", ["Percentual (%)", "Valor Fixo (R$)"], key=nome_taxa)
    if modo == "Percentual (%)":
        percentual = st.number_input(f"{nome_taxa} (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1, key=f"{nome_taxa}_percentual")
        return valor * percentual / 100
    else:
        valor_fixo = st.number_input(f"{nome_taxa} (R$)", min_value=0.0, value=0.0, step=10.0, key=f"{nome_taxa}_fixo")
        return valor_fixo

# Entradas das taxas
st.markdown("### 📌 Taxas Adicionais")
valor_taxa1 = entrada_taxa("Taxa 1")
valor_taxa2 = entrada_taxa("Taxa 2")
valor_taxa3 = entrada_taxa("Taxa 3")

# Função para ícone
def obter_icone(nome):
    for chave in ICONES:
        if chave in nome:
            return ICONES[chave]
    return ICONES["outro"]

# Cálculo
if st.button("🔍 Calcular Valor Total"):
    if valor > 0:
        total = valor + valor_taxa1 + valor_taxa2 + valor_taxa3
        icone = obter_icone(nome_item)

        resultado = {
            "Item": nome_item.title(),
            "Ícone": icone,
            "Valor (R$)": round(valor, 2),
            "Taxa 1 (R$)": round(valor_taxa1, 2),
            "Taxa 2 (R$)": round(valor_taxa2, 2),
            "Taxa 3 (R$)": round(valor_taxa3, 2),
            "Total (R$)": round(total, 2)
        }

        st.session_state["historico"].append(resultado)

        st.success(f"{icone} Resultado para **{nome_item.title()}**")
        st.write(f"📄 Taxa 1: R$ {valor_taxa1:.2f}")
        st.write(f"📄 Taxa 2: R$ {valor_taxa2:.2f}")
        st.write(f"📄 Taxa 3: R$ {valor_taxa3:.2f}")
        st.write(f"💵 Valor Total: **R$ {total:.2f}**")
    else:
        st.warning("Preencha o valor arrematado corretamente.")

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
