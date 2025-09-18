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

@st.cache_data
def get_rendas_familiares(df: pd.DataFrame) -> List[str]:
    return sorted(df['renda_familiar_labels'].unique())

@st.cache_data
def get_tipos_escola(df: pd.DataFrame) -> List[str]:
    return sorted(df['tipo_escola_em_labels'].unique())

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

# Inicializações no session_state
if "municipios_visiveis" not in st.session_state:
    st.session_state["municipios_visiveis"] = []

if "municipio_result_sel" not in st.session_state:
    st.session_state["municipio_result_sel"] = []

# Campo de busca
municipio_input = st.sidebar.text_input(
    "Digite o nome do município:",
    placeholder="Ex: São Paulo",
    key="municipio_input"
)

# Filtro do município
municipios_filtrados = []
if st.session_state["municipio_input"]:
    municipios_filtrados = [
        m for m in municipios_disponiveis
        if str(st.session_state["municipio_input"]).lower() in m.lower()
    ]

# Selectbox controlado por session_state
st.sidebar.selectbox(
    "Resultados da busca:",
    options=municipios_filtrados,
    key="municipio_result_sel"
)

# Função auxiliar para adicionar municípios à lista
def adicionar_municipio():
    sel = st.session_state["municipio_result_sel"]
    if sel and sel not in st.session_state["municipios_visiveis"]:
        st.session_state["municipios_visiveis"].append(sel)
    
# Função auxiliar para limpar municípios
def limpar_municipios():
    st.session_state["municipios_visiveis"] = []
    st.session_state["municipio_result_sel"] = []
    st.session_state["municipio_input"] = ""

# Botões com on_click
st.sidebar.button("Adicionar município", on_click=adicionar_municipio)
st.sidebar.button("Limpar municípios selecionados", on_click=limpar_municipios)

# Mostra municípios selecionados
if st.session_state["municipios_visiveis"]:
    st.sidebar.write("Municípios selecionados:", st.session_state["municipios_visiveis"])
        
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
    "Escolaridade do pai",
    options=escolaridades_pais_reordenadas,
    key="escolaridades_pais_selecionadas"
)

if st.sidebar.button("🔄 Resetar escolaridades dos pais"):
    st.session_state.pop("escolaridades_pais_selecionadas")
    st.rerun()

# --- Filtro de escolaridade da mãe --- #
escolaridades_maes_disponiveis = get_escolaridades_maes(df)

# Reordenação
ordem_esc = ["Nunca estudou",
             "Fundamental I incompleto",
             "Fundamental I completo, mas não Fundamental II",
             "Fundamental II completo, mas não Médio",
             "Médio completo",
             "Superior completo",
             "Pós-graduação",
             "Não sei"]

escolaridades_maes_reordenadas = [esc for esc in ordem_esc if esc in escolaridades_maes_disponiveis]

if "escolaridades_maes_selecionadas" not in st.session_state:
    st.session_state["escolaridades_maes_selecionadas"] = escolaridades_maes_reordenadas.copy()

escolaridades_maes_selecionadas = st.sidebar.multiselect(
    "Escolaridade da mãe",
    options=escolaridades_maes_reordenadas,
    key="escolaridades_maes_selecionadas"
)

if st.sidebar.button("🔄 Resetar escolaridades das mães"):
    st.session_state.pop("escolaridades_maes_selecionadas")
    st.rerun()

# --- Filtro de renda familiar --- #
rendas_familiares_disponiveis = get_rendas_familiares(df)

# Reordenação
ordem_rf = ["Nenhuma renda",
            "Muito baixa (até 2 SM)",
            "Baixa (2-4 SM)",
            "Média-baixa (4-7 SM)",
            "Média (7-10 SM)",
            "Média-alta (10-15 SM)",
            "Alta (15-20 SM)",
            "Muito alta (20+ SM)"]

rendas_familiares_reordenadas = [rf for rf in ordem_rf if rf in rendas_familiares_disponiveis]

if "rendas_familiares_selecionadas" not in st.session_state:
    st.session_state["rendas_familiares_selecionadas"] = rendas_familiares_reordenadas.copy()

rendas_familiares_selecionadas = st.sidebar.multiselect(
    "Renda familiar mensal",
    options=rendas_familiares_reordenadas,
    key="rendas_familiares_selecionadas"
)

if st.sidebar.button("🔄 Resetar rendas familiares"):
    st.session_state.pop("rendas_familiares_selecionadas")
    st.rerun()

# --- Filtro de tipo de escola --- #
tipos_escola_disponiveis = get_tipos_escola(df)

