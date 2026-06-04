import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from graphs.algorithms import bellman_ford
from graphs.graph import Grafo


def grafo_com_peso_negativo():
    """
    Grafo dirigido com aresta negativa B-C sem criar ciclo negativo.

    A -1- B
    A -4- C
    B -2- C
    C -3- D

    Distâncias de A: A=0, B=1, C=-1, D=2
    """
    g = Grafo(4)
    g.adicionar_vertice(0, 'A')
    g.adicionar_vertice(1, 'B')
    g.adicionar_vertice(2, 'C')
    g.adicionar_vertice(3, 'D')
    g.adicionar_aresta_dirigida(0, 1,  1)
    g.adicionar_aresta_dirigida(0, 2,  4)
    g.adicionar_aresta_dirigida(1, 2, -2)
    g.adicionar_aresta_dirigida(2, 3,  3)
    return g


def test_bellman_ford_custos_corretos_com_peso_negativo():
    resultado = bellman_ford(grafo_com_peso_negativo(), 'A')
    assert resultado['A']['custo'] == 0
    assert resultado['B']['custo'] == 1
    assert resultado['C']['custo'] == -1
    assert resultado['D']['custo'] == 2


def test_bellman_ford_caminho_correto_com_peso_negativo():
    """O caminho ótimo para C passa por B (via aresta negativa)."""
    resultado = bellman_ford(grafo_com_peso_negativo(), 'A')
    assert resultado['C']['caminho'] == 'A -> B -> C'


def test_bellman_ford_destino_especifico_com_peso_negativo():
    custo, caminho = bellman_ford(grafo_com_peso_negativo(), 'A', 'D')
    assert custo == 2
    assert caminho == 'A -> B -> C -> D'


def test_bellman_ford_detecta_ciclo_negativo():
    """
    Ciclo dirigido A-B-C-A com peso total negativo 1-3+1 = -1
    Bellman-Ford deve retornar None como flag
    """
    g = Grafo(3)
    g.adicionar_vertice(0, 'A')
    g.adicionar_vertice(1, 'B')
    g.adicionar_vertice(2, 'C')
    g.adicionar_aresta_dirigida(0, 1,  1)
    g.adicionar_aresta_dirigida(1, 2, -3)
    g.adicionar_aresta_dirigida(2, 0,  1)

    assert bellman_ford(g, 'A') is None


def test_bellman_ford_funciona_com_pesos_positivos():
    """Bellman-Ford também deve funcionar corretamente sem pesos negativos"""
    g = Grafo(3)
    g.adicionar_vertice(0, 'A')
    g.adicionar_vertice(1, 'B')
    g.adicionar_vertice(2, 'C')
    g.adicionar_aresta_dirigida(0, 1, 3)
    g.adicionar_aresta_dirigida(0, 2, 1)
    g.adicionar_aresta_dirigida(2, 1, 1)

    resultado = bellman_ford(g, 'A')
    assert resultado['A']['custo'] == 0
    assert resultado['C']['custo'] == 1
    assert resultado['B']['custo'] == 2   # A-C-B = 1+1, melhor que A-B = 3
