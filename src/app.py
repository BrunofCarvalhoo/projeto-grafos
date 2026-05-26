import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import pandas as pd
import json
import plotly.express as px


PALETA_GRAFICOS = ["#264653", "#2A9D8F", "#E9C46A", "#F4A261", "#E76F51"]
ESCALA_CONTINUA = "YlGnBu"


@st.cache_data
def carregar_dados(pasta_projeto: Path):
    pasta_out = pasta_projeto / "out"
    pasta_data = pasta_projeto / "data"

    df_grau = pd.read_csv(pasta_out / "graus.csv")
    df_grau.columns = df_grau.columns.str.strip()

    df_aeroportos = pd.read_csv(pasta_data / "aeroportos_data.csv")
    df_aeroportos.columns = df_aeroportos.columns.str.strip()

    df_grau = df_grau.merge(
        df_aeroportos[["iata", "cidade", "regiao"]],
        left_on="aeroporto",
        right_on="iata",
        how="left",
    )

    with open(pasta_out / "regioes.json", "r", encoding="utf-8") as f:
        dados_regioes = json.load(f)
    df_regioes = pd.DataFrame.from_dict(dados_regioes, orient="index").reset_index()
    df_regioes.rename(columns={"index": "regiao"}, inplace=True)
    df_regioes["tamanho"] = df_regioes["tamanho"].astype(int)
    df_regioes["densidade"] = df_regioes["densidade"].str.replace(",", ".").astype(float)
    df_regioes["regiao"] = df_regioes["regiao"].str.title()

    df_distancias = pd.read_csv(pasta_out / "distancias_rotas.csv")

    return df_grau, df_regioes, df_distancias


def pagina_analise(df_grau, df_regioes, df_distancias):
    st.title("Análise de Graus e Regiões")
    st.markdown("Estatísticas gerais do grafo, métricas de conexões e distribuição regional.")

    regioes_disponiveis = sorted(df_grau["regiao"].dropna().unique().tolist())

    #Distribuição dos Graus 
    st.subheader("Distribuição dos Graus dos Aeroportos")

    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        regioes_dist = st.multiselect(
            "Filtrar por região",
            options=regioes_disponiveis,
            default=regioes_disponiveis,
            key="dist_regioes",
        )
    with col_f2:
        grau_min = int(df_grau["grau"].min())
        grau_max = int(df_grau["grau"].max())
        faixa_grau = st.slider(
            "Faixa de grau", grau_min, grau_max, (grau_min, grau_max), key="dist_faixa"
        )

    df_dist = df_grau[
        df_grau["regiao"].isin(regioes_dist)
        & df_grau["grau"].between(faixa_grau[0], faixa_grau[1])
    ]
    fig_dist = px.histogram(
        df_dist,
        x="grau",
        color="regiao",
        nbins=10,
        title="Distribuição dos Graus dos Aeroportos",
        labels={"grau": "Grau", "count": "Quantidade de Aeroportos", "regiao": "Região"},
        color_discrete_sequence=PALETA_GRAFICOS,
    )
    fig_dist.update_layout(bargap=0.1, legend_title="Região")
    st.plotly_chart(fig_dist, use_container_width=True)

    st.divider()

    #Ranking de Grau por Aeroporto 
    st.subheader("Ranking de Grau por Aeroporto")

    col_f3, col_f4 = st.columns([2, 1])
    with col_f3:
        regioes_rank = st.multiselect(
            "Filtrar por região",
            options=regioes_disponiveis,
            default=regioes_disponiveis,
            key="rank_regioes",
        )
    with col_f4:
        top_n = st.slider("Top N aeroportos", 5, len(df_grau), len(df_grau), key="rank_topn")

    df_rank = (
        df_grau[df_grau["regiao"].isin(regioes_rank)]
        .sort_values("grau", ascending=False)
        .head(top_n)
    )
    fig_rank = px.bar(
        df_rank,
        x="aeroporto",
        y="grau",
        color="regiao",
        hover_data=["cidade"],
        title="Ranking de Grau por Aeroporto (IATA)",
        labels={"aeroporto": "Aeroporto (IATA)", "grau": "Grau", "regiao": "Região"},
        color_discrete_sequence=PALETA_GRAFICOS,
    )
    fig_rank.update_layout(xaxis_tickangle=-45, legend_title="Região")
    st.plotly_chart(fig_rank, use_container_width=True)

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        #Comparação de Conexões por Região
        st.subheader("Conexões por Região")

        regioes_conn = st.multiselect(
            "Regiões a exibir",
            options=df_regioes["regiao"].tolist(),
            default=df_regioes["regiao"].tolist(),
            key="conn_regioes",
        )
        df_conn = df_regioes[df_regioes["regiao"].isin(regioes_conn)].sort_values(
            "tamanho", ascending=False
        )
        fig_conn = px.bar(
            df_conn,
            x="regiao",
            y="tamanho",
            color="regiao",
            text="tamanho",
            title="Comparação de Conexões (Tamanho da Rede) por Região",
            labels={"regiao": "Região", "tamanho": "Número de Conexões"},
            color_discrete_sequence=PALETA_GRAFICOS,
        )
        fig_conn.update_traces(textposition="outside")
        fig_conn.update_layout(showlegend=False)
        st.plotly_chart(fig_conn, use_container_width=True)

    with col2:
        #Densidade por Região 
        st.subheader("Densidade de Conexões por Região")

        regioes_den = st.multiselect(
            "Regiões a exibir",
            options=df_regioes["regiao"].tolist(),
            default=df_regioes["regiao"].tolist(),
            key="den_regioes",
        )
        df_den = df_regioes[df_regioes["regiao"].isin(regioes_den)].sort_values(
            "densidade", ascending=False
        )
        fig_den = px.bar(
            df_den,
            x="regiao",
            y="densidade",
            color="regiao",
            text=df_den["densidade"].map("{:.4f}".format),
            title="Comparação de Densidade de Conexões por Região",
            labels={"regiao": "Região", "densidade": "Densidade"},
            color_discrete_sequence=PALETA_GRAFICOS,
        )
        fig_den.update_traces(textposition="outside")
        fig_den.update_layout(showlegend=False, xaxis_tickangle=-30)
        st.plotly_chart(fig_den, use_container_width=True)

    st.divider()

    #Mapa de Calor
    st.subheader("Mapa de Calor das Distâncias entre Aeroportos")

    origens_disp = sorted(df_distancias["origem"].unique())
    destinos_disp = sorted(df_distancias["destino"].unique())

    col_hm1, col_hm2 = st.columns(2)
    with col_hm1:
        origens_sel = st.multiselect(
            "Origens", origens_disp, default=origens_disp, key="hm_origens"
        )
    with col_hm2:
        destinos_sel = st.multiselect(
            "Destinos", destinos_disp, default=destinos_disp, key="hm_destinos"
        )

    df_hm = df_distancias[
        df_distancias["origem"].isin(origens_sel)
        & df_distancias["destino"].isin(destinos_sel)
    ]
    if not df_hm.empty:
        matriz = df_hm.pivot(index="origem", columns="destino", values="custo")
        fig_hm = px.imshow(
            matriz,
            color_continuous_scale=ESCALA_CONTINUA,
            title="Mapa de Calor das Distâncias Mínimas entre Aeroportos",
            labels={"color": "Custo do menor caminho", "x": "Destino", "y": "Origem"},
            text_auto=True,
        )
        st.plotly_chart(fig_hm, use_container_width=True)
    else:
        st.warning("Nenhuma rota encontrada para a seleção atual.")

    st.divider()

    #Ranking de Rotas por Distância 
    st.subheader("Ranking de Rotas por Custo do Menor Caminho")

    aeroportos_rot = sorted(
        set(df_distancias["origem"].unique()) | set(df_distancias["destino"].unique())
    )
    aeroportos_sel = st.multiselect(
        "Filtrar por aeroporto (origem ou destino)",
        options=aeroportos_rot,
        default=[],
        key="rot_aeroportos",
        placeholder="Todos os aeroportos",
    )

    col_rot1, col_rot2 = st.columns(2)
    with col_rot1:
        n_menores = st.slider("Menores rotas", 1, 10, 5, key="rot_menores")
    with col_rot2:
        n_maiores = st.slider("Maiores rotas", 1, 10, 5, key="rot_maiores")

    df_rot = df_distancias.copy()
    if aeroportos_sel:
        df_rot = df_rot[
            df_rot["origem"].isin(aeroportos_sel) | df_rot["destino"].isin(aeroportos_sel)
        ]

    df_rot["rota"] = df_rot["origem"] + " → " + df_rot["destino"]
    df_sorted = df_rot.sort_values("custo")
    menores = df_sorted.head(n_menores)
    maiores = df_sorted.tail(n_maiores).sort_values("custo")
    ranking = pd.concat([menores, maiores]).drop_duplicates()

    fig_rot = px.bar(
        ranking,
        y="rota",
        x="custo",
        orientation="h",
        color="custo",
        color_continuous_scale=ESCALA_CONTINUA,
        hover_data=["caminho"],
        title="Rotas com Menor e Maior Custo no Menor Caminho",
        labels={"rota": "Rota", "custo": "Custo do Menor Caminho"},
    )
    fig_rot.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_rot, use_container_width=True)