# Reordenação
ordem_te = ["Não frequentou EM",
            "Somente escola pública",
            "Escola pública + privada (com bolsa)",
            "Escola pública + privada (sem bolsa)",
            "Somente escola privada (com bolsa)",
            "Somente escola privada (sem bolsa)"]

tipos_escola_reordenados = [te for te in ordem_te if te in tipos_escola_disponiveis]

if "tipos_escola_selecionados" not in st.session_state:
    st.session_state["tipos_escola_selecionados"] = tipos_escola_reordenados.copy()

tipos_escola_selecionados = st.sidebar.multiselect(
    "Tipo de escola - Ensino médio",
    options=tipos_escola_reordenados,
    key="tipos_escola_selecionados"
)

if st.sidebar.button("🔄 Resetar tipos de escola"):
    st.session_state.pop("tipos_escola_selecionados")
    st.rerun()

# --- Aplicando filtros no DataFrame --- #
def filtrar_dados(
    df: pd.DataFrame,
    ufs_selecionadas: List[str],
    sexos_selecionados: List[str],
    faixas_etarias_selecionadas: List[str],
    estados_civis_selecionados: List[str],
    cores_racas_selecionadas: List[str],
    escolaridades_pais_selecionadas: List[str],
    escolaridades_maes_selecionadas: List[str],
    rendas_familiares_selecionadas: List[str],
    tipos_escola_selecionados: List[str]
):
    """
    Aplica filtros no DataFrame de acordo com as seleções do usuário.
    Considera UFs obrigatoriamente e municípios apenas se existirem selecionados.
    """

    # Se houver municípios visíveis no session_state, usa eles
    municipios_tratados = (
        st.session_state["municipios_visiveis"]
        if len(st.session_state["municipios_visiveis"]) > 0
        else None
    )

    # Começa filtrando pelas UFs
    mask = df['uf_prova'].isin(ufs_selecionadas)

    # Só aplica filtro de município se houver seleção
    if municipios_tratados:
        if isinstance(municipios_tratados, str):
            municipios_tratados = [municipios_tratados]
        mask &= df["municipio_prova"].isin(municipios_tratados)

    # Aplica os demais filtros
    mask &= df['sexo_labels'].isin(sexos_selecionados)
    mask &= df['faixa_etaria_labels'].isin(faixas_etarias_selecionadas)
    mask &= df['estado_civil_labels'].isin(estados_civis_selecionados)
    mask &= df['cor_raca_labels'].isin(cores_racas_selecionadas)
    mask &= df['escolaridade_pai_labels'].isin(escolaridades_pais_selecionadas)
    mask &= df['escolaridade_mae_labels'].isin(escolaridades_maes_selecionadas)
    mask &= df['renda_familiar_labels'].isin(rendas_familiares_selecionadas)
    mask &= df['tipo_escola_em_labels'].isin(tipos_escola_selecionados)

    return df[mask]

df_filtrado = filtrar_dados(
    df,
    ufs_selecionadas,
    sexos_selecionados,
    faixas_etarias_selecionadas,
    estados_civis_selecionados,
    cores_racas_selecionadas,
    escolaridades_pais_selecionadas,
    escolaridades_maes_selecionadas,
    rendas_familiares_selecionadas,
    tipos_escola_selecionados,
)

# --- Página principal --- #
st.title(":books: Dashboard para análise dos microdados do ENEM 2024")
st.markdown("Explore os dados dos participantes do ENEM 2024. Utilize os filtros à esquerda para refinar suas análises.")

# --- Métricas gerais --- #
st.subheader("Métricas gerais")
st.markdown("Médias das notas obtidas em cada uma das 5 áreas avaliadas, além da média da somatória dessas mesmas notas.")

if not df_filtrado.empty:
    # Cria a coluna com a média da somatória das notas
    df_filtrado["nota_somatoria"] = df_filtrado[[
        "nota_redacao",
        "nota_ciencias_natureza",
        "nota_ciencias_humanas",
        "nota_matematica",
        "nota_linguagens_codigos"
    ]].mean(axis=1)

    total_inscritos = df_filtrado.shape[0]
    media_natureza = df_filtrado["nota_ciencias_natureza"].mean()
    media_humanas = df_filtrado["nota_ciencias_humanas"].mean()
    media_linguagens = df_filtrado["nota_linguagens_codigos"].mean()
    media_matematica = df_filtrado["nota_matematica"].mean()
    media_redacao = df_filtrado["nota_redacao"].mean()
    media_somatoria = df_filtrado["nota_somatoria"].mean()
    maxima_natureza = df_filtrado["nota_ciencias_natureza"].max()
    maxima_humanas = df_filtrado["nota_ciencias_humanas"].max()
    maxima_linguagens = df_filtrado["nota_linguagens_codigos"].max()
    maxima_matematica = df_filtrado["nota_matematica"].max()
    maxima_redacao = df_filtrado["nota_redacao"].max()
    maxima_somatoria = df_filtrado["nota_somatoria"].max() 
