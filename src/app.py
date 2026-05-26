import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
from PIL import Image

def main():
    st.set_page_config(page_title="Dashboard - Projeto Grafos", layout="wide")

    pasta_src = Path(__file__).resolve().parent
    pasta_projeto = pasta_src.parent
    pasta_out = pasta_projeto / "out"

    st.sidebar.title("✈️ Navegação")
    st.sidebar.markdown("Selecione a página que deseja visualizar:")
    
    pagina = st.sidebar.radio(
        "Ir para:",
        [
            "1. Análise de Graus e Regiões",
            "2. Árvores de Percurso (Menor Caminho)"
        ]
    )

    if pagina == "1. Análise de Graus e Regiões":
        st.title("📊 Análise de Graus e Regiões")
        st.markdown("Esta página exibe as estatísticas gerais do grafo, métricas de conexões e distribuição regional.")
        
        img_distribuicao = pasta_out / "distribuicao_graus.png"
        img_ranking = pasta_out / "ranking_graus_aeroportos.png"
        img_comparacao = pasta_out / "comparacao_regioes.png"
        img_comparacao_densidade = pasta_out / "densidade_regioes.png"
        img_mapa_calor = pasta_out / "mapa_calor_distancias.png"
        img_ranking_rotas_distancia = pasta_out / "ranking_rotas_distancia.png"
        col1, col2 = st.columns(2)
        
        with col1:
            if img_distribuicao.exists():
                st.image(Image.open(img_distribuicao), caption="Distribuição dos Graus dos Aeroportos", use_container_width=True)
            else:
                st.warning("O arquivo 'distribuicao_graus.png' não foi encontrado na pasta 'out/'.")
                
            if img_comparacao.exists():
                st.image(Image.open(img_comparacao), caption="Comparação de Conexões (Tamanho da Rede) por Região", use_container_width=True)
            else:
                st.warning("O arquivo 'comparacao_regioes.png' não foi encontrado na pasta 'out/'.")
            
            if img_mapa_calor.exists():
                st.image(Image.open(img_mapa_calor), caption="Mapa de Calor das Distâncias entre Aeroportos", use_container_width=True)
            else:
                st.warning("O arquivo 'mapa_calor_distancias.png' não foi encontrado na pasta 'out/'.")

        with col2:
            if img_ranking.exists():
                st.image(Image.open(img_ranking), caption="Ranking de Grau por Aeroporto (IATA)", use_container_width=True)
            else:
                st.warning("O arquivo 'ranking_graus_aeroportos.png' não foi encontrado na pasta 'out/'.")
            if img_comparacao_densidade.exists():
                st.image(Image.open(img_comparacao_densidade), caption="Comparação de Densidade de Conexões por Região", use_container_width=True)
            else:
                st.warning("O arquivo 'densidade_regioes.png' não foi encontrado na pasta 'out/'.")
            if img_ranking_rotas_distancia.exists():
                st.image(Image.open(img_ranking_rotas_distancia), caption="Ranking de Rotas por Custo do Menor Caminho", use_container_width=True)
            else:
                st.warning("O arquivo 'ranking_rotas_distancia.png' não foi encontrado na pasta 'out/'.")


    elif pagina == "2. Árvores de Percurso (Menor Caminho)":
        st.title("🕸️ Árvores de Percurso (Menor Caminho)")
        st.markdown("Visualize de forma interativa os caminhos mais rápidos mapeados pelo algoritmo de Dijkstra.")

        if pasta_out.exists():
            
            html_files = list(pasta_out.glob("arvore_percurso_*.html"))
            
            if html_files:
                
                opcoes_rotas = {
                    f.name.replace('arvore_percurso_', '').replace('.html', '').replace('_', ' '): f 
                    for f in html_files
                }
                
                rotas_ordenadas = sorted(opcoes_rotas.keys())
                
                rota_selecionada = st.selectbox(
                    "Selecione uma das rotas processadas:",
                    options=rotas_ordenadas
                )
                
                if rota_selecionada:
                    arquivo_html = opcoes_rotas[rota_selecionada]
                    with open(arquivo_html, 'r', encoding='utf-8') as f:
                        conteudo_html = f.read()
                    
                    st.markdown(f"**Grafo Interativo da Rota:** `{rota_selecionada}`")
                   
                    components.html(conteudo_html, height=650, scrolling=False)
            else:
                st.info("Nenhum gráfico HTML de percurso foi encontrado na pasta 'out/'. Lembre-se de rodar o comando 'python src/arvore_percurso.py' primeiro.")
        else:
            st.error(f"Erro: A pasta de saída não foi encontrada no caminho esperado: {pasta_out}")

if __name__ == "__main__":
    main()