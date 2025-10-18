import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Calculadora de Leilão", layout="centered")

# Histórico
if "historico" not in st.session_state:
    st.session_state["historico"] = []

st.markdown("<h1 style='text-align:center;color:#2E8B57;'>🛒 Calculadora de Leilão</h1>", unsafe_allow_html=True)

# Valor arrematado
col1, col2 = st.columns(2)
with col1:
    nome_item = st.text_input("📝 Nome do Item").strip().lower()
with col2:
    valor = st.number_input("💰 Valor Arrematado (R$)", min_value=0.0, step=100.0)

# Consulta à API da Tabela Fipe
st.markdown("### 🚗 Dados do Veículo")

# Marcas
res_marcas = requests.get("https://fipe.parallelum.com.br/api/v2/cars/brands")
if res_marcas.status_code == 200:
    marcas = res_marcas.json()
    marca_opcoes = {m["name"]: m["code"] for m in marcas}
    marca_nome = st.selectbox("Marca", list(marca_opcoes.keys()))
    marca_id = marca_opcoes[marca_nome]
else:
    st.error("❌ Não foi possível carregar as marcas.")
    st.stop()

# Modelos
res_modelos = requests.get(f"https://fipe.parallelum.com.br/api/v2/cars/brands/{marca_id}/models")
if res_modelos.status_code == 200 and "models" in res_modelos.json():
    modelos = res_modelos.json()["models"]
    modelo_opcoes = {m["name"]: m["code"] for m in modelos}
    modelo_nome = st.selectbox("Modelo", list(modelo_opcoes.keys()))
    modelo_id = modelo_opcoes[modelo_nome]
else:
    st.error("❌ Não foi possível carregar os modelos.")
    st.stop()

# Anos
res_anos = requests.get(f"https://fipe.parallelum.com.br/api/v2/cars/brands/{marca_id}/models/{modelo_id}/years")
if res_anos.status_code == 200:
    anos = res_anos.json()
    ano_opcoes = {a["name"]: a["code"] for a in anos}
    ano_nome = st.selectbox("Ano", list(ano_opcoes.keys()))
    ano_id = ano_opcoes[ano_nome]
else:
    st.error("❌ Não foi possível carregar os anos.")
    st.stop()

# Valor Fipe
valor_fipe = 0.0
res_fipe = requests.get(f"https://fipe.parallelum.com.br/api/v2/cars/brands/{marca_id}/models/{modelo_id}/years/{ano_id}")
if res_fipe.status_code == 200 and "price" in res_fipe.json():
    fipe_data = res_fipe.json()
    valor_fipe = float(fipe_data["price"].replace("R$ ", "").replace(".", "").replace(",", "."))
    st.success(f"📊 Valor Fipe: R$ {valor_fipe:.2f}")
else:
    st.warning("⚠️ Não foi possível obter o valor Fipe.")

# Função para entrada de taxa
def entrada_taxa(nome_taxa, chave):
    st.markdown(f"**{nome_taxa}**")
    modo = st.radio("Escolha o tipo", ["Percentual (%)", "Valor Fixo (R$)"], horizontal=True, key=f"modo_{chave}")
    if modo == "Percentual (%)":
        percentual = st.number_input(f"{nome_taxa} (%)", min_value=0.0, max_value=100.0, value=0.0, step=0.1, key=f"{chave}_percentual")
        return valor * percentual / 100
    else:
        valor_fixo = st.number_input(f"{nome_taxa} (R$)", min_value=0.0, value=0.0, step=10.0, key=f"{chave}_fixo")
        return valor_fixo

# Taxas
st.markdown("### 📌 Taxas Adicionais")
valor_taxa1 = entrada_taxa("Taxa 1", "taxa1")
valor_taxa2 = entrada_taxa("Taxa 2", "taxa2")
valor_taxa3 = entrada_taxa("Taxa 3", "taxa3")

# Lucro desejado
st.markdown("### 📈 Lucro Desejado")
modo_lucro = st.radio("Tipo de Lucro", ["Percentual (%)", "Valor Fixo (R$)"], horizontal=True)
if modo_lucro == "Percentual (%)":
    lucro_percentual = st.number_input("Lucro (%)", min_value=0.0, max_value=100.0, value=20.0)
    preco_revenda = (valor + valor_taxa1 + valor_taxa2 + valor_taxa3) * (1 + lucro_percentual / 100)
else:
    lucro_fixo = st.number_input("Lucro (R$)", min_value=0.0, value=5000.0)
    preco_revenda = valor + valor_taxa1 + valor_taxa2 + valor_taxa3 + lucro_fixo

# Cálculo final
if st.button("🔍 Calcular Valor Total e Projeção"):
    if valor > 0:
        total = valor + valor_taxa1 + valor_taxa2 + valor_taxa3
        margem_fipe = valor_fipe - preco_revenda if valor_fipe > 0 else None

        resultado = {
            "Item": nome_item.title(),
            "Marca": marca_nome,
            "Modelo": modelo_nome,
            "Ano": ano_nome,
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

        st.success(f"🔧 Resultado para **{modelo_nome} {ano_nome}**")
        st.write(f"💵 Custo Total: **R$ {total:.2f}**")
        st.write(f"📈 Preço mínimo de revenda: **R$ {preco_revenda:.2f}**")
        st.write(f"📊 Valor Fipe: R$ {valor_fipe:.2f}")
        st.write(f"📉 Margem sobre Fipe: R$ {margem_fipe:.2f}")
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
