import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from graphs.algorithms import dfs
from graphs.graph import Grafo


def test_dfs_sem_ciclo():
    """Caminho A-B-C-D não tem ciclo."""
    g = Grafo(4)
    g.adicionar_vertice(0, 'A')
    g.adicionar_vertice(1, 'B')
    g.adicionar_vertice(2, 'C')
    g.adicionar_vertice(3, 'D')
    g.adicionar_aresta(0, 1, 1)
    g.adicionar_aresta(1, 2, 1)
    g.adicionar_aresta(2, 3, 1)

    _, _, tem_ciclo, _, _ = dfs(g, 'A')
    assert tem_ciclo == False


def test_dfs_detecta_ciclo():
    """Triângulo A-B-C-A tem ciclo."""
    g = Grafo(3)
    g.adicionar_vertice(0, 'A')
    g.adicionar_vertice(1, 'B')
    g.adicionar_vertice(2, 'C')
    g.adicionar_aresta(0, 1, 1)
    g.adicionar_aresta(1, 2, 1)
    g.adicionar_aresta(2, 0, 1)

    _, _, tem_ciclo, _, _ = dfs(g, 'A')
    assert tem_ciclo == True


def test_dfs_classificacao_arestas_com_ciclo():
    """
    Triângulo A-B-C-A:
    - 2 arestas de árvore (n-1)
    - 1 aresta de retorno (fecha o ciclo)
    """
    g = Grafo(3)
    g.adicionar_vertice(0, 'A')
    g.adicionar_vertice(1, 'B')
    g.adicionar_vertice(2, 'C')
    g.adicionar_aresta(0, 1, 1)
    g.adicionar_aresta(1, 2, 1)
    g.adicionar_aresta(2, 0, 1)

    _, _, _, arestas_arvore, arestas_retorno = dfs(g, 'A')
    assert len(arestas_arvore) == 2
    assert len(arestas_retorno) == 1


def test_dfs_arestas_arvore_formam_n_menos_1_arestas():
    """Grafo com n vértices deve ter n-1 arestas de árvore."""
    g = Grafo(4)
    g.adicionar_vertice(0, 'A')
    g.adicionar_vertice(1, 'B')
    g.adicionar_vertice(2, 'C')
    g.adicionar_vertice(3, 'D')
    g.adicionar_aresta(0, 1, 1)
    g.adicionar_aresta(1, 2, 1)
    g.adicionar_aresta(2, 3, 1)

    _, _, _, arestas_arvore, _ = dfs(g, 'A')
    assert len(arestas_arvore) == 3  # n-1 = 4-1


def test_dfs_sem_arestas_retorno_em_grafo_aciclico():
    """Grafo sem ciclo não deve ter nenhuma aresta de retorno."""
    g = Grafo(4)
    g.adicionar_vertice(0, 'A')
    g.adicionar_vertice(1, 'B')
    g.adicionar_vertice(2, 'C')
    g.adicionar_vertice(3, 'D')
    g.adicionar_aresta(0, 1, 1)
    g.adicionar_aresta(1, 2, 1)
    g.adicionar_aresta(2, 3, 1)

    _, _, _, _, arestas_retorno = dfs(g, 'A')
    assert len(arestas_retorno) == 0
