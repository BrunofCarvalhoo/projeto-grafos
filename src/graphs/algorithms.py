def dijkstra(grafo, nome_origem, nome_destino=None):
    for v in range(grafo.numero_vertices):
        for _, peso in grafo.lista_adjacencia[v]:
            if peso < 0:
                raise ValueError(
                    f"Dijkstra não suporta pesos negativos. Peso {peso} encontrado."
                )

    indice_origem = grafo.mapa_indice[nome_origem]
    distancias = [float('inf')] * grafo.numero_vertices
    distancias[indice_origem] = 0
    visitados = [False] * grafo.numero_vertices
    veio_de = [None] * grafo.numero_vertices

    for _ in range(grafo.numero_vertices):
        menor_distancia = float('inf')
        vertice_atual = None
        for i in range(grafo.numero_vertices):
            if not visitados[i] and distancias[i] < menor_distancia:
                menor_distancia = distancias[i]
                vertice_atual = i

        if vertice_atual is None:
            break
        
        visitados[vertice_atual] = True

        for vizinho, peso in grafo.lista_adjacencia[vertice_atual]:
            if not visitados[vizinho]:
                nova_distancia = distancias[vertice_atual] + peso
                if nova_distancia < distancias[vizinho]:
                    distancias[vizinho] = nova_distancia
                    veio_de[vizinho] = vertice_atual
                
    def reconstruir_caminho(destino):
        caminho = []
        atual = destino
        while atual is not None:
            caminho.append(grafo.nome_vertice[atual])
            atual = veio_de[atual]
        caminho.reverse()
        return caminho

    if nome_destino:
        indice_destino = grafo.mapa_indice[nome_destino]
        custo = distancias[indice_destino]
        caminho_str = " -> ".join(reconstruir_caminho(indice_destino))
        return custo, caminho_str
    
    else:
        resultado = {}
        for i in range(grafo.numero_vertices):
            iata = grafo.nome_vertice[i]
            resultado[iata] = {
                "custo": distancias[i],
                "caminho": " -> ".join(reconstruir_caminho(i))
            }
        return resultado
    
def bellman_ford(grafo, nome_origem, nome_destino=None):
    indice_origem = grafo.mapa_indice[nome_origem]
    distancias = [float('inf')] * grafo.numero_vertices
    distancias[indice_origem] = 0
    veio_de = [None] * grafo.numero_vertices

    #lista das arestas do grafo
    arestas = []
    for vertice in range(grafo.numero_vertices):
        for vizinho, peso in grafo.lista_adjacencia[vertice]:
            arestas.append((vertice, vizinho, peso))

    #relaxamento
    for _ in range(grafo.numero_vertices - 1):
        for origem_aresta, destino_aresta, peso in arestas:
            nova_distancia = distancias[origem_aresta] + peso
            if nova_distancia < distancias[destino_aresta]:
                distancias[destino_aresta] = nova_distancia
                veio_de[destino_aresta] = origem_aresta

    for origem_aresta, destino_aresta, peso in arestas:
        if distancias[origem_aresta] + peso < distancias[destino_aresta]:
            return None  #ciclo negativo detectado
    #depois tem que simular essa parte de ciclo negativo aq
    

    def reconstruir_caminho(destino):
        caminho = []
        atual = destino
        while atual is not None:
            caminho.append(grafo.nome_vertice[atual])
            atual = veio_de[atual]
        caminho.reverse()
        return caminho

    if nome_destino:
        indice_destino = grafo.mapa_indice[nome_destino]
        custo = distancias[indice_destino]
        caminho_str = " -> ".join(reconstruir_caminho(indice_destino))
        return custo, caminho_str

    else:
        resultado = {}
        for i in range(grafo.numero_vertices):
            vertice = grafo.nome_vertice[i]
            resultado[vertice] = {
                "custo": distancias[i],
                "caminho": " -> ".join(reconstruir_caminho(i))
            }
        return resultado


from collections import deque

def bfs(grafo, nome_origem):
    indice_origem = grafo.mapa_indice[nome_origem]

    distancias = [float('inf')] * grafo.numero_vertices
    visitados = [False] * grafo.numero_vertices
    veio_de = [None] * grafo.numero_vertices
    ordem_visita = []

    fila = deque([indice_origem])
    visitados[indice_origem] = True
    distancias[indice_origem] = 0

    while fila:
        vertice_atual = fila.popleft()
        ordem_visita.append(grafo.nome_vertice[vertice_atual])

        for vizinho, _ in grafo.lista_adjacencia[vertice_atual]:
            if not visitados[vizinho]:
                visitados[vizinho] = True
                distancias[vizinho] = distancias[vertice_atual] + 1
                veio_de[vizinho] = vertice_atual
                fila.append(vizinho)

    return ordem_visita, distancias, veio_de

def dfs(grafo, nome_origem):
    indice_origem = grafo.mapa_indice[nome_origem]
    visitados = [False] * grafo.numero_vertices
    veio_de = [None] * grafo.numero_vertices
    ordem_visita = []
    tem_ciclo = False
    arestas_arvore = []
    arestas_retorno = []
    visto_retorno = set()

    pilha = [(indice_origem, -1)]

    while pilha:
        vertice_atual, pai = pilha.pop()

        if visitados[vertice_atual]:
            continue

        visitados[vertice_atual] = True
        ordem_visita.append(grafo.nome_vertice[vertice_atual])

        if pai != -1:
            arestas_arvore.append((grafo.nome_vertice[pai], grafo.nome_vertice[vertice_atual]))

        for vizinho, _ in reversed(grafo.lista_adjacencia[vertice_atual]):
            if not visitados[vizinho]:
                if veio_de[vizinho] is None and vizinho != indice_origem:
                    veio_de[vizinho] = vertice_atual
                pilha.append((vizinho, vertice_atual))
            elif vizinho != pai:
                tem_ciclo = True
                chave = (min(vertice_atual, vizinho), max(vertice_atual, vizinho))
                if chave not in visto_retorno:
                    visto_retorno.add(chave)
                    arestas_retorno.append(
                        (grafo.nome_vertice[vertice_atual], grafo.nome_vertice[vizinho])
                    )

    return ordem_visita, veio_de, tem_ciclo, arestas_arvore, arestas_retorno
