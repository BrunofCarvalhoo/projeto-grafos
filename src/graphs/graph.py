class Grafo:
    def __init__(self, numero_vertices):
        self.lista_adjacencia = [[] for _ in range(numero_vertices)] 
        self.numero_vertices = numero_vertices
        self.nome_vertice = [''] * numero_vertices
        self.mapa_indice = {}
        self.quantidade_atual = 0
    
    def adicionar_vertice(self, indice, nome):
        if 0 <= indice < self.numero_vertices:
            self.nome_vertice[indice] = nome
            self.mapa_indice[nome] = indice
            self.quantidade_atual += 1
            
    def adicionar_aresta(self,origem,destino,peso):
        if 0 <= origem < self.numero_vertices and 0 <= destino < self.numero_vertices:
            self.lista_adjacencia[origem].append((destino, peso))
            self.lista_adjacencia[destino].append((origem, peso))

    def adicionar_aresta_dirigida(self, origem, destino, peso):
        if 0 <= origem < self.numero_vertices and 0 <= destino < self.numero_vertices:
            self.lista_adjacencia[origem].append((destino, peso))
        