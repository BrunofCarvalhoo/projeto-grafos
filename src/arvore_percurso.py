
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


COR_ARVORE = "#90EE90"


# O CSV informa o custo total do caminho, mas não informa o custo de cada aresta
# quando o caminho tem escalas, por exemplo: BVB -> BSB -> FLN.
# Para reproduzir os HTMLs anexados, os custos das arestas conhecidas ficam aqui.
DISTANCIAS_ARESTAS: Dict[Tuple[str, str], float] = {
    ("REC", "POA"): 270.0,
    ("MAO", "GRU"): 230.0,
    ("CGH", "GIG"): 60.0,
    ("BVB", "BSB"): 210.0,
    ("BSB", "FLN"): 140.0,
    ("RBR", "BSB"): 205.0,
    ("FOR", "REC"): 80.0,
    ("REC", "JPA"): 45.0,
    ("CWB", "SSA"): 180.0,
    ("MCP", "BSB"): 165.0,
    ("BSB", "VIX"): 80.0,
    ("CGB", "BSB"): 100.0,
    ("BSB", "NAT"): 170.0,
    ("PMW", "CNF"): 115.0,
}


def caminho_para_vertices(caminho: str) -> List[str]:
    """Converte 'A -> B -> C' em ['A', 'B', 'C'].""" 
    return [parte.strip() for parte in caminho.split("->") if parte.strip()]


def pares_consecutivos(vertices: Iterable[str]) -> List[Tuple[str, str]]:
    """Gera pares consecutivos: ['A', 'B', 'C'] -> [('A', 'B'), ('B', 'C')]."""
    lista = list(vertices)
    return list(zip(lista, lista[1:]))


def obter_custo_aresta(origem: str, destino: str, custo_total: float, quantidade_arestas: int) -> float:
    """
    Retorna o custo da aresta.

    Primeiro tenta usar a distância conhecida em DISTANCIAS_ARESTAS.
    Se não existir, usa:
    - custo_total quando o caminho tem só uma aresta;
    - custo_total / quantidade_arestas como fallback para caminhos com escalas.
    """
    if (origem, destino) in DISTANCIAS_ARESTAS:
        return DISTANCIAS_ARESTAS[(origem, destino)]

    if (destino, origem) in DISTANCIAS_ARESTAS:
        return DISTANCIAS_ARESTAS[(destino, origem)]

    if quantidade_arestas <= 1:
        return custo_total

    return custo_total / quantidade_arestas


def criar_nodes(vertices: List[str]) -> List[dict]:
    """Cria os nós no formato usado pelo vis-network."""
    return [
        {
            "color": COR_ARVORE,
            "font": {"color": "black"},
            "id": aeroporto,
            "label": aeroporto,
            "shape": "dot",
            "size": 35,
            "title": f"aeroportoporto {aeroporto}",
        }
        for aeroporto in vertices
    ]


def criar_edges(vertices: List[str], custo_total: float) -> List[dict]:
    """Cria as arestas no formato usado pelo vis-network."""
    pares = pares_consecutivos(vertices)
    quantidade_arestas = len(pares)

    return [
        {
            "color": COR_ARVORE,
            "from": origem,
            "label": f"{obter_custo_aresta(origem, destino, custo_total, quantidade_arestas):.1f}",
            "to": destino,
            "width": 4,
        }
        for origem, destino in pares
    ]


