import csv
from .graph import Grafo

def ler_grafo_csv(vertice, aresta, numero_vertice=28):
    grafo = Grafo(numero_vertice)

    with open(vertice, 'r', encoding='utf-8') as arquivo_v:
        texto = csv.reader(arquivo_v)
        next(texto) 
        indice_atual = 0 
        for linha in texto:
            iata = linha[0].strip()
            grafo.adicionar_vertice(indice_atual, iata)
            indice_atual += 1

    with open(aresta, 'r', encoding='utf-8') as arquivo_a:
        texto = csv.reader(arquivo_a)
        next(texto)  
        
        for linha in texto:
            origem = linha[0].strip()
            destino = linha[1].strip()
            peso = float(linha[4].strip())
            
            origem_numero = grafo.mapa_indice[origem]
            destino_numero = grafo.mapa_indice[destino]
            
            grafo.adicionar_aresta(origem_numero, destino_numero, peso)

    return grafo


def ler_grafo_wikipedia(caminho_paginas, caminho_links):
    numero_vertices = _contar_linhas_csv(caminho_paginas)
    grafo = Grafo(numero_vertices)

    with open(caminho_paginas, 'r', encoding='utf-8') as f:
        leitor = csv.DictReader(f)
        for indice, linha in enumerate(leitor):
            nome = linha['title'].strip()
            grafo.adicionar_vertice(indice, nome)

    with open(caminho_links, 'r', encoding='utf-8') as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            origem = linha['origem'].strip()
            destino = linha['destino'].strip()
            peso = float(linha['peso'].strip()) if linha.get('peso', '').strip() else 1.0

            if origem in grafo.mapa_indice and destino in grafo.mapa_indice:
                origem_num = grafo.mapa_indice[origem]
                destino_num = grafo.mapa_indice[destino]
                grafo.adicionar_aresta(origem_num, destino_num, peso)

    return grafo

def _contar_linhas_csv(caminho_arquivo):
    """Conta o número de linhas de dados (excluindo o cabeçalho) em um arquivo CSV."""
    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        leitor = csv.reader(f)
        next(leitor, None)
        return sum(1 for _ in leitor)