def pagina_arvores(pasta_out):
    st.title("Árvores de Percurso (Menor Caminho)")
    st.markdown(
        "Visualize de forma interativa os caminhos mais rápidos mapeados pelo algoritmo de Dijkstra."
    )

    if not pasta_out.exists():
        st.error(f"Erro: A pasta de saída não foi encontrada: {pasta_out}")
        return

    html_files = list(pasta_out.glob("arvore_percurso_*.html"))

    if not html_files:
        st.info(
            "Nenhum gráfico HTML de percurso encontrado na pasta 'out/'. "
            "Rode 'python src/arvore_percurso.py' primeiro."
        )
        return

    opcoes = {
        f.name.replace("arvore_percurso_", "").replace(".html", "").replace("_", " "): f
        for f in html_files
    }
    rota = st.selectbox("Selecione uma das rotas processadas:", sorted(opcoes.keys()))

    if rota:
        with open(opcoes[rota], "r", encoding="utf-8") as f:
            html = f.read()
        st.markdown(f"**Grafo Interativo da Rota:** `{rota}`")
        components.html(html, height=520, scrolling=False)


def main():
    st.set_page_config(page_title="Dashboard - Projeto Grafos", layout="wide")

    pasta_src = Path(__file__).resolve().parent
    pasta_projeto = pasta_src.parent
    pasta_out = pasta_projeto / "out"

    st.sidebar.title("Navegação")
    st.sidebar.markdown("Selecione a página que deseja visualizar:")
    pagina = st.sidebar.radio(
        "Ir para:",
        ["1. Análise de Graus e Regiões", "2. Árvores de Percurso (Menor Caminho)"],
    )

    df_grau, df_regioes, df_distancias = carregar_dados(pasta_projeto)

    if pagina == "1. Análise de Graus e Regiões":
        pagina_analise(df_grau, df_regioes, df_distancias)
    else:
        pagina_arvores(pasta_out)


if __name__ == "__main__":
    main()
