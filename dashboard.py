from typing import List
import pandas as pd
import plotly.express as px
import streamlit as st

# --- Configurações da página --- #
# Título, ícone e layout da página
st.set_page_config(
    page_title="Dashboard para análise exploratória dos microdados do ENEM 2024",
    page_icon=":books:",
    layout="wide"
)

# --- Função cacheada para carregar os dados --- #
@st.cache_data
def carregar_dados():
    return pd.read_csv("enem_2024.csv", sep=";", encoding="latin1")

# Chamada da função
df = carregar_dados()

# --- Funções cacheadas para extrair filtros --- #
@st.cache_data
def get_estados(df: pd.DataFrame) -> List[str]:
    return sorted(df["uf_prova"].unique())

@st.cache_data
def get_municipios(df: pd.DataFrame, uf_list: str | List[str]) -> List[str]:
    if isinstance(uf_list, str):  # Caso seja só 1 UF na seleção
        uf_list = [uf_list]
    return sorted(df[df["uf_prova"].isin(uf_list)]["municipio_prova"].unique())

@st.cache_data
def get_faixas_etarias(df: pd.DataFrame) -> List[str]:
    return sorted(df['faixa_etaria_labels'].unique())

@st.cache_data
def get_sexos(df: pd.DataFrame) -> List[str]:
    return sorted(df['sexo_labels'].unique())

# --- Barra lateral (Filtros) --- #
st.sidebar.header(":mag: --- Filtros --- :mag_right:")

# --- Filtro de estado --- #
estados_disponiveis = get_estados(df)
ufs_selecionadas = st.sidebar.multiselect(
    "Estado",
    estados_disponiveis,
    default=estados_disponiveis
)

# --- Filtro de município (dependente do(s) estado(s) selecionados(s)) --- #
municipios_disponiveis = get_municipios(df, ufs_selecionadas)

# Busca por texto
municipio_input = st.sidebar.text_input(
    "Digite o nome do município:",
    placeholder="Ex: São Paulo"
)

# Filtra municípios que contenham o texto digitado
if municipio_input:
    municipios_filtrados = [municipio for municipio in municipios_disponiveis if municipio_input.lower() in municipio.lower()]
    municipios_selecionados = st.sidebar.multiselect(
        "Resultados da busca:",
        options=municipios_filtrados
    )

# --- Filtro de faixa etária --- #
faixas_etarias_disponiveis = get_faixas_etarias(df)
faixas_etarias_selecionadas = st.sidebar.multiselect(
    "Faixa etária",
    options=faixas_etarias_disponiveis,
    default=faixas_etarias_disponiveis
)

# --- Filtro de sexo --- #
sexos_disponiveis = get_sexos(df)
sexos_selecionados = st.sidebar.multiselect(
    "Sexo",
    options=sexos_disponiveis,
    default=sexos_disponiveis
)