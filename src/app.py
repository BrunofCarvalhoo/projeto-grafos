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
    pasta_out  = pasta_projeto / "out"
    pasta_data = pasta_projeto / "data"

    df_grau = pd.read_csv(pasta_out / "graus.csv")
    df_grau.columns = df_grau.columns.str.strip()

    df_aeroportos = pd.read_csv(pasta_data / "aeroportos_data.csv")
    df_aeroportos.columns = df_aeroportos.columns.str.strip()

    df_grau = df_grau.merge(
        df_aeroportos[["iata", "cidade", "regiao"]],
        left_on="aeroporto", right_on="iata", how="left",
    )

    with open(pasta_out / "regioes.json", "r", encoding="utf-8") as f:
        dados_regioes = json.load(f)
    df_regioes = pd.DataFrame.from_dict(dados_regioes, orient="index").reset_index()
    df_regioes.rename(columns={"index": "regiao"}, inplace=True)
    df_regioes["tamanho"]   = df_regioes["tamanho"].astype(int)
    df_regioes["densidade"] = df_regioes["densidade"].str.replace(",", ".").astype(float)
    df_regioes["regiao"]    = df_regioes["regiao"].str.title()

    df_distancias = pd.read_csv(pasta_out / "distancias_rotas.csv")

    df_ego = pd.read_csv(pasta_out / "ego_aeroportos.csv")
    df_ego.columns = df_ego.columns.str.strip()
    df_ego['aeroporto'] = df_ego['aeroporto'].str.strip()

    df_adj = pd.read_csv(pasta_data / "adjacencias_aeroportos.csv")
    df_adj.columns = df_adj.columns.str.strip()
    df_adj['origem'] = df_adj['origem'].str.strip()
    df_adj['destino'] = df_adj['destino'].str.strip()
    df_adj['tipo_conexao'] = df_adj['tipo_conexao'].str.strip()

    return df_grau, df_regioes, df_distancias, df_ego, df_adj


def preparar_fluxo_regional_nao_direcionado(df_adj, df_grau):
    dados_aeroporto = df_grau[['aeroporto', 'regiao']].drop_duplicates()
    df_fluxo = (
        df_adj
        .merge(
            dados_aeroporto.rename(columns={'aeroporto': 'origem', 'regiao': 'regiao_origem'}),
            on='origem',
            how='left',
        )
        .merge(
            dados_aeroporto.rename(columns={'aeroporto': 'destino', 'regiao': 'regiao_destino'}),
            on='destino',
            how='left',
        )
        .dropna(subset=['regiao_origem', 'regiao_destino'])
    )
    df_fluxo['regiao_a'] = df_fluxo[['regiao_origem', 'regiao_destino']].min(axis=1)
    df_fluxo['regiao_b'] = df_fluxo[['regiao_origem', 'regiao_destino']].max(axis=1)
    return df_fluxo


def montar_matriz_regioes(df_fluxo):
    regioes = sorted(set(df_fluxo['regiao_a']) | set(df_fluxo['regiao_b']))
    matriz = pd.DataFrame(0, index=regioes, columns=regioes)
    pares = df_fluxo.groupby(['regiao_a', 'regiao_b']).size().reset_index(name='conexoes')

    for row in pares.itertuples():
        matriz.loc[row.regiao_a, row.regiao_b] = row.conexoes
        matriz.loc[row.regiao_b, row.regiao_a] = row.conexoes

    return matriz


def preparar_pesos_conexoes(df_adj):
    df_pesos = df_adj.copy()
    df_pesos['peso'] = pd.to_numeric(df_pesos['peso'], errors='coerce')
    return df_pesos.dropna(subset=['peso', 'tipo_conexao'])


