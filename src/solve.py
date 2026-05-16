import csv
import os

from graphs.io import ler_grafo_csv
from graphs.algorithms import dijkstra

def distancias_rotas(grafo, caminho_entrada, caminho_saida):
    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)

    with open(caminho_entrada, mode='r', encoding='utf-8') as f_in, \
         open(caminho_saida, mode='w', encoding='utf-8', newline='') as f_out:
        
        leitor = csv.reader(f_in)
        escritor = csv.writer(f_out)
        
        next(leitor, None) 
        escritor.writerow(['origem', 'destino', 'custo', 'caminho'])
        
        for linha in leitor:
            if len(linha) >= 2:
                origem = linha[0].strip()
                destino = linha[1].strip()
                
                try:
                    custo, caminho = dijkstra(grafo, origem, destino)
                    escritor.writerow([origem, destino, custo, caminho])
                    print(f"{origem} -> {destino} processado")
                except Exception as e:
                    print(f"erro na rota {origem} -> {destino} falhou: {e}")

def main():
    
    caminho_vertices = 'data/aeroportos_data.csv'
    caminho_arestas = 'data/adjacencias_aeroportos.csv'
    caminho_rotas = 'data/rotas.csv'
    saida_distancias = 'out/distancias_rotas.csv'

    try:
        grafo = ler_grafo_csv(caminho_vertices, caminho_arestas)
        
    except Exception as e:
        print(f"Erro ao carregar o grafo: {e}")
        return

    distancias_rotas(grafo, caminho_rotas, saida_distancias)
if __name__ == "__main__":
    main()