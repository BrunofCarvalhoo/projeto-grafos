import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from graphs.algorithms import bfs
from graphs.graph import Grafo


def grafo_em_camadas():
    """
    Grafo em 3 níveis a partir de A:
        A          - nível 0
       / \\
      B   C        - nível 1
      |   |
      D   E        - nível 2
    """
    g = Grafo(5)
    g.adicionar_vertice(0, 'A')
    g.adicionar_vertice(1, 'B')
    g.adicionar_vertice(2, 'C')
    g.adicionar_vertice(3, 'D')
    g.adicionar_vertice(4, 'E')
    g.adicionar_aresta(0, 1, 1)  
    g.adicionar_aresta(0, 2, 1)  
    g.adicionar_aresta(1, 3, 1)  
    g.adicionar_aresta(2, 4, 1)  
    return g


def test_bfs_origem_tem_nivel_zero():
    _, distancias, _ = bfs(grafo_em_camadas(), 'A')
    assert distancias[0] == 0


def test_bfs_vizinhos_diretos_em_nivel_um():
    _, distancias, _ = bfs(grafo_em_camadas(), 'A')
    assert distancias[1] == 1  
    assert distancias[2] == 1  


def test_bfs_niveis_corretos_em_grafo_pequeno():
    _, distancias, _ = bfs(grafo_em_camadas(), 'A')
    assert distancias[0] == 0  
    assert distancias[1] == 1 
    assert distancias[2] == 1  
    assert distancias[3] == 2  
    assert distancias[4] == 2  


def test_bfs_visita_por_nivel():
    ordem, _, _ = bfs(grafo_em_camadas(), 'A')
    assert ordem[0] == 'A'
    assert set(ordem[1:3]) == {'B', 'C'}   
    assert set(ordem[3:])  == {'D', 'E'}   


def test_bfs_grafo_linear_niveis_sequenciais():
    """Caminho A-B-C-D: cada vértice está um nível mais profundo que o anterior"""
    g = Grafo(4)
    g.adicionar_vertice(0, 'A')
    g.adicionar_vertice(1, 'B')
    g.adicionar_vertice(2, 'C')
    g.adicionar_vertice(3, 'D')
    g.adicionar_aresta(0, 1, 1)
    g.adicionar_aresta(1, 2, 1)
    g.adicionar_aresta(2, 3, 1)

    _, distancias, _ = bfs(g, 'A')
    assert distancias[0] == 0
    assert distancias[1] == 1
    assert distancias[2] == 2
    assert distancias[3] == 3
