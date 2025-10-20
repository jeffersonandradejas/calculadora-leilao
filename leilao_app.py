import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Calculadora de Leilão", layout="centered")

def formatar_reais(valor):
    valor_str = f"{valor:,.2f}"
    valor_str = valor_str.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {valor_str}"

ICONES = {
    "computador": "🖥️", "notebook": "💻", "carro": "🚗", "moto": "🏍️",
    "bicicleta": "🚲", "impressora": "🖨️", "servidor": "🗄️", "monitor": "🖥️",
    "celular": "📱", "caminhão": "🚚", "outro": "📦"
}

if "historico" not in st.session_state:
    st.session_state["historico"] = []

st.markdown("<h1 style='text-align:center;color:#2E8B57;'>🛒 Calculadora de Leilão</h1>", unsafe_allow_html=True)
st.markdown("Preencha os dados abaixo para calcular os encargos e projeção de revenda:")

col1, col2 = st.columns(2)
with col1:
    nome_item = st.text_input("📝 Nome do Item").strip().lower()
with col2:
    valor = st.number_input("💰 Valor Arrematado (R$)", min_value=0.0, step=100.0)

col3, col4 = st.columns(2)
with col3:
    modelo = st.text_input("🚗 Modelo do Veículo")
with col4:
    ano = st.text_input("📅 Ano")

def entrada_taxa(nome_taxa, chave):
    st.markdown(f"**{nome_taxa}**")
    modo = st.radio("Escolha o tipo", ["Percentual (%)", "Valor Fixo (R$)"], horizontal=True, key=f"modo_{chave}")
    if modo == "Percentual (%)":
        percentual = st.number_input(f"{nome_taxa} (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1, key=f"{chave}_percentual")
        return valor * percentual / 100
    else:
        valor_fixo = st.number_input(f"{nome_taxa} (R$)", min_value=0.0, value=0.0, step=10.0, key=f"{chave}_fixo")
        return valor_fixo

st.markdown("### 📌 Taxas Adicionais")
valor_taxa1 = entrada_taxa("Taxa 1", "taxa1")
valor_taxa2 = entrada_taxa("Taxa 2", "taxa2")
valor_taxa3 = entrada_taxa("Taxa 3", "taxa3")

st.markdown("### 🚗 Valor de Mercado (Tabela Fipe)")
valor_fipe = st.number_input("Valor Fipe (R$)", min_value=0.0, step=100.0)

st.markdown("### 📈 Lucro Desejado")
modo_lucro = st.radio("Tipo de Lucro", ["Percentual (%)", "Valor Fixo (R$)"], horizontal=True)
if modo_lucro == "Percentual (%)":
    lucro_percentual = st.number_input("Lucro (%)", min_value=0.0, max_value=100.0, value=20.0)
    preco_revenda = (valor + valor_taxa1 + valor_taxa2 + valor_taxa3) * (1 + lucro_percentual / 100)
else:
    lucro_fixo = st.number_input("Lucro (R$)", min_value=0.0, value=5000.0)
    preco_revenda = valor + valor_taxa1 + valor_taxa2 + valor_taxa3 + lucro_fixo

def obter_icone(nome):
    for chave in ICONES:
        if chave in nome:
            return ICONES[chave]
    return ICONES["outro"]

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
            "Margem Fipe (R$)": round(margem_fipe, 2) if margem_fipe is not None else None
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

if st.session_state["historico"]:
    st.markdown("---")
    st.markdown("### 📊 Histórico de Cálculos Realizados")
    df = pd.DataFrame(st.session_state["historico"])

    # ✅ Correção do erro 2: garantir que todos os dados sejam strings válidas
    df = df.astype(str)

    # ✅ Correção do erro 3: filtrar linhas com valores válidos para cálculo de lucro
    df_filtrado = df[df["Preço Revenda (R$)"].str.replace(",", "").str.replace(".", "").str.isnumeric()]
    df_filtrado["Preço Revenda (R$)"] = df_filtrado["Preço Revenda (R$)"].astype(float)
    df_filtrado["Total (R$)"] = df_filtrado["Total (R$)"].astype(float)
    df_filtrado["Lucro"] = df_filtrado["Preço Revenda (R$)"] - df_filtrado["Total (R$)"]

    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📄 Exportar Histórico para CSV",
        data=csv,
        file_name="calculos_leilao.csv",
        mime="text/csv"
    )

    st.markdown("### 📈 Gráfico de Rentabilidade por Item")
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(df_filtrado["Item"], df_filtrado["Lucro"], color="#2E8B57")
    ax.set_title("Rentabilidade por
