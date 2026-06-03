import sys, time
from pathlib import Path
from typing import Optional

import pandas as pd
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parent))
from graphs.graph import Grafo
from graphs.algorithms import dijkstra, bellman_ford, bfs, dfs

CSV_LINKS = Path("data/dataset_parte2/links_reduzido.csv")

app = FastAPI(title="Grafo Wikipedia — API de Algoritmos")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     
    allow_methods=["*"],
    allow_headers=["*"],
)

def carregar_grafo():
    print("Carregando grafo...", flush=True)
    df = pd.read_csv(CSV_LINKS)

    nos = sorted(set(df["origem"]) | set(df["destino"]))
    grafo = Grafo(len(nos))
    for i, nome in enumerate(nos):
        grafo.adicionar_vertice(i, nome)

    for _, row in df.iterrows():
        oi = grafo.mapa_indice.get(row["origem"])
        di = grafo.mapa_indice.get(row["destino"])
        if oi is not None and di is not None:
            peso = float(row["peso"]) + 1  
            grafo.adicionar_aresta(oi, di, peso)

    print(f"  {len(nos):,} vértices carregados.")
    return grafo, nos

GRAFO, NOS = carregar_grafo()
NOS_SET = set(NOS)


def detectar_ciclos_negativos():
    ciclos = []
    vistos = set()
    for u in range(GRAFO.numero_vertices):
        for v, peso_uv in GRAFO.lista_adjacencia[u]:
            par = tuple(sorted((u, v)))
            if par in vistos or u == v:
                continue
            # Procura aresta de volta v → u
            peso_vu = next((p for w, p in GRAFO.lista_adjacencia[v] if w == u), None)
            if peso_vu is None:
                continue
            soma = peso_uv + peso_vu
            if soma < 0:
                ciclos.append({
                    "a": GRAFO.nome_vertice[u],
                    "b": GRAFO.nome_vertice[v],
                    "peso_ab": round(peso_uv, 1),
                    "peso_ba": round(peso_vu, 1),
                    "soma":    round(soma, 1),
                })
            vistos.add(par)
    return ciclos


CICLOS_NEGATIVOS = detectar_ciclos_negativos()
print(f"  {len(CICLOS_NEGATIVOS)} ciclo(s) negativo(s) detectado(s) no grafo.")

class PedidoAlgoritmo(BaseModel):
    algoritmo: str
    origem:    str
    destino:   Optional[str] = None

def passos_com_peso(caminho_nos):
    passos = []
    for i in range(len(caminho_nos) - 1):
        de   = caminho_nos[i]
        para = caminho_nos[i + 1]
        idx_de   = GRAFO.mapa_indice[de]
        idx_para = GRAFO.mapa_indice[para]
        peso = next(
            (p for v, p in GRAFO.lista_adjacencia[idx_de] if v == idx_para),
            0.0
        )
        passos.append({"de": de, "para": para, "peso": round(peso, 1)})
    return passos

def construir_arvore(veio_de):
    return [
        {"pai": GRAFO.nome_vertice[pai], "filho": GRAFO.nome_vertice[i]}
        for i, pai in enumerate(veio_de) if pai is not None
    ]

@app.get("/nos")
def listar_nos():
    return NOS

@app.get("/info")
def info():
    total_arestas = sum(len(adj) for adj in GRAFO.lista_adjacencia) // 2
    return {
        "vertices": GRAFO.numero_vertices,
        "arestas":  total_arestas,
    }


@app.post("/algoritmo")
def executar(pedido: PedidoAlgoritmo):
    algoritmo = pedido.algoritmo
    origem    = pedido.origem
    destino   = pedido.destino or None

    # Validações
    if origem not in NOS_SET:
        raise HTTPException(400, f'Nó de origem "{origem}" não encontrado.')
    if destino is not None and destino not in NOS_SET:
        raise HTTPException(400, f'Nó de destino "{destino}" não encontrado.')

    inicio = time.perf_counter()

    if algoritmo == "Dijkstra":
        if not destino:
            raise HTTPException(400, "Dijkstra exige um destino.")
        custo, caminho_str = dijkstra(GRAFO, origem, destino)
        tempo = (time.perf_counter() - inicio) * 1000

        if custo == float("inf"):
            return {
                "algoritmo": "Dijkstra", "origem": origem, "destino": destino,
                "tempo_ms": round(tempo, 2),
                "alcancavel": False,
            }

        caminho = caminho_str.split(" -> ")
        return {
            "algoritmo":   "Dijkstra",
            "origem":      origem,
            "destino":     destino,
            "alcancavel":  True,
            "custo_total": round(custo, 2),
            "passos":      passos_com_peso(caminho),
            "tempo_ms":    round(tempo, 2),
        }

    if algoritmo == "Bellman-Ford":
        if not destino:
            raise HTTPException(400, "Bellman-Ford exige um destino.")
        resultado = bellman_ford(GRAFO, origem, destino)
        tempo = (time.perf_counter() - inicio) * 1000

        if resultado is None:
            return {
                "algoritmo":       "Bellman-Ford",
                "origem":          origem,
                "destino":         destino,
                "tempo_ms":        round(tempo, 2),
                "ciclo_negativo":  True,
                "alcancavel":      False,
                "ciclos_no_grafo": CICLOS_NEGATIVOS[:5],
            }

        custo, caminho_str = resultado
        if custo == float("inf"):
            return {
                "algoritmo": "Bellman-Ford", "origem": origem, "destino": destino,
                "tempo_ms": round(tempo, 2),
                "ciclo_negativo": False,
                "alcancavel": False,
            }

        caminho = caminho_str.split(" -> ")
        return {
            "algoritmo":      "Bellman-Ford",
            "origem":         origem,
            "destino":        destino,
            "alcancavel":     True,
            "ciclo_negativo": False,
            "custo_total":    round(custo, 2),
            "passos":         passos_com_peso(caminho),
            "tempo_ms":       round(tempo, 2),
        }

    if algoritmo == "BFS":
        ordem_visita, distancias, veio_de = bfs(GRAFO, origem)
        tempo = (time.perf_counter() - inicio) * 1000

        nivel_por_no = {
            GRAFO.nome_vertice[i]: d
            for i, d in enumerate(distancias)
            if d != float("inf")
        }
        return {
            "algoritmo":       "BFS",
            "origem":          origem,
            "tempo_ms":        round(tempo, 2),
            "total_visitados": len(ordem_visita),
            "total_vertices":  GRAFO.numero_vertices,
            "ordem_visita":    ordem_visita,
            "nivel_por_no":    nivel_por_no,
            "arestas_arvore":  construir_arvore(veio_de),
        }

    if algoritmo == "DFS":
        ordem_visita, veio_de = dfs(GRAFO, origem)
        tempo = (time.perf_counter() - inicio) * 1000

        return {
            "algoritmo":       "DFS",
            "origem":          origem,
            "tempo_ms":        round(tempo, 2),
            "total_visitados": len(ordem_visita),
            "total_vertices":  GRAFO.numero_vertices,
            "ordem_visita":    ordem_visita,
            "arestas_arvore":  construir_arvore(veio_de),
        }

    raise HTTPException(400, f'Algoritmo "{algoritmo}" não reconhecido.')


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