else:
    total_inscritos = 0
    media_natureza, media_humanas, media_linguagens, media_matematica, media_redacao, media_somatoria = 0, 0, 0, 0, 0, 0
    maxima_natureza, maxima_humanas, maxima_linguagens, maxima_matematica, maxima_redacao, maxima_somatoria = 0, 0, 0, 0, 0, 0
    
st.markdown(
    f"<h3 style='text-align: center;'>Total de inscritos: {total_inscritos:,}".replace(",", ".") + "</h3>",
    unsafe_allow_html=True
)
col1, col2, col3, col4, col5, col6 = st.columns(6)
col1.metric("Ciências da Natureza - Nota média", f"{media_natureza:.1f}")
col2.metric("Ciências Humanas - Nota média", f"{media_humanas:.1f}")
col3.metric("Linguagens e Códigos - Nota média", f"{media_linguagens:.1f}")
col4.metric("Matemática - Nota média", f"{media_matematica:.1f}")
col5.metric("Redação - Nota média", f"{media_redacao:.1f}")
col6.metric("Somatória - Nota média", f"{media_somatoria:.1f}")
col7, col8, col9, col10, col11, col12 = st.columns(6)
col7.metric("Ciências da Natureza - Nota máxima", f"{maxima_natureza:.1f}")
col8.metric("Ciências Humanas - Nota máxima", f"{maxima_humanas:.1f}")
col9.metric("Linguagens e Códigos - Nota máxima", f"{maxima_linguagens:.1f}")
col10.metric("Matemática - Nota máxima", f"{maxima_matematica:.1f}")
col11.metric("Redação - Nota máxima", f"{maxima_redacao:.1f}")
col12.metric("Somatória - Nota máxima", f"{maxima_somatoria:.1f}")
st.markdown("---")

# --- Visualizações --- #
st.subheader("Visualizações gráficas")
st.markdown("Abaixo, encontram-se gráficos que fixam, de acordo com os filtros aplicados, proporções entre aspectos sociais dos estudantes, tais como (i) sexos, (ii) cores/raças, (iii) estados civis e (iv) tipos de escola em que eles frequentaram no Ensino Médio.")

col_graf1, col_graf2 = st.columns(2)
st.markdown("---")

with col_graf1:
    if not df_filtrado.empty:
        sexo_contagem = df_filtrado['sexo_labels'].value_counts().reset_index()
        sexo_contagem.columns = ['sexo', 'quantidade']
        grafico_sexo = px.pie(
            sexo_contagem,
            names='sexo',
            values='quantidade',
            title='Sexos',
            hole=0.4,
            color='sexo',
            color_discrete_map={
                "Masculino": "blue",
                "Feminino": "red"
            }
        )
        grafico_sexo.update_traces(textinfo='percent+label')
        st.plotly_chart(grafico_sexo, use_container_width=True)
    else:
        st.warning("Nenhum dado para ser exibido no gráfico com a proporção entre os sexos dos estudantes. Cheque os filtros.")

with col_graf2:
    if not df_filtrado.empty:
        cor_raca_contagem = df_filtrado['cor_raca_labels'].value_counts().reset_index()
        cor_raca_contagem.columns = ['cor_raca', 'quantidade']
        grafico_cor_raca = px.pie(
            cor_raca_contagem,
            names='cor_raca',
            values='quantidade',
            title='Cores/raças',
            hole=0.4,
            color='cor_raca',
            color_discrete_map={
                "Não declarado": "grey",
                "Branca": "#e6e6e6ed",
                "Preta": "black",
                "Parda": "peru",
                "Amarela": "yellow",
                "Indígena": "red",
                "Não dispõe da informação": "green"
            }
        )
        grafico_cor_raca.update_traces(
            textinfo='percent+label',
        )
        st.plotly_chart(grafico_cor_raca, use_container_width=True)
    else:
        st.warning("Nenhum dado para ser exibido no gráfico com a proporção entre as cores/raças dos estudantes. Cheque os filtros.")

col_graf3, col_graf4 = st.columns(2)
st.markdown("---")

