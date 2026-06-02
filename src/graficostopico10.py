import pandas as pd
import matplotlib.pyplot as plt


CORES = ['#264653', '#2A9D8F', '#E9C46A', '#F4A261', '#E76F51']


def scatter_grau_ego(arquivo_ego, arquivo_aeroportos, arquivo_saida):
    df_ego = pd.read_csv(arquivo_ego)
    df_ego.columns = df_ego.columns.str.strip()

    df_aeroportos = pd.read_csv(arquivo_aeroportos)
    df_aeroportos.columns = df_aeroportos.columns.str.strip()

    df = df_ego.merge(df_aeroportos[['iata', 'regiao']], left_on='aeroporto', right_on='iata', how='left')
    df['aeroporto'] = df['aeroporto'].str.strip()

    rank = df.groupby(['grau', 'densidade_ego']).cumcount()
    tamanho = df.groupby(['grau', 'densidade_ego'])['grau'].transform('count')
    df['grau_j'] = df['grau'].astype(float) + (rank - (tamanho - 1) / 2) * 0.35

    regioes = sorted(df['regiao'].dropna().unique())
    mapa_cores = {r: CORES[i % len(CORES)] for i, r in enumerate(regioes)}
    posicoes_label = ['bottom', 'top']

    fig, ax = plt.subplots(figsize=(13, 8))

    for regiao in regioes:
        subset = df[df['regiao'] == regiao].reset_index(drop=True)
        ax.scatter(
            subset['grau_j'], subset['densidade_ego'],
            color=mapa_cores[regiao], label=regiao,
            s=90, edgecolors='black', linewidth=0.5, zorder=3,
        )
        for i, row in subset.iterrows():
            va = posicoes_label[i % 2]
            dy = 4 if va == 'bottom' else -4
            ax.annotate(
                row['aeroporto'],
                (row['grau_j'], row['densidade_ego']),
                fontsize=6.5, ha='center', va=va,
                xytext=(0, dy), textcoords='offset points',
            )

    ax.set_title('Relação entre Grau e Densidade da Ego-rede por Aeroporto', fontsize=14, pad=15)
    ax.set_xlabel('Grau (número de conexões)', fontsize=12)
    ax.set_ylabel('Densidade da Ego-rede', fontsize=12)
    ax.legend(title='Região', loc='upper right')
    ax.set_xticks(sorted(df['grau'].unique()))
    ax.grid(linestyle='--', alpha=0.5)

    plt.savefig(arquivo_saida, bbox_inches='tight')
    plt.close()


def barras_tipo_conexao(arquivo_adj, arquivo_saida):
    df_adj = pd.read_csv(arquivo_adj)
    df_adj.columns = df_adj.columns.str.strip()
    df_adj['origem'] = df_adj['origem'].str.strip()
    df_adj['destino'] = df_adj['destino'].str.strip()
    df_adj['tipo_conexao'] = df_adj['tipo_conexao'].str.strip()

    df_origem = df_adj[['origem', 'tipo_conexao']].rename(columns={'origem': 'aeroporto'})
    df_destino = df_adj[['destino', 'tipo_conexao']].rename(columns={'destino': 'aeroporto'})
    df_all = pd.concat([df_origem, df_destino])

    contagem = df_all.groupby(['aeroporto', 'tipo_conexao']).size().unstack(fill_value=0)
    contagem['_total'] = contagem.sum(axis=1)
    contagem = contagem.sort_values('_total', ascending=False).drop(columns='_total')

    cores_tipo = {'hub': '#E76F51', 'regional': '#2A9D8F'}
    cores_plot = [cores_tipo.get(c, '#264653') for c in contagem.columns]

    fig, ax = plt.subplots(figsize=(14, 6))
    contagem.plot(kind='bar', stacked=True, ax=ax, color=cores_plot, edgecolor='black', width=0.7)

    ax.set_title('Composição das Conexões por Aeroporto: Regional vs Hub', fontsize=14, pad=15)
    ax.set_xlabel('Aeroporto (IATA)', fontsize=12)
    ax.set_ylabel('Número de Conexões', fontsize=12)
    ax.legend(title='Tipo de Conexão', loc='upper right')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.xticks(rotation=45, ha='right')

    plt.savefig(arquivo_saida, bbox_inches='tight')
    plt.close()


def main():
    scatter_grau_ego(
        'out/ego_aeroportos.csv',
        'data/aeroportos_data.csv',
        'out/scatter_grau_ego.png',
    )
    barras_tipo_conexao(
        'data/adjacencias_aeroportos.csv',
        'out/barras_tipo_conexao.png',
    )


if __name__ == '__main__':
    main()
