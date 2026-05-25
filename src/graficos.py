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


def main():
    arquivo_grau = 'out/graus.csv'
    arquivo_regioes = 'out/regioes.json'
    arquivo_saida_distribuicao_graus = 'out/distribuicao_graus.png'
    arquivo_saida_ranking_graus_aeroportos = 'out/ranking_graus_aeroportos.png' 
    arquivo_saida_comparacao_regioes = 'out/comparacao_regioes.png'
    arquivo_saida_densidade_regioes = 'out/densidade_regioes.png'
    distribuicao_graus(arquivo_grau, arquivo_saida_distribuicao_graus)
    graus_por_aeroporto(arquivo_grau, arquivo_saida_ranking_graus_aeroportos)
    comparacao_por_regiao(arquivo_regioes, arquivo_saida_comparacao_regioes)
    comparacao_densidade_por_regiao(arquivo_regioes, arquivo_saida_densidade_regioes)

if __name__ == "__main__":
    main()