with col_graf3:
    if not df_filtrado.empty:
        estado_civil_contagem = df_filtrado['estado_civil_labels'].value_counts().reset_index()
        estado_civil_contagem.columns = ['estado_civil', 'quantidade']
        
        estado_civil_contagem["estado_civil_simplificado"] = estado_civil_contagem["estado_civil"].str.split("/").str[0]
        
        grafico_estado_civil = px.pie(
            estado_civil_contagem,
            names='estado_civil_simplificado',
            values='quantidade',
            title='Estados civis',
            hole=0.4,
            color='estado_civil_simplificado',
            color_discrete_map={
                "Não informado": "grey",
                "Solteiro(a)": "orange",
                "Casado(a)": "lightpink",
                "Divorciado(a)": "blue",
                "Viúvo(a)": "purple"
            }
        )
        grafico_estado_civil.update_traces(
            textinfo='percent+label',
        )
        st.plotly_chart(grafico_estado_civil, use_container_width=True)
    else:
        st.warning("Nenhum dado para ser exibido no gráfico com a proporção entre os estados civis dos estudantes. Cheque os filtros.")

with col_graf4:
    if not df_filtrado.empty:
        tipo_escola_contagem = df_filtrado['tipo_escola_em_labels'].value_counts().reset_index()
        tipo_escola_contagem.columns = ['tipo_escola', 'quantidade']
        
        mapa_simplificado = {
            "Não frequentou EM": "Não frequentou",
            "Somente escola pública": "Apenas pública",
            "Somente escola privada (sem bolsa)": "Privada s/ bolsa",
            "Somente escola privada (com bolsa)": "Privada c/ bolsa",
            "Escola pública + privada (sem bolsa)": "Mista s/ bolsa",
            "Escola pública + privada (com bolsa)": "Mista c/ bolsa"
        }

        tipo_escola_contagem["tipo_escola_simplificado"] = (
            tipo_escola_contagem["tipo_escola"]
            .map(mapa_simplificado)
            .fillna(tipo_escola_contagem["tipo_escola"])
        )

        grafico_tipo_escola = px.pie(
            tipo_escola_contagem,
            names='tipo_escola_simplificado',
            values='quantidade',
            title='Tipos de escola - Ensino Médio',
            hole=0.4,
            color='tipo_escola',
            color_discrete_map={
                "Não frequentou EM": "grey",
                "Somente escola pública": "red",
                "Escola pública + privada (com bolsa)": "lightblue",
                "Escola pública + privada (sem bolsa)": "blue",
                "Somente escola privada (com bolsa)": "lightgreen",
                "Somente escola privada (sem bolsa)": "darkgreen"
            }
        )
        grafico_tipo_escola.update_traces(
            textinfo='percent+label',
        )
        st.plotly_chart(grafico_tipo_escola, use_container_width=True)
    else:
        st.warning("Nenhum dado para ser exibido no gráfico com a proporção entre os tipos de escola em que os estudantes frequentaram no Ensino Médio. Cheque os filtros.")

col_graf5, col_graf6, col_graf7 = st.columns(3)

with col_graf5:
    if not df_filtrado.empty:
        grafico_hist_natureza = px.histogram(
            df_filtrado,
            x='nota_ciencias_natureza',
            nbins=30,
            title='Distribuição das notas - Ciências da Natureza',
            labels={'nota_ciencias_natureza': 'Notas - Ciências da Natureza'}
        )
        grafico_hist_natureza.update_layout(
            yaxis_title="Quantidade",
            title_x=0.1
        )
        grafico_hist_natureza.update_traces(
            marker_color="green"
        )
        st.plotly_chart(grafico_hist_natureza, use_container_width=True)
    else:
        st.warning("Nenhum dado para ser exibido no gráfico de distribuição pelas notas da prova de Ciências da Natureza. Cheque os filtros.")

with col_graf6:
    if not df_filtrado.empty:
        grafico_hist_humanas = px.histogram(
            df_filtrado,
            x='nota_ciencias_humanas',
            nbins=30,
            title='Distribuição das notas - Ciências Humanas',
            labels={'nota_ciencias_humanas': 'Notas - Ciências Humanas', 'count': 'Quantidade'}
        )
        grafico_hist_humanas.update_layout(
            yaxis_title="Quantidade",
            title_x=0.1
        )
        grafico_hist_humanas.update_traces(
            marker_color="red"
        )
        st.plotly_chart(grafico_hist_humanas, use_container_width=True)
    else:
        st.warning("Nenhum dado para ser exibido no gráfico de distribuição pelas notas da prova de Ciências Humanas. Cheque os filtros.")

