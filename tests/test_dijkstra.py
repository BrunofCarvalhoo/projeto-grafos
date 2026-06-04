import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from graphs.algorithms import dijkstra
from graphs.graph import Grafo


def grafo_base():
   
    g = Grafo(5)
    g.adicionar_vertice(0, 'A')
    g.adicionar_vertice(1, 'B')
    g.adicionar_vertice(2, 'C')
    g.adicionar_vertice(3, 'D')
    g.adicionar_vertice(4, 'E')
    g.adicionar_aresta(0, 2, 1)
    g.adicionar_aresta(0, 1, 4)
    g.adicionar_aresta(2, 1, 2)
    g.adicionar_aresta(1, 3, 1)
    g.adicionar_aresta(2, 3, 5)
    g.adicionar_aresta(3, 4, 3)
    return g


def test_custo_e_caminho_para_destino_especifico():
    custo, caminho = dijkstra(grafo_base(), 'A', 'D')
    assert custo == 4
    assert caminho == "A -> C -> B -> D"


def test_custos_para_todos_os_destinos():
    resultado = dijkstra(grafo_base(), 'A')
    assert resultado['A']['custo'] == 0
    assert resultado['C']['custo'] == 1
    assert resultado['B']['custo'] == 3
    assert resultado['D']['custo'] == 4
    assert resultado['E']['custo'] == 7


def test_prefere_caminho_mais_curto_entre_alternativas():
    g = Grafo(3)
    g.adicionar_vertice(0, 'A')
    g.adicionar_vertice(1, 'B')
    g.adicionar_vertice(2, 'C')
    g.adicionar_aresta(0, 2, 10)  
    g.adicionar_aresta(0, 1, 3)   
    g.adicionar_aresta(1, 2, 4)
    custo, caminho = dijkstra(g, 'A', 'C')
    assert custo == 7
    assert caminho == 'A -> B -> C'


def test_rejeita_peso_negativo():
    g = Grafo(3)
    g.adicionar_vertice(0, 'A')
    g.adicionar_vertice(1, 'B')
    g.adicionar_vertice(2, 'C')
    g.adicionar_aresta(0, 1, 2)
    g.adicionar_aresta(1, 2, -1)
    with pytest.raises(ValueError):
        dijkstra(g, 'A', 'C')


def test_peso_zero_e_valido():
    g = Grafo(2)
    g.adicionar_vertice(0, 'A')
    g.adicionar_vertice(1, 'B')
    g.adicionar_aresta(0, 1, 0)
    custo, _ = dijkstra(g, 'A', 'B')
    assert custo == 0
