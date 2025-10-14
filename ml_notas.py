import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from minisom import MiniSom

def clusters_anglo_liceu():
    # ========================

    # Carregar dataset

    # ========================

    @st.cache_data
    def carregar_dados():
        df = pd.read_csv("data/notas_anglo_liceu.csv", sep=";", encoding="latin1")
        return df

    df = carregar_dados()
    st.write("### Dataset Carregado", df.head())

    # ========================

    # Seleção de colunas numéricas

    # ========================

    colunas_numericas = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    st.write("Colunas numéricas disponíveis:", colunas_numericas)

    colunas_escolhidas = st.multiselect(
    "Selecione as colunas para análise",
    colunas_numericas,
    default=colunas_numericas[:2]
    )

    if len(colunas_escolhidas) >= 2:
        # Preparar dados
        df_filtrado = df[colunas_escolhidas].dropna().copy()
        X_scaled = StandardScaler().fit_transform(df_filtrado)

        # ========================
        # DBSCAN
        # ========================
        eps = st.slider("DBSCAN - eps", 0.1, 5.0, 1.0, 0.1)
        min_samples = st.slider("DBSCAN - min_samples", 1, 20, 5)

        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        clusters_dbscan = dbscan.fit_predict(X_scaled)

        df_filtrado["Cluster_DBSCAN"] = clusters_dbscan.astype(str)

        st.write("### Resultado DBSCAN")
        fig_dbscan = px.scatter(
            df_filtrado,
            x=colunas_escolhidas[0],
            y=colunas_escolhidas[1],
            color="Cluster_DBSCAN",
            title="Clusters DBSCAN"
        )
        st.plotly_chart(fig_dbscan, use_container_width=True)


        # ========================
        # SOM
        # ========================
        st.write("### Self-Organizing Map (SOM)")
        grid_x = st.slider("Tamanho do SOM (x)", 2, 15, 5)
        grid_y = st.slider("Tamanho do SOM (y)", 2, 15, 5)

        som = MiniSom(grid_x, grid_y, X_scaled.shape[1], sigma=1.0, learning_rate=0.5)
        som.random_weights_init(X_scaled)
        som.train_random(X_scaled, 500)

        clusters_som = []
        for x in X_scaled:
            w = som.winner(x)
            clusters_som.append(str(w))
        df_filtrado["Cluster_SOM"] = clusters_som

        fig_som = px.scatter(
            df_filtrado,
            x=colunas_escolhidas[0],
            y=colunas_escolhidas[1],
            color="Cluster_SOM",
            title="Clusters SOM"
        )
        st.plotly_chart(fig_som, use_container_width=True)

        # ========================
        # COMBINADO DBSCAN + SOM
        # ========================
        st.write("### Comparação DBSCAN + SOM")
        fig_combinado = px.scatter(
            df_filtrado,
            x=colunas_escolhidas[0],
            y=colunas_escolhidas[1],
            color="Cluster_DBSCAN",   # cor pelo DBSCAN
            symbol="Cluster_SOM",     # símbolo pelo SOM
            title="Clusters DBSCAN (cores) + SOM (símbolos)"
        )
        st.plotly_chart(fig_combinado, use_container_width=True)

        # ========================
        # MATRIZ DE COMPARAÇÃO
        # ========================
        st.write("### Matriz de Comparação entre DBSCAN e SOM")
        matriz_comparacao = pd.crosstab(df_filtrado["Cluster_DBSCAN"], df_filtrado["Cluster_SOM"])
        st.dataframe(matriz_comparacao)

        # Heatmap da matriz
        fig_heatmap = px.imshow(
            matriz_comparacao,
            text_auto=True,
            color_continuous_scale="Blues",
            title="Heatmap da Comparação DBSCAN x SOM"
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)
    else:
        st.warning("Selecione pelo menos duas colunas numéricas para rodar a análise.")