def gerar_html(nodes: List[dict], edges: List[dict]) -> str:
    """Gera o conteúdo HTML do grafo."""
    nodes_json = json.dumps(nodes, ensure_ascii=False, indent=8)
    edges_json = json.dumps(edges, ensure_ascii=False, indent=8)

    return f"""<html>
<head>
  <meta charset="utf-8">

  <script src="lib/bindings/utils.js"></script>

  <link rel="stylesheet"
        href="https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.2/dist/dist/vis-network.min.css"
        crossorigin="anonymous"
        referrerpolicy="no-referrer" />

  <script src="https://cdnjs.cloudflare.com/ajax/libs/vis-network/9.1.2/dist/vis-network.min.js"
          crossorigin="anonymous"
          referrerpolicy="no-referrer"></script>

  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta3/dist/css/bootstrap.min.css"
        rel="stylesheet"
        crossorigin="anonymous" />

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta3/dist/js/bootstrap.bundle.min.js"
          crossorigin="anonymous"></script>

  <style type="text/css">
    #mynetwork {{
      width: 100%;
      height: 600px;
      background-color: #ffffff;
      border: 1px solid lightgray;
      position: relative;
      float: left;
    }}
  </style>
</head>

<body>
  <div class="card" style="width: 100%">
    <div id="mynetwork" class="card-body"></div>
  </div>

  <script type="text/javascript">
    var edges;
    var nodes;
    var allNodes;
    var allEdges;
    var nodeColors;
    var network;
    var data;

    function drawGraph() {{
      var container = document.getElementById('mynetwork');

      nodes = new vis.DataSet({nodes_json});

      edges = new vis.DataSet({edges_json});

      nodeColors = {{}};
      allNodes = nodes.get({{ returnType: "Object" }});

      for (nodeId in allNodes) {{
        nodeColors[nodeId] = allNodes[nodeId].color;
      }}

      allEdges = edges.get({{ returnType: "Object" }});

      data = {{
        nodes: nodes,
        edges: edges
      }};

      var options = {{
        "configure": {{
          "enabled": false
        }},
        "edges": {{
          "color": {{
            "inherit": false
          }},
          "smooth": {{
            "enabled": true,
            "type": "dynamic"
          }},
          "font": {{
            "color": "black",
            "size": 16
          }}
        }},
        "interaction": {{
          "dragNodes": true,
          "hideEdgesOnDrag": false,
          "hideNodesOnDrag": false
        }},
        "physics": {{
          "enabled": true,
          "stabilization": {{
            "enabled": true,
            "fit": true,
            "iterations": 1000,
            "onlyDynamicEdges": false,
            "updateInterval": 50
          }}
        }}
      }};

      network = new vis.Network(container, data, options);

      return network;
    }}

    drawGraph();
  </script>
</body>
</html>
"""


def gerar_arquivos(csv_path: Path, output_dir: Path) -> None:
    """Lê o CSV e gera um HTML por linha."""
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV não encontrado: {csv_path}")

    output_dir.mkdir(parents=True, exist_ok=True)

    with csv_path.open("r", encoding="utf-8-sig", newline="") as arquivo_csv:
        leitor = csv.DictReader(arquivo_csv)

        colunas_esperadas = {"origem", "destino", "custo", "caminho"}
        colunas_encontradas = set(leitor.fieldnames or [])

        if not colunas_esperadas.issubset(colunas_encontradas):
            raise ValueError(
                "CSV inválido. Colunas esperadas: "
                f"{', '.join(sorted(colunas_esperadas))}. "
                f"Colunas encontradas: {', '.join(sorted(colunas_encontradas))}"
            )

        total_gerado = 0

        for linha in leitor:
            origem = linha["origem"].strip()
            destino = linha["destino"].strip()
            custo_total = float(linha["custo"])
            vertices = caminho_para_vertices(linha["caminho"])

            if len(vertices) < 2:
                print(f"Pulando linha inválida, caminho incompleto: {linha}")
                continue

            nodes = criar_nodes(vertices)
            edges = criar_edges(vertices, custo_total)
            html = gerar_html(nodes, edges)

            nome_arquivo = f"arvore_percurso_{origem}_para_{destino}.html"
            caminho_saida = output_dir / nome_arquivo
            caminho_saida.write_text(html, encoding="utf-8")

            print(f"Gerado: {caminho_saida}")
            total_gerado += 1

        print(f"\nTotal de arquivos HTML gerados: {total_gerado}")


def main() -> None:
    pasta_src = Path(__file__).resolve().parent
    pasta_projeto = pasta_src.parent

    csv_path = pasta_projeto / "out" / "distancias_rotas.csv"
    output_dir = pasta_projeto / "out"

    gerar_arquivos(csv_path, output_dir)


if __name__ == "__main__":
    main()
