import pandas as pd
import matplotlib.pyplot as plt
import json
def distribuicao_graus(arquivo_grau, arquivo_saida):
        
    df_grau = pd.read_csv(arquivo_grau)
    plt.figure(figsize=(10, 6))
    faixas = [0, 5, 10, 15, 20, 25, 30]
    df_grau['grau'].hist(bins=faixas, edgecolor='black', color='#4682B4')
    plt.title('Distribuição dos Graus dos Aeroportos', fontsize=14, pad=15)
    plt.xlabel('Graus', fontsize=12)
    plt.ylabel('Quantidade de Aeroportos', fontsize=12)
    plt.xticks(faixas)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.grid(axis='x', visible=False) 
    plt.savefig(arquivo_saida, bbox_inches='tight')
    plt.close()
    
def graus_por_aeroporto(arquivo_grau, arquivo_saida):
    df_grau = pd.read_csv(arquivo_grau)
    df_grau_por_aeroporto = df_grau.sort_values(by='grau', ascending=False)
    plt.figure(figsize=(14, 6))
    plt.bar(df_grau_por_aeroporto['aeroporto'], df_grau_por_aeroporto['grau'], 
            color='#55A868', edgecolor='black') 
    
    plt.title('Ranking de grau por Aeroporto', fontsize=14, pad=15)
    plt.xlabel('Aeroportos (IATA)', fontsize=12)
    plt.ylabel('Quantidade de Graus', fontsize=12)
    
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig(arquivo_saida, bbox_inches='tight')
    plt.close()
    
def comparacao_por_regiao(arquivo_regioes, arquivo_saida):
    with open(arquivo_regioes, 'r', encoding='utf-8') as f:
        dados = json.load(f)
       
    df_regioes = pd.DataFrame.from_dict(dados, orient='index').reset_index()
    df_regioes.rename(columns={'index': 'regiao'}, inplace=True)
    
    df_regioes['tamanho'] = df_regioes['tamanho'].astype(int)
    df_regioes['regiao'] = df_regioes['regiao'].str.title()
    df_regioes = df_regioes.sort_values(by='tamanho', ascending=False)
    
    plt.figure(figsize=(10, 6))
    plt.bar(df_regioes['regiao'], df_regioes['tamanho'], 
            color='#E24A33', edgecolor='black', label='Quantidade de Conexões (Tamanho)') 
    
    plt.title('Comparação de Conexões (Tamanho da Rede) por Região', fontsize=14, pad=15)
    plt.xlabel('Regiões', fontsize=12)
    plt.ylabel('Número de Conexões', fontsize=12)
    
    plt.legend(loc='upper right')
    plt.xticks(rotation=0) 
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.savefig(arquivo_saida, bbox_inches='tight')
    plt.close()

def comparacao_densidade_por_regiao(arquivo_regioes, arquivo_saida):
    with open(arquivo_regioes, 'r', encoding='utf-8') as f:
        dados = json.load(f)
    df_regioes = pd.DataFrame.from_dict(dados, orient='index').reset_index()
    df_regioes.rename(columns={'index': 'regiao'}, inplace=True)
    df_regioes['densidade'] = df_regioes['densidade'].str.replace(',', '.').astype(float)
    
    df_regioes['regiao'] = df_regioes['regiao'].str.title()
    df_regioes = df_regioes.sort_values(by='densidade', ascending=False)
    
    plt.figure(figsize=(10, 6))
    plt.bar(df_regioes['regiao'], df_regioes['densidade'], 
            color="#33E245", edgecolor='black', label='Densidade de Conexões') 
    
    plt.title('Comparação de Densidade de Conexões por Região', fontsize=14, pad=15)
    plt.xlabel('Regiões', fontsize=12)
    plt.ylabel('Densidade de Conexões', fontsize=12)
    
    plt.legend(loc='upper right')
    plt.xticks(rotation=45, ha='right') 
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    plt.savefig(arquivo_saida, bbox_inches='tight')
    plt.close()

def mapa_calor_distancias(arquivo_distancias, arquivo_saida):
    df = pd.read_csv(arquivo_distancias)

    matriz = df.pivot(index='origem', columns='destino', values='custo')

    plt.figure(figsize=(10, 7))
    plt.imshow(matriz, cmap='YlOrRd', aspect='auto')

    plt.colorbar(label='Custo do menor caminho')
    plt.title('Mapa de Calor das Distâncias Mínimas entre Aeroportos', fontsize=14, pad=15)
    plt.xlabel('Destino', fontsize=12)
    plt.ylabel('Origem', fontsize=12)

    plt.xticks(range(len(matriz.columns)), matriz.columns, rotation=45)
    plt.yticks(range(len(matriz.index)), matriz.index)

    plt.savefig(arquivo_saida, bbox_inches='tight')
    plt.close()

