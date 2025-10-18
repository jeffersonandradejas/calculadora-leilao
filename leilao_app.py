import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Configuração da página
st.set_page_config(page_title="Calculadora de Leilão", layout="centered")

# Função para formatar moeda no padrão brasileiro
def formatar_reais(valor):
    partes = f"{valor:,.2f}".split(".")
    milhar = partes[0].replace(",", ".")
    centavos = partes[1]
    return f"R$ {milhar},{centavos}"

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
st.markdown("<h1 style='text-align:center;color:#2E8B57;'>🛒 Calculadora de Leilão</h1>", unsafe_allow_html=True)
st.markdown("Preencha os dados abaixo para calcular os encargos e projeção de revenda:")

# Entradas principais
col1, col2 = st.columns(2)
with col1:
    nome_item = st.text_input("📝 Nome do Item").strip().lower()
with col2:
    valor = st.number_input("💰 Valor Arrematado (R$)", min_value=0.0, step=100.0)

# Campos de modelo e ano
col3, col4 = st.columns(2)
with col3:
    modelo = st.text_input("🚗 Modelo do Veículo")
with col4:
    ano = st.text_input("📅 Ano")

# Função para entrada de taxa com radio buttons
def entrada_taxa(nome_taxa, chave):
    st.markdown(f"**{nome_taxa}**")
    modo = st.radio("Escolha o tipo", ["Percentual (%)", "Valor Fixo (R$)"], horizontal=True, key=f"modo_{chave}")
    if modo == "Percentual (%)":
        percentual = st.number_input(f"{nome_taxa} (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1, key=f"{chave}_percentual")
        return valor * percentual / 100
    else:
        valor_fixo = st.number_input(f"{nome_taxa} (R$)", min_value=0.0, value=0.0, step=10.0, key=f"{chave}_fixo")
        return valor_fixo

# Entradas das taxas
st.markdown("### 📌 Taxas Adicionais")
valor_taxa1 = entrada_taxa("Taxa 1", "taxa1")
valor_taxa2 = entrada_taxa("Taxa 2", "taxa2")
valor_taxa3 = entrada_taxa("Taxa 3", "taxa3")

# Entrada de valor Fipe
st.markdown("### 🚗 Valor de Mercado (Tabela Fipe)")
valor_fipe = st.number_input("Valor Fipe (R$)", min_value=0.0, step=100.0)

# Entrada de lucro desejado
st.markdown("### 📈 Lucro Desejado")
modo_lucro = st.radio("Tipo de Lucro", ["Percentual (%)", "Valor Fixo (R$)"], horizontal=True)
if modo_lucro == "Percentual (%)":
    lucro_percentual = st.number_input("Lucro (%)", min_value=0.0, max_value=100.0, value=20.0)
    preco_revenda = (valor + valor_taxa1 + valor_taxa2 + valor_taxa3) * (1 + lucro_percentual / 100)
else:
    lucro_fixo = st.number_input("Lucro (R$)", min_value=0.0, value=5000.0)
    preco_revenda = valor + valor_taxa1 + valor_taxa2 + valor_taxa3 + lucro_fixo

# Função para ícone
def obter_icone(nome):
    for chave in ICONES:
        if chave in nome:
            return ICONES[chave]
    return ICONES["outro"]

# Cálculo
if st.button("🔍 Calcular Valor Total e Projeção"):
    if valor > 0:
        total = valor + valor_taxa1 + valor_taxa2 + valor_taxa3
        margem_fipe = valor_fipe - preco_revenda if valor_fipe > 0 else None
        icone = obter_icone(nome_item)

        resultado = {
            "Item": nome_item.title(),
            "Modelo": modelo,
            "Ano": ano,
            "Ícone": icone,
            "Valor (R$)": round(valor, 2),
            "Taxa 1 (R$)": round(valor_taxa1, 2),
            "Taxa 2 (R$)": round(valor_taxa2, 2),
            "Taxa 3 (R$)": round(valor_taxa3, 2),
            "Total (R$)": round(total, 2),
            "Preço Revenda (R$)": round(preco_revenda, 2),
            "Valor Fipe (R$)": round(valor_fipe, 2),
            "Margem Fipe (R$)": round(margem_fipe, 2) if margem_fipe is not None else "N/A"
        }

        st.session_state["historico"].append(resultado)

        st.success(f"{icone} Resultado para **{nome_item.title()}**")
        st.write(f"📄 Modelo: {modelo}")
        st.write(f"📅 Ano: {ano}")
        st.write(f"📄 Taxa 1: {formatar_reais(valor_taxa1)}")
        st.write(f"📄 Taxa 2: {formatar_reais(valor_taxa2)}")
        st.write(f"📄 Taxa 3: {formatar_reais(valor_taxa3)}")
        st.write(f"💵 Custo Total: **{formatar_reais(total)}**")
        st.write(f"📈 Preço mínimo de revenda: **{formatar_reais(preco_revenda)}**")
        if valor_fipe > 0:
            st.write(f"📊 Valor Fipe: {formatar_reais(valor_fipe)}")
            st.write(f"📉 Margem sobre Fipe: {formatar_reais(margem_fipe)}")
    else:
        st.warning("Preencha o valor arrematado corretamente.")

# Histórico
if st.session_state["historico"]:
    st.markdown("---")
    st.markdown("### 📊 Histórico de Cálculos Realizados")
    df = pd.DataFrame(st.session_state["historico"])
    st.dataframe(df, use_container_width=True)

    # Exportar CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📄 Exportar Histórico para CSV",
        data=csv,
        file_name="calculos_leilao.csv",
        mime="text/csv"
    )

    # Gráfico de rentabilidade
    st.markdown("### 📈 Gráfico de Rentabilidade por Item")
    df["Lucro"] = df["Preço Revenda (R$)"] - df["Total (R$)"]
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(df["Item"], df["Lucro"], color="#2E8B57")
    ax.set_title("Rentabilidade por Item", fontsize=16)
    ax.set_ylabel("Lucro (R$)", fontsize=12)
    ax.set_xlabel("Item", fontsize=12)
    ax.grid(axis="y", linestyle="--", alpha=0.7)

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 50, formatar_reais(height), ha='center', va='bottom', fontsize=10)

    st.pyplot(fig)