with col_graf7:
    if not df_filtrado.empty:
        grafico_hist_linguagens = px.histogram(
            df_filtrado,
            x='nota_linguagens_codigos',
            nbins=30,
            title='Distribuição das notas - Linguagens e Códigos',
            labels={'nota_linguagens_codigos': 'Notas - Linguagens e Códigos'}
        )
        grafico_hist_linguagens.update_layout(
            yaxis_title="Quantidade",
            title_x=0.1
        )
        grafico_hist_linguagens.update_traces(
            marker_color="blue"
        )
        st.plotly_chart(grafico_hist_linguagens, use_container_width=True)
    else:
        st.warning("Nenhum dado para ser exibido no gráfico de distribuição pelas notas da prova de Linguagens e Códigos. Cheque os filtros.")

col_graf8, col_graf9, col_graf10 = st.columns(3)
st.markdown("---")

with col_graf8:
    if not df_filtrado.empty:
        grafico_hist_matematica = px.histogram(
            df_filtrado,
            x='nota_matematica',
            nbins=30,
            title='Distribuição das notas - Matemática',
            labels={'nota_matematica': 'Notas - Matemática'}
        )
        grafico_hist_matematica.update_layout(
            yaxis_title="Quantidade",
            title_x=0.1
        )
        grafico_hist_matematica.update_traces(
            marker_color="yellow"
        )
        st.plotly_chart(grafico_hist_matematica, use_container_width=True)
    else:
        st.warning("Nenhum dado para ser exibido no gráfico de distribuição pelas notas da prova de Matemática. Cheque os filtros.")

with col_graf9:
    if not df_filtrado.empty:
        grafico_hist_redacao = px.histogram(
            df_filtrado,
            x='nota_redacao',
            nbins=30,
            title='Distribuição das notas - Redação',
            labels={'nota_redacao': 'Notas - Redação'}
        )
        grafico_hist_redacao.update_layout(
            yaxis_title="Quantidade",
            title_x=0.1
        )
        grafico_hist_redacao.update_traces(
            marker_color="purple"
        )
        st.plotly_chart(grafico_hist_redacao, use_container_width=True)
    else:
        st.warning("Nenhum dado para ser exibido no gráfico de distribuição pelas notas da prova de Redação. Cheque os filtros.")

with col_graf10:
    if not df_filtrado.empty:
        grafico_hist_somatoria = px.histogram(
            df_filtrado,
            x='nota_somatoria',
            nbins=30,
            title='Distribuição das notas - Média da Somatória',
            labels={'nota_somatoria': 'Notas - Média da Somatória'}
        )
        grafico_hist_somatoria.update_layout(
            yaxis_title="Quantidade",
            title_x=0.1
        )
        grafico_hist_somatoria.update_traces(
            marker_color="orange"
        )
        st.plotly_chart(grafico_hist_somatoria, use_container_width=True)
    else:
        st.warning("Nenhum dado para ser exibido no gráfico de distribuição pela média da somatória das notas de todas as provas. Cheque os filtros.")

col_graf11, col_graf12, col_graf13 = st.columns(3)
st.markdown("---")

with col_graf11:
    if not df_filtrado.empty:
        faixa_etaria_contagem = df_filtrado['faixa_etaria_labels'].value_counts().reset_index()
        faixa_etaria_contagem.columns = ['faixa_etaria', 'quantidade']

        grafico_bar_faixa_etaria = px.bar(
            faixa_etaria_contagem,
            x="quantidade",
            y="faixa_etaria",
            orientation="h",
            title="Distribuição por Faixa Etária",
            color="faixa_etaria"
        )
        st.plotly_chart(grafico_bar_faixa_etaria, use_container_width=True)

with col_graf12:
    if not df_filtrado.empty:
        pais_maes = df_filtrado.melt(
            value_vars=["escolaridade_pai_labels", "escolaridade_mae_labels"],
            var_name="origem",
            value_name="escolaridade"
        )

        fig = px.histogram(
            pais_maes,
            x="escolaridade",
            color="origem",
            barmode="group",
            title="Escolaridade do Pai e da Mãe"
        )
        fig.update_xaxes(title="Escolaridade", tickangle=45)
        fig.update_yaxes(title="Quantidade")
        st.plotly_chart(fig, use_container_width=True)

with col_graf13:
    if not df_filtrado.empty:
        renda_contagem = df_filtrado['renda_familiar_labels'].value_counts().reset_index()
        renda_contagem.columns = ['renda', 'quantidade']

        fig = px.bar(
            renda_contagem,
            x="renda",
            y="quantidade",
            title="Distribuição por Renda Familiar",
            color="renda"
        )
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