def ranking_rotas_por_distancia(arquivo_distancias, arquivo_saida):
    df = pd.read_csv(arquivo_distancias)

    df['rota'] = df['origem'] + ' -> ' + df['destino']
    df = df.sort_values(by='custo', ascending=True)

    menores = df.head(5)
    maiores = df.tail(5).sort_values(by='custo', ascending=True)
    ranking = pd.concat([menores, maiores])

    normalizador = plt.Normalize(ranking['custo'].min(), ranking['custo'].max())
    cores = plt.cm.Blues(normalizador(ranking['custo']))

    fig, ax = plt.subplots(figsize=(12, 7))
    ax.barh(ranking['rota'], ranking['custo'], color=cores, edgecolor='black')

    barra_cores = plt.cm.ScalarMappable(cmap='Blues', norm=normalizador)
    barra_cores.set_array([])
    fig.colorbar(barra_cores, ax=ax, label='Custo do menor caminho')

    ax.set_title('Rotas com Menor e Maior Custo no Menor Caminho', fontsize=14, pad=15)
    ax.set_xlabel('Custo do Menor Caminho', fontsize=12)
    ax.set_ylabel('Rotas', fontsize=12)
    ax.grid(axis='x', linestyle='--', alpha=0.7)

    plt.savefig(arquivo_saida, bbox_inches='tight')
    plt.close()


def participacao_aeroportos_menores_caminhos(arquivo_distancias, arquivo_saida):
    df_distancias = pd.read_csv(arquivo_distancias)

    registros = []
    for row in df_distancias.dropna(subset=['caminho']).itertuples():
        aeroportos = [aeroporto.strip() for aeroporto in str(row.caminho).split('->')]
        total_aeroportos = len(aeroportos)

        for posicao, aeroporto in enumerate(aeroportos):
            if posicao == 0:
                papel = 'Origem'
            elif posicao == total_aeroportos - 1:
                papel = 'Destino'
            else:
                papel = 'Intermediario'

            registros.append({'aeroporto': aeroporto, 'papel': papel})

    if not registros:
        return

    df_participacao = pd.DataFrame(registros)
    contagem = (
        df_participacao
        .groupby(['aeroporto', 'papel'])
        .size()
        .unstack(fill_value=0)
    )

    for coluna in ['Origem', 'Intermediario', 'Destino']:
        if coluna not in contagem.columns:
            contagem[coluna] = 0

    contagem['total'] = contagem[['Origem', 'Intermediario', 'Destino']].sum(axis=1)
    contagem = contagem.sort_values('total', ascending=False).head(10)
    dados_plot = contagem[['Origem', 'Intermediario', 'Destino']]

    cores = {
        'Origem': '#264653',
        'Intermediario': '#E76F51',
        'Destino': '#2A9D8F',
    }

    fig, ax = plt.subplots(figsize=(12, 7))
    dados_plot.plot(
        kind='bar',
        stacked=True,
        ax=ax,
        color=[cores[coluna] for coluna in dados_plot.columns],
        edgecolor='black',
        width=0.75,
    )

    ax.set_title('Participacao dos Aeroportos nos Menores Caminhos', fontsize=14, pad=15)
    ax.set_xlabel('Aeroporto (IATA)', fontsize=12)
    ax.set_ylabel('Frequencia nos menores caminhos', fontsize=12)
    ax.legend(title='Papel no caminho', loc='upper right')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(rotation=45, ha='right')

    plt.savefig(arquivo_saida, bbox_inches='tight')
    plt.close()

def main():
    arquivo_grau = 'out/graus.csv'
    arquivo_regioes = 'out/regioes.json'
    arquivo_distancias = 'out/distancias_rotas.csv'
    arquivo_saida_distribuicao_graus = 'out/distribuicao_graus.png'
    arquivo_saida_ranking_graus_aeroportos = 'out/ranking_graus_aeroportos.png' 
    arquivo_saida_comparacao_regioes = 'out/comparacao_regioes.png'
    arquivo_saida_densidade_regioes = 'out/densidade_regioes.png'
    arquivo_saida_mapa_calor_distancias = 'out/mapa_calor_distancias.png'
    arquivo_saida_ranking_rotas_distancia = 'out/ranking_rotas_distancia.png'
    arquivo_saida_participacao_caminhos = 'out/participacao_aeroportos_menores_caminhos.png'
    
    distribuicao_graus(arquivo_grau, arquivo_saida_distribuicao_graus)
    graus_por_aeroporto(arquivo_grau, arquivo_saida_ranking_graus_aeroportos)
    comparacao_por_regiao(arquivo_regioes, arquivo_saida_comparacao_regioes)
    comparacao_densidade_por_regiao(arquivo_regioes, arquivo_saida_densidade_regioes)
    mapa_calor_distancias(arquivo_distancias, arquivo_saida_mapa_calor_distancias)
    ranking_rotas_por_distancia(arquivo_distancias, arquivo_saida_ranking_rotas_distancia)
    participacao_aeroportos_menores_caminhos(arquivo_distancias, arquivo_saida_participacao_caminhos)

if __name__ == "__main__":
    main()
