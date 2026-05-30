import time
import json
import os
from graphs.io import ler_grafo_wikipedia
from graphs.algorithms import bfs, dfs, dijkstra, bellman_ford

def rodar_benchmark():
    caminho_paginas = 'data/dataset_parte2/pages_reduzido.csv'
    caminho_links = 'data/dataset_parte2/links_reduzido.csv'
    
    print("Carregando o grafo da Wikipédia...")
    grafo = ler_grafo_wikipedia(caminho_paginas, caminho_links)
    print(f"Grafo carregado: {grafo.numero_vertices} vértices")
    
    chaves = list(grafo.mapa_indice.keys())
    origem = chaves[0]
    
    destino = None
    for vizinho_idx, _ in grafo.lista_adjacencia[grafo.mapa_indice[origem]]:
        destino = grafo.nome_vertice[vizinho_idx]
        break
        
    if not destino:
        destino = chaves[10] if len(chaves) > 10 else chaves[-1]
    
    print("\nMedindo BFS...")
    t0 = time.perf_counter()
    bfs(grafo, origem)
    t_bfs = (time.perf_counter() - t0) * 1000
    print(f"BFS concluído em {t_bfs:.2f} ms")
    
    print("Medindo DFS...")
    t0 = time.perf_counter()
    dfs(grafo, origem)
    t_dfs = (time.perf_counter() - t0) * 1000
    print(f"DFS concluído em {t_dfs:.2f} ms")
    
    print("Medindo Dijkstra...")
    t0 = time.perf_counter()
    dijkstra(grafo, origem, destino)
    t_dijkstra = (time.perf_counter() - t0) * 1000
    print(f"Dijkstra concluído em {t_dijkstra:.2f} ms")
    
    print("Medindo Bellman-Ford (isso pode levar alguns segundos)...")
    t0 = time.perf_counter()
    bellman_ford(grafo, origem, destino)
    t_bf = (time.perf_counter() - t0) * 1000
    print(f"Bellman-Ford concluído em {t_bf:.2f} ms")
    
    report = {
      "bfs": {
        "tempo_ms": round(t_bfs, 2),
        "complexidade": "O(V + E)"
      },
      "dfs": {
        "tempo_ms": round(t_dfs, 2),
        "complexidade": "O(V + E)"
      },
      "dijkstra": {
        "tempo_ms": round(t_dijkstra, 2),
        "complexidade": "O((V + E) log V)"
      },
      "bellman_ford": {
        "tempo_ms": round(t_bf, 2),
        "complexidade": "O(V * E)"
      }
    }
    
    os.makedirs('out', exist_ok=True)
    
    with open('out/parte2_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    pasta_public = 'src/grafo-wiki/public'
    if os.path.exists(pasta_public):
        with open(os.path.join(pasta_public, 'parte2_report.json'), 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
            
    print("\nSucesso! Arquivos de relatório gerados em:")
    print(" - out/parte2_report.json")
    print(" - src/grafo-wiki/public/parte2_report.json")

if __name__ == "__main__":
    rodar_benchmark()
