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
def carregar_df():
    return pd.read_csv("enem_2024_dash.csv", sep=";", encoding="latin1")

# Chamada da função
df = carregar_df()

# --- Funções cacheadas para extrair filtros --- #
@st.cache_data
def get_ufs(df: pd.DataFrame) -> List[str]:
    return sorted(df["uf_prova"].unique())

@st.cache_data
def get_municipios(df: pd.DataFrame, uf_list: str | List[str]) -> List[str]:
    if isinstance(uf_list, str):  # Caso seja só 1 UF na seleção
        uf_list = [uf_list]
    return sorted(df[df["uf_prova"].isin(uf_list)]["municipio_prova"].unique())

@st.cache_data
def get_sexos(df: pd.DataFrame) -> List[str]:
    return sorted(df['sexo_labels'].unique())

@st.cache_data
def get_faixas_etarias(df: pd.DataFrame) -> List[str]:
    return sorted(df['faixa_etaria_labels'].unique())

@st.cache_data
def get_estados_civis(df: pd.DataFrame) -> List[str]:
    return sorted(df['estado_civil_labels'].unique())

@st.cache_data
def get_cores_racas(df: pd.DataFrame) -> List[str]:
    return sorted(df['cor_raca_labels'].unique())

@st.cache_data
def get_escolaridades_pais(df: pd.DataFrame) -> List[str]:
    return sorted(df['escolaridade_pai_labels'].unique())

@st.cache_data
def get_escolaridades_maes(df: pd.DataFrame) -> List[str]:
    return sorted(df['escolaridade_mae_labels'].unique())

# --- Barra lateral (Filtros) --- #
st.sidebar.header(":mag: --- Filtros --- :mag_right:")

# --- Filtro de UF --- #
ufs_disponiveis = get_ufs(df)

if "ufs_selecionadas" not in st.session_state:
    st.session_state["ufs_selecionadas"] = ufs_disponiveis.copy()

ufs_selecionadas = st.sidebar.multiselect(
    "Estado/DF",
    ufs_disponiveis,
    key="ufs_selecionadas"
)

if st.sidebar.button("🔄 Resetar Estados/DF"):
    st.session_state.pop("ufs_selecionadas")
    st.rerun()

# --- Filtro de município (dependente do(s) estado(s) selecionados(s)) --- #
municipios_disponiveis = get_municipios(df, ufs_selecionadas)

# Inicializa a lista de municípios selecionados no estado da sessão
if "municipios_selecionados" not in st.session_state:
    st.session_state["municipios_selecionados"] = municipios_disponiveis
    st.session_state["municipios_visiveis"] = []

# Busca por texto
municipio_input = st.sidebar.text_input(
    "Digite o nome do município:",
    placeholder="Ex: São Paulo"
)

# Filtra municípios que contenham o texto digitado
if municipio_input:
    municipios_filtrados = [municipio for municipio in municipios_disponiveis if municipio_input.lower() in municipio.lower()]
    municipios_selecionados = st.sidebar.selectbox(
        "Resultados da busca:",
        options=municipios_filtrados
    )

    # Botão para adicionar município sem perder os anteriores
    if st.sidebar.button("Adicionar município"):
        if municipios_selecionados not in st.session_state["municipios_visiveis"]:
            st.session_state["municipios_visiveis"].append(municipios_selecionados)

    # Mostrar os municípios selecionados até agora
    st.sidebar.write("Municípios selecionados:", st.session_state["municipios_visiveis"])

    # Botão para limpar municípios
    if st.sidebar.button("Limpar municípios selecionados"):
        st.session_state["municipios_selecionados"] = []

# --- Filtro de sexo --- #
sexos_disponiveis = get_sexos(df)
sexos_selecionados = st.sidebar.multiselect(
    "Sexo",
    options=sexos_disponiveis,
    default=sexos_disponiveis
)

# --- Filtro de faixa etária --- #
faixas_etarias_disponiveis = get_faixas_etarias(df)

# Reordenação
faixas_reordenadas = (["Até 16"] if "Até 16" in faixas_etarias_disponiveis else []) + \
                     [faixa for faixa in faixas_etarias_disponiveis if faixa != "Até 16"]

