def dijkstra(grafo, nome_origem):    
    indice_origem = grafo.mapa_indice[nome_origem]
    distancias = [float('inf')] * grafo.numero_vertices
    distancias[indice_origem] = 0
    visitados = [False] * grafo.numero_vertices

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

        for vizinho in range(grafo.numero_vertices):
            peso = grafo.arestas_peso[vertice_atual][vizinho]            
            if peso != 0 and not visitados[vizinho]:
                nova_distancia = distancias[vertice_atual] + peso
                if nova_distancia < distancias[vizinho]:
                    distancias[vizinho] = nova_distancia

    resultado = {}
    for i in range(grafo.numero_vertices):
        iata = grafo.nome_vertice[i]
        resultado[iata] = distancias[i]

    return resultado