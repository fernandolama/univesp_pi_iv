import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN, KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor
from minisom import MiniSom

def clusters_anglo_liceu():
    # ========================

    # Carregar dataset

    # ========================

    @st.cache_data
    def carregar_dados():
        df = pd.read_csv("data/notas_colegio_teste.csv", sep=";", encoding="latin1")
        return df

    df = carregar_dados()
    st.write("### Dataset Carregado", df.head())

    # ========================

    # Seleção de colunas numéricas

    # ========================

    colunas_numericas = df.select_dtypes(include=["int64", "float64"])
    st.write("Colunas numéricas disponíveis:", colunas_numericas.columns.tolist())

    colunas_escolhidas = st.multiselect(
    "Selecione as colunas para análise",
    colunas_numericas.columns.tolist(),
    default=colunas_numericas.columns.tolist()[:2]
    )

    if len(colunas_escolhidas) >= 2:
        # Preparar dados
        df_filtrado = df[colunas_escolhidas].dropna().copy()
        X_scaled = StandardScaler().fit_transform(df_filtrado)

        # ============================== 
        # Estatística descritiva simples 
        # ============================== 
        st.subheader("📊 Estatística Descritiva") 
        st.write(colunas_numericas.describe()) 
        
        # Maiores e menores notas por disciplina 
        maiores = colunas_numericas.max().sort_values(ascending=False) 
        menores = colunas_numericas.min().sort_values(ascending=True) 
        st.write("### Maiores notas por disciplina", maiores) 
        st.write("### Menores notas por disciplina", menores)

        # ============================== 
        # RandomForest - Importância das disciplinas 
        # ============================== 
        st.subheader("🌲 RandomForest - Importância das disciplinas") 
        # Seleciona apenas colunas numéricas antes de calcular a média
        colunas_notas = df[[
            "nota_ciencias_natureza",
            "nota_ciencias_humanas",
            "nota_linguagens_codigos",
            "nota_matematica",
            "nota_redacao"
        ]].dropna()
        y = colunas_notas.mean(axis=1) # média geral como "alvo" 
        rf = RandomForestRegressor(n_estimators=100, random_state=42)
        rf_scaled = StandardScaler().fit_transform(colunas_notas)
        rf.fit(rf_scaled, y) 
        importancia = pd.Series(rf.feature_importances_, index=colunas_notas.columns)
        importancia = importancia.sort_values(ascending=True) 
        
        fig_importancia = px.bar(
            importancia, 
            orientation="h", 
            title="Importância das disciplinas para o desempenho geral" 
        )
        
        st.plotly_chart(fig_importancia, use_container_width=True)

        # Explicação textual sobre o Random Forest
        st.info(
            "🌲 **Interpretação do algoritmo Random Forest:**\n"
            "- O Random Forest é um modelo de aprendizado supervisionado baseado em múltiplas árvores de decisão, usadas em conjunto para realizar previsões mais robustas e reduzir o risco de overfitting.\n"
            "- Cada árvore toma decisões sobre o desempenho dos alunos com base nas notas das disciplinas, e o modelo final combina essas árvores para encontrar padrões consistentes.\n"
            "- Uma das principais saídas da Random Forest é a **importância das variáveis**, que indica quanto cada disciplina contribui para explicar o desempenho geral.\n"
            "- Disciplinas com maior importância têm maior peso na diferenciação dos resultados entre alunos.\n"
            "- Por exemplo, se a nota de Matemática aparece como a variável mais importante, isso sugere que ela é um bom preditor do desempenho global.\n"
            "- Essa análise é útil para identificar **as áreas que mais influenciam o sucesso dos estudantes**, ajudando a priorizar ações pedagógicas e intervenções específicas."
        )

    
        # ============================== 
        # KMeans - Agrupamento de alunos 
        # ============================== 
        st.subheader("🤖 KMeans - Agrupamento")
        n_clusters = st.slider("Número de clusters (K)", 2, 10, 3) 
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10) 
        clusters = kmeans.fit_predict(X_scaled) 
        df["Cluster_KMeans"] = -1 
        df.loc[df_filtrado.index, "Cluster_KMeans"] = clusters.astype(str) 
        fig_clusters = px.scatter( 
            df_filtrado, 
            x=colunas_escolhidas[0], 
            y=colunas_escolhidas[1], 
            color=df.loc[df_filtrado.index, "Cluster_KMeans"], title="Clusters de alunos (KMeans)" 
        ) 
        st.plotly_chart(fig_clusters, use_container_width=True)

        st.info(
            "🤖 **Interpretação do algoritmo K-Means:**\n"
            "- O K-Means é um método de **clusterização não supervisionada**, que agrupa alunos com base em similaridades nas notas das disciplinas.\n"
            "- Cada ponto (aluno) é atribuído a um grupo cujo centro (centróide) representa o padrão médio de desempenho daquele cluster.\n"
            "- Os grupos formados indicam perfis de estudantes com características semelhantes, como desempenho equilibrado, alta nota em exatas, ou dificuldades específicas em uma área.\n"
            "- A quantidade de clusters (K) é definida previamente, permitindo comparar diferentes segmentações.\n"
            "- Essa análise ajuda a entender **padrões de aprendizado e diferenciação entre perfis de alunos**, auxiliando em estratégias pedagógicas mais direcionadas."
        )
        
        # ========================
        # DBSCAN
        # ========================
        st.subheader("🧩 DBSCAN - Agrupamento por densidade")
        eps = st.slider("eps - Raio máximo de vizinhança", 0.1, 5.0, 1.0, 0.1)
        min_samples = st.slider("min_samples - Exemplos mínimos a serem considerados", 1, 20, 5)

        st.info(
            "**Explicação sobre a parametrizaçãa do algoritmo:**\n"
            "1. O algoritmo escolhe um ponto qualquer.\n"
            "2. Cria uma 'bolha' de raio **eps** ao redor dele.\n"
            "3. Se dentro dessa 'bolha' houver ao menos **min_samples** pontos, então o ponto é considerado um core point e forma um cluster.\n"
            "4. Se não houver, o ponto pode ser classificado como border point (se estiver próximo de um core point) ou como noise, ou ruído (se não pertencer a cluster nenhum)."
        )
        
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

        st.info(
            "🧩 **Interpretação do algoritmo DBSCAN:**\n"
            "- O DBSCAN é um algoritmo de **clusterização baseada em densidade**, que identifica grupos de alunos de acordo com a concentração dos dados — sem precisar definir o número de clusters previamente.\n"
            "- Ele é capaz de detectar **grupos de comportamento atípico** (como alunos com desempenho muito alto ou muito baixo) e também **outliers**, que não se encaixam bem em nenhum padrão.\n"
            "- Os clusters representam regiões de alta densidade de alunos com notas semelhantes, enquanto os pontos ruidosos indicam casos excepcionais.\n"
            "- Essa abordagem é útil quando os grupos têm formas irregulares ou tamanhos diferentes, oferecendo uma visão mais flexível dos padrões de desempenho."
        )

        # ========================
        # SOM
        # ========================
        st.subheader("🧠 Self-Organizing Map (SOM)")
        grid_x = st.slider("Tamanho do SOM (x)", 2, 10, 3)
        grid_y = st.slider("Tamanho do SOM (y)", 1, 10, 1)

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

        st.info(
            "🧠 **Interpretação do algoritmo SOM (Self-Organizing Map):**\n"
            "- O SOM é uma **rede neural não supervisionada** que projeta dados multidimensionais (como notas em várias disciplinas) em um mapa bidimensional.\n"
            "- Cada célula do mapa representa um grupo de alunos com padrões semelhantes de desempenho.\n"
            "- A disposição espacial dos grupos no mapa reflete **relações de similaridade**: células próximas indicam alunos com perfis de notas parecidos.\n"
            "- Regiões do mapa mais distantes representam perfis distintos, como grupos com alto desempenho em exatas versus linguagens.\n"
            "- Essa técnica permite visualizar de forma intuitiva **como os alunos se distribuem em diferentes perfis de aprendizagem** e identificar gradientes de desempenho entre os grupos."
        )

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
        st.write("### Matriz de Comparação entre Kmeans e SOM")
        matriz_comparacao = pd.crosstab(df["Cluster_KMeans"], df_filtrado["Cluster_SOM"])
        st.dataframe(matriz_comparacao)

        # Heatmap da matriz
        fig_heatmap = px.imshow(
            matriz_comparacao,
            text_auto=True,
            color_continuous_scale="Blues",
            title="Heatmap da Comparação Kmeans x SOM"
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)

       # ============================== 
        # PCA - Redução de Dimensionalidade 
        # ============================== 
        st.subheader("📉 PCA - Visualização em 2D")

        # Executar o PCA sobre as notas
        pca = PCA(n_components=2)
        pca_resultado = pca.fit_transform(colunas_notas)

        # Variância explicada
        var_exp = pca.explained_variance_ratio_ * 100
        st.write(f"### Variância explicada: PC1 = {var_exp[0]:.2f}% | PC2 = {var_exp[1]:.2f}%")

        # Adicionar resultados ao DataFrame
        df_pca = pd.DataFrame(pca_resultado, columns=["PC1", "PC2"])
        if "Cluster_KMeans" in df.columns:
            df_pca["Cluster_KMeans"] = df["Cluster_KMeans"].astype(str)
        else:
            df_pca["Cluster_KMeans"] = "0"

        # Gráfico PCA 2D
        st.write("### Redução de dimensionalidade (PCA)")
        fig_pca = px.scatter(
            df_pca,
            x="PC1",
            y="PC2",
            color="Cluster_KMeans",
            title="Visualização dos clusters após PCA (2 componentes principais)"
        )
        st.plotly_chart(fig_pca, use_container_width=True)

        # ========================
        # Gráficos de contribuição (loadings)
        # ========================
        st.write("### Contribuição das variáveis nos componentes principais")

        # Cálculo dos loadings
        loadings = pca.components_.T * np.sqrt(pca.explained_variance_)

        # PC1
        fig_loadings1 = px.bar(
            x=colunas_notas.columns,
            y=np.abs(loadings[:, 0]),
            title="Contribuição das variáveis no PC1",
            labels={"x": "Variável", "y": "Contribuição (|loading|)"}
        )
        st.plotly_chart(fig_loadings1, use_container_width=True)

        # PC2
        fig_loadings2 = px.bar(
            x=colunas_notas.columns,
            y=np.abs(loadings[:, 1]),
            title="Contribuição das variáveis no PC2",
            labels={"x": "Variável", "y": "Contribuição (|loading|)"}
        )
        st.plotly_chart(fig_loadings2, use_container_width=True)

        # Explicação textual sobre o PCA
        st.info(
            "📉 **Interpretação do PCA (Análise de Componentes Principais):**\n"
            "- O PCA reduz o conjunto de variáveis originais (as notas das disciplinas) para dois componentes principais (PC1 e PC2), que explicam a maior parte da variabilidade dos dados.\n"
            "- Cada ponto no gráfico representa um aluno, projetado nas dimensões que melhor sintetizam as diferenças de desempenho.\n"
            "- As cores representam os clusters identificados (ex: via KMeans), permitindo observar se há grupos bem separados ou sobrepostos.\n"
            "- As barras dos gráficos de contribuição mostram o quanto cada disciplina influencia em cada componente principal.\n"
            "- Disciplinas com maior contribuição em um componente indicam áreas que mais ajudam a diferenciar o desempenho dos estudantes — por exemplo, se Matemática e Ciências da Natureza dominam o PC1, isso sugere que essas notas explicam melhor a variação global do desempenho.\n"
            "- Essa análise permite compreender **quais áreas são mais determinantes para o desempenho geral** e pode orientar estratégias pedagógicas mais focadas."
        )

        st.markdown("---")

        st.subheader("💡 Esboço de diagnóstico")
        st.info(
            "- Analisando as saídas do **RandomForest** e os gráficos à popósito das **Contribuições no PC1 e PC2**, temos que as notas em redação e matemática são as que mais destoam em relação à média da somatóriaa das notas, não obstante sejam as mais determinantes para o desempenho geral.\n"
            "- Ao se comparar, por exemplo, as notas de redação no eixo x e de ciências humanas no eixo y, notam-se pontos mais difusos no quadrante superior direito (notas altas e ambas as provas) e quatro pontos no quadrante superior esquerdo (notas altas no eixo y, mas baixas no eixo x)\n"
            "- Isso indica que uma troca pedagógica entre os professores de ciências humanas e o professor de redação pode ser muito benéfica a este último."
        )

    else:
        st.warning("Selecione pelo menos duas colunas numéricas para rodar a análise.")