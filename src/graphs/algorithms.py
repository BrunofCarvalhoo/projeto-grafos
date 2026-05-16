def dijkstra(grafo, nome_origem, nome_destino=None):    
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