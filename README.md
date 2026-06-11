# Grafos-AVD
Projeto de grafos e avd

### Documentação do projeto
https://docs.google.com/document/d/1jquqn2maJD1fjfvGnv9ONwBkvVQNSlphJQJz95pkfwQ/edit?usp=sharing

# Parte 1
## Necessário para rodar o projeto:
Python

## Como rodar o projeto:

- Primeiro precisamos criar um ambiente virtual e ativa-lo:
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

- Depois vamos instalar as bibliotecas necessárias:
```bash
pip install -r requirements.txt
```

- Depois basta rodar o streamlit:
```bash
cd src
streamlit run app.py
```

# Parte 2
## Necessário para rodar o projeto:
- **Node.js** (para o front-end React)
- **Python** com as dependências do `requirements.txt` (para a API que executa os algoritmos)

## Como rodar o projeto:

A Parte 2 precisa de **dois terminais abertos ao mesmo tempo**: um para a API Python e outro para o front-end React. A API recebe as requisições do React, executa os algoritmos de `src/graphs/algorithms.py` e devolve os resultados.

### Terminal 1 — API Python (FastAPI)

```bash
# Com o venv já ativado (ver Parte 1)
python src/api.py
```

A API sobe em `http://localhost:5000`. Ela carrega o grafo do `data/dataset_parte2/links_reduzido.csv` na inicialização e expõe os endpoints usados pelo React. A documentação interativa fica em `http://localhost:5000/docs`.

### Terminal 2 — Front-end React

```bash
cd src/grafo-wiki
# Só precisa rodar npm install na primeira vez
npm install
npm run dev
```

O React sobe em `http://localhost:5173`. Abra essa URL no navegador.

### Páginas disponíveis no React
- **`/`** — visualização interativa do grafo (com filtro de quantidade de arestas)
- **`/algoritmos`** — escolhe o algoritmo (BFS, DFS, Dijkstra, Bellman-Ford), digita origem e destino e roda em tempo real via API

## Como rodar os testes
```bash
# Na pasta raiz do projeto
.\venv\Scripts\python.exe -m pytest tests/ -v
```


# Integrantes:
- Arthur Leal
- Bruno Carvalho
- Guilherme Coutinho
- Igor Couto
- William Souza