def pagina_analise(df_grau, df_regioes, df_distancias):
    st.title("Análise de Graus e Regiões")
    st.markdown("Estatísticas gerais do grafo, métricas de conexões e distribuição regional.")

    regioes_disponiveis = sorted(df_grau["regiao"].dropna().unique().tolist())

    st.subheader("Distribuição dos Graus dos Aeroportos")
    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        regioes_dist = st.multiselect(
            "Filtrar por região", options=regioes_disponiveis,
            default=regioes_disponiveis, key="dist_regioes",
        )
    with col_f2:
        grau_min, grau_max = int(df_grau["grau"].min()), int(df_grau["grau"].max())
        faixa_grau = st.slider(
            "Faixa de grau", grau_min, grau_max, (grau_min, grau_max), key="dist_faixa"
        )

    df_d = df_grau[
        df_grau["regiao"].isin(regioes_dist) &
        df_grau["grau"].between(faixa_grau[0], faixa_grau[1])
    ]
    fig_dist = px.histogram(
        df_d, x="grau", color="regiao", nbins=10,
        title="Distribuição dos Graus dos Aeroportos",
        labels={"grau": "Grau", "count": "Quantidade de Aeroportos", "regiao": "Região"},
        color_discrete_sequence=PALETA_GRAFICOS,
    )
    fig_dist.update_layout(bargap=0.1, legend_title="Região")
    st.plotly_chart(fig_dist, use_container_width=True)

    st.divider()

    st.subheader("Ranking de Grau por Aeroporto")
    col_f3, col_f4 = st.columns([2, 1])
    with col_f3:
        regioes_rank = st.multiselect(
            "Filtrar por região", options=regioes_disponiveis,
            default=regioes_disponiveis, key="rank_regioes",
        )
    with col_f4:
        top_n = st.slider("Top N aeroportos", 5, len(df_grau), len(df_grau), key="rank_topn")

    df_rank = (
        df_grau[df_grau["regiao"].isin(regioes_rank)]
        .sort_values("grau", ascending=False).head(top_n)
    )
    fig_rank = px.bar(
        df_rank, x="aeroporto", y="grau", color="regiao", hover_data=["cidade"],
        title="Ranking de Grau por Aeroporto (IATA)",
        labels={"aeroporto": "Aeroporto (IATA)", "grau": "Grau", "regiao": "Região"},
        color_discrete_sequence=PALETA_GRAFICOS,
    )
    fig_rank.update_layout(xaxis_tickangle=-45, legend_title="Região")
    st.plotly_chart(fig_rank, use_container_width=True)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Conexões por Região")
        regioes_conn = st.multiselect(
            "Regiões a exibir", options=df_regioes["regiao"].tolist(),
            default=df_regioes["regiao"].tolist(), key="conn_regioes",
        )
        df_conn = df_regioes[df_regioes["regiao"].isin(regioes_conn)].sort_values(
            "tamanho", ascending=False
        )
        fig_conn = px.bar(
            df_conn, x="regiao", y="tamanho", color="regiao", text="tamanho",
            title="Comparação de Conexões (Tamanho da Rede) por Região",
            labels={"regiao": "Região", "tamanho": "Número de Conexões"},
            color_discrete_sequence=PALETA_GRAFICOS,
        )
        fig_conn.update_traces(textposition="outside")
        fig_conn.update_layout(showlegend=False)
        st.plotly_chart(fig_conn, use_container_width=True)

    with col2:
        st.subheader("Densidade de Conexões por Região")
        regioes_den = st.multiselect(
            "Regiões a exibir", options=df_regioes["regiao"].tolist(),
            default=df_regioes["regiao"].tolist(), key="den_regioes",
        )
        df_den = df_regioes[df_regioes["regiao"].isin(regioes_den)].sort_values(
            "densidade", ascending=False
        )
        fig_den = px.bar(
            df_den, x="regiao", y="densidade", color="regiao",
            text=df_den["densidade"].map("{:.4f}".format),
            title="Comparação de Densidade de Conexões por Região",
            labels={"regiao": "Região", "densidade": "Densidade"},
            color_discrete_sequence=PALETA_GRAFICOS,
        )
        fig_den.update_traces(textposition="outside")
        fig_den.update_layout(showlegend=False, xaxis_tickangle=-30)
        st.plotly_chart(fig_den, use_container_width=True)

    st.divider()

    st.subheader("Mapa de Calor das Distâncias entre Aeroportos")
    origens_disp  = sorted(df_distancias["origem"].unique())
    destinos_disp = sorted(df_distancias["destino"].unique())

    col_hm1, col_hm2 = st.columns(2)
    with col_hm1:
        origens_sel  = st.multiselect("Origens",  origens_disp,  default=origens_disp,  key="hm_origens")
    with col_hm2:
        destinos_sel = st.multiselect("Destinos", destinos_disp, default=destinos_disp, key="hm_destinos")

    df_hm = df_distancias[
        df_distancias["origem"].isin(origens_sel) &
        df_distancias["destino"].isin(destinos_sel)
    ]
    if not df_hm.empty:
        matriz = df_hm.pivot(index="origem", columns="destino", values="custo")
        fig_hm = px.imshow(
            matriz, color_continuous_scale=ESCALA_CONTINUA,
            title="Mapa de Calor das Distâncias Mínimas entre Aeroportos",
            labels={"color": "Custo do menor caminho", "x": "Destino", "y": "Origem"},
            text_auto=True,
        )
        st.plotly_chart(fig_hm, use_container_width=True)
    else:
        st.warning("Nenhuma rota encontrada para a seleção atual.")

    st.divider()

    st.subheader("Ranking de Rotas por Custo do Menor Caminho")
    aeroportos_rot = sorted(
        set(df_distancias["origem"].unique()) | set(df_distancias["destino"].unique())
    )
    aeroportos_sel = st.multiselect(
        "Filtrar por aeroporto (origem ou destino)", options=aeroportos_rot,
        default=[], key="rot_aeroportos", placeholder="Todos os aeroportos",
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
    df_rot["rota"] = df_rot["origem"] + " -> " + df_rot["destino"]
    df_sorted = df_rot.sort_values("custo")
    ranking = pd.concat([df_sorted.head(n_menores), df_sorted.tail(n_maiores)]).drop_duplicates()

    fig_rot = px.bar(
        ranking, y="rota", x="custo", orientation="h", color="custo",
        color_continuous_scale=ESCALA_CONTINUA, hover_data=["caminho"],
        title="Rotas com Menor e Maior Custo no Menor Caminho",
        labels={"rota": "Rota", "custo": "Custo do Menor Caminho"},
    )
    fig_rot.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig_rot, use_container_width=True)


