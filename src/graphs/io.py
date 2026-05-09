import csv
from graph import Grafo

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