if "faixas_etarias_selecionadas" not in st.session_state:
    st.session_state["faixas_etarias_selecionadas"] = faixas_reordenadas.copy()

faixas_etarias_selecionadas = st.sidebar.multiselect(
    "Faixa etária",
    options=faixas_reordenadas,
    key="faixas_etarias_selecionadas"
)

if st.sidebar.button("🔄 Resetar faixas etárias"):
    st.session_state.pop("faixas_etarias_selecionadas")
    st.rerun()

# --- Filtro de estado civil --- #
estados_civis_disponiveis = get_estados_civis(df)

# Reordenação
ordem_ec = ["Não informado", "Solteiro(a)", "Casado(a)/Mora com companheiro(a)", "Divorciado(a)/Desquitado(a)/Separado(a)", "Viúvo(a)"]

estados_civis_reordenados = [ec for ec in ordem_ec if ec in estados_civis_disponiveis]

if "estados_civis_selecionados" not in st.session_state:
    st.session_state["estados_civis_selecionados"] = estados_civis_reordenados.copy()

estados_civis_selecionados = st.sidebar.multiselect(
    "Estado civil",
    options=estados_civis_reordenados,
    key="estados_civis_selecionados"
)

if st.sidebar.button("🔄 Resetar estados civis"):
    st.session_state.pop("estados_civis_selecionados")
    st.rerun()

# --- Filtro de cor/raça --- #
cores_racas_disponiveis = get_cores_racas(df)

# Reordenação
ordem_cr = ["Não declarado",
            "Branca",
            "Preta",
            "Parda",
            "Amarela",
            "Indígena",
            "Não dispõe da informação"]

cores_racas_reordenadas = [cr for cr in ordem_cr if cr in cores_racas_disponiveis]

if "cores_racas_selecionadas" not in st.session_state:
    st.session_state["cores_racas_selecionadas"] = cores_racas_reordenadas.copy()

cores_racas_selecionadas = st.sidebar.multiselect(
    "Cor/raça",
    options=cores_racas_reordenadas,
    key="cores_racas_selecionadas"
)

if st.sidebar.button("🔄 Resetar cores/raças"):
    st.session_state.pop("cores_racas_selecionadas")
    st.rerun()

# --- Filtro de escolaridade do pai --- #
escolaridades_pais_disponiveis = get_escolaridades_pais(df)

# Reordenação
ordem_esc = ["Nunca estudou",
             "Fundamental I incompleto",
             "Fundamental I completo, mas não Fundamental II",
             "Fundamental II completo, mas não Médio",
             "Médio completo",
             "Superior completo",
             "Pós-graduação",
             "Não sei"]

escolaridades_pais_reordenadas = [esc for esc in ordem_esc if esc in escolaridades_pais_disponiveis]

if "escolaridades_pais_selecionadas" not in st.session_state:
    st.session_state["escolaridades_pais_selecionadas"] = escolaridades_pais_reordenadas.copy()

escolaridades_pais_selecionadas = st.sidebar.multiselect(
    "Cor/raça",
    options=escolaridades_pais_reordenadas,
    key="escolaridades_pais_selecionadas"
)

if st.sidebar.button("🔄 Resetar escolaridades dos pais"):
    st.session_state.pop("escolaridades_pais_selecionadas")
    st.rerun()

# --- Aplicando filtros no DataFrame --- #
df_filtrado = df[
    (df['uf_prova'].isin(ufs_selecionadas)) &
    (df["municipio_prova"].isin(st.session_state["municipios_selecionados"] if len(st.session_state["municipios_visiveis"]) < 1 else st.session_state["municipios_visiveis"])) &
    (df['sexo_labels'].isin(sexos_selecionados)) &
    (df['faixa_etaria_labels'].isin(faixas_etarias_selecionadas)) &
    (df['estado_civil_labels'].isin(estados_civis_selecionados)) &
    (df['cor_raca_labels'].isin(cores_racas_selecionadas)) &
    (df['escolaridade_pai_labels'].isin(escolaridades_pais_selecionadas))
]

# --- Página principal --- #
st.title(":books: Dashboard para análise dos microdados do ENEM 2024")
st.markdown("Explore os dados dos participantes do ENEM 2024. Utilize os filtros à esquerda para refinar suas análises.")