def pagina_avd(df_grau, df_regioes, df_ego, df_adj):
    PALETA = ["#264653", "#2A9D8F", "#E9C46A", "#F4A261", "#E76F51"]

    st.title("Análise Exploratória e Explanatória (AVD)")
    st.subheader("Exploratória — Grau vs Densidade da Ego-rede")
    st.caption(
        "Cada ponto é um aeroporto. Hubs com alto grau tendem a ter menor densidade local "
        "porque seus vizinhos não se conectam entre si."
    )

    df_scatter = df_ego.merge(
        df_grau[['aeroporto', 'regiao', 'cidade']],
        on='aeroporto', how='left',
    )

    regioes_disp = sorted(df_scatter['regiao'].dropna().unique())
    regioes_sel = st.multiselect(
        "Filtrar regiões", options=regioes_disp, default=regioes_disp, key="avd_scatter_reg"
    )
    df_s = df_scatter[df_scatter['regiao'].isin(regioes_sel)].copy()

    rank_no_grupo = df_s.groupby(['grau', 'densidade_ego']).cumcount()
    tamanho_grupo = df_s.groupby(['grau', 'densidade_ego'])['grau'].transform('count')
    df_s['grau_j'] = df_s['grau'].astype(float) + (rank_no_grupo - (tamanho_grupo - 1) / 2) * 0.35

    posicoes = ['top center', 'bottom center'] * (len(df_s) // 2 + 1)
    df_s = df_s.reset_index(drop=True)

    fig_scatter = px.scatter(
        df_s, x='grau_j', y='densidade_ego', color='regiao',
        text='aeroporto', hover_data={'cidade': True, 'regiao': False, 'aeroporto': False, 'grau_j': False},
        custom_data=['grau'],
        title='Relação entre Grau e Densidade da Ego-rede por Aeroporto',
        labels={'grau_j': 'Grau (conexões)', 'densidade_ego': 'Densidade da Ego-rede', 'regiao': 'Região'},
        color_discrete_sequence=PALETA,
    )
    fig_scatter.update_traces(
        marker=dict(size=9, line=dict(width=1, color='black')),
        textfont=dict(size=8),
    )
    for i, trace in enumerate(fig_scatter.data):
        trace.textposition = posicoes[i % 2]

    fig_scatter.update_layout(
        legend_title='Região',
        height=650,
        xaxis=dict(title='Grau (conexões)', tickmode='linear', dtick=1),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.divider()

    st.subheader("Exploratória — Composição das Conexões por Aeroporto (Regional vs Hub)")
    st.caption(
        "Cada barra mostra o grau total de um aeroporto dividido em dois tipos: "
        "**regional** = conexões com aeroportos da mesma região geográfica; "
        "**hub** = conexões com aeroportos de outras regiões. "
        "Aeroportos com barra predominantemente laranja são conectores inter-regionais."
    )

    df_orig = df_adj[['origem', 'tipo_conexao']].rename(columns={'origem': 'aeroporto'})
    df_dest = df_adj[['destino', 'tipo_conexao']].rename(columns={'destino': 'aeroporto'})
    df_tipo = pd.concat([df_orig, df_dest])
    contagem = df_tipo.groupby(['aeroporto', 'tipo_conexao']).size().reset_index(name='qtd')
    totais = contagem.groupby('aeroporto')['qtd'].sum().reset_index(name='total')
    contagem = contagem.merge(totais, on='aeroporto').sort_values('total', ascending=False)

    aeroportos_disp = contagem['aeroporto'].unique().tolist()
    top_n = st.slider("Exibir top N aeroportos", 5, len(aeroportos_disp), len(aeroportos_disp), key="avd_topn")
    top_aeroportos = totais.sort_values('total', ascending=False).head(top_n)['aeroporto'].tolist()
    df_tipo_filtrado = contagem[contagem['aeroporto'].isin(top_aeroportos)]

    fig_stack = px.bar(
        df_tipo_filtrado, x='aeroporto', y='qtd', color='tipo_conexao',
        barmode='stack',
        title='Composição das Conexões por Aeroporto: Regional vs Hub',
        labels={'aeroporto': 'Aeroporto (IATA)', 'qtd': 'Número de Conexões', 'tipo_conexao': 'Tipo'},
        color_discrete_map={'hub': '#E76F51', 'regional': '#2A9D8F'},
        category_orders={'aeroporto': top_aeroportos},
    )
    fig_stack.update_layout(xaxis_tickangle=-45, legend_title='Tipo de Conexão')
    st.plotly_chart(fig_stack, use_container_width=True)

    st.divider()

    st.subheader("Explanatória - Integração entre regiões no grafo não direcionado")
    st.caption(
        "Como as rotas do dataset representam um grafo nao direcionado, a matriz abaixo conta cada "
        "conexao uma unica vez por par de regioes. Por isso, a leitura correta e simetrica: Nordeste-Sudeste "
        "e Sudeste-Nordeste representam o mesmo tipo de relacao."
    )

    df_fluxo = preparar_fluxo_regional_nao_direcionado(df_adj, df_grau)
    matriz_regioes = montar_matriz_regioes(df_fluxo)

    fig_heatmap_regioes = px.imshow(
        matriz_regioes,
        text_auto=True,
        color_continuous_scale=ESCALA_CONTINUA,
        title='Heatmap Simétrico de Conexões entre Regiões',
        labels={'x': 'Região', 'y': 'Região', 'color': 'Conexões'},
    )
    fig_heatmap_regioes.update_layout(height=560)
    st.plotly_chart(fig_heatmap_regioes, use_container_width=True)


    st.divider()

    st.subheader("Explanatória - Peso das rotas por tipo de conexão")
    st.caption(
        "Está análise usa o peso das arestas do grafo. O objetivo e explicar se conexões do tipo hub "
        "tendem a ter custo maior que conexões regionais, o que ajuda a entender o papel dos hubs na malha."
    )

    df_pesos = preparar_pesos_conexoes(df_adj)

    fig_pesos = px.box(
        df_pesos,
        x='tipo_conexao',
        y='peso',
        color='tipo_conexao',
        points='all',
        title='Distribuição dos Pesos das Arestas por Tipo de Conexão',
        labels={
            'tipo_conexao': 'Tipo de conexão',
            'peso': 'Peso da aresta',
        },
        color_discrete_map={'hub': '#E76F51', 'regional': '#2A9D8F'},
    )
    fig_pesos.update_layout(height=560, showlegend=False)
    st.plotly_chart(fig_pesos, use_container_width=True)

    



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


def pagina_mapa(pasta_projeto: Path):
    st.title("Mapa Interativo de Aeroportos")
    st.caption(
        "Clique em um aeroporto para ver suas conexões destacadas. "
        "A busca por IATA ou cidade também destaca as rotas do aeroporto encontrado."
    )

    html_path = pasta_projeto / "out" / "mapa_interativo.html"

    if not html_path.exists():
        import mapa_interativo
        with st.spinner("Gerando mapa interativo."):
            mapa_interativo.gerar_mapa(pasta_projeto)

    components.html(html_path.read_text(encoding="utf-8"), height=720, scrolling=False)


def main():
    st.set_page_config(page_title="Dashboard - Projeto Grafos", layout="wide")

    pasta_src     = Path(__file__).resolve().parent
    pasta_projeto = pasta_src.parent
    pasta_out     = pasta_projeto / "out"

    st.sidebar.title("Navegação")
    st.sidebar.markdown("Selecione a página que deseja visualizar:")
    pagina = st.sidebar.radio(
        "Ir para:",
        [
            "1. Análise de Graus e Regiões",
            "2. Árvores de Percurso (Menor Caminho)",
            "3. Mapa Interativo de Aeroportos",
            "4. Análise Exploratória e Explanatória (AVD)",
        ],
    )

    df_grau, df_regioes, df_distancias, df_ego, df_adj = carregar_dados(pasta_projeto)

    if pagina == "1. Análise de Graus e Regiões":
        pagina_analise(df_grau, df_regioes, df_distancias)
    elif pagina == "2. Árvores de Percurso (Menor Caminho)":
        pagina_arvores(pasta_out)
    elif pagina == "3. Mapa Interativo de Aeroportos":
        pagina_mapa(pasta_projeto)
    else:
        pagina_avd(df_grau, df_regioes, df_ego, df_adj)


if __name__ == "__main__":
    